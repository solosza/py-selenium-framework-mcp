"""
AuditLogger - Audit Trail System for QA Management Engine.

Provides per-run audit logging for the 5-step workflow (v3.0).
DEF-040 - Incremental persist after each event (crash-safe, no data loss).

Features:
- Event-driven audit trail (typed events: gate_validation, tool_call, hitl_interaction, hook_intervention)
- Gate validation logging with results and sources
- Self-heal attempt logging
- Atomic writes per event (no data loss on crash)
- Outputs events array format per finalized data model (FR-5 in PRD)

Output Format:
{
  "workflow_id": "2026-01-22T10-30-45.123456Z",
  "events": [
    {"type": "gate_validation", "step": 1, "gate": "qg_preflight", "result": "pass", ...},
    {"type": "self-heal", "step": 2, "attempt": 1, "error": "...", ...}
  ]
}

Schema matches PRD spec (2-prd-pair-programming-formalization.md FR-5).
"""

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditLogger:
    """Logs workflow execution for audit trail."""

    def __init__(
        self,
        run_id: Optional[str] = None,
        execution_mode: str = "mixed",
        output_dir: Optional[str] = None
    ):
        """
        Initialize AuditLogger.

        Args:
            run_id: Optional custom run ID. If None, generates ISO timestamp.
            execution_mode: Execution mode (mixed, skills_only). Default: mixed.
            output_dir: Directory for audit file. Default: mcp_server/state/
        """
        if run_id is None:
            run_id = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        self.run_id = run_id
        self.execution_mode = execution_mode

        # DEF-040: Set up audit file path for incremental persist
        # DEF-042: Write to tests/_audit/ instead of mcp_server/state/
        if output_dir is None:
            # Navigate from mcp_server/utils/ to project root, then to tests/_audit/
            project_root = Path(__file__).parent.parent.parent
            output_dir = str(project_root / "tests" / "_audit")
        self._output_dir = Path(output_dir)

        # Generate filename from run_id (replace : with - for Windows compatibility)
        safe_run_id = self.run_id.replace(":", "-")
        self._audit_file = self._output_dir / f"audit_log_{safe_run_id}.json"

        # DEF-043: Load existing audit data if continuing a session
        self.events: List[Dict[str, Any]] = []
        self.files_generated: List[Dict[str, Any]] = []  # Kept for backward compatibility
        self._load_existing_data()

    def _load_existing_data(self) -> None:
        """
        DEF-043: Load existing audit data when continuing a session.

        If the audit file already exists (from a previous MCP tool call in
        the same workflow run), load its events list to continue appending.
        """
        if not self._audit_file.exists():
            return

        try:
            with open(self._audit_file, 'r') as f:
                data = json.load(f)

            # Restore existing events
            self.events = data.get("events", [])

            # Restore files_generated for backward compatibility
            self.files_generated = data.get("files_generated", [])

            # Restore execution_mode if present
            if "execution_mode" in data:
                self.execution_mode = data["execution_mode"]
        except (json.JSONDecodeError, IOError):
            # If file is corrupted, start fresh
            self.events = []
            self.files_generated = []

    def log_gate(
        self,
        step: int,
        gate_name: str,
        mode: str,
        result: str,
        error: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a gate call and persist immediately (DEF-040).

        Args:
            step: Step number (1-10)
            gate_name: Gate name (e.g., qg_preflight)
            mode: Gate mode (PRE, POST)
            result: Result (pass, fail, blocked)
            error: Error message if failed
            source: Execution source (tool, ai, self-heal)
            metadata: Validation data from this step (e.g., persona, URL, page_name)
        """
        entry: Dict[str, Any] = {
            "type": "gate_validation",
            "step": step,
            "gate": gate_name,
            "mode": mode,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        if error is not None:
            entry["error"] = error

        if source is not None:
            entry["source"] = source

        if metadata is not None:
            entry["metadata"] = metadata

        self.events.append(entry)

        # DEF-040: Persist immediately after each log
        self._persist()

    def log_self_heal(
        self,
        step: int,
        attempt: int,
        error: str
    ) -> None:
        """
        Log a self-heal attempt and persist immediately (DEF-040).

        Args:
            step: Step number where self-heal occurred
            attempt: Attempt number (1, 2, 3...)
            error: Error that triggered self-heal
        """
        entry = {
            "type": "self-heal",
            "step": step,
            "attempt": attempt,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        self.events.append(entry)

        # DEF-040: Persist immediately after each log
        self._persist()

    def log_file_generated(
        self,
        path: str,
        step: int
    ) -> None:
        """
        Log a generated file and persist immediately (DEF-040).

        Args:
            path: File path (relative to project root)
            step: Step number that generated the file
        """
        entry = {
            "path": path,
            "step": step
        }

        self.files_generated.append(entry)

        # DEF-040: Persist immediately after each log
        self._persist()

    def get_summary(self) -> Dict[str, Any]:
        """
        Calculate summary statistics from events.

        NOTE: Summary is computed on-demand and NOT persisted to audit log.
        Metrics belong in workflow_state.json per the finalized data model.

        Returns:
            Dict with total_steps, gates_passed, gates_failed, self_heals,
            final_result, execution_mode, source_counts
        """
        # Count unique steps
        unique_steps = set()
        gates_passed = 0
        gates_failed = 0
        self_heals = 0
        last_result = None

        # Task 2.5: Count sources
        source_counts: Dict[str, int] = {}

        for entry in self.events:
            step = entry.get("step")
            if step is not None:
                unique_steps.add(step)

            entry_type = entry.get("type")
            if entry_type == "self-heal":
                self_heals += 1
            elif entry_type == "gate_validation":
                # It's a gate entry
                result = entry.get("result")
                if result == "pass":
                    gates_passed += 1
                    last_result = "pass"
                elif result == "fail":
                    gates_failed += 1
                    last_result = "fail"
                elif result == "blocked":
                    gates_failed += 1
                    last_result = "blocked"

                # Task 2.5: Track source
                source = entry.get("source")
                if source is not None:
                    source_counts[source] = source_counts.get(source, 0) + 1

        return {
            "total_steps": len(unique_steps),
            "gates_passed": gates_passed,
            "gates_failed": gates_failed,
            "self_heals": self_heals,
            "final_result": last_result if last_result else "incomplete",
            "execution_mode": self.execution_mode,
            "source_counts": source_counts
        }

    def _persist(self) -> None:
        """
        DEF-040: Persist audit log to disk using atomic write.

        Called automatically after each log_gate(), log_self_heal(),
        and log_file_generated() call. Crash-safe - data is never lost.

        Persists events array per finalized data model (FR-5 in PRD).
        """
        # Ensure parent directory exists
        self._output_dir.mkdir(parents=True, exist_ok=True)

        # Build output data (events array format per designed data model)
        data = {
            "workflow_id": self.run_id,  # Renamed from run_id
            "events": self.events  # Renamed from steps, contains typed events
        }

        # Atomic write: write to temp file, then rename
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self._output_dir,
            suffix=".tmp"
        )
        try:
            with os.fdopen(temp_fd, 'w') as f:
                json.dump(data, f, indent=2)

            # Atomic rename (on Windows, need to remove target first)
            if os.name == 'nt' and self._audit_file.exists():
                self._audit_file.unlink()
            os.rename(temp_path, self._audit_file)
        except Exception:
            # Clean up temp file on failure
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    def finalize(self, output_dir: Optional[str] = None) -> str:
        """
        Finalize audit log (optional - data is already persisted).

        DEF-040: Since we now persist after each log call, this method
        is optional. It's kept for backward compatibility and returns
        the audit file path.

        Args:
            output_dir: Ignored (kept for backward compatibility).

        Returns:
            Path to audit log file.
        """
        # Ensure final persist with complete summary
        self._persist()

        return str(self._audit_file)

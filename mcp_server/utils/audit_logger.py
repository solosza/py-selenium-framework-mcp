"""
AuditLogger - Audit Trail System for QA Execution Engine.

Task 1.0 - Provides per-run audit logging for the 10-step workflow.

Features:
- Logs gate calls with results and sources
- Logs self-heal attempts
- Logs generated files
- Generates summary statistics
- Writes JSON audit file per run

Schema matches PRD spec (1-prd-release-readiness.md).
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditLogger:
    """Logs workflow execution for audit trail."""

    def __init__(
        self,
        run_id: Optional[str] = None,
        execution_mode: str = "mixed"
    ):
        """
        Initialize AuditLogger.

        Args:
            run_id: Optional custom run ID. If None, generates ISO timestamp.
            execution_mode: Execution mode (mixed, skills_only). Default: mixed.
        """
        if run_id is None:
            run_id = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        self.run_id = run_id
        self.execution_mode = execution_mode
        self.steps: List[Dict[str, Any]] = []
        self.files_generated: List[Dict[str, Any]] = []

    def log_gate(
        self,
        step: int,
        gate_name: str,
        mode: str,
        result: str,
        error: Optional[str] = None,
        source: Optional[str] = None
    ) -> None:
        """
        Log a gate call.

        Args:
            step: Step number (1-10)
            gate_name: Gate name (e.g., qg_preflight)
            mode: Gate mode (PRE, POST)
            result: Result (pass, fail, blocked)
            error: Error message if failed
            source: Execution source (tool, ai, self-heal)
        """
        entry: Dict[str, Any] = {
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

        self.steps.append(entry)

    def log_self_heal(
        self,
        step: int,
        attempt: int,
        error: str
    ) -> None:
        """
        Log a self-heal attempt.

        Args:
            step: Step number where self-heal occurred
            attempt: Attempt number (1, 2, 3...)
            error: Error that triggered self-heal
        """
        entry = {
            "step": step,
            "type": "self-heal",
            "attempt": attempt,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        self.steps.append(entry)

    def log_file_generated(
        self,
        path: str,
        step: int
    ) -> None:
        """
        Log a generated file.

        Args:
            path: File path (relative to project root)
            step: Step number that generated the file
        """
        entry = {
            "path": path,
            "step": step
        }

        self.files_generated.append(entry)

    def get_summary(self) -> Dict[str, Any]:
        """
        Calculate summary statistics.

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

        for entry in self.steps:
            step = entry.get("step")
            if step is not None:
                unique_steps.add(step)

            entry_type = entry.get("type")
            if entry_type == "self-heal":
                self_heals += 1
            else:
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

    def finalize(self, output_dir: Optional[str] = None) -> str:
        """
        Write audit log to JSON file.

        Args:
            output_dir: Directory to write file. Default: mcp_server/state/

        Returns:
            Path to created audit log file.
        """
        if output_dir is None:
            output_dir = str(Path(__file__).parent.parent / "state")

        # Create directory if needed
        os.makedirs(output_dir, exist_ok=True)

        # Build output data
        data = {
            "run_id": self.run_id,
            "execution_mode": self.execution_mode,
            "steps": self.steps,
            "files_generated": self.files_generated,
            "summary": self.get_summary()
        }

        # Generate filename from run_id (replace : with - for Windows compatibility)
        safe_run_id = self.run_id.replace(":", "-")
        filename = f"audit_log_{safe_run_id}.json"
        filepath = os.path.join(output_dir, filename)

        # Write JSON
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        return filepath

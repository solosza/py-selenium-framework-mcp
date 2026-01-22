"""
TranscriptWriter - Human-Readable Workflow Transcript System.

Generates human-readable markdown transcript from audit log events.
Part of finalized data model (FR-5 in PRD).

Features:
- Reads events array from audit log
- Converts typed events to markdown narrative
- Progressive updates (regenerate after each event)
- Outputs to tests/_reports/{run_id}/workflow_transcript.md

Single source of truth: audit log (observability)
Human-readable view: transcript (developer/user comprehension)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class TranscriptWriter:
    """Generates human-readable workflow transcript from audit events."""

    def __init__(self, run_id: str, audit_dir: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialize TranscriptWriter.

        Args:
            run_id: Workflow run ID (ISO timestamp)
            audit_dir: Directory containing audit log. Default: tests/_audit/
            output_dir: Directory for transcript. Default: tests/_reports/{run_id}/
        """
        self.run_id = run_id

        # Find project root
        project_root = Path(__file__).parent.parent.parent

        # Set audit file path
        if audit_dir is None:
            audit_dir = str(project_root / "tests" / "_audit")
        self._audit_dir = Path(audit_dir)

        # Generate audit filename (replace : with - for Windows compatibility)
        safe_run_id = run_id.replace(":", "-")
        self._audit_file = self._audit_dir / f"audit_log_{safe_run_id}.json"

        # Set output path
        if output_dir is None:
            output_dir = str(project_root / "tests" / "_reports" / run_id)
        self._output_dir = Path(output_dir)
        self._transcript_file = self._output_dir / "workflow_transcript.md"

    def generate(self) -> str:
        """
        Generate transcript from audit log and persist to disk.

        Reads events array from audit log, converts to markdown narrative,
        and writes to transcript file.

        Returns:
            Path to transcript file.
        """
        # Load audit log
        if not self._audit_file.exists():
            raise FileNotFoundError(f"Audit log not found: {self._audit_file}")

        with open(self._audit_file, 'r') as f:
            audit_data = json.load(f)

        workflow_id = audit_data.get("workflow_id", self.run_id)
        events = audit_data.get("events", [])

        # Generate markdown content
        content = self._generate_markdown(workflow_id, events)

        # Persist to disk
        self._persist(content)

        return str(self._transcript_file)

    def _generate_markdown(self, workflow_id: str, events: List[Dict[str, Any]]) -> str:
        """
        Convert audit events to markdown narrative.

        Args:
            workflow_id: Workflow identifier
            events: List of typed events from audit log

        Returns:
            Markdown content string
        """
        lines = []

        # Header
        lines.append(f"# Workflow Transcript")
        lines.append(f"")
        lines.append(f"**Workflow ID:** `{workflow_id}`")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

        if not events:
            lines.append(f"*No events recorded yet.*")
            return "\n".join(lines)

        # Group events by step
        steps: Dict[int, List[Dict[str, Any]]] = {}
        for event in events:
            step = event.get("step")
            if step is not None:
                if step not in steps:
                    steps[step] = []
                steps[step].append(event)

        # Generate step sections
        for step_num in sorted(steps.keys()):
            step_events = steps[step_num]
            lines.append(f"## Step {step_num}")
            lines.append(f"")

            for event in step_events:
                event_type = event.get("type", "unknown")

                if event_type == "gate_validation":
                    lines.extend(self._format_gate_event(event))
                elif event_type == "self-heal":
                    lines.extend(self._format_self_heal_event(event))
                elif event_type == "tool_call":
                    lines.extend(self._format_tool_call_event(event))
                elif event_type == "hitl_interaction":
                    lines.extend(self._format_hitl_event(event))
                elif event_type == "hook_intervention":
                    lines.extend(self._format_hook_event(event))
                else:
                    lines.extend(self._format_unknown_event(event))

                lines.append(f"")

            lines.append(f"---")
            lines.append(f"")

        return "\n".join(lines)

    def _format_gate_event(self, event: Dict[str, Any]) -> List[str]:
        """Format gate_validation event as markdown."""
        gate = event.get("gate", "unknown")
        mode = event.get("mode", "")
        result = event.get("result", "unknown")
        timestamp = event.get("timestamp", "")
        error = event.get("error")
        metadata = event.get("metadata", {})

        lines = []

        # Result icon
        icon = "✅" if result == "pass" else "❌" if result == "fail" else "🚫"

        lines.append(f"### {icon} Gate: `{gate}` ({mode})")
        lines.append(f"")
        lines.append(f"**Result:** `{result}`")
        lines.append(f"**Timestamp:** {timestamp}")

        if error:
            lines.append(f"")
            lines.append(f"**Error:**")
            lines.append(f"```")
            lines.append(f"{error}")
            lines.append(f"```")

        if metadata:
            lines.append(f"")
            lines.append(f"**Metadata:**")
            for key, value in metadata.items():
                lines.append(f"- `{key}`: {value}")

        return lines

    def _format_self_heal_event(self, event: Dict[str, Any]) -> List[str]:
        """Format self-heal event as markdown."""
        attempt = event.get("attempt", 0)
        error = event.get("error", "unknown")
        timestamp = event.get("timestamp", "")

        lines = []
        lines.append(f"### 🔧 Self-Heal Attempt #{attempt}")
        lines.append(f"")
        lines.append(f"**Timestamp:** {timestamp}")
        lines.append(f"**Error:**")
        lines.append(f"```")
        lines.append(f"{error}")
        lines.append(f"```")

        return lines

    def _format_tool_call_event(self, event: Dict[str, Any]) -> List[str]:
        """Format tool_call event as markdown."""
        tool = event.get("tool", "unknown")
        timestamp = event.get("timestamp", "")
        input_data = event.get("input")
        output_data = event.get("output")

        lines = []
        lines.append(f"### 🔨 Tool Call: `{tool}`")
        lines.append(f"")
        lines.append(f"**Timestamp:** {timestamp}")

        if input_data:
            lines.append(f"")
            lines.append(f"**Input:**")
            lines.append(f"```json")
            lines.append(json.dumps(input_data, indent=2))
            lines.append(f"```")

        if output_data:
            lines.append(f"")
            lines.append(f"**Output:**")
            lines.append(f"```json")
            lines.append(json.dumps(output_data, indent=2))
            lines.append(f"```")

        return lines

    def _format_hitl_event(self, event: Dict[str, Any]) -> List[str]:
        """Format hitl_interaction event as markdown."""
        trigger = event.get("trigger_reason", "unknown")
        timestamp = event.get("timestamp", "")
        user_choice = event.get("user_choice")

        lines = []
        lines.append(f"### 👤 HITL Interaction")
        lines.append(f"")
        lines.append(f"**Trigger:** {trigger}")
        lines.append(f"**Timestamp:** {timestamp}")

        if user_choice:
            lines.append(f"**User Choice:** {user_choice}")

        return lines

    def _format_hook_event(self, event: Dict[str, Any]) -> List[str]:
        """Format hook_intervention event as markdown."""
        hook = event.get("hook", "unknown")
        pattern = event.get("pattern", "unknown")
        timestamp = event.get("timestamp", "")

        lines = []
        lines.append(f"### ⚠️ Hook Intervention: `{hook}`")
        lines.append(f"")
        lines.append(f"**Pattern:** {pattern}")
        lines.append(f"**Timestamp:** {timestamp}")

        return lines

    def _format_unknown_event(self, event: Dict[str, Any]) -> List[str]:
        """Format unknown event type as markdown."""
        event_type = event.get("type", "unknown")
        timestamp = event.get("timestamp", "")

        lines = []
        lines.append(f"### ❓ Unknown Event Type: `{event_type}`")
        lines.append(f"")
        lines.append(f"**Timestamp:** {timestamp}")
        lines.append(f"")
        lines.append(f"**Raw Data:**")
        lines.append(f"```json")
        lines.append(json.dumps(event, indent=2))
        lines.append(f"```")

        return lines

    def _persist(self, content: str) -> None:
        """
        Persist transcript to disk.

        Args:
            content: Markdown content to write
        """
        # Ensure parent directory exists
        self._output_dir.mkdir(parents=True, exist_ok=True)

        # Write transcript file
        with open(self._transcript_file, 'w', encoding='utf-8') as f:
            f.write(content)

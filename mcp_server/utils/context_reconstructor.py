"""
Context Reconstructor - Rebuild workflow state from audit trail.

Solves context window issues by using audit trail as source of truth.
When context is lost, read audit trail metadata to reconstruct where we were.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class ContextReconstructor:
    """Reconstruct workflow state from audit trail metadata."""

    def __init__(self, audit_file_path: str):
        """
        Initialize reconstructor with audit file.

        Args:
            audit_file_path: Path to audit JSON file
        """
        self.audit_file = Path(audit_file_path)
        if not self.audit_file.exists():
            raise FileNotFoundError(f"Audit file not found: {audit_file_path}")

        with open(self.audit_file, 'r') as f:
            self.audit_data = json.load(f)

    def get_completed_steps(self) -> List[int]:
        """
        Get list of completed steps from audit trail.

        Returns:
            List of step numbers that passed validation
        """
        steps = self.audit_data.get("steps", [])
        completed = set()

        for entry in steps:
            if entry.get("result") == "pass":
                completed.add(entry.get("step"))

        return sorted(list(completed))

    def get_step_metadata(self, step: int) -> List[Dict[str, Any]]:
        """
        Get all metadata entries for a specific step.

        For multi-page workflows (like Step 6), returns multiple entries.

        Args:
            step: Step number (1-10)

        Returns:
            List of metadata dicts for this step
        """
        steps = self.audit_data.get("steps", [])
        metadata_entries = []

        for entry in steps:
            if entry.get("step") == step and entry.get("result") == "pass":
                metadata = entry.get("metadata")
                if metadata:
                    metadata_entries.append(metadata)

        return metadata_entries

    def get_workflow_summary(self) -> Dict[str, Any]:
        """
        Get human-readable summary of workflow progress.

        Returns:
            Dict with workflow state information
        """
        completed_steps = self.get_completed_steps()

        summary = {
            "run_id": self.audit_data.get("run_id"),
            "execution_mode": self.audit_data.get("execution_mode"),
            "completed_steps": completed_steps,
            "last_step": max(completed_steps) if completed_steps else 0,
            "workflow_complete": 10 in completed_steps,
            "step_details": {}
        }

        # Extract key info from each step
        if 1 in completed_steps:
            preflight = self.get_step_metadata(1)
            if preflight:
                summary["step_details"]["preflight"] = preflight[0]

        if 2 in completed_steps:
            user_input = self.get_step_metadata(2)
            if user_input:
                summary["step_details"]["user_input"] = user_input[0]

        if 3 in completed_steps:
            ai_processing = self.get_step_metadata(3)
            if ai_processing:
                summary["step_details"]["ai_processing"] = ai_processing[0]

        if 6 in completed_steps:
            pom_entries = self.get_step_metadata(6)
            summary["step_details"]["poms_generated"] = {
                "count": len(pom_entries),
                "pages": [entry.get("page_name") for entry in pom_entries]
            }

        if 7 in completed_steps:
            task_entries = self.get_step_metadata(7)
            if task_entries:
                summary["step_details"]["task"] = task_entries[0]

        if 8 in completed_steps:
            role_entries = self.get_step_metadata(8)
            if role_entries:
                summary["step_details"]["role"] = role_entries[0]

        if 9 in completed_steps:
            test_entries = self.get_step_metadata(9)
            if test_entries:
                summary["step_details"]["test"] = test_entries[0]

        return summary

    def can_resume_from_step(self, step: int) -> bool:
        """
        Check if we have enough metadata to resume from this step.

        Args:
            step: Step number to check

        Returns:
            True if we can resume from this step
        """
        completed_steps = self.get_completed_steps()

        # To resume from step N, step N-1 must be complete
        if step == 1:
            return True  # Can always start from Step 1

        return (step - 1) in completed_steps

    def reconstruct_state(self) -> Dict[str, Any]:
        """
        Reconstruct workflow state from audit trail metadata.

        This can be used to rebuild workflow_state.json if it's lost/corrupted.

        Returns:
            Dict with reconstructed state for each step
        """
        state = {
            "step_0": {
                "audit_run_id": self.audit_data.get("run_id")
            }
        }

        # Step 1: Preflight
        preflight = self.get_step_metadata(1)
        if preflight:
            state["step_1"] = preflight[0]

        # Step 2: User Input
        user_input = self.get_step_metadata(2)
        if user_input:
            state["step_2"] = user_input[0]

        # Step 3: AI Processing
        ai_processing = self.get_step_metadata(3)
        if ai_processing:
            state["step_3"] = {
                "intent": ai_processing[0].get("intent"),
                "scenarios_count": ai_processing[0].get("scenarios_count"),
                "expected_states_count": ai_processing[0].get("expected_states_count")
            }
            # Note: Full BDD scenarios not in audit, would need to read from state file

        # Step 6: POMs (multi-page support)
        pom_entries = self.get_step_metadata(6)
        if pom_entries:
            state["step_6"] = {
                "generated_poms": {
                    entry.get("page_name"): {
                        "class_name": entry.get("class_name"),
                        "import_path": entry.get("import_path"),
                        "action_methods_count": entry.get("action_methods_count"),
                        "state_methods_count": entry.get("state_methods_count"),
                        "multi_page": entry.get("multi_page")
                    }
                    for entry in pom_entries
                },
                "poms_generated": len(pom_entries)
            }

        # Step 7: Task
        task_entries = self.get_step_metadata(7)
        if task_entries:
            state["step_7"] = task_entries[0]

        # Step 8: Role
        role_entries = self.get_step_metadata(8)
        if role_entries:
            state["step_8"] = role_entries[0]

        # Step 9: Test
        test_entries = self.get_step_metadata(9)
        if test_entries:
            state["step_9"] = test_entries[0]

        return state


def find_latest_audit_file(audit_dir: str = None) -> Optional[str]:
    """
    Find the most recent audit file.

    Args:
        audit_dir: Directory to search. Defaults to tests/_audit/

    Returns:
        Path to latest audit file, or None if no files found
    """
    if audit_dir is None:
        # Default to tests/_audit/ relative to project root
        project_root = Path(__file__).parent.parent.parent
        audit_dir = str(project_root / "tests" / "_audit")

    audit_path = Path(audit_dir)
    if not audit_path.exists():
        return None

    audit_files = list(audit_path.glob("audit_log_*.json"))
    if not audit_files:
        return None

    # Get most recent by modification time
    latest = max(audit_files, key=lambda p: p.stat().st_mtime)
    return str(latest)


# Example usage
if __name__ == "__main__":
    # Find latest audit file
    audit_file = find_latest_audit_file()
    if not audit_file:
        print("No audit files found")
        exit(1)

    print(f"Reading audit file: {audit_file}\n")

    # Reconstruct context
    reconstructor = ContextReconstructor(audit_file)

    # Show summary
    summary = reconstructor.get_workflow_summary()
    print("Workflow Summary:")
    print(json.dumps(summary, indent=2))

    print("\n" + "="*60)
    print("Completed Steps:", reconstructor.get_completed_steps())
    print("Can resume from Step 7?", reconstructor.can_resume_from_step(7))

    # Show reconstructed state
    print("\n" + "="*60)
    print("Reconstructed State:")
    state = reconstructor.reconstruct_state()
    print(json.dumps(state, indent=2))

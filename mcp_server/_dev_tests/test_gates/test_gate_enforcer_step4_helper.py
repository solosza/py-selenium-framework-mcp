"""
Helper module to test gate enforcer logic without running the hook subprocess.

This module simulates the gate enforcer check by importing and calling
the gate enforcer functions directly.
"""

import json
from pathlib import Path


def check_gate_enforcer(file_path: str, state_dir: Path) -> dict:
    """
    Simulate gate enforcer check for a file path.

    Args:
        file_path: Path to file being written
        state_dir: Directory containing workflow_state.json

    Returns:
        dict with keys:
            - blocked (bool): True if write would be blocked
            - error (str | None): Error message if blocked
    """
    # Import gate enforcer functions
    import sys
    import os

    # Add hooks directory to path
    hooks_dir = Path(__file__).parent.parent.parent.parent / ".claude" / "hooks"
    sys.path.insert(0, str(hooks_dir))

    try:
        # Import gate enforcer functions (this will work since it's in _dev_tests/)
        from pathlib import Path as HookPath
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "qa_gate_enforcer",
            hooks_dir / "qa-gate-enforcer.py"
        )
        enforcer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(enforcer)

        # Get required step and metadata key
        required_step = enforcer.get_required_step(file_path)

        if required_step is None:
            # Not a protected path
            return {"blocked": False, "error": None}

        # Load state
        state_file = state_dir / "workflow_state.json"

        if not state_file.exists():
            return {
                "blocked": True,
                "error": f"BLOCKED: No QA workflow state found. Expected: {state_file}"
            }

        with open(state_file, 'r') as f:
            state = json.load(f)

        # Check if gate passed
        gate_passed = enforcer.is_gate_passed(state, required_step, file_path=file_path)

        if not gate_passed:
            # Determine which metadata key is required
            if required_step == 'step_4':
                required_metadata = enforcer.get_required_metadata_key(file_path) or 'unknown'
            else:
                required_metadata = 'complete'

            return {
                "blocked": True,
                "error": f"BLOCKED: {required_step} must have {required_metadata}"
            }

        # Gate passed
        return {"blocked": False, "error": None}

    finally:
        # Clean up sys.path
        if str(hooks_dir) in sys.path:
            sys.path.remove(str(hooks_dir))

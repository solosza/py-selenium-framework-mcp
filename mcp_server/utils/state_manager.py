"""
StateManager - Workflow state persistence for QA Execution Engine

Task 2.0 - Manages workflow state across quality gate operations.
Task 2.5 - Adds execution mode management.

Features:
- Atomic writes to prevent corruption
- Step validation (1-10 range)
- Graceful handling of missing/corrupted files
- Execution mode get/set with env var default
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Optional


# Valid execution modes (Topic 1 from PRD)
VALID_EXECUTION_MODES = {"mixed", "skills_only"}


# Valid step range for the 10-step workflow
VALID_STEPS = range(1, 11)  # 1-10 inclusive


class StateManager:
    """Manages workflow state persistence across gate operations."""

    def __init__(self, state_file: str = None):
        """
        Initialize StateManager with optional state file path.

        Args:
            state_file: Path to state JSON file. If None, uses default location.
        """
        if state_file is None:
            # Default: mcp_server/state/workflow_state.json
            default_dir = Path(__file__).parent.parent / "state"
            state_file = str(default_dir / "workflow_state.json")

        self._state_file = Path(state_file)

    def save(self, step: int, data: dict) -> None:
        """
        Save step data to state file using atomic write.

        Args:
            step: Step number (1-10)
            data: Dictionary of step data to save
        """
        # Load existing state
        current_state = self.load()

        # Update with new step data
        step_key = f"step_{step}"
        current_state[step_key] = data

        # Ensure parent directory exists
        self._state_file.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write: write to temp file, then rename
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self._state_file.parent,
            suffix=".tmp"
        )
        try:
            with os.fdopen(temp_fd, 'w') as f:
                json.dump(current_state, f, indent=2)

            # Atomic rename (on Windows, need to remove target first)
            if os.name == 'nt' and self._state_file.exists():
                self._state_file.unlink()
            os.rename(temp_path, self._state_file)
        except Exception:
            # Clean up temp file on failure
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    def load(self) -> dict:
        """
        Load complete state from file.

        Returns:
            Dictionary of all step data, or empty dict if file missing/corrupted.
        """
        if not self._state_file.exists():
            return {}

        try:
            with open(self._state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Return empty dict for corrupted files
            return {}

    def get_step(self, step: int) -> Optional[dict]:
        """
        Get data for a specific step.

        Args:
            step: Step number (1-10)

        Returns:
            Step data dict, or None if step not found or invalid.
        """
        # Validate step range (1-10)
        if step not in VALID_STEPS:
            return None

        state = self.load()
        step_key = f"step_{step}"
        return state.get(step_key)

    def is_step_complete(self, step: int) -> bool:
        """
        Check if a step has been completed (has data saved).

        Args:
            step: Step number (1-10)

        Returns:
            True if step exists with data, False otherwise.
        """
        step_data = self.get_step(step)
        return step_data is not None

    def clear(self) -> None:
        """Clear state file (for testing and workflow reset)."""
        if self._state_file.exists():
            self._state_file.unlink()

    # =========================================================================
    # Attempt Tracking (Task 2.0 - Self-Heal Cap)
    # =========================================================================

    def get_attempt_count(self, step: int) -> int:
        """
        Get current attempt count for a step.

        Args:
            step: Step number (1-10)

        Returns:
            Current attempt count (0 if no attempts yet).
        """
        state = self.load()
        attempts = state.get("_attempts", {})
        return attempts.get(str(step), 0)

    def increment_attempt(self, step: int) -> int:
        """
        Increment attempt count for a step and persist to disk.

        Args:
            step: Step number (1-10)

        Returns:
            New attempt count after increment.
        """
        state = self.load()

        # Initialize attempts dict if needed
        if "_attempts" not in state:
            state["_attempts"] = {}

        # Increment
        step_key = str(step)
        current = state["_attempts"].get(step_key, 0)
        new_count = current + 1
        state["_attempts"][step_key] = new_count

        # Persist
        self._save_state(state)

        return new_count

    def reset_attempts(self, step: int) -> None:
        """
        Reset attempt count for a step to zero.

        Args:
            step: Step number (1-10)
        """
        state = self.load()

        if "_attempts" not in state:
            return  # Nothing to reset

        step_key = str(step)
        if step_key in state["_attempts"]:
            state["_attempts"][step_key] = 0
            self._save_state(state)

    # =========================================================================
    # Execution Mode (Task 2.5 - Execution Mode Flag)
    # =========================================================================

    def get_execution_mode(self) -> str:
        """
        Get current execution mode.

        Priority:
        1. Saved value in state file (if exists)
        2. ISAGAWA_EXECUTION_MODE env var (if set)
        3. Default: "mixed"

        Returns:
            Execution mode ("mixed" or "skills_only").
        """
        # Check saved state first
        state = self.load()
        saved_mode = state.get("_execution_mode")
        if saved_mode is not None:
            return saved_mode

        # Check env var
        env_mode = os.environ.get("ISAGAWA_EXECUTION_MODE")
        if env_mode and env_mode in VALID_EXECUTION_MODES:
            return env_mode

        # Default
        return "mixed"

    def set_execution_mode(self, mode: str) -> None:
        """
        Set execution mode.

        Args:
            mode: Execution mode ("mixed" or "skills_only")

        Raises:
            ValueError: If mode is not valid.
        """
        if mode not in VALID_EXECUTION_MODES:
            valid_modes = ", ".join(sorted(VALID_EXECUTION_MODES))
            raise ValueError(
                f"Invalid execution mode: '{mode}'. Valid modes: {valid_modes}"
            )

        state = self.load()
        state["_execution_mode"] = mode
        self._save_state(state)

    def _save_state(self, state: dict) -> None:
        """
        Internal method to save complete state to disk.

        Args:
            state: Complete state dictionary to persist.
        """
        # Ensure parent directory exists
        self._state_file.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write: write to temp file, then rename
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self._state_file.parent,
            suffix=".tmp"
        )
        try:
            with os.fdopen(temp_fd, 'w') as f:
                json.dump(state, f, indent=2)

            # Atomic rename (on Windows, need to remove target first)
            if os.name == 'nt' and self._state_file.exists():
                self._state_file.unlink()
            os.rename(temp_path, self._state_file)
        except Exception:
            # Clean up temp file on failure
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

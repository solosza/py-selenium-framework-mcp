"""
Quality Gate: Save Run (Step 10).

PRE-only validation gate for file save and test execution.

PRE Validation:
- Step 9 complete
- All 4 code blocks present (pom_code, task_code, role_code, test_code)
- No skeleton code in any layer (DD-25 final sweep)
- Primary: code from input_data; Fallback: code from state (IC-10-01)

No POST Validation (PRE-only gate per IC-10-02).

Enforces: DD-22, DD-25, IC-10-01 through IC-10-05
"""

import re
from typing import Any, Dict, Optional, Tuple

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGSaveRun(BaseGate):
    """Quality gate for Step 10: Save & Run."""

    # Skeleton code patterns (DD-25) - same as other gates
    SKELETON_PATTERNS = [
        (r'^\s*pass\s*$', 'pass statement'),
        (r'#\s*TODO:', 'TODO comment'),
        (r'#\s*[Aa]dd\s+.*\s+as\s+needed', 'placeholder comment'),
        (r'raise\s+NotImplementedError', 'NotImplementedError'),
    ]

    # Code field to step mapping (IC-10-05)
    CODE_FIELDS = {
        "pom_code": {"step": 6, "layer": "POM"},
        "task_code": {"step": 7, "layer": "Task"},
        "role_code": {"step": 8, "layer": "Role"},
        "test_code": {"step": 9, "layer": "Test"},
    }

    @classmethod
    def _get_state_manager(cls) -> StateManager:
        """Get StateManager instance. Extracted for testing."""
        return StateManager()

    @classmethod
    def _get_code(cls, input_data: Dict[str, Any], field: str, step: int) -> Optional[str]:
        """
        Get code from input_data or fallback to state (IC-10-01).

        Args:
            input_data: Input data dict
            field: Code field name (e.g., 'pom_code')
            step: Step number to read from state if not in input

        Returns:
            Code string or None if not found in either source
        """
        # Primary: check input_data
        code = input_data.get(field)
        if code is not None:
            return code

        # Fallback: check state
        state_manager = cls._get_state_manager()
        step_data = state_manager.get_step(step)
        if step_data and isinstance(step_data, dict):
            return step_data.get("code")

        return None

    @classmethod
    def _validate_code_field(
        cls,
        input_data: Dict[str, Any],
        field: str,
        step: int,
        layer: str
    ) -> Optional[Dict[str, Any]]:
        """
        Validate a single code field for presence and skeleton.

        Args:
            input_data: Input data dict
            field: Code field name
            step: Step number for this code
            layer: Human-readable layer name (POM, Task, Role, Test)

        Returns:
            fail_response if validation fails, None if passes
        """
        code = cls._get_code(input_data, field, step)

        # Check presence
        if code is None:
            return cls.fail_response(
                error=f"Missing {field}: {layer} code not found",
                fix_hint=f"Go back to Step {step} to generate {layer} code."
            )

        # Check not empty
        if not isinstance(code, str) or not code.strip():
            return cls.fail_response(
                error=f"Empty {field}: {layer} code is empty",
                fix_hint=f"Go back to Step {step} to generate {layer} code."
            )

        # Check for skeleton code (DD-25, IC-10-03)
        skeleton_error = cls._detect_skeleton_code(code, layer)
        if skeleton_error:
            return skeleton_error

        return None

    @classmethod
    def _detect_skeleton_code(cls, code: str, layer: str) -> Optional[Dict[str, Any]]:
        """
        Detect skeleton code patterns in generated code (DD-25, IC-10-03).

        Returns fail_response if skeleton detected, None otherwise.
        """
        for pattern, description in cls.SKELETON_PATTERNS:
            if re.search(pattern, code, re.MULTILINE):
                return cls.fail_response(
                    error=f"Skeleton code detected in {layer}: {description} (DD-25 violation)",
                    fix_hint=f"Complete the {layer} code. Remove placeholders and implement all methods."
                )
        return None

    @classmethod
    def validate_pre(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PRE validation before file save.

        Validates:
        - Step 9 is complete
        - All 4 code blocks present (input_data or state)
        - No skeleton code in any layer (DD-25 final sweep)

        Args:
            input_data: Dict with pom_code, task_code, role_code, test_code

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
        """
        # Check Step 9 completion
        state_manager = cls._get_state_manager()
        if not state_manager.is_step_complete(9):
            return cls.fail_response(
                error="Step 9 is not complete. Cannot proceed to Step 10.",
                fix_hint="Complete Step 9 (Generate Test Runner) first."
            )

        # Validate all 4 code blocks (IC-10-04: fail-fast)
        for field, info in cls.CODE_FIELDS.items():
            error = cls._validate_code_field(
                input_data,
                field,
                info["step"],
                info["layer"]
            )
            if error:
                return error

        return cls.pass_response()

    @classmethod
    def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation entry point.

        Routes to PRE validation only (PRE-only gate per IC-10-02).

        Args:
            input_data: Dict with "mode" field and code fields

        Returns:
            Validation result
        """
        mode = input_data.get("mode", "")

        if not mode:
            return cls.fail_response(
                error="Missing required field: mode",
                fix_hint="Specify mode='PRE' for validation."
            )

        mode_upper = mode.upper() if isinstance(mode, str) else ""

        if mode_upper == "PRE":
            return cls.validate_pre(input_data)
        elif mode_upper == "POST":
            return cls.fail_response(
                error="POST mode not supported. This is a PRE-only gate.",
                fix_hint="Use mode='PRE'. Step 10 validates before save, not after."
            )
        else:
            return cls.fail_response(
                error=f"Invalid mode: '{mode}'. Must be 'PRE'.",
                fix_hint="Specify mode='PRE' for validation."
            )

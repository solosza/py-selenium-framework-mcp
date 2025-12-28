"""
BaseGate - Base class with shared validation utilities for quality gates.

Task 3.0 - Provides common functionality for all quality gates:
- Response formatting (pass/fail)
- Skeleton code detection (DD-25)
- Locator detection (DD-27)
- POM assertion validation (DD-15)
- Required field validation

Task 1.0 - Added audit logging integration:
- Audit logger instance (class-level)
- Automatic logging on pass/fail responses

Task 2.0 - Added self-heal cap enforcement:
- MAX_ATTEMPTS constant (3)
- blocked_response() for capped steps
- State manager integration for attempt tracking
"""

import re
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from utils.audit_logger import AuditLogger
    from utils.state_manager import StateManager


class BaseGate:
    """Base class with shared validation utilities for quality gates."""

    # Task 2.0: Self-heal cap (DD-22)
    MAX_ATTEMPTS = 3

    # Audit logger instance (shared across all gates for a workflow run)
    _audit_logger: Optional["AuditLogger"] = None

    # State manager for attempt tracking (Task 2.0)
    _state_manager: Optional["StateManager"] = None

    # DD-25: Skeleton code patterns to detect
    SKELETON_PATTERNS = [
        (r'^\s*pass\s*$', "Empty 'pass' statement"),
        (r'#\s*Add\s+.*\s+as needed', "Placeholder comment '# Add ... as needed'"),
        (r'#\s*TODO', "TODO comment"),
        (r'#\s*FIXME', "FIXME comment"),
        (r'#\s*XXX', "XXX comment"),
    ]

    # DD-27: Locator patterns to detect
    LOCATOR_PATTERNS = [
        r'from selenium\.webdriver\.common\.by import By',
        r'By\.ID',
        r'By\.CSS_SELECTOR',
        r'By\.XPATH',
        r'By\.CLASS_NAME',
        r'By\.NAME',
        r'By\.TAG_NAME',
        r'By\.LINK_TEXT',
        r'By\.PARTIAL_LINK_TEXT',
    ]

    @classmethod
    def set_audit_logger(cls, logger: Optional["AuditLogger"]) -> None:
        """
        Set the audit logger for all gates.

        Args:
            logger: AuditLogger instance, or None to disable logging.
        """
        cls._audit_logger = logger

    @classmethod
    def get_audit_logger(cls) -> Optional["AuditLogger"]:
        """Get the current audit logger."""
        return cls._audit_logger

    @classmethod
    def set_state_manager(cls, manager: Optional["StateManager"]) -> None:
        """
        Set the state manager for attempt tracking.

        Args:
            manager: StateManager instance, or None to disable tracking.
        """
        cls._state_manager = manager

    @classmethod
    def get_state_manager(cls) -> Optional["StateManager"]:
        """Get the current state manager."""
        return cls._state_manager

    @classmethod
    def blocked_response(
        cls,
        step: int,
        attempts: int,
        errors: List[str]
    ) -> dict:
        """
        Return blocked response when max attempts exceeded (DD-22).

        Args:
            step: Step number that is blocked
            attempts: Number of attempts made
            errors: List of errors from previous attempts

        Returns:
            {"status": "blocked", "step": int, "attempts": int, "errors": list, "fix_hint": str}
        """
        # Log to audit trail if logger set
        if cls._audit_logger:
            cls._audit_logger.log_gate(
                step=step,
                gate_name=f"step_{step}_blocked",
                mode="POST",
                result="blocked",
                error=f"Max attempts ({attempts}) exceeded"
            )

        return {
            "status": "blocked",
            "step": step,
            "attempts": attempts,
            "errors": errors,
            "fix_hint": f"Step {step} blocked after {attempts} attempts. Manual user intervention required (DD-22)."
        }

    @classmethod
    def pass_response(
        cls,
        step: Optional[int] = None,
        gate_name: Optional[str] = None,
        mode: Optional[str] = None,
        source: Optional[str] = None
    ) -> dict:
        """
        Return standard pass response and optionally log to audit trail.

        Args:
            step: Step number (for audit logging)
            gate_name: Gate name (for audit logging)
            mode: Gate mode PRE/POST (for audit logging)
            source: Execution source tool/ai/self-heal (for audit logging)

        Returns:
            {"status": "pass"}
        """
        # Log to audit trail if logger set and context provided
        if cls._audit_logger and step is not None and gate_name is not None:
            cls._audit_logger.log_gate(
                step=step,
                gate_name=gate_name,
                mode=mode or "POST",
                result="pass",
                source=source
            )

        return {"status": "pass"}

    @classmethod
    def fail_response(
        cls,
        error: str,
        fix_hint: str,
        step: Optional[int] = None,
        gate_name: Optional[str] = None,
        mode: Optional[str] = None,
        source: Optional[str] = None
    ) -> dict:
        """
        Return standard fail response and optionally log to audit trail.

        Args:
            error: Error message
            fix_hint: Hint for fixing the issue
            step: Step number (for audit logging)
            gate_name: Gate name (for audit logging)
            mode: Gate mode PRE/POST (for audit logging)
            source: Execution source tool/ai/self-heal (for audit logging)

        Returns:
            {"status": "fail", "error": str, "fix_hint": str}
        """
        # Log to audit trail if logger set and context provided
        if cls._audit_logger and step is not None and gate_name is not None:
            cls._audit_logger.log_gate(
                step=step,
                gate_name=gate_name,
                mode=mode or "POST",
                result="fail",
                error=error,
                source=source
            )

        return {
            "status": "fail",
            "error": error,
            "fix_hint": fix_hint
        }

    @classmethod
    def detect_skeleton_code(cls, code: str) -> List[str]:
        """
        DD-25: Detect skeleton code indicators.

        Returns list of detected skeleton patterns (empty if clean).
        """
        if not code or not code.strip():
            return []

        detected = []
        for pattern, description in cls.SKELETON_PATTERNS:
            if re.search(pattern, code, re.MULTILINE | re.IGNORECASE):
                detected.append(description)

        return detected

    @staticmethod
    def validate_required_fields(data: dict, required: List[str]) -> List[str]:
        """
        Validate that all required fields are present in data.

        Returns list of missing field names (empty if all present).
        """
        if not required:
            return []

        missing = []
        for field in required:
            if field not in data:
                missing.append(field)

        return missing

    @classmethod
    def has_locators(cls, code: str) -> bool:
        """
        DD-27: Detect locator usage in code.

        Returns True if locators (By.*, etc.) are found.
        """
        if not code:
            return False

        for pattern in cls.LOCATOR_PATTERNS:
            if re.search(pattern, code):
                return True

        return False

    @staticmethod
    def validate_pom_assertions(test_code: str) -> bool:
        """
        DD-15: Validate test assertions use POM state methods.

        Returns True if assertions follow pattern: page.is_*, page.has_*, page.get_*
        Returns False if assertions are on return values.
        """
        if not test_code:
            return True

        # Pattern for valid POM assertions: assert <obj>.is_*(), assert <obj>.has_*(), assert <obj>.get_*()
        pom_assertion_pattern = r'assert\s+\w+\.(is_|has_|get_)\w+\('

        # Pattern for invalid assertions on return values: result = ...; assert result
        # or: assert <var> is True/False
        invalid_patterns = [
            r'assert\s+\w+\s+is\s+(True|False)',  # assert result is True
            r'assert\s+\w+\s*==\s*(True|False)',  # assert result == True
        ]

        # Check if there are any assertions in the code
        has_assertions = bool(re.search(r'\bassert\b', test_code))
        if not has_assertions:
            return True  # No assertions to validate

        # Check for invalid patterns first
        for pattern in invalid_patterns:
            if re.search(pattern, test_code):
                return False

        # Check if valid POM assertions exist
        has_valid_pom_assertions = bool(re.search(pom_assertion_pattern, test_code))

        # If code has assertions but none are valid POM assertions, check if
        # it's asserting on a return value stored in a variable
        if not has_valid_pom_assertions:
            # Pattern: result = something(); assert result
            result_assign = re.search(r'(\w+)\s*=\s*\w+\.\w+\(\)', test_code)
            if result_assign:
                var_name = result_assign.group(1)
                if re.search(rf'assert\s+{var_name}\b', test_code):
                    return False

        return True

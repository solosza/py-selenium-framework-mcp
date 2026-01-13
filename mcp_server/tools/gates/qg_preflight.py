"""
QGPreflight - Step 1 Pre-flight Configuration Quality Gate.

Task 4.0 - PD-004: Validates configuration strategy before test generation.

Validates:
- DD-24: credential_strategy (static, dynamic, self-contained, none)
- DD-28: test_data_location (shared, workflow, both, none)

Saves state on PASS via StateManager.
"""

from typing import Dict, Any

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGPreflight(BaseGate):
    """Step 1 quality gate for pre-flight configuration validation."""

    # Valid credential strategies (DD-24)
    VALID_CREDENTIAL_STRATEGIES = ["static", "dynamic", "self-contained", "none"]

    # Valid test data locations (DD-28)
    VALID_TEST_DATA_LOCATIONS = ["shared", "workflow", "both", "none"]

    @classmethod
    def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate pre-flight configuration.

        DEF-052A FIX: Clear stale class variable and session marker from previous
        workflow to ensure fresh run_id for each new workflow. This prevents
        long-running MCP server from reusing old logger across workflows.

        Args:
            input_data: Dict with credential_strategy and test_data_location

        Returns:
            {"status": "pass"} on success
            {"status": "fail", "error": "...", "fix_hint": "..."} on failure
        """
        # DEF-052A: Clear stale session from previous workflow
        cls._audit_logger = None
        cls._clear_session_marker()

        # Check required fields
        missing = cls.validate_required_fields(
            input_data,
            ["credential_strategy", "test_data_location"]
        )

        if missing:
            return cls.fail_response(
                error=f"Missing required field(s): {', '.join(missing)}",
                fix_hint=cls._get_fix_hint_for_missing(missing)
            )

        # Validate credential_strategy (DD-24)
        credential_strategy = input_data.get("credential_strategy")
        if not cls._is_valid_credential_strategy(credential_strategy):
            return cls.fail_response(
                error=f"Invalid credential_strategy: '{credential_strategy}'",
                fix_hint=cls._get_credential_strategy_hint()
            )

        # Validate test_data_location (DD-28)
        test_data_location = input_data.get("test_data_location")
        if not cls._is_valid_test_data_location(test_data_location):
            return cls.fail_response(
                error=f"Invalid test_data_location: '{test_data_location}'",
                fix_hint=cls._get_test_data_location_hint()
            )

        # All valid - save state and return pass
        # Task 9.0: Use per-run state isolation
        audit_logger = cls.get_audit_logger()
        state_manager = StateManager(run_id=audit_logger.run_id)
        state_manager.save(step=1, data={
            "credential_strategy": credential_strategy,
            "test_data_location": test_data_location
        })

        return cls.pass_response(
            step=1,
            gate_name="qg_preflight",
            mode="POST",
            metadata={
                "credential_strategy": credential_strategy,
                "test_data_location": test_data_location
            }
        )

    @classmethod
    def _is_valid_credential_strategy(cls, value: Any) -> bool:
        """Check if credential_strategy is valid."""
        if value is None or value == "":
            return False
        return value in cls.VALID_CREDENTIAL_STRATEGIES

    @classmethod
    def _is_valid_test_data_location(cls, value: Any) -> bool:
        """Check if test_data_location is valid."""
        if value is None or value == "":
            return False
        return value in cls.VALID_TEST_DATA_LOCATIONS

    @staticmethod
    def _get_fix_hint_for_missing(missing_fields: list) -> str:
        """Get fix hint for missing fields."""
        hints = []

        if "credential_strategy" in missing_fields:
            hints.append(
                "Provide credential_strategy: one of "
                "'static', 'dynamic', 'self-contained', or 'none'"
            )

        if "test_data_location" in missing_fields:
            hints.append(
                "Provide test_data_location: one of "
                "'shared', 'workflow', 'both', or 'none'"
            )

        return " | ".join(hints)

    @staticmethod
    def _get_credential_strategy_hint() -> str:
        """Get fix hint for invalid credential_strategy."""
        return (
            "credential_strategy must be one of: "
            "'static' (existing account), "
            "'dynamic' (register fresh user), "
            "'self-contained' (register and use in same test), or "
            "'none' (no credentials needed)"
        )

    @staticmethod
    def _get_test_data_location_hint() -> str:
        """Get fix hint for invalid test_data_location."""
        return (
            "test_data_location must be one of: "
            "'shared' (tests/data/), "
            "'workflow' (tests/{workflow}/data/), "
            "'both' (shared + workflow-specific), or "
            "'none' (no external data)"
        )

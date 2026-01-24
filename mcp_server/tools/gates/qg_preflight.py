"""
QGPreflight - Step 2 Pre-flight Configuration Quality Gate.

Task 4.0 - PD-004: Validates configuration strategy before test generation.

Validates:
- DD-24: credential_strategy (static, dynamic, self-contained, none)
- DD-28: test_data_location (shared, workflow, both, none)

DEF-060: Auto-scaffolds test data infrastructure based on strategy.

Saves state on PASS via StateManager.
"""

from typing import Dict, Any, Optional
from pathlib import Path

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGPreflight(BaseGate):
    """Step 2 quality gate for pre-flight configuration validation."""

    # Valid credential strategies (DD-24)
    VALID_CREDENTIAL_STRATEGIES = ["static", "dynamic", "self-contained", "none"]

    # Valid test data locations (DD-28)
    VALID_TEST_DATA_LOCATIONS = ["shared", "workflow", "both", "none"]

    @classmethod
    def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate pre-flight configuration.

        Args:
            input_data: Dict with credential_strategy, test_data_location,
                       browser_config, timeout_config

        Returns:
            {"status": "pass"} on success
            {"status": "fail", "error": "...", "fix_hint": "..."} on failure
        """
        # Check required fields
        missing = cls.validate_required_fields(
            input_data,
            ["credential_strategy", "test_data_location", "browser_config", "timeout_config"]
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

        # Validate browser_config (FR-8.1)
        browser_config = input_data.get("browser_config")
        browser_error = cls._validate_browser_config(browser_config)
        if browser_error:
            return browser_error

        # Validate timeout_config (FR-8.2)
        timeout_config = input_data.get("timeout_config")
        timeout_error = cls._validate_timeout_config(timeout_config)
        if timeout_error:
            return timeout_error

        # DEF-060: Check test data infrastructure (Phase 1 scaffolding)
        infrastructure_check = cls._check_test_data_infrastructure(
            credential_strategy=credential_strategy,
            test_data_location=test_data_location
        )

        if infrastructure_check:
            return infrastructure_check  # NEEDS_RETRY - AI creates files, retries

        # All valid - use universal completion pattern
        return cls.validate_and_pass(
            step=2,
            step_name="Pre-flight Configuration",
            gate_name="qg_preflight",
            state_data={
                "credential_strategy": credential_strategy,
                "test_data_location": test_data_location,
                "browser_config": browser_config,
                "timeout_config": timeout_config
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

    @classmethod
    def _validate_browser_config(cls, browser_config: Any) -> Optional[Dict[str, Any]]:
        """
        Validate browser_config structure (FR-8.1).

        Args:
            browser_config: Dict with headless field

        Returns:
            fail_response if invalid, None if valid
        """
        if not isinstance(browser_config, dict):
            return cls.fail_response(
                error="browser_config must be a dict",
                fix_hint="browser_config should be: {\"headless\": false}"
            )

        if "headless" not in browser_config:
            return cls.fail_response(
                error="browser_config missing 'headless' field",
                fix_hint="browser_config should be: {\"headless\": false}"
            )

        if browser_config["headless"] is not False:
            return cls.fail_response(
                error="browser_config.headless must be false (pair programming requires visible browser)",
                fix_hint="Set browser_config to: {\"headless\": false}"
            )

        return None

    @classmethod
    def _validate_timeout_config(cls, timeout_config: Any) -> Optional[Dict[str, Any]]:
        """
        Validate timeout_config structure (FR-8.2).

        Args:
            timeout_config: Dict with enabled and threshold_seconds fields

        Returns:
            fail_response if invalid, None if valid
        """
        if not isinstance(timeout_config, dict):
            return cls.fail_response(
                error="timeout_config must be a dict",
                fix_hint="timeout_config should be: {\"enabled\": true, \"threshold_seconds\": 30}"
            )

        if "enabled" not in timeout_config:
            return cls.fail_response(
                error="timeout_config missing 'enabled' field",
                fix_hint="timeout_config should be: {\"enabled\": true, \"threshold_seconds\": 30}"
            )

        if not isinstance(timeout_config["enabled"], bool):
            return cls.fail_response(
                error="timeout_config.enabled must be a boolean",
                fix_hint="Set enabled to true or false"
            )

        if timeout_config["enabled"]:
            if "threshold_seconds" not in timeout_config:
                return cls.fail_response(
                    error="timeout_config missing 'threshold_seconds' field when enabled",
                    fix_hint="timeout_config should be: {\"enabled\": true, \"threshold_seconds\": 30}"
                )

            threshold = timeout_config["threshold_seconds"]
            if not isinstance(threshold, (int, float)) or threshold <= 0:
                return cls.fail_response(
                    error="timeout_config.threshold_seconds must be a positive number",
                    fix_hint="Set threshold_seconds to a positive number (e.g., 30, 60)"
                )

        return None

    @classmethod
    def _check_test_data_infrastructure(
        cls,
        credential_strategy: str,
        test_data_location: str
    ) -> Optional[Dict[str, Any]]:
        """
        Phase 1: Check/create shared test data infrastructure (DEF-060).

        Checks for:
        - tests/data/ directory
        - tests/data/test_users.json (if credential_strategy requires it)

        Args:
            credential_strategy: One of static, dynamic, self-contained, none
            test_data_location: One of shared, workflow, both, none

        Returns:
            None if infrastructure exists
            NEEDS_RETRY dict with scaffolding instructions if missing
        """
        missing = []

        # Check tests/data/ directory exists
        data_dir = Path("tests/data")
        if not data_dir.exists():
            missing.append({
                "type": "directory",
                "path": "tests/data",
                "reason": "Root directory for shared test data"
            })

        # Check credential file based on strategy
        if credential_strategy in ["static", "dynamic"]:
            cred_file = Path("tests/data/test_users.json")
            if not cred_file.exists():
                missing.append({
                    "type": "file",
                    "path": "tests/data/test_users.json",
                    "template": '{\n  "default_user": {\n    "username": "",\n    "password": "",\n    "email": ""\n  }\n}',
                    "reason": "Credential storage for static/dynamic strategies"
                })

        if missing:
            return {
                "status": "NEEDS_RETRY",
                "fix_applied": "test_data_infrastructure_scaffolded",
                "error": "Missing test data infrastructure",
                "message": "Create the following files/directories based on Step 2 config:",
                "scaffolding_needed": missing
            }

        return None

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

        if "browser_config" in missing_fields:
            hints.append(
                "Provide browser_config: {\"headless\": false}"
            )

        if "timeout_config" in missing_fields:
            hints.append(
                "Provide timeout_config: {\"enabled\": true, \"threshold_seconds\": 30}"
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

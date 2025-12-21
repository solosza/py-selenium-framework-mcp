"""
Quality Gate: Test Scenarios (Step 4).

PRE+POST validation gate for Tool 1 (generate_tests_from_user_story).

PRE Validation:
- Step 3 complete (bdd_scenarios, expected_states, intent exist in state)
- metadata_context present with required fields
- workflow is valid (auth, catalog, cart, checkout)

POST Validation:
- test_scenarios present and not empty
- Each scenario has name, given, when, then fields
- No skeleton code patterns (DD-25)
- BDD format validation (DD-23)

Enforces: DD-19, DD-23, DD-25
"""

from typing import Any, Dict, List

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGTestScenarios(BaseGate):
    """Quality gate for Step 4: Test Scenarios generation."""

    # Valid workflow values
    VALID_WORKFLOWS = {"auth", "catalog", "cart", "checkout"}

    # Skeleton patterns to detect in scenarios
    SKELETON_PATTERNS = [
        "pass",
        "# add",
        "# todo",
        "as needed",
        "placeholder",
    ]

    @classmethod
    def _get_state_manager(cls) -> StateManager:
        """Get StateManager instance. Extracted for testing."""
        return StateManager()

    @classmethod
    def validate_pre(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PRE validation before Tool 1 operation.

        Validates:
        - Step 3 is complete
        - metadata_context is present with required fields
        - workflow is valid

        Args:
            input_data: Dict with metadata_context and workflow

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
        """
        # Check Step 3 completion
        state_manager = cls._get_state_manager()
        if not state_manager.is_step_complete(3):
            return cls.fail_response(
                error="Step 3 is not complete. Cannot proceed to Step 4.",
                fix_hint="Complete Step 3 (AI Processing) first. Ensure bdd_scenarios, expected_states, and intent are validated."
            )

        # Check metadata_context present
        metadata_context = input_data.get("metadata_context")
        if not metadata_context:
            return cls.fail_response(
                error="Missing required field: metadata_context",
                fix_hint="Provide metadata_context with bdd_scenarios, expected_states, and intent from Step 3."
            )

        # Validate metadata_context structure
        required_fields = ["bdd_scenarios", "expected_states", "intent"]
        missing = cls.validate_required_fields(metadata_context, required_fields)
        if missing:
            return cls.fail_response(
                error=f"metadata_context missing required fields: {', '.join(missing)}",
                fix_hint=f"Ensure metadata_context includes: {', '.join(required_fields)}"
            )

        # Validate workflow
        workflow = input_data.get("workflow")
        if not workflow:
            return cls.fail_response(
                error="Missing required field: workflow",
                fix_hint=f"Provide workflow value. Valid options: {', '.join(sorted(cls.VALID_WORKFLOWS))}"
            )

        if workflow not in cls.VALID_WORKFLOWS:
            return cls.fail_response(
                error=f"Invalid workflow: '{workflow}'",
                fix_hint=f"Use one of: {', '.join(sorted(cls.VALID_WORKFLOWS))}"
            )

        return cls.pass_response()

    @classmethod
    def validate_post(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST validation after Tool 1 operation.

        Validates:
        - test_scenarios is present and not empty
        - Each scenario has required fields (name, given, when, then)
        - No skeleton code patterns (DD-25)
        - BDD format is valid (DD-23)

        Args:
            input_data: Dict with test_scenarios from Tool 1

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
        """
        test_scenarios = input_data.get("test_scenarios")

        # Check test_scenarios present
        if test_scenarios is None:
            return cls.fail_response(
                error="Missing required field: test_scenarios",
                fix_hint="Tool 1 must return test_scenarios array."
            )

        # Check not empty
        if not isinstance(test_scenarios, list) or len(test_scenarios) == 0:
            return cls.fail_response(
                error="test_scenarios is empty or invalid. At least one scenario required.",
                fix_hint="Retry Tool 1 to generate at least one test scenario."
            )

        # Validate each scenario
        for i, scenario in enumerate(test_scenarios):
            if not isinstance(scenario, dict):
                return cls.fail_response(
                    error=f"Scenario {i} is not a valid object.",
                    fix_hint="Each scenario must be a dictionary with name, given, when, then fields."
                )

            # Check required fields for each scenario
            scenario_errors = cls._validate_scenario_fields(scenario, i)
            if scenario_errors:
                return cls.fail_response(
                    error=scenario_errors,
                    fix_hint="Ensure each scenario has: name (str), given (str), when (list), then (list)."
                )

            # Check for skeleton code (DD-25)
            skeleton_error = cls._check_skeleton_in_scenario(scenario, i)
            if skeleton_error:
                return cls.fail_response(
                    error=skeleton_error,
                    fix_hint="Remove skeleton patterns (pass, # TODO, # Add...as needed). Provide concrete Given/When/Then steps."
                )

        return cls.pass_response()

    @classmethod
    def _validate_scenario_fields(cls, scenario: Dict[str, Any], index: int) -> str:
        """Validate a single scenario has all required fields."""
        required = ["name", "given", "when", "then"]

        for field in required:
            if field not in scenario:
                return f"Scenario {index} missing required field: '{field}'"

        # Validate field types
        if not isinstance(scenario.get("name"), str) or not scenario["name"].strip():
            return f"Scenario {index} 'name' must be a non-empty string"

        if not isinstance(scenario.get("given"), str) or not scenario["given"].strip():
            return f"Scenario {index} 'given' must be a non-empty string"

        when = scenario.get("when")
        if not isinstance(when, list) or len(when) == 0:
            return f"Scenario {index} 'when' must be a non-empty list"

        then = scenario.get("then")
        if not isinstance(then, list) or len(then) == 0:
            return f"Scenario {index} 'then' must be a non-empty list"

        return ""

    @classmethod
    def _check_skeleton_in_scenario(cls, scenario: Dict[str, Any], index: int) -> str:
        """Check for skeleton code patterns in scenario fields."""
        # Check 'given'
        given = scenario.get("given", "").lower()
        for pattern in cls.SKELETON_PATTERNS:
            if pattern in given:
                return f"Scenario {index} 'given' contains skeleton pattern: '{pattern}'"

        # Check 'when' list
        for action in scenario.get("when", []):
            action_lower = str(action).lower()
            for pattern in cls.SKELETON_PATTERNS:
                if pattern in action_lower:
                    return f"Scenario {index} 'when' contains skeleton pattern: '{pattern}'"

        # Check 'then' list
        for assertion in scenario.get("then", []):
            assertion_lower = str(assertion).lower()
            for pattern in cls.SKELETON_PATTERNS:
                if pattern in assertion_lower:
                    return f"Scenario {index} 'then' contains skeleton pattern: '{pattern}'"

        return ""

    @classmethod
    def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation entry point.

        Routes to PRE or POST validation based on mode.

        Args:
            input_data: Dict with "mode" field ("PRE" or "POST") and relevant data

        Returns:
            Validation result
        """
        mode = input_data.get("mode", "").upper()

        if mode == "PRE":
            return cls.validate_pre(input_data)
        elif mode == "POST":
            return cls.validate_post(input_data)
        else:
            return cls.fail_response(
                error=f"Invalid mode: '{mode}'. Must be 'PRE' or 'POST'.",
                fix_hint="Specify mode='PRE' for input validation or mode='POST' for output validation."
            )

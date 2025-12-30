"""
QGAIProcessing - Step 3 AI Processing Quality Gate.

Task 6.0 - PD-006: Validates AI-generated metadata before proceeding to Tool 1.

Validates:
- DD-03: bdd_scenarios (must have valid Given/When/Then structure)
- DD-09: expected_states (at least one state derived from "Then" clauses)
- intent: action verb from requirement (must be present)

Builds metadata_context and saves state on PASS via StateManager.
"""

from typing import Dict, Any, List

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGAIProcessing(BaseGate):
    """Step 3 quality gate for AI-generated metadata validation."""

    @classmethod
    def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate AI-generated metadata.

        Args:
            input_data: Dict with bdd_scenarios, expected_states, intent

        Returns:
            {"status": "pass", "metadata_context": {...}} on success
            {"status": "fail", "error": "...", "fix_hint": "..."} on failure
        """
        # Check required fields
        required_fields = ["bdd_scenarios", "expected_states", "intent"]
        missing = cls.validate_required_fields(input_data, required_fields)

        if missing:
            return cls.fail_response(
                error=f"Missing required field(s): {', '.join(missing)}",
                fix_hint=cls._get_fix_hint_for_missing(missing)
            )

        # Validate bdd_scenarios (DD-03)
        bdd_scenarios = input_data.get("bdd_scenarios")
        bdd_error = cls._validate_bdd_scenarios(bdd_scenarios)
        if bdd_error:
            return cls.fail_response(
                error=bdd_error,
                fix_hint=cls._get_bdd_hint()
            )

        # Validate expected_states (DD-09)
        expected_states = input_data.get("expected_states")
        if not cls._is_valid_expected_states(expected_states):
            return cls.fail_response(
                error="Invalid expected_states: at least one state must be derived from Then clauses",
                fix_hint=cls._get_expected_states_hint()
            )

        # Validate intent
        intent = input_data.get("intent")
        if not cls._is_valid_intent(intent):
            return cls.fail_response(
                error="Invalid intent: must be a non-empty action verb",
                fix_hint=cls._get_intent_hint()
            )

        # All valid - build metadata_context, save state, and return pass
        metadata_context = {
            "bdd_scenarios": bdd_scenarios,
            "expected_states": expected_states,
            "intent": intent
        }

        state_manager = StateManager()
        state_manager.save(step=3, data=metadata_context)

        response = cls.pass_response(step=3, gate_name="qg_ai_processing", mode="POST")
        response["metadata_context"] = metadata_context
        return response

    @classmethod
    def _validate_bdd_scenarios(cls, scenarios: Any) -> str | None:
        """
        Validate BDD scenarios structure.

        Returns error message if invalid, None if valid.
        """
        if scenarios is None or not isinstance(scenarios, list):
            return "bdd_scenarios must be a non-empty list"

        if len(scenarios) == 0:
            return "bdd_scenarios must contain at least one scenario"

        for i, scenario in enumerate(scenarios):
            if not isinstance(scenario, dict):
                return f"bdd_scenarios[{i}] must be a dictionary"

            # Check for 'given' clause
            if "given" not in scenario:
                return f"bdd_scenarios[{i}] missing 'given' clause"

            given = scenario.get("given")
            if not given or (isinstance(given, str) and len(given.strip()) == 0):
                return f"bdd_scenarios[{i}] has empty 'given' clause"

            # Check for 'when' clause
            if "when" not in scenario:
                return f"bdd_scenarios[{i}] missing 'when' clause"

            when = scenario.get("when")
            if not when:
                return f"bdd_scenarios[{i}] has empty 'when' clause"
            if isinstance(when, list) and len(when) == 0:
                return f"bdd_scenarios[{i}] has empty 'when' list"

            # Check for 'then' clause
            if "then" not in scenario:
                return f"bdd_scenarios[{i}] missing 'then' clause"

            then = scenario.get("then")
            if not then:
                return f"bdd_scenarios[{i}] has empty 'then' clause"
            if isinstance(then, list) and len(then) == 0:
                return f"bdd_scenarios[{i}] has empty 'then' list"

        return None

    @classmethod
    def _is_valid_expected_states(cls, value: Any) -> bool:
        """Check if expected_states is valid (DD-09)."""
        if value is None:
            return False
        if not isinstance(value, list):
            return False
        if len(value) == 0:
            return False
        # At least one non-empty state
        return all(isinstance(s, str) and len(s.strip()) > 0 for s in value)

    @classmethod
    def _is_valid_intent(cls, value: Any) -> bool:
        """Check if intent is valid (non-empty string)."""
        if value is None or value == "":
            return False
        return isinstance(value, str) and len(value.strip()) > 0

    @staticmethod
    def _get_fix_hint_for_missing(missing_fields: List[str]) -> str:
        """Get fix hint for missing fields."""
        hints = []

        if "bdd_scenarios" in missing_fields:
            hints.append(
                "Provide bdd_scenarios: list of scenarios with 'given', 'when', 'then' structure"
            )

        if "expected_states" in missing_fields:
            hints.append(
                "Provide expected_states: list of state names derived from 'Then' clauses (e.g., 'is_logged_in', 'is_on_dashboard')"
            )

        if "intent" in missing_fields:
            hints.append(
                "Provide intent: action verb from requirement (e.g., 'login', 'register', 'purchase')"
            )

        return " | ".join(hints)

    @staticmethod
    def _get_bdd_hint() -> str:
        """Get fix hint for invalid BDD scenarios."""
        return (
            "BDD scenarios must have 'given', 'when', 'then' structure. "
            "Example: {'given': 'I am on login page', 'when': ['I enter email', 'I click login'], "
            "'then': ['I should see dashboard']}"
        )

    @staticmethod
    def _get_expected_states_hint() -> str:
        """Get fix hint for invalid expected_states (DD-09)."""
        return (
            "expected_states must have at least one state derived from 'Then' clauses. "
            "Example: ['is_logged_in', 'is_dashboard_visible']. "
            "These become POM state-check methods."
        )

    @staticmethod
    def _get_intent_hint() -> str:
        """Get fix hint for invalid intent."""
        return (
            "intent must be an action verb extracted from the requirement. "
            "Example: 'login', 'register', 'add_to_cart', 'checkout'"
        )

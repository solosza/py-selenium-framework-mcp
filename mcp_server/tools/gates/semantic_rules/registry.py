"""
Central registry for all semantic validation rules.

Part of the Pluggable Semantic Rules Framework.
"""

from typing import List, Dict, Any, Optional
from .base import SemanticRule


class SemanticRuleRegistry:
    """
    Central registry for semantic validation rules.

    Usage:
        # In gate code
        from semantic_rules.registry import SEMANTIC_RULES

        result = SEMANTIC_RULES.check_all(code, context)
        if result:
            return result  # Rule failed, propagate error

    Adding new rules:
        # In registry.py
        from .my_new_rule import MyNewRule
        SEMANTIC_RULES.register(MyNewRule())

        # That's it - rule automatically runs in all gates
    """

    def __init__(self):
        self._rules: List[SemanticRule] = []

    def register(self, rule: SemanticRule):
        """
        Register a new semantic rule.

        Args:
            rule: SemanticRule instance to add to registry

        Note:
            Rules run in registration order. Register most specific
            rules first if order matters.
        """
        self._rules.append(rule)

    def check_all(self, code: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Run all registered rules against code.

        Args:
            code: Generated code to validate
            context: Context dict (Step 1 config, metadata, etc.)

        Returns:
            None if all rules pass
            Dict with error response if any rule fails (first failure returned)

        Note:
            Short-circuits on first failure (fail-fast pattern).
            If rule order matters, register critical rules first.
        """
        for rule in self._rules:
            result = rule.check(code, context)
            if result:  # Rule failed
                # Add rule name to error for debugging
                result["failed_rule"] = rule.name
                return result

        return None  # All rules passed

    def list_rules(self) -> List[Dict[str, str]]:
        """
        List all registered rules.

        Returns:
            List of dicts with rule metadata:
            [{"name": "rule_name", "description": "..."}, ...]

        Useful for debugging and documentation.
        """
        return [
            {"name": rule.name, "description": rule.description}
            for rule in self._rules
        ]


# Global registry instance
# Import this in gate code: from semantic_rules.registry import SEMANTIC_RULES
SEMANTIC_RULES = SemanticRuleRegistry()


# Register rules here (Task 36.5-36.8)
# Rules will be imported and registered as they are implemented

# Task 36.5: FR-14.1 - Parameter contradiction detection
from .contradiction_rule import ParameterContradictionRule
SEMANTIC_RULES.register(ParameterContradictionRule())

# Task 36.6: FR-14.2 - Credential strategy enforcement
from .credential_strategy_rule import CredentialStrategyRule
SEMANTIC_RULES.register(CredentialStrategyRule())

# Task 36.7: FR-14.3 - Test data location enforcement
from .test_data_location_rule import TestDataLocationRule
SEMANTIC_RULES.register(TestDataLocationRule())

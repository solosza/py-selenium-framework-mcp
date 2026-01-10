"""
Semantic Rules Framework - Pluggable semantic validation for generated code.

This package provides extensible semantic validation that grows as new
patterns are discovered in production.

Architecture:
- base.py: SemanticRule abstract base class
- registry.py: SemanticRuleRegistry + global SEMANTIC_RULES instance
- *_rule.py: Individual rule implementations

Usage in gates:
    from semantic_rules.registry import SEMANTIC_RULES

    result = SEMANTIC_RULES.check_all(code, context)
    if result:
        return result  # Rule failed

Adding new rules:
    1. Create new_rule.py implementing SemanticRule
    2. Register in registry.py: SEMANTIC_RULES.register(NewRule())
    3. Update protocols to document new rule
    4. Done - rule runs automatically in all gates
"""

from .base import SemanticRule
from .registry import SemanticRuleRegistry, SEMANTIC_RULES
from .contradiction_rule import ParameterContradictionRule
from .credential_strategy_rule import CredentialStrategyRule
from .test_data_location_rule import TestDataLocationRule

__all__ = [
    "SemanticRule",
    "SemanticRuleRegistry",
    "SEMANTIC_RULES",
    "ParameterContradictionRule",
    "CredentialStrategyRule",
    "TestDataLocationRule",
]

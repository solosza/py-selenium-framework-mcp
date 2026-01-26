"""
Base class for semantic validation rules.

Part of the Pluggable Semantic Rules Framework - allows extensible
semantic validation that grows as new patterns are discovered in production.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class SemanticRule(ABC):
    """
    Abstract base class for semantic validation rules.

    Semantic rules validate MEANING and LOGIC in generated code,
    not just structure (syntax, imports, patterns).

    Examples:
    - Parameter contradictions (from_account == to_account)
    - Strategy violations (Role uses wrong credential strategy)
    - Logic errors (unrealistic test data)

    Usage:
        class MyRule(SemanticRule):
            @property
            def name(self) -> str:
                return "my_rule"

            @property
            def description(self) -> str:
                return "Validates X in generated code"

            def check(self, code: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
                # Validation logic
                if issue_detected:
                    return {
                        "status": "NEEDS_RETRY",
                        "fix_applied": "rule_name_violation",
                        "error": "Description of what's wrong",
                        "message": "Guidance for AI to fix"
                    }
                return None  # Valid
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Rule identifier (e.g., 'parameter_contradiction').

        Used for logging and tracking which rule failed.
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Human-readable rule description.

        Explains what this rule validates and why it matters.
        """
        pass

    @abstractmethod
    def check(self, code: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check code against this semantic rule.

        Args:
            code: Generated code to validate (from Tool 3-6)
            context: Context dict containing:
                - step_1_config: Step 1 strategies (credential_strategy, test_data_location)
                - pom_metadata: POM metadata from Tool 3 (for state methods)
                - task_metadata: Task metadata from Tool 4
                - role_metadata: Role metadata from Tool 5
                - Any other context needed for validation

        Returns:
            None if code is valid (passes semantic check)

            Dict with NEEDS_RETRY response if invalid (auto-fixable):
            {
                "status": "NEEDS_RETRY",
                "fix_applied": "rule_violation_type",
                "error": "What's wrong with the code",
                "message": "How AI should fix it"
            }

            Dict with fail response if invalid (requires manual intervention):
            {
                "status": "fail",
                "error": "What's wrong",
                "teach": "What user needs to do"
            }

        Note:
            Prefer NEEDS_RETRY over fail when possible (Smart Gate pattern).
            Provide actionable guidance in error/message fields.
        """
        pass

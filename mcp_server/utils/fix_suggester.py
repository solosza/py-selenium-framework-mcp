"""
Fix Suggester - Task 5.0

Single Responsibility: "Given error, what fix to try?"

Takes an error category and context, queries the Knowledge Base,
and returns a fix recommendation if a pattern exists.

Design Notes:
- Returns Optional[FixRecommendation] - None means "no known fix"
- When None is returned, AI orchestration (not this module) decides what to do
  (typically: stop, ask user - DD-22 protocol)
- Does NOT apply fixes (that's AI orchestration)
- Thin wrapper around KnowledgeBase for single responsibility

PRD Reference: enhanced-runtime-validation
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from mcp_server.utils.knowledge_base import KnowledgeBase, Pattern


@dataclass
class FixRecommendation:
    """
    A recommended fix for a validation error.

    Attributes:
        fix_action: What action to take (e.g., "wait_for_visibility", "use_js_click")
        fix_details: Additional details/parameters for the fix
            - original_pattern: The Pattern from KB that matched
            - suggested_code: Optional code snippet if applicable
        confidence: How confident we are in this fix (0.0-1.0)
        source: Where this recommendation came from
    """
    fix_action: str
    fix_details: Dict[str, Any]
    confidence: float
    source: str = "knowledge_base"

    @classmethod
    def from_pattern(cls, pattern: Pattern) -> "FixRecommendation":
        """
        Create a FixRecommendation from a Pattern.

        This is the primary way to create recommendations from KB lookups.
        """
        return cls(
            fix_action=cls._extract_action(pattern.fix),
            fix_details={
                "description": pattern.fix,
                "context_matched": pattern.context_match,
                "original_pattern": pattern
            },
            confidence=pattern.confidence,
            source=pattern.source
        )

    @staticmethod
    def _extract_action(fix_description: str) -> str:
        """
        Extract a machine-actionable action from fix description.

        Maps common fix descriptions to action identifiers:
        - "wait for element" -> "wait_for_visibility"
        - "scroll into view" -> "scroll_into_view"
        - "JavaScript click" -> "use_js_click"
        - etc.
        """
        fix_lower = fix_description.lower()

        # Action mappings
        if "wait" in fix_lower and "visibility" in fix_lower:
            return "wait_for_visibility"
        elif "wait" in fix_lower and "enabled" in fix_lower:
            return "wait_for_enabled"
        elif "scroll" in fix_lower:
            return "scroll_into_view"
        elif "javascript" in fix_lower or "js" in fix_lower:
            return "use_js_click"
        elif "re-find" in fix_lower or "refind" in fix_lower:
            return "refind_element"
        elif "selector" in fix_lower:
            return "verify_selector"
        elif "loaded" in fix_lower:
            return "wait_for_page_load"
        else:
            # Default: use the first word as action
            return fix_description.split()[0].lower() if fix_description else "unknown"


class FixSuggester:
    """
    Suggests fixes for validation errors based on Knowledge Base patterns.

    Single Responsibility: Answer "Given this error, what fix should we try?"

    Does NOT:
    - Validate elements (that's RuntimeValidator)
    - Store patterns (that's KnowledgeBase)
    - Apply fixes (that's AI orchestration)

    Usage:
        kb = KnowledgeBase("docs/KNOWLEDGE_BASE.md")
        suggester = FixSuggester(kb)

        recommendation = suggester.suggest_fix("NOT_VISIBLE", {"symptom": "hidden"})
        if recommendation:
            print(f"Try: {recommendation.fix_action}")
        else:
            # No known fix - AI should ask user (DD-22)
            print("No known fix - ask user")
    """

    def __init__(self, kb: KnowledgeBase):
        """
        Initialize FixSuggester with a KnowledgeBase.

        Args:
            kb: KnowledgeBase instance for pattern lookups
        """
        self._kb = kb

    def suggest_fix(
        self,
        error_category: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[FixRecommendation]:
        """
        Suggest a fix for the given error category and context.

        Args:
            error_category: Error category from RuntimeValidator
                (e.g., "LOCATOR_NOT_FOUND", "NOT_VISIBLE", "NOT_INTERACTABLE")
            context: Additional context for matching patterns
                (e.g., {"symptom": "hidden", "element_type": "button"})

        Returns:
            FixRecommendation if a matching pattern exists, None otherwise.

        Note:
            When None is returned, this means "no known fix for this error."
            The caller (AI orchestration) should handle this case - typically
            by stopping and asking the user for guidance (DD-22 protocol).
        """
        pattern = self._kb.find_pattern(error_category, context)

        if pattern is None:
            return None

        return FixRecommendation.from_pattern(pattern)

    def suggest_all_fixes(
        self,
        error_category: str,
        context: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        Suggest all applicable fixes for the error, sorted by confidence.

        Useful when multiple fixes might apply and caller wants options.

        Args:
            error_category: Error category to match
            context: Additional context for matching

        Returns:
            List of FixRecommendation objects, sorted by confidence (highest first).
            Empty list if no patterns match.
        """
        patterns = self._kb.find_all_patterns(error_category, context)

        return [
            FixRecommendation.from_pattern(pattern)
            for pattern in patterns
        ]

    def has_fix_for(self, error_category: str) -> bool:
        """
        Quick check if any fix exists for this error category.

        Useful for reporting/UI to show which errors have known fixes.

        Args:
            error_category: Error category to check

        Returns:
            True if at least one pattern exists for this category
        """
        patterns = self._kb.get_patterns_by_category(error_category)
        return len(patterns) > 0

    @property
    def knowledge_base(self) -> KnowledgeBase:
        """Return the underlying KnowledgeBase."""
        return self._kb


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def suggest_fix_for_error(
    error_category: str,
    context: Optional[Dict[str, Any]] = None,
    kb_path: Optional[str] = None
) -> Optional[FixRecommendation]:
    """
    Convenience function to suggest a fix for an error.

    Args:
        error_category: Error category to match
        context: Additional context for matching
        kb_path: Path to KB file (optional, uses default)

    Returns:
        FixRecommendation if found, None otherwise
    """
    from mcp_server.utils.knowledge_base import load_knowledge_base

    kb = load_knowledge_base(kb_path)
    suggester = FixSuggester(kb)
    return suggester.suggest_fix(error_category, context)


def create_suggester(kb_path: Optional[str] = None) -> FixSuggester:
    """
    Create a FixSuggester with default or specified KB path.

    Args:
        kb_path: Path to KB file (optional, uses default)

    Returns:
        FixSuggester instance
    """
    from mcp_server.utils.knowledge_base import load_knowledge_base

    kb = load_knowledge_base(kb_path)
    return FixSuggester(kb)

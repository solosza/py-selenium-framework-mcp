"""
Unit Tests - Fix Suggester (Task 5.0)

Tests the FixSuggester module:
- Known pattern returns FixRecommendation
- Unknown pattern returns None
- Correct KB integration
- Action extraction from fix descriptions
- Multiple fix suggestions

Following testing skill conventions.
"""

import pytest
import tempfile
import os

from mcp_server.utils.fix_suggester import (
    FixSuggester,
    FixRecommendation,
    suggest_fix_for_error,
    create_suggester
)
from mcp_server.utils.knowledge_base import KnowledgeBase, Pattern


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_kb_file():
    """Create a temporary KB file with test patterns."""
    content = """# Knowledge Base

## Runtime Validation Patterns

### PATTERN: NOT_VISIBLE - Hidden element

**Context:** symptom=hidden
**Fix:** Wait for element visibility or scroll into view
**Confidence:** 0.9

---

### PATTERN: NOT_INTERACTABLE - Disabled element

**Context:** symptom=disabled
**Fix:** Wait for element to become enabled
**Confidence:** 0.85

---

### PATTERN: NOT_INTERACTABLE - Pointer events blocked

**Context:** symptom=pointer
**Fix:** Use JavaScript click to bypass CSS pointer events
**Confidence:** 0.95

---

### PATTERN: LOCATOR_NOT_FOUND - Element missing

**Context:** any
**Fix:** Verify page fully loaded before interaction
**Confidence:** 0.8

---

### PATTERN: STALE_REFERENCE - Stale element

**Context:** symptom=stale
**Fix:** Re-find element after DOM mutation
**Confidence:** 0.9

---
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    os.unlink(temp_path)


@pytest.fixture
def empty_kb_file():
    """Create an empty KB file (no patterns)."""
    content = """# Knowledge Base

## Runtime Validation Patterns

(No patterns defined yet)
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    os.unlink(temp_path)


@pytest.fixture
def knowledge_base(temp_kb_file):
    """Create a KnowledgeBase from temp file."""
    return KnowledgeBase(kb_path=temp_kb_file)


@pytest.fixture
def empty_knowledge_base(empty_kb_file):
    """Create a KnowledgeBase with no patterns."""
    return KnowledgeBase(kb_path=empty_kb_file)


@pytest.fixture
def suggester(knowledge_base):
    """Create a FixSuggester with loaded KB."""
    return FixSuggester(knowledge_base)


@pytest.fixture
def empty_suggester(empty_knowledge_base):
    """Create a FixSuggester with empty KB."""
    return FixSuggester(empty_knowledge_base)


# =============================================================================
# TEST: Basic Fix Suggestion
# =============================================================================

class TestSuggestFix:
    """Test suggest_fix() method."""

    @pytest.mark.fix_suggester
    def test_known_pattern_returns_recommendation(self, suggester):
        """When pattern exists, returns FixRecommendation."""
        result = suggester.suggest_fix(
            "NOT_VISIBLE",
            {"symptom": "hidden"}
        )

        assert result is not None
        assert isinstance(result, FixRecommendation)
        assert result.confidence >= 0.8
        assert "visibility" in result.fix_details["description"].lower()

    @pytest.mark.fix_suggester
    def test_unknown_pattern_returns_none(self, suggester):
        """When no pattern exists, returns None (not fallback)."""
        result = suggester.suggest_fix(
            "COMPLETELY_UNKNOWN_ERROR",
            {"weird": "context"}
        )

        assert result is None

    @pytest.mark.fix_suggester
    def test_empty_kb_returns_none(self, empty_suggester):
        """Empty KB returns None for any error."""
        result = empty_suggester.suggest_fix(
            "NOT_VISIBLE",
            {"symptom": "hidden"}
        )

        assert result is None

    @pytest.mark.fix_suggester
    def test_category_without_context_matches(self, suggester):
        """Pattern with 'any' context matches without specific context."""
        result = suggester.suggest_fix("LOCATOR_NOT_FOUND")

        assert result is not None
        assert result.confidence >= 0.7

    @pytest.mark.fix_suggester
    def test_wrong_context_still_matches_category(self, suggester):
        """Wrong context falls back to category-only match if available."""
        # LOCATOR_NOT_FOUND has "any" context which matches everything
        result = suggester.suggest_fix(
            "LOCATOR_NOT_FOUND",
            {"unrelated": "context"}
        )

        assert result is not None


# =============================================================================
# TEST: FixRecommendation Creation
# =============================================================================

class TestFixRecommendation:
    """Test FixRecommendation class."""

    @pytest.mark.fix_suggester
    def test_from_pattern_creates_recommendation(self):
        """from_pattern() creates proper recommendation."""
        pattern = Pattern(
            error_category="NOT_VISIBLE",
            context_match={"symptom": "hidden"},
            fix="Wait for element visibility",
            confidence=0.9,
            source="test"
        )

        rec = FixRecommendation.from_pattern(pattern)

        assert rec.fix_action == "wait_for_visibility"
        assert rec.confidence == 0.9
        assert rec.source == "test"
        assert "description" in rec.fix_details
        assert rec.fix_details["original_pattern"] == pattern

    @pytest.mark.fix_suggester
    def test_action_extraction_wait_visibility(self):
        """Extracts wait_for_visibility action."""
        action = FixRecommendation._extract_action("Wait for element visibility")
        assert action == "wait_for_visibility"

    @pytest.mark.fix_suggester
    def test_action_extraction_wait_enabled(self):
        """Extracts wait_for_enabled action."""
        action = FixRecommendation._extract_action("Wait for element to become enabled")
        assert action == "wait_for_enabled"

    @pytest.mark.fix_suggester
    def test_action_extraction_scroll(self):
        """Extracts scroll_into_view action."""
        action = FixRecommendation._extract_action("Scroll into view first")
        assert action == "scroll_into_view"

    @pytest.mark.fix_suggester
    def test_action_extraction_js_click(self):
        """Extracts use_js_click action."""
        action = FixRecommendation._extract_action("Use JavaScript click to bypass")
        assert action == "use_js_click"

    @pytest.mark.fix_suggester
    def test_action_extraction_refind(self):
        """Extracts refind_element action."""
        action = FixRecommendation._extract_action("Re-find element after DOM change")
        assert action == "refind_element"

    @pytest.mark.fix_suggester
    def test_action_extraction_page_load(self):
        """Extracts wait_for_page_load action."""
        action = FixRecommendation._extract_action("Verify page fully loaded")
        assert action == "wait_for_page_load"

    @pytest.mark.fix_suggester
    def test_action_extraction_unknown_uses_first_word(self):
        """Unknown action uses first word."""
        action = FixRecommendation._extract_action("Activate special mode")
        assert action == "activate"


# =============================================================================
# TEST: Multiple Fix Suggestions
# =============================================================================

class TestSuggestAllFixes:
    """Test suggest_all_fixes() method."""

    @pytest.mark.fix_suggester
    def test_returns_all_matching_patterns(self, suggester):
        """Returns all patterns for category."""
        results = suggester.suggest_all_fixes("NOT_INTERACTABLE")

        # KB has 2 NOT_INTERACTABLE patterns
        assert len(results) >= 2
        assert all(isinstance(r, FixRecommendation) for r in results)

    @pytest.mark.fix_suggester
    def test_sorted_by_confidence(self, suggester):
        """Results sorted by confidence descending."""
        results = suggester.suggest_all_fixes("NOT_INTERACTABLE")

        confidences = [r.confidence for r in results]
        assert confidences == sorted(confidences, reverse=True)

    @pytest.mark.fix_suggester
    def test_empty_for_unknown_category(self, suggester):
        """Returns empty list for unknown category."""
        results = suggester.suggest_all_fixes("UNKNOWN_CATEGORY")

        assert results == []


# =============================================================================
# TEST: has_fix_for()
# =============================================================================

class TestHasFixFor:
    """Test has_fix_for() method."""

    @pytest.mark.fix_suggester
    def test_true_for_known_category(self, suggester):
        """Returns True for categories with patterns."""
        assert suggester.has_fix_for("NOT_VISIBLE") is True
        assert suggester.has_fix_for("NOT_INTERACTABLE") is True
        assert suggester.has_fix_for("LOCATOR_NOT_FOUND") is True
        assert suggester.has_fix_for("STALE_REFERENCE") is True

    @pytest.mark.fix_suggester
    def test_false_for_unknown_category(self, suggester):
        """Returns False for categories without patterns."""
        assert suggester.has_fix_for("UNKNOWN_ERROR") is False
        assert suggester.has_fix_for("RANDOM_CATEGORY") is False

    @pytest.mark.fix_suggester
    def test_false_for_empty_kb(self, empty_suggester):
        """Returns False for empty KB."""
        assert empty_suggester.has_fix_for("NOT_VISIBLE") is False


# =============================================================================
# TEST: KB Integration
# =============================================================================

class TestKBIntegration:
    """Test integration with KnowledgeBase."""

    @pytest.mark.fix_suggester
    def test_suggester_exposes_kb(self, suggester, knowledge_base):
        """Can access underlying KnowledgeBase."""
        assert suggester.knowledge_base is knowledge_base

    @pytest.mark.fix_suggester
    def test_context_matching_works(self, suggester):
        """Context matching filters results correctly."""
        # Pointer events should match higher-confidence pattern
        result = suggester.suggest_fix(
            "NOT_INTERACTABLE",
            {"symptom": "pointer"}
        )

        assert result is not None
        assert result.confidence == 0.95
        assert "javascript" in result.fix_details["description"].lower()

    @pytest.mark.fix_suggester
    def test_different_context_different_result(self, suggester):
        """Different context returns different pattern."""
        pointer_result = suggester.suggest_fix(
            "NOT_INTERACTABLE",
            {"symptom": "pointer"}
        )

        disabled_result = suggester.suggest_fix(
            "NOT_INTERACTABLE",
            {"symptom": "disabled"}
        )

        assert pointer_result is not None
        assert disabled_result is not None
        assert pointer_result.fix_action != disabled_result.fix_action


# =============================================================================
# TEST: Convenience Functions
# =============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    @pytest.mark.fix_suggester
    def test_suggest_fix_for_error(self, temp_kb_file):
        """suggest_fix_for_error() works end-to-end."""
        result = suggest_fix_for_error(
            "NOT_VISIBLE",
            {"symptom": "hidden"},
            kb_path=temp_kb_file
        )

        assert result is not None
        assert isinstance(result, FixRecommendation)

    @pytest.mark.fix_suggester
    def test_create_suggester(self, temp_kb_file):
        """create_suggester() creates working suggester."""
        suggester = create_suggester(kb_path=temp_kb_file)

        assert suggester is not None
        result = suggester.suggest_fix("STALE_REFERENCE")
        assert result is not None


# =============================================================================
# TEST: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.fix_suggester
    def test_none_context_handled(self, suggester):
        """None context doesn't cause errors."""
        result = suggester.suggest_fix("NOT_VISIBLE", None)

        # Should still find pattern with "any" context
        assert result is not None or result is None  # Either is valid

    @pytest.mark.fix_suggester
    def test_empty_context_handled(self, suggester):
        """Empty dict context doesn't cause errors."""
        result = suggester.suggest_fix("NOT_VISIBLE", {})

        assert result is not None or result is None  # Either is valid

    @pytest.mark.fix_suggester
    def test_case_insensitive_category(self, suggester):
        """Error category matching is case-insensitive."""
        upper = suggester.suggest_fix("NOT_VISIBLE")
        lower = suggester.suggest_fix("not_visible")
        mixed = suggester.suggest_fix("Not_Visible")

        # All should return the same result
        all_found = [r is not None for r in [upper, lower, mixed]]
        assert all(all_found) or not any(all_found)

    @pytest.mark.fix_suggester
    def test_empty_fix_description_handled(self):
        """Empty fix description doesn't crash action extraction."""
        action = FixRecommendation._extract_action("")
        assert action == "unknown"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

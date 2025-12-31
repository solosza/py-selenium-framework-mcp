"""
Unit tests for KnowledgeBase - Task 4.0

Test suite for knowledge base read/write operations.

Test Matrix:
- Pattern dataclass: 4 tests (P0)
- Find patterns: 5 tests (P0)
- Save patterns: 3 tests (P0)
- Parse KB file: 4 tests (P1)
- Convenience functions: 2 tests (P1)

Testing Skill Reference: .claude/skills/testing/
"""

import pytest
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.knowledge_base import (
    KnowledgeBase,
    Pattern,
    load_knowledge_base,
    find_pattern_for_error
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def temp_kb_file():
    """Create a temporary KB file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("""# Knowledge Base

## Runtime Validation Patterns

### PATTERN: NOT_INTERACTABLE - Pointer events blocked

**Context:** symptom=pointer events
**Fix:** Use JavaScript click (click_js) to bypass
**Confidence:** 0.9

---

### PATTERN: LOCATOR_NOT_FOUND - Element timing

**Context:** symptom=timing
**Fix:** Add explicit wait before interaction
**Confidence:** 0.7

---

### PATTERN: NOT_VISIBLE - Hidden element

**Context:** element_type=modal
**Fix:** Wait for modal to become visible
**Confidence:** 0.85

---

## Adding New Patterns

Document patterns here.
""")
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def empty_kb_file():
    """Create an empty KB file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Knowledge Base\n\nEmpty knowledge base.\n")
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def legacy_kb_file():
    """Create a KB file with legacy patterns only."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("""# Knowledge Base

## Specific Patterns

### Pointer Events Interception

**Problem:** Click fails with "element intercepts pointer events"

**Solution:** Use JavaScript click to bypass.

---
""")
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def sample_pattern():
    """Sample pattern for testing."""
    return Pattern(
        error_category="NOT_INTERACTABLE",
        context_match={"symptom": "disabled"},
        fix="Wait for element to be enabled",
        confidence=0.8,
        source="test"
    )


# =============================================================================
# PATTERN DATACLASS TESTS
# =============================================================================

class TestPatternDataclass:
    """
    Tests for Pattern dataclass.

    Verifies:
    - Basic creation
    - Context matching logic
    - Default values
    """

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_pattern_creation(self):
        """
        P0: Verify Pattern creation with all fields.

        AAA Pattern:
        1. Arrange - Pattern data
        2. Act - Create Pattern
        3. Assert - All fields set correctly
        """
        # Arrange/Act
        pattern = Pattern(
            error_category="NOT_VISIBLE",
            context_match={"element": "button"},
            fix="Scroll element into view",
            confidence=0.85,
            source="test"
        )

        # Assert
        assert pattern.error_category == "NOT_VISIBLE"
        assert pattern.context_match == {"element": "button"}
        assert pattern.fix == "Scroll element into view"
        assert pattern.confidence == 0.85
        assert pattern.source == "test"

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_pattern_default_values(self):
        """
        P0: Verify Pattern has correct defaults.

        AAA Pattern:
        1. Arrange - Minimal pattern data
        2. Act - Create Pattern
        3. Assert - Defaults applied
        """
        # Arrange/Act
        pattern = Pattern(
            error_category="LOCATOR_NOT_FOUND",
            context_match={},
            fix="Check selector"
        )

        # Assert
        assert pattern.confidence == 0.8, "Default confidence should be 0.8"
        assert pattern.source == "kb_file", "Default source should be 'kb_file'"

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_pattern_matches_context_exact(self):
        """
        P0: Verify context matching with exact match.

        AAA Pattern:
        1. Arrange - Pattern with context_match
        2. Act - Check matching contexts
        3. Assert - Matches when context contains required keys
        """
        # Arrange
        pattern = Pattern(
            error_category="NOT_INTERACTABLE",
            context_match={"symptom": "disabled"},
            fix="Wait for enabled"
        )

        # Act/Assert - Exact match
        assert pattern.matches_context({"symptom": "disabled"}) is True

        # Act/Assert - Superset match (has extra keys)
        assert pattern.matches_context(
            {"symptom": "disabled", "element": "button"}
        ) is True

        # Act/Assert - Partial match (case insensitive)
        assert pattern.matches_context({"symptom": "element is DISABLED"}) is True

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_pattern_matches_context_no_match(self):
        """
        P0: Verify context matching returns False when no match.

        AAA Pattern:
        1. Arrange - Pattern with context_match
        2. Act - Check non-matching contexts
        3. Assert - Returns False
        """
        # Arrange
        pattern = Pattern(
            error_category="NOT_INTERACTABLE",
            context_match={"symptom": "disabled"},
            fix="Wait for enabled"
        )

        # Act/Assert - Missing key
        assert pattern.matches_context({"other_key": "value"}) is False

        # Act/Assert - Wrong value
        assert pattern.matches_context({"symptom": "visible"}) is False

        # Act/Assert - Empty context
        assert pattern.matches_context({}) is False


# =============================================================================
# FIND PATTERNS TESTS
# =============================================================================

class TestKnowledgeBaseFindPatterns:
    """
    Tests for finding patterns in KnowledgeBase.

    Verifies:
    - Find by error category
    - Find with context matching
    - Returns None when not found
    - Returns highest confidence match
    """

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_find_pattern_by_category(self, temp_kb_file):
        """
        P0: Verify finding pattern by error category.

        AAA Pattern:
        1. Arrange - KB with patterns
        2. Act - Find by category
        3. Assert - Returns matching pattern
        """
        # Arrange
        kb = KnowledgeBase(kb_path=temp_kb_file)

        # Act
        pattern = kb.find_pattern("NOT_INTERACTABLE")

        # Assert
        assert pattern is not None, "Should find NOT_INTERACTABLE pattern"
        assert pattern.error_category == "NOT_INTERACTABLE"

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_find_pattern_with_context(self, temp_kb_file):
        """
        P0: Verify finding pattern with context matching.

        AAA Pattern:
        1. Arrange - KB with patterns
        2. Act - Find with matching context
        3. Assert - Returns pattern matching context
        """
        # Arrange
        kb = KnowledgeBase(kb_path=temp_kb_file)

        # Act
        pattern = kb.find_pattern(
            "LOCATOR_NOT_FOUND",
            {"symptom": "timing issue"}
        )

        # Assert
        assert pattern is not None
        assert pattern.error_category == "LOCATOR_NOT_FOUND"
        assert "wait" in pattern.fix.lower()

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_find_pattern_returns_none_when_not_found(self, temp_kb_file):
        """
        P0: Verify None returned when no pattern matches.

        AAA Pattern:
        1. Arrange - KB with patterns
        2. Act - Find non-existent category
        3. Assert - Returns None
        """
        # Arrange
        kb = KnowledgeBase(kb_path=temp_kb_file)

        # Act
        pattern = kb.find_pattern("NON_EXISTENT_CATEGORY")

        # Assert
        assert pattern is None, "Should return None for unknown category"

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_find_pattern_returns_highest_confidence(self, temp_kb_file):
        """
        P0: Verify highest confidence pattern is returned.

        AAA Pattern:
        1. Arrange - KB with multiple patterns for same category
        2. Act - Find pattern
        3. Assert - Returns highest confidence match
        """
        # Arrange
        kb = KnowledgeBase(kb_path=temp_kb_file)
        # Add a lower confidence pattern
        kb._patterns.append(Pattern(
            error_category="NOT_INTERACTABLE",
            context_match={},
            fix="Low confidence fix",
            confidence=0.5
        ))

        # Act
        pattern = kb.find_pattern("NOT_INTERACTABLE")

        # Assert
        assert pattern is not None
        assert pattern.confidence >= 0.9, \
            f"Should return highest confidence (0.9), got {pattern.confidence}"

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_find_all_patterns(self, temp_kb_file):
        """
        P0: Verify finding all matching patterns.

        AAA Pattern:
        1. Arrange - KB with multiple patterns
        2. Act - Find all for category
        3. Assert - Returns list sorted by confidence
        """
        # Arrange
        kb = KnowledgeBase(kb_path=temp_kb_file)
        # Add another pattern
        kb._patterns.append(Pattern(
            error_category="NOT_INTERACTABLE",
            context_match={},
            fix="Alternative fix",
            confidence=0.6
        ))

        # Act
        patterns = kb.find_all_patterns("NOT_INTERACTABLE")

        # Assert
        assert len(patterns) >= 2, "Should find multiple patterns"
        assert patterns[0].confidence >= patterns[-1].confidence, \
            "Should be sorted by confidence descending"


# =============================================================================
# SAVE PATTERNS TESTS
# =============================================================================

class TestKnowledgeBaseSavePatterns:
    """
    Tests for saving patterns to KnowledgeBase.

    Verifies:
    - Pattern saved to memory
    - Pattern appended to file
    - File format is correct
    """

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_save_pattern_to_memory(self, temp_kb_file, sample_pattern):
        """
        P0: Verify pattern saved to in-memory list.

        AAA Pattern:
        1. Arrange - KB and new pattern
        2. Act - Save pattern
        3. Assert - Pattern in memory
        """
        # Arrange
        kb = KnowledgeBase(kb_path=temp_kb_file)
        initial_count = len(kb.get_all_patterns())

        # Act
        kb.save_pattern(sample_pattern)

        # Assert
        assert len(kb.get_all_patterns()) == initial_count + 1
        assert sample_pattern in kb.get_all_patterns()

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_save_pattern_to_file(self, temp_kb_file, sample_pattern):
        """
        P0: Verify pattern appended to file.

        AAA Pattern:
        1. Arrange - KB and new pattern
        2. Act - Save pattern
        3. Assert - Pattern in file content
        """
        # Arrange
        kb = KnowledgeBase(kb_path=temp_kb_file)

        # Act
        kb.save_pattern(sample_pattern)

        # Assert - Read file and check
        content = Path(temp_kb_file).read_text(encoding="utf-8")
        assert sample_pattern.error_category in content
        assert sample_pattern.fix in content
        assert str(sample_pattern.confidence) in content

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_save_pattern_creates_section_if_missing(self, empty_kb_file, sample_pattern):
        """
        P0: Verify section created if missing.

        AAA Pattern:
        1. Arrange - Empty KB file
        2. Act - Save pattern
        3. Assert - Section created in file
        """
        # Arrange
        kb = KnowledgeBase(kb_path=empty_kb_file)

        # Act
        kb.save_pattern(sample_pattern)

        # Assert
        content = Path(empty_kb_file).read_text(encoding="utf-8")
        assert "## Runtime Validation Patterns" in content
        assert sample_pattern.fix in content


# =============================================================================
# PARSE KB FILE TESTS
# =============================================================================

class TestKnowledgeBaseParsing:
    """
    Tests for parsing KB file.

    Verifies:
    - Structured patterns parsed correctly
    - Legacy patterns parsed
    - Handles missing file
    """

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_parse_structured_patterns(self, temp_kb_file):
        """
        P1: Verify structured patterns parsed from file.

        AAA Pattern:
        1. Arrange - KB file with structured patterns
        2. Act - Load KB
        3. Assert - Patterns parsed correctly
        """
        # Arrange/Act
        kb = KnowledgeBase(kb_path=temp_kb_file)

        # Assert
        patterns = kb.get_all_patterns()
        assert len(patterns) >= 3, f"Should parse 3 patterns, got {len(patterns)}"

        # Check specific pattern
        not_interactable = kb.find_pattern("NOT_INTERACTABLE")
        assert not_interactable is not None
        assert not_interactable.confidence == 0.9

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_parse_legacy_patterns(self, legacy_kb_file):
        """
        P1: Verify legacy patterns parsed from file.

        AAA Pattern:
        1. Arrange - KB file with legacy patterns only
        2. Act - Load KB
        3. Assert - Legacy patterns extracted
        """
        # Arrange/Act
        kb = KnowledgeBase(kb_path=legacy_kb_file)

        # Assert - Find by category only (legacy patterns may have specific context)
        pattern = kb.find_pattern("NOT_INTERACTABLE")
        assert pattern is not None, "Should parse legacy pointer events pattern"
        assert "javascript" in pattern.fix.lower() or "click_js" in pattern.fix.lower()

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_handles_missing_file(self):
        """
        P1: Verify graceful handling of missing file.

        AAA Pattern:
        1. Arrange - Non-existent file path
        2. Act - Load KB
        3. Assert - No error, empty patterns
        """
        # Arrange/Act
        kb = KnowledgeBase(kb_path="/non/existent/path.md")

        # Assert
        assert len(kb.get_all_patterns()) == 0
        assert kb.find_pattern("ANY") is None

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_reload_patterns(self, temp_kb_file, sample_pattern):
        """
        P1: Verify reload refreshes patterns from file.

        AAA Pattern:
        1. Arrange - KB loaded, then modified
        2. Act - Reload
        3. Assert - Patterns refreshed
        """
        # Arrange
        kb = KnowledgeBase(kb_path=temp_kb_file)
        initial_count = len(kb.get_all_patterns())

        # Add pattern to file directly
        kb.save_pattern(sample_pattern)

        # Create new KB to simulate external modification
        kb2 = KnowledgeBase(kb_path=temp_kb_file)

        # Assert
        assert len(kb2.get_all_patterns()) == initial_count + 1


# =============================================================================
# CONVENIENCE FUNCTIONS TESTS
# =============================================================================

class TestConvenienceFunctions:
    """
    Tests for convenience functions.

    Verifies:
    - load_knowledge_base()
    - find_pattern_for_error()
    """

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_load_knowledge_base(self, temp_kb_file):
        """
        P1: Verify load_knowledge_base convenience function.

        AAA Pattern:
        1. Arrange - KB file path
        2. Act - Load KB
        3. Assert - Returns KnowledgeBase instance
        """
        # Act
        kb = load_knowledge_base(temp_kb_file)

        # Assert
        assert isinstance(kb, KnowledgeBase)
        assert len(kb.get_all_patterns()) > 0

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_find_pattern_for_error(self, temp_kb_file):
        """
        P1: Verify find_pattern_for_error convenience function.

        AAA Pattern:
        1. Arrange - KB file with patterns
        2. Act - Find pattern
        3. Assert - Returns matching pattern
        """
        # Act
        pattern = find_pattern_for_error(
            "NOT_INTERACTABLE",
            kb_path=temp_kb_file
        )

        # Assert
        assert pattern is not None
        assert pattern.error_category == "NOT_INTERACTABLE"


# =============================================================================
# GET PATTERNS BY CATEGORY TESTS
# =============================================================================

class TestGetPatternsByCategory:
    """
    Tests for get_patterns_by_category method.
    """

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_get_patterns_by_category(self, temp_kb_file):
        """
        P1: Verify get_patterns_by_category returns correct patterns.

        AAA Pattern:
        1. Arrange - KB with multiple categories
        2. Act - Get patterns for one category
        3. Assert - Only returns matching category
        """
        # Arrange
        kb = KnowledgeBase(kb_path=temp_kb_file)

        # Act
        patterns = kb.get_patterns_by_category("NOT_VISIBLE")

        # Assert
        assert all(p.error_category == "NOT_VISIBLE" for p in patterns)

    @pytest.mark.unit
    @pytest.mark.knowledge_base
    def test_get_patterns_by_category_case_insensitive(self, temp_kb_file):
        """
        P1: Verify category matching is case insensitive.

        AAA Pattern:
        1. Arrange - KB with patterns
        2. Act - Get patterns with different case
        3. Assert - Returns patterns regardless of case
        """
        # Arrange
        kb = KnowledgeBase(kb_path=temp_kb_file)

        # Act
        patterns_upper = kb.get_patterns_by_category("NOT_VISIBLE")
        patterns_lower = kb.get_patterns_by_category("not_visible")

        # Assert
        assert len(patterns_upper) == len(patterns_lower)

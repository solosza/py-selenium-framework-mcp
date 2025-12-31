"""
Unit tests for RuntimeValidator - Task 3.0

Test suite for runtime element validation with error categorization.

Test Matrix:
- Happy path: 5 tests (P0)
- Error categories: 5 tests (P0) - one per category
- Edge cases: 4 tests (P1)
- Convenience functions: 2 tests (P1)

Testing Skill Reference: .claude/skills/testing/
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.runtime_validator import (
    RuntimeValidator,
    ValidationResult,
    ErrorCategory,
    ElementInfo,
    validate_element,
    validate_elements
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def sample_snapshot():
    """Sample Playwright accessibility snapshot with various elements."""
    return {
        "role": "document",
        "name": "Test Page",
        "children": [
            {
                "role": "button",
                "name": "Submit Form",
                "ref": "S1.B1",
                "disabled": False
            },
            {
                "role": "textbox",
                "name": "Email Address",
                "ref": "S1.T1",
                "disabled": False
            },
            {
                "role": "button",
                "name": "Disabled Button",
                "ref": "S1.B2",
                "disabled": True
            },
            {
                "role": "link",
                "name": "Hidden Link",
                "ref": "S1.L1",
                "hidden": True
            },
            {
                "role": "heading",
                "name": "Welcome Header",
                "ref": "S1.H1"
            }
        ]
    }


@pytest.fixture
def empty_snapshot():
    """Empty snapshot with no elements."""
    return {"role": "document", "name": "Empty Page", "children": []}


@pytest.fixture
def nested_snapshot():
    """Snapshot with nested elements."""
    return {
        "role": "document",
        "name": "Nested Page",
        "children": [
            {
                "role": "navigation",
                "name": "Main Nav",
                "ref": "S1.N1",
                "children": [
                    {
                        "role": "link",
                        "name": "Home",
                        "ref": "S1.N1.L1"
                    },
                    {
                        "role": "link",
                        "name": "About",
                        "ref": "S1.N1.L2"
                    }
                ]
            },
            {
                "role": "main",
                "name": "Content",
                "children": [
                    {
                        "role": "button",
                        "name": "Click Me",
                        "ref": "S2.B1"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def validator():
    """Basic RuntimeValidator instance."""
    return RuntimeValidator()


@pytest.fixture
def validator_with_snapshot_fn(sample_snapshot):
    """Validator with snapshot function."""
    return RuntimeValidator(snapshot_fn=lambda: sample_snapshot)


# =============================================================================
# HAPPY PATH TESTS
# =============================================================================

class TestRuntimeValidatorHappyPath:
    """
    Happy path tests for RuntimeValidator.

    Verifies core functionality works correctly:
    - Valid element detection
    - Correct result structure
    - Proper element info extraction
    """

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_valid_element_by_ref(self, validator, sample_snapshot):
        """
        P0: Verify valid element found by exact ref returns valid result.

        AAA Pattern:
        1. Arrange - Sample snapshot with element ref S1.B1
        2. Act - Validate element with ref locator
        3. Assert - Returns is_valid=True, no error category
        """
        # Arrange
        locator = "S1.B1"

        # Act
        result = validator.validate_element_from_snapshot(
            sample_snapshot, locator
        )

        # Assert
        assert result.is_valid is True, \
            "Valid element should return is_valid=True"
        assert result.error_category is None, \
            "Valid element should have no error category"
        assert result.details["locator"] == locator, \
            f"Details should contain locator, got {result.details}"

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_valid_element_by_name(self, validator, sample_snapshot):
        """
        P0: Verify valid element found by name returns valid result.

        AAA Pattern:
        1. Arrange - Sample snapshot with element name "Submit Form"
        2. Act - Validate element with name locator
        3. Assert - Returns is_valid=True
        """
        # Arrange
        locator = "Submit Form"

        # Act
        result = validator.validate_element_from_snapshot(
            sample_snapshot, locator
        )

        # Assert
        assert result.is_valid is True, \
            "Element found by name should be valid"
        assert result.error_category is None

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_valid_element_by_role_name(self, validator, sample_snapshot):
        """
        P0: Verify valid element found by role:name pattern.

        AAA Pattern:
        1. Arrange - Sample snapshot with button role and name
        2. Act - Validate with role:name pattern
        3. Assert - Returns is_valid=True
        """
        # Arrange
        locator = "button:Submit"

        # Act
        result = validator.validate_element_from_snapshot(
            sample_snapshot, locator
        )

        # Assert
        assert result.is_valid is True, \
            "Element found by role:name pattern should be valid"

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_valid_element_has_element_info(self, validator, sample_snapshot):
        """
        P0: Verify valid result includes element info.

        AAA Pattern:
        1. Arrange - Sample snapshot
        2. Act - Validate valid element
        3. Assert - Details contain element_info with role/name
        """
        # Arrange
        locator = "S1.B1"

        # Act
        result = validator.validate_element_from_snapshot(
            sample_snapshot, locator
        )

        # Assert
        assert "element_info" in result.details, \
            "Valid result should include element_info"
        element_info = result.details["element_info"]
        assert element_info.get("role") == "button", \
            f"Element info should have role, got {element_info}"

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_validation_result_valid_factory(self):
        """
        P0: Verify ValidationResult.valid() creates correct result.

        AAA Pattern:
        1. Arrange - Locator and element info
        2. Act - Create valid result
        3. Assert - Result has correct structure
        """
        # Arrange
        locator = "test-locator"
        element_info = {"role": "button", "name": "Test"}

        # Act
        result = ValidationResult.valid(locator, element_info)

        # Assert
        assert result.is_valid is True
        assert result.error_category is None
        assert result.details["locator"] == locator
        assert result.details["element_info"] == element_info


# =============================================================================
# ERROR CATEGORY TESTS
# =============================================================================

class TestRuntimeValidatorErrorCategories:
    """
    Tests for each error category.

    One test per error category to ensure proper categorization.
    """

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_locator_not_found(self, validator, sample_snapshot):
        """
        P0: Verify LOCATOR_NOT_FOUND when element doesn't exist.

        AAA Pattern:
        1. Arrange - Snapshot without target element
        2. Act - Validate non-existent locator
        3. Assert - Returns LOCATOR_NOT_FOUND
        """
        # Arrange
        locator = "NonExistentElement"

        # Act
        result = validator.validate_element_from_snapshot(
            sample_snapshot, locator
        )

        # Assert
        assert result.is_valid is False, \
            "Non-existent element should be invalid"
        assert result.error_category == ErrorCategory.LOCATOR_NOT_FOUND, \
            f"Expected LOCATOR_NOT_FOUND, got {result.error_category}"
        assert "not found" in result.details["message"].lower()

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_not_visible_hidden_element(self, validator, sample_snapshot):
        """
        P0: Verify NOT_VISIBLE when element is hidden.

        AAA Pattern:
        1. Arrange - Snapshot with hidden element
        2. Act - Validate hidden element
        3. Assert - Returns NOT_VISIBLE
        """
        # Arrange
        locator = "Hidden Link"

        # Act
        result = validator.validate_element_from_snapshot(
            sample_snapshot, locator
        )

        # Assert
        assert result.is_valid is False, \
            "Hidden element should be invalid"
        assert result.error_category == ErrorCategory.NOT_VISIBLE, \
            f"Expected NOT_VISIBLE, got {result.error_category}"

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_not_interactable_disabled_element(self, validator, sample_snapshot):
        """
        P0: Verify NOT_INTERACTABLE when element is disabled.

        AAA Pattern:
        1. Arrange - Snapshot with disabled button
        2. Act - Validate disabled element
        3. Assert - Returns NOT_INTERACTABLE
        """
        # Arrange
        locator = "Disabled Button"

        # Act
        result = validator.validate_element_from_snapshot(
            sample_snapshot, locator
        )

        # Assert
        assert result.is_valid is False, \
            "Disabled element should be invalid"
        assert result.error_category == ErrorCategory.NOT_INTERACTABLE, \
            f"Expected NOT_INTERACTABLE, got {result.error_category}"

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_method_not_found(self, validator):
        """
        P0: Verify METHOD_NOT_FOUND for method existence check.

        AAA Pattern:
        1. Arrange - Validator instance
        2. Act - Check method existence
        3. Assert - Returns METHOD_NOT_FOUND (placeholder)
        """
        # Arrange
        method_name = "click_js"

        # Act
        result = validator.validate_method_exists(method_name)

        # Assert
        assert result.is_valid is False
        assert result.error_category == ErrorCategory.METHOD_NOT_FOUND

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_validation_result_invalid_factory(self):
        """
        P0: Verify ValidationResult.invalid() creates correct result.

        AAA Pattern:
        1. Arrange - Error details
        2. Act - Create invalid result
        3. Assert - Result has correct structure and category
        """
        # Arrange
        category = ErrorCategory.LOCATOR_NOT_FOUND
        locator = "missing-element"
        message = "Element not found"

        # Act
        result = ValidationResult.invalid(
            category, locator, message, extra="info"
        )

        # Assert
        assert result.is_valid is False
        assert result.error_category == category
        assert result.details["locator"] == locator
        assert result.details["message"] == message
        assert result.details["extra"] == "info"


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestRuntimeValidatorEdgeCases:
    """
    Edge case tests for RuntimeValidator.

    Verifies handling of:
    - Empty locator
    - Empty snapshot
    - Nested elements
    - Skip visibility/interactability checks
    """

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_empty_locator_returns_not_found(self, validator, sample_snapshot):
        """
        P1: Verify empty locator returns LOCATOR_NOT_FOUND.

        AAA Pattern:
        1. Arrange - Empty locator string
        2. Act - Validate empty locator
        3. Assert - Returns LOCATOR_NOT_FOUND with appropriate message
        """
        # Arrange
        locator = ""

        # Act
        result = validator.validate_element_from_snapshot(
            sample_snapshot, locator
        )

        # Assert
        assert result.is_valid is False
        assert result.error_category == ErrorCategory.LOCATOR_NOT_FOUND
        assert "empty" in result.details["message"].lower()

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_empty_snapshot_returns_not_found(self, validator, empty_snapshot):
        """
        P1: Verify empty snapshot returns LOCATOR_NOT_FOUND.

        AAA Pattern:
        1. Arrange - Snapshot with no child elements
        2. Act - Validate any locator
        3. Assert - Returns LOCATOR_NOT_FOUND
        """
        # Arrange
        locator = "AnyElement"

        # Act
        result = validator.validate_element_from_snapshot(
            empty_snapshot, locator
        )

        # Assert
        assert result.is_valid is False
        assert result.error_category == ErrorCategory.LOCATOR_NOT_FOUND

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_nested_elements_found(self, validator, nested_snapshot):
        """
        P1: Verify nested elements are found correctly.

        AAA Pattern:
        1. Arrange - Snapshot with deeply nested elements
        2. Act - Validate nested element
        3. Assert - Returns valid
        """
        # Arrange
        locator = "S1.N1.L1"  # Nested link

        # Act
        result = validator.validate_element_from_snapshot(
            nested_snapshot, locator
        )

        # Assert
        assert result.is_valid is True, \
            "Nested element should be found"

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_skip_visibility_check(self, validator, sample_snapshot):
        """
        P1: Verify hidden element passes when visibility check skipped.

        AAA Pattern:
        1. Arrange - Snapshot with hidden element
        2. Act - Validate with check_visibility=False
        3. Assert - Returns valid (existence + interactability only)
        """
        # Arrange
        locator = "Hidden Link"

        # Act
        result = validator.validate_element_from_snapshot(
            sample_snapshot,
            locator,
            check_visibility=False
        )

        # Assert
        assert result.is_valid is True, \
            "Hidden element should pass when visibility check skipped"

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_skip_interactability_check(self, validator, sample_snapshot):
        """
        P1: Verify disabled element passes when interactability check skipped.

        AAA Pattern:
        1. Arrange - Snapshot with disabled element
        2. Act - Validate with check_interactable=False
        3. Assert - Returns valid (existence + visibility only)
        """
        # Arrange
        locator = "Disabled Button"

        # Act
        result = validator.validate_element_from_snapshot(
            sample_snapshot,
            locator,
            check_interactable=False
        )

        # Assert
        assert result.is_valid is True, \
            "Disabled element should pass when interactability check skipped"


# =============================================================================
# SNAPSHOT FUNCTION TESTS
# =============================================================================

class TestRuntimeValidatorWithSnapshotFunction:
    """
    Tests for RuntimeValidator with snapshot function injection.

    Verifies:
    - Snapshot function is called
    - Results are stored
    - Error handling for snapshot failures
    """

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_snapshot_function_called(self, sample_snapshot):
        """
        P1: Verify injected snapshot function is called.

        AAA Pattern:
        1. Arrange - Validator with snapshot function
        2. Act - Validate element
        3. Assert - Snapshot function was called
        """
        # Arrange
        call_count = [0]

        def mock_snapshot():
            call_count[0] += 1
            return sample_snapshot

        validator = RuntimeValidator(snapshot_fn=mock_snapshot)

        # Act
        validator.validate_element("S1.B1")

        # Assert
        assert call_count[0] == 1, "Snapshot function should be called once"

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_last_snapshot_stored(self, validator_with_snapshot_fn, sample_snapshot):
        """
        P1: Verify last snapshot is stored after validation.

        AAA Pattern:
        1. Arrange - Validator with snapshot function
        2. Act - Validate element
        3. Assert - get_last_snapshot() returns snapshot
        """
        # Arrange
        validator = validator_with_snapshot_fn

        # Act
        validator.validate_element("S1.B1")

        # Assert
        stored = validator.get_last_snapshot()
        assert stored is not None, "Last snapshot should be stored"
        assert stored == sample_snapshot

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_snapshot_function_failure_returns_not_found(self):
        """
        P1: Verify snapshot function failure returns LOCATOR_NOT_FOUND.

        AAA Pattern:
        1. Arrange - Validator with failing snapshot function
        2. Act - Validate element
        3. Assert - Returns LOCATOR_NOT_FOUND
        """
        # Arrange
        def failing_snapshot():
            raise Exception("Snapshot failed")

        validator = RuntimeValidator(snapshot_fn=failing_snapshot)

        # Act
        result = validator.validate_element("AnyLocator")

        # Assert
        assert result.is_valid is False
        assert result.error_category == ErrorCategory.LOCATOR_NOT_FOUND
        assert "snapshot" in result.details["message"].lower()


# =============================================================================
# ELEMENT INFO TESTS
# =============================================================================

class TestElementInfo:
    """
    Tests for ElementInfo dataclass.

    Verifies:
    - Basic instantiation
    - Factory method from snapshot node
    """

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_element_info_creation(self):
        """
        P1: Verify ElementInfo creation.

        AAA Pattern:
        1. Arrange - Element properties
        2. Act - Create ElementInfo
        3. Assert - All properties set correctly
        """
        # Arrange/Act
        info = ElementInfo(
            ref="S1.B1",
            role="button",
            name="Submit",
            visible=True,
            disabled=False,
            focused=True
        )

        # Assert
        assert info.ref == "S1.B1"
        assert info.role == "button"
        assert info.name == "Submit"
        assert info.visible is True
        assert info.disabled is False
        assert info.focused is True

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_element_info_from_snapshot_node(self):
        """
        P1: Verify ElementInfo.from_snapshot_node() factory.

        AAA Pattern:
        1. Arrange - Snapshot node dict
        2. Act - Create ElementInfo from node
        3. Assert - Properties extracted correctly
        """
        # Arrange
        node = {
            "ref": "S2.L1",
            "role": "link",
            "name": "Click Here",
            "hidden": False,
            "disabled": True,
            "focused": False
        }

        # Act
        info = ElementInfo.from_snapshot_node(node)

        # Assert
        assert info.ref == "S2.L1"
        assert info.role == "link"
        assert info.name == "Click Here"
        assert info.visible is True  # hidden=False means visible
        assert info.disabled is True
        assert info.focused is False


# =============================================================================
# CONVENIENCE FUNCTION TESTS
# =============================================================================

class TestConvenienceFunctions:
    """
    Tests for convenience functions.

    Verifies:
    - validate_element() works
    - validate_elements() works with multiple locators
    """

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_validate_element_function(self, sample_snapshot):
        """
        P1: Verify validate_element convenience function.

        AAA Pattern:
        1. Arrange - Sample snapshot and locator
        2. Act - Call validate_element function
        3. Assert - Returns valid result
        """
        # Arrange
        locator = "S1.B1"

        # Act
        result = validate_element(locator, snapshot=sample_snapshot)

        # Assert
        assert result.is_valid is True

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_validate_elements_function(self, sample_snapshot):
        """
        P1: Verify validate_elements convenience function.

        AAA Pattern:
        1. Arrange - Sample snapshot and multiple locators
        2. Act - Call validate_elements function
        3. Assert - Returns dict with results for each locator
        """
        # Arrange
        locators = ["S1.B1", "NonExistent", "Hidden Link"]

        # Act
        results = validate_elements(locators, snapshot=sample_snapshot)

        # Assert
        assert len(results) == 3, "Should return result for each locator"
        assert results["S1.B1"].is_valid is True
        assert results["NonExistent"].is_valid is False
        assert results["NonExistent"].error_category == ErrorCategory.LOCATOR_NOT_FOUND
        assert results["Hidden Link"].is_valid is False
        assert results["Hidden Link"].error_category == ErrorCategory.NOT_VISIBLE


# =============================================================================
# ERROR CATEGORY ENUM TESTS
# =============================================================================

class TestErrorCategoryEnum:
    """
    Tests for ErrorCategory enum.

    Verifies all expected categories exist.
    """

    @pytest.mark.unit
    @pytest.mark.runtime_validator
    def test_all_error_categories_exist(self):
        """
        P0: Verify all documented error categories exist.

        AAA Pattern:
        1. Arrange - Expected category names
        2. Act - Check enum values
        3. Assert - All categories present
        """
        # Arrange
        expected = [
            "LOCATOR_NOT_FOUND",
            "NOT_VISIBLE",
            "NOT_INTERACTABLE",
            "STALE_REFERENCE",
            "METHOD_NOT_FOUND"
        ]

        # Act
        actual = [cat.value for cat in ErrorCategory]

        # Assert
        for category in expected:
            assert category in actual, \
                f"Missing error category: {category}"

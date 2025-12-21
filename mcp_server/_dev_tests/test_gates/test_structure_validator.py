"""
Unit tests for TestStructureValidator - Task 3.0

Test Matrix:
- AAA validation: 2 tests (P0)
- Marker validation: 2 tests (P0)
- Assertion message validation: 1 test (P0)
- Docstring priority validation: 1 test (P0)

Testing Skill Reference: .claude/skills/testing/
"""

import pytest

from tools.gates.test_structure_validator import TestStructureValidator


class TestAAAPatternValidation:
    """
    Test suite for AAA pattern validation.

    Tests organized by: validation outcome (pass/fail)
    """

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_validates_aaa_pattern(self):
        """
        P0: Verify validator accepts tests with AAA comments.

        AAA Pattern:
        1. Arrange - Create test source with AAA comments
        2. Act - Call validate_aaa_pattern()
        3. Assert - Returns True (valid pattern)
        """
        # Arrange
        test_source = '''
def test_something():
    # Arrange
    data = {"key": "value"}

    # Act
    result = process(data)

    # Assert
    assert result == expected, "Should match expected"
'''

        # Act
        result = TestStructureValidator.validate_aaa_pattern(test_source)

        # Assert
        assert result is True, "Test with AAA comments should pass validation"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_rejects_missing_aaa_comments(self):
        """
        P0: Verify validator rejects tests without AAA comments.

        AAA Pattern:
        1. Arrange - Create test source without AAA comments
        2. Act - Call validate_aaa_pattern()
        3. Assert - Returns False (missing pattern)
        """
        # Arrange
        test_source = '''
def test_something():
    data = {"key": "value"}
    result = process(data)
    assert result == expected
'''

        # Act
        result = TestStructureValidator.validate_aaa_pattern(test_source)

        # Assert
        assert result is False, "Test without AAA comments should fail validation"


class TestMarkerValidation:
    """
    Test suite for pytest marker validation.

    Tests organized by: validation outcome (pass/fail)
    """

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_validates_pytest_markers(self):
        """
        P0: Verify validator accepts tests with type markers.

        AAA Pattern:
        1. Arrange - Create marker list with type marker
        2. Act - Call validate_markers()
        3. Assert - Returns True (valid markers)
        """
        # Arrange
        markers = ["unit", "state_manager"]

        # Act
        result = TestStructureValidator.validate_markers(markers)

        # Assert
        assert result is True, "Test with type marker should pass validation"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_rejects_missing_markers(self):
        """
        P0: Verify validator rejects tests without type markers.

        AAA Pattern:
        1. Arrange - Create marker list without type markers
        2. Act - Call validate_markers()
        3. Assert - Returns False (missing type marker)
        """
        # Arrange
        markers = ["custom_marker", "another_marker"]

        # Act
        result = TestStructureValidator.validate_markers(markers)

        # Assert
        assert result is False, "Test without type marker should fail validation"


class TestAssertionMessageValidation:
    """
    Test suite for assertion message validation.

    Tests organized by: validation outcome
    """

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_validates_assertion_messages(self):
        """
        P0: Verify validator checks for assertion messages.

        AAA Pattern:
        1. Arrange - Create test source with/without assertion messages
        2. Act - Call validate_assertion_messages()
        3. Assert - Detects missing messages correctly
        """
        # Arrange
        valid_source = '''
def test_with_messages():
    assert result == expected, "Should match expected value"
    assert page.is_loaded(), "Page should be loaded"
'''
        invalid_source = '''
def test_without_messages():
    assert result == expected
    assert page.is_loaded()
'''

        # Act
        valid_result = TestStructureValidator.validate_assertion_messages(valid_source)
        invalid_result = TestStructureValidator.validate_assertion_messages(invalid_source)

        # Assert
        assert valid_result is True, "Assertions with messages should pass"
        assert invalid_result is False, "Assertions without messages should fail"


class TestDocstringPriorityValidation:
    """
    Test suite for docstring priority validation.

    Tests organized by: validation outcome
    """

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_validates_docstring_priority(self):
        """
        P0: Verify validator checks for P0/P1/P2 priority in docstring.

        AAA Pattern:
        1. Arrange - Create docstrings with/without priority
        2. Act - Call validate_docstring_priority()
        3. Assert - Detects missing priority correctly
        """
        # Arrange
        valid_docstring = """
        P0: Verify something important.

        AAA Pattern:
        1. Arrange - Setup
        2. Act - Do something
        3. Assert - Check result
        """
        invalid_docstring = """
        Verify something important.

        This test does stuff.
        """

        # Act
        valid_result = TestStructureValidator.validate_docstring_priority(valid_docstring)
        invalid_result = TestStructureValidator.validate_docstring_priority(invalid_docstring)

        # Assert
        assert valid_result is True, "Docstring with P0 priority should pass"
        assert invalid_result is False, "Docstring without priority should fail"

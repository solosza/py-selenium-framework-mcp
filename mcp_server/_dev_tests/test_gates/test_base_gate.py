"""
Unit tests for BaseGate - Task 3.0

Test Matrix:
- Happy path: 5 tests (P0)
- Negative: 2 tests (P0)
- Edge cases: 3 tests (P1)
- DD-25 skeleton detection: 3 tests (P0)
- DD-27 locator detection: 2 tests (P0)
- DD-15 POM assertion: 2 tests (P0)

Testing Skill Reference: .claude/skills/testing/
"""

import pytest

from tools.gates.base_gate import BaseGate


class TestBaseGateResponses:
    """
    Test suite for BaseGate response methods.

    Tests organized by: response type (pass/fail)
    """

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_pass_response_format(self):
        """
        P0: Verify pass_response returns correct format.

        AAA Pattern:
        1. Arrange - No setup needed (static method)
        2. Act - Call pass_response()
        3. Assert - Response has status: pass
        """
        # Arrange
        # No setup needed for static method

        # Act
        result = BaseGate.pass_response()

        # Assert
        assert result == {"status": "pass"}, "pass_response should return {'status': 'pass'}"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_fail_response_format(self):
        """
        P0: Verify fail_response returns correct format with error and fix_hint.

        AAA Pattern:
        1. Arrange - Prepare error and fix_hint values
        2. Act - Call fail_response()
        3. Assert - Response has status, error, and fix_hint
        """
        # Arrange
        error = "Missing required field"
        fix_hint = "Add 'credential_strategy' to input"

        # Act
        result = BaseGate.fail_response(error, fix_hint)

        # Assert
        expected = {
            "status": "fail",
            "error": error,
            "fix_hint": fix_hint
        }
        assert result == expected, f"fail_response should return {expected}"


class TestSkeletonCodeDetection:
    """
    Test suite for DD-25 skeleton code detection.

    Tests organized by: skeleton pattern type
    """

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_detect_skeleton_finds_pass(self):
        """
        P0: Verify detect_skeleton_code finds 'pass' statements.

        AAA Pattern:
        1. Arrange - Create code with pass statement
        2. Act - Call detect_skeleton_code()
        3. Assert - Returns list containing the skeleton indicator
        """
        # Arrange
        code = '''
class AuthTasks:
    def log_in(self, email, password):
        pass
'''

        # Act
        result = BaseGate.detect_skeleton_code(code)

        # Assert
        assert len(result) > 0, "Should detect 'pass' as skeleton code"
        assert any("pass" in r.lower() for r in result), "Result should mention 'pass'"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_detect_skeleton_finds_add_comment(self):
        """
        P0: Verify detect_skeleton_code finds '# Add ... as needed' comments.

        AAA Pattern:
        1. Arrange - Create code with placeholder comment
        2. Act - Call detect_skeleton_code()
        3. Assert - Returns list containing the skeleton indicator
        """
        # Arrange
        code = '''
class AuthTasks:
    def __init__(self, web, base_url):
        self.web = web
        # Add page compositions as needed
'''

        # Act
        result = BaseGate.detect_skeleton_code(code)

        # Assert
        assert len(result) > 0, "Should detect '# Add ... as needed' as skeleton code"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_skeleton_pattern_empty_body(self):
        """
        P0: Verify detect_skeleton_code finds empty method bodies.

        AAA Pattern:
        1. Arrange - Create code with empty method returning self only
        2. Act - Call detect_skeleton_code()
        3. Assert - Returns list containing the skeleton indicator
        """
        # Arrange
        code = '''
class LoginPage:
    def enter_email(self, text: str) -> "LoginPage":
        # TODO: implement
        return self
'''

        # Act
        result = BaseGate.detect_skeleton_code(code)

        # Assert
        assert len(result) > 0, "Should detect TODO comment as skeleton code"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_detect_skeleton_clean_code_returns_empty(self):
        """
        P0: Verify detect_skeleton_code returns empty list for valid code.

        AAA Pattern:
        1. Arrange - Create complete, valid code
        2. Act - Call detect_skeleton_code()
        3. Assert - Returns empty list
        """
        # Arrange
        code = '''
class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def enter_email(self, text: str) -> "LoginPage":
        self.web.type_text(*self.EMAIL, text)
        return self
'''

        # Act
        result = BaseGate.detect_skeleton_code(code)

        # Assert
        assert result == [], f"Clean code should return empty list, got {result}"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_detect_skeleton_empty_string(self):
        """
        P1: Verify detect_skeleton_code handles empty string.

        AAA Pattern:
        1. Arrange - Empty string input
        2. Act - Call detect_skeleton_code()
        3. Assert - Returns empty list (no skeleton to detect)
        """
        # Arrange
        code = ""

        # Act
        result = BaseGate.detect_skeleton_code(code)

        # Assert
        assert result == [], "Empty string should return empty list"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_detect_skeleton_multiline(self):
        """
        P1: Verify detect_skeleton_code handles multiline skeleton patterns.

        AAA Pattern:
        1. Arrange - Code with multiple skeleton indicators
        2. Act - Call detect_skeleton_code()
        3. Assert - Returns all skeleton indicators found
        """
        # Arrange
        code = '''
class AuthTasks:
    def __init__(self):
        # Add dependencies as needed
        pass

    def log_in(self):
        # TODO: implement login
        pass
'''

        # Act
        result = BaseGate.detect_skeleton_code(code)

        # Assert
        assert len(result) >= 2, f"Should find multiple skeleton indicators, found {len(result)}"


class TestRequiredFieldsValidation:
    """
    Test suite for validate_required_fields method.

    Tests organized by: validation outcome (pass/fail)
    """

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_validate_required_fields_all_present(self):
        """
        P0: Verify validation passes when all required fields present.

        AAA Pattern:
        1. Arrange - Create data with all required fields
        2. Act - Call validate_required_fields()
        3. Assert - Returns empty list (no missing fields)
        """
        # Arrange
        data = {
            "credential_strategy": "static",
            "test_data_location": "shared"
        }
        required = ["credential_strategy", "test_data_location"]

        # Act
        result = BaseGate.validate_required_fields(data, required)

        # Assert
        assert result == [], "Should return empty list when all fields present"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_validate_required_fields_missing(self):
        """
        P0: Verify validation returns missing field names.

        AAA Pattern:
        1. Arrange - Create data missing required fields
        2. Act - Call validate_required_fields()
        3. Assert - Returns list of missing field names
        """
        # Arrange
        data = {"credential_strategy": "static"}
        required = ["credential_strategy", "test_data_location", "workflow"]

        # Act
        result = BaseGate.validate_required_fields(data, required)

        # Assert
        assert "test_data_location" in result, "Should report test_data_location as missing"
        assert "workflow" in result, "Should report workflow as missing"
        assert len(result) == 2, f"Should have exactly 2 missing fields, got {len(result)}"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_validate_fields_empty_list(self):
        """
        P1: Verify validation with empty required list returns empty.

        AAA Pattern:
        1. Arrange - Empty required fields list
        2. Act - Call validate_required_fields()
        3. Assert - Returns empty list
        """
        # Arrange
        data = {"some_field": "value"}
        required = []

        # Act
        result = BaseGate.validate_required_fields(data, required)

        # Assert
        assert result == [], "Empty required list should return empty result"


class TestLocatorDetection:
    """
    Test suite for DD-27 locator detection.

    Tests organized by: detection pattern type
    """

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_locator_detection_empty_code(self):
        """
        P1: Verify has_locators handles empty code.

        AAA Pattern:
        1. Arrange - Empty string input
        2. Act - Call has_locators()
        3. Assert - Returns False (no locators in empty code)
        """
        # Arrange
        code = ""

        # Act
        result = BaseGate.has_locators(code)

        # Assert
        assert result is False, "Empty code should return False"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_locator_detection_clean_code(self):
        """
        P1: Verify has_locators returns False for clean code without locators.

        AAA Pattern:
        1. Arrange - Create Task code without any locators
        2. Act - Call has_locators()
        3. Assert - Returns False (no violation)
        """
        # Arrange
        clean_code = '''
class AuthTasks:
    def __init__(self, web, base_url):
        self.login_page = LoginPage(web)

    def log_in(self, email, password):
        self.login_page.enter_email(email).enter_password(password).click_submit()
'''

        # Act
        result = BaseGate.has_locators(clean_code)

        # Assert
        assert result is False, "Clean code without locators should return False"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_locator_detection_by_import(self):
        """
        P0: Verify has_locators detects By import in non-POM code.

        AAA Pattern:
        1. Arrange - Create Task code with By import
        2. Act - Call has_locators()
        3. Assert - Returns True (violation detected)
        """
        # Arrange
        task_code = '''
from selenium.webdriver.common.by import By

class AuthTasks:
    EMAIL = (By.ID, "email")
'''

        # Act
        result = BaseGate.has_locators(task_code)

        # Assert
        assert result is True, "Should detect By import as locator violation"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_locator_detection_by_css_selector(self):
        """
        P0: Verify has_locators detects By.CSS_SELECTOR usage.

        AAA Pattern:
        1. Arrange - Create code with By.CSS_SELECTOR
        2. Act - Call has_locators()
        3. Assert - Returns True (violation detected)
        """
        # Arrange
        code = '''
class SomeTasks:
    def do_something(self):
        self.web.click(By.CSS_SELECTOR, "#submit")
'''

        # Act
        result = BaseGate.has_locators(code)

        # Assert
        assert result is True, "Should detect By.CSS_SELECTOR as locator"


class TestPOMAssertionValidation:
    """
    Test suite for DD-15 POM assertion pattern validation.

    Tests organized by: validation outcome
    """

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_pom_assertion_empty_code(self):
        """
        P1: Verify validate_pom_assertions handles empty code.

        AAA Pattern:
        1. Arrange - Empty string input
        2. Act - Call validate_pom_assertions()
        3. Assert - Returns True (no assertions to validate)
        """
        # Arrange
        code = ""

        # Act
        result = BaseGate.validate_pom_assertions(code)

        # Assert
        assert result is True, "Empty code should return True"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_pom_assertion_no_assertions(self):
        """
        P1: Verify validate_pom_assertions handles code without assertions.

        AAA Pattern:
        1. Arrange - Code without any assert statements
        2. Act - Call validate_pom_assertions()
        3. Assert - Returns True (no assertions to validate)
        """
        # Arrange
        code = '''
def test_something():
    user.login()
    user.browse_products()
'''

        # Act
        result = BaseGate.validate_pom_assertions(code)

        # Assert
        assert result is True, "Code without assertions should return True"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_pom_assertion_pattern_valid(self):
        """
        P0: Verify valid POM assertions are recognized.

        AAA Pattern:
        1. Arrange - Create test code with valid POM assertions
        2. Act - Call validate_pom_assertions()
        3. Assert - Returns True (valid pattern)
        """
        # Arrange
        test_code = '''
def test_login():
    user.login()
    assert login_page.is_logged_in(), "Should be logged in"
    assert profile_page.has_username(), "Should have username"
    assert order_page.get_total() > 0, "Total should be positive"
'''

        # Act
        result = BaseGate.validate_pom_assertions(test_code)

        # Assert
        assert result is True, "Valid POM assertions should pass validation"

    @pytest.mark.unit
    @pytest.mark.base_gate
    def test_pom_assertion_pattern_invalid(self):
        """
        P0: Verify invalid assertions (on return values) are rejected.

        AAA Pattern:
        1. Arrange - Create test code asserting on return values
        2. Act - Call validate_pom_assertions()
        3. Assert - Returns False (invalid pattern)
        """
        # Arrange
        test_code = '''
def test_login():
    result = user.login()
    assert result is True, "Login should return True"
'''

        # Act
        result = BaseGate.validate_pom_assertions(test_code)

        # Assert
        assert result is False, "Assertions on return values should fail validation"

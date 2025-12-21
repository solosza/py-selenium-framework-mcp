"""
Tests for QGDiscoveredElements quality gate (Step 5).

PRE+POST validation gate for Tool 2 (discover_page_elements).

Test Categories:
- PRE validation: Step 4 complete, URL, page_name, credential_strategy (IC-05-01)
- POST validation: elements array, element structure, locators (IC-05-03), page_name PascalCase (IC-05-02)
- Routing: validate() routes to PRE/POST based on mode

Coverage Target: 90%+
"""

import pytest
from unittest.mock import patch, MagicMock

from tools.gates.qg_discovered_elements import QGDiscoveredElements


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def valid_pre_input():
    """Valid PRE validation input."""
    return {
        "mode": "PRE",
        "url": "http://www.automationpractice.pl/index.php",
        "page_name": "LoginPage",
        "credential_strategy": "static"
    }


@pytest.fixture
def valid_post_input():
    """Valid POST validation input with single element."""
    return {
        "mode": "POST",
        "page_name": "LoginPage",
        "elements": [
            {
                "suggested_name": "EMAIL_INPUT",
                "element_type": "textbox",
                "locator_id": "#email",
                "locator_css": "",
                "locator_xpath": ""
            }
        ]
    }


@pytest.fixture
def valid_element():
    """Valid element structure."""
    return {
        "suggested_name": "SUBMIT_BUTTON",
        "element_type": "button",
        "locator_id": "#submit",
        "locator_css": "",
        "locator_xpath": ""
    }


@pytest.fixture
def mock_state_manager_step_4_complete():
    """Mock StateManager with Step 4 complete."""
    with patch.object(QGDiscoveredElements, '_get_state_manager') as mock:
        state_manager = MagicMock()
        state_manager.is_step_complete.return_value = True
        mock.return_value = state_manager
        yield mock


@pytest.fixture
def mock_state_manager_step_4_incomplete():
    """Mock StateManager with Step 4 incomplete."""
    with patch.object(QGDiscoveredElements, '_get_state_manager') as mock:
        state_manager = MagicMock()
        state_manager.is_step_complete.return_value = False
        mock.return_value = state_manager
        yield mock


# =============================================================================
# PRE Validation - Happy Path
# =============================================================================

class TestPreValidationHappy:
    """PRE validation happy path tests."""

    @pytest.mark.unit
    def test_pre_all_valid_passes(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: Valid PRE input passes all checks.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Valid PRE input should pass"

    @pytest.mark.unit
    def test_pre_step_4_complete_checked(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE validation checks Step 4 completion.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass when Step 4 complete"
        mock_state_manager_step_4_complete.return_value.is_step_complete.assert_called_with(4)


# =============================================================================
# PRE Validation - Negative (Step 4)
# =============================================================================

class TestPreValidationStep4:
    """PRE validation Step 4 checks."""

    @pytest.mark.unit
    def test_pre_step_4_incomplete_fails(self, valid_pre_input, mock_state_manager_step_4_incomplete):
        """
        P0: PRE fails when Step 4 is not complete.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when Step 4 incomplete"
        assert "Step 4" in result["error"], "Error should mention Step 4"
        assert "fix_hint" in result, "Should provide fix hint"


# =============================================================================
# PRE Validation - Negative (URL)
# =============================================================================

class TestPreValidationURL:
    """PRE validation URL checks."""

    @pytest.mark.unit
    def test_pre_url_missing_fails(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE fails when URL is missing.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        del input_data["url"]

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when URL missing"
        assert "url" in result["error"].lower(), "Error should mention URL"

    @pytest.mark.unit
    def test_pre_url_empty_fails(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE fails when URL is empty string.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["url"] = ""

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when URL empty"
        assert "url" in result["error"].lower(), "Error should mention URL"

    @pytest.mark.unit
    def test_pre_url_invalid_format_fails(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE fails when URL doesn't start with http/https.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["url"] = "www.example.com"

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when URL invalid format"
        assert "http" in result["error"].lower(), "Error should mention http"


# =============================================================================
# PRE Validation - Negative (page_name)
# =============================================================================

class TestPreValidationPageName:
    """PRE validation page_name checks."""

    @pytest.mark.unit
    def test_pre_page_name_missing_fails(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE fails when page_name is missing.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        del input_data["page_name"]

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when page_name missing"
        assert "page_name" in result["error"].lower(), "Error should mention page_name"

    @pytest.mark.unit
    def test_pre_page_name_empty_fails(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE fails when page_name is empty string.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["page_name"] = ""

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when page_name empty"
        assert "page_name" in result["error"].lower(), "Error should mention page_name"


# =============================================================================
# PRE Validation - Negative (credential_strategy - IC-05-01)
# =============================================================================

class TestPreValidationCredentialStrategy:
    """PRE validation credential_strategy checks (IC-05-01)."""

    @pytest.mark.unit
    def test_pre_credential_strategy_missing_fails(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE fails when credential_strategy is missing (IC-05-01).

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        del input_data["credential_strategy"]

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when credential_strategy missing"
        assert "credential_strategy" in result["error"].lower(), "Error should mention credential_strategy"

    @pytest.mark.unit
    def test_pre_credential_strategy_invalid_fails(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE fails when credential_strategy has invalid value.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["credential_strategy"] = "invalid_strategy"

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when credential_strategy invalid"
        assert "credential_strategy" in result["error"].lower(), "Error should mention credential_strategy"


# =============================================================================
# PRE Validation - Edge Cases
# =============================================================================

class TestPreValidationEdge:
    """PRE validation edge cases."""

    @pytest.mark.unit
    def test_pre_url_localhost_valid(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P1: PRE accepts localhost URLs.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["url"] = "http://localhost:8080/login"

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Should accept localhost URL"

    @pytest.mark.unit
    def test_pre_url_with_port_valid(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P1: PRE accepts URLs with port numbers.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["url"] = "https://example.com:3000/page"

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Should accept URL with port"


# =============================================================================
# POST Validation - Happy Path
# =============================================================================

class TestPostValidationHappy:
    """POST validation happy path tests."""

    @pytest.mark.unit
    def test_post_valid_single_element_passes(self, valid_post_input):
        """
        P0: Valid POST input with single element passes.

        # Arrange
        """
        # Arrange
        input_data = valid_post_input

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Valid single element should pass"

    @pytest.mark.unit
    def test_post_valid_multiple_elements_passes(self, valid_post_input, valid_element):
        """
        P0: Valid POST input with multiple elements passes.

        # Arrange
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["elements"] = [valid_post_input["elements"][0], valid_element]

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Valid multiple elements should pass"

    @pytest.mark.unit
    def test_post_page_name_pascalcase_passes(self, valid_post_input):
        """
        P0: POST accepts PascalCase page names (IC-05-02).

        # Arrange
        """
        # Arrange - test various valid PascalCase names
        valid_names = ["LoginPage", "CartModal", "OAuth2Page", "CheckoutForm"]

        for name in valid_names:
            input_data = valid_post_input.copy()
            input_data["page_name"] = name

            # Act
            result = QGDiscoveredElements.validate_post(input_data)

            # Assert
            assert result["status"] == "pass", f"Should accept PascalCase name: {name}"


# =============================================================================
# POST Validation - Negative (elements array)
# =============================================================================

class TestPostValidationElements:
    """POST validation elements array checks."""

    @pytest.mark.unit
    def test_post_elements_missing_fails(self, valid_post_input):
        """
        P0: POST fails when elements is missing.

        # Arrange
        """
        # Arrange
        input_data = valid_post_input.copy()
        del input_data["elements"]

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when elements missing"
        assert "elements" in result["error"].lower(), "Error should mention elements"

    @pytest.mark.unit
    def test_post_elements_not_list_fails(self, valid_post_input):
        """
        P0: POST fails when elements is not a list.

        # Arrange
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["elements"] = "not a list"

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when elements not list"
        assert "elements" in result["error"].lower(), "Error should mention elements"

    @pytest.mark.unit
    def test_post_elements_empty_fails(self, valid_post_input):
        """
        P0: POST fails when elements is empty array.

        # Arrange
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["elements"] = []

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when elements empty"
        assert "at least" in result["error"].lower() or "empty" in result["error"].lower(), \
            "Error should mention empty/at least"


# =============================================================================
# POST Validation - Negative (element structure)
# =============================================================================

class TestPostValidationElementStructure:
    """POST validation element structure checks."""

    @pytest.mark.unit
    def test_post_element_not_dict_fails(self, valid_post_input):
        """
        P0: POST fails when element is not a dict.

        # Arrange
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["elements"] = ["not a dict"]

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when element not dict"

    @pytest.mark.unit
    def test_post_element_missing_name_fails(self, valid_post_input):
        """
        P0: POST fails when element missing suggested_name.

        # Arrange
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["elements"] = [{
            "element_type": "button",
            "locator_id": "#submit"
        }]

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when suggested_name missing"
        assert "suggested_name" in result["error"].lower() or "name" in result["error"].lower(), \
            "Error should mention name"

    @pytest.mark.unit
    def test_post_element_empty_name_fails(self, valid_post_input):
        """
        P0: POST fails when element has empty suggested_name.

        # Arrange
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["elements"] = [{
            "suggested_name": "",
            "element_type": "button",
            "locator_id": "#submit"
        }]

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when suggested_name empty"

    @pytest.mark.unit
    def test_post_element_missing_type_fails(self, valid_post_input):
        """
        P0: POST fails when element missing element_type.

        # Arrange
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["elements"] = [{
            "suggested_name": "SUBMIT",
            "locator_id": "#submit"
        }]

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when element_type missing"
        assert "element_type" in result["error"].lower() or "type" in result["error"].lower(), \
            "Error should mention type"


# =============================================================================
# POST Validation - Negative (locators - IC-05-03)
# =============================================================================

class TestPostValidationLocators:
    """POST validation locator checks (IC-05-03)."""

    @pytest.mark.unit
    def test_post_element_no_locators_fails(self, valid_post_input):
        """
        P0: POST fails when element has no locator fields (IC-05-03).

        # Arrange
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["elements"] = [{
            "suggested_name": "SUBMIT",
            "element_type": "button"
            # No locator_id, locator_css, or locator_xpath
        }]

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when no locators"
        assert "locator" in result["error"].lower(), "Error should mention locator"

    @pytest.mark.unit
    def test_post_element_all_locators_empty_fails(self, valid_post_input):
        """
        P0: POST fails when all locator fields are empty strings (IC-05-03).

        # Arrange
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["elements"] = [{
            "suggested_name": "SUBMIT",
            "element_type": "button",
            "locator_id": "",
            "locator_css": "",
            "locator_xpath": ""
        }]

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when all locators empty"
        assert "locator" in result["error"].lower(), "Error should mention locator"


# =============================================================================
# POST Validation - Negative (page_name PascalCase - IC-05-02)
# =============================================================================

class TestPostValidationPageNameCase:
    """POST validation page_name PascalCase checks (IC-05-02)."""

    @pytest.mark.unit
    def test_post_page_name_lowercase_fails(self, valid_post_input):
        """
        P0: POST fails when page_name is lowercase (IC-05-02).

        # Arrange
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["page_name"] = "loginpage"

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when page_name lowercase"
        assert "pascalcase" in result["error"].lower() or "page_name" in result["error"].lower(), \
            "Error should mention PascalCase or page_name"

    @pytest.mark.unit
    def test_post_page_name_snake_case_fails(self, valid_post_input):
        """
        P0: POST fails when page_name is snake_case (IC-05-02).

        # Arrange
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["page_name"] = "login_page"

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when page_name snake_case"


# =============================================================================
# validate() Routing Tests
# =============================================================================

class TestValidateRouting:
    """Tests for validate() method routing."""

    @pytest.mark.unit
    def test_validate_routes_to_pre(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: validate() routes to validate_pre when mode=PRE.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input

        # Act
        result = QGDiscoveredElements.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Should route to PRE and pass"

    @pytest.mark.unit
    def test_validate_routes_to_post(self, valid_post_input):
        """
        P0: validate() routes to validate_post when mode=POST.

        # Arrange
        """
        # Arrange
        input_data = valid_post_input

        # Act
        result = QGDiscoveredElements.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Should route to POST and pass"

    @pytest.mark.unit
    def test_validate_invalid_mode_fails(self):
        """
        P0: validate() fails with invalid mode.

        # Arrange
        """
        # Arrange
        input_data = {"mode": "INVALID"}

        # Act
        result = QGDiscoveredElements.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail with invalid mode"
        assert "mode" in result["error"].lower(), "Error should mention mode"

    @pytest.mark.unit
    def test_validate_empty_mode_fails(self):
        """
        P0: validate() fails with empty mode.

        # Arrange
        """
        # Arrange
        input_data = {"mode": ""}

        # Act
        result = QGDiscoveredElements.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail with empty mode"

    @pytest.mark.unit
    def test_validate_missing_mode_fails(self):
        """
        P0: validate() fails when mode is missing.

        # Arrange
        """
        # Arrange
        input_data = {}

        # Act
        result = QGDiscoveredElements.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail with missing mode"

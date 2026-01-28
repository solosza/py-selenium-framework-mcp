"""
Tests for QGDiscoveredElements quality gate (Step 5).

PRE+POST validation gate for Tool 2 (discover_page_elements) or DD-33 (Playwright snapshot).

Test Categories:
- PRE validation: Step 4 complete, URL, page_name, credential_strategy (IC-05-01), discovery_method (DD-33)
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
        "credential_strategy": "static",
        "discovery_method": "tool2"
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
        ],
        "validation_results": {
            "valid_count": 1,
            "error_count": 0,
            "elements": [
                {
                    "name": "EMAIL_INPUT",
                    "is_valid": True,
                    "error_category": None
                }
            ]
        }
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
def mock_transcript_check():
    """Mock pre_check_previous_transcript to pass (return None)."""
    with patch.object(QGDiscoveredElements, 'pre_check_previous_transcript') as mock:
        mock.return_value = None  # None = check passes
        yield mock


@pytest.fixture
def mock_state_manager_step_3_complete(mock_transcript_check):
    """Mock StateManager with Step 3 complete (for Step 4 PRE validation)."""
    with patch.object(QGDiscoveredElements, '_get_state_manager') as mock:
        state_manager = MagicMock()
        state_manager.is_step_complete.return_value = True
        state_manager.get_step.return_value = {}  # Empty state data
        mock.return_value = state_manager
        yield mock


@pytest.fixture
def mock_state_manager_step_3_incomplete(mock_transcript_check):
    """Mock StateManager with Step 3 incomplete (for Step 4 PRE validation)."""
    with patch.object(QGDiscoveredElements, '_get_state_manager') as mock:
        state_manager = MagicMock()
        state_manager.is_step_complete.return_value = False
        mock.return_value = state_manager
        yield mock


# Legacy aliases for backward compatibility
@pytest.fixture
def mock_state_manager_step_4_complete(mock_state_manager_step_3_complete):
    """Alias: Mock for Step 4 PRE validation (checks Step 3)."""
    return mock_state_manager_step_3_complete


@pytest.fixture
def mock_state_manager_step_4_incomplete(mock_state_manager_step_3_incomplete):
    """Alias: Mock for Step 4 PRE validation when Step 3 incomplete."""
    return mock_state_manager_step_3_incomplete


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
    def test_pre_step_3_complete_checked(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE validation checks Step 3 completion (previous step).

        Step 4 (Discovered Elements) PRE validation verifies Step 3 (AI Processing)
        is complete before proceeding.
        """
        # Arrange
        input_data = valid_pre_input

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass when Step 3 complete"
        # Note: Step 4 PRE validates Step 3 (previous step) is complete


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
        assert "teach" in result, "Should provide fix hint"


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
# PRE Validation - Negative (discovery_method - DD-33)
# =============================================================================

class TestPreValidationDiscoveryMethod:
    """PRE validation discovery_method checks (DD-33)."""

    @pytest.mark.unit
    def test_pre_discovery_method_missing_fails(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE fails when discovery_method is missing (DD-33).

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        del input_data["discovery_method"]

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when discovery_method missing"
        assert "discovery_method" in result["error"].lower(), "Error should mention discovery_method"
        assert "DD-33" in result["error"], "Error should reference DD-33"

    @pytest.mark.unit
    def test_pre_discovery_method_invalid_fails(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE fails when discovery_method has invalid value.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["discovery_method"] = "invalid_method"

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when discovery_method invalid"
        assert "discovery_method" in result["error"].lower(), "Error should mention discovery_method"

    @pytest.mark.unit
    def test_pre_discovery_method_tool2_passes_with_deprecation_warning(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE passes when discovery_method is 'tool2' but includes deprecation warning.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["discovery_method"] = "tool2"

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass when discovery_method is tool2"
        assert "warning" in result, "Should include deprecation warning for tool2"
        assert "DEPRECATED" in result["warning"], "Warning should mention DEPRECATED"
        assert "playwright" in result["warning"].lower(), "Warning should recommend playwright"

    @pytest.mark.unit
    def test_pre_discovery_method_playwright_passes_no_warning(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE passes when discovery_method is 'playwright' without deprecation warning.

        # Arrange
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["discovery_method"] = "playwright"

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass when discovery_method is playwright"
        assert "warning" not in result, "Should not include deprecation warning for playwright"


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


# =============================================================================
# DD-44: Multi-Page Scope Discovery Tests
# =============================================================================

@pytest.fixture
def mock_state_manager_multi_page(mock_transcript_check):
    """Mock StateManager with Step 3 complete and multi-page BDD scenarios."""
    with patch.object(QGDiscoveredElements, '_get_state_manager') as mock:
        state_manager = MagicMock()
        state_manager.is_step_complete.return_value = True
        # Multi-page BDD scenario (4 pages)
        state_manager.get_step.return_value = {
            "test_scenarios": [
                {
                    "given": ["user is on search page"],
                    "when": ["user searches for customer", "user clicks new customer"],
                    "then": ["user is on customer page"]
                },
                {
                    "given": ["user is on customer page"],
                    "when": ["user fills customer details"],
                    "then": ["user sees contacts page"]
                },
                {
                    "given": ["user is on contacts page"],
                    "when": ["user fills contact details"],
                    "then": ["user sees address page"]
                },
                {
                    "given": ["user is on address page"],
                    "when": ["user fills address details"],
                    "then": ["customer is created"]
                }
            ]
        }
        mock.return_value = state_manager
        yield mock


@pytest.fixture
def mock_state_manager_single_page(mock_transcript_check):
    """Mock StateManager with Step 3 complete and single-page BDD scenario."""
    with patch.object(QGDiscoveredElements, '_get_state_manager') as mock:
        state_manager = MagicMock()
        state_manager.is_step_complete.return_value = True
        # Single-page BDD scenario
        state_manager.get_step.return_value = {
            "test_scenarios": [
                {
                    "given": ["user is on login page"],
                    "when": ["user enters credentials", "user clicks submit"],
                    "then": ["user is logged in"]
                }
            ]
        }
        mock.return_value = state_manager
        yield mock


class TestDD44MultiPageDetection:
    """DD-44: Multi-page scope discovery enforcement tests."""

    @pytest.mark.unit
    def test_pre_multi_page_without_scope_result_fails(self, valid_pre_input, mock_state_manager_multi_page):
        """
        P0: PRE fails when multi-page BDD detected but scope_result not provided (DD-44).
        """
        # Arrange
        input_data = valid_pre_input.copy()
        # No scope_result provided

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when multi-page without scope_result"
        assert "DD-44" in result["error"], "Error should reference DD-44"
        assert "scope_result" in result["error"].lower(), "Error should mention scope_result"

    @pytest.mark.unit
    def test_pre_multi_page_with_scope_result_passes(self, valid_pre_input, mock_state_manager_multi_page):
        """
        P0: PRE passes when multi-page BDD has scope_result provided (DD-44).
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["scope_result"] = {
            "page_count": 4,
            "pages": [
                {"name": "SearchPage", "order": 1},
                {"name": "CustomerPage", "order": 2},
                {"name": "ContactsPage", "order": 3},
                {"name": "AddressPage", "order": 4}
            ]
        }
        input_data["page_name"] = "SearchPage"  # Must match one in scope

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass when multi-page with scope_result"

    @pytest.mark.unit
    def test_pre_single_page_without_scope_result_passes(self, valid_pre_input, mock_state_manager_single_page):
        """
        P0: PRE passes for single-page BDD without scope_result (DD-44 not triggered).
        """
        # Arrange
        input_data = valid_pre_input.copy()
        # No scope_result needed for single page

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass when single-page without scope_result"

    @pytest.mark.unit
    def test_pre_no_bdd_in_state_passes(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P1: PRE passes when no BDD scenarios in state (defaults to single page).
        """
        # Arrange
        input_data = valid_pre_input.copy()
        # mock_state_manager_step_4_complete doesn't set up get_step, so it returns None

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass when no BDD in state (defaults single page)"

    @pytest.mark.unit
    def test_detect_page_count_from_bdd(self, mock_state_manager_multi_page):
        """
        P0: _detect_page_count_from_bdd correctly counts pages from BDD.
        """
        # Arrange
        state_manager = mock_state_manager_multi_page.return_value

        # Act
        page_count = QGDiscoveredElements._detect_page_count_from_bdd(state_manager)

        # Assert
        assert page_count >= 4, "Should detect at least 4 pages from multi-page BDD"


@pytest.fixture
def mock_state_manager_for_post():
    """Mock StateManager for POST validation with clean state."""
    with patch.object(QGDiscoveredElements, '_get_state_manager') as mock:
        state_manager = MagicMock()
        state_manager.get_step.return_value = {}  # Clean state
        state_manager.save = MagicMock()  # Mock save
        mock.return_value = state_manager
        yield mock


class TestDD44MultiPageProgress:
    """DD-44: Multi-page discovery progress tracking tests."""

    @pytest.mark.unit
    def test_post_multi_page_returns_progress(self, valid_post_input, mock_state_manager_for_post):
        """
        P0: POST returns multi_page_progress for multi-page workflows.

        NOTE: DEF-045 two-pass discovery - page only counts as discovered when it has BOTH types.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["type"] = "input"  # DEF-045: First pass (input only)
        input_data["scope_result"] = {
            "page_count": 4,
            "pages": [
                {"name": "SearchPage", "order": 1},
                {"name": "CustomerPage", "order": 2},
                {"name": "ContactsPage", "order": 3},
                {"name": "AddressPage", "order": 4}
            ]
        }
        input_data["page_name"] = "SearchPage"

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass"
        assert "multi_page_progress" in result, "Should include progress info"
        assert result["multi_page_progress"]["total_pages"] == 4
        # DEF-045: With only input elements, page not yet discovered (needs output too)
        assert result["multi_page_progress"]["pages_discovered"] == 0
        assert result["multi_page_progress"]["discovery_complete"] is False

    @pytest.mark.unit
    def test_post_single_page_no_progress(self, valid_post_input, mock_state_manager_for_post):
        """
        P1: POST does not return multi_page_progress for single-page workflows.
        """
        # Arrange
        input_data = valid_post_input.copy()
        # No scope_result = single page

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass"
        assert "multi_page_progress" not in result, "Should not include progress for single page"

    @pytest.mark.unit
    def test_post_incomplete_discovery_has_hint(self, valid_post_input, mock_state_manager_for_post):
        """
        P0: POST returns hint when discovery incomplete.

        NOTE: DEF-045 two-pass discovery - page only counts as discovered when it has BOTH types.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["type"] = "input"  # DEF-045: First pass (input only)
        input_data["scope_result"] = {
            "page_count": 4,
            "pages": [{"name": "SearchPage", "order": 1}]
        }
        input_data["page_name"] = "SearchPage"

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Should still pass (just one page at a time)"
        assert "hint" in result, "Should include hint about remaining pages"
        # DEF-045: With only input elements, shows 0/4 (needs output too)
        assert "0/4" in result["hint"], "Hint should show progress (0 pages with both types)"


# =============================================================================
# DEF-045: Two-Pass Discovery - Type Parameter Tests
# =============================================================================

class TestDEF045TypeParameter:
    """DEF-045: Type parameter validation tests for two-pass discovery."""

    @pytest.mark.unit
    def test_pre_type_missing_defaults_to_input(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE without type parameter defaults to 'input' (backward compat).
        """
        # Arrange
        input_data = valid_pre_input.copy()
        # No type parameter

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass and default to input"

    @pytest.mark.unit
    def test_pre_type_input_passes(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE passes when type='input'.
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["type"] = "input"

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass with type=input"

    @pytest.mark.unit
    def test_pre_type_output_passes(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE passes when type='output'.
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["type"] = "output"

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass with type=output"

    @pytest.mark.unit
    def test_pre_type_invalid_fails(self, valid_pre_input, mock_state_manager_step_4_complete):
        """
        P0: PRE fails when type has invalid value.
        """
        # Arrange
        input_data = valid_pre_input.copy()
        input_data["type"] = "invalid_type"

        # Act
        result = QGDiscoveredElements.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail with invalid type"
        assert "type" in result["error"].lower(), "Error should mention type"

    @pytest.mark.unit
    def test_post_type_input_saves_to_input_elements(self, valid_post_input, mock_state_manager_for_post):
        """
        P0: POST with type='input' saves to discovered_pages[page]['input_elements'].
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["type"] = "input"
        input_data["validation_results"] = {
            "valid_count": 1,
            "error_count": 0,
            "elements": [{"name": "EMAIL_INPUT", "is_valid": True}]
        }

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass"
        # Verify state saved with nested structure
        state_manager = mock_state_manager_for_post.return_value
        saved_state = state_manager.save.call_args[0][1]
        assert "LoginPage" in saved_state["discovered_pages"], "Page should be in discovered_pages"
        assert "input_elements" in saved_state["discovered_pages"]["LoginPage"], "Should have input_elements key"

    @pytest.mark.unit
    def test_post_type_output_saves_to_output_elements(self, valid_post_input, mock_state_manager_for_post):
        """
        P0: POST with type='output' saves to discovered_pages[page]['output_elements'].
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["type"] = "output"
        input_data["validation_results"] = {
            "valid_count": 1,
            "error_count": 0,
            "elements": [{"name": "SUCCESS_MESSAGE", "is_valid": True}]
        }

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass"
        # Verify state saved with nested structure
        state_manager = mock_state_manager_for_post.return_value
        saved_state = state_manager.save.call_args[0][1]
        assert "LoginPage" in saved_state["discovered_pages"], "Page should be in discovered_pages"
        assert "output_elements" in saved_state["discovered_pages"]["LoginPage"], "Should have output_elements key"

    @pytest.mark.unit
    def test_post_type_missing_defaults_to_input(self, valid_post_input, mock_state_manager_for_post):
        """
        P0: POST without type parameter defaults to 'input' (backward compat).
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["validation_results"] = {
            "valid_count": 1,
            "error_count": 0,
            "elements": [{"name": "EMAIL_INPUT", "is_valid": True}]
        }
        # No type parameter

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass and default to input"
        state_manager = mock_state_manager_for_post.return_value
        saved_state = state_manager.save.call_args[0][1]
        assert "input_elements" in saved_state["discovered_pages"]["LoginPage"], "Should default to input_elements"


# =============================================================================
# DEF-045: Two-Pass Discovery - Nested State Tests
# =============================================================================

class TestDEF045NestedState:
    """DEF-045: Nested state structure tests for two-pass discovery."""

    @pytest.mark.unit
    def test_post_creates_nested_structure_on_first_input(self, valid_post_input, mock_state_manager_for_post):
        """
        P0: POST creates nested structure on first input pass.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["type"] = "input"
        input_data["validation_results"] = {
            "valid_count": 1,
            "error_count": 0,
            "elements": [{"name": "EMAIL_INPUT", "is_valid": True}]
        }

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "pass"
        state_manager = mock_state_manager_for_post.return_value
        saved_state = state_manager.save.call_args[0][1]
        discovered_pages = saved_state["discovered_pages"]
        assert isinstance(discovered_pages["LoginPage"], dict), "Page should be dict"
        assert "input_elements" in discovered_pages["LoginPage"], "Should have input_elements"

    @pytest.mark.unit
    def test_post_adds_output_to_existing_input(self, valid_post_input):
        """
        P0: POST adds output_elements to existing page with input_elements.
        """
        # Arrange - mock state with existing input elements
        with patch.object(QGDiscoveredElements, '_get_state_manager') as mock:
            state_manager = MagicMock()
            state_manager.get_step.return_value = {
                "discovered_pages": {
                    "LoginPage": {
                        "input_elements": [{"suggested_name": "EMAIL", "element_type": "textbox"}]
                    }
                }
            }
            state_manager.save = MagicMock()
            mock.return_value = state_manager

            input_data = valid_post_input.copy()
            input_data["type"] = "output"
            input_data["validation_results"] = {
                "valid_count": 1,
                "error_count": 0,
                "elements": [{"name": "SUCCESS_MSG", "is_valid": True}]
            }

            # Act
            result = QGDiscoveredElements.validate_post(input_data)

            # Assert
            assert result["status"] == "pass"
            saved_state = state_manager.save.call_args[0][1]
            login_page = saved_state["discovered_pages"]["LoginPage"]
            assert "input_elements" in login_page, "Should preserve input_elements"
            assert "output_elements" in login_page, "Should add output_elements"

    @pytest.mark.unit
    def test_post_state_saved_with_correct_nested_structure(self, valid_post_input, mock_state_manager_for_post):
        """
        P0: POST saves state with correct nested structure.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["type"] = "input"
        input_data["validation_results"] = {
            "valid_count": 1,
            "error_count": 0,
            "elements": [{"name": "EMAIL_INPUT", "is_valid": True}]
        }

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "pass"
        state_manager = mock_state_manager_for_post.return_value
        saved_state = state_manager.save.call_args[0][1]

        # Verify backward compat fields
        assert "discovered_elements" in saved_state, "Should have backward compat field"
        assert "page_name" in saved_state, "Should have backward compat field"

        # Verify new nested structure
        assert "discovered_pages" in saved_state, "Should have discovered_pages"
        assert isinstance(saved_state["discovered_pages"]["LoginPage"], dict), "Page should be dict"


# =============================================================================
# DEF-045: Two-Pass Discovery - Discovery Complete Tests
# =============================================================================

class TestDEF045DiscoveryComplete:
    """DEF-045: Discovery complete calculation tests."""

    @pytest.mark.unit
    def test_discovery_complete_false_when_only_input_elements(self, valid_post_input):
        """
        P0: discovery_complete is False when page has only input_elements.
        """
        # Arrange - single page with only input elements
        with patch.object(QGDiscoveredElements, '_get_state_manager') as mock:
            state_manager = MagicMock()
            state_manager.get_step.return_value = {}
            state_manager.save = MagicMock()
            mock.return_value = state_manager

            input_data = valid_post_input.copy()
            input_data["type"] = "input"
            input_data["validation_results"] = {
                "valid_count": 1,
                "error_count": 0,
                "elements": [{"name": "EMAIL", "is_valid": True}]
            }

            # Act
            result = QGDiscoveredElements.validate_post(input_data)

            # Assert
            assert result["status"] == "pass"
            saved_state = state_manager.save.call_args[0][1]
            assert saved_state["discovery_complete"] is False, "Should not be complete with only input"

    @pytest.mark.unit
    def test_discovery_complete_true_when_both_input_and_output(self, valid_post_input):
        """
        P0: discovery_complete is True when page has both input_elements and output_elements.
        """
        # Arrange - state with input, adding output
        with patch.object(QGDiscoveredElements, '_get_state_manager') as mock:
            state_manager = MagicMock()
            state_manager.get_step.return_value = {
                "discovered_pages": {
                    "LoginPage": {
                        "input_elements": [{"suggested_name": "EMAIL"}]
                    }
                }
            }
            state_manager.save = MagicMock()
            mock.return_value = state_manager

            input_data = valid_post_input.copy()
            input_data["type"] = "output"
            input_data["validation_results"] = {
                "valid_count": 1,
                "error_count": 0,
                "elements": [{"name": "SUCCESS", "is_valid": True}]
            }

            # Act
            result = QGDiscoveredElements.validate_post(input_data)

            # Assert
            assert result["status"] == "pass"
            saved_state = state_manager.save.call_args[0][1]
            assert saved_state["discovery_complete"] is True, "Should be complete with both types"

    @pytest.mark.unit
    def test_multi_page_all_pages_need_both_types(self, valid_post_input):
        """
        P0: Multi-page discovery requires ALL pages to have both types.
        """
        # Arrange - 2 pages, only first has both types
        with patch.object(QGDiscoveredElements, '_get_state_manager') as mock:
            state_manager = MagicMock()
            state_manager.get_step.return_value = {
                "discovered_pages": {
                    "Page1": {
                        "input_elements": [{"suggested_name": "INPUT1"}],
                        "output_elements": [{"suggested_name": "OUTPUT1"}]
                    },
                    "Page2": {
                        "input_elements": [{"suggested_name": "INPUT2"}]
                        # Missing output_elements
                    }
                }
            }
            state_manager.save = MagicMock()
            mock.return_value = state_manager

            input_data = valid_post_input.copy()
            input_data["type"] = "output"
            input_data["page_name"] = "Page2"
            input_data["validation_results"] = {
                "valid_count": 1,
                "error_count": 0,
                "elements": [{"name": "OUTPUT2", "is_valid": True}]
            }
            input_data["scope_result"] = {
                "page_count": 2,
                "pages": [{"name": "Page1"}, {"name": "Page2"}]
            }

            # Act
            result = QGDiscoveredElements.validate_post(input_data)

            # Assert
            assert result["status"] == "pass"
            saved_state = state_manager.save.call_args[0][1]
            assert saved_state["pages_discovered"] == 2, "Both pages should have both types"
            assert saved_state["discovery_complete"] is True, "Should be complete when all pages have both"


# =============================================================================
# DD-46: Validation Results Tests (CRITICAL GAP)
# =============================================================================

class TestDD46ValidationResults:
    """DD-46: Validation results enforcement tests (CRITICAL - was missing)."""

    @pytest.mark.unit
    def test_post_validation_results_missing_fails(self, valid_post_input):
        """
        P0: POST fails when validation_results is missing for unknown discovery_method (DD-46).

        DEF-058: After conditional DD-46, this tests the fallback path (unknown discovery_method).
        """
        # Arrange
        input_data = valid_post_input.copy()
        del input_data["validation_results"]  # Remove validation_results to test missing case
        # No discovery_method set - should default to requiring validation_results

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when validation_results missing"
        assert "validation_results" in result["error"].lower(), "Error should mention validation_results"
        assert "DD-46" in result["error"], "Error should reference DD-46"

    @pytest.mark.unit
    def test_post_validation_results_not_dict_fails(self, valid_post_input):
        """
        P0: POST fails when validation_results is not a dict.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["validation_results"] = "not a dict"

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when validation_results not dict"
        assert "validation_results" in result["error"].lower()

    @pytest.mark.unit
    def test_post_validation_results_missing_valid_count_fails(self, valid_post_input):
        """
        P0: POST fails when validation_results missing valid_count.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["validation_results"] = {
            "error_count": 0,
            "elements": []
        }

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when valid_count missing"
        assert "valid_count" in result["error"].lower()

    @pytest.mark.unit
    def test_post_validation_results_missing_error_count_fails(self, valid_post_input):
        """
        P0: POST fails when validation_results missing error_count.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["validation_results"] = {
            "valid_count": 1,
            "elements": []
        }

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when error_count missing"
        assert "error_count" in result["error"].lower()

    @pytest.mark.unit
    def test_post_validation_results_missing_elements_fails(self, valid_post_input):
        """
        P0: POST fails when validation_results missing elements array.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["validation_results"] = {
            "valid_count": 1,
            "error_count": 0
        }

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when elements missing"
        assert "elements" in result["error"].lower()

    @pytest.mark.unit
    def test_post_validation_results_valid_passes(self, valid_post_input, mock_state_manager_for_post):
        """
        P0: POST passes when validation_results has all required fields.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["validation_results"] = {
            "valid_count": 1,
            "error_count": 0,
            "elements": [
                {
                    "name": "EMAIL_INPUT",
                    "is_valid": True,
                    "error_category": None
                }
            ]
        }

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass with valid validation_results"

    @pytest.mark.unit
    def test_post_playwright_auto_validates(self, valid_post_input, mock_state_manager_for_post):
        """
        DEF-058: POST auto-generates validation_results for playwright discovery_method.

        Smart Gate pattern (DD-50): Gate self-heals when using DD-33 (snapshot extraction).
        """
        # Arrange
        input_data = valid_post_input.copy()
        del input_data["validation_results"]  # Remove to trigger auto-generation
        input_data["discovery_method"] = "playwright"  # DD-33 flow

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass with auto-generated validation_results"
        # Playwright auto-validates - no need to check metadata, just verify it didn't fail

    @pytest.mark.unit
    def test_post_tool2_requires_validation(self, valid_post_input):
        """
        DEF-058: POST requires validation_results for tool2 discovery_method.

        Tool 2 (Selenium) MUST have explicit RuntimeValidator validation.
        """
        # Arrange
        input_data = valid_post_input.copy()
        del input_data["validation_results"]  # Remove to trigger failure
        input_data["discovery_method"] = "tool2"  # Tool 2 flow

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail when tool2 missing validation_results"
        assert "validation_results" in result["error"].lower(), "Error should mention validation_results"
        assert "DD-46" in result["error"], "Error should reference DD-46"


# =============================================================================
# HITL (Human-in-the-Loop) Tests
# =============================================================================

class TestHITLTriggerDetection:
    """Tests for HITL trigger detection."""

    @pytest.mark.unit
    def test_should_trigger_hitl_with_validation_errors(self):
        """
        P0: HITL triggers when validation_results.error_count > 0.
        """
        # Arrange
        validation_results = {
            "valid_count": 3,
            "error_count": 2,
            "elements": []
        }

        # Act
        result = QGDiscoveredElements._should_trigger_hitl("some error", validation_results)

        # Assert
        assert result is True, "Should trigger HITL when error_count > 0"

    @pytest.mark.unit
    def test_should_not_trigger_hitl_without_validation_errors(self):
        """
        P0: HITL does not trigger when validation_results.error_count = 0.
        """
        # Arrange
        validation_results = {
            "valid_count": 5,
            "error_count": 0,
            "elements": []
        }

        # Act
        result = QGDiscoveredElements._should_trigger_hitl("some error", validation_results)

        # Assert
        assert result is False, "Should not trigger HITL when error_count = 0"

    @pytest.mark.unit
    def test_should_not_trigger_hitl_without_validation_results(self):
        """
        P0: HITL does not trigger when validation_results is None.
        """
        # Act
        result = QGDiscoveredElements._should_trigger_hitl("elements is empty", None)

        # Assert
        assert result is False, "Should not trigger HITL without validation_results"

    @pytest.mark.unit
    def test_should_not_trigger_hitl_structural_errors(self):
        """
        P0: Structural errors (missing fields) don't trigger HITL.
        """
        # Arrange - test various structural errors without validation results
        structural_errors = [
            "Missing required field: page_name",
            "page_name must be a non-empty string",
            "page_name 'loginpage' is not PascalCase",
            "elements must be a list",
            "Element 0 missing required field: suggested_name",
        ]

        for error in structural_errors:
            result = QGDiscoveredElements._should_trigger_hitl(error, None)
            assert result is False, f"Structural error should NOT trigger HITL: {error}"


class TestHITLTriggering:
    """Tests for HITL triggering in validate_post."""

    @pytest.mark.unit
    def test_post_validation_errors_returns_needs_retry(self, valid_post_input):
        """
        P0: POST returns NEEDS_RETRY when validation_results.error_count > 0.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["validation_results"] = {
            "valid_count": 1,
            "error_count": 2,  # Errors found
            "elements": [
                {"name": "ELEM1", "is_valid": True},
                {"name": "ELEM2", "is_valid": False, "error_category": "not_found"},
                {"name": "ELEM3", "is_valid": False, "error_category": "stale"},
            ]
        }

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "NEEDS_RETRY", "Should return NEEDS_RETRY when validation errors exist"
        assert result["fix_applied"] == "hitl_required", "Should require HITL"
        assert "fix_data" in result, "Should include fix_data"
        assert "diagnostic_data" in result["fix_data"], "Should include diagnostic data"
        assert "ai_analysis" in result["fix_data"], "Should include AI analysis"
        assert "presentation" in result["fix_data"], "Should include triage presentation"

    @pytest.mark.unit
    def test_post_structural_error_returns_fail(self, valid_post_input):
        """
        P0: POST returns fail (not NEEDS_RETRY) for structural errors.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["page_name"] = "lowercase_name"  # PascalCase violation = structural

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should return fail for structural error"
        assert "fix_applied" not in result, "Should not have fix_applied"

    @pytest.mark.unit
    def test_post_empty_elements_returns_fail_not_hitl(self, valid_post_input):
        """
        P0: POST returns fail (not NEEDS_RETRY) for empty elements (structural).

        Empty elements is a structural issue (no elements provided), not a runtime
        validation failure, so it should return fail, not NEEDS_RETRY.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["elements"] = []  # Empty = structural fail

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Should return fail for empty elements"

    @pytest.mark.unit
    def test_hitl_triage_options_included(self, valid_post_input):
        """
        P0: HITL response includes all triage options.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["validation_results"] = {
            "valid_count": 0,
            "error_count": 1,  # Trigger HITL
            "elements": [{"name": "ELEM", "is_valid": False}]
        }

        # Act
        result = QGDiscoveredElements.validate_post(input_data)

        # Assert
        assert result["status"] == "NEEDS_RETRY"
        triage_options = result["fix_data"]["triage_options"]
        assert "ai_investigate" in triage_options
        assert "provide_guidance" in triage_options
        assert "skip_continue" in triage_options
        assert "abort" in triage_options


class TestHITLDiagnosticData:
    """Tests for HITL diagnostic data capture."""

    @pytest.mark.unit
    def test_capture_diagnostic_data_structure(self, valid_post_input):
        """
        P0: Diagnostic data has correct structure.
        """
        # Arrange
        input_data = valid_post_input.copy()
        error = "Test error message"

        # Act
        diagnostic = QGDiscoveredElements._capture_discovery_diagnostic_data(
            input_data, error, None
        )

        # Assert
        assert "version" in diagnostic
        assert diagnostic["version"] == "v1"
        assert "discovery_context" in diagnostic
        assert "error_info" in diagnostic
        assert "elements_attempted" in diagnostic

    @pytest.mark.unit
    def test_capture_diagnostic_data_includes_context(self, valid_post_input):
        """
        P0: Diagnostic data includes discovery context.
        """
        # Arrange
        input_data = valid_post_input.copy()
        input_data["url"] = "http://example.com/page"
        input_data["discovery_method"] = "playwright"
        input_data["credential_strategy"] = "static"
        error = "Test error"

        # Act
        diagnostic = QGDiscoveredElements._capture_discovery_diagnostic_data(
            input_data, error, None
        )

        # Assert
        ctx = diagnostic["discovery_context"]
        assert ctx["page_name"] == "LoginPage"
        assert ctx["url"] == "http://example.com/page"
        assert ctx["discovery_method"] == "playwright"
        assert ctx["credential_strategy"] == "static"


class TestHITLAIAnalysis:
    """Tests for HITL AI analysis generation."""

    @pytest.mark.unit
    def test_ai_analysis_with_validation_errors(self):
        """
        P0: AI analysis for validation errors scenario.
        """
        # Arrange
        diagnostic_data = {
            "error_info": {
                "error_message": "validation failed",
                "validation_results": {
                    "valid_count": 3,
                    "error_count": 2,
                    "elements": []
                }
            },
            "elements_attempted": {"count": 5}
        }

        # Act
        analysis = QGDiscoveredElements._generate_discovery_analysis(diagnostic_data)

        # Assert
        assert "likely_cause" in analysis
        assert "confidence" in analysis
        assert "observation" in analysis
        assert "2" in analysis["likely_cause"], "Should mention error count"
        assert analysis["confidence"] >= 70  # High confidence for validation errors

    @pytest.mark.unit
    def test_ai_analysis_empty_elements(self):
        """
        P0: AI analysis for empty elements scenario.
        """
        # Arrange
        diagnostic_data = {
            "error_info": {"error_message": "elements is empty"},
            "elements_attempted": {"count": 0}
        }

        # Act
        analysis = QGDiscoveredElements._generate_discovery_analysis(diagnostic_data)

        # Assert
        assert "likely_cause" in analysis
        assert "confidence" in analysis
        assert "observation" in analysis
        assert analysis["confidence"] >= 50  # Should have reasonable confidence


class TestHITLTriageDecisionHandler:
    """Tests for HITL triage decision handling."""

    @pytest.mark.unit
    def test_handle_decision_ai_investigate(self):
        """
        P0: Option 1 (AI Investigate) returns correct action.
        """
        # Arrange
        diagnostic_data = {"test": "data"}

        # Act
        result = QGDiscoveredElements.handle_discovery_triage_decision("1", diagnostic_data)

        # Assert
        assert result["action"] == "ai_investigate"
        assert result["blocking"] is False
        assert "diagnostic_data" in result

    @pytest.mark.unit
    def test_handle_decision_provide_guidance(self):
        """
        P0: Option 2 (Provide Guidance) returns correct action.
        """
        # Arrange
        diagnostic_data = {"test": "data"}

        # Act
        result = QGDiscoveredElements.handle_discovery_triage_decision("2", diagnostic_data)

        # Assert
        assert result["action"] == "await_guidance"
        assert result["blocking"] is True

    @pytest.mark.unit
    def test_handle_decision_skip_continue(self):
        """
        P0: Option 3 (Skip + Continue) returns correct action.
        """
        # Arrange
        diagnostic_data = {"test": "data"}

        # Act
        result = QGDiscoveredElements.handle_discovery_triage_decision("3", diagnostic_data)

        # Assert
        assert result["action"] == "skip_continue"
        assert result["blocking"] is False

    @pytest.mark.unit
    def test_handle_decision_abort(self):
        """
        P0: Option 4 (Abort) returns correct action.
        """
        # Arrange
        diagnostic_data = {"test": "data"}

        # Act
        result = QGDiscoveredElements.handle_discovery_triage_decision("4", diagnostic_data)

        # Assert
        assert result["action"] == "abort"
        assert result["blocking"] is True

    @pytest.mark.unit
    def test_handle_decision_custom_guidance(self):
        """
        P0: Custom text input returns custom_guidance action.
        """
        # Arrange
        diagnostic_data = {"test": "data"}
        custom_input = "The page has a CAPTCHA, please solve it"

        # Act
        result = QGDiscoveredElements.handle_discovery_triage_decision(custom_input, diagnostic_data)

        # Assert
        assert result["action"] == "custom_guidance"
        assert result["user_input"] == custom_input
        assert result["blocking"] is False

    @pytest.mark.unit
    def test_handle_decision_text_aliases(self):
        """
        P1: Text aliases work (e.g., 'skip', 'fix', 'abort').
        """
        # Arrange
        diagnostic_data = {"test": "data"}

        # Act/Assert - various aliases
        assert QGDiscoveredElements.handle_discovery_triage_decision("fix", diagnostic_data)["action"] == "ai_investigate"
        assert QGDiscoveredElements.handle_discovery_triage_decision("skip", diagnostic_data)["action"] == "skip_continue"
        assert QGDiscoveredElements.handle_discovery_triage_decision("abort", diagnostic_data)["action"] == "abort"
        assert QGDiscoveredElements.handle_discovery_triage_decision("stop", diagnostic_data)["action"] == "abort"

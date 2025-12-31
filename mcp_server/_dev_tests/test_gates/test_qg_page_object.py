"""
Unit tests for QGPageObject quality gate (Step 6).

Tests PRE+POST validation for Tool 3 (generate_page_object).

Enforces: DD-09, DD-25, DD-26, IC-06-01, IC-06-02, IC-06-03
"""

import pytest
from unittest.mock import patch, MagicMock


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_state_complete():
    """Mock StateManager with Step 5 complete."""
    with patch("tools.gates.qg_page_object.QGPageObject._get_state_manager") as mock:
        state_manager = MagicMock()
        state_manager.is_step_complete.return_value = True
        mock.return_value = state_manager
        yield state_manager


@pytest.fixture
def mock_state_incomplete():
    """Mock StateManager with Step 5 incomplete."""
    with patch("tools.gates.qg_page_object.QGPageObject._get_state_manager") as mock:
        state_manager = MagicMock()
        state_manager.is_step_complete.return_value = False
        mock.return_value = state_manager
        yield state_manager


@pytest.fixture
def valid_pre_input():
    """Valid PRE input data."""
    return {
        "mode": "PRE",
        "discovered_elements": [
            {
                "suggested_name": "EMAIL",
                "element_type": "inputs",
                "locator_id": "#email"
            }
        ],
        "page_name": "LoginPage",
        "expected_states": [
            {"name": "is_logged_in", "description": "user is logged in"}
        ]
    }


@pytest.fixture
def valid_post_input():
    """Valid POST input data with complete code and metadata."""
    return {
        "mode": "POST",
        "code": '''class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def enter_email(self, email: str) -> "LoginPage":
        self.web.type_text(*self.EMAIL, text=email)
        return self

    def is_logged_in(self) -> bool:
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)
''',
        "metadata": {
            "class_name": "LoginPage",
            "import_path": "pages.auth.login_page",
            "locators": [
                {"name": "EMAIL", "by": "CSS_SELECTOR", "value": "#email"}
            ],
            "action_methods": [
                {"name": "enter_email", "params": ["email: str"], "returns": "self"}
            ],
            "state_methods": [
                {"name": "is_logged_in", "params": [], "returns": "bool"}
            ]
        },
        "expected_states": [
            {"name": "is_logged_in", "description": "user is logged in"}
        ]
    }


# =============================================================================
# PRE VALIDATION - HAPPY PATH
# =============================================================================

class TestPreValidationHappy:
    """PRE validation happy path tests."""

    def test_pre_all_valid_passes(self, mock_state_complete, valid_pre_input):
        """
        P0: PRE validation passes with all valid inputs.

        Tests that valid discovered_elements, page_name, and expected_states pass.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject

        # Act
        result = QGPageObject.validate_pre(valid_pre_input)

        # Assert
        assert result["status"] == "pass", "Valid PRE input should pass"

    def test_pre_step_5_complete_checked(self, mock_state_complete, valid_pre_input):
        """
        P0: PRE validation checks Step 5 completion.

        Tests that is_step_complete(5) is called.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject

        # Act
        QGPageObject.validate_pre(valid_pre_input)

        # Assert
        mock_state_complete.is_step_complete.assert_called_with(5)

    def test_pre_expected_states_optional(self, mock_state_complete):
        """
        P1: PRE validation passes without expected_states.

        expected_states is optional but recommended.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        input_data = {
            "mode": "PRE",
            "discovered_elements": [
                {"suggested_name": "EMAIL", "element_type": "inputs", "locator_id": "#email"}
            ],
            "page_name": "LoginPage"
            # No expected_states
        }

        # Act
        result = QGPageObject.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "PRE should pass without expected_states"


# =============================================================================
# PRE VALIDATION - NEGATIVE
# =============================================================================

class TestPreValidationNegative:
    """PRE validation negative tests."""

    def test_pre_step_5_incomplete_fails(self, mock_state_incomplete, valid_pre_input):
        """
        P0: PRE validation fails when Step 5 is incomplete.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject

        # Act
        result = QGPageObject.validate_pre(valid_pre_input)

        # Assert
        assert result["status"] == "fail", "Should fail when Step 5 incomplete"
        assert "Step 5" in result["error"]

    def test_pre_discovered_elements_missing_fails(self, mock_state_complete):
        """
        P0: PRE validation fails when discovered_elements is missing.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        input_data = {
            "mode": "PRE",
            "page_name": "LoginPage"
            # No discovered_elements
        }

        # Act
        result = QGPageObject.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "discovered_elements" in result["error"]

    def test_pre_discovered_elements_empty_fails(self, mock_state_complete):
        """
        P0: PRE validation fails when discovered_elements is empty.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        input_data = {
            "mode": "PRE",
            "discovered_elements": [],
            "page_name": "LoginPage"
        }

        # Act
        result = QGPageObject.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "empty" in result["error"].lower()

    def test_pre_discovered_elements_not_list_fails(self, mock_state_complete):
        """
        P0: PRE validation fails when discovered_elements is not a list.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        input_data = {
            "mode": "PRE",
            "discovered_elements": "not a list",
            "page_name": "LoginPage"
        }

        # Act
        result = QGPageObject.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "list" in result["error"].lower()

    def test_pre_page_name_missing_fails(self, mock_state_complete):
        """
        P0: PRE validation fails when page_name is missing.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        input_data = {
            "mode": "PRE",
            "discovered_elements": [{"suggested_name": "EMAIL", "element_type": "inputs", "locator_id": "#email"}]
            # No page_name
        }

        # Act
        result = QGPageObject.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "page_name" in result["error"]

    def test_pre_page_name_empty_fails(self, mock_state_complete):
        """
        P0: PRE validation fails when page_name is empty.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        input_data = {
            "mode": "PRE",
            "discovered_elements": [{"suggested_name": "EMAIL", "element_type": "inputs", "locator_id": "#email"}],
            "page_name": ""
        }

        # Act
        result = QGPageObject.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "page_name" in result["error"]

    def test_pre_page_name_not_pascalcase_fails(self, mock_state_complete):
        """
        P0: PRE validation fails when page_name is not PascalCase.

        Uses same pattern as IC-05-02.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        input_data = {
            "mode": "PRE",
            "discovered_elements": [{"suggested_name": "EMAIL", "element_type": "inputs", "locator_id": "#email"}],
            "page_name": "login_page"  # snake_case, not PascalCase
        }

        # Act
        result = QGPageObject.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "PascalCase" in result["error"]


# =============================================================================
# POST VALIDATION - HAPPY PATH
# =============================================================================

class TestPostValidationHappy:
    """POST validation happy path tests."""

    def test_post_valid_code_and_metadata_passes(self, valid_post_input):
        """
        P0: POST validation passes with complete code and metadata.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "pass", f"Should pass: {result.get('error', '')}"

    def test_post_state_methods_match_expected_states(self, valid_post_input):
        """
        P0: POST validation passes when state_methods match expected_states (IC-06-01).
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        # valid_post_input already has matching state_methods and expected_states

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "pass", "Should pass when state_methods match expected_states"


# =============================================================================
# POST VALIDATION - SKELETON CODE (DD-25, IC-06-02)
# =============================================================================

class TestPostValidationSkeleton:
    """POST validation skeleton code detection tests (DD-25)."""

    def test_post_skeleton_pass_statement_fails(self, valid_post_input):
        """
        P0: POST validation fails when code contains 'pass' statement (DD-25).
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["code"] = '''class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def enter_email(self, email: str) -> "LoginPage":
        pass
'''

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower() or "pass" in result["error"].lower()

    def test_post_skeleton_add_comment_fails(self, valid_post_input):
        """
        P0: POST validation fails when code contains '# Add...' placeholder (DD-25).
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["code"] = '''class LoginPage:
    # Add locators as needed
    pass
'''

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower()

    def test_post_skeleton_notimplementederror_fails(self, valid_post_input):
        """
        P0: POST validation fails when code contains NotImplementedError (IC-06-02).
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["code"] = '''class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def is_logged_in(self) -> bool:
        raise NotImplementedError("Implement is_logged_in")
'''

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower() or "NotImplementedError" in result["error"]

    def test_post_skeleton_todo_comment_fails(self, valid_post_input):
        """
        P0: POST validation fails when code contains '# TODO:' comment (DD-25).
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["code"] = '''class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def enter_email(self, email: str) -> "LoginPage":
        # TODO: Implement this method
        self.web.type_text(*self.EMAIL, text=email)
        return self
'''

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower() or "TODO" in result["error"]


# =============================================================================
# POST VALIDATION - METADATA STRUCTURE (DD-26)
# =============================================================================

class TestPostValidationMetadata:
    """POST validation metadata structure tests (DD-26)."""

    def test_post_code_missing_fails(self, valid_post_input):
        """
        P0: POST validation fails when code field is missing.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        del valid_post_input["code"]

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "code" in result["error"].lower()

    def test_post_code_empty_fails(self, valid_post_input):
        """
        P0: POST validation fails when code is empty.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["code"] = ""

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "code" in result["error"].lower()

    def test_post_metadata_missing_fails(self, valid_post_input):
        """
        P0: POST validation fails when metadata field is missing.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        del valid_post_input["metadata"]

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "metadata" in result["error"].lower()

    def test_post_class_name_missing_fails(self, valid_post_input):
        """
        P0: POST validation fails when class_name is missing from metadata.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        del valid_post_input["metadata"]["class_name"]

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "class_name" in result["error"]

    def test_post_import_path_missing_fails(self, valid_post_input):
        """
        P0: POST validation fails when import_path is missing from metadata.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        del valid_post_input["metadata"]["import_path"]

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "import_path" in result["error"]


# =============================================================================
# POST VALIDATION - LOCATORS
# =============================================================================

class TestPostValidationLocators:
    """POST validation locators tests."""

    def test_post_locators_missing_fails(self, valid_post_input):
        """
        P0: POST validation fails when locators is missing from metadata.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        del valid_post_input["metadata"]["locators"]

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "locators" in result["error"]

    def test_post_locators_empty_fails(self, valid_post_input):
        """
        P0: POST validation fails when locators is empty.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["metadata"]["locators"] = []

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "locators" in result["error"].lower()


# =============================================================================
# POST VALIDATION - ACTION METHODS (IC-06-03)
# =============================================================================

class TestPostValidationActionMethods:
    """POST validation action_methods tests (IC-06-03)."""

    def test_post_action_methods_missing_fails(self, valid_post_input):
        """
        P0: POST validation fails when action_methods is missing from metadata.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        del valid_post_input["metadata"]["action_methods"]

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "action_methods" in result["error"]

    def test_post_action_methods_empty_when_locators_exist_fails(self, valid_post_input):
        """
        P0: POST validation fails when action_methods is empty but locators exist (IC-06-03).
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["metadata"]["action_methods"] = []
        # locators still exist

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "action_methods" in result["error"].lower()


# =============================================================================
# POST VALIDATION - STATE METHODS (DD-09, IC-06-01)
# =============================================================================

class TestPostValidationStateMethods:
    """POST validation state_methods tests (DD-09, IC-06-01)."""

    def test_post_state_methods_missing_fails(self, valid_post_input):
        """
        P0: POST validation fails when state_methods is missing from metadata.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        del valid_post_input["metadata"]["state_methods"]

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "state_methods" in result["error"]

    def test_post_state_methods_empty_fails(self, valid_post_input):
        """
        P0: POST validation fails when state_methods is empty.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["metadata"]["state_methods"] = []

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "state_methods" in result["error"].lower()

    def test_post_state_methods_not_matching_expected_states_fails(self, valid_post_input):
        """
        P0: POST validation fails when state_methods don't match expected_states (IC-06-01).
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        # expected_states has is_logged_in, but state_methods has different method
        valid_post_input["expected_states"] = [
            {"name": "is_logged_in", "description": "user is logged in"}
        ]
        valid_post_input["metadata"]["state_methods"] = [
            {"name": "is_page_loaded", "params": [], "returns": "bool"}  # Wrong method
        ]

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "is_logged_in" in result["error"] or "expected_states" in result["error"].lower()

    def test_post_state_methods_without_expected_states_passes(self, valid_post_input):
        """
        P1: POST validation passes when no expected_states provided.

        If expected_states wasn't provided in PRE, we don't enforce IC-06-01 matching.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        del valid_post_input["expected_states"]
        # state_methods still has methods, just no expected_states to match against

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "pass", "Should pass without expected_states"


# =============================================================================
# MODE ROUTING
# =============================================================================

class TestModeRouting:
    """Mode routing tests."""

    def test_validate_routes_to_pre(self, mock_state_complete, valid_pre_input):
        """
        P0: validate() routes to validate_pre() when mode is PRE.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject

        # Act
        result = QGPageObject.validate(valid_pre_input)

        # Assert
        assert result["status"] == "pass"
        mock_state_complete.is_step_complete.assert_called()

    def test_validate_routes_to_post(self, valid_post_input):
        """
        P0: validate() routes to validate_post() when mode is POST.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject

        # Act
        result = QGPageObject.validate(valid_post_input)

        # Assert
        assert result["status"] == "pass"

    def test_validate_invalid_mode_fails(self):
        """
        P0: validate() fails when mode is invalid.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        input_data = {"mode": "INVALID"}

        # Act
        result = QGPageObject.validate(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "mode" in result["error"].lower()

    def test_validate_empty_mode_fails(self):
        """
        P0: validate() fails when mode is empty.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        input_data = {"mode": ""}

        # Act
        result = QGPageObject.validate(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "mode" in result["error"].lower()

    def test_validate_missing_mode_fails(self):
        """
        P0: validate() fails when mode is missing.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        input_data = {}

        # Act
        result = QGPageObject.validate(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "mode" in result["error"].lower()


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Edge case tests."""

    def test_pre_multiple_elements_passes(self, mock_state_complete):
        """
        P1: PRE validation passes with multiple elements.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        input_data = {
            "mode": "PRE",
            "discovered_elements": [
                {"suggested_name": "EMAIL", "element_type": "inputs", "locator_id": "#email"},
                {"suggested_name": "PASSWORD", "element_type": "inputs", "locator_id": "#passwd"},
                {"suggested_name": "SUBMIT", "element_type": "buttons", "locator_id": "#SubmitLogin"}
            ],
            "page_name": "LoginPage"
        }

        # Act
        result = QGPageObject.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass"

    def test_post_multiple_state_methods_match_expected_states(self, valid_post_input):
        """
        P1: POST validation passes when all expected_states have matching state_methods.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["expected_states"] = [
            {"name": "is_logged_in", "description": "user is logged in"},
            {"name": "has_error", "description": "error is displayed"}
        ]
        valid_post_input["metadata"]["state_methods"] = [
            {"name": "is_logged_in", "params": [], "returns": "bool"},
            {"name": "has_error", "params": [], "returns": "bool"},
            {"name": "is_page_loaded", "params": [], "returns": "bool"}  # Extra method is OK
        ]

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "pass", "Extra state_methods beyond expected_states should be OK"

    def test_pre_page_name_with_numbers_passes(self, mock_state_complete):
        """
        P1: PRE validation passes with page_name containing numbers (OAuth2Page).
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        input_data = {
            "mode": "PRE",
            "discovered_elements": [
                {"suggested_name": "TOKEN", "element_type": "inputs", "locator_id": "#token"}
            ],
            "page_name": "OAuth2Page"
        }

        # Act
        result = QGPageObject.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "PascalCase with numbers should be valid"


# =============================================================================
# ERROR HINTS
# =============================================================================

class TestErrorHints:
    """Error hint tests."""

    def test_fix_hint_for_skeleton_code(self, valid_post_input):
        """
        P1: fix_hint is provided when skeleton code is detected.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["code"] = "class LoginPage:\n    pass"

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "fix_hint" in result
        assert len(result["fix_hint"]) > 0

    def test_fix_hint_for_missing_state_method(self, valid_post_input):
        """
        P1: fix_hint is provided when state_method doesn't match expected_states.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["expected_states"] = [
            {"name": "is_logged_in", "description": "user is logged in"}
        ]
        valid_post_input["metadata"]["state_methods"] = []

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "fix_hint" in result


# =============================================================================
# WEBINTERFACE METHOD VALIDATION (Task 8.0)
# =============================================================================

class TestWebInterfaceMethodValidation:
    """Task 8.0: WebInterface method validation tests."""

    def test_post_valid_webinterface_methods_passes(self, valid_post_input):
        """
        P0: POST validation passes when code uses valid WebInterface methods.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        # valid_post_input already uses self.web.type_text and self.web.is_element_displayed

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "pass", f"Valid WebInterface methods should pass: {result.get('error', '')}"

    def test_post_invalid_webinterface_method_fails(self, valid_post_input):
        """
        P0: POST validation fails when code uses invalid WebInterface method.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["code"] = '''class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def enter_email(self, email: str) -> "LoginPage":
        self.web.invalid_method_name(*self.EMAIL, text=email)
        return self

    def is_logged_in(self) -> bool:
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)
'''

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "invalid_method_name" in result["error"].lower()

    def test_post_typo_suggests_similar_method(self, valid_post_input):
        """
        P0: POST validation suggests similar method for typos.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["code"] = '''class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def enter_email(self, email: str) -> "LoginPage":
        self.web.clik(*self.EMAIL)
        return self

    def is_logged_in(self) -> bool:
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)
'''

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        # Should suggest "click" for typo "clik"
        assert "clik" in result["error"].lower()
        assert "click" in result["error"].lower() or "Did you mean" in result["error"]

    def test_post_multiple_invalid_methods_all_reported(self, valid_post_input):
        """
        P0: POST validation reports all invalid methods.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["code"] = '''class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def enter_email(self, email: str) -> "LoginPage":
        self.web.fake_method_one(*self.EMAIL)
        self.web.fake_method_two(*self.PASSWORD)
        return self

    def is_logged_in(self) -> bool:
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)
'''

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        # Both invalid methods should be in error message
        assert "fake_method_one" in result["error"].lower()
        assert "fake_method_two" in result["error"].lower()

    def test_post_no_webinterface_calls_passes(self, valid_post_input):
        """
        P1: POST validation passes for POMs with no WebInterface calls.

        Some POMs may only have state-check methods that access attributes.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["code"] = '''class StaticPage:
    TITLE = "Static Page"

    def get_title(self) -> str:
        return self.TITLE

    def is_valid(self) -> bool:
        return True
'''

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "pass", "POMs without WebInterface calls should pass"

    def test_post_private_webinterface_method_fails(self, valid_post_input):
        """
        P1: POST validation fails when code uses private WebInterface method.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["code"] = '''class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def enter_email(self, email: str) -> "LoginPage":
        self.web._take_screenshot()
        self.web.type_text(*self.EMAIL, text=email)
        return self

    def is_logged_in(self) -> bool:
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)
'''

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "_take_screenshot" in result["error"] or "private" in result["error"].lower()

    def test_post_common_webinterface_methods_pass(self, valid_post_input):
        """
        P1: POST validation passes for common WebInterface methods.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        valid_post_input["code"] = '''class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")
    PASSWORD = (By.CSS_SELECTOR, "#passwd")
    SUBMIT = (By.CSS_SELECTOR, "#SubmitLogin")

    def enter_email(self, email: str) -> "LoginPage":
        self.web.type_text(*self.EMAIL, text=email)
        return self

    def click_submit(self) -> "LoginPage":
        self.web.click(*self.SUBMIT)
        return self

    def navigate_to_login(self) -> "LoginPage":
        self.web.navigate_to(self.url)
        return self

    def is_logged_in(self) -> bool:
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)

    def get_error_text(self) -> str:
        return self.web.get_text(*self.ERROR_MESSAGE)
'''

        # Act
        result = QGPageObject.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "pass", f"Common methods should pass: {result.get('error', '')}"

    def test_webinterface_method_pattern_extracts_correctly(self):
        """
        P1: WebInterface method call pattern correctly extracts method names.
        """
        # Arrange
        from tools.gates.qg_page_object import QGPageObject
        code = '''
        self.web.click(*self.BTN)
        self.web.type_text(By.CSS_SELECTOR, "#input", text="test")
        self.web.navigate_to(url)
        self.web.is_element_displayed ( *self.ELEM )
        '''

        # Act
        matches = QGPageObject.WEBINTERFACE_CALL_PATTERN.findall(code)

        # Assert
        assert "click" in matches
        assert "type_text" in matches
        assert "navigate_to" in matches
        assert "is_element_displayed" in matches

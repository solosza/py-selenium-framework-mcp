"""
TDD Tests for QGTestRunner (Step 9 Quality Gate).

Tests PRE and POST validation for Tool 6 (generate_test_runner).

PRE Validation:
- Step 8 complete (role_metadata exists in state)
- role_metadata present and valid
- pom_metadata present and valid
- test_scenarios present (from Step 4)

POST Validation:
- code field present and not empty
- No skeleton code (DD-25): pass, # TODO, placeholder
- At least one role method call (IC-09-03)
- POM state assertions used (IC-09-04, DD-15)
- @autologger.automation_logger("Test") decorator (IC-09-05)
- metadata present with required structure

TDD Approach: Write tests first, then implement gate.
"""

import pytest
from unittest.mock import patch, MagicMock


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def valid_role_metadata():
    """Valid role metadata from Step 8."""
    return {
        "class_name": "RegisteredUser",
        "import_path": "roles.registered_user",
        "workflow_methods": [
            {"name": "login", "params": [], "calls": ["auth_tasks.log_in"]}
        ]
    }


@pytest.fixture
def valid_pom_metadata():
    """Valid POM metadata from Step 6."""
    return {
        "class_name": "LoginPage",
        "import_path": "pages.auth.login_page",
        "state_methods": [
            {"name": "is_logged_in", "params": []}
        ]
    }


@pytest.fixture
def valid_test_scenarios():
    """Valid test scenarios from Step 4."""
    return [
        {
            "name": "test_valid_login",
            "description": "Verify user can login with valid credentials",
            "given": "a registered user",
            "when": "they login with valid credentials",
            "then": "they should see their account page"
        }
    ]


@pytest.fixture
def valid_test_code():
    """Valid generated test code."""
    return '''"""
Test suite for auth workflows.
"""

import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage


class TestLogin:
    """Test suite for login workflows."""

    @pytest.fixture(autouse=True)
    def setup(self, web_interface, config):
        """Setup test fixtures."""
        self.web = web_interface
        self.config = config
        self.base_url = config.get("url", "")
        self.login_page = LoginPage(self.web)

    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_valid_login(self):
        """Test that user can login with valid credentials."""
        # Arrange
        user_data = {"email": "test@example.com", "password": "TestPass123"}
        user = RegisteredUser(self.web, user_data, self.base_url)

        # Act
        user.login()

        # Assert
        assert self.login_page.is_logged_in(), "User should be logged in"
'''


@pytest.fixture
def valid_test_metadata():
    """Valid test metadata."""
    return {
        "class_name": "TestLogin",
        "file_path": "tests/auth/test_login.py",
        "role_used": "RegisteredUser",
        "page_used": "LoginPage",
        "test_methods": ["test_valid_login"]
    }


@pytest.fixture
def mock_state_manager_step8_complete():
    """Mock StateManager with Step 8 complete."""
    mock = MagicMock()
    mock.is_step_complete.return_value = True
    mock.get_step.return_value = {
        "role_metadata": {
            "class_name": "RegisteredUser",
            "import_path": "roles.registered_user"
        }
    }
    return mock


@pytest.fixture
def mock_state_manager_step8_incomplete():
    """Mock StateManager with Step 8 incomplete."""
    mock = MagicMock()
    mock.is_step_complete.return_value = False
    return mock


# =============================================================================
# PRE-VALIDATION: HAPPY PATH
# =============================================================================

class TestPreValidationHappyPath:
    """Test PRE validation passes with valid inputs."""

    def test_pre_valid_all_metadata_present(
        self, valid_role_metadata, valid_pom_metadata, valid_test_scenarios,
        mock_state_manager_step8_complete
    ):
        """PRE passes when all required metadata present."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "role_metadata": valid_role_metadata,
                "pom_metadata": valid_pom_metadata,
                "test_scenarios": valid_test_scenarios
            })

        assert result["status"] == "pass"

    def test_pre_valid_minimal_metadata(
        self, mock_state_manager_step8_complete
    ):
        """PRE passes with minimal but valid metadata."""
        from tools.gates.qg_test_runner import QGTestRunner

        minimal_role = {"class_name": "GuestUser", "import_path": "roles.guest"}
        minimal_pom = {"class_name": "HomePage", "import_path": "pages.home"}
        minimal_scenarios = [{"name": "test_browse"}]

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "role_metadata": minimal_role,
                "pom_metadata": minimal_pom,
                "test_scenarios": minimal_scenarios
            })

        assert result["status"] == "pass"


# =============================================================================
# PRE-VALIDATION: NEGATIVE CASES
# =============================================================================

class TestPreValidationNegative:
    """Test PRE validation fails with invalid inputs."""

    def test_pre_fails_step8_incomplete(
        self, valid_role_metadata, valid_pom_metadata, valid_test_scenarios,
        mock_state_manager_step8_incomplete
    ):
        """PRE fails when Step 8 is not complete."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_incomplete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "role_metadata": valid_role_metadata,
                "pom_metadata": valid_pom_metadata,
                "test_scenarios": valid_test_scenarios
            })

        assert result["status"] == "fail"
        assert "Step 8" in result["error"]

    def test_pre_fails_missing_role_metadata(
        self, valid_pom_metadata, valid_test_scenarios,
        mock_state_manager_step8_complete
    ):
        """PRE fails when role_metadata is missing."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "pom_metadata": valid_pom_metadata,
                "test_scenarios": valid_test_scenarios
            })

        assert result["status"] == "fail"
        assert "role_metadata" in result["error"]

    def test_pre_fails_missing_pom_metadata(
        self, valid_role_metadata, valid_test_scenarios,
        mock_state_manager_step8_complete
    ):
        """PRE fails when pom_metadata is missing."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "role_metadata": valid_role_metadata,
                "test_scenarios": valid_test_scenarios
            })

        assert result["status"] == "fail"
        assert "pom_metadata" in result["error"]

    def test_pre_fails_missing_test_scenarios(
        self, valid_role_metadata, valid_pom_metadata,
        mock_state_manager_step8_complete
    ):
        """PRE fails when test_scenarios is missing."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "role_metadata": valid_role_metadata,
                "pom_metadata": valid_pom_metadata
            })

        assert result["status"] == "fail"
        assert "test_scenarios" in result["error"]

    def test_pre_fails_empty_role_metadata(
        self, valid_pom_metadata, valid_test_scenarios,
        mock_state_manager_step8_complete
    ):
        """PRE fails when role_metadata is empty dict."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "role_metadata": {},
                "pom_metadata": valid_pom_metadata,
                "test_scenarios": valid_test_scenarios
            })

        assert result["status"] == "fail"
        assert "class_name" in result["error"]

    def test_pre_fails_role_metadata_missing_class_name(
        self, valid_pom_metadata, valid_test_scenarios,
        mock_state_manager_step8_complete
    ):
        """PRE fails when role_metadata missing class_name."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "role_metadata": {"import_path": "roles.user"},
                "pom_metadata": valid_pom_metadata,
                "test_scenarios": valid_test_scenarios
            })

        assert result["status"] == "fail"
        assert "class_name" in result["error"]

    def test_pre_fails_pom_metadata_missing_class_name(
        self, valid_role_metadata, valid_test_scenarios,
        mock_state_manager_step8_complete
    ):
        """PRE fails when pom_metadata missing class_name."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "role_metadata": valid_role_metadata,
                "pom_metadata": {"import_path": "pages.login"},
                "test_scenarios": valid_test_scenarios
            })

        assert result["status"] == "fail"
        assert "class_name" in result["error"]

    def test_pre_fails_empty_test_scenarios(
        self, valid_role_metadata, valid_pom_metadata,
        mock_state_manager_step8_complete
    ):
        """PRE fails when test_scenarios is empty list."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "role_metadata": valid_role_metadata,
                "pom_metadata": valid_pom_metadata,
                "test_scenarios": []
            })

        assert result["status"] == "fail"
        assert "test_scenarios" in result["error"]


# =============================================================================
# POST-VALIDATION: HAPPY PATH
# =============================================================================

class TestPostValidationHappyPath:
    """Test POST validation passes with valid output."""

    def test_post_valid_complete_test_code(
        self, valid_test_code, valid_test_metadata
    ):
        """POST passes with complete, valid test code."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": valid_test_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "pass"

    def test_post_valid_multi_role_test(self):
        """POST passes with multi-role test (admin + user)."""
        from tools.gates.qg_test_runner import QGTestRunner

        multi_role_code = '''"""Multi-role test."""
import pytest
from resources.utilities import autologger
from roles.admin_user import AdminUser
from roles.registered_user import RegisteredUser
from pages.admin.user_management_page import UserManagementPage


class TestAdminCreatesUser:
    @pytest.mark.admin
    @autologger.automation_logger("Test")
    def test_admin_created_user_can_login(self):
        """Test admin creates user, user can login."""
        # Arrange
        admin = AdminUser(self.web, admin_data, self.base_url)
        user = RegisteredUser(self.web, user_data, self.base_url)

        # Act
        admin.create_user(user_data)
        admin.logout()
        user.login()

        # Assert
        assert self.user_page.is_logged_in()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": multi_role_code,
            "metadata": {"class_name": "TestAdminCreatesUser", "file_path": "tests/admin/test_create_user.py"}
        })

        assert result["status"] == "pass"

    def test_post_valid_multiple_method_calls(self):
        """POST passes with multiple role method calls in one test."""
        from tools.gates.qg_test_runner import QGTestRunner

        complex_test_code = '''"""Complex workflow test."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.checkout.confirmation_page import ConfirmationPage


class TestPurchaseFlow:
    @pytest.mark.checkout
    @autologger.automation_logger("Test")
    def test_complete_purchase(self):
        """Test complete purchase flow."""
        # Arrange
        user = RegisteredUser(self.web, user_data, self.base_url)

        # Act - Multiple method calls allowed
        user.login()
        user.add_to_cart(product)
        user.checkout()

        # Assert
        assert self.confirmation_page.is_order_confirmed()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": complex_test_code,
            "metadata": {"class_name": "TestPurchaseFlow", "file_path": "tests/checkout/test_purchase.py"}
        })

        assert result["status"] == "pass"


# =============================================================================
# POST-VALIDATION: SKELETON CODE (DD-25, IC-09-02)
# =============================================================================

class TestPostValidationSkeletonCode:
    """Test POST validation catches skeleton code."""

    def test_post_fails_pass_statement(self, valid_test_metadata):
        """POST fails when test has pass statement."""
        from tools.gates.qg_test_runner import QGTestRunner

        skeleton_code = '''"""Test with pass."""
import pytest
from resources.utilities import autologger


class TestPlaceholder:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_placeholder(self):
        """Placeholder test."""
        pass
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": skeleton_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower() or "pass" in result["error"].lower()

    def test_post_fails_todo_comment(self, valid_test_metadata):
        """POST fails when test has TODO comment."""
        from tools.gates.qg_test_runner import QGTestRunner

        todo_code = '''"""Test with TODO."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser


class TestIncomplete:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_incomplete(self):
        """Incomplete test."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        # TODO: Add assertions
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": todo_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "TODO" in result["error"] or "skeleton" in result["error"].lower()

    def test_post_fails_placeholder_comment(self, valid_test_metadata):
        """POST fails when test has placeholder comment."""
        from tools.gates.qg_test_runner import QGTestRunner

        placeholder_code = '''"""Test with placeholder."""
import pytest
from resources.utilities import autologger


class TestPlaceholder:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_placeholder(self):
        """Placeholder test."""
        # Add test implementation as needed
        assert True
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": placeholder_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "placeholder" in result["error"].lower() or "skeleton" in result["error"].lower()

    def test_post_fails_notimplementederror(self, valid_test_metadata):
        """POST fails when test raises NotImplementedError."""
        from tools.gates.qg_test_runner import QGTestRunner

        not_implemented_code = '''"""Test with NotImplementedError."""
import pytest
from resources.utilities import autologger


class TestNotImplemented:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_not_implemented(self):
        """Not implemented test."""
        raise NotImplementedError("Test not implemented")
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": not_implemented_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "NotImplementedError" in result["error"] or "skeleton" in result["error"].lower()


# =============================================================================
# POST-VALIDATION: ROLE METHOD CALLS (IC-09-03)
# =============================================================================

class TestPostValidationRoleMethodCalls:
    """Test POST validation requires at least one role method call."""

    def test_post_fails_no_role_call(self, valid_test_metadata):
        """POST fails when test has no role method calls."""
        from tools.gates.qg_test_runner import QGTestRunner

        no_role_call_code = '''"""Test with no role call."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage


class TestNoRoleCall:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_no_role_call(self):
        """Test without role method call."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        assert self.login_page.is_logged_in()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": no_role_call_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "role" in result["error"].lower() and "call" in result["error"].lower()

    def test_post_passes_single_role_call(self, valid_test_code, valid_test_metadata):
        """POST passes with single role method call."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": valid_test_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "pass"


# =============================================================================
# POST-VALIDATION: POM STATE ASSERTIONS (IC-09-04, DD-15)
# =============================================================================

class TestPostValidationPOMAssertions:
    """Test POST validation requires POM state assertions."""

    def test_post_fails_return_value_assertion(self, valid_test_metadata):
        """POST fails when test asserts on return value instead of POM."""
        from tools.gates.qg_test_runner import QGTestRunner

        return_assertion_code = '''"""Test with return assertion."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser


class TestReturnAssertion:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_return_assertion(self):
        """Test with return value assertion (wrong)."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        result = user.login()
        assert result is True
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": return_assertion_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "return" in result["error"].lower() or "POM" in result["error"]

    def test_post_passes_pom_assertion(self, valid_test_code, valid_test_metadata):
        """POST passes with POM state method assertion."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": valid_test_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "pass"

    def test_post_fails_assert_true_only(self, valid_test_metadata):
        """POST fails when test only has assert True (no real assertion)."""
        from tools.gates.qg_test_runner import QGTestRunner

        assert_true_code = '''"""Test with only assert True."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser


class TestAssertTrue:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_assert_true_only(self):
        """Test with only assert True."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        assert True
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": assert_true_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "assert" in result["error"].lower() or "POM" in result["error"]


# =============================================================================
# POST-VALIDATION: DECORATOR (IC-09-05)
# =============================================================================

class TestPostValidationDecorator:
    """Test POST validation requires @autologger.automation_logger("Test") decorator."""

    def test_post_fails_missing_decorator(self, valid_test_metadata):
        """POST fails when test method missing decorator."""
        from tools.gates.qg_test_runner import QGTestRunner

        no_decorator_code = '''"""Test without decorator."""
import pytest
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage


class TestNoDecorator:
    @pytest.mark.auth
    def test_no_decorator(self):
        """Test without autologger decorator."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        assert self.login_page.is_logged_in()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": no_decorator_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "decorator" in result["error"].lower() or "autologger" in result["error"].lower()

    def test_post_fails_wrong_decorator_type(self, valid_test_metadata):
        """POST fails when decorator has wrong type (not 'Test')."""
        from tools.gates.qg_test_runner import QGTestRunner

        wrong_decorator_code = '''"""Test with wrong decorator type."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage


class TestWrongDecorator:
    @pytest.mark.auth
    @autologger.automation_logger("Role")
    def test_wrong_decorator(self):
        """Test with Role decorator instead of Test."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        assert self.login_page.is_logged_in()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": wrong_decorator_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "Test" in result["error"] or "decorator" in result["error"].lower()


# =============================================================================
# POST-VALIDATION: METADATA STRUCTURE
# =============================================================================

class TestPostValidationMetadata:
    """Test POST validation requires valid metadata."""

    def test_post_fails_missing_metadata(self, valid_test_code):
        """POST fails when metadata is missing."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": valid_test_code
        })

        assert result["status"] == "fail"
        assert "metadata" in result["error"]

    def test_post_fails_empty_metadata(self, valid_test_code):
        """POST fails when metadata is empty."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": valid_test_code,
            "metadata": {}
        })

        assert result["status"] == "fail"
        assert "class_name" in result["error"] or "file_path" in result["error"]

    def test_post_fails_missing_class_name(self, valid_test_code):
        """POST fails when metadata missing class_name."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": valid_test_code,
            "metadata": {"file_path": "tests/auth/test_login.py"}
        })

        assert result["status"] == "fail"
        assert "class_name" in result["error"]

    def test_post_fails_missing_file_path(self, valid_test_code):
        """POST fails when metadata missing file_path."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": valid_test_code,
            "metadata": {"class_name": "TestLogin"}
        })

        assert result["status"] == "fail"
        assert "file_path" in result["error"]

    def test_post_fails_missing_code(self, valid_test_metadata):
        """POST fails when code is missing."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate_post({
            "mode": "POST",
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "code" in result["error"]

    def test_post_fails_empty_code(self, valid_test_metadata):
        """POST fails when code is empty."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": "",
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "code" in result["error"] or "empty" in result["error"].lower()


# =============================================================================
# ROUTE VALIDATION (validate method)
# =============================================================================

class TestValidateRouting:
    """Test validate() routes to correct PRE/POST method."""

    def test_validate_routes_to_pre(
        self, valid_role_metadata, valid_pom_metadata, valid_test_scenarios,
        mock_state_manager_step8_complete
    ):
        """validate() routes to validate_pre when mode=PRE."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate({
                "mode": "PRE",
                "role_metadata": valid_role_metadata,
                "pom_metadata": valid_pom_metadata,
                "test_scenarios": valid_test_scenarios
            })

        assert result["status"] == "pass"

    def test_validate_routes_to_post(self, valid_test_code, valid_test_metadata):
        """validate() routes to validate_post when mode=POST."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate({
            "mode": "POST",
            "code": valid_test_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "pass"

    def test_validate_fails_missing_mode(self):
        """validate() fails when mode is missing."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate({
            "code": "some code"
        })

        assert result["status"] == "fail"
        assert "mode" in result["error"]

    def test_validate_fails_invalid_mode(self):
        """validate() fails when mode is invalid."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate({
            "mode": "INVALID"
        })

        assert result["status"] == "fail"
        assert "mode" in result["error"].lower() or "invalid" in result["error"].lower()

    def test_validate_case_insensitive_mode(self, valid_test_code, valid_test_metadata):
        """validate() handles mode case-insensitively."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate({
            "mode": "post",
            "code": valid_test_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "pass"


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_pre_role_metadata_not_dict(
        self, valid_pom_metadata, valid_test_scenarios,
        mock_state_manager_step8_complete
    ):
        """PRE fails when role_metadata is not a dict."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "role_metadata": "not a dict",
                "pom_metadata": valid_pom_metadata,
                "test_scenarios": valid_test_scenarios
            })

        assert result["status"] == "fail"
        assert "dict" in result["error"].lower() or "role_metadata" in result["error"]

    def test_pre_pom_metadata_not_dict(
        self, valid_role_metadata, valid_test_scenarios,
        mock_state_manager_step8_complete
    ):
        """PRE fails when pom_metadata is not a dict."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "role_metadata": valid_role_metadata,
                "pom_metadata": ["not", "a", "dict"],
                "test_scenarios": valid_test_scenarios
            })

        assert result["status"] == "fail"
        assert "dict" in result["error"].lower() or "pom_metadata" in result["error"]

    def test_pre_test_scenarios_not_list(
        self, valid_role_metadata, valid_pom_metadata,
        mock_state_manager_step8_complete
    ):
        """PRE fails when test_scenarios is not a list."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "role_metadata": valid_role_metadata,
                "pom_metadata": valid_pom_metadata,
                "test_scenarios": {"not": "a list"}
            })

        assert result["status"] == "fail"
        assert "list" in result["error"].lower() or "test_scenarios" in result["error"]

    def test_post_code_not_string(self, valid_test_metadata):
        """POST fails when code is not a string."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": 12345,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "code" in result["error"]


# =============================================================================
# FIX HINTS
# =============================================================================

class TestFixHints:
    """Test that error responses include helpful fix hints."""

    def test_pre_error_includes_fix_hint(
        self, valid_pom_metadata, valid_test_scenarios,
        mock_state_manager_step8_complete
    ):
        """PRE errors include fix_hint field."""
        from tools.gates.qg_test_runner import QGTestRunner

        with patch.object(QGTestRunner, '_get_state_manager', return_value=mock_state_manager_step8_complete):
            result = QGTestRunner.validate_pre({
                "mode": "PRE",
                "pom_metadata": valid_pom_metadata,
                "test_scenarios": valid_test_scenarios
            })

        assert result["status"] == "fail"
        assert "fix_hint" in result
        assert len(result["fix_hint"]) > 0

    def test_post_error_includes_fix_hint(self, valid_test_metadata):
        """POST errors include fix_hint field."""
        from tools.gates.qg_test_runner import QGTestRunner

        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": "",
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "fix_hint" in result
        assert len(result["fix_hint"]) > 0


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

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

    def test_post_valid_multiple_method_calls_multi_persona(self):
        """POST passes with multiple role method calls across DIFFERENT personas (multi-persona exception)."""
        from tools.gates.qg_test_runner import QGTestRunner

        multi_persona_test_code = '''"""Multi-persona workflow test."""
import pytest
from resources.utilities import autologger
from roles.admin_user import AdminUser
from roles.registered_user import RegisteredUser
from pages.user.profile_page import ProfilePage


class TestUserManagement:
    @pytest.mark.admin
    @autologger.automation_logger("Test")
    def test_admin_creates_user_and_user_logs_in(self):
        """Test admin creates user, then new user logs in."""
        # Arrange
        admin = AdminUser(self.web, admin_data, self.base_url)
        new_user = RegisteredUser(self.web, user_data, self.base_url)
        profile_page = ProfilePage(self.web)

        # Act - Multiple calls across DIFFERENT personas (VALID multi-persona)
        admin.create_user(user_data)
        admin.logout()
        new_user.login()

        # Assert
        assert profile_page.is_logged_in()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": multi_persona_test_code,
            "metadata": {"class_name": "TestUserManagement", "file_path": "tests/admin/test_user_management.py"}
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
# POST-VALIDATION: TEST ORCHESTRATION (Pattern-based Smart Gate)
# =============================================================================

class TestPostValidationOrchestration:
    """Test orchestration detection - tests should call ONE workflow method (Pattern-based Smart Gate)."""

    @pytest.mark.unit
    def test_post_multiple_role_calls_single_persona_fails(self, valid_test_metadata):
        """
        P0: Detects multiple Role method calls for SINGLE persona (orchestration violation).

        Pattern-based Smart Gate: Returns NEEDS_RETRY with correct pattern.

        # Arrange
        """
        from tools.gates.qg_test_runner import QGTestRunner
        orchestration_code = '''"""Test with orchestration violation."""
import pytest
from resources.utilities import autologger
from roles.existing_customer import ExistingCustomer
from pages.open_new_account_page import OpenNewAccountPage
from pages.transfer_funds_page import TransferFundsPage


class TestBankingWorkflow:
    @pytest.mark.banking
    @autologger.automation_logger("Test")
    def test_complete_workflow(self):
        """Test orchestrates workflow."""
        # Arrange
        customer = ExistingCustomer(self.web, user_data, self.base_url)

        # Act - ORCHESTRATION VIOLATION: Multiple Role method calls
        customer.open_new_account("SAVINGS", "12345")
        customer.transfer_funds("100", "12345", "54321")
        customer.navigate_to_account_activity()

        # Assert
        assert self.activity_page.is_transaction_visible()
'''
        input_data = {
            "mode": "POST",
            "code": orchestration_code,
            "metadata": valid_test_metadata
        }

        # Act
        result = QGTestRunner.validate_post(input_data)

        # Assert
        assert result["status"] == "NEEDS_RETRY", "Should return NEEDS_RETRY for pattern-based fix"
        assert "orchestrat" in result["error"].lower() or "multiple" in result["error"].lower()
        assert "role" in result["error"].lower() and "method" in result["error"].lower()

    @pytest.mark.unit
    def test_post_orchestration_provides_pattern(self, valid_test_metadata):
        """
        P0: Returns correct pattern from step-09.md when orchestration detected.

        # Arrange
        """
        from tools.gates.qg_test_runner import QGTestRunner
        orchestration_code = '''
class TestWorkflow:
    @autologger.automation_logger("Test")
    def test_workflow(self):
        customer = ExistingCustomer(self.web, user_data, self.base_url)
        customer.open_new_account("SAVINGS", "12345")
        customer.transfer_funds("100", "12345", "54321")
        customer.view_activity()
'''
        input_data = {
            "mode": "POST",
            "code": orchestration_code,
            "metadata": valid_test_metadata
        }

        # Act
        result = QGTestRunner.validate_post(input_data)

        # Assert
        assert result["status"] == "NEEDS_RETRY"
        assert "pattern" in result, "Should include pattern key"

        # Pattern should show ONE workflow method call
        pattern = result["pattern"]
        assert "# ✅ CORRECT" in pattern or "CORRECT PATTERN" in pattern
        assert "ONE" in pattern or "single" in pattern.lower()

        # Pattern should mention Role workflow method
        assert "workflow" in pattern.lower() or "role" in pattern.lower()

    @pytest.mark.unit
    def test_post_pattern_includes_role_and_test_example(self, valid_test_metadata):
        """
        P0: Pattern includes workflow method in Role + test calling it.

        # Arrange
        """
        from tools.gates.qg_test_runner import QGTestRunner
        orchestration_code = '''
class TestWorkflow:
    @autologger.automation_logger("Test")
    def test_workflow(self):
        customer = ExistingCustomer(self.web, user_data, self.base_url)
        customer.method1()
        customer.method2()
        customer.method3()
'''
        input_data = {
            "mode": "POST",
            "code": orchestration_code,
            "metadata": valid_test_metadata
        }

        # Act
        result = QGTestRunner.validate_post(input_data)

        # Assert
        assert result["status"] == "NEEDS_RETRY"
        assert "pattern" in result

        pattern = result["pattern"]
        # Should show Role workflow method definition
        assert "def " in pattern and "self" in pattern, "Should show Role method definition"

        # Should show test calling ONE method
        assert "# Act" in pattern or "ACT" in pattern
        assert ".complete_" in pattern or "workflow" in pattern.lower()

    @pytest.mark.unit
    def test_post_multi_persona_not_flagged(self, valid_test_metadata):
        """
        P0: Multi-persona scenarios ARE valid (different roles).

        # Arrange
        """
        from tools.gates.qg_test_runner import QGTestRunner
        multi_persona_code = '''"""Multi-persona test (VALID)."""
import pytest
from resources.utilities import autologger
from roles.admin_user import AdminUser
from roles.registered_user import RegisteredUser
from pages.admin_page import AdminPage


class TestAdminCreatesUser:
    @pytest.mark.admin
    @autologger.automation_logger("Test")
    def test_admin_created_user_can_login(self):
        """Admin creates user, user logs in (multi-persona - VALID)."""
        # Arrange
        admin = AdminUser(self.web, admin_data, self.base_url)
        new_user = RegisteredUser(self.web, user_data, self.base_url)

        # Act - Multiple Role calls (VALID: different personas)
        admin.create_user(user_data)
        admin.logout()
        new_user.login()

        # Assert
        assert self.admin_page.is_user_created()
        assert self.login_page.is_logged_in()
'''
        input_data = {
            "mode": "POST",
            "code": multi_persona_code,
            "metadata": valid_test_metadata
        }

        # Act
        result = QGTestRunner.validate_post(input_data)

        # Assert
        # Should NOT flag as orchestration (multi-persona is valid)
        if result["status"] == "NEEDS_RETRY":
            assert "orchestrat" not in result.get("error", "").lower(), \
                "Should NOT flag multi-persona scenarios as orchestration"

    @pytest.mark.unit
    def test_post_single_role_call_passes(self, valid_test_code, valid_test_metadata):
        """
        P0: No false positives - tests with ONE role call pass.

        # Arrange
        """
        from tools.gates.qg_test_runner import QGTestRunner

        # valid_test_code has ONE role call: user.login()
        input_data = {
            "mode": "POST",
            "code": valid_test_code,
            "metadata": valid_test_metadata
        }

        # Act
        result = QGTestRunner.validate_post(input_data)

        # Assert
        # Should pass orchestration check (may fail other checks, but not this one)
        if result["status"] == "NEEDS_RETRY":
            assert "orchestrat" not in result.get("error", "").lower(), \
                "Should NOT flag tests with ONE role call"
            assert "multiple" not in result.get("message", "").lower() or \
                   "role" not in result.get("message", "").lower(), \
                "Should NOT flag single role call as orchestration"


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
# POST-VALIDATION: REDUNDANCY DETECTION (DEF-046)
# =============================================================================

class TestDEF046RedundancyDetection:
    """Test POST validation catches redundant tests (subset redundancy)."""

    def test_post_passes_single_test_no_redundancy(self, valid_test_metadata):
        """POST passes when only one test present (no redundancy possible)."""
        from tools.gates.qg_test_runner import QGTestRunner

        single_test_code = '''"""Single test."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage


class TestSingleTest:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_login(self):
        """Test login."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        assert self.login_page.is_logged_in()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": single_test_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "pass"

    def test_post_passes_independent_tests_no_redundancy(self, valid_test_metadata):
        """POST passes when tests have different role calls (no subset)."""
        from tools.gates.qg_test_runner import QGTestRunner

        independent_tests_code = '''"""Independent tests."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage
from pages.catalog.catalog_page import CatalogPage


class TestIndependent:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_login(self):
        """Test login only."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        assert self.login_page.is_logged_in()

    @pytest.mark.catalog
    @autologger.automation_logger("Test")
    def test_browse(self):
        """Test browse only."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.browse_category("Women")
        assert self.catalog_page.has_products()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": independent_tests_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "pass"

    def test_post_fails_test_a_subset_of_test_b(self, valid_test_metadata):
        """POST fails when test A's role calls are subset of test B's."""
        from tools.gates.qg_test_runner import QGTestRunner

        redundant_code = '''"""Redundant tests."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage
from pages.catalog.catalog_page import CatalogPage


class TestRedundant:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_login(self):
        """Test login only (REDUNDANT - subset of test_login_and_browse)."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        assert self.login_page.is_logged_in()

    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_login_and_browse(self):
        """Test login and browse."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        user.browse_category("Women")
        assert self.catalog_page.has_products()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": redundant_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "redundant" in result["error"].lower()
        assert "test_login" in result["error"]
        assert "test_login_and_browse" in result["error"]
        assert "subset" in result["error"].lower()

    def test_post_fails_test_b_subset_of_test_a(self, valid_test_metadata):
        """POST fails when test B's role calls are subset of test A's (reversed order)."""
        from tools.gates.qg_test_runner import QGTestRunner

        redundant_code = '''"""Redundant tests (reversed)."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage
from pages.catalog.catalog_page import CatalogPage


class TestRedundant:
    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_complete_workflow(self):
        """Test complete workflow."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        user.browse_category("Women")
        user.add_to_cart("Blouse")
        assert self.cart_page.has_items()

    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_login_only(self):
        """Test login only (REDUNDANT - subset of test_complete_workflow)."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        assert self.login_page.is_logged_in()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": redundant_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "redundant" in result["error"].lower()
        assert "test_login_only" in result["error"]
        assert "test_complete_workflow" in result["error"]

    def test_post_passes_identical_role_calls(self, valid_test_metadata):
        """POST passes when tests have identical role calls (not considered redundant)."""
        from tools.gates.qg_test_runner import QGTestRunner

        identical_tests_code = '''"""Tests with identical role calls."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage


class TestIdentical:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_login_valid_credentials(self):
        """Test login with valid credentials."""
        user = RegisteredUser(self.web, valid_user_data, self.base_url)
        user.login()
        assert self.login_page.is_logged_in()

    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        user = RegisteredUser(self.web, invalid_user_data, self.base_url)
        user.login()
        assert self.login_page.has_error_message()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": identical_tests_code,
            "metadata": valid_test_metadata
        })

        # Identical role calls means sets are equal, not subset
        assert result["status"] == "pass"

    def test_post_fails_multiple_redundant_tests(self, valid_test_metadata):
        """POST fails when multiple tests have redundancy."""
        from tools.gates.qg_test_runner import QGTestRunner

        multi_redundant_code = '''"""Multiple redundant tests."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage
from pages.catalog.catalog_page import CatalogPage
from pages.cart.cart_page import CartPage


class TestMultiRedundant:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_login(self):
        """Test login only (REDUNDANT)."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        assert self.login_page.is_logged_in()

    @pytest.mark.catalog
    @autologger.automation_logger("Test")
    def test_login_and_browse(self):
        """Test login and browse (REDUNDANT)."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        user.browse_category("Women")
        assert self.catalog_page.has_products()

    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_full_workflow(self):
        """Test full workflow."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        user.browse_category("Women")
        user.add_to_cart("Blouse")
        assert self.cart_page.has_items()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": multi_redundant_code,
            "metadata": valid_test_metadata
        })

        # Should detect first redundancy pair
        assert result["status"] == "fail"
        assert "redundant" in result["error"].lower()

    def test_post_passes_multi_persona_tests(self, valid_test_metadata):
        """POST passes when tests use different roles (admin vs user)."""
        from tools.gates.qg_test_runner import QGTestRunner

        multi_persona_code = '''"""Multi-persona tests."""
import pytest
from resources.utilities import autologger
from roles.admin_user import AdminUser
from roles.registered_user import RegisteredUser
from pages.admin.user_management_page import UserManagementPage
from pages.auth.login_page import LoginPage


class TestMultiPersona:
    @pytest.mark.admin
    @autologger.automation_logger("Test")
    def test_admin_login(self):
        """Test admin login."""
        admin = AdminUser(self.web, admin_data, self.base_url)
        admin.login()
        assert self.admin_page.is_logged_in()

    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_user_login(self):
        """Test user login."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        assert self.login_page.is_logged_in()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": multi_persona_code,
            "metadata": valid_test_metadata
        })

        # Both call login(), but different role instances (admin vs user)
        assert result["status"] == "pass"

    def test_post_error_includes_fix_hint(self, valid_test_metadata):
        """POST redundancy error includes helpful fix hint."""
        from tools.gates.qg_test_runner import QGTestRunner

        redundant_code = '''"""Redundant tests."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage


class TestRedundant:
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_login(self):
        """Test login."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        assert self.login_page.is_logged_in()

    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_login_and_browse(self):
        """Test login and browse."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        user.browse_category("Women")
        assert self.catalog_page.has_products()
'''
        result = QGTestRunner.validate_post({
            "mode": "POST",
            "code": redundant_code,
            "metadata": valid_test_metadata
        })

        assert result["status"] == "fail"
        assert "fix_hint" in result
        assert "One user story" in result["fix_hint"]
        assert "ONE E2E test" in result["fix_hint"]
        assert "Merge" in result["fix_hint"] or "split" in result["fix_hint"].lower()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

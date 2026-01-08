"""
Unit tests for QGTask quality gate (Step 7).

Tests PRE+POST validation for Tool 4 (generate_task).

Enforces:
- DD-12: Check existing before generate (AI behavior, not gate)
- DD-25: No skeleton code
- DD-26: Metadata contracts
- DD-27: No locators in Task code
- IC-07-01 through IC-07-05

Test Categories:
- PRE-Happy: Valid inputs pass (3 tests)
- PRE-Negative: Invalid inputs fail (8 tests)
- POST-Happy: Valid outputs pass (2 tests)
- POST-Skeleton: DD-25 skeleton detection (4 tests)
- POST-Locator: DD-27 locator detection (3 tests)
- POST-Return: IC-07-02 return value detection (2 tests)
- POST-Decorator: IC-07-04 decorator check (2 tests)
- POST-Metadata: DD-26 metadata validation (5 tests)
- Route: Mode routing (5 tests)
- Edge: Edge cases (2 tests)
- Hints: Fix hint messages (2 tests)

Total: 38 tests
"""

import pytest
from unittest.mock import patch, MagicMock


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def valid_pom_metadata():
    """Valid POM metadata from Tool 3."""
    return {
        "class_name": "LoginPage",
        "import_path": "pages.auth.login_page",
        "action_methods": [
            {"name": "enter_email", "params": ["text: str"]},
            {"name": "enter_password", "params": ["text: str"]},
            {"name": "click_submit", "params": []}
        ],
        "state_methods": [
            {"name": "is_logged_in", "params": []}
        ],
        "locators": ["EMAIL", "PASSWORD", "SUBMIT_BTN"]
    }


@pytest.fixture
def valid_pre_input(valid_pom_metadata):
    """Valid PRE validation input."""
    return {
        "mode": "PRE",
        "pom_metadata": valid_pom_metadata,
        "domain": "auth",
        "task_name": "AuthTasks"
    }


@pytest.fixture
def valid_task_code():
    """Valid Task code with no skeleton, no locators, proper decorator."""
    return '''"""
AuthTasks - Task module for Authentication workflows.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from pages.auth.login_page import LoginPage


class AuthTasks:
    """Task module for authentication operations."""

    def __init__(self, web: WebInterface, base_url: str):
        """Compose Page Objects - NO decorator on constructor."""
        self.web = web
        self.base_url = base_url
        self.login_page = LoginPage(web)

    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        """
        Complete login operation.
        NO return value - test asserts via POM.
        """
        # DD-49: Tasks call POM navigate() method
        self.login_page.navigate()

        (self.login_page
            .enter_email(email)
            .enter_password(password)
            .click_submit())
        # NO return
'''


@pytest.fixture
def valid_task_metadata():
    """Valid Task metadata from Tool 4."""
    return {
        "class_name": "AuthTasks",
        "import_path": "tasks.auth.auth_tasks",
        "composed_pages": ["LoginPage"],
        "task_methods": [
            {
                "name": "log_in",
                "params": ["email: str", "password: str"],
                "calls": ["enter_email", "enter_password", "click_submit"]
            }
        ]
    }


@pytest.fixture
def valid_post_input(valid_task_code, valid_task_metadata):
    """Valid POST validation input."""
    return {
        "mode": "POST",
        "code": valid_task_code,
        "metadata": valid_task_metadata
    }


@pytest.fixture
def mock_state_manager_step6_complete():
    """Mock StateManager with Step 6 complete."""
    with patch('tools.gates.qg_task.QGTask._get_state_manager') as mock:
        manager = MagicMock()
        manager.is_step_complete.return_value = True
        mock.return_value = manager
        yield mock


@pytest.fixture
def mock_state_manager_step6_incomplete():
    """Mock StateManager with Step 6 incomplete."""
    with patch('tools.gates.qg_task.QGTask._get_state_manager') as mock:
        manager = MagicMock()
        manager.is_step_complete.return_value = False
        mock.return_value = manager
        yield mock


# =============================================================================
# PRE-HAPPY: Valid inputs pass (3 tests)
# =============================================================================

class TestPreHappy:
    """PRE validation happy path tests."""

    @pytest.mark.unit
    def test_pre_all_valid_passes(self, valid_pre_input, mock_state_manager_step6_complete):
        """
        P0: Valid PRE input passes validation.

        # Arrange
        """
        from tools.gates.qg_task import QGTask

        # Act
        result = QGTask.validate_pre(valid_pre_input)

        # Assert
        assert result["status"] == "pass", "Valid PRE input should pass"

    @pytest.mark.unit
    def test_pre_step_6_complete_checked(self, valid_pre_input, mock_state_manager_step6_complete):
        """
        P0: Step 6 completion is verified.

        # Arrange
        """
        from tools.gates.qg_task import QGTask

        # Act
        QGTask.validate_pre(valid_pre_input)

        # Assert
        mock_state_manager_step6_complete.return_value.is_step_complete.assert_called_with(6)

    @pytest.mark.unit
    def test_pre_minimal_pom_metadata_passes(self, mock_state_manager_step6_complete):
        """
        P1: Minimal valid pom_metadata passes.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "PRE",
            "pom_metadata": {
                "class_name": "LoginPage",
                "action_methods": []  # Empty but present
            },
            "domain": "auth",
            "task_name": "AuthTasks"
        }

        # Act
        result = QGTask.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Minimal pom_metadata should pass"


# =============================================================================
# PRE-NEGATIVE: Invalid inputs fail (8 tests)
# =============================================================================

class TestPreNegative:
    """PRE validation negative tests."""

    @pytest.mark.unit
    def test_pre_step_6_incomplete_fails(self, valid_pre_input, mock_state_manager_step6_incomplete):
        """
        P0: Step 6 incomplete fails validation.

        # Arrange
        """
        from tools.gates.qg_task import QGTask

        # Act
        result = QGTask.validate_pre(valid_pre_input)

        # Assert
        assert result["status"] == "fail", "Step 6 incomplete should fail"
        assert "Step 6" in result["error"], "Error should mention Step 6"

    @pytest.mark.unit
    def test_pre_pom_metadata_missing_fails(self, mock_state_manager_step6_complete):
        """
        P0: Missing pom_metadata fails validation.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "PRE",
            "domain": "auth",
            "task_name": "AuthTasks"
        }

        # Act
        result = QGTask.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Missing pom_metadata should fail"
        assert "pom_metadata" in result["error"], "Error should mention pom_metadata"

    @pytest.mark.unit
    def test_pre_pom_metadata_not_dict_fails(self, mock_state_manager_step6_complete):
        """
        P1: pom_metadata not a dict fails validation.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "PRE",
            "pom_metadata": "not a dict",
            "domain": "auth",
            "task_name": "AuthTasks"
        }

        # Act
        result = QGTask.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "pom_metadata not dict should fail"

    @pytest.mark.unit
    def test_pre_class_name_missing_fails(self, mock_state_manager_step6_complete):
        """
        P0: IC-07-05 - Missing class_name in pom_metadata fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "PRE",
            "pom_metadata": {
                "action_methods": []
            },
            "domain": "auth",
            "task_name": "AuthTasks"
        }

        # Act
        result = QGTask.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Missing class_name should fail"
        assert "class_name" in result["error"], "Error should mention class_name"

    @pytest.mark.unit
    def test_pre_class_name_empty_fails(self, mock_state_manager_step6_complete):
        """
        P1: Empty class_name in pom_metadata fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "PRE",
            "pom_metadata": {
                "class_name": "",
                "action_methods": []
            },
            "domain": "auth",
            "task_name": "AuthTasks"
        }

        # Act
        result = QGTask.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Empty class_name should fail"

    @pytest.mark.unit
    def test_pre_empty_workflow_fails(self, valid_pom_metadata, mock_state_manager_step6_complete):
        """
        P0: Empty workflow fails validation.

        Workflow/domain is dynamic - any non-empty string is valid.
        Only empty/missing workflow should fail.
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "PRE",
            "pom_metadata": valid_pom_metadata,
            "workflow": "",  # Empty workflow should fail
            "task_name": "AuthTasks"
        }

        # Act
        result = QGTask.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Empty workflow should fail"
        assert "workflow" in result["error"].lower() or "domain" in result["error"].lower(), "Error should mention workflow/domain"

    @pytest.mark.unit
    def test_pre_task_name_missing_fails(self, valid_pom_metadata, mock_state_manager_step6_complete):
        """
        P0: Missing task_name fails validation.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "PRE",
            "pom_metadata": valid_pom_metadata,
            "domain": "auth"
        }

        # Act
        result = QGTask.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Missing task_name should fail"
        assert "task_name" in result["error"], "Error should mention task_name"

    @pytest.mark.unit
    def test_pre_task_name_empty_fails(self, valid_pom_metadata, mock_state_manager_step6_complete):
        """
        P1: Empty task_name fails validation.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "PRE",
            "pom_metadata": valid_pom_metadata,
            "domain": "auth",
            "task_name": ""
        }

        # Act
        result = QGTask.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Empty task_name should fail"


# =============================================================================
# POST-HAPPY: Valid outputs pass (2 tests)
# =============================================================================

class TestPostHappy:
    """POST validation happy path tests."""

    @pytest.mark.unit
    def test_post_valid_code_and_metadata_passes(self, valid_post_input):
        """
        P0: Valid Task code and metadata passes POST validation.

        # Arrange
        """
        from tools.gates.qg_task import QGTask

        # Act
        result = QGTask.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "pass", "Valid POST input should pass"

    @pytest.mark.unit
    def test_post_code_with_bare_return_passes(self, valid_task_metadata):
        """
        P1: Code with bare 'return' or 'return None' passes.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        code_with_return_none = '''
class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        self.login_page.enter_email(email)
        return None

    @autologger.automation_logger("Task")
    def log_out(self) -> None:
        self.login_page.click_logout()
        return
'''
        input_data = {
            "mode": "POST",
            "code": code_with_return_none,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Bare return/return None should pass"


# =============================================================================
# POST-SKELETON: DD-25 skeleton detection (4 tests)
# =============================================================================

class TestPostSkeleton:
    """POST validation skeleton code detection (DD-25, IC-07-01)."""

    @pytest.mark.unit
    def test_post_skeleton_pass_statement_fails(self, valid_task_metadata):
        """
        P0: DD-25 - Skeleton code with 'pass' fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        skeleton_code = '''
class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        pass
'''
        input_data = {
            "mode": "POST",
            "code": skeleton_code,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Skeleton pass should fail"
        assert "skeleton" in result["error"].lower() or "pass" in result["error"].lower()

    @pytest.mark.unit
    def test_post_skeleton_add_comment_fails(self, valid_task_metadata):
        """
        P0: DD-25 - Skeleton code with '# Add ... as needed' fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        skeleton_code = '''
class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        self.login_page.enter_email(email)
        # Add additional steps as needed
'''
        input_data = {
            "mode": "POST",
            "code": skeleton_code,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Skeleton Add comment should fail"

    @pytest.mark.unit
    def test_post_skeleton_notimplementederror_fails(self, valid_task_metadata):
        """
        P0: DD-25 - Skeleton code with NotImplementedError fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        skeleton_code = '''
class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        raise NotImplementedError("TODO: implement")
'''
        input_data = {
            "mode": "POST",
            "code": skeleton_code,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "NotImplementedError should fail"

    @pytest.mark.unit
    def test_post_skeleton_todo_comment_fails(self, valid_task_metadata):
        """
        P0: DD-25 - Skeleton code with '# TODO:' fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        skeleton_code = '''
class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        # TODO: implement login
        self.login_page.enter_email(email)
'''
        input_data = {
            "mode": "POST",
            "code": skeleton_code,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "TODO comment should fail"


# =============================================================================
# POST-LOCATOR: DD-27 locator detection (3 tests)
# =============================================================================

class TestPostLocator:
    """POST validation locator detection (DD-27, IC-07-03)."""

    @pytest.mark.unit
    def test_post_by_import_fails(self, valid_task_metadata):
        """
        P0: DD-27 - Code with 'from selenium...import By' fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        code_with_locator = '''
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface

class AuthTasks:
    EMAIL = (By.CSS_SELECTOR, "#email")

    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        self.web.click(*self.EMAIL)
'''
        input_data = {
            "mode": "POST",
            "code": code_with_locator,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "By import should fail"
        assert "locator" in result["error"].lower() or "DD-27" in result["error"]

    @pytest.mark.unit
    def test_post_by_tuple_fails(self, valid_task_metadata):
        """
        P0: DD-27 - Code with (By.CSS_SELECTOR, ...) tuple fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        code_with_locator = '''
class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        locator = (By.CSS_SELECTOR, "#email")
        self.web.type_text(*locator, email)
'''
        input_data = {
            "mode": "POST",
            "code": code_with_locator,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "By tuple should fail"

    @pytest.mark.unit
    def test_post_find_element_fails(self, valid_task_metadata):
        """
        P0: DD-27 - Code with driver.find_element() fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        code_with_locator = '''
class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        element = self.driver.find_element(By.ID, "email")
        element.send_keys(email)
'''
        input_data = {
            "mode": "POST",
            "code": code_with_locator,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "find_element should fail"


# =============================================================================
# POST-RETURN: IC-07-02 return value detection (2 tests)
# =============================================================================

class TestPostReturn:
    """POST validation return value detection (IC-07-02)."""

    @pytest.mark.unit
    def test_post_return_value_fails(self, valid_task_metadata):
        """
        P0: IC-07-02 - Method returning value fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        code_with_return = '''
class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> bool:
        self.login_page.enter_email(email)
        self.login_page.enter_password(password)
        self.login_page.click_submit()
        return True
'''
        input_data = {
            "mode": "POST",
            "code": code_with_return,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Return value should fail"
        assert "return" in result["error"].lower(), "Error should mention return"

    @pytest.mark.unit
    def test_post_return_self_fails(self, valid_task_metadata):
        """
        P1: IC-07-02 - Method returning self fails (Tasks don't chain).

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        code_with_return = '''
class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str):
        self.login_page.enter_email(email)
        return self
'''
        input_data = {
            "mode": "POST",
            "code": code_with_return,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Return self should fail"


# =============================================================================
# POST-DECORATOR: IC-07-04 decorator check (2 tests)
# =============================================================================

class TestPostDecorator:
    """POST validation decorator check (IC-07-04)."""

    @pytest.mark.unit
    def test_post_missing_decorator_fails(self, valid_task_metadata):
        """
        P0: IC-07-04 - Missing @autologger decorator fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        code_no_decorator = '''
class AuthTasks:
    def log_in(self, email: str, password: str) -> None:
        self.login_page.enter_email(email)
        self.login_page.enter_password(password)
        self.login_page.click_submit()
'''
        input_data = {
            "mode": "POST",
            "code": code_no_decorator,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Missing decorator should fail"
        assert "decorator" in result["error"].lower() or "autologger" in result["error"].lower()

    @pytest.mark.unit
    def test_post_wrong_decorator_type_fails(self, valid_task_metadata):
        """
        P1: IC-07-04 - Wrong decorator type (Role instead of Task) fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        code_wrong_decorator = '''
class AuthTasks:
    @autologger.automation_logger("Role")
    def log_in(self, email: str, password: str) -> None:
        self.login_page.enter_email(email)
'''
        input_data = {
            "mode": "POST",
            "code": code_wrong_decorator,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Wrong decorator type should fail"


# =============================================================================
# POST-METADATA: DD-26 metadata validation (5 tests)
# =============================================================================

class TestPostMetadata:
    """POST validation metadata structure (DD-26)."""

    @pytest.mark.unit
    def test_post_code_missing_fails(self):
        """
        P0: Missing code field fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "POST",
            "metadata": {"class_name": "AuthTasks"}
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Missing code should fail"
        assert "code" in result["error"], "Error should mention code"

    @pytest.mark.unit
    def test_post_code_empty_fails(self, valid_task_metadata):
        """
        P0: Empty code field fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "POST",
            "code": "",
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Empty code should fail"

    @pytest.mark.unit
    def test_post_metadata_missing_fails(self, valid_task_code):
        """
        P0: Missing metadata field fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "POST",
            "code": valid_task_code
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Missing metadata should fail"
        assert "metadata" in result["error"], "Error should mention metadata"

    @pytest.mark.unit
    def test_post_metadata_class_name_missing_fails(self, valid_task_code):
        """
        P0: DD-26 - Missing class_name in metadata fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "POST",
            "code": valid_task_code,
            "metadata": {
                "import_path": "tasks.auth.auth_tasks",
                "task_methods": []
            }
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Missing class_name should fail"

    @pytest.mark.unit
    def test_post_metadata_import_path_missing_fails(self, valid_task_code):
        """
        P0: DD-26 - Missing import_path in metadata fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "POST",
            "code": valid_task_code,
            "metadata": {
                "class_name": "AuthTasks",
                "task_methods": []
            }
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Missing import_path should fail"


# =============================================================================
# ROUTE: Mode routing (5 tests)
# =============================================================================

class TestRoute:
    """Mode routing tests."""

    @pytest.mark.unit
    def test_validate_routes_to_pre(self, valid_pre_input, mock_state_manager_step6_complete):
        """
        P0: mode='PRE' routes to validate_pre().

        # Arrange
        """
        from tools.gates.qg_task import QGTask

        # Act
        result = QGTask.validate(valid_pre_input)

        # Assert
        assert result["status"] == "pass", "PRE mode should route correctly"

    @pytest.mark.unit
    def test_validate_routes_to_post(self, valid_post_input):
        """
        P0: mode='POST' routes to validate_post().

        # Arrange
        """
        from tools.gates.qg_task import QGTask

        # Act
        result = QGTask.validate(valid_post_input)

        # Assert
        assert result["status"] == "pass", "POST mode should route correctly"

    @pytest.mark.unit
    def test_validate_invalid_mode_fails(self):
        """
        P0: Invalid mode fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {"mode": "INVALID"}

        # Act
        result = QGTask.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Invalid mode should fail"
        assert "mode" in result["error"].lower(), "Error should mention mode"

    @pytest.mark.unit
    def test_validate_empty_mode_fails(self):
        """
        P1: Empty mode fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {"mode": ""}

        # Act
        result = QGTask.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty mode should fail"

    @pytest.mark.unit
    def test_validate_missing_mode_fails(self):
        """
        P1: Missing mode fails.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {}

        # Act
        result = QGTask.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Missing mode should fail"


# =============================================================================
# EDGE: Edge cases (2 tests)
# =============================================================================

class TestEdge:
    """Edge case tests."""

    @pytest.mark.unit
    def test_pre_domain_case_insensitive(self, valid_pom_metadata, mock_state_manager_step6_complete):
        """
        P2: Domain validation is case-insensitive.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        input_data = {
            "mode": "PRE",
            "pom_metadata": valid_pom_metadata,
            "domain": "AUTH",  # Uppercase
            "task_name": "AuthTasks"
        }

        # Act
        result = QGTask.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Uppercase domain should pass"

    @pytest.mark.unit
    def test_post_multiline_return_detection(self, valid_task_metadata):
        """
        P2: Return value detection works across multiline.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        code_with_return = '''
class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str):
        result = self.login_page.enter_email(email)
        return (
            result
        )
'''
        input_data = {
            "mode": "POST",
            "code": code_with_return,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Multiline return should be caught"


# =============================================================================
# HINTS: Fix hint messages (2 tests)
# =============================================================================

class TestHints:
    """Fix hint message tests."""

    @pytest.mark.unit
    def test_fix_hint_for_skeleton_code(self, valid_task_metadata):
        """
        P1: Skeleton code error includes fix hint.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        skeleton_code = '''
class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        pass
'''
        input_data = {
            "mode": "POST",
            "code": skeleton_code,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "fix_hint" in result, "Should include fix_hint"
        assert len(result["fix_hint"]) > 0, "fix_hint should not be empty"

    @pytest.mark.unit
    def test_fix_hint_for_locators(self, valid_task_metadata):
        """
        P1: Locator error includes fix hint mentioning POM.

        # Arrange
        """
        from tools.gates.qg_task import QGTask
        code_with_locator = '''
from selenium.webdriver.common.by import By

class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        self.web.click(By.ID, "submit")
'''
        input_data = {
            "mode": "POST",
            "code": code_with_locator,
            "metadata": valid_task_metadata
        }

        # Act
        result = QGTask.validate_post(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "fix_hint" in result, "Should include fix_hint"
        assert "pom" in result["fix_hint"].lower() or "page object" in result["fix_hint"].lower()

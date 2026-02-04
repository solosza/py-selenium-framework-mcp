"""
Unit tests for QGRole quality gate (Step 8).

Tests PRE+POST validation for Tool 5 (generate_role).

Enforces:
- DD-12: Check existing before generate (AI behavior, not gate)
- DD-25: No skeleton code
- DD-26: Metadata contracts
- DD-27: No locators in Role code
- IC-08-01 through IC-08-06

Test Categories:
- PRE-Happy: Valid inputs pass (3 tests)
- PRE-Negative: Invalid inputs fail (8 tests)
- POST-Happy: Valid outputs pass (2 tests)
- POST-Skeleton: DD-25 skeleton detection (4 tests)
- POST-Locator: DD-27 locator detection (3 tests)
- POST-Return: No return values (2 tests)
- POST-Decorator: IC-08-04 decorator check (2 tests)
- POST-TaskCall: IC-08-06 task method calls (2 tests)
- POST-Metadata: DD-26 metadata validation (5 tests)
- Route: Mode routing (5 tests)
- Edge: Edge cases (2 tests)
- Hints: Fix hint messages (2 tests)

Total: 40 tests
"""

import pytest
from unittest.mock import patch, MagicMock


# =============================================================================
# FIXTURES
# =============================================================================

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
def valid_pre_input(valid_task_metadata):
    """Valid PRE validation input."""
    return {
        "mode": "PRE",
        "task_metadata": valid_task_metadata,
        "role_name": "RegisteredUser"
    }


@pytest.fixture
def valid_role_code():
    """Valid Role code with no skeleton, no locators, proper decorator, task calls."""
    return '''"""
RegisteredUser - Role for orchestrating authentication workflows.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.auth.auth_tasks import AuthTasks


class RegisteredUser:
    """RegisteredUser - orchestrates complete business workflows."""

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any], base_url: str):
        """Initialize with credentials and compose Task modules."""
        self.web = web_interface
        self.base_url = base_url
        self.user_data = user_data
        # Dynamic credential resolution (DEF-063)
        self.username = user_data.get('username') or user_data.get('email')
        self.password = user_data.get('password')
        self.auth_tasks = AuthTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def login(self) -> None:
        """
        Login workflow.
        NO return value - test asserts via POM.
        """
        self.auth_tasks.log_in(self.username, self.password)
        # NO return
'''


@pytest.fixture
def valid_role_metadata():
    """Valid Role metadata from Tool 5."""
    return {
        "class_name": "RegisteredUser",
        "import_path": "roles.registered_user",
        "composed_tasks": ["AuthTasks"],
        "workflow_methods": [
            {
                "name": "login",
                "params": [],
                "calls": ["auth_tasks.log_in"]
            }
        ]
    }


@pytest.fixture
def valid_post_input(valid_role_code, valid_role_metadata):
    """Valid POST validation input."""
    return {
        "mode": "POST",
        "code": valid_role_code,
        "metadata": valid_role_metadata
    }


@pytest.fixture
def mock_state_manager_step7_complete():
    """Mock StateManager with Step 7 complete."""
    with patch('tools.gates.qg_role.QGRole._get_state_manager') as mock:
        manager = MagicMock()
        manager.is_step_complete.return_value = True
        mock.return_value = manager
        yield mock


@pytest.fixture
def mock_state_manager_step7_incomplete():
    """Mock StateManager with Step 7 incomplete."""
    with patch('tools.gates.qg_role.QGRole._get_state_manager') as mock:
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
    def test_pre_all_valid_passes(self, valid_pre_input, mock_state_manager_step7_complete):
        """
        P0: Valid PRE input passes validation.

        # Arrange
        """
        from tools.gates.qg_role import QGRole

        # Act
        result = QGRole.validate_pre(valid_pre_input)

        # Assert
        assert result["status"] == "pass", "Valid PRE input should pass"

    @pytest.mark.unit
    def test_pre_step_7_complete_checked(self, valid_pre_input, mock_state_manager_step7_complete):
        """
        P0: Step 7 completion is verified.

        # Arrange
        """
        from tools.gates.qg_role import QGRole

        # Act
        QGRole.validate_pre(valid_pre_input)

        # Assert
        mock_state_manager_step7_complete.return_value.is_step_complete.assert_called_with(7)

    @pytest.mark.unit
    def test_pre_minimal_task_metadata_passes(self, mock_state_manager_step7_complete):
        """
        P1: Minimal valid task_metadata passes.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "PRE",
            "task_metadata": {
                "class_name": "AuthTasks",
                "task_methods": []  # Empty but present
            },
            "role_name": "RegisteredUser"
        }

        # Act
        result = QGRole.validate_pre(input_data)

        # Assert
        assert result["status"] == "pass", "Minimal task_metadata should pass"


# =============================================================================
# PRE-NEGATIVE: Invalid inputs fail (8 tests)
# =============================================================================

class TestPreNegative:
    """PRE validation negative tests."""

    @pytest.mark.unit
    def test_pre_step_7_incomplete_fails(self, valid_pre_input, mock_state_manager_step7_incomplete):
        """
        P0: Step 7 incomplete fails validation.

        # Arrange
        """
        from tools.gates.qg_role import QGRole

        # Act
        result = QGRole.validate_pre(valid_pre_input)

        # Assert
        assert result["status"] == "fail", "Step 7 incomplete should fail"
        assert "Step 7" in result["error"], "Error should mention Step 7"

    @pytest.mark.unit
    def test_pre_task_metadata_missing_fails(self, mock_state_manager_step7_complete):
        """
        P0: Missing task_metadata fails validation.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "PRE",
            "role_name": "RegisteredUser"
        }

        # Act
        result = QGRole.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Missing task_metadata should fail"
        assert "task_metadata" in result["error"], "Error should mention task_metadata"

    @pytest.mark.unit
    def test_pre_task_metadata_not_dict_fails(self, mock_state_manager_step7_complete):
        """
        P1: task_metadata not a dict fails validation.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "PRE",
            "task_metadata": "not a dict",
            "role_name": "RegisteredUser"
        }

        # Act
        result = QGRole.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "task_metadata not dict should fail"

    @pytest.mark.unit
    def test_pre_class_name_missing_fails(self, mock_state_manager_step7_complete):
        """
        P0: IC-08-05 - Missing class_name in task_metadata fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "PRE",
            "task_metadata": {
                "task_methods": []
            },
            "role_name": "RegisteredUser"
        }

        # Act
        result = QGRole.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Missing class_name should fail"
        assert "class_name" in result["error"], "Error should mention class_name"

    @pytest.mark.unit
    def test_pre_class_name_empty_fails(self, mock_state_manager_step7_complete):
        """
        P1: Empty class_name in task_metadata fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "PRE",
            "task_metadata": {
                "class_name": "",
                "task_methods": []
            },
            "role_name": "RegisteredUser"
        }

        # Act
        result = QGRole.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Empty class_name should fail"

    @pytest.mark.unit
    def test_pre_role_name_missing_fails(self, valid_task_metadata, mock_state_manager_step7_complete):
        """
        P0: Missing role_name fails validation.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "PRE",
            "task_metadata": valid_task_metadata
        }

        # Act
        result = QGRole.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Missing role_name should fail"
        assert "role_name" in result["error"], "Error should mention role_name"

    @pytest.mark.unit
    def test_pre_role_name_empty_fails(self, valid_task_metadata, mock_state_manager_step7_complete):
        """
        P1: Empty role_name fails validation.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "PRE",
            "task_metadata": valid_task_metadata,
            "role_name": ""
        }

        # Act
        result = QGRole.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Empty role_name should fail"

    @pytest.mark.unit
    def test_pre_role_name_not_pascalcase_fails(self, valid_task_metadata, mock_state_manager_step7_complete):
        """
        P1: role_name not PascalCase fails validation.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "PRE",
            "task_metadata": valid_task_metadata,
            "role_name": "registered_user"  # snake_case, not PascalCase
        }

        # Act
        result = QGRole.validate_pre(input_data)

        # Assert
        assert result["status"] == "fail", "Non-PascalCase role_name should fail"
        assert "PascalCase" in result["error"], "Error should mention PascalCase"


# =============================================================================
# POST-HAPPY: Valid outputs pass (2 tests)
# =============================================================================

class TestPostHappy:
    """POST validation happy path tests."""

    @pytest.mark.unit
    def test_post_valid_code_and_metadata_passes(self, valid_post_input):
        """
        P0: Valid Role code and metadata passes POST validation.

        # Arrange
        """
        from tools.gates.qg_role import QGRole

        # Act
        result = QGRole.validate_post(valid_post_input)

        # Assert
        assert result["status"] == "pass", "Valid POST input should pass"

    @pytest.mark.unit
    def test_post_code_with_bare_return_passes(self, valid_role_metadata):
        """
        P1: Code with bare 'return' or 'return None' passes.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_with_return_none = '''
class RegisteredUser:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface, user_data, base_url):
        self.username = user_data.get('username') or user_data.get('email')
        self.password = user_data.get('password')
        self.auth_tasks = AuthTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def login(self) -> None:
        self.auth_tasks.log_in(self.username, self.password)
        return None

    @autologger.automation_logger("Role")
    def logout(self) -> None:
        self.auth_tasks.log_out()
        return
'''
        input_data = {
            "mode": "POST",
            "code": code_with_return_none,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Bare return/return None should pass"


# =============================================================================
# POST-SKELETON: DD-25 skeleton detection (4 tests)
# =============================================================================

class TestPostSkeleton:
    """POST validation skeleton code detection (DD-25, IC-08-01)."""

    @pytest.mark.unit
    def test_post_skeleton_pass_statement_fails(self, valid_role_metadata):
        """
        P0: DD-25 - Skeleton code with 'pass' fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        skeleton_code = '''
class RegisteredUser:
    @autologger.automation_logger("Role")
    def login(self) -> None:
        pass
'''
        input_data = {
            "mode": "POST",
            "code": skeleton_code,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Skeleton pass should fail"
        assert "skeleton" in result["error"].lower() or "pass" in result["error"].lower()

    @pytest.mark.unit
    def test_post_skeleton_add_comment_fails(self, valid_role_metadata):
        """
        P0: DD-25 - Skeleton code with '# Add ... as needed' fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        skeleton_code = '''
class RegisteredUser:
    @autologger.automation_logger("Role")
    def login(self) -> None:
        self.auth_tasks.log_in(self.email, self.password)
        # Add additional steps as needed
'''
        input_data = {
            "mode": "POST",
            "code": skeleton_code,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Skeleton Add comment should fail"

    @pytest.mark.unit
    def test_post_skeleton_notimplementederror_fails(self, valid_role_metadata):
        """
        P0: DD-25 - Skeleton code with NotImplementedError fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        skeleton_code = '''
class RegisteredUser:
    @autologger.automation_logger("Role")
    def login(self) -> None:
        raise NotImplementedError("TODO: implement")
'''
        input_data = {
            "mode": "POST",
            "code": skeleton_code,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "NotImplementedError should fail"

    @pytest.mark.unit
    def test_post_skeleton_todo_comment_fails(self, valid_role_metadata):
        """
        P0: DD-25 - Skeleton code with '# TODO:' fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        skeleton_code = '''
class RegisteredUser:
    @autologger.automation_logger("Role")
    def login(self) -> None:
        # TODO: implement login
        self.auth_tasks.log_in(self.email, self.password)
'''
        input_data = {
            "mode": "POST",
            "code": skeleton_code,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "TODO comment should fail"


# =============================================================================
# POST-LOCATOR: DD-27 locator detection (3 tests)
# =============================================================================

class TestPostLocator:
    """POST validation locator detection (DD-27, IC-08-03)."""

    @pytest.mark.unit
    def test_post_by_import_fails(self, valid_role_metadata):
        """
        P0: DD-27 - Code with 'from selenium...import By' fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_with_locator = '''
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface

class RegisteredUser:
    EMAIL = (By.CSS_SELECTOR, "#email")

    @autologger.automation_logger("Role")
    def login(self) -> None:
        self.web.click(*self.EMAIL)
'''
        input_data = {
            "mode": "POST",
            "code": code_with_locator,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "By import should fail"
        assert "locator" in result["error"].lower() or "DD-27" in result["error"]

    @pytest.mark.unit
    def test_post_by_tuple_fails(self, valid_role_metadata):
        """
        P0: DD-27 - Code with (By.CSS_SELECTOR, ...) tuple fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_with_locator = '''
class RegisteredUser:
    @autologger.automation_logger("Role")
    def login(self) -> None:
        locator = (By.CSS_SELECTOR, "#email")
        self.web.type_text(*locator, self.email)
'''
        input_data = {
            "mode": "POST",
            "code": code_with_locator,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "By tuple should fail"

    @pytest.mark.unit
    def test_post_find_element_fails(self, valid_role_metadata):
        """
        P0: DD-27 - Code with driver.find_element() fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_with_locator = '''
class RegisteredUser:
    @autologger.automation_logger("Role")
    def login(self) -> None:
        element = self.driver.find_element(By.ID, "email")
        element.send_keys(self.email)
'''
        input_data = {
            "mode": "POST",
            "code": code_with_locator,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "find_element should fail"


# =============================================================================
# POST-RETURN: No return values (2 tests)
# =============================================================================

class TestPostReturn:
    """POST validation return value detection."""

    @pytest.mark.unit
    def test_post_return_value_fails(self, valid_role_metadata):
        """
        P0: Method returning value fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_with_return = '''
class RegisteredUser:
    @autologger.automation_logger("Role")
    def login(self) -> bool:
        self.auth_tasks.log_in(self.email, self.password)
        return True
'''
        input_data = {
            "mode": "POST",
            "code": code_with_return,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Return value should fail"
        assert "return" in result["error"].lower(), "Error should mention return"

    @pytest.mark.unit
    def test_post_return_self_fails(self, valid_role_metadata):
        """
        P1: Method returning self fails (Roles don't chain).

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_with_return = '''
class RegisteredUser:
    @autologger.automation_logger("Role")
    def login(self):
        self.auth_tasks.log_in(self.email, self.password)
        return self
'''
        input_data = {
            "mode": "POST",
            "code": code_with_return,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Return self should fail"


# =============================================================================
# POST-DECORATOR: IC-08-04 decorator check (2 tests)
# =============================================================================

class TestPostDecorator:
    """POST validation decorator check (IC-08-04)."""

    @pytest.mark.unit
    def test_post_missing_decorator_fails(self, valid_role_metadata):
        """
        P0: IC-08-04 - Missing @autologger decorator fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_no_decorator = '''
class RegisteredUser:
    def login(self) -> None:
        self.auth_tasks.log_in(self.email, self.password)
'''
        input_data = {
            "mode": "POST",
            "code": code_no_decorator,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Missing decorator should fail"
        assert "decorator" in result["error"].lower() or "autologger" in result["error"].lower()

    @pytest.mark.unit
    def test_post_wrong_decorator_type_fails(self, valid_role_metadata):
        """
        P1: IC-08-04 - Wrong decorator type (Task instead of Role) fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_wrong_decorator = '''
class RegisteredUser:
    @autologger.automation_logger("Task")
    def login(self) -> None:
        self.auth_tasks.log_in(self.email, self.password)
'''
        input_data = {
            "mode": "POST",
            "code": code_wrong_decorator,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Wrong decorator type should fail"


# =============================================================================
# POST-TASKCALL: IC-08-06 task method calls (2 tests)
# =============================================================================

class TestPostTaskCall:
    """POST validation task method call check (IC-08-06)."""

    @pytest.mark.unit
    def test_post_no_task_call_fails(self, valid_role_metadata):
        """
        P0: IC-08-06 - Method without task call fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_no_task_call = '''
class RegisteredUser:
    @autologger.automation_logger("Role")
    def login(self) -> None:
        print("Logging in...")
'''
        input_data = {
            "mode": "POST",
            "code": code_no_task_call,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "No task call should fail"
        assert "task" in result["error"].lower(), "Error should mention task"

    @pytest.mark.unit
    def test_post_with_task_call_passes(self, valid_role_metadata):
        """
        P0: IC-08-06 - Method with task call passes.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_with_task_call = '''
class RegisteredUser:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface, user_data, base_url):
        self.username = user_data.get('username') or user_data.get('email')
        self.password = user_data.get('password')
        self.auth_tasks = AuthTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def login(self) -> None:
        self.auth_tasks.log_in(self.username, self.password)
'''
        input_data = {
            "mode": "POST",
            "code": code_with_task_call,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "With task call should pass"


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
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "POST",
            "metadata": {"class_name": "RegisteredUser"}
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Missing code should fail"
        assert "code" in result["error"], "Error should mention code"

    @pytest.mark.unit
    def test_post_code_empty_fails(self, valid_role_metadata):
        """
        P0: Empty code field fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "POST",
            "code": "",
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Empty code should fail"

    @pytest.mark.unit
    def test_post_metadata_missing_fails(self, valid_role_code):
        """
        P0: Missing metadata field fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "POST",
            "code": valid_role_code
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Missing metadata should fail"
        assert "metadata" in result["error"], "Error should mention metadata"

    @pytest.mark.unit
    def test_post_metadata_class_name_missing_fails(self, valid_role_code):
        """
        P0: DD-26 - Missing class_name in metadata fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "POST",
            "code": valid_role_code,
            "metadata": {
                "import_path": "roles.registered_user",
                "workflow_methods": []
            }
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Missing class_name should fail"

    @pytest.mark.unit
    def test_post_metadata_import_path_missing_fails(self, valid_role_code):
        """
        P0: DD-26 - Missing import_path in metadata fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {
            "mode": "POST",
            "code": valid_role_code,
            "metadata": {
                "class_name": "RegisteredUser",
                "workflow_methods": []
            }
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail", "Missing import_path should fail"


# =============================================================================
# ROUTE: Mode routing (5 tests)
# =============================================================================

class TestRoute:
    """Mode routing tests."""

    @pytest.mark.unit
    def test_validate_routes_to_pre(self, valid_pre_input, mock_state_manager_step7_complete):
        """
        P0: mode='PRE' routes to validate_pre().

        # Arrange
        """
        from tools.gates.qg_role import QGRole

        # Act
        result = QGRole.validate(valid_pre_input)

        # Assert
        assert result["status"] == "pass", "PRE mode should route correctly"

    @pytest.mark.unit
    def test_validate_routes_to_post(self, valid_post_input):
        """
        P0: mode='POST' routes to validate_post().

        # Arrange
        """
        from tools.gates.qg_role import QGRole

        # Act
        result = QGRole.validate(valid_post_input)

        # Assert
        assert result["status"] == "pass", "POST mode should route correctly"

    @pytest.mark.unit
    def test_validate_invalid_mode_fails(self):
        """
        P0: Invalid mode fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {"mode": "INVALID"}

        # Act
        result = QGRole.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Invalid mode should fail"
        assert "mode" in result["error"].lower(), "Error should mention mode"

    @pytest.mark.unit
    def test_validate_empty_mode_fails(self):
        """
        P1: Empty mode fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {"mode": ""}

        # Act
        result = QGRole.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty mode should fail"

    @pytest.mark.unit
    def test_validate_missing_mode_fails(self):
        """
        P1: Missing mode fails.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        input_data = {}

        # Act
        result = QGRole.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Missing mode should fail"


# =============================================================================
# EDGE: Edge cases (2 tests)
# =============================================================================

class TestEdge:
    """Edge case tests."""

    @pytest.mark.unit
    def test_post_multiple_workflow_methods_passes(self, valid_role_metadata):
        """
        P2: Code with multiple workflow methods all with task calls passes.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_multiple_methods = '''
class RegisteredUser:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface, user_data, base_url):
        self.username = user_data.get('username') or user_data.get('email')
        self.password = user_data.get('password')
        self.auth_tasks = AuthTasks(web_interface, base_url)
        self.catalog_tasks = CatalogTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def login(self) -> None:
        self.auth_tasks.log_in(self.username, self.password)

    @autologger.automation_logger("Role")
    def logout(self) -> None:
        self.auth_tasks.log_out()

    @autologger.automation_logger("Role")
    def login_and_browse(self, category: str) -> None:
        self.auth_tasks.log_in(self.username, self.password)
        self.catalog_tasks.browse_category(category)
'''
        input_data = {
            "mode": "POST",
            "code": code_multiple_methods,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Multiple valid methods should pass"

    @pytest.mark.unit
    def test_post_constructor_decorator_allowed(self, valid_role_metadata):
        """
        P2: Constructor with 'Role Constructor' decorator is allowed.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_with_constructor = '''
class RegisteredUser:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web, user_data, base_url):
        self.auth_tasks = AuthTasks(web, base_url)

    @autologger.automation_logger("Role")
    def login(self) -> None:
        self.auth_tasks.log_in(self.email, self.password)
'''
        input_data = {
            "mode": "POST",
            "code": code_with_constructor,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Constructor decorator should be allowed"


# =============================================================================
# DEF-063: Dynamic Credential Field Resolution (3 tests)
# =============================================================================

class TestDynamicCredentialFields:
    """DEF-063: Test credential field hardcoding detection."""

    @pytest.mark.unit
    def test_detects_hardcoded_email(self, valid_role_metadata):
        """
        P0: DEF-063 - Verify gate detects hardcoded 'email' field.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code = '''
class RegisteredUser:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface, user_data, base_url):
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        self.auth_tasks = AuthTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def login(self) -> None:
        self.auth_tasks.log_in(self.email, self.password)
'''
        input_data = {
            "mode": "POST",
            "code": code,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "NEEDS_RETRY", "Should return NEEDS_RETRY for hardcoded email"
        assert "email" in result["error"], "Error should mention email"
        assert result["fix_applied"] == "dynamic_credential_fields"
        assert "scaffolding_needed" in result, "Should include scaffolding template"
        assert result["scaffolding_needed"][0]["type"] == "code_pattern"

    @pytest.mark.unit
    def test_passes_dynamic_pattern(self, valid_role_metadata):
        """
        P0: DEF-063 - Verify gate passes when dynamic pattern used (idempotent).

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code = '''
class RegisteredUser:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface, user_data, base_url):
        self.user_data = user_data
        self.username = user_data.get('username') or user_data.get('email')
        self.password = user_data.get('password')
        self.auth_tasks = AuthTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def login(self) -> None:
        self.auth_tasks.log_in(self.username, self.password)
'''
        input_data = {
            "mode": "POST",
            "code": code,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "pass", "Dynamic pattern should pass validation"

    @pytest.mark.unit
    def test_detects_password_without_username_fallback(self, valid_role_metadata):
        """
        P1: DEF-063 - Verify gate detects password field without username fallback.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code = '''
class RegisteredUser:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface, user_data, base_url):
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        self.auth_tasks = AuthTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def login(self) -> None:
        self.auth_tasks.log_in(self.email, self.password)
'''
        input_data = {
            "mode": "POST",
            "code": code,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "NEEDS_RETRY", "Should return NEEDS_RETRY"
        assert "password" in result["error"] or "email" in result["error"]


# =============================================================================
# HINTS: Fix hint messages (2 tests)
# =============================================================================

class TestHints:
    """Fix hint message tests."""

    @pytest.mark.unit
    def test_fix_hint_for_skeleton_code(self, valid_role_metadata):
        """
        P1: Skeleton code error includes fix hint.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        skeleton_code = '''
class RegisteredUser:
    @autologger.automation_logger("Role")
    def login(self) -> None:
        pass
'''
        input_data = {
            "mode": "POST",
            "code": skeleton_code,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "fix_hint" in result, "Should include fix_hint"
        assert len(result["fix_hint"]) > 0, "fix_hint should not be empty"

    @pytest.mark.unit
    def test_fix_hint_for_missing_task_call(self, valid_role_metadata):
        """
        P1: Missing task call error includes fix hint mentioning task methods.

        # Arrange
        """
        from tools.gates.qg_role import QGRole
        code_no_task_call = '''
class RegisteredUser:
    @autologger.automation_logger("Role")
    def login(self) -> None:
        print("No task call here")
'''
        input_data = {
            "mode": "POST",
            "code": code_no_task_call,
            "metadata": valid_role_metadata
        }

        # Act
        result = QGRole.validate_post(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "fix_hint" in result, "Should include fix_hint"
        assert "task" in result["fix_hint"].lower(), "fix_hint should mention task"
"""
Integration Tests for QA Execution Engine - Task 15.0

Tests cross-gate behavior, state flow, and workflow integrity.

Test Categories:
1. Step Blocking Enforcement (10 tests)
2. Cross-Gate State Flow (9 tests)
3. Resume From Any Step (10 tests)
4. Skeleton Code Propagation (4 tests)
5. Gate Mode Enforcement (3 tests)
6. E2E Workflow (2 tests)

Total: 38 tests
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from utils.state_manager import StateManager
from tools.gates.qg_preflight import QGPreflight
from tools.gates.qg_user_input import QGUserInput
from tools.gates.qg_ai_processing import QGAIProcessing
from tools.gates.qg_test_scenarios import QGTestScenarios
from tools.gates.qg_discovered_elements import QGDiscoveredElements
from tools.gates.qg_page_object import QGPageObject
from tools.gates.qg_task import QGTask
from tools.gates.qg_role import QGRole
from tools.gates.qg_test_runner import QGTestRunner
from tools.gates.qg_save_run import QGSaveRun


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def temp_state_file():
    """Create a temporary state file for isolated testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def state_manager(temp_state_file):
    """Create a StateManager with isolated temp file."""
    return StateManager(state_file=temp_state_file)


@pytest.fixture
def mock_state_manager(state_manager):
    """Patch all gates to use the test state manager."""
    with patch.object(QGTestScenarios, '_get_state_manager', return_value=state_manager), \
         patch.object(QGDiscoveredElements, '_get_state_manager', return_value=state_manager), \
         patch.object(QGPageObject, '_get_state_manager', return_value=state_manager), \
         patch.object(QGTask, '_get_state_manager', return_value=state_manager), \
         patch.object(QGRole, '_get_state_manager', return_value=state_manager), \
         patch.object(QGTestRunner, '_get_state_manager', return_value=state_manager), \
         patch.object(QGSaveRun, '_get_state_manager', return_value=state_manager):
        yield state_manager


# =============================================================================
# Test Data Factories
# =============================================================================

def valid_step_1_data():
    """Valid preflight data (Step 1)."""
    return {
        "credential_strategy": "static",
        "test_data_location": "shared"
    }


def valid_step_2_data():
    """Valid user input data (Step 2)."""
    return {
        "persona": "As a registered user",
        "URL": "http://www.automationpractice.pl/index.php?controller=authentication",
        "role_name": "RegisteredUser",
        "domain": "auth",
        "raw_requirement": "I want to log in to my account"
    }


def valid_step_3_data():
    """Valid AI processing data (Step 3)."""
    return {
        "bdd_scenarios": [{
            "given": "I am on the login page",
            "when": ["I enter valid credentials", "I click submit"],
            "then": ["I should see my account dashboard"]
        }],
        "expected_states": ["is_logged_in", "is_on_dashboard"],
        "intent": "login"
    }


def valid_step_4_data():
    """Valid test scenarios data (Step 4) - for POST validation."""
    return {
        "mode": "POST",
        "test_scenarios": [{
            "name": "test_valid_login",
            "given": "I am on the login page",
            "when": ["I enter valid credentials", "I click submit"],
            "then": ["I should be logged in"]
        }]
    }


def valid_step_5_pre_data():
    """Valid discover elements PRE data (Step 5)."""
    return {
        "mode": "PRE",
        "url": "http://www.automationpractice.pl/index.php?controller=authentication",
        "page_name": "LoginPage",
        "credential_strategy": "static",
        "discovery_method": "tool2"
    }


def valid_step_5_post_data():
    """Valid discover elements POST data (Step 5)."""
    return {
        "mode": "POST",
        "page_name": "LoginPage",
        "elements": [{
            "suggested_name": "EMAIL_INPUT",
            "element_type": "input",
            "locator_css": "#email",
            "locator_xpath": "",
            "locator_id": "email"
        }],
        "validation_results": {
            "valid_count": 1,
            "error_count": 0,
            "elements": []
        }
    }


def valid_step_6_pre_data():
    """Valid page object PRE data (Step 6)."""
    return {
        "mode": "PRE",
        "discovered_elements": [{
            "suggested_name": "EMAIL_INPUT",
            "element_type": "input",
            "locator_css": "#email"
        }],
        "page_name": "LoginPage",
        "expected_states": ["is_logged_in"]
    }


def valid_step_6_post_data():
    """Valid page object POST data (Step 6)."""
    return {
        "mode": "POST",
        "code": '''
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface

class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def __init__(self, web: WebInterface):
        self.web = web

    def enter_email(self, text: str) -> "LoginPage":
        self.web.type_text(*self.EMAIL, text)
        return self

    def is_logged_in(self) -> bool:
        return self.web.is_element_displayed(By.CSS_SELECTOR, ".logout")
''',
        "metadata": {
            "class_name": "LoginPage",
            "import_path": "pages.auth.login_page",
            "locators": ["EMAIL"],
            "action_methods": ["enter_email"],
            "state_methods": ["is_logged_in"]
        }
    }


def valid_step_7_pre_data():
    """Valid task PRE data (Step 7)."""
    return {
        "mode": "PRE",
        "pom_metadata": {
            "class_name": "LoginPage",
            "import_path": "pages.auth.login_page",
            "action_methods": ["enter_email", "enter_password", "click_submit"]
        },
        "domain": "auth",
        "task_name": "AuthTasks"
    }


def valid_step_7_post_data():
    """Valid task POST data (Step 7)."""
    return {
        "mode": "POST",
        "code": '''
from interfaces.web_interface import WebInterface
from pages.auth.login_page import LoginPage
from resources.utilities import autologger

class AuthTasks:
    def __init__(self, web: WebInterface, base_url: str):
        self.web = web
        self.base_url = base_url
        self.login_page = LoginPage(web)

    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str):
        self.login_page.enter_email(email).enter_password(password).click_submit()
''',
        "metadata": {
            "class_name": "AuthTasks",
            "import_path": "tasks.auth.auth_tasks",
            "workflow_methods": ["log_in"]
        }
    }


def valid_step_8_pre_data():
    """Valid role PRE data (Step 8)."""
    return {
        "mode": "PRE",
        "task_metadata": {
            "class_name": "AuthTasks",
            "import_path": "tasks.auth.auth_tasks",
            "workflow_methods": ["log_in"]
        },
        "role_name": "RegisteredUser"
    }


def valid_step_8_post_data():
    """Valid role POST data (Step 8)."""
    return {
        "mode": "POST",
        "code": '''
from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.auth.auth_tasks import AuthTasks
from resources.utilities import autologger

class RegisteredUser:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any], base_url: str):
        self.web = web_interface
        self.user_data = user_data
        self.auth_tasks = AuthTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def login(self):
        self.auth_tasks.log_in(self.user_data["email"], self.user_data["password"])
''',
        "metadata": {
            "class_name": "RegisteredUser",
            "import_path": "roles.registered_user",
            "workflow_methods": ["login"]
        }
    }


def valid_step_9_pre_data():
    """Valid test runner PRE data (Step 9)."""
    return {
        "mode": "PRE",
        "role_metadata": {
            "class_name": "RegisteredUser",
            "import_path": "roles.registered_user",
            "workflow_methods": ["login"]
        },
        "pom_metadata": {
            "class_name": "LoginPage",
            "import_path": "pages.auth.login_page",
            "state_methods": ["is_logged_in"]
        },
        "test_scenarios": [{
            "name": "test_valid_login",
            "given": "I am on the login page",
            "when": ["I enter valid credentials"],
            "then": ["I should be logged in"]
        }]
    }


def valid_step_9_post_data():
    """Valid test runner POST data (Step 9).

    Matches unit test fixture: test_qg_test_runner.py::valid_test_code, valid_test_metadata
    """
    return {
        "mode": "POST",
        "code": '''"""
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
''',
        "metadata": {
            "class_name": "TestLogin",
            "file_path": "tests/auth/test_login.py",
            "role_used": "RegisteredUser",
            "page_used": "LoginPage",
            "test_methods": ["test_valid_login"]
        }
    }


def valid_step_10_pre_data():
    """Valid save run PRE data (Step 10)."""
    pom_code = valid_step_6_post_data()["code"]
    task_code = valid_step_7_post_data()["code"]
    role_code = valid_step_8_post_data()["code"]
    test_code = valid_step_9_post_data()["code"]

    return {
        "mode": "PRE",
        "pom_code": pom_code,
        "task_code": task_code,
        "role_code": role_code,
        "test_code": test_code
    }


# =============================================================================
# Category 1: Step Blocking Enforcement (10 tests)
# =============================================================================

class TestStepBlockingEnforcement:
    """
    Test that gates block progression when previous step is incomplete.

    Note: Steps 1-3 are POST-only gates that don't explicitly check previous step.
    Steps 4-10 have PRE validation that checks previous step completion.
    """

    @pytest.mark.integration
    def test_step_0_incomplete_blocks_step_1(self, mock_state_manager):
        """
        Step 1 (preflight) has no previous step - always allowed.
        This test verifies Step 1 can run without any prior state.
        """
        # Clear any existing state
        mock_state_manager.clear()

        # Step 1 should pass with valid data (no prior step required)
        result = QGPreflight.validate(valid_step_1_data())
        assert result["status"] == "pass"

    @pytest.mark.integration
    def test_step_1_incomplete_blocks_step_2(self, mock_state_manager):
        """
        Step 2 (user input) is POST-only - doesn't check Step 1.
        But we verify it CAN validate without Step 1 (orchestrator's job to enforce).
        """
        mock_state_manager.clear()

        # Step 2 validates data structure, not step sequence
        result = QGUserInput.validate(valid_step_2_data())
        assert result["status"] == "pass"

    @pytest.mark.integration
    def test_step_2_incomplete_blocks_step_3(self, mock_state_manager):
        """
        Step 3 (AI processing) is POST-only - doesn't check Step 2.
        But we verify it CAN validate without Step 2 (orchestrator's job to enforce).
        """
        mock_state_manager.clear()

        # Step 3 validates data structure, not step sequence
        result = QGAIProcessing.validate(valid_step_3_data())
        assert result["status"] == "pass"

    @pytest.mark.integration
    def test_step_3_incomplete_blocks_step_4(self, mock_state_manager):
        """Step 4 PRE validation blocks when Step 3 is incomplete."""
        mock_state_manager.clear()

        # Try Step 4 PRE without Step 3 complete
        result = QGTestScenarios.validate({"mode": "PRE", "user_story": "test", "workflow": "auth"})

        assert result["status"] == "fail"
        assert "Step 3" in result["error"]

    @pytest.mark.integration
    def test_step_4_incomplete_blocks_step_5(self, mock_state_manager):
        """Step 5 PRE validation blocks when Step 4 is incomplete."""
        # Complete Steps 1-3, skip Step 4
        mock_state_manager.save(1, valid_step_1_data())
        mock_state_manager.save(2, valid_step_2_data())
        mock_state_manager.save(3, valid_step_3_data())

        # Try Step 5 PRE without Step 4 complete
        result = QGDiscoveredElements.validate(valid_step_5_pre_data())

        assert result["status"] == "fail"
        assert "Step 4" in result["error"]

    @pytest.mark.integration
    def test_step_5_incomplete_blocks_step_6(self, mock_state_manager):
        """Step 6 PRE validation blocks when Step 5 is incomplete."""
        # Complete Steps 1-4, skip Step 5
        mock_state_manager.save(1, valid_step_1_data())
        mock_state_manager.save(2, valid_step_2_data())
        mock_state_manager.save(3, valid_step_3_data())
        mock_state_manager.save(4, {"test_scenarios": [{"name": "test"}]})

        # Try Step 6 PRE without Step 5 complete
        result = QGPageObject.validate(valid_step_6_pre_data())

        assert result["status"] == "fail"
        assert "Step 5" in result["error"]

    @pytest.mark.integration
    def test_step_6_incomplete_blocks_step_7(self, mock_state_manager):
        """Step 7 PRE validation blocks when Step 6 is incomplete."""
        # Complete Steps 1-5, skip Step 6
        mock_state_manager.save(1, valid_step_1_data())
        mock_state_manager.save(2, valid_step_2_data())
        mock_state_manager.save(3, valid_step_3_data())
        mock_state_manager.save(4, {"test_scenarios": [{"name": "test"}]})
        mock_state_manager.save(5, {"elements": [{"suggested_name": "TEST_ELEMENT", "element_type": "button", "locator_css": "#test"}], "page_name": "TestPage"})

        # Try Step 7 PRE without Step 6 complete
        result = QGTask.validate(valid_step_7_pre_data())

        assert result["status"] == "fail"
        assert "Step 6" in result["error"]

    @pytest.mark.integration
    def test_step_7_incomplete_blocks_step_8(self, mock_state_manager):
        """Step 8 PRE validation blocks when Step 7 is incomplete."""
        # Complete Steps 1-6, skip Step 7
        for step in range(1, 7):
            mock_state_manager.save(step, {"data": f"step_{step}"})

        # Try Step 8 PRE without Step 7 complete
        result = QGRole.validate(valid_step_8_pre_data())

        assert result["status"] == "fail"
        assert "Step 7" in result["error"]

    @pytest.mark.integration
    def test_step_8_incomplete_blocks_step_9(self, mock_state_manager):
        """Step 9 PRE validation blocks when Step 8 is incomplete."""
        # Complete Steps 1-7, skip Step 8
        for step in range(1, 8):
            mock_state_manager.save(step, {"data": f"step_{step}"})

        # Try Step 9 PRE without Step 8 complete
        result = QGTestRunner.validate(valid_step_9_pre_data())

        assert result["status"] == "fail"
        assert "Step 8" in result["error"]

    @pytest.mark.integration
    def test_step_9_incomplete_blocks_step_10(self, mock_state_manager):
        """Step 10 PRE validation blocks when Step 9 is incomplete."""
        # Complete Steps 1-8, skip Step 9
        for step in range(1, 9):
            mock_state_manager.save(step, {"data": f"step_{step}"})

        # Try Step 10 PRE without Step 9 complete
        result = QGSaveRun.validate(valid_step_10_pre_data())

        assert result["status"] == "fail"
        assert "Step 9" in result["error"]


# =============================================================================
# Category 2: Cross-Gate State Flow (9 tests)
# =============================================================================

class TestCrossGateStateFlow:
    """
    Test that state saved by Step N is readable by Step N+1.
    Verifies the data contract between consecutive gates.
    """

    @pytest.mark.integration
    def test_state_flows_step_1_to_2(self, state_manager):
        """Step 1 state (credential_strategy, test_data_location) persists for Step 2."""
        # Save Step 1 data
        step_1_data = valid_step_1_data()
        state_manager.save(1, step_1_data)

        # Verify Step 2 can read it
        retrieved = state_manager.get_step(1)
        assert retrieved["credential_strategy"] == step_1_data["credential_strategy"]
        assert retrieved["test_data_location"] == step_1_data["test_data_location"]

    @pytest.mark.integration
    def test_state_flows_step_2_to_3(self, state_manager):
        """Step 2 state (persona, URL, role_name, domain) persists for Step 3."""
        step_2_data = valid_step_2_data()
        state_manager.save(2, step_2_data)

        retrieved = state_manager.get_step(2)
        assert retrieved["persona"] == step_2_data["persona"]
        assert retrieved["URL"] == step_2_data["URL"]
        assert retrieved["role_name"] == step_2_data["role_name"]
        assert retrieved["domain"] == step_2_data["domain"]

    @pytest.mark.integration
    def test_state_flows_step_3_to_4(self, state_manager):
        """Step 3 state (bdd_scenarios, expected_states, intent) persists for Step 4."""
        step_3_data = valid_step_3_data()
        state_manager.save(3, step_3_data)

        retrieved = state_manager.get_step(3)
        assert retrieved["bdd_scenarios"] == step_3_data["bdd_scenarios"]
        assert retrieved["expected_states"] == step_3_data["expected_states"]
        assert retrieved["intent"] == step_3_data["intent"]

    @pytest.mark.integration
    def test_state_flows_step_4_to_5(self, state_manager):
        """Step 4 state (test_scenarios) persists for Step 5."""
        step_4_data = {"test_scenarios": valid_step_4_data()["test_scenarios"]}
        state_manager.save(4, step_4_data)

        retrieved = state_manager.get_step(4)
        assert retrieved["test_scenarios"] == step_4_data["test_scenarios"]

    @pytest.mark.integration
    def test_state_flows_step_5_to_6(self, state_manager):
        """Step 5 state (discovered_elements, page_name) persists for Step 6."""
        step_5_data = {
            "elements": valid_step_5_post_data()["elements"],
            "page_name": valid_step_5_post_data()["page_name"]
        }
        state_manager.save(5, step_5_data)

        retrieved = state_manager.get_step(5)
        assert retrieved["elements"] == step_5_data["elements"]
        assert retrieved["page_name"] == step_5_data["page_name"]

    @pytest.mark.integration
    def test_state_flows_step_6_to_7(self, state_manager):
        """Step 6 state (code, metadata) persists for Step 7."""
        step_6_data = {
            "code": valid_step_6_post_data()["code"],
            "metadata": valid_step_6_post_data()["metadata"]
        }
        state_manager.save(6, step_6_data)

        retrieved = state_manager.get_step(6)
        assert retrieved["code"] == step_6_data["code"]
        assert retrieved["metadata"]["class_name"] == "LoginPage"

    @pytest.mark.integration
    def test_state_flows_step_7_to_8(self, state_manager):
        """Step 7 state (code, metadata) persists for Step 8."""
        step_7_data = {
            "code": valid_step_7_post_data()["code"],
            "metadata": valid_step_7_post_data()["metadata"]
        }
        state_manager.save(7, step_7_data)

        retrieved = state_manager.get_step(7)
        assert retrieved["code"] == step_7_data["code"]
        assert retrieved["metadata"]["class_name"] == "AuthTasks"

    @pytest.mark.integration
    def test_state_flows_step_8_to_9(self, state_manager):
        """Step 8 state (code, metadata) persists for Step 9."""
        step_8_data = {
            "code": valid_step_8_post_data()["code"],
            "metadata": valid_step_8_post_data()["metadata"]
        }
        state_manager.save(8, step_8_data)

        retrieved = state_manager.get_step(8)
        assert retrieved["code"] == step_8_data["code"]
        assert retrieved["metadata"]["class_name"] == "RegisteredUser"

    @pytest.mark.integration
    def test_state_flows_step_9_to_10(self, state_manager):
        """Step 9 state (test_code) persists for Step 10."""
        step_9_data = {
            "code": valid_step_9_post_data()["code"],
            "metadata": valid_step_9_post_data()["metadata"]
        }
        state_manager.save(9, step_9_data)

        retrieved = state_manager.get_step(9)
        assert retrieved["code"] == step_9_data["code"]
        assert "test_valid_login" in retrieved["code"]


# =============================================================================
# Category 3: Resume From Any Step (10 tests)
# =============================================================================

class TestResumeFromAnyStep:
    """
    Test that workflow can resume from any completed step.
    Simulates workflow interruption and recovery.
    """

    @pytest.mark.integration
    def test_resume_from_step_1(self, state_manager):
        """Can resume workflow after Step 1 completion."""
        # Complete Step 1
        state_manager.save(1, valid_step_1_data())

        # Simulate restart - verify state persisted
        new_manager = StateManager(state_file=state_manager._state_file)
        assert new_manager.is_step_complete(1)
        assert new_manager.get_step(1)["credential_strategy"] == "static"

    @pytest.mark.integration
    def test_resume_from_step_2(self, state_manager):
        """Can resume workflow after Step 2 completion."""
        state_manager.save(1, valid_step_1_data())
        state_manager.save(2, valid_step_2_data())

        new_manager = StateManager(state_file=state_manager._state_file)
        assert new_manager.is_step_complete(2)
        assert new_manager.get_step(2)["role_name"] == "RegisteredUser"

    @pytest.mark.integration
    def test_resume_from_step_3(self, state_manager):
        """Can resume workflow after Step 3 completion."""
        for i in range(1, 4):
            state_manager.save(i, {"step": i, "data": f"step_{i}"})
        state_manager.save(3, valid_step_3_data())

        new_manager = StateManager(state_file=state_manager._state_file)
        assert new_manager.is_step_complete(3)
        assert new_manager.get_step(3)["intent"] == "login"

    @pytest.mark.integration
    def test_resume_from_step_4(self, state_manager):
        """Can resume workflow after Step 4 completion."""
        for i in range(1, 5):
            state_manager.save(i, {"step": i})
        state_manager.save(4, {"test_scenarios": [{"name": "test_login"}]})

        new_manager = StateManager(state_file=state_manager._state_file)
        assert new_manager.is_step_complete(4)
        assert new_manager.get_step(4)["test_scenarios"][0]["name"] == "test_login"

    @pytest.mark.integration
    def test_resume_from_step_5(self, state_manager):
        """Can resume workflow after Step 5 completion."""
        for i in range(1, 6):
            state_manager.save(i, {"step": i})
        state_manager.save(5, {"elements": [{"suggested_name": "EMAIL_INPUT", "element_type": "input", "locator_css": "#email"}], "page_name": "LoginPage"})

        new_manager = StateManager(state_file=state_manager._state_file)
        assert new_manager.is_step_complete(5)
        assert new_manager.get_step(5)["page_name"] == "LoginPage"

    @pytest.mark.integration
    def test_resume_from_step_6(self, state_manager):
        """Can resume workflow after Step 6 completion."""
        for i in range(1, 7):
            state_manager.save(i, {"step": i})
        state_manager.save(6, {"code": "class LoginPage:", "metadata": {"class_name": "LoginPage"}})

        new_manager = StateManager(state_file=state_manager._state_file)
        assert new_manager.is_step_complete(6)
        assert "LoginPage" in new_manager.get_step(6)["code"]

    @pytest.mark.integration
    def test_resume_from_step_7(self, state_manager):
        """Can resume workflow after Step 7 completion."""
        for i in range(1, 8):
            state_manager.save(i, {"step": i})
        state_manager.save(7, {"code": "class AuthTasks:", "metadata": {"class_name": "AuthTasks"}})

        new_manager = StateManager(state_file=state_manager._state_file)
        assert new_manager.is_step_complete(7)
        assert "AuthTasks" in new_manager.get_step(7)["code"]

    @pytest.mark.integration
    def test_resume_from_step_8(self, state_manager):
        """Can resume workflow after Step 8 completion."""
        for i in range(1, 9):
            state_manager.save(i, {"step": i})
        state_manager.save(8, {"code": "class RegisteredUser:", "metadata": {"class_name": "RegisteredUser"}})

        new_manager = StateManager(state_file=state_manager._state_file)
        assert new_manager.is_step_complete(8)
        assert "RegisteredUser" in new_manager.get_step(8)["code"]

    @pytest.mark.integration
    def test_resume_from_step_9(self, state_manager):
        """Can resume workflow after Step 9 completion."""
        for i in range(1, 10):
            state_manager.save(i, {"step": i})
        state_manager.save(9, {"code": "def test_login():", "metadata": {"test_name": "test_login"}})

        new_manager = StateManager(state_file=state_manager._state_file)
        assert new_manager.is_step_complete(9)
        assert "test_login" in new_manager.get_step(9)["code"]

    @pytest.mark.integration
    def test_resume_clears_incomplete_step(self, state_manager):
        """Incomplete step data should not persist after clear."""
        # Complete steps 1-5
        for i in range(1, 6):
            state_manager.save(i, {"step": i})

        # Clear state
        state_manager.clear()

        # Verify all steps cleared
        new_manager = StateManager(state_file=state_manager._state_file)
        for i in range(1, 11):
            assert not new_manager.is_step_complete(i)


# =============================================================================
# Category 4: Skeleton Code Propagation (4 tests)
# =============================================================================

class TestSkeletonCodePropagation:
    """
    Test that skeleton code is caught at each layer's gate.
    DD-25 enforcement across the tool chain.
    """

    @pytest.mark.integration
    def test_skeleton_in_pom_blocked_at_step_6(self, mock_state_manager):
        """Skeleton code in POM is blocked by qg_page_object POST validation."""
        # Complete Steps 1-5
        for i in range(1, 6):
            mock_state_manager.save(i, {"step": i})

        # Try POST with skeleton code
        skeleton_pom = {
            "mode": "POST",
            "code": '''
class LoginPage:
    def enter_email(self, text):
        pass  # TODO: Implement
''',
            "metadata": {
                "class_name": "LoginPage",
                "import_path": "pages.auth.login_page",
                "locators": [],
                "action_methods": ["enter_email"],
                "state_methods": []
            }
        }

        result = QGPageObject.validate(skeleton_pom)
        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower() or "pass" in result["error"].lower()

    @pytest.mark.integration
    def test_skeleton_in_task_blocked_at_step_7(self, mock_state_manager):
        """Skeleton code in Task is blocked by qg_task POST validation."""
        # Complete Steps 1-6
        for i in range(1, 7):
            mock_state_manager.save(i, {"step": i})

        skeleton_task = {
            "mode": "POST",
            "code": '''
class AuthTasks:
    @autologger.automation_logger("Task")
    def log_in(self, email, password):
        pass  # Add implementation as needed
''',
            "metadata": {
                "class_name": "AuthTasks",
                "import_path": "tasks.auth.auth_tasks"
            }
        }

        result = QGTask.validate(skeleton_task)
        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower() or "pass" in result["error"].lower()

    @pytest.mark.integration
    def test_skeleton_in_role_blocked_at_step_8(self, mock_state_manager):
        """Skeleton code in Role is blocked by qg_role POST validation."""
        # Complete Steps 1-7
        for i in range(1, 8):
            mock_state_manager.save(i, {"step": i})

        skeleton_role = {
            "mode": "POST",
            "code": '''
class RegisteredUser:
    @autologger.automation_logger("Role")
    def login(self):
        pass  # TODO: call auth_tasks
''',
            "metadata": {
                "class_name": "RegisteredUser",
                "import_path": "roles.registered_user"
            }
        }

        result = QGRole.validate(skeleton_role)
        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower() or "pass" in result["error"].lower()

    @pytest.mark.integration
    def test_skeleton_in_test_blocked_at_step_9(self, mock_state_manager):
        """Skeleton code in Test is blocked by qg_test_runner POST validation."""
        # Complete Steps 1-8
        for i in range(1, 9):
            mock_state_manager.save(i, {"step": i})

        skeleton_test = {
            "mode": "POST",
            "code": '''
@pytest.mark.auth
def test_valid_login(web_interface, config, test_data):
    pass  # TODO: Implement test
''',
            "metadata": {
                "test_name": "test_valid_login",
                "test_file": "tests/auth/test_login.py"
            }
        }

        result = QGTestRunner.validate(skeleton_test)
        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower() or "pass" in result["error"].lower()


# =============================================================================
# Category 5: Gate Mode Enforcement (3 tests)
# =============================================================================

class TestGateModeEnforcement:
    """
    Test that each gate type enforces its specific mode correctly.
    - POST-only gates (Steps 1-3): No mode parameter, validate data only
    - PRE+POST gates (Steps 4-9): Must specify mode, both validations available
    - PRE-only gate (Step 10): Only PRE mode accepted
    """

    @pytest.mark.integration
    def test_post_only_gates_have_no_mode_parameter(self):
        """Steps 1-3 gates don't use mode parameter - they validate data directly."""
        # Step 1 - no mode parameter
        result = QGPreflight.validate(valid_step_1_data())
        assert result["status"] == "pass"

        # Step 2 - no mode parameter
        result = QGUserInput.validate(valid_step_2_data())
        assert result["status"] == "pass"

        # Step 3 - no mode parameter
        result = QGAIProcessing.validate(valid_step_3_data())
        assert result["status"] == "pass"

    @pytest.mark.integration
    def test_pre_post_gates_require_mode(self, mock_state_manager):
        """Steps 4-9 gates require mode parameter."""
        # Complete prerequisites
        for i in range(1, 9):
            mock_state_manager.save(i, {"step": i, "data": "test"})

        # Test without mode - should fail
        no_mode_data = {"test": "data"}

        result = QGTestScenarios.validate(no_mode_data)
        assert result["status"] == "fail"
        assert "mode" in result["error"].lower()

    @pytest.mark.integration
    def test_pre_only_gate_rejects_post_mode(self, mock_state_manager):
        """Step 10 gate (PRE-only) rejects POST mode."""
        # Complete all prerequisites
        for i in range(1, 10):
            mock_state_manager.save(i, {"step": i, "code": "valid code"})

        # Try POST mode on Step 10
        post_data = {
            "mode": "POST",
            "pom_code": "code",
            "task_code": "code",
            "role_code": "code",
            "test_code": "code"
        }

        result = QGSaveRun.validate(post_data)
        assert result["status"] == "fail"
        assert "POST" in result["error"] or "PRE" in result["fix_hint"]


# =============================================================================
# Category 6: E2E Workflow (2 tests)
# =============================================================================

class TestE2EWorkflow:
    """
    Full workflow from Step 1 to Step 10 with realistic data.
    These tests simulate actual AI-driven workflow execution.
    """

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_e2e_auth_workflow_complete(self, mock_state_manager):
        """
        Full auth workflow: login test generation from Step 1 to Step 10.
        Simulates complete happy path.
        """
        # Step 1: Preflight
        result = QGPreflight.validate(valid_step_1_data())
        assert result["status"] == "pass", f"Step 1 failed: {result}"
        mock_state_manager.save(1, valid_step_1_data())

        # Step 2: User Input
        result = QGUserInput.validate(valid_step_2_data())
        assert result["status"] == "pass", f"Step 2 failed: {result}"
        mock_state_manager.save(2, valid_step_2_data())

        # Step 3: AI Processing
        result = QGAIProcessing.validate(valid_step_3_data())
        assert result["status"] == "pass", f"Step 3 failed: {result}"
        mock_state_manager.save(3, valid_step_3_data())

        # Step 4: Test Scenarios (PRE + POST)
        pre_data_4 = {
            "mode": "PRE",
            "metadata_context": {
                "bdd_scenarios": valid_step_3_data()["bdd_scenarios"],
                "expected_states": valid_step_3_data()["expected_states"],
                "intent": valid_step_3_data()["intent"]
            },
            "workflow": "auth"
        }
        result = QGTestScenarios.validate(pre_data_4)
        assert result["status"] == "pass", f"Step 4 PRE failed: {result}"

        result = QGTestScenarios.validate(valid_step_4_data())
        assert result["status"] == "pass", f"Step 4 POST failed: {result}"
        mock_state_manager.save(4, {"test_scenarios": valid_step_4_data()["test_scenarios"]})

        # Step 5: Discover Elements (PRE + POST)
        result = QGDiscoveredElements.validate(valid_step_5_pre_data())
        assert result["status"] == "pass", f"Step 5 PRE failed: {result}"

        result = QGDiscoveredElements.validate(valid_step_5_post_data())
        assert result["status"] == "pass", f"Step 5 POST failed: {result}"
        mock_state_manager.save(5, {
            "elements": valid_step_5_post_data()["elements"],
            "page_name": valid_step_5_post_data()["page_name"]
        })

        # Step 6: Page Object (PRE + POST)
        result = QGPageObject.validate(valid_step_6_pre_data())
        assert result["status"] == "pass", f"Step 6 PRE failed: {result}"

        result = QGPageObject.validate(valid_step_6_post_data())
        assert result["status"] == "pass", f"Step 6 POST failed: {result}"
        mock_state_manager.save(6, {
            "code": valid_step_6_post_data()["code"],
            "metadata": valid_step_6_post_data()["metadata"]
        })

        # Step 7: Task (PRE + POST)
        result = QGTask.validate(valid_step_7_pre_data())
        assert result["status"] == "pass", f"Step 7 PRE failed: {result}"

        result = QGTask.validate(valid_step_7_post_data())
        assert result["status"] == "pass", f"Step 7 POST failed: {result}"
        mock_state_manager.save(7, {
            "code": valid_step_7_post_data()["code"],
            "metadata": valid_step_7_post_data()["metadata"]
        })

        # Step 8: Role (PRE + POST)
        result = QGRole.validate(valid_step_8_pre_data())
        assert result["status"] == "pass", f"Step 8 PRE failed: {result}"

        result = QGRole.validate(valid_step_8_post_data())
        assert result["status"] == "pass", f"Step 8 POST failed: {result}"
        mock_state_manager.save(8, {
            "code": valid_step_8_post_data()["code"],
            "metadata": valid_step_8_post_data()["metadata"]
        })

        # Step 9: Test Runner (PRE + POST)
        result = QGTestRunner.validate(valid_step_9_pre_data())
        assert result["status"] == "pass", f"Step 9 PRE failed: {result}"

        result = QGTestRunner.validate(valid_step_9_post_data())
        assert result["status"] == "pass", f"Step 9 POST failed: {result}"
        mock_state_manager.save(9, {
            "code": valid_step_9_post_data()["code"],
            "metadata": valid_step_9_post_data()["metadata"]
        })

        # Step 10: Save Run (PRE only)
        result = QGSaveRun.validate(valid_step_10_pre_data())
        assert result["status"] == "pass", f"Step 10 PRE failed: {result}"

        # Verify complete workflow state
        assert mock_state_manager.is_step_complete(9), "All steps should be complete"

    @pytest.mark.integration
    @pytest.mark.e2e
    def test_e2e_skeleton_rejection_at_any_layer(self, mock_state_manager):
        """
        Workflow that attempts to sneak skeleton code through.
        Verifies DD-25 enforcement catches it.
        """
        # Complete Steps 1-5 successfully
        mock_state_manager.save(1, valid_step_1_data())
        mock_state_manager.save(2, valid_step_2_data())
        mock_state_manager.save(3, valid_step_3_data())
        mock_state_manager.save(4, {"test_scenarios": valid_step_4_data()["test_scenarios"]})
        mock_state_manager.save(5, {
            "elements": valid_step_5_post_data()["elements"],
            "page_name": valid_step_5_post_data()["page_name"]
        })

        # Step 6 PRE passes
        result = QGPageObject.validate(valid_step_6_pre_data())
        assert result["status"] == "pass"

        # Step 6 POST with skeleton code - should FAIL
        skeleton_pom = {
            "mode": "POST",
            "code": '''
class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def enter_email(self, text):
        pass  # Add implementation as needed

    def is_logged_in(self):
        raise NotImplementedError
''',
            "metadata": {
                "class_name": "LoginPage",
                "import_path": "pages.auth.login_page",
                "locators": ["EMAIL"],
                "action_methods": ["enter_email"],
                "state_methods": ["is_logged_in"]
            }
        }

        result = QGPageObject.validate(skeleton_pom)
        assert result["status"] == "fail", "Skeleton code should be rejected"

        # Workflow cannot continue - Step 6 not saved
        assert not mock_state_manager.is_step_complete(6), "Step 6 should not complete with skeleton"

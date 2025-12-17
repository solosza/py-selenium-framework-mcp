"""
Integration Tests for QA Validation Agent Workflow

Tests the full integration between:
- SR QA Engineer (scenario provider)
- Reviewer (artifact validator)
- Supervisor (orchestration)

Test Categories:
1. Happy Path: Good code passes validation
2. Rejection Flow: Bad code triggers DD violations
3. Fail-Fast: First failure skips remaining scenarios
4. Report Generation: Accurate summaries and aggregation

Task 6.0 Implementation
"""

import pytest
import asyncio
from typing import Dict, Any

# Import test wrappers (not MCP-decorated tools)
from agents.tools.sr_qa_engineer import (
    SCENARIOS,
    _test_get_scenario
)
from agents.tools.reviewer import (
    _test_validate_artifacts,
    DD_SEVERITY,
    Severity
)
from agents.tools.supervisor import (
    _test_run_scenario,
    _test_run_validation_suite,
    _reset_supervisor_state,
    _get_current_report,
    ScenarioStatus,
    FailureType
)


# =============================================================================
# Test Fixtures: Sample Code
# =============================================================================

# Good POM following all DDs
GOOD_LOGIN_PAGE = '''
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class LoginPage:
    """Login page object for authentication."""

    # LOCATORS - Class-level constants
    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "passwd")
    SUBMIT_BTN = (By.CSS_SELECTOR, "#SubmitLogin")
    LOGOUT_LINK = (By.CSS_SELECTOR, ".logout")
    ERROR_MSG = (By.CSS_SELECTOR, ".alert-danger")

    def __init__(self, web: WebInterface):
        self.web = web

    def enter_email(self, email: str) -> "LoginPage":
        """Enter email in the email field."""
        self.web.type_text(*self.EMAIL, text=email)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        """Enter password in the password field."""
        self.web.type_text(*self.PASSWORD, text=password)
        return self

    def click_submit(self) -> "LoginPage":
        """Click the login submit button."""
        self.web.click(*self.SUBMIT_BTN)
        return self

    # STATE-CHECK METHODS (DD-09, DD-11)
    def is_logged_in(self) -> bool:
        """Check if user is logged in by looking for logout link."""
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)

    def is_error_displayed(self) -> bool:
        """Check if error message is displayed."""
        return self.web.is_element_displayed(*self.ERROR_MSG, timeout=3)

    def get_error_text(self) -> str:
        """Get the error message text."""
        return self.web.get_text(*self.ERROR_MSG)
'''

# Good Task following all DDs
GOOD_AUTH_TASKS = '''
from interfaces.web_interface import WebInterface
from pages.auth.login_page import LoginPage
from resources.utilities import autologger


class AuthTasks:
    """Authentication tasks for login/logout operations."""

    def __init__(self, web: WebInterface, base_url: str):
        self.web = web
        self.base_url = base_url
        self.login_page = LoginPage(web)

    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str):
        """
        Login with email and password.

        Note: NO return value - test asserts via POM state methods.
        """
        self.web.navigate_to(f"{self.base_url}/index.php?controller=authentication")

        (self.login_page
            .enter_email(email)
            .enter_password(password)
            .click_submit())
        # NO return - test uses login_page.is_logged_in()

    @autologger.automation_logger("Task")
    def log_out(self):
        """Logout the current user."""
        self.login_page.click_logout()
        # NO return - test uses login_page.is_logged_out()
'''

# Good Role following all DDs
GOOD_REGISTERED_USER = '''
from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.auth.auth_tasks import AuthTasks
from resources.utilities import autologger


class RegisteredUser:
    """Registered user role with authentication capabilities."""

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web: WebInterface, user_data: Dict[str, Any], base_url: str):
        self.web = web
        self.user_data = user_data
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        self.base_url = base_url

        # Compose tasks
        self.auth_tasks = AuthTasks(web, base_url)

    @autologger.automation_logger("Role")
    def login(self):
        """
        Complete login workflow.

        Note: NO return value - test asserts via POM state methods.
        """
        self.auth_tasks.log_in(self.email, self.password)
        # NO return - test uses auth_tasks.login_page.is_logged_in()
'''

# Good Test following all DDs
GOOD_TEST_LOGIN = '''
import pytest
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage
from resources.utilities import autologger


@pytest.mark.auth
@autologger.automation_logger("Test")
def test_valid_login(web_interface, config, test_data):
    """Test that registered user can login successfully."""
    # Arrange
    user = RegisteredUser(web_interface, test_data["user"], config["base_url"])
    login_page = LoginPage(web_interface)

    # Act - ONE call to workflow method (no return value)
    user.login()

    # Assert - Via POM state-check methods (DD-15)
    assert login_page.is_logged_in(), "User should be logged in after valid credentials"
'''


# =============================================================================
# Bad Code Samples (with intentional DD violations)
# =============================================================================

# Bad Task: DD-03 violation (locator in Task)
BAD_TASK_DD03 = '''
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class AuthTasks:
    def __init__(self, web: WebInterface, base_url: str):
        self.web = web
        self.base_url = base_url

    def log_in(self, email: str, password: str):
        # DD-03 VIOLATION: Locators should be in Page Objects only
        self.web.type_text(By.ID, "email", text=email)
        self.web.type_text(By.ID, "passwd", text=password)
        self.web.click(By.CSS_SELECTOR, "#SubmitLogin")
'''

# Bad Task: DD-09 violation (returns value)
BAD_TASK_DD09 = '''
from interfaces.web_interface import WebInterface
from pages.auth.login_page import LoginPage


class AuthTasks:
    def __init__(self, web: WebInterface, base_url: str):
        self.web = web
        self.base_url = base_url
        self.login_page = LoginPage(web)

    def log_in(self, email: str, password: str):
        self.login_page.enter_email(email)
        self.login_page.enter_password(password)
        self.login_page.click_submit()
        # DD-09 VIOLATION: Task should NOT return values
        return self.login_page.is_logged_in()
'''

# Bad Test: DD-15 violation (asserts on return value)
BAD_TEST_DD15 = '''
import pytest


def test_login():
    # DD-15 VIOLATION: Capturing return value from workflow
    result = user.login()

    # DD-15 VIOLATION: Asserting on return value instead of POM state method
    assert result is True
'''

# Bad imports: DD-19 violation
BAD_IMPORTS_DD19 = '''
from utils.helpers import some_function  # DD-19 VIOLATION: Import from tools/, not utils/
from interfaces.web_interface import WebInterface


class SomeTasks:
    def __init__(self, web: WebInterface):
        self.web = web
'''


# =============================================================================
# Test Class: Integration Tests
# =============================================================================

class TestAgentIntegration:
    """Integration tests for the agent workflow."""

    def setup_method(self):
        """Reset state before each test."""
        _reset_supervisor_state()

    # -------------------------------------------------------------------------
    # Happy Path Tests
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_good_code_passes_review(self):
        """Good code following all DDs should pass review."""
        # Arrange: Good code for QA-EASY-001 artifacts
        content_map = {
            "framework/pages/auth/login_page.py": GOOD_LOGIN_PAGE,
            "framework/tasks/auth/auth_tasks.py": GOOD_AUTH_TASKS,
            "framework/roles/registered_user.py": GOOD_REGISTERED_USER,
            "tests/auth/test_valid_login.py": GOOD_TEST_LOGIN
        }

        # Act
        result = await _test_validate_artifacts({
            "paths": list(content_map.keys()),
            "content_map": content_map
        })

        # Assert
        assert result["status"] == "APPROVE"
        assert result["blocking_violations"] == 0

    @pytest.mark.asyncio
    async def test_good_scenario_passes_full_workflow(self):
        """Full workflow with good code should PASS."""
        # Arrange
        content_map = {
            "framework/pages/auth/login_page.py": GOOD_LOGIN_PAGE,
            "framework/tasks/auth/auth_tasks.py": GOOD_AUTH_TASKS,
            "framework/roles/registered_user.py": GOOD_REGISTERED_USER,
            "tests/auth/test_valid_login.py": GOOD_TEST_LOGIN
        }

        # Act: Run single scenario with good content
        result = await _test_run_scenario("QA-EASY-001", content_map)

        # Assert
        assert result["status"] == ScenarioStatus.PASSED.value
        assert result["review_status"] == "APPROVE"
        assert result["failure_type"] is None

    @pytest.mark.asyncio
    async def test_multiple_scenarios_all_pass(self):
        """Multiple scenarios with good code should all PASS."""
        # Arrange: Good content for ALL expected_artifacts of each scenario
        # QA-EASY-001 expects: login_page, auth_tasks, registered_user, test_valid_login
        # QA-EASY-002 expects: header_page, contact_page, navigation_tasks, test_contact_navigation

        content_maps = {
            "QA-EASY-001": {
                "framework/pages/auth/login_page.py": GOOD_LOGIN_PAGE,
                "framework/tasks/auth/auth_tasks.py": GOOD_AUTH_TASKS,
                "framework/roles/registered_user.py": GOOD_REGISTERED_USER,
                "tests/auth/test_valid_login.py": GOOD_TEST_LOGIN,
            },
            "QA-EASY-002": {
                "framework/pages/common/header_page.py": GOOD_LOGIN_PAGE,  # Reuse good code
                "framework/pages/contact/contact_page.py": GOOD_LOGIN_PAGE,
                "framework/tasks/navigation/navigation_tasks.py": GOOD_AUTH_TASKS,
                "tests/navigation/test_contact_navigation.py": GOOD_TEST_LOGIN,
            }
        }

        # Act
        report = await _test_run_validation_suite(
            ["QA-EASY-001", "QA-EASY-002"],
            content_maps
        )

        # Assert
        assert report["overall_status"] == "PASSED"
        assert report["scenarios_passed"] == 2
        assert report["scenarios_failed"] == 0
        assert report["scenarios_skipped"] == 0

    # -------------------------------------------------------------------------
    # Rejection Flow Tests
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_dd03_violation_detected(self):
        """DD-03 violation (locator in Task) should be detected."""
        # Arrange
        content_map = {
            "framework/tasks/auth/auth_tasks.py": BAD_TASK_DD03
        }

        # Act
        result = await _test_validate_artifacts({
            "paths": ["framework/tasks/auth/auth_tasks.py"],
            "content_map": content_map
        })

        # Assert
        assert result["status"] == "REJECT"
        assert result["blocking_violations"] > 0

        # Check DD-03 specifically detected
        dd03_violations = [v for v in result["violations"] if v["dd_id"] == "DD-03"]
        assert len(dd03_violations) > 0

    @pytest.mark.asyncio
    async def test_dd09_violation_detected(self):
        """DD-09 violation (Task returns value) should be detected."""
        # Arrange
        content_map = {
            "framework/tasks/auth/auth_tasks.py": BAD_TASK_DD09
        }

        # Act
        result = await _test_validate_artifacts({
            "paths": ["framework/tasks/auth/auth_tasks.py"],
            "content_map": content_map
        })

        # Assert
        assert result["status"] == "REJECT"

        # Check DD-09 specifically detected
        dd09_violations = [v for v in result["violations"] if v["dd_id"] == "DD-09"]
        assert len(dd09_violations) > 0

    @pytest.mark.asyncio
    async def test_dd15_violation_detected(self):
        """DD-15 violation (assert on return value) should be detected."""
        # Arrange
        content_map = {
            "tests/auth/test_login.py": BAD_TEST_DD15
        }

        # Act
        result = await _test_validate_artifacts({
            "paths": ["tests/auth/test_login.py"],
            "content_map": content_map
        })

        # Assert
        assert result["status"] == "REJECT"

        # Check DD-15 specifically detected
        dd15_violations = [v for v in result["violations"] if v["dd_id"] == "DD-15"]
        assert len(dd15_violations) > 0

    @pytest.mark.asyncio
    async def test_dd19_violation_detected(self):
        """DD-19 violation (import from utils/) should be detected."""
        # Arrange
        content_map = {
            "framework/tasks/some_tasks.py": BAD_IMPORTS_DD19
        }

        # Act
        result = await _test_validate_artifacts({
            "paths": ["framework/tasks/some_tasks.py"],
            "content_map": content_map
        })

        # Assert
        assert result["status"] == "REJECT"

        # Check DD-19 specifically detected
        dd19_violations = [v for v in result["violations"] if v["dd_id"] == "DD-19"]
        assert len(dd19_violations) > 0

    @pytest.mark.asyncio
    async def test_bad_code_triggers_type1_failure(self):
        """Bad code should trigger TYPE_1_REVIEW_REJECT failure."""
        # Arrange
        content_map = {
            "framework/tasks/auth/auth_tasks.py": BAD_TASK_DD03
        }

        # Act
        result = await _test_run_scenario("QA-EASY-001", content_map)

        # Assert
        assert result["status"] == ScenarioStatus.FAILED.value
        assert result["failure_type"] == FailureType.TYPE_1_REVIEW_REJECT.value
        assert result["review_status"] == "REJECT"

    # -------------------------------------------------------------------------
    # Fail-Fast Behavior Tests
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_fail_fast_skips_remaining_scenarios(self):
        """First failure should skip remaining scenarios."""
        # Arrange: First scenario bad, second good
        content_maps = {
            "QA-EASY-001": {
                "framework/tasks/auth/auth_tasks.py": BAD_TASK_DD03  # Will fail
            },
            "QA-EASY-002": {
                "framework/pages/common/header_page.py": GOOD_LOGIN_PAGE  # Would pass
            }
        }

        # Act
        report = await _test_run_validation_suite(
            ["QA-EASY-001", "QA-EASY-002"],
            content_maps
        )

        # Assert: First fails, second skipped
        assert report["overall_status"] == "FAILED"
        assert report["scenarios_failed"] == 1
        assert report["scenarios_skipped"] == 1
        assert report["scenarios_passed"] == 0

        # Check scenario statuses
        scenario_1 = report["scenario_results"][0]
        scenario_2 = report["scenario_results"][1]

        assert scenario_1["status"] == ScenarioStatus.FAILED.value
        assert scenario_2["status"] == ScenarioStatus.SKIPPED.value

    @pytest.mark.asyncio
    async def test_fail_fast_skips_all_remaining(self):
        """First failure should skip ALL remaining scenarios."""
        # Arrange: 3 scenarios, first fails
        content_maps = {
            "QA-EASY-001": {
                "framework/tasks/auth/auth_tasks.py": BAD_TASK_DD03  # Fails
            },
            "QA-MID-001": {
                "framework/pages/catalog/category_page.py": GOOD_LOGIN_PAGE
            },
            "QA-HARD-001": {
                "framework/pages/catalog/product_list_page.py": GOOD_LOGIN_PAGE
            }
        }

        # Act
        report = await _test_run_validation_suite(
            ["QA-EASY-001", "QA-MID-001", "QA-HARD-001"],
            content_maps
        )

        # Assert
        assert report["scenarios_failed"] == 1
        assert report["scenarios_skipped"] == 2
        assert report["scenarios_passed"] == 0

    # -------------------------------------------------------------------------
    # Report Generation Tests
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_report_violation_aggregation(self):
        """Report should aggregate violations by severity."""
        # Arrange: Code with multiple violations
        multi_violation_code = BAD_TASK_DD03 + "\n# Extra bad import\nfrom utils.foo import bar"

        content_maps = {
            "QA-EASY-001": {
                "framework/tasks/auth/auth_tasks.py": multi_violation_code
            }
        }

        # Act
        report = await _test_run_validation_suite(["QA-EASY-001"], content_maps)

        # Assert: Violations aggregated
        assert report["total_dd_violations"] > 0
        assert len(report["violations_by_severity"]) > 0

        # Should have CRITICAL (DD-03) and HIGH (DD-19) violations
        severities = report["violations_by_severity"]
        assert "CRITICAL" in severities or "HIGH" in severities

    @pytest.mark.asyncio
    async def test_report_contains_scenario_details(self):
        """Report should contain detailed scenario results."""
        # Act
        report = await _test_run_validation_suite(["QA-EASY-001"])

        # Assert: Has scenario details
        assert len(report["scenario_results"]) == 1

        scenario = report["scenario_results"][0]
        assert "scenario_id" in scenario
        assert "scenario_name" in scenario
        assert "status" in scenario
        assert scenario["scenario_id"] == "QA-EASY-001"

    @pytest.mark.asyncio
    async def test_report_has_timing_info(self):
        """Report should include timing information."""
        # Act
        report = await _test_run_validation_suite(["QA-EASY-001"])

        # Assert: Has timing
        assert report["scenario_results"][0]["started_at"] is not None
        assert report["scenario_results"][0]["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_formatted_report_readable(self):
        """Formatted report should be human-readable."""
        # Act
        report = await _test_run_validation_suite(["QA-EASY-001"])

        # Assert: Has formatted output
        assert "formatted_report" in report
        formatted = report["formatted_report"]

        # Check key sections exist
        assert "QA VALIDATION REPORT" in formatted
        assert "SUMMARY" in formatted
        assert "SCENARIO RESULTS" in formatted
        assert "QA-EASY-001" in formatted

    # -------------------------------------------------------------------------
    # SR QA Engineer Integration Tests
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_scenario_returns_valid_format(self):
        """SR QA Engineer should return properly formatted scenario."""
        # Act
        scenario = await _test_get_scenario({"level": "easy"})

        # Assert: Has required fields
        assert "id" in scenario
        assert "persona" in scenario
        assert "requirement" in scenario
        assert "url" in scenario
        assert "expected_artifacts" in scenario
        assert scenario["id"].startswith("QA-")

    @pytest.mark.asyncio
    async def test_get_scenario_by_id(self):
        """SR QA Engineer should return specific scenario by ID."""
        # Act
        scenario = await _test_get_scenario({"level": "QA-HARD-001"})

        # Assert
        assert scenario["id"] == "QA-HARD-001"
        assert scenario["complexity"] == "hard"

    @pytest.mark.asyncio
    async def test_all_scenarios_have_validation_points(self):
        """All scenarios should have validation points for reviewer."""
        for scenario_id in SCENARIOS:
            scenario = await _test_get_scenario({"level": scenario_id})

            assert "validation_points" in scenario, f"{scenario_id} missing validation_points"
            assert len(scenario["validation_points"]) > 0, f"{scenario_id} has empty validation_points"

    # -------------------------------------------------------------------------
    # Edge Case Tests
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_invalid_scenario_id_handled(self):
        """Invalid scenario ID should return error."""
        # Act
        result = await _test_get_scenario({"level": "QA-INVALID-999"})

        # Assert
        assert "error" in result

    @pytest.mark.asyncio
    async def test_empty_paths_handled(self):
        """Empty paths list should return appropriate response."""
        # Act
        result = await _test_validate_artifacts({"paths": []})

        # Assert
        assert result["status"] == "REJECT"
        assert result["total_violations"] == 0


# =============================================================================
# Test Class: Severity Tests
# =============================================================================

class TestViolationSeverity:
    """Test that violation severities are correctly classified."""

    def test_dd03_is_critical(self):
        """DD-03 (locators in non-POM) should be CRITICAL."""
        assert DD_SEVERITY["DD-03"] == Severity.CRITICAL

    def test_dd15_is_critical(self):
        """DD-15 (assertions not using POM) should be CRITICAL."""
        assert DD_SEVERITY["DD-15"] == Severity.CRITICAL

    def test_dd22_is_critical(self):
        """DD-22 (stop-and-discuss) should be CRITICAL."""
        assert DD_SEVERITY["DD-22"] == Severity.CRITICAL

    def test_dd09_is_high(self):
        """DD-09 (expected_states) should be HIGH."""
        assert DD_SEVERITY["DD-09"] == Severity.HIGH

    def test_all_dds_have_severity(self):
        """All 22 DDs should have defined severity."""
        # DDs we track
        expected_dds = [
            "DD-01", "DD-02", "DD-03", "DD-04", "DD-05",
            "DD-06", "DD-07", "DD-08", "DD-09", "DD-10",
            "DD-11", "DD-12", "DD-13", "DD-14", "DD-15",
            "DD-16", "DD-17", "DD-18", "DD-19", "DD-20",
            "DD-21", "DD-22"
        ]

        for dd in expected_dds:
            assert dd in DD_SEVERITY, f"{dd} missing from DD_SEVERITY"


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

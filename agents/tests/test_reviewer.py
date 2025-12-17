"""
Unit tests for QA Reviewer Agent Tool

Tests the artifact validation tool that checks generated code against
FRAMEWORK.md patterns and 22 Design Decisions.
"""

import pytest
from agents.tools.reviewer import (
    _test_validate_artifacts,
    validate_artifact,
    detect_file_type,
    DD_SEVERITY,
    Severity,
)


# =============================================================================
# Test Fixtures - Sample Code
# =============================================================================

@pytest.fixture
def good_pom_code():
    """Valid Page Object following all patterns."""
    return '''
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class LoginPage:
    """Page Object for Login page."""

    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "passwd")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "#SubmitLogin")
    LOGOUT_LINK = (By.CSS_SELECTOR, ".logout")

    def __init__(self, web: WebInterface):
        self.web = web

    def enter_email(self, email: str) -> "LoginPage":
        self.web.type_text(*self.EMAIL_INPUT, text=email)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        self.web.type_text(*self.PASSWORD_INPUT, text=password)
        return self

    def click_submit(self) -> "LoginPage":
        self.web.click(*self.SUBMIT_BUTTON)
        return self

    def is_logged_in(self) -> bool:
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)

    def has_error(self) -> bool:
        return self.web.is_element_displayed(*self.ERROR_MSG, timeout=3)

    def get_error_message(self) -> str:
        return self.web.get_text(*self.ERROR_MSG)
'''


@pytest.fixture
def good_task_code():
    """Valid Task following all patterns."""
    return '''
from interfaces.web_interface import WebInterface
from pages.auth.login_page import LoginPage
from resources.utilities import autologger


class AuthTasks:
    """Authentication task module."""

    def __init__(self, web: WebInterface, base_url: str):
        self.web = web
        self.base_url = base_url
        self.login_page = LoginPage(web)

    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str):
        """Log in user. NO return value."""
        self.web.navigate_to(f"{self.base_url}/login")
        (self.login_page
            .enter_email(email)
            .enter_password(password)
            .click_submit())
        # NO return - test asserts via POM
'''


@pytest.fixture
def good_test_code():
    """Valid Test following all patterns."""
    return '''
import pytest
from roles.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage
from resources.utilities import autologger


class TestLogin:
    """Login test suite."""

    @pytest.fixture(autouse=True)
    def setup(self, web_interface, config, test_data):
        self.web = web_interface
        self.login_page = LoginPage(web_interface)

    @autologger.automation_logger("Test")
    def test_valid_login(self):
        """Test valid login."""
        # Arrange
        user = RegisteredUser(self.web, test_data["user"], config["url"])

        # Act - ONE call, no return
        user.login()

        # Assert - Via POM state method
        assert self.login_page.is_logged_in(), "User should be logged in"
'''


@pytest.fixture
def bad_task_with_locator():
    """Task with DD-03 violation (locator in task layer)."""
    return '''
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class AuthTasks:
    def __init__(self, web: WebInterface):
        self.web = web

    def log_in(self, email: str, password: str):
        self.web.type_text(By.ID, "email", text=email)
        self.web.click(By.CSS_SELECTOR, "#submit")
'''


@pytest.fixture
def bad_task_with_return():
    """Task with DD-09 violation (returns value)."""
    return '''
from interfaces.web_interface import WebInterface
from pages.auth.login_page import LoginPage


class AuthTasks:
    def __init__(self, web: WebInterface):
        self.web = web
        self.login_page = LoginPage(web)

    def log_in(self, email: str, password: str):
        self.login_page.enter_email(email)
        self.login_page.click_submit()
        return True  # BAD: returning value
'''


@pytest.fixture
def bad_test_asserts_return():
    """Test with DD-15 violation (asserts on return value)."""
    return '''
import pytest


class TestLogin:
    def test_login(self):
        result = user.login()  # BAD: capturing return
        assert result is True  # BAD: asserting on return
'''


@pytest.fixture
def bad_pom_no_state_methods():
    """POM missing state-check methods (DD-09 related)."""
    return '''
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class LoginPage:
    EMAIL = (By.ID, "email")

    def __init__(self, web: WebInterface):
        self.web = web

    def enter_email(self, email: str) -> "LoginPage":
        self.web.type_text(*self.EMAIL, text=email)
        return self

    # Missing is_logged_in(), has_error(), etc.
'''


# =============================================================================
# Test: File Type Detection
# =============================================================================

class TestFileTypeDetection:
    """Test file type detection logic."""

    def test_detect_page_from_path(self):
        """Should detect page from path."""
        assert detect_file_type("framework/pages/auth/login_page.py", "") == "page"

    def test_detect_task_from_path(self):
        """Should detect task from path."""
        assert detect_file_type("framework/tasks/auth/auth_tasks.py", "") == "task"

    def test_detect_role_from_path(self):
        """Should detect role from path."""
        assert detect_file_type("framework/roles/registered_user.py", "") == "role"

    def test_detect_test_from_path(self):
        """Should detect test from path."""
        assert detect_file_type("tests/auth/test_login.py", "") == "test"

    def test_detect_test_from_filename(self):
        """Should detect test from test_ prefix."""
        assert detect_file_type("test_something.py", "") == "test"


# =============================================================================
# Test: DD-03 Locators Only in POM
# =============================================================================

class TestDD03LocatorsInPOM:
    """Test DD-03: Locators ONLY in Page Objects."""

    @pytest.mark.asyncio
    async def test_good_pom_passes(self, good_pom_code):
        """Good POM should pass DD-03."""
        result = await _test_validate_artifacts({
            "paths": ["framework/pages/auth/login_page.py"],
            "content_map": {"framework/pages/auth/login_page.py": good_pom_code}
        })

        dd03_violations = [v for v in result["violations"] if v["dd_id"] == "DD-03"]
        assert len(dd03_violations) == 0

    @pytest.mark.asyncio
    async def test_task_with_locator_fails(self, bad_task_with_locator):
        """Task with locator should fail DD-03."""
        result = await _test_validate_artifacts({
            "paths": ["framework/tasks/auth/auth_tasks.py"],
            "content_map": {"framework/tasks/auth/auth_tasks.py": bad_task_with_locator}
        })

        dd03_violations = [v for v in result["violations"] if v["dd_id"] == "DD-03"]
        assert len(dd03_violations) > 0
        assert all(v["severity"] == "CRITICAL" for v in dd03_violations)

    @pytest.mark.asyncio
    async def test_task_with_locator_blocks(self, bad_task_with_locator):
        """DD-03 violation should block (REJECT)."""
        result = await _test_validate_artifacts({
            "paths": ["framework/tasks/auth/auth_tasks.py"],
            "content_map": {"framework/tasks/auth/auth_tasks.py": bad_task_with_locator}
        })

        assert result["status"] == "REJECT"
        assert result["blocking_violations"] > 0


# =============================================================================
# Test: DD-09 No Return Values
# =============================================================================

class TestDD09NoReturnValues:
    """Test DD-09: Tasks/Roles should not return values."""

    @pytest.mark.asyncio
    async def test_good_task_passes(self, good_task_code):
        """Good task without return should pass."""
        result = await _test_validate_artifacts({
            "paths": ["framework/tasks/auth/auth_tasks.py"],
            "content_map": {"framework/tasks/auth/auth_tasks.py": good_task_code}
        })

        dd09_violations = [v for v in result["violations"] if v["dd_id"] == "DD-09"]
        assert len(dd09_violations) == 0

    @pytest.mark.asyncio
    async def test_task_with_return_fails(self, bad_task_with_return):
        """Task with return value should fail DD-09."""
        result = await _test_validate_artifacts({
            "paths": ["framework/tasks/auth/auth_tasks.py"],
            "content_map": {"framework/tasks/auth/auth_tasks.py": bad_task_with_return}
        })

        dd09_violations = [v for v in result["violations"] if v["dd_id"] == "DD-09"]
        assert len(dd09_violations) > 0


# =============================================================================
# Test: DD-15 Assertions Use POM
# =============================================================================

class TestDD15AssertionsUsePOM:
    """Test DD-15: Test assertions must use POM state methods."""

    @pytest.mark.asyncio
    async def test_good_test_passes(self, good_test_code):
        """Good test with POM assertions should pass."""
        result = await _test_validate_artifacts({
            "paths": ["tests/auth/test_login.py"],
            "content_map": {"tests/auth/test_login.py": good_test_code}
        })

        dd15_violations = [v for v in result["violations"] if v["dd_id"] == "DD-15"]
        assert len(dd15_violations) == 0

    @pytest.mark.asyncio
    async def test_test_asserts_return_fails(self, bad_test_asserts_return):
        """Test asserting on return value should fail DD-15."""
        result = await _test_validate_artifacts({
            "paths": ["tests/auth/test_login.py"],
            "content_map": {"tests/auth/test_login.py": bad_test_asserts_return}
        })

        dd15_violations = [v for v in result["violations"] if v["dd_id"] == "DD-15"]
        assert len(dd15_violations) > 0
        assert all(v["severity"] == "CRITICAL" for v in dd15_violations)


# =============================================================================
# Test: POM State Methods
# =============================================================================

class TestPOMStateMethods:
    """Test that POMs have required state-check methods."""

    @pytest.mark.asyncio
    async def test_pom_with_state_methods_passes(self, good_pom_code):
        """POM with state methods should pass."""
        result = await _test_validate_artifacts({
            "paths": ["framework/pages/auth/login_page.py"],
            "content_map": {"framework/pages/auth/login_page.py": good_pom_code}
        })

        # Should not have missing state methods violation
        state_violations = [v for v in result["violations"]
                          if "state-check" in v.get("description", "").lower()]
        assert len(state_violations) == 0

    @pytest.mark.asyncio
    async def test_pom_missing_state_methods_fails(self, bad_pom_no_state_methods):
        """POM without state methods should fail."""
        result = await _test_validate_artifacts({
            "paths": ["framework/pages/auth/login_page.py"],
            "content_map": {"framework/pages/auth/login_page.py": bad_pom_no_state_methods}
        })

        state_violations = [v for v in result["violations"]
                          if "state-check" in v.get("description", "").lower()]
        assert len(state_violations) > 0


# =============================================================================
# Test: Review Result Format
# =============================================================================

class TestReviewResultFormat:
    """Test that review results have correct format."""

    @pytest.mark.asyncio
    async def test_result_has_required_fields(self, good_pom_code):
        """Result should have all required fields."""
        result = await _test_validate_artifacts({
            "paths": ["framework/pages/auth/login_page.py"],
            "content_map": {"framework/pages/auth/login_page.py": good_pom_code}
        })

        required_fields = [
            "status",
            "violations",
            "summary",
            "files_reviewed",
            "blocking_violations",
            "total_violations"
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_approve_status_when_no_blocking(self, good_pom_code):
        """Should return APPROVE when no blocking violations."""
        result = await _test_validate_artifacts({
            "paths": ["framework/pages/auth/login_page.py"],
            "content_map": {"framework/pages/auth/login_page.py": good_pom_code}
        })

        assert result["status"] == "APPROVE"
        assert result["blocking_violations"] == 0

    @pytest.mark.asyncio
    async def test_reject_status_with_critical(self, bad_task_with_locator):
        """Should return REJECT when CRITICAL violations exist."""
        result = await _test_validate_artifacts({
            "paths": ["framework/tasks/auth/auth_tasks.py"],
            "content_map": {"framework/tasks/auth/auth_tasks.py": bad_task_with_locator}
        })

        assert result["status"] == "REJECT"
        assert result["blocking_violations"] > 0

    @pytest.mark.asyncio
    async def test_empty_paths_returns_reject(self):
        """Empty paths should return REJECT."""
        result = await _test_validate_artifacts({"paths": []})

        assert result["status"] == "REJECT"
        assert "No artifact paths" in result["summary"]


# =============================================================================
# Test: Violation Details
# =============================================================================

class TestViolationDetails:
    """Test violation detail format."""

    @pytest.mark.asyncio
    async def test_violation_has_required_fields(self, bad_task_with_locator):
        """Violations should have all required fields."""
        result = await _test_validate_artifacts({
            "paths": ["framework/tasks/auth/auth_tasks.py"],
            "content_map": {"framework/tasks/auth/auth_tasks.py": bad_task_with_locator}
        })

        assert len(result["violations"]) > 0

        violation = result["violations"][0]
        required_fields = ["dd_id", "severity", "file_path", "description"]

        for field in required_fields:
            assert field in violation, f"Violation missing field: {field}"

    @pytest.mark.asyncio
    async def test_violation_includes_line_number(self, bad_task_with_locator):
        """Violations should include line numbers when available."""
        result = await _test_validate_artifacts({
            "paths": ["framework/tasks/auth/auth_tasks.py"],
            "content_map": {"framework/tasks/auth/auth_tasks.py": bad_task_with_locator}
        })

        # At least one violation should have line number
        line_violations = [v for v in result["violations"] if v.get("line_number")]
        assert len(line_violations) > 0


# =============================================================================
# Test: DD Severity Mapping
# =============================================================================

class TestDDSeverityMapping:
    """Test that DD severities are correctly mapped."""

    def test_critical_dds(self):
        """CRITICAL DDs should be mapped correctly."""
        critical_dds = ["DD-03", "DD-15", "DD-22"]
        for dd in critical_dds:
            assert DD_SEVERITY[dd] == Severity.CRITICAL, f"{dd} should be CRITICAL"

    def test_high_dds(self):
        """HIGH DDs should be mapped correctly."""
        high_dds = ["DD-01", "DD-02", "DD-08", "DD-09", "DD-12", "DD-17", "DD-18", "DD-19"]
        for dd in high_dds:
            assert DD_SEVERITY[dd] == Severity.HIGH, f"{dd} should be HIGH"

    def test_all_22_dds_mapped(self):
        """All 22 DDs should be mapped."""
        assert len(DD_SEVERITY) == 22, f"Expected 22 DDs, got {len(DD_SEVERITY)}"


# =============================================================================
# Test: Multiple Files
# =============================================================================

class TestMultipleFiles:
    """Test validation of multiple files."""

    @pytest.mark.asyncio
    async def test_validate_multiple_good_files(self, good_pom_code, good_task_code, good_test_code):
        """Multiple good files should all pass."""
        result = await _test_validate_artifacts({
            "paths": [
                "framework/pages/auth/login_page.py",
                "framework/tasks/auth/auth_tasks.py",
                "tests/auth/test_login.py"
            ],
            "content_map": {
                "framework/pages/auth/login_page.py": good_pom_code,
                "framework/tasks/auth/auth_tasks.py": good_task_code,
                "tests/auth/test_login.py": good_test_code
            }
        })

        assert result["status"] == "APPROVE"
        assert len(result["files_reviewed"]) == 3

    @pytest.mark.asyncio
    async def test_one_bad_file_rejects_all(self, good_pom_code, bad_task_with_locator):
        """One bad file should cause overall REJECT."""
        result = await _test_validate_artifacts({
            "paths": [
                "framework/pages/auth/login_page.py",
                "framework/tasks/auth/auth_tasks.py"
            ],
            "content_map": {
                "framework/pages/auth/login_page.py": good_pom_code,
                "framework/tasks/auth/auth_tasks.py": bad_task_with_locator
            }
        })

        assert result["status"] == "REJECT"
        assert result["blocking_violations"] > 0

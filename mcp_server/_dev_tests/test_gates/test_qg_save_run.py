"""
Tests for qg_save_run (Step 10 Quality Gate).

PRE-only gate that validates all code is ready before save.

Test Categories:
- PRE-Happy: All code present, no skeleton, step 9 complete
- PRE-Negative: Missing code, skeleton in code, step 9 incomplete
- Route: PRE mode only (POST not supported)
- Edge: Fallback to state, minimal code
- Hints: Fix hints for each failure type

Enforces: DD-22, DD-25, IC-10-01 through IC-10-05
"""

import pytest
from unittest.mock import patch, MagicMock

from tools.gates.qg_save_run import QGSaveRun


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def valid_pom_code():
    """Valid POM code with no skeleton indicators."""
    return '''
class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")
    PASSWORD = (By.CSS_SELECTOR, "#passwd")

    def __init__(self, web):
        self.web = web

    def enter_email(self, text):
        self.web.type_text(*self.EMAIL, text)
        return self

    def is_logged_in(self):
        return self.web.is_element_displayed(*self.LOGOUT_LINK)
'''


@pytest.fixture
def valid_task_code():
    """Valid Task code with no skeleton indicators."""
    return '''
class AuthTasks:
    def __init__(self, web, base_url):
        self.web = web
        self.login_page = LoginPage(web)

    @autologger.automation_logger("Task")
    def log_in(self, email, password):
        self.login_page.enter_email(email).enter_password(password).click_submit()
'''


@pytest.fixture
def valid_role_code():
    """Valid Role code with no skeleton indicators."""
    return '''
class RegisteredUser:
    def __init__(self, web, user_data, base_url):
        self.auth_tasks = AuthTasks(web, base_url)

    @autologger.automation_logger("Role")
    def login_and_browse(self):
        self.auth_tasks.log_in(self.email, self.password)
'''


@pytest.fixture
def valid_test_code():
    """Valid Test code with no skeleton indicators."""
    return '''
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_valid_login(web_interface, config):
    user = RegisteredUser(web_interface, test_data, config["url"])
    user.login_and_browse()
    assert login_page.is_logged_in()
'''


@pytest.fixture
def valid_pre_input(valid_pom_code, valid_task_code, valid_role_code, valid_test_code):
    """Valid PRE input with all code blocks."""
    return {
        "mode": "PRE",
        "pom_code": valid_pom_code,
        "task_code": valid_task_code,
        "role_code": valid_role_code,
        "test_code": valid_test_code
    }


@pytest.fixture
def skeleton_pom_code():
    """POM code with skeleton indicator."""
    return '''
class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def enter_email(self, text):
        pass  # TODO: implement
'''


@pytest.fixture
def skeleton_task_code():
    """Task code with skeleton indicator."""
    return '''
class AuthTasks:
    def log_in(self, email, password):
        # Add login logic as needed
        pass
'''


@pytest.fixture
def skeleton_role_code():
    """Role code with skeleton indicator."""
    return '''
class RegisteredUser:
    def login_and_browse(self):
        raise NotImplementedError
'''


@pytest.fixture
def skeleton_test_code():
    """Test code with skeleton indicator."""
    return '''
def test_valid_login():
    # TODO: implement test
    pass
'''


@pytest.fixture
def mock_state_manager_step9_complete():
    """Mock StateManager with Step 9 complete."""
    with patch.object(QGSaveRun, '_get_state_manager') as mock:
        state_manager = MagicMock()
        state_manager.is_step_complete.return_value = True
        state_manager.get_step.return_value = None
        mock.return_value = state_manager
        yield mock


@pytest.fixture
def mock_state_manager_step9_incomplete():
    """Mock StateManager with Step 9 incomplete."""
    with patch.object(QGSaveRun, '_get_state_manager') as mock:
        state_manager = MagicMock()
        state_manager.is_step_complete.return_value = False
        mock.return_value = state_manager
        yield mock


@pytest.fixture
def mock_state_manager_with_code(valid_pom_code, valid_task_code, valid_role_code, valid_test_code):
    """Mock StateManager with code in state (for fallback testing)."""
    with patch.object(QGSaveRun, '_get_state_manager') as mock:
        state_manager = MagicMock()
        state_manager.is_step_complete.return_value = True

        def get_step_side_effect(step):
            if step == 6:
                return {"pom_code": valid_pom_code}
            elif step == 7:
                return {"task_code": valid_task_code}
            elif step == 8:
                return {"role_code": valid_role_code}
            elif step == 9:
                return {"test_code": valid_test_code}
            return None

        state_manager.get_step.side_effect = get_step_side_effect
        mock.return_value = state_manager
        yield mock


# =============================================================================
# PRE-Happy Tests
# =============================================================================

class TestPreHappy:
    """PRE validation happy path tests."""

    @pytest.mark.unit
    def test_pre_all_code_present_passes(self, valid_pre_input, mock_state_manager_step9_complete):
        """
        P0: All 4 code blocks present with no skeleton code passes.

        IC-10-03: Final skeleton sweep on ALL 4 layers.
        """
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "pass", "All valid code should pass"

    @pytest.mark.unit
    def test_pre_step_9_complete_checked(self, valid_pre_input, mock_state_manager_step9_complete):
        """
        P0: Step 9 completion is verified.

        Validates that is_step_complete(9) is called.
        """
        result = QGSaveRun.validate_pre(valid_pre_input)
        state_manager = mock_state_manager_step9_complete.return_value
        state_manager.is_step_complete.assert_called_with(9)
        assert result["status"] == "pass"

    @pytest.mark.unit
    def test_pre_pom_code_validated(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: POM code is validated for presence and skeleton."""
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "pass"

    @pytest.mark.unit
    def test_pre_task_code_validated(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Task code is validated for presence and skeleton."""
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "pass"

    @pytest.mark.unit
    def test_pre_role_code_validated(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Role code is validated for presence and skeleton."""
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "pass"

    @pytest.mark.unit
    def test_pre_test_code_validated(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Test code is validated for presence and skeleton."""
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "pass"

    @pytest.mark.unit
    def test_pre_fallback_to_state(self, mock_state_manager_with_code):
        """
        P0: When input_data missing code, fallback to state.

        IC-10-01: Primary input_data, fallback state.
        """
        input_data = {"mode": "PRE"}  # No code in input
        result = QGSaveRun.validate_pre(input_data)
        assert result["status"] == "pass", "Should fallback to state for code"


# =============================================================================
# PRE-Negative Tests
# =============================================================================

class TestPreNegative:
    """PRE validation negative tests."""

    @pytest.mark.unit
    def test_pre_step_9_incomplete_fails(self, valid_pre_input, mock_state_manager_step9_incomplete):
        """
        P0: Step 9 incomplete fails validation.

        Gate is blocked until Step 9 is complete.
        """
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "Step 9" in result["error"]

    @pytest.mark.unit
    def test_pre_missing_pom_code_fails(self, valid_pre_input, mock_state_manager_step9_complete):
        """
        P0: Missing pom_code fails validation.

        IC-10-05: Returns step hint for POM.
        """
        del valid_pre_input["pom_code"]
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "pom_code" in result["error"].lower() or "pom" in result["error"].lower()

    @pytest.mark.unit
    def test_pre_missing_task_code_fails(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Missing task_code fails validation."""
        del valid_pre_input["task_code"]
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "task_code" in result["error"].lower() or "task" in result["error"].lower()

    @pytest.mark.unit
    def test_pre_missing_role_code_fails(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Missing role_code fails validation."""
        del valid_pre_input["role_code"]
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "role_code" in result["error"].lower() or "role" in result["error"].lower()

    @pytest.mark.unit
    def test_pre_missing_test_code_fails(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Missing test_code fails validation."""
        del valid_pre_input["test_code"]
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "test_code" in result["error"].lower() or "test" in result["error"].lower()

    @pytest.mark.unit
    def test_pre_empty_pom_code_fails(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Empty pom_code fails validation."""
        valid_pre_input["pom_code"] = ""
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"

    @pytest.mark.unit
    def test_pre_empty_task_code_fails(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Empty task_code fails validation."""
        valid_pre_input["task_code"] = "   "
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"

    @pytest.mark.unit
    def test_pre_empty_role_code_fails(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Empty role_code fails validation."""
        valid_pre_input["role_code"] = ""
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"

    @pytest.mark.unit
    def test_pre_empty_test_code_fails(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Empty test_code fails validation."""
        valid_pre_input["test_code"] = "\n\n"
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"


# =============================================================================
# PRE-Skeleton Tests
# =============================================================================

class TestPreSkeleton:
    """PRE validation skeleton detection tests (DD-25)."""

    @pytest.mark.unit
    def test_pre_skeleton_in_pom_fails(self, valid_pre_input, skeleton_pom_code, mock_state_manager_step9_complete):
        """
        P0: Skeleton code in POM fails validation (DD-25).

        IC-10-03: Final skeleton sweep on ALL 4 layers.
        """
        valid_pre_input["pom_code"] = skeleton_pom_code
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower() or "DD-25" in result["error"]

    @pytest.mark.unit
    def test_pre_skeleton_in_task_fails(self, valid_pre_input, skeleton_task_code, mock_state_manager_step9_complete):
        """P0: Skeleton code in Task fails validation (DD-25)."""
        valid_pre_input["task_code"] = skeleton_task_code
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower() or "DD-25" in result["error"]

    @pytest.mark.unit
    def test_pre_skeleton_in_role_fails(self, valid_pre_input, skeleton_role_code, mock_state_manager_step9_complete):
        """P0: Skeleton code in Role fails validation (DD-25)."""
        valid_pre_input["role_code"] = skeleton_role_code
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower() or "DD-25" in result["error"]

    @pytest.mark.unit
    def test_pre_skeleton_in_test_fails(self, valid_pre_input, skeleton_test_code, mock_state_manager_step9_complete):
        """P0: Skeleton code in Test fails validation (DD-25)."""
        valid_pre_input["test_code"] = skeleton_test_code
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "skeleton" in result["error"].lower() or "DD-25" in result["error"]


# =============================================================================
# Route Tests
# =============================================================================

class TestRoute:
    """Mode routing tests."""

    @pytest.mark.unit
    def test_validate_routes_to_pre(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: validate() routes to validate_pre() for mode='PRE'."""
        result = QGSaveRun.validate(valid_pre_input)
        assert result["status"] == "pass"

    @pytest.mark.unit
    def test_validate_post_mode_not_supported(self, valid_pre_input, mock_state_manager_step9_complete):
        """
        P0: POST mode not supported (PRE-only gate).

        IC-10-02: PRE-only mode.
        """
        valid_pre_input["mode"] = "POST"
        result = QGSaveRun.validate(valid_pre_input)
        assert result["status"] == "fail"
        assert "PRE-only" in result["error"] or "not supported" in result["error"].lower()

    @pytest.mark.unit
    def test_validate_invalid_mode_fails(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Invalid mode fails validation."""
        valid_pre_input["mode"] = "INVALID"
        result = QGSaveRun.validate(valid_pre_input)
        assert result["status"] == "fail"
        assert "mode" in result["error"].lower()

    @pytest.mark.unit
    def test_validate_empty_mode_fails(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Empty mode fails validation."""
        valid_pre_input["mode"] = ""
        result = QGSaveRun.validate(valid_pre_input)
        assert result["status"] == "fail"

    @pytest.mark.unit
    def test_validate_missing_mode_fails(self, valid_pre_input, mock_state_manager_step9_complete):
        """P0: Missing mode fails validation."""
        del valid_pre_input["mode"]
        result = QGSaveRun.validate(valid_pre_input)
        assert result["status"] == "fail"


# =============================================================================
# Edge Tests
# =============================================================================

class TestEdge:
    """Edge case tests."""

    @pytest.mark.unit
    def test_pre_minimal_valid_code(self, mock_state_manager_step9_complete):
        """P1: Minimal valid code passes validation."""
        input_data = {
            "mode": "PRE",
            "pom_code": "class P:\n    def m(self): return self",
            "task_code": "class T:\n    def t(self): self.p.m()",
            "role_code": "class R:\n    def r(self): self.t.t()",
            "test_code": "def test_x(): assert True"
        }
        result = QGSaveRun.validate_pre(input_data)
        assert result["status"] == "pass"

    @pytest.mark.unit
    def test_pre_fallback_state_missing_code_fails(self, mock_state_manager_step9_complete):
        """
        P1: Fallback to state fails if state also missing code.

        IC-10-01: Both input_data and state checked.
        """
        # Mock state with no code
        mock_state_manager_step9_complete.return_value.get_step.return_value = None
        input_data = {"mode": "PRE"}  # No code in input
        result = QGSaveRun.validate_pre(input_data)
        assert result["status"] == "fail"

    @pytest.mark.unit
    def test_pre_code_from_input_takes_precedence(self, mock_state_manager_with_code, skeleton_pom_code):
        """
        P1: Code from input_data takes precedence over state.

        IC-10-01: Primary input_data.
        """
        # Input has skeleton POM, state has valid POM
        input_data = {
            "mode": "PRE",
            "pom_code": skeleton_pom_code,  # Skeleton - should fail
            "task_code": "class T: pass",  # Simple valid
            "role_code": "class R: pass",  # Will fail skeleton check
            "test_code": "def t(): pass"   # Will fail skeleton check
        }
        result = QGSaveRun.validate_pre(input_data)
        # Should fail because input has skeleton, even if state has valid
        assert result["status"] == "fail"

    @pytest.mark.unit
    def test_pre_whitespace_only_code_fails(self, mock_state_manager_step9_complete):
        """P1: Whitespace-only code is treated as empty."""
        input_data = {
            "mode": "PRE",
            "pom_code": "   \n\t\n   ",
            "task_code": "class T:\n    def t(self): self.p.m()",
            "role_code": "class R:\n    def r(self): self.t.t()",
            "test_code": "def test_x(): assert True"
        }
        result = QGSaveRun.validate_pre(input_data)
        assert result["status"] == "fail"


# =============================================================================
# Hint Tests
# =============================================================================

class TestHints:
    """Fix hint tests."""

    @pytest.mark.unit
    def test_fix_hint_for_missing_pom(self, valid_pre_input, mock_state_manager_step9_complete):
        """
        P1: Missing POM code returns Step 6 hint.

        IC-10-05: Actionable fix guidance.
        """
        del valid_pre_input["pom_code"]
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "fix_hint" in result
        assert "Step 6" in result["fix_hint"] or "POM" in result["fix_hint"]

    @pytest.mark.unit
    def test_fix_hint_for_missing_task(self, valid_pre_input, mock_state_manager_step9_complete):
        """P1: Missing Task code returns Step 7 hint."""
        del valid_pre_input["task_code"]
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "fix_hint" in result
        assert "Step 7" in result["fix_hint"] or "Task" in result["fix_hint"]

    @pytest.mark.unit
    def test_fix_hint_for_missing_role(self, valid_pre_input, mock_state_manager_step9_complete):
        """P1: Missing Role code returns Step 8 hint."""
        del valid_pre_input["role_code"]
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "fix_hint" in result
        assert "Step 8" in result["fix_hint"] or "Role" in result["fix_hint"]

    @pytest.mark.unit
    def test_fix_hint_for_missing_test(self, valid_pre_input, mock_state_manager_step9_complete):
        """P1: Missing Test code returns Step 9 hint."""
        del valid_pre_input["test_code"]
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "fix_hint" in result
        assert "Step 9" in result["fix_hint"] or "Test" in result["fix_hint"]

    @pytest.mark.unit
    def test_fix_hint_for_skeleton_code(self, valid_pre_input, skeleton_pom_code, mock_state_manager_step9_complete):
        """P1: Skeleton code returns DD-25 fix hint."""
        valid_pre_input["pom_code"] = skeleton_pom_code
        result = QGSaveRun.validate_pre(valid_pre_input)
        assert result["status"] == "fail"
        assert "fix_hint" in result
        # Hint should mention completing the code or DD-25
        assert "complete" in result["fix_hint"].lower() or "skeleton" in result["fix_hint"].lower()

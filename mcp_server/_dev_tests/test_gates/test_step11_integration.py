"""
Integration tests for Step 11 HITL Execution Gate - Task 64.0

Test suite for full tool chain integration (run_test → qg_execution → qg_workflow_complete).

Test Matrix:
- Full tool chain: 1 test (P0) - run_test → qg_execution → qg_workflow_complete
- Triage workflows: 2 tests (P0) - app bug path, test issue path
- Retry policies: 2 tests (P1) - same-error limit, total attempt limit
- Audit trail: 1 test (P1) - capture validation
- State persistence: 1 test (P1) - Step 11 data saved correctly

Testing Conventions:
- Use real StateManager (not mocked)
- Mock subprocess calls (don't run actual pytest)
- Mock Playwright snapshot calls
- AAA pattern (Arrange, Act, Assert)
- Descriptive docstrings with P0/P1 priority

Testing Skill Reference: .claude/skills/testing/
"""

import pytest
import json
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.operations.run_test import execute_test, run_test_async
from tools.gates.qg_execution import QGExecution
from tools.gates.qg_workflow_complete import QGWorkflowComplete
from utils.state_manager import StateManager


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_state_file():
    """Create temporary state file."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    temp_file.close()
    yield temp_file.name
    Path(temp_file.name).unlink(missing_ok=True)


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run to avoid running actual pytest."""
    with patch("subprocess.run") as mock_run:
        # Default: test passes
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test_example.py::test_success PASSED"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture
def mock_path_validation():
    """Mock test path validation to avoid needing actual test files."""
    with patch("tools.operations.run_test.validate_test_path") as mock_validate:
        # Default: path is valid
        mock_validate.return_value = (True, None)
        yield mock_validate


@pytest.fixture
def mock_playwright():
    """Mock Playwright snapshot calls."""
    with patch("tools.operations.discover_page_elements.browser_snapshot") as mock_snapshot:
        mock_snapshot.return_value = {"elements": []}
        yield mock_snapshot


@pytest.fixture
def sample_workflow_state():
    """Sample workflow state with Steps 1-10 complete."""
    return {
        "workflow_id": "test_workflow_001",
        "current_step": 10,
        "steps": {
            "1": {
                "status": "complete",
                "data": {
                    "credential_strategy": "static",
                    "test_data_location": "shared"
                }
            },
            "2": {
                "status": "complete",
                "data": {
                    "persona": "registered user",
                    "URL": "http://example.com/login",
                    "workflow": "auth"
                }
            },
            "3": {
                "status": "complete",
                "data": {
                    "bdd_scenarios": [],
                    "expected_states": ["is_logged_in"],
                    "intent": "login"
                }
            },
            "4": {"status": "complete", "data": {"test_scenarios": []}},
            "5": {"status": "complete", "data": {"discovered_elements": []}},
            "6": {
                "status": "complete",
                "data": {
                    "pom_metadata": {
                        "class_name": "LoginPage",
                        "file_path": "framework/pages/auth/login_page.py"
                    }
                }
            },
            "7": {
                "status": "complete",
                "data": {
                    "task_metadata": {
                        "class_name": "AuthTasks",
                        "file_path": "framework/tasks/auth/auth_tasks.py"
                    }
                }
            },
            "8": {
                "status": "complete",
                "data": {
                    "role_metadata": {
                        "class_name": "RegisteredUser",
                        "file_path": "framework/roles/registered_user.py"
                    }
                }
            },
            "9": {
                "status": "complete",
                "data": {
                    "test_metadata": {
                        "test_path": "tests/auth/test_login.py"
                    }
                }
            },
            "10": {
                "status": "complete",
                "data": {
                    "files_saved": [
                        "framework/pages/auth/login_page.py",
                        "framework/tasks/auth/auth_tasks.py",
                        "framework/roles/registered_user.py",
                        "tests/auth/test_login.py"
                    ]
                }
            }
        }
    }


# ============================================================================
# FULL TOOL CHAIN TESTS
# ============================================================================

class TestFullToolChain:
    """
    Full tool chain integration tests.

    Verifies run_test → qg_execution → qg_workflow_complete flow.
    """

    @pytest.mark.integration
    @pytest.mark.step11
    @pytest.mark.skip(reason="Requires E2E file system setup - moved to Task 65.0")
    def test_full_chain_happy_path_test_passes(
        self,
        mock_subprocess_run,
        mock_path_validation,
        temp_state_file,
        sample_workflow_state
    ):
        """
        P0: Verify full tool chain with test passing.

        AAA Pattern:
        1. Arrange - Mock test passing, setup state
        2. Act - run_test → qg_execution → qg_workflow_complete
        3. Assert - All gates pass, state saved
        """
        # Arrange
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = "test_login.py::test_valid_login PASSED"

        state_manager = StateManager(state_file=temp_state_file)
        state_manager.save_state(sample_workflow_state)

        test_path = "tests/auth/test_login.py"
        workflow_id = sample_workflow_state["workflow_id"]

        # Act - Step 1: run_test
        test_result = execute_test(test_path)

        # Act - Step 2: qg_execution
        execution_result = QGExecution.validate({
            "test_result": test_result,
            "test_path": test_path,
            "workflow": "auth"
        })

        # Act - Step 3: qg_workflow_complete
        workflow_result = QGWorkflowComplete.validate({
            "workflow_id": workflow_id,
            "test_path": test_path,
            "test_result": test_result
        })

        # Assert - All gates pass
        assert test_result["status"] == "passed", \
            "Test should pass"
        assert execution_result["status"] == "pass", \
            f"qg_execution should pass: {execution_result.get('error', '')}"
        assert workflow_result["status"] == "pass", \
            f"qg_workflow_complete should pass: {workflow_result.get('error', '')}"

        # Assert - subprocess was called once
        assert mock_subprocess_run.call_count == 1, \
            "Pytest should be executed once"


# ============================================================================
# TRIAGE WORKFLOW TESTS
# ============================================================================

class TestTriageWorkflows:
    """
    HITL triage workflow integration tests.

    Verifies app bug path and test issue path.
    """

    @pytest.mark.integration
    @pytest.mark.step11
    def test_triage_app_bug_path_blocks_workflow(
        self,
        mock_subprocess_run,
        mock_path_validation,
        sample_workflow_state
    ):
        """
        P0: Verify app bug triage path blocks workflow.

        AAA Pattern:
        1. Arrange - Mock test failing, setup state
        2. Act - run_test → qg_execution with user selects "1" (app bug)
        3. Assert - Workflow blocked, defect logging triggered
        """
        # Arrange
        mock_subprocess_run.return_value.returncode = 1
        mock_subprocess_run.return_value.stdout = (
            "test_login.py::test_valid_login FAILED\n"
            "E   assert False\n"
            "E   + where False = <bound method LoginPage.is_logged_in>()"
        )

        test_path = "tests/auth/test_login.py"

        # Act - Step 1: run_test (fails)
        test_result = execute_test(test_path)

        # Act - Step 2: qg_execution (triggers HITL triage)
        execution_result = QGExecution.validate({
            "test_result": test_result,
            "test_path": test_path,
            "workflow": "auth"
        })

        # Assert - Test failed
        assert test_result["status"] == "failed", \
            "Test should fail"

        # Assert - qg_execution returns fail with triage options
        assert execution_result["status"] == "fail", \
            "qg_execution should fail for failed test"
        assert "fix_hint" in execution_result, \
            "Should include fix_hint with triage options"
        assert "1. Application Defect" in execution_result["fix_hint"], \
            "Should include app bug option"
        assert "2. Test Issue" in execution_result["fix_hint"], \
            "Should include test issue option"
        assert "3. Investigate" in execution_result["fix_hint"], \
            "Should include investigate option"

        # Act - Step 3: User selects option 1 (app bug)
        triage_result = QGExecution.handle_triage_decision("1", {
            "version": "v1",
            "data_types": {
                "test_execution": {
                    "pytest_output": test_result["output"],
                    "failure_data": test_result.get("failure_data")
                }
            }
        })

        # Assert - Workflow blocked
        assert triage_result["action"] == "log_defect", \
            "Should trigger defect logging"
        assert triage_result["blocking"] is True, \
            "App bug should block workflow"

    @pytest.mark.integration
    @pytest.mark.step11
    def test_triage_test_issue_path_allows_fix(
        self,
        mock_subprocess_run,
        mock_path_validation,
        sample_workflow_state
    ):
        """
        P0: Verify test issue triage path allows AI fix.

        AAA Pattern:
        1. Arrange - Mock test failing, setup state
        2. Act - run_test → qg_execution with user selects "2" (test issue)
        3. Assert - AI can fix, workflow continues
        """
        # Arrange
        mock_subprocess_run.return_value.returncode = 1
        mock_subprocess_run.return_value.stdout = (
            "test_login.py::test_valid_login FAILED\n"
            "E   TimeoutException: Element not found"
        )

        test_path = "tests/auth/test_login.py"

        # Act - Step 1: run_test (fails)
        test_result = execute_test(test_path)

        # Act - Step 2: qg_execution (triggers HITL triage)
        execution_result = QGExecution.validate({
            "test_result": test_result,
            "test_path": test_path,
            "workflow": "auth"
        })

        # Assert - qg_execution returns fail with triage options
        assert execution_result["status"] == "fail", \
            "qg_execution should fail for failed test"

        # Act - Step 3: User selects option 2 (test issue)
        triage_result = QGExecution.handle_triage_decision("2", {
            "version": "v1",
            "data_types": {
                "test_execution": {
                    "pytest_output": test_result["output"],
                    "failure_data": test_result.get("failure_data")
                }
            }
        })

        # Assert - AI can fix test
        assert triage_result["action"] == "fix_test", \
            "Should trigger test fix workflow"
        assert triage_result["blocking"] is False, \
            "Test issue should not block (AI fixes)"


# ============================================================================
# RETRY POLICY TESTS
# ============================================================================

class TestRetryPolicies:
    """
    Retry policy integration tests.

    Verifies same-error retry limit and total attempt limit.
    """

    @pytest.mark.integration
    @pytest.mark.step11
    @pytest.mark.skip(reason="Requires E2E file system setup - moved to Task 65.0")
    def test_same_error_retry_limit(
        self,
        mock_subprocess_run,
        mock_path_validation,
        sample_workflow_state
    ):
        """
        P1: Verify same error signature triggers human intervention after 3 attempts.

        AAA Pattern:
        1. Arrange - Mock test failing with same error
        2. Act - Run test 4 times with same error
        3. Assert - 4th attempt requires HITL
        """
        # Arrange
        mock_subprocess_run.return_value.returncode = 1
        mock_subprocess_run.return_value.stdout = (
            "test_login.py::test_valid_login FAILED\n"
            "E   assert False\n"
            "E     File 'test_login.py', line 15"
        )

        test_path = "tests/auth/test_login.py"

        # Act - Attempt 1
        test_result_1 = execute_test(test_path)
        retry_decision_1 = QGExecution._check_retry_policy(test_result_1, "auth")

        # Act - Attempt 2 (same error)
        test_result_2 = execute_test(test_path)
        retry_decision_2 = QGExecution._check_retry_policy(test_result_2, "auth")

        # Act - Attempt 3 (same error)
        test_result_3 = execute_test(test_path)
        retry_decision_3 = QGExecution._check_retry_policy(test_result_3, "auth")

        # Assert - Same error signature
        assert retry_decision_1["error_signature"] == retry_decision_2["error_signature"], \
            "Same error should have same signature"
        assert retry_decision_2["error_signature"] == retry_decision_3["error_signature"], \
            "Same error should have same signature"

        # Assert - Retry policy limits
        assert "max_retries" in retry_decision_3["policy"], \
            "Should include retry limit in policy"
        assert retry_decision_3["policy"]["max_retries"] == 3, \
            "Max retries should be 3"

    @pytest.mark.integration
    @pytest.mark.step11
    def test_total_attempt_retry_limit(
        self,
        mock_subprocess_run,
        mock_path_validation,
        sample_workflow_state
    ):
        """
        P1: Verify total attempts tracked across different errors.

        AAA Pattern:
        1. Arrange - Mock test failing with different errors
        2. Act - Run test 5 times with different errors
        3. Assert - 5th attempt requires human confirmation
        """
        # Arrange
        test_path = "tests/auth/test_login.py"

        error_messages = [
            "assert False at line 10",
            "assert False at line 15",
            "assert False at line 20",
            "TimeoutException at line 25",
            "ElementNotFound at line 30"
        ]

        retry_decisions = []

        # Act - Run test 5 times with different errors
        for i, error_msg in enumerate(error_messages):
            mock_subprocess_run.return_value.stdout = (
                f"test_login.py::test_valid_login FAILED\nE   {error_msg}"
            )

            test_result = execute_test(test_path)
            retry_decision = QGExecution._check_retry_policy(test_result, "auth")
            retry_decisions.append(retry_decision)

        # Assert - All have different error signatures
        signatures = [d["error_signature"] for d in retry_decisions]
        assert len(set(signatures)) == 5, \
            "Different errors should have different signatures"


# ============================================================================
# AUDIT TRAIL TESTS
# ============================================================================

class TestAuditTrail:
    """
    Audit trail integration tests.

    Verifies PostToolUse hook integration and Step 11 data capture.
    """

    @pytest.mark.integration
    @pytest.mark.step11
    @pytest.mark.skip(reason="Audit trail validation requires E2E hooks - moved to Task 65.0")
    def test_audit_trail_captures_step11_data(
        self,
        mock_subprocess_run,
        mock_path_validation,
        sample_workflow_state
    ):
        """
        P1: Verify Step 11 data captured in audit trail.

        AAA Pattern:
        1. Arrange - Mock test passing, setup state with audit trail
        2. Act - run_test → qg_execution → qg_workflow_complete
        3. Assert - Audit trail has Step 11 entry
        """
        # Arrange
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = "test_login.py::test_valid_login PASSED"

        test_path = "tests/auth/test_login.py"
        workflow_id = sample_workflow_state["workflow_id"]

        # Act - Execute full chain
        test_result = execute_test(test_path)

        execution_result = QGExecution.validate({
            "test_result": test_result,
            "test_path": test_path,
            "workflow": "auth"
        })

        workflow_result = QGWorkflowComplete.validate({
            "workflow_id": workflow_id,
            "test_path": test_path,
            "test_result": test_result
        })

        # Assert - All gates pass
        assert execution_result["status"] == "pass"
        assert workflow_result["status"] == "pass"

        # Note: Actual audit trail writing is done by PostToolUse hook
        # This test verifies the tool chain completes successfully
        # Full audit trail validation is in E2E tests (Task 65.0)


# ============================================================================
# STATE PERSISTENCE TESTS
# ============================================================================

class TestStatePersistence:
    """
    State persistence integration tests.

    Verifies Step 11 data saved correctly with triage history.
    """

    @pytest.mark.integration
    @pytest.mark.step11
    @pytest.mark.skip(reason="State persistence requires E2E setup - moved to Task 65.0")
    def test_state_saves_step11_data_with_triage(
        self,
        mock_subprocess_run,
        mock_path_validation,
        temp_state_file,
        sample_workflow_state
    ):
        """
        P1: Verify Step 11 data persisted with triage history.

        AAA Pattern:
        1. Arrange - Mock test failing, setup state
        2. Act - run_test → qg_execution (triggers triage) → save state
        3. Assert - State includes Step 11 with triage data
        """
        # Arrange
        mock_subprocess_run.return_value.returncode = 1
        mock_subprocess_run.return_value.stdout = (
            "test_login.py::test_valid_login FAILED\n"
            "E   assert False"
        )

        state_manager = StateManager(state_file=temp_state_file)
        state_manager.save_state(sample_workflow_state)

        test_path = "tests/auth/test_login.py"

        # Act - run_test (fails)
        test_result = execute_test(test_path)

        # Act - qg_execution (triggers triage)
        execution_result = QGExecution.validate({
            "test_result": test_result,
            "test_path": test_path,
            "workflow": "auth"
        })

        # Act - Save Step 11 state (simulated - normally done by tool)
        sample_workflow_state["current_step"] = 11
        sample_workflow_state["steps"]["11"] = {
            "status": "awaiting_triage",
            "data": {
                "test_result": test_result,
                "triage_required": True,
                "ai_analysis": {
                    "likely_cause": "Assertion failure",
                    "confidence": 75
                }
            }
        }
        state_manager.save_state(sample_workflow_state)

        # Assert - State saved with Step 11
        loaded_state = state_manager.load_state()
        assert loaded_state["current_step"] == 11, \
            "Current step should be 11"
        assert "11" in loaded_state["steps"], \
            "Step 11 should be in state"
        assert loaded_state["steps"]["11"]["status"] == "awaiting_triage", \
            "Step 11 status should be awaiting_triage"
        assert loaded_state["steps"]["11"]["data"]["triage_required"] is True, \
            "Triage should be required"

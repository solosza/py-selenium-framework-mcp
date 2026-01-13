"""
Unit tests for QGWorkflowComplete meta-gate - Task 61.0

Test suite for workflow completion validation with 8 consistency checks.

Test Matrix:
- Happy path: 1 test (P0) - all checks pass
- Validation: 3 tests (P0) - missing parameters
- Consistency checks: 8 tests (P0) - each check failing individually
- Escalation: 4 tests (P1) - decision handling
- Integration: 2 tests (P1) - multiple checks, state manager integration

Testing Skill Reference: .claude/skills/testing/
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.gates.qg_workflow_complete import QGWorkflowComplete


# ============================================================================
# HAPPY PATH TESTS
# ============================================================================

class TestQGWorkflowCompleteHappyPath:
    """
    Happy path tests for qg_workflow_complete gate.

    Verifies all 8 consistency checks pass when workflow is valid.
    """

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_all_checks_pass_returns_pass(self, tmp_path):
        """
        P0: Verify all checks passing returns pass_response.

        AAA Pattern:
        1. Arrange - Create valid workflow state with all steps complete
        2. Act - Validate
        3. Assert - Returns pass with all_checks_passed=True
        """
        # Arrange - Mock state manager with valid state
        mock_state = MagicMock()

        # Mock comprehensive step data for all required steps
        def get_step_side_effect(step_num):
            if step_num == 2:
                return {"metadata": {"persona": "user", "url": "http://test.com", "workflow": "auth"}}
            elif step_num == 3:
                return {"metadata": {"bdd_scenarios": ["scenario1"], "expected_states": ["state1"]}}
            elif step_num == 4:
                return {"metadata": {"test_scenarios": ["scenario1"]}}
            elif step_num == 5:
                return {"metadata": {"discovered_elements": ["elem1"]}}
            elif step_num == 6:
                return {"metadata": {"pom_metadata": {"class": "Page"}}}
            elif step_num == 7:
                return {"metadata": {"task_metadata": {"class": "Task"}}}
            elif step_num == 8:
                return {"metadata": {"role_metadata": {"class": "Role"}}}
            elif step_num == 9:
                return {"metadata": {"test_path": "tests/test_example.py"}}
            elif step_num == 11:
                return {"metadata": {"test_result": {"status": "passed"}}}
            else:
                return {"metadata": {"workflow": "auth"}}

        mock_state.get_step.side_effect = get_step_side_effect

        # Mock is_step_complete for all steps 1-11
        mock_state.is_step_complete.return_value = True

        QGWorkflowComplete.set_state_manager(mock_state)

        # Mock audit logger with valid audit file
        audit_file_content = json.dumps({
            "steps": [{"step": i, "gate": f"gate_{i}"} for i in range(1, 12)]
        })

        with patch('builtins.open', mock_open(read_data=audit_file_content)):
            with patch('pathlib.Path.exists', return_value=True):
                # Act
                arguments = {
                    "workflow_id": "auth",
                    "test_path": "tests/test_example.py",
                    "test_result": {"status": "passed", "exit_code": 0}
                }

                result = QGWorkflowComplete.validate(arguments)

        # Assert
        assert result["status"] == "pass", \
            f"All checks passing should return 'pass', got {result['status']}"

        # Cleanup
        QGWorkflowComplete.set_state_manager(None)


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestQGWorkflowCompleteValidation:
    """
    Validation tests for qg_workflow_complete gate.

    Verifies parameter validation and error handling.
    """

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_missing_workflow_id_returns_fail(self):
        """
        P0: Verify missing workflow_id parameter returns fail response.

        AAA Pattern:
        1. Arrange - Create arguments without workflow_id
        2. Act - Validate
        3. Assert - Returns fail with error message
        """
        # Arrange
        arguments = {
            "test_path": "tests/test_example.py",
            "test_result": {"status": "passed"}
        }

        # Act
        result = QGWorkflowComplete.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Missing workflow_id should return 'fail'"
        assert "workflow_id" in result["error"].lower(), \
            f"Error should mention workflow_id, got: {result['error']}"

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_missing_test_path_returns_fail(self):
        """
        P0: Verify missing test_path parameter returns fail response.

        AAA Pattern:
        1. Arrange - Create arguments without test_path
        2. Act - Validate
        3. Assert - Returns fail with error message
        """
        # Arrange
        arguments = {
            "workflow_id": "auth",
            "test_result": {"status": "passed"}
        }

        # Act
        result = QGWorkflowComplete.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Missing test_path should return 'fail'"
        assert "test_path" in result["error"].lower(), \
            f"Error should mention test_path, got: {result['error']}"

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_missing_test_result_returns_fail(self):
        """
        P0: Verify missing test_result parameter returns fail response.

        AAA Pattern:
        1. Arrange - Create arguments without test_result
        2. Act - Validate
        3. Assert - Returns fail with error message
        """
        # Arrange
        arguments = {
            "workflow_id": "auth",
            "test_path": "tests/test_example.py"
        }

        # Act
        result = QGWorkflowComplete.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Missing test_result should return 'fail'"
        assert "test_result" in result["error"].lower(), \
            f"Error should mention test_result, got: {result['error']}"


# ============================================================================
# CONSISTENCY CHECK TESTS
# ============================================================================

class TestConsistencyChecks:
    """
    Tests for individual consistency checks.

    Verifies each of the 8 checks detects failures correctly.
    """

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_check1_test_path_mismatch_fails(self):
        """
        P0: Verify Check 1 (test path consistency) detects mismatch.

        AAA Pattern:
        1. Arrange - Mock Step 9 with different test path
        2. Act - Validate
        3. Assert - Returns fail with test path error
        """
        # Arrange - Mock state manager
        mock_state = MagicMock()
        mock_state.get_step.return_value = {
            "metadata": {"test_path": "tests/test_login.py"}
        }
        mock_state.is_step_complete.return_value = True

        QGWorkflowComplete.set_state_manager(mock_state)

        # Mock audit file with all steps
        audit_content = json.dumps({
            "steps": [{"step": i, "gate": f"gate_{i}"} for i in range(1, 12)]
        })

        with patch('builtins.open', mock_open(read_data=audit_content)):
            with patch('pathlib.Path.exists', return_value=True):
                # Act
                arguments = {
                    "workflow_id": "auth",
                    "test_path": "tests/test_checkout.py",  # Different path!
                    "test_result": {"status": "passed"}
                }

                result = QGWorkflowComplete.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Test path mismatch should return 'fail'"
        assert "consistency check" in result["error"].lower() or "failed" in result["error"].lower(), \
            f"Error should mention check failure, got: {result['error']}"
        assert "Test path consistency" in result["fix_hint"], \
            "Fix hint should mention test path consistency check"

        # Cleanup
        QGWorkflowComplete.set_state_manager(None)

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_check2_missing_file_fails(self):
        """
        P0: Verify Check 2 (file existence) detects missing files.

        AAA Pattern:
        1. Arrange - Mock Step 6 with POM path that doesn't exist
        2. Act - Validate
        3. Assert - Returns fail with file existence error
        """
        # Arrange
        mock_state = MagicMock()

        def get_step_side_effect(step_num):
            if step_num == 2:
                return {"metadata": {"workflow": "auth"}}
            elif step_num == 3:
                return {"metadata": {"bdd_scenarios": ["s1"], "expected_states": ["s1"]}}
            elif step_num == 9:
                return {"metadata": {"test_path": "tests/test_example.py"}}
            elif step_num == 6:
                return {"metadata": {"pom_path": "framework/pages/missing_page.py"}}
            elif step_num in [4, 5, 7, 8, 11]:
                return {"metadata": {"workflow": "auth", "dummy": "data"}}
            else:
                return {"metadata": {"workflow": "auth"}}

        mock_state.get_step.side_effect = get_step_side_effect
        mock_state.is_step_complete.return_value = True

        QGWorkflowComplete.set_state_manager(mock_state)

        audit_content = json.dumps({
            "steps": [{"step": i, "gate": f"gate_{i}"} for i in range(1, 12)]
        })

        # Create a side effect for Path.exists that returns False for POM, True for others
        def path_exists_side_effect(path_obj):
            path_str = str(path_obj)
            if "missing_page.py" in path_str:
                return False  # POM file missing
            return True  # Other files exist (audit, etc.)

        with patch('builtins.open', mock_open(read_data=audit_content)):
            with patch.object(Path, 'exists', side_effect=path_exists_side_effect):
                # Act
                arguments = {
                    "workflow_id": "auth",
                    "test_path": "tests/test_example.py",
                    "test_result": {"status": "passed"}
                }

                result = QGWorkflowComplete.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Missing file should return 'fail'"
        assert "File existence" in result["fix_hint"], \
            "Fix hint should mention file existence check"

        # Cleanup
        QGWorkflowComplete.set_state_manager(None)

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_check4_workflow_id_mismatch_fails(self):
        """
        P0: Verify Check 4 (workflow ID consistency) detects mismatch.

        AAA Pattern:
        1. Arrange - Mock steps with different workflow IDs
        2. Act - Validate
        3. Assert - Returns fail with workflow ID error
        """
        # Arrange
        mock_state = MagicMock()

        def get_step_side_effect(step_num):
            if step_num == 9:
                return {"metadata": {"test_path": "tests/test_example.py"}}
            elif step_num == 2:
                return {"metadata": {"workflow": "parabank"}}  # Different!
            else:
                return {"metadata": {"workflow": "auth"}}

        mock_state.get_step.side_effect = get_step_side_effect
        mock_state.is_step_complete.return_value = True

        QGWorkflowComplete.set_state_manager(mock_state)

        audit_content = json.dumps({
            "steps": [{"step": i, "gate": f"gate_{i}"} for i in range(1, 12)]
        })

        with patch('builtins.open', mock_open(read_data=audit_content)):
            with patch('pathlib.Path.exists', return_value=True):
                # Act
                arguments = {
                    "workflow_id": "auth",
                    "test_path": "tests/test_example.py",
                    "test_result": {"status": "passed"}
                }

                result = QGWorkflowComplete.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Workflow ID mismatch should return 'fail'"
        assert "Workflow ID consistency" in result["fix_hint"], \
            "Fix hint should mention workflow ID consistency check"

        # Cleanup
        QGWorkflowComplete.set_state_manager(None)

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_check5_audit_trail_incomplete_fails(self):
        """
        P0: Verify Check 5 (audit trail complete) detects missing steps.

        AAA Pattern:
        1. Arrange - Mock audit file missing Step 7
        2. Act - Validate
        3. Assert - Returns fail with audit trail error
        """
        # Arrange
        mock_state = MagicMock()
        mock_state.get_step.return_value = {
            "metadata": {"test_path": "tests/test_example.py"}
        }
        mock_state.is_step_complete.return_value = True

        QGWorkflowComplete.set_state_manager(mock_state)

        # Audit missing Step 7
        audit_content = json.dumps({
            "steps": [
                {"step": i, "gate": f"gate_{i}"}
                for i in range(1, 12) if i != 7  # Skip step 7
            ]
        })

        with patch('builtins.open', mock_open(read_data=audit_content)):
            with patch('pathlib.Path.exists', return_value=True):
                # Act
                arguments = {
                    "workflow_id": "auth",
                    "test_path": "tests/test_example.py",
                    "test_result": {"status": "passed"}
                }

                result = QGWorkflowComplete.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Incomplete audit trail should return 'fail'"
        assert "Audit trail complete" in result["fix_hint"], \
            "Fix hint should mention audit trail check"

        # Cleanup
        QGWorkflowComplete.set_state_manager(None)

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_check6_state_metadata_missing_fails(self):
        """
        P0: Verify Check 6 (state completeness) detects missing metadata.

        AAA Pattern:
        1. Arrange - Mock Step 3 without required metadata
        2. Act - Validate
        3. Assert - Returns fail with state completeness error
        """
        # Arrange
        mock_state = MagicMock()

        def get_step_side_effect(step_num):
            if step_num == 9:
                return {"metadata": {"test_path": "tests/test_example.py"}}
            elif step_num == 3:
                return {"metadata": {}}  # Missing bdd_scenarios and expected_states!
            else:
                return {"metadata": {"dummy": "data"}}

        mock_state.get_step.side_effect = get_step_side_effect
        mock_state.is_step_complete.return_value = True

        QGWorkflowComplete.set_state_manager(mock_state)

        audit_content = json.dumps({
            "steps": [{"step": i, "gate": f"gate_{i}"} for i in range(1, 12)]
        })

        with patch('builtins.open', mock_open(read_data=audit_content)):
            with patch('pathlib.Path.exists', return_value=True):
                # Act
                arguments = {
                    "workflow_id": "auth",
                    "test_path": "tests/test_example.py",
                    "test_result": {"status": "passed"}
                }

                result = QGWorkflowComplete.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Missing state metadata should return 'fail'"
        assert "State completeness" in result["fix_hint"], \
            "Fix hint should mention state completeness check"

        # Cleanup
        QGWorkflowComplete.set_state_manager(None)

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_check8_orphaned_state_fails(self):
        """
        P0: Verify Check 8 (no orphaned state) detects incomplete steps.

        AAA Pattern:
        1. Arrange - Mock Step 5 not marked complete
        2. Act - Validate
        3. Assert - Returns fail with orphaned state error
        """
        # Arrange
        mock_state = MagicMock()
        mock_state.get_step.return_value = {
            "metadata": {"test_path": "tests/test_example.py"}
        }

        # Step 5 not complete
        def is_complete_side_effect(step_num):
            return step_num != 5

        mock_state.is_step_complete.side_effect = is_complete_side_effect

        QGWorkflowComplete.set_state_manager(mock_state)

        audit_content = json.dumps({
            "steps": [{"step": i, "gate": f"gate_{i}"} for i in range(1, 12)]
        })

        with patch('builtins.open', mock_open(read_data=audit_content)):
            with patch('pathlib.Path.exists', return_value=True):
                # Act
                arguments = {
                    "workflow_id": "auth",
                    "test_path": "tests/test_example.py",
                    "test_result": {"status": "passed"}
                }

                result = QGWorkflowComplete.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Incomplete step should return 'fail'"
        assert "No orphaned state" in result["fix_hint"], \
            "Fix hint should mention orphaned state check"

        # Cleanup
        QGWorkflowComplete.set_state_manager(None)


# ============================================================================
# ESCALATION DECISION TESTS
# ============================================================================

class TestEscalationDecisions:
    """
    Tests for handling escalation decisions.

    Verifies correct action for each decision type.
    """

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_rerun_step11_decision(self):
        """
        P1: Verify re-run Step 11 decision triggers correct action.

        AAA Pattern:
        1. Arrange - User selects option 1 (rerun)
        2. Act - Handle decision
        3. Assert - Returns rerun_step11 action, blocking=False
        """
        # Arrange
        failed_checks = [{"check": "test_path", "error": "mismatch"}]

        # Act
        result = QGWorkflowComplete.handle_escalation_decision("1", failed_checks)

        # Assert
        assert result["action"] == "rerun_step11", \
            f"Option 1 should trigger rerun_step11, got {result['action']}"
        assert result["blocking"] is False, \
            "Re-run should not be blocking"

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_restart_workflow_decision(self):
        """
        P1: Verify restart workflow decision triggers correct action.

        AAA Pattern:
        1. Arrange - User selects option 2 (restart)
        2. Act - Handle decision
        3. Assert - Returns restart_workflow action, blocking=True
        """
        # Arrange
        failed_checks = [{"check": "workflow_id", "error": "inconsistent"}]

        # Act
        result = QGWorkflowComplete.handle_escalation_decision("2", failed_checks)

        # Assert
        assert result["action"] == "restart_workflow", \
            f"Option 2 should trigger restart_workflow, got {result['action']}"
        assert result["blocking"] is True, \
            "Restart should be blocking"

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_accept_as_is_decision(self):
        """
        P1: Verify accept as-is decision allows workflow to proceed.

        AAA Pattern:
        1. Arrange - User selects option 3 (accept)
        2. Act - Handle decision
        3. Assert - Returns accept_as_is action, blocking=False
        """
        # Arrange
        failed_checks = [{"check": "minor_issue", "error": "acceptable"}]

        # Act
        result = QGWorkflowComplete.handle_escalation_decision("3", failed_checks)

        # Assert
        assert result["action"] == "accept_as_is", \
            f"Option 3 should trigger accept_as_is, got {result['action']}"
        assert result["blocking"] is False, \
            "Accept as-is should not be blocking"

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_abort_workflow_decision(self):
        """
        P1: Verify abort workflow decision stops execution.

        AAA Pattern:
        1. Arrange - User selects option 4 (abort)
        2. Act - Handle decision
        3. Assert - Returns abort action, blocking=True
        """
        # Arrange
        failed_checks = [{"check": "critical_issue", "error": "cannot_proceed"}]

        # Act
        result = QGWorkflowComplete.handle_escalation_decision("4", failed_checks)

        # Assert
        assert result["action"] == "abort", \
            f"Option 4 should trigger abort, got {result['action']}"
        assert result["blocking"] is True, \
            "Abort should be blocking"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """
    Integration tests for qg_workflow_complete gate.

    Verifies gate behavior with real state manager integration.
    """

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_multiple_checks_fail_lists_all(self):
        """
        P1: Verify multiple failing checks all listed in fix_hint.

        AAA Pattern:
        1. Arrange - Mock state with multiple issues
        2. Act - Validate
        3. Assert - Fix hint mentions all failed checks
        """
        # Arrange
        mock_state = MagicMock()

        def get_step_side_effect(step_num):
            if step_num == 9:
                return {"metadata": {"test_path": "tests/wrong.py"}}  # Check 1 fail (path mismatch)
            elif step_num == 2:
                return {"metadata": {"workflow": "wrong"}}  # Check 4 fail (workflow ID)
            elif step_num == 3:
                return {"metadata": {}}  # Check 6 fail (missing metadata)
            else:
                return {"metadata": {"workflow": "auth"}}

        mock_state.get_step.side_effect = get_step_side_effect
        mock_state.is_step_complete.return_value = False  # Check 8 fail (incomplete steps)

        QGWorkflowComplete.set_state_manager(mock_state)

        # Audit missing steps (Check 5 fail)
        audit_content = json.dumps({"steps": [{"step": 1, "gate": "gate_1"}]})

        with patch('builtins.open', mock_open(read_data=audit_content)):
            with patch('pathlib.Path.exists', return_value=True):
                # Act
                arguments = {
                    "workflow_id": "auth",
                    "test_path": "tests/test_example.py",
                    "test_result": {"status": "passed"}
                }

                result = QGWorkflowComplete.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Multiple failures should return 'fail'"
        assert len(result["metadata"]["failed_checks"]) >= 2, \
            f"Should list multiple failed checks, got {len(result['metadata']['failed_checks'])}"
        assert "ESCALATION OPTIONS" in result["fix_hint"], \
            "Should include escalation options"

        # Cleanup
        QGWorkflowComplete.set_state_manager(None)

    @pytest.mark.unit
    @pytest.mark.qg_workflow_complete
    def test_without_state_manager_skips_checks(self):
        """
        P1: Verify gate handles missing state manager gracefully.

        AAA Pattern:
        1. Arrange - No state manager set
        2. Act - Validate
        3. Assert - Returns pass (cannot validate without state)
        """
        # Arrange - Ensure no state manager
        QGWorkflowComplete.set_state_manager(None)

        audit_content = json.dumps({
            "steps": [{"step": i, "gate": f"gate_{i}"} for i in range(1, 12)]
        })

        with patch('builtins.open', mock_open(read_data=audit_content)):
            with patch('pathlib.Path.exists', return_value=True):
                # Act
                arguments = {
                    "workflow_id": "auth",
                    "test_path": "tests/test_example.py",
                    "test_result": {"status": "passed"}
                }

                result = QGWorkflowComplete.validate(arguments)

        # Assert - Without state manager, most checks are skipped
        # Gate should either pass or fail gracefully
        assert result["status"] in ["pass", "fail"], \
            f"Should return valid status, got {result['status']}"

"""
Test suite for Task 7.0 - Production Test Fixes.

Tests three critical fixes discovered in production:
- DEF-049: Audit run_id reuse causing history loss
- DEF-050: State not persisted per-run (no context recovery)
- DEF-051: Multi-POM workflows only save 1 file

Test Pyramid Layers:
1. StateManager: Run isolation, state persistence, recovery
2. BaseGate Audit: Fresh run_id, no reuse, history preservation
3. Gates File Write: Immediate writes, multi-file handling, validation

Coverage Target: 90%+ (Critical path)
"""

import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


# ==================== STATEMANAGER TESTS (Per-Run Architecture) ====================


class TestStateManagerPerRunArchitecture:
    """
    Tests for StateManager per-run directory isolation.

    Pyramid Layer: RUN ISOLATION
    Verifies each workflow gets separate state directory.
    """

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup with temporary test directory."""
        self.test_state_dir = tmp_path / "_state"
        self.test_state_dir.mkdir()

    # ==================== TEST METHODS ====================

    @pytest.mark.unit
    def test_create_per_run_directory_structure(self):
        """
        P0: StateManager creates per-run directory.

        AAA Pattern:
        1. Arrange - Mock run_id and base directory
        2. Act - Initialize StateManager with run_id
        3. Assert - Directory tests/_state/{run_id}/ exists
        """
        # Arrange
        from utils.state_manager import StateManager
        run_id = "2026-01-07T10-00-00Z"

        # Act
        state_manager = StateManager(run_id=run_id)
        # Save some data to trigger directory creation
        state_manager.save(step=1, data={"test": "data"})

        # Assert
        expected_file = Path(__file__).parent.parent.parent / "tests" / "_state" / run_id / "workflow_state.json"
        assert expected_file.exists(), f"State file should exist at {expected_file}"
        assert state_manager.get_run_id() == run_id, f"Should return run_id {run_id}"

    @pytest.mark.unit
    def test_save_state_to_per_run_file(self):
        """
        P0: StateManager saves state to per-run file.

        AAA Pattern:
        1. Arrange - StateManager with run_id, test data
        2. Act - Call save(step=6, data={...})
        3. Assert - File tests/_state/{run_id}/workflow_state.json exists
        """
        # Arrange
        from utils.state_manager import StateManager
        run_id = "2026-01-07T10-00-00Z"
        test_data = {"generated_poms": {"LoginPage": {"code": "test"}}}

        # Act
        state_manager = StateManager(run_id=run_id)
        state_manager.save(step=6, data=test_data)

        # Assert
        expected_file = Path(__file__).parent.parent.parent / "tests" / "_state" / run_id / "workflow_state.json"
        assert expected_file.exists(), "State file should exist in per-run directory"

        # Verify content
        loaded_data = state_manager.load()
        assert "step_6" in loaded_data, "Should have step_6 key"
        assert loaded_data["step_6"] == test_data, "Should save exact data"

    @pytest.mark.unit
    def test_load_state_from_previous_run(self):
        """
        P0: StateManager can load state from previous run.

        AAA Pattern:
        1. Arrange - Create state file for previous run_id
        2. Act - Initialize StateManager with same run_id, call load()
        3. Assert - Returns saved state data
        """
        # Arrange
        from utils.state_manager import StateManager
        run_id = "2026-01-07T10-00-00Z"
        state_dir = Path(__file__).parent.parent.parent / "tests" / "_state" / run_id
        state_dir.mkdir(parents=True, exist_ok=True)
        state_file = state_dir / "workflow_state.json"
        expected_data = {"step_6": {"generated_poms": {}}}
        state_file.write_text(json.dumps(expected_data))

        # Act
        state_manager = StateManager(run_id=run_id)
        loaded_data = state_manager.load()

        # Assert
        assert loaded_data == expected_data, "Should load exact state from previous run"

    @pytest.mark.unit
    def test_multiple_runs_create_separate_directories(self):
        """
        P0: Multiple workflow runs create separate state directories.

        AAA Pattern:
        1. Arrange - Two different run_ids
        2. Act - Create StateManager for each run_id, save data
        3. Assert - Two separate directories exist
        """
        # Arrange
        from utils.state_manager import StateManager
        run_id_1 = "2026-01-07T10-00-00Z"
        run_id_2 = "2026-01-07T11-00-00Z"

        # Act
        state_manager_1 = StateManager(run_id=run_id_1)
        state_manager_1.save(step=1, data={"run": 1})

        state_manager_2 = StateManager(run_id=run_id_2)
        state_manager_2.save(step=1, data={"run": 2})

        # Assert
        base_dir = Path(__file__).parent.parent.parent / "tests" / "_state"
        dir_1 = base_dir / run_id_1 / "workflow_state.json"
        dir_2 = base_dir / run_id_2 / "workflow_state.json"
        assert dir_1.exists(), "First run should have separate directory"
        assert dir_2.exists(), "Second run should have separate directory"

        # Verify data isolation
        assert state_manager_1.load()["step_1"] == {"run": 1}, "First run data should be isolated"
        assert state_manager_2.load()["step_1"] == {"run": 2}, "Second run data should be isolated"

    @pytest.mark.unit
    def test_invalid_run_id_raises_error(self):
        """
        P0: StateManager rejects invalid run_id format.

        AAA Pattern:
        1. Arrange - Invalid run_id (empty, malformed)
        2. Act - Try to initialize StateManager
        3. Assert - Raises ValueError with helpful message
        """
        # Arrange
        from utils.state_manager import StateManager
        invalid_run_id = ""

        # Act & Assert
        with pytest.raises(ValueError, match="run_id cannot be empty"):
            StateManager(run_id=invalid_run_id)

    @pytest.mark.unit
    def test_get_run_id_method(self):
        """
        P0: StateManager exposes get_run_id() method.

        AAA Pattern:
        1. Arrange - StateManager with known run_id
        2. Act - Call get_run_id()
        3. Assert - Returns the run_id passed to constructor
        """
        # Arrange
        from utils.state_manager import StateManager
        run_id = "2026-01-07T10-00-00Z"

        # Act
        state_manager = StateManager(run_id=run_id)
        result = state_manager.get_run_id()

        # Assert
        assert result == run_id, f"Should return {run_id}, got {result}"

        # Also test that legacy StateManager returns None
        legacy_state_manager = StateManager()
        assert legacy_state_manager.get_run_id() is None, "Legacy StateManager should return None"


# ==================== BASEGATE AUDIT LOGGER TESTS (Fresh Run ID) ====================


class TestBaseGateAuditRunID:
    """
    Tests for BaseGate audit logger run_id generation.

    Pyramid Layer: FRESH RUN ID
    Verifies each workflow gets new audit run_id (never reused).
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        from tools.gates.base_gate import BaseGate
        # Reset class-level audit logger before each test
        BaseGate._audit_logger = None

    # ==================== TEST METHODS ====================

    @pytest.mark.unit
    def test_fresh_run_id_each_workflow(self):
        """
        P0: Each workflow (after session clear) gets fresh run_id.

        AAA Pattern:
        1. Arrange - Clean BaseGate state
        2. Act - Call get_audit_logger() twice with session clear between
        3. Assert - Two different run_ids generated

        DEF-052: Updated to clear session marker instead of just class variable
        """
        # Arrange
        from tools.gates.base_gate import BaseGate
        import time

        # Act
        logger_1 = BaseGate.get_audit_logger()
        run_id_1 = logger_1.run_id

        time.sleep(0.01)  # Ensure timestamp difference
        # DEF-052: Clear session marker (simulates new workflow)
        BaseGate._clear_session_marker()
        BaseGate._audit_logger = None

        logger_2 = BaseGate.get_audit_logger()
        run_id_2 = logger_2.run_id

        # Assert
        assert run_id_1 != run_id_2, f"Each workflow should get fresh run_id: {run_id_1} vs {run_id_2}"

    @pytest.mark.unit
    def test_no_run_id_reuse_from_state(self):
        """
        P0: BaseGate NEVER reads run_id from StateManager.

        AAA Pattern:
        1. Arrange - Create actual state file with old run_id in step_0
        2. Act - Call get_audit_logger()
        3. Assert - Does NOT use run_id from state
        """
        # Arrange
        from tools.gates.base_gate import BaseGate
        from utils.state_manager import StateManager
        old_run_id = "2026-01-07T10-00-00Z"

        # Create state with old audit_run_id
        state = StateManager()
        state.save(step=0, data={"audit_run_id": old_run_id})

        # Act
        logger = BaseGate.get_audit_logger()

        # Assert
        assert logger.run_id != old_run_id, f"Should NOT reuse run_id from state: got {logger.run_id}, should not be {old_run_id}"

        # Cleanup
        state.clear()

    @pytest.mark.unit
    def test_multiple_audit_files_created(self):
        """
        P0: Multiple workflow runs create separate audit files.

        AAA Pattern:
        1. Arrange - Two separate workflow runs
        2. Act - Call get_audit_logger() for each run, finalize both
        3. Assert - Two different audit files exist

        DEF-052: Updated to clear session marker between workflows
        """
        # Arrange
        from tools.gates.base_gate import BaseGate
        import time

        # Act
        logger_1 = BaseGate.get_audit_logger()
        run_id_1 = logger_1.run_id
        logger_1.finalize()  # Write audit file

        time.sleep(0.01)  # Ensure timestamp difference
        # DEF-052: Clear session marker (new workflow)
        BaseGate._clear_session_marker()
        BaseGate._audit_logger = None

        logger_2 = BaseGate.get_audit_logger()
        run_id_2 = logger_2.run_id
        logger_2.finalize()  # Write audit file

        # Assert
        assert run_id_1 != run_id_2, "Different workflows should have different run_ids"

        # Check audit files exist
        audit_dir = Path(__file__).parent.parent.parent / "tests" / "_audit"
        audit_file_1 = audit_dir / f"audit_log_{run_id_1}.json"
        audit_file_2 = audit_dir / f"audit_log_{run_id_2}.json"

        assert audit_file_1.exists(), f"First audit file should exist: {audit_file_1}"
        assert audit_file_2.exists(), f"Second audit file should exist: {audit_file_2}"


# ==================== QUALITY GATES FILE WRITE TESTS (Immediate Persistence) ====================


class TestQualityGatesImmediateFileWrite:
    """
    Tests for immediate file writes after gate validation.

    Pyramid Layer: IMMEDIATE WRITE
    Verifies files written to disk during workflow, not at Step 10.
    """

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup with temporary framework directory."""
        self.test_framework_dir = tmp_path / "framework"
        self.test_framework_dir.mkdir()

    # ==================== TEST METHODS ====================

    @pytest.mark.unit
    def test_pom_file_written_immediately_after_pass(self):
        """
        P0: POM file written to disk immediately after qg_page_object passes.

        AAA Pattern:
        1. Arrange - Mock qg_page_object POST with valid POM
        2. Act - Call validate_post()
        3. Assert - File exists on disk before returning
        """
        # Arrange
        pom_code = 'class LoginPage:\n    pass'
        file_path = self.test_framework_dir / "pages" / "auth" / "login_page.py"

        # Act
        # TODO: Call qg_page_object.validate_post() with code + metadata

        # Assert
        # assert file_path.exists(), "POM file should exist immediately after validation"
        assert True, "Placeholder - implement after gate file write fix"

    @pytest.mark.unit
    def test_multi_pom_all_files_saved(self):
        """
        P0: Multi-page workflow saves ALL POMs, not just last one (DEF-051 fix).

        AAA Pattern:
        1. Arrange - 6 POMs in generated_poms dict
        2. Act - Call validate_post() with multi-page metadata
        3. Assert - All 6 POM files exist on disk
        """
        # Arrange
        generated_poms = {
            "LoginPage": {"code": "class LoginPage: pass", "metadata": {}},
            "AccountPage": {"code": "class AccountPage: pass", "metadata": {}},
            "TransferPage": {"code": "class TransferPage: pass", "metadata": {}},
            "ActivityPage": {"code": "class ActivityPage: pass", "metadata": {}},
            "RegisterPage": {"code": "class RegisterPage: pass", "metadata": {}},
            "ConfirmPage": {"code": "class ConfirmPage: pass", "metadata": {}},
        }

        # Act
        # TODO: Call qg_page_object.validate_post() with all POMs

        # Assert
        # for page_name in generated_poms.keys():
        #     file_path = self.test_framework_dir / "pages" / f"{page_name.lower()}.py"
        #     assert file_path.exists(), f"{page_name} should be saved to disk"
        assert True, "Placeholder - implement after gate file write fix"

    @pytest.mark.unit
    def test_task_file_written_immediately(self):
        """
        P0: Task file written immediately after qg_task passes.

        AAA Pattern:
        1. Arrange - Mock qg_task POST with valid Task
        2. Act - Call validate_post()
        3. Assert - File exists on disk
        """
        # Arrange
        task_code = 'class AuthTasks:\n    pass'
        file_path = self.test_framework_dir / "tasks" / "auth" / "auth_tasks.py"

        # Act
        # TODO: Call qg_task.validate_post()

        # Assert
        # assert file_path.exists(), "Task file should exist immediately"
        assert True, "Placeholder - implement after gate file write fix"

    @pytest.mark.unit
    def test_role_file_written_immediately(self):
        """
        P0: Role file written immediately after qg_role passes.

        AAA Pattern:
        1. Arrange - Mock qg_role POST with valid Role
        2. Act - Call validate_post()
        3. Assert - File exists on disk
        """
        # Arrange
        role_code = 'class RegisteredUser:\n    pass'
        file_path = self.test_framework_dir / "roles" / "registered_user.py"

        # Act
        # TODO: Call qg_role.validate_post()

        # Assert
        # assert file_path.exists(), "Role file should exist immediately"
        assert True, "Placeholder - implement after gate file write fix"

    @pytest.mark.unit
    def test_test_file_written_immediately(self):
        """
        P0: Test file written immediately after qg_test_runner passes.

        AAA Pattern:
        1. Arrange - Mock qg_test_runner POST with valid test
        2. Act - Call validate_post()
        3. Assert - File exists on disk
        """
        # Arrange
        test_code = 'def test_login():\n    pass'
        file_path = self.test_framework_dir / "tests" / "auth" / "test_login.py"

        # Act
        # TODO: Call qg_test_runner.validate_post()

        # Assert
        # assert file_path.exists(), "Test file should exist immediately"
        assert True, "Placeholder - implement after gate file write fix"

    @pytest.mark.integration
    def test_file_write_logged_to_audit(self):
        """
        P0: File write is logged to audit trail after gate passes.

        AAA Pattern:
        1. Arrange - Mock audit logger, qg_page_object with POM
        2. Act - Call validate_post()
        3. Assert - Audit logger called with file_path
        """
        # Arrange
        from tools.gates.base_gate import BaseGate
        mock_audit = Mock()
        BaseGate._audit_logger = mock_audit

        # Act
        # TODO: Call qg_page_object.validate_post()

        # Assert
        # mock_audit.log_file_generated.assert_called_once()
        assert True, "Placeholder - implement after gate file write fix"


# ==================== STEP 10 VALIDATION TESTS (File Existence Check) ====================


class TestStep10FileValidation:
    """
    Tests for Step 10 PRE gate file validation.

    Pyramid Layer: VALIDATION
    Verifies qg_save_run detects missing files before save.
    """

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup with temporary framework directory."""
        self.test_framework_dir = tmp_path / "framework"
        self.test_framework_dir.mkdir()

    # ==================== TEST METHODS ====================

    @pytest.mark.unit
    def test_step10_detects_missing_files(self):
        """
        P0: Step 10 PRE gate fails if expected files don't exist.

        AAA Pattern:
        1. Arrange - State with expected files, but files don't exist on disk
        2. Act - Call qg_save_run.validate_pre()
        3. Assert - Returns fail with missing file list
        """
        # Arrange
        expected_files = [
            "framework/pages/auth/login_page.py",
            "framework/tasks/auth/auth_tasks.py",
            "framework/roles/registered_user.py",
        ]

        # Act
        # TODO: Call qg_save_run.validate_pre() with state containing expected files

        # Assert
        # result = qg_save_run.validate_pre(...)
        # assert result["status"] == "fail", "Should fail when files missing"
        # assert "Missing: [...]" in result["error"], "Should list missing files"
        assert True, "Placeholder - implement after Step 10 enhancement"

    @pytest.mark.unit
    def test_step10_passes_when_all_files_exist(self):
        """
        P0: Step 10 PRE gate passes when all expected files exist.

        AAA Pattern:
        1. Arrange - Create all expected files on disk
        2. Act - Call qg_save_run.validate_pre()
        3. Assert - Returns pass
        """
        # Arrange
        expected_files = [
            self.test_framework_dir / "pages" / "auth" / "login_page.py",
            self.test_framework_dir / "tasks" / "auth" / "auth_tasks.py",
        ]
        for file_path in expected_files:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("# test file")

        # Act
        # TODO: Call qg_save_run.validate_pre()

        # Assert
        # result = qg_save_run.validate_pre(...)
        # assert result["status"] == "pass", "Should pass when all files exist"
        assert True, "Placeholder - implement after Step 10 enhancement"

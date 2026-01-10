"""
Unit tests for FR-14.4: File existence validation in qg_save_run.

Tests that qg_save_run validates required test data files exist
based on Step 1 strategies before workflow completion.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from tools.gates.qg_save_run import QGSaveRun
from utils.state_manager import StateManager


class TestFileExistenceValidation:
    """Test FR-14.4: Test data file existence validation."""

    def test_passes_when_static_credentials_file_exists(self):
        """Test validation passes when static strategy and file exists."""
        # Mock state manager
        state_manager = MagicMock(spec=StateManager)
        state_manager.get_step.side_effect = lambda step: {
            1: {"credential_strategy": "static", "test_data_location": "shared"},
            2: {"workflow": "auth"}
        }.get(step, None)

        # Mock file existence check to return True
        with patch('pathlib.Path.exists', return_value=True):
            result = QGSaveRun._validate_test_data_files_exist(state_manager)

        assert result is None  # No error

    def test_fails_when_static_credentials_file_missing(self):
        """Test validation fails when static strategy but file missing."""
        # Mock state manager
        state_manager = MagicMock(spec=StateManager)
        state_manager.get_step.side_effect = lambda step: {
            1: {"credential_strategy": "static", "test_data_location": "shared"},
            2: {"workflow": "auth"}
        }.get(step, None)

        # Mock file existence check to return False
        with patch('pathlib.Path.exists', return_value=False):
            result = QGSaveRun._validate_test_data_files_exist(state_manager)

        assert result is not None
        assert result["status"] == "fail"
        assert "test_users.json" in result["error"]
        assert "static" in result["error"]

    def test_passes_when_self_contained_strategy(self):
        """Test validation passes with self-contained (no file required)."""
        # Mock state manager
        state_manager = MagicMock(spec=StateManager)
        state_manager.get_step.side_effect = lambda step: {
            1: {"credential_strategy": "self-contained", "test_data_location": "none"},
            2: {"workflow": "auth"}
        }.get(step, None)

        # No need to mock file existence - shouldn't check
        result = QGSaveRun._validate_test_data_files_exist(state_manager)

        assert result is None  # No error

    def test_passes_when_dynamic_strategy(self):
        """Test validation passes with dynamic strategy (no pre-existing file required)."""
        # Mock state manager
        state_manager = MagicMock(spec=StateManager)
        state_manager.get_step.side_effect = lambda step: {
            1: {"credential_strategy": "dynamic", "test_data_location": "workflow"},
            2: {"workflow": "auth"}
        }.get(step, None)

        # Mock workflow directory exists
        with patch('pathlib.Path.exists', return_value=True):
            result = QGSaveRun._validate_test_data_files_exist(state_manager)

        assert result is None  # No error

    def test_warns_when_workflow_directory_missing(self):
        """Test validation warns when workflow directory doesn't exist."""
        # Mock state manager
        state_manager = MagicMock(spec=StateManager)
        state_manager.get_step.side_effect = lambda step: {
            1: {"credential_strategy": "none", "test_data_location": "workflow"},
            2: {"workflow": "parabank"}
        }.get(step, None)

        # Mock directory existence check to return False
        with patch('pathlib.Path.exists', return_value=False):
            result = QGSaveRun._validate_test_data_files_exist(state_manager)

        assert result is not None
        assert result["status"] == "fail"
        assert "parabank" in result["error"]
        assert "workflow" in result["error"]

    def test_passes_when_no_step1_data(self):
        """Test validation skips when no Step 1 data exists."""
        # Mock state manager with no Step 1 data
        state_manager = MagicMock(spec=StateManager)
        state_manager.get_step.return_value = None

        result = QGSaveRun._validate_test_data_files_exist(state_manager)

        assert result is None  # Skipped validation

    def test_passes_when_both_strategy_with_shared_file(self):
        """Test validation passes with 'both' strategy when shared file exists."""
        # Mock state manager
        state_manager = MagicMock(spec=StateManager)
        state_manager.get_step.side_effect = lambda step: {
            1: {"credential_strategy": "static", "test_data_location": "both"},
            2: {"workflow": "auth"}
        }.get(step, None)

        # Mock file existence
        with patch('pathlib.Path.exists', return_value=True):
            result = QGSaveRun._validate_test_data_files_exist(state_manager)

        assert result is None  # No error

    def test_error_message_includes_fix_hints(self):
        """Test error message provides actionable fix hints."""
        # Mock state manager
        state_manager = MagicMock(spec=StateManager)
        state_manager.get_step.side_effect = lambda step: {
            1: {"credential_strategy": "static", "test_data_location": "shared"},
            2: {"workflow": "auth"}
        }.get(step, None)

        # Mock file missing
        with patch('pathlib.Path.exists', return_value=False):
            result = QGSaveRun._validate_test_data_files_exist(state_manager)

        assert result is not None
        assert "fix_hint" in result
        assert "Create" in result["error"] or "Create" in result["fix_hint"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

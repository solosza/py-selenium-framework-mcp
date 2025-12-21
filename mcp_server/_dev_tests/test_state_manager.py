"""
Unit tests for StateManager - Task 2.0

Test suite for workflow state persistence.

Test Matrix:
- Happy path: 4 tests (P0)
- Negative: 3 tests (P0)
- Edge cases: 3 tests (P1)
- Error handling: 2 tests (P1)
- Default path: 1 test (P1)
- Write errors: 2 tests (P2)

Testing Skill Reference: .claude/skills/testing/
"""

import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.state_manager import StateManager


# ============================================================================
# HAPPY PATH TESTS
# ============================================================================

class TestStateManagerHappyPath:
    """
    Happy path tests for StateManager.

    Verifies core functionality works correctly under normal conditions:
    - save() creates state files
    - load() returns state
    - get_step() retrieves specific steps
    - is_step_complete() checks completion status
    """

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_save_creates_state_file(self, tmp_path):
        """
        P0: Verify save() creates a state file with step data.

        AAA Pattern:
        1. Arrange - Create StateManager with temp path
        2. Act - Save step 1 data
        3. Assert - File exists with correct content
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        manager = StateManager(state_file=str(state_file))

        # Act
        manager.save(step=1, data={"credential_strategy": "static"})

        # Assert
        assert state_file.exists(), "State file should be created after save()"
        with open(state_file) as f:
            content = json.load(f)
        assert "step_1" in content, "State should contain step_1 key"
        assert content["step_1"]["credential_strategy"] == "static", \
            "Step data should match saved values"

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_load_returns_state(self, tmp_path):
        """
        P0: Verify load() returns the complete state dictionary.

        AAA Pattern:
        1. Arrange - Create state file with known content
        2. Act - Load state via StateManager
        3. Assert - Returned state matches file content
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        initial_state = {
            "step_1": {"credential_strategy": "static"},
            "step_2": {"persona": "registered user", "url": "http://example.com"}
        }
        with open(state_file, "w") as f:
            json.dump(initial_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.load()

        # Assert
        assert result == initial_state, \
            f"Loaded state should match file content, got {result}"

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_get_step_returns_data(self, tmp_path):
        """
        P0: Verify get_step() returns data for a specific step.

        AAA Pattern:
        1. Arrange - Create state file with multiple steps
        2. Act - Get step 1 data
        3. Assert - Returns correct step data
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        initial_state = {
            "step_1": {"credential_strategy": "dynamic"},
            "step_2": {"persona": "guest"}
        }
        with open(state_file, "w") as f:
            json.dump(initial_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.get_step(1)

        # Assert
        assert result == {"credential_strategy": "dynamic"}, \
            f"get_step(1) should return step_1 data, got {result}"

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_is_step_complete_returns_true(self, tmp_path):
        """
        P0: Verify is_step_complete() returns True when step exists with data.

        AAA Pattern:
        1. Arrange - Create state file with step 3 data
        2. Act - Check if step 3 is complete
        3. Assert - Returns True
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        initial_state = {"step_3": {"bdd_scenarios": ["given...", "when...", "then..."]}}
        with open(state_file, "w") as f:
            json.dump(initial_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.is_step_complete(3)

        # Assert
        assert result is True, "Step 3 should be marked complete when data exists"


# ============================================================================
# NEGATIVE TESTS
# ============================================================================

class TestStateManagerNegative:
    """
    Negative tests for StateManager.

    Verifies graceful handling of:
    - Missing files
    - Non-existent steps
    - Incomplete workflow state
    """

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_load_missing_file_returns_empty(self, tmp_path):
        """
        P0: Verify load() returns empty dict when file doesn't exist.

        AAA Pattern:
        1. Arrange - Create manager pointing to non-existent file
        2. Act - Load state
        3. Assert - Returns empty dict
        """
        # Arrange
        state_file = tmp_path / "nonexistent.json"
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.load()

        # Assert
        assert result == {}, \
            f"Missing file should return empty dict, got {result}"

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_get_step_not_found_returns_none(self, tmp_path):
        """
        P0: Verify get_step() returns None for non-existent step.

        AAA Pattern:
        1. Arrange - Create state with only step 1
        2. Act - Request step 5
        3. Assert - Returns None
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        initial_state = {"step_1": {"data": "exists"}}
        with open(state_file, "w") as f:
            json.dump(initial_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.get_step(5)

        # Assert
        assert result is None, \
            f"Non-existent step should return None, got {result}"

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_is_step_complete_returns_false(self, tmp_path):
        """
        P0: Verify is_step_complete() returns False for incomplete step.

        AAA Pattern:
        1. Arrange - Create state with only step 1
        2. Act - Check if step 2 is complete
        3. Assert - Returns False
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        initial_state = {"step_1": {"data": "exists"}}
        with open(state_file, "w") as f:
            json.dump(initial_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.is_step_complete(2)

        # Assert
        assert result is False, \
            "Incomplete step should return False"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestStateManagerEdgeCases:
    """
    Edge case tests for StateManager.

    Verifies handling of:
    - Empty data
    - Boundary step values (0, 10)
    - Invalid step numbers
    """

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_save_empty_data(self, tmp_path):
        """
        P1: Verify save() handles empty data dict.

        AAA Pattern:
        1. Arrange - Create StateManager
        2. Act - Save empty data for step 1
        3. Assert - File created with empty step data
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        manager = StateManager(state_file=str(state_file))

        # Act
        manager.save(step=1, data={})

        # Assert
        assert state_file.exists(), "State file should be created"
        with open(state_file) as f:
            content = json.load(f)
        assert "step_1" in content, "State should contain step_1"
        assert content["step_1"] == {}, \
            f"Empty data should be saved as empty dict, got {content['step_1']}"

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_get_step_zero(self, tmp_path):
        """
        P1: Verify get_step(0) returns None (valid steps are 1-10).

        AAA Pattern:
        1. Arrange - Create state with step_0 key (shouldn't be valid)
        2. Act - Request step 0
        3. Assert - Returns None (invalid step)
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        initial_state = {"step_0": {"should": "not exist"}}
        with open(state_file, "w") as f:
            json.dump(initial_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.get_step(0)

        # Assert
        assert result is None, \
            "Step 0 is invalid - should return None even if key exists"

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_get_step_boundary_ten(self, tmp_path):
        """
        P1: Verify get_step(10) works correctly (last valid step).

        AAA Pattern:
        1. Arrange - Create state with step 10 data
        2. Act - Request step 10
        3. Assert - Returns step 10 data
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        initial_state = {"step_10": {"final": "data"}}
        with open(state_file, "w") as f:
            json.dump(initial_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.get_step(10)

        # Assert
        assert result == {"final": "data"}, \
            f"Step 10 should be valid boundary, got {result}"


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestStateManagerErrorHandling:
    """
    Error handling tests for StateManager.

    Verifies:
    - Atomic writes prevent corruption
    - Corrupted JSON handled gracefully
    """

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_atomic_write_no_corruption(self, tmp_path):
        """
        P1: Verify save() uses atomic write to prevent corruption.

        AAA Pattern:
        1. Arrange - Create StateManager
        2. Act - Save two steps sequentially
        3. Assert - Both steps exist without corruption
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        manager = StateManager(state_file=str(state_file))

        # Act
        manager.save(step=1, data={"initial": "data"})
        manager.save(step=2, data={"second": "step"})

        # Assert
        with open(state_file) as f:
            content = json.load(f)
        assert "step_1" in content, "Step 1 should exist after second save"
        assert "step_2" in content, "Step 2 should exist"
        assert content["step_1"] == {"initial": "data"}, \
            "Step 1 data should not be corrupted"
        assert content["step_2"] == {"second": "step"}, \
            "Step 2 data should be correct"

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_invalid_json_handled(self, tmp_path):
        """
        P1: Verify load() handles corrupted JSON gracefully.

        AAA Pattern:
        1. Arrange - Create file with invalid JSON
        2. Act - Load state
        3. Assert - Returns empty dict without crashing
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        with open(state_file, "w") as f:
            f.write("{invalid json content")
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.load()

        # Assert
        assert result == {}, \
            f"Corrupted JSON should return empty dict, got {result}"


# ============================================================================
# CLEAR METHOD TESTS
# ============================================================================

class TestStateManagerClear:
    """
    Tests for clear() method.

    Verifies state file removal for test isolation.
    """

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_clear_removes_state(self, tmp_path):
        """
        P1: Verify clear() removes the state file.

        AAA Pattern:
        1. Arrange - Create state file with data
        2. Act - Call clear()
        3. Assert - File removed, load returns empty
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        manager = StateManager(state_file=str(state_file))
        manager.save(step=1, data={"test": "data"})
        assert state_file.exists(), "Precondition: file should exist"

        # Act
        manager.clear()

        # Assert
        assert not state_file.exists(), "State file should be removed"
        assert manager.load() == {}, "Load after clear should return empty dict"


# ============================================================================
# DEFAULT PATH TESTS
# ============================================================================

class TestStateManagerDefaultPath:
    """
    Tests for default state file path behavior.

    Verifies StateManager uses correct default path when None provided.
    """

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_default_state_file_path(self):
        """
        P1: Verify StateManager uses default path when None provided.

        AAA Pattern:
        1. Arrange - N/A (testing default behavior)
        2. Act - Create StateManager with state_file=None
        3. Assert - Path contains expected components
        """
        # Arrange
        # (no setup needed - testing default behavior)

        # Act
        manager = StateManager(state_file=None)

        # Assert
        assert manager._state_file is not None, \
            "Default path should be set"
        assert "workflow_state.json" in str(manager._state_file), \
            "Default path should contain workflow_state.json"
        assert "state" in str(manager._state_file), \
            "Default path should be in state directory"


# ============================================================================
# WRITE ERROR TESTS
# ============================================================================

class TestStateManagerWriteErrors:
    """
    Tests for error handling during write operations.

    Verifies:
    - Invalid paths raise exceptions
    - Temp files cleaned up on failure
    """

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_save_to_readonly_location_raises(self, tmp_path):
        """
        P2: Verify save() to invalid location raises exception.

        AAA Pattern:
        1. Arrange - Create manager with invalid path
        2. Act - Attempt to save
        3. Assert - Exception raised
        """
        # Arrange
        invalid_path = "/nonexistent/path/that/cannot/exist/state.json"
        if os.name == 'nt':
            invalid_path = "Z:\\nonexistent\\path\\state.json"
        manager = StateManager(state_file=invalid_path)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            manager.save(step=1, data={"test": "data"})
        assert exc_info.value is not None, "Should raise exception for invalid path"

    @pytest.mark.unit
    @pytest.mark.state_manager
    def test_save_cleans_up_temp_file_on_rename_failure(self, tmp_path):
        """
        P2: Verify temp file is cleaned up if rename fails.

        AAA Pattern:
        1. Arrange - Create manager, mock os.rename to fail
        2. Act - Attempt save (will fail on rename)
        3. Assert - No temp files left behind
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        manager = StateManager(state_file=str(state_file))

        def failing_rename(src, dst):
            assert os.path.exists(src), "Temp file should exist before rename"
            raise OSError("Simulated rename failure")

        # Act
        with patch('os.rename', side_effect=failing_rename):
            with pytest.raises(OSError):
                manager.save(step=1, data={"test": "data"})

        # Assert
        temp_files = list(tmp_path.glob("*.tmp"))
        assert len(temp_files) == 0, \
            f"Temp files should be cleaned up on failure, found {temp_files}"

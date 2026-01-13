"""
Unit tests for StateManager Step 11 Support - Task 58.0

Test suite for 11-step workflow extension.

Test Matrix:
- Happy path: 3 tests (P0) - step 11 save/get/is_complete
- Backward compatibility: 1 test (P0) - old 10-step state files readable
- Boundary: 2 tests (P1) - step 11 as boundary, step 12 invalid

Testing Skill Reference: .claude/skills/testing/
"""

import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.state_manager import StateManager, VALID_STEPS


# ============================================================================
# HAPPY PATH TESTS - STEP 11 SUPPORT
# ============================================================================

class TestStateManagerStep11Support:
    """
    Happy path tests for Step 11 support.

    Verifies 11-step workflow extension works correctly:
    - save() accepts step 11
    - get_step() returns step 11 data
    - is_step_complete() works for step 11
    """

    @pytest.mark.unit
    @pytest.mark.state_manager
    @pytest.mark.step11
    def test_save_step_11_succeeds(self, tmp_path):
        """
        P0: Verify save() accepts step 11 and creates state file.

        AAA Pattern:
        1. Arrange - Create StateManager with temp path
        2. Act - Save step 11 data
        3. Assert - File exists with step 11 content
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        manager = StateManager(state_file=str(state_file))

        # Act
        manager.save(step=11, data={"test_execution": "passed", "test_path": "tests/test_example.py"})

        # Assert
        assert state_file.exists(), "State file should be created after save()"
        with open(state_file) as f:
            content = json.load(f)
        assert "step_11" in content, "State should contain step_11 key"
        assert content["step_11"]["test_execution"] == "passed", \
            "Step 11 data should match saved values"

    @pytest.mark.unit
    @pytest.mark.state_manager
    @pytest.mark.step11
    def test_get_step_11_returns_data(self, tmp_path):
        """
        P0: Verify get_step(11) returns step 11 data.

        AAA Pattern:
        1. Arrange - Create state file with step 11 data
        2. Act - Get step 11 data
        3. Assert - Returns correct step 11 data
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        initial_state = {
            "step_10": {"pom_code": "...", "task_code": "..."},
            "step_11": {"test_execution": "passed", "report_path": "tests/_reports/report.html"}
        }
        with open(state_file, "w") as f:
            json.dump(initial_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.get_step(11)

        # Assert
        assert result == {"test_execution": "passed", "report_path": "tests/_reports/report.html"}, \
            f"get_step(11) should return step_11 data, got {result}"

    @pytest.mark.unit
    @pytest.mark.state_manager
    @pytest.mark.step11
    def test_is_step_complete_11_returns_true(self, tmp_path):
        """
        P0: Verify is_step_complete(11) returns True when step 11 exists with data.

        AAA Pattern:
        1. Arrange - Create state file with step 11 data
        2. Act - Check if step 11 is complete
        3. Assert - Returns True
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        initial_state = {"step_11": {"test_execution": "passed"}}
        with open(state_file, "w") as f:
            json.dump(initial_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.is_step_complete(11)

        # Assert
        assert result is True, "Step 11 should be marked complete when data exists"


# ============================================================================
# BACKWARD COMPATIBILITY TESTS
# ============================================================================

class TestStateManagerBackwardCompatibility:
    """
    Backward compatibility tests for Step 11 extension.

    Verifies old 10-step state files remain valid:
    - Old state files (steps 1-10) still readable
    - Step 11 can be added to existing 10-step state
    """

    @pytest.mark.unit
    @pytest.mark.state_manager
    @pytest.mark.step11
    def test_old_10_step_state_readable(self, tmp_path):
        """
        P0: Verify old 10-step state files are still readable.

        AAA Pattern:
        1. Arrange - Create state file with only steps 1-10 (old format)
        2. Act - Load state and get existing steps
        3. Assert - All 10 steps readable, step 11 returns None (not present)
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        old_state = {
            "step_1": {"credential_strategy": "static"},
            "step_2": {"persona": "registered user"},
            "step_3": {"bdd_scenarios": [{"given": "...", "when": "...", "then": "..."}]},
            "step_4": {"test_scenarios": [{"name": "test_login"}]},
            "step_5": {"elements": [{"name": "email_input"}]},
            "step_6": {"pom_metadata": {"class_name": "LoginPage"}},
            "step_7": {"task_metadata": {"class_name": "AuthTasks"}},
            "step_8": {"role_metadata": {"class_name": "RegisteredUser"}},
            "step_9": {"test_code": "def test_login(): ..."},
            "step_10": {"code_validation": "passed"}
        }
        with open(state_file, "w") as f:
            json.dump(old_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        loaded_state = manager.load()
        step_1_data = manager.get_step(1)
        step_10_data = manager.get_step(10)
        step_11_data = manager.get_step(11)

        # Assert
        assert loaded_state == old_state, "Old state should load without modification"
        assert step_1_data == {"credential_strategy": "static"}, \
            "Step 1 from old state should be accessible"
        assert step_10_data == {"code_validation": "passed"}, \
            "Step 10 from old state should be accessible"
        assert step_11_data is None, \
            "Step 11 should return None when not present in old state"

    @pytest.mark.unit
    @pytest.mark.state_manager
    @pytest.mark.step11
    def test_step_11_can_extend_old_state(self, tmp_path):
        """
        P1: Verify step 11 can be added to existing 10-step state.

        AAA Pattern:
        1. Arrange - Create state file with steps 1-10 (old format)
        2. Act - Add step 11 to existing state
        3. Assert - All 11 steps now present, no data loss
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        old_state = {
            "step_1": {"credential_strategy": "static"},
            "step_10": {"code_validation": "passed"}
        }
        with open(state_file, "w") as f:
            json.dump(old_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        manager.save(step=11, data={"test_execution": "passed"})

        # Assert
        loaded_state = manager.load()
        assert "step_1" in loaded_state, "Step 1 should still exist"
        assert "step_10" in loaded_state, "Step 10 should still exist"
        assert "step_11" in loaded_state, "Step 11 should be added"
        assert loaded_state["step_1"] == {"credential_strategy": "static"}, \
            "Step 1 data should not be corrupted"
        assert loaded_state["step_10"] == {"code_validation": "passed"}, \
            "Step 10 data should not be corrupted"
        assert loaded_state["step_11"] == {"test_execution": "passed"}, \
            "Step 11 data should be saved correctly"


# ============================================================================
# BOUNDARY TESTS
# ============================================================================

class TestStateManagerStep11Boundary:
    """
    Boundary tests for Step 11 extension.

    Verifies:
    - Step 11 is the new upper boundary
    - Step 12 is invalid (beyond range)
    """

    @pytest.mark.unit
    @pytest.mark.state_manager
    @pytest.mark.step11
    def test_step_11_is_valid_boundary(self, tmp_path):
        """
        P1: Verify step 11 is the new valid upper boundary.

        AAA Pattern:
        1. Arrange - Create state with step 11 data
        2. Act - Request step 11
        3. Assert - Returns step 11 data (valid boundary)
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        initial_state = {"step_11": {"boundary": "test"}}
        with open(state_file, "w") as f:
            json.dump(initial_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.get_step(11)

        # Assert
        assert result == {"boundary": "test"}, \
            f"Step 11 should be valid upper boundary, got {result}"

    @pytest.mark.unit
    @pytest.mark.state_manager
    @pytest.mark.step11
    def test_step_12_invalid(self, tmp_path):
        """
        P1: Verify step 12 returns None (beyond valid range 1-11).

        AAA Pattern:
        1. Arrange - Create state with step_12 key (should not be valid)
        2. Act - Request step 12
        3. Assert - Returns None (invalid step beyond boundary)
        """
        # Arrange
        state_file = tmp_path / "workflow_state.json"
        initial_state = {"step_12": {"should": "not exist"}}
        with open(state_file, "w") as f:
            json.dump(initial_state, f)
        manager = StateManager(state_file=str(state_file))

        # Act
        result = manager.get_step(12)

        # Assert
        assert result is None, \
            "Step 12 is invalid (beyond 1-11 range) - should return None even if key exists"


# ============================================================================
# VALID_STEPS CONSTANT VERIFICATION
# ============================================================================

class TestValidStepsConstant:
    """
    Verify VALID_STEPS constant updated correctly.

    Ensures:
    - VALID_STEPS includes step 11
    - VALID_STEPS excludes step 12
    """

    @pytest.mark.unit
    @pytest.mark.state_manager
    @pytest.mark.step11
    def test_valid_steps_includes_11(self):
        """
        P0: Verify VALID_STEPS constant includes step 11.

        AAA Pattern:
        1. Arrange - N/A (testing module constant)
        2. Act - Check if 11 in VALID_STEPS
        3. Assert - Step 11 is in range
        """
        # Act & Assert
        assert 11 in VALID_STEPS, \
            f"VALID_STEPS should include 11, got range: {VALID_STEPS.start} to {VALID_STEPS.stop - 1}"

    @pytest.mark.unit
    @pytest.mark.state_manager
    @pytest.mark.step11
    def test_valid_steps_excludes_12(self):
        """
        P0: Verify VALID_STEPS constant excludes step 12.

        AAA Pattern:
        1. Arrange - N/A (testing module constant)
        2. Act - Check if 12 not in VALID_STEPS
        3. Assert - Step 12 is not in range
        """
        # Act & Assert
        assert 12 not in VALID_STEPS, \
            f"VALID_STEPS should exclude 12, got range: {VALID_STEPS.start} to {VALID_STEPS.stop - 1}"

    @pytest.mark.unit
    @pytest.mark.state_manager
    @pytest.mark.step11
    def test_valid_steps_range_is_1_to_11(self):
        """
        P0: Verify VALID_STEPS is exactly range(1, 12) (1-11 inclusive).

        AAA Pattern:
        1. Arrange - N/A (testing module constant)
        2. Act - Check VALID_STEPS start and stop
        3. Assert - Range is 1-11 inclusive
        """
        # Act & Assert
        assert VALID_STEPS.start == 1, \
            f"VALID_STEPS should start at 1, got {VALID_STEPS.start}"
        assert VALID_STEPS.stop == 12, \
            f"VALID_STEPS should stop at 12 (11 inclusive), got {VALID_STEPS.stop}"
        assert list(VALID_STEPS) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], \
            f"VALID_STEPS should be [1-11], got {list(VALID_STEPS)}"

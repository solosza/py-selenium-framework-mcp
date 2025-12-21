"""
Unit tests for qg_ai_processing - Task 6.0

Test Matrix:
- Happy path: 5 tests (P0)
- Negative: 7 tests (P0)
- Edge cases: 3 tests (P1)
- Error handling: 2 tests (P0)
- Integration: 1 test (P0)

Testing Skill Reference: .claude/skills/testing/

DD Coverage:
- DD-03: BDD scenarios validation (Given/When/Then structure)
- DD-09: expected_states validation (derived from "Then" clauses)
"""

import pytest
from unittest.mock import patch, MagicMock

from tools.gates.qg_ai_processing import QGAIProcessing


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def valid_bdd_scenario():
    """Valid BDD scenario with Given/When/Then structure."""
    return {
        "given": "I am on the login page",
        "when": ["I enter valid email", "I enter valid password", "I click login"],
        "then": ["I should see my account dashboard", "I should see logout link"]
    }


@pytest.fixture
def valid_input_data(valid_bdd_scenario):
    """Valid input data with all required fields."""
    return {
        "bdd_scenarios": [valid_bdd_scenario],
        "expected_states": ["is_on_dashboard", "is_logout_visible"],
        "intent": "login"
    }


# =============================================================================
# HAPPY PATH TESTS
# =============================================================================

class TestValidBDDScenarios:
    """
    Test suite for BDD scenario validation (DD-03).

    Tests organized by: valid scenario structures
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_valid_bdd_scenarios_passes(self, valid_input_data):
        """
        P0: Verify valid BDD scenarios pass validation.

        AAA Pattern:
        1. Arrange - Create input with valid BDD scenarios
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = valid_input_data

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Valid BDD scenarios should pass"


class TestValidExpectedStates:
    """
    Test suite for expected_states validation (DD-09).

    Tests organized by: valid expected states lists
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_valid_expected_states_passes(self, valid_input_data):
        """
        P0: Verify valid expected_states pass validation.

        AAA Pattern:
        1. Arrange - Create input with valid expected_states
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = valid_input_data

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Valid expected_states should pass"


class TestValidIntent:
    """
    Test suite for intent validation.

    Tests organized by: valid intent values
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_valid_intent_passes(self, valid_input_data):
        """
        P0: Verify valid intent passes validation.

        AAA Pattern:
        1. Arrange - Create input with valid intent
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = valid_input_data

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Valid intent should pass"


class TestMetadataContextBuilt:
    """
    Test suite for metadata_context construction.

    Tests organized by: metadata structure validation
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_metadata_context_built(self, valid_input_data):
        """
        P0: Verify metadata_context is built and included in response.

        AAA Pattern:
        1. Arrange - Create valid input data
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Response includes metadata_context
        """
        # Arrange
        input_data = valid_input_data

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Validation should pass"
        assert "metadata_context" in result, "Response should include metadata_context"
        assert "bdd_scenarios" in result["metadata_context"], "metadata_context should include bdd_scenarios"
        assert "expected_states" in result["metadata_context"], "metadata_context should include expected_states"
        assert "intent" in result["metadata_context"], "metadata_context should include intent"


class TestStateSavedOnPass:
    """
    Test suite for state persistence on pass.

    Tests organized by: state management
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_state_saved_on_pass(self, valid_input_data):
        """
        P0: Verify state is saved when validation passes.

        AAA Pattern:
        1. Arrange - Create valid input, mock StateManager
        2. Act - Call qg_ai_processing.validate()
        3. Assert - StateManager.save() was called with correct data
        """
        # Arrange
        input_data = valid_input_data

        # Act
        with patch('tools.gates.qg_ai_processing.StateManager') as MockStateManager:
            mock_instance = MagicMock()
            MockStateManager.return_value = mock_instance
            result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Validation should pass"
        mock_instance.save.assert_called_once()
        call_args = mock_instance.save.call_args
        assert call_args[1]["step"] == 3, "State should be saved for step 3"


# =============================================================================
# NEGATIVE TESTS
# =============================================================================

class TestMissingBDDScenarios:
    """
    Test suite for missing bdd_scenarios handling.

    Tests organized by: validation failures
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_missing_bdd_scenarios_fails(self):
        """
        P0: Verify missing bdd_scenarios fails validation.

        AAA Pattern:
        1. Arrange - Create input without bdd_scenarios
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Missing bdd_scenarios should fail"
        assert "bdd_scenarios" in result["error"], "Error should mention bdd_scenarios"


class TestBDDMissingGiven:
    """
    Test suite for BDD scenario missing 'given' clause.

    Tests organized by: BDD structure validation
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_bdd_missing_given_fails(self):
        """
        P0: Verify BDD scenario without 'given' fails validation.

        AAA Pattern:
        1. Arrange - Create BDD scenario without 'given'
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [{
                "when": ["I enter email"],
                "then": ["I should see dashboard"]
            }],
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "BDD without 'given' should fail"
        assert "given" in result["error"].lower(), "Error should mention 'given'"


class TestBDDMissingWhen:
    """
    Test suite for BDD scenario missing 'when' clause.

    Tests organized by: BDD structure validation
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_bdd_missing_when_fails(self):
        """
        P0: Verify BDD scenario without 'when' fails validation.

        AAA Pattern:
        1. Arrange - Create BDD scenario without 'when'
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [{
                "given": "I am on the login page",
                "then": ["I should see dashboard"]
            }],
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "BDD without 'when' should fail"
        assert "when" in result["error"].lower(), "Error should mention 'when'"


class TestBDDMissingThen:
    """
    Test suite for BDD scenario missing 'then' clause.

    Tests organized by: BDD structure validation
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_bdd_missing_then_fails(self):
        """
        P0: Verify BDD scenario without 'then' fails validation.

        AAA Pattern:
        1. Arrange - Create BDD scenario without 'then'
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [{
                "given": "I am on the login page",
                "when": ["I enter email", "I enter password"]
            }],
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "BDD without 'then' should fail"
        assert "then" in result["error"].lower(), "Error should mention 'then'"


class TestEmptyExpectedStates:
    """
    Test suite for empty expected_states handling.

    Tests organized by: DD-09 enforcement
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_empty_expected_states_fails(self, valid_bdd_scenario):
        """
        P0: Verify empty expected_states fails validation (DD-09).

        AAA Pattern:
        1. Arrange - Create input with empty expected_states
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [valid_bdd_scenario],
            "expected_states": [],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty expected_states should fail"
        assert "expected_states" in result["error"], "Error should mention expected_states"


class TestMissingIntent:
    """
    Test suite for missing intent handling.

    Tests organized by: validation failures
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_missing_intent_fails(self, valid_bdd_scenario):
        """
        P0: Verify missing intent fails validation.

        AAA Pattern:
        1. Arrange - Create input without intent
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [valid_bdd_scenario],
            "expected_states": ["is_on_dashboard"]
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Missing intent should fail"
        assert "intent" in result["error"], "Error should mention intent"


class TestNoStateSavedOnFail:
    """
    Test suite for state NOT being saved on failure.

    Tests organized by: state management
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_no_state_saved_on_fail(self):
        """
        P0: Verify state is NOT saved when validation fails.

        AAA Pattern:
        1. Arrange - Create invalid input, mock StateManager
        2. Act - Call qg_ai_processing.validate()
        3. Assert - StateManager.save() was NOT called
        """
        # Arrange
        input_data = {
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
            # Missing bdd_scenarios
        }

        # Act
        with patch('tools.gates.qg_ai_processing.StateManager') as MockStateManager:
            mock_instance = MagicMock()
            MockStateManager.return_value = mock_instance
            result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Validation should fail"
        mock_instance.save.assert_not_called()


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestSingleExpectedState:
    """
    Test suite for single expected_state handling.

    Tests organized by: edge cases
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_single_expected_state(self, valid_bdd_scenario):
        """
        P1: Verify single expected_state is valid.

        AAA Pattern:
        1. Arrange - Create input with one expected_state
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [valid_bdd_scenario],
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Single expected_state should be valid"


class TestVeryLongIntent:
    """
    Test suite for very long intent handling.

    Tests organized by: edge cases
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_very_long_intent(self, valid_bdd_scenario):
        """
        P1: Verify very long intent is handled (but may be warned).

        AAA Pattern:
        1. Arrange - Create input with very long intent
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns pass or appropriate warning
        """
        # Arrange
        long_intent = "login_and_verify_dashboard_is_displayed_with_user_name_and_logout_link"
        input_data = {
            "bdd_scenarios": [valid_bdd_scenario],
            "expected_states": ["is_on_dashboard"],
            "intent": long_intent
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Very long intent should still pass"


class TestMultipleScenarios:
    """
    Test suite for multiple BDD scenarios handling.

    Tests organized by: edge cases
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_multiple_scenarios(self, valid_bdd_scenario):
        """
        P1: Verify multiple BDD scenarios are validated.

        AAA Pattern:
        1. Arrange - Create input with multiple scenarios
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        second_scenario = {
            "given": "I am logged in",
            "when": ["I click logout"],
            "then": ["I should see login page"]
        }
        input_data = {
            "bdd_scenarios": [valid_bdd_scenario, second_scenario],
            "expected_states": ["is_on_dashboard", "is_on_login_page"],
            "intent": "login_logout"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Multiple scenarios should pass"


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestFixHints:
    """
    Test suite for fix hints in error messages.

    Tests organized by: error handling
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_fix_hint_for_missing_bdd(self):
        """
        P0: Verify fix_hint is provided for missing bdd_scenarios.

        AAA Pattern:
        1. Arrange - Create input without bdd_scenarios
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Response includes fix_hint
        """
        # Arrange
        input_data = {
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Validation should fail"
        assert "fix_hint" in result, "Response should include fix_hint"
        assert len(result["fix_hint"]) > 0, "fix_hint should not be empty"

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_fix_hint_for_empty_states(self, valid_bdd_scenario):
        """
        P0: Verify fix_hint is provided for empty expected_states.

        AAA Pattern:
        1. Arrange - Create input with empty expected_states
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Response includes fix_hint
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [valid_bdd_scenario],
            "expected_states": [],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Validation should fail"
        assert "fix_hint" in result, "Response should include fix_hint"
        assert "expected_states" in result["fix_hint"].lower() or "then" in result["fix_hint"].lower(), \
            "fix_hint should mention expected_states or Then clauses"


# =============================================================================
# ADDITIONAL EDGE CASE TESTS FOR COVERAGE
# =============================================================================

class TestBDDScenariosEdgeCases:
    """
    Test suite for BDD scenarios edge cases.

    Tests organized by: edge case coverage
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_bdd_scenarios_not_a_list_fails(self):
        """
        P1: Verify bdd_scenarios as non-list fails validation.

        AAA Pattern:
        1. Arrange - Create input with bdd_scenarios as string
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": "not a list",
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "bdd_scenarios as string should fail"

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_bdd_scenarios_empty_list_fails(self):
        """
        P1: Verify empty bdd_scenarios list fails validation.

        AAA Pattern:
        1. Arrange - Create input with empty bdd_scenarios list
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [],
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty bdd_scenarios list should fail"

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_bdd_scenario_not_a_dict_fails(self):
        """
        P1: Verify bdd_scenario as non-dict fails validation.

        AAA Pattern:
        1. Arrange - Create input with scenario as string
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": ["not a dict"],
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Scenario as string should fail"

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_bdd_empty_given_string_fails(self):
        """
        P1: Verify empty given string fails validation.

        AAA Pattern:
        1. Arrange - Create scenario with empty given
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [{
                "given": "   ",
                "when": ["I click login"],
                "then": ["I see dashboard"]
            }],
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty given string should fail"

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_bdd_empty_when_list_fails(self):
        """
        P1: Verify empty when list fails validation.

        AAA Pattern:
        1. Arrange - Create scenario with empty when list
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [{
                "given": "I am on login page",
                "when": [],
                "then": ["I see dashboard"]
            }],
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty when list should fail"

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_bdd_empty_then_list_fails(self):
        """
        P1: Verify empty then list fails validation.

        AAA Pattern:
        1. Arrange - Create scenario with empty then list
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [{
                "given": "I am on login page",
                "when": ["I click login"],
                "then": []
            }],
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty then list should fail"


class TestExpectedStatesEdgeCases:
    """
    Test suite for expected_states edge cases.

    Tests organized by: edge case coverage
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_expected_states_not_a_list_fails(self, valid_bdd_scenario):
        """
        P1: Verify expected_states as non-list fails validation.

        AAA Pattern:
        1. Arrange - Create input with expected_states as string
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [valid_bdd_scenario],
            "expected_states": "not a list",
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "expected_states as string should fail"

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_expected_states_with_empty_string_fails(self, valid_bdd_scenario):
        """
        P1: Verify expected_states containing empty string fails validation.

        AAA Pattern:
        1. Arrange - Create input with empty string in expected_states
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [valid_bdd_scenario],
            "expected_states": ["is_on_dashboard", "   "],
            "intent": "login"
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "expected_states with empty string should fail"


class TestIntentEdgeCases:
    """
    Test suite for intent edge cases.

    Tests organized by: edge case coverage
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_empty_intent_string_fails(self, valid_bdd_scenario):
        """
        P1: Verify empty intent string fails validation.

        AAA Pattern:
        1. Arrange - Create input with empty intent
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "bdd_scenarios": [valid_bdd_scenario],
            "expected_states": ["is_on_dashboard"],
            "intent": "   "
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty intent string should fail"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """
    Test suite for integration with workflow.

    Tests organized by: step blocking
    """

    @pytest.mark.unit
    @pytest.mark.qg_ai_processing
    def test_blocks_step_4_on_fail(self):
        """
        P0: Verify failed validation blocks Step 4 progression.

        AAA Pattern:
        1. Arrange - Create invalid input
        2. Act - Call qg_ai_processing.validate()
        3. Assert - Returns fail status (blocking Step 4)
        """
        # Arrange
        input_data = {
            "expected_states": ["is_on_dashboard"],
            "intent": "login"
            # Missing bdd_scenarios
        }

        # Act
        result = QGAIProcessing.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Invalid input should block Step 4"
        assert "error" in result, "Response should include error message"

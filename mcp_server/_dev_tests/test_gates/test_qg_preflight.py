"""
Unit tests for qg_preflight - Task 4.0

Test Matrix:
- Happy path: 10 tests (P0)
- Negative: 6 tests (P0)
- Edge cases: 3 tests (P1)
- Error handling: 1 test (P0)

Testing Skill Reference: .claude/skills/testing/

DD Coverage:
- DD-24: Credential strategy validation
- DD-28: Test data location validation
"""

import pytest
from unittest.mock import patch, MagicMock

from tools.gates.qg_preflight import QGPreflight


class TestValidCredentialStrategy:
    """
    Test suite for credential_strategy validation (DD-24).

    Tests organized by: valid strategy values
    """

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_credential_strategy_static(self):
        """
        P0: Verify 'static' credential strategy passes validation.

        AAA Pattern:
        1. Arrange - Create input with 'static' strategy
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Static credential strategy should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_credential_strategy_dynamic(self):
        """
        P0: Verify 'dynamic' credential strategy passes validation.

        AAA Pattern:
        1. Arrange - Create input with 'dynamic' strategy
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "credential_strategy": "dynamic",
            "test_data_location": "shared"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Dynamic credential strategy should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_credential_strategy_self_contained(self):
        """
        P0: Verify 'self-contained' credential strategy passes validation.

        AAA Pattern:
        1. Arrange - Create input with 'self-contained' strategy
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "credential_strategy": "self-contained",
            "test_data_location": "shared"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Self-contained credential strategy should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_credential_strategy_none(self):
        """
        P0: Verify 'none' credential strategy passes validation.

        AAA Pattern:
        1. Arrange - Create input with 'none' strategy
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "credential_strategy": "none",
            "test_data_location": "shared"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "None credential strategy should pass"


class TestValidTestDataLocation:
    """
    Test suite for test_data_location validation (DD-28).

    Tests organized by: valid location values
    """

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_test_data_location_shared(self):
        """
        P0: Verify 'shared' test data location passes validation.

        AAA Pattern:
        1. Arrange - Create input with 'shared' location
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Shared test data location should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_test_data_location_workflow(self):
        """
        P0: Verify 'workflow' test data location passes validation.

        AAA Pattern:
        1. Arrange - Create input with 'workflow' location
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "workflow"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Workflow test data location should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_test_data_location_both(self):
        """
        P0: Verify 'both' test data location passes validation.

        AAA Pattern:
        1. Arrange - Create input with 'both' location
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "both"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Both test data location should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_test_data_location_none(self):
        """
        P0: Verify 'none' test data location passes validation.

        AAA Pattern:
        1. Arrange - Create input with 'none' location
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "none"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "None test data location should pass"


class TestBothFieldsValid:
    """
    Test suite for combined validation.

    Tests organized by: pass behavior
    """

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_both_fields_valid_passes(self):
        """
        P0: Verify both valid fields together pass validation.

        AAA Pattern:
        1. Arrange - Create input with both fields valid
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "credential_strategy": "dynamic",
            "test_data_location": "both"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Both valid fields should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_state_saved_on_pass(self):
        """
        P0: Verify state is saved when validation passes.

        AAA Pattern:
        1. Arrange - Create valid input, mock state_manager
        2. Act - Call qg_preflight.validate()
        3. Assert - state_manager.save() called with correct data
        """
        # Arrange
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared"
        }

        # Act
        with patch('tools.gates.qg_preflight.StateManager') as MockStateManager:
            mock_instance = MagicMock()
            MockStateManager.return_value = mock_instance
            result = QGPreflight.validate(input_data)

            # Assert
            assert result["status"] == "pass", "Validation should pass"
            mock_instance.save.assert_called_once()
            call_kwargs = mock_instance.save.call_args.kwargs
            assert call_kwargs["step"] == 1, "Should save to step 1"
            assert "credential_strategy" in call_kwargs["data"], "Should include credential_strategy"
            assert "test_data_location" in call_kwargs["data"], "Should include test_data_location"


class TestInvalidInputs:
    """
    Test suite for invalid input validation.

    Tests organized by: failure type
    """

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_invalid_credential_strategy_fails(self):
        """
        P0: Verify invalid credential strategy fails validation.

        AAA Pattern:
        1. Arrange - Create input with invalid strategy
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "credential_strategy": "invalid_strategy",
            "test_data_location": "shared"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Invalid credential strategy should fail"
        assert "error" in result, "Should include error message"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_invalid_test_data_location_fails(self):
        """
        P0: Verify invalid test data location fails validation.

        AAA Pattern:
        1. Arrange - Create input with invalid location
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "invalid_location"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Invalid test data location should fail"
        assert "error" in result, "Should include error message"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_missing_credential_strategy_fails(self):
        """
        P0: Verify missing credential strategy fails validation.

        AAA Pattern:
        1. Arrange - Create input without credential_strategy
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "test_data_location": "shared"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Missing credential strategy should fail"
        assert "error" in result, "Should include error message"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_missing_test_data_location_fails(self):
        """
        P0: Verify missing test data location fails validation.

        AAA Pattern:
        1. Arrange - Create input without test_data_location
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "credential_strategy": "static"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Missing test data location should fail"
        assert "error" in result, "Should include error message"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_both_invalid_fails(self):
        """
        P0: Verify both invalid fields fail validation.

        AAA Pattern:
        1. Arrange - Create input with both fields invalid
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "credential_strategy": "bad_strategy",
            "test_data_location": "bad_location"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Both invalid fields should fail"
        assert "error" in result, "Should include error message"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_no_state_saved_on_fail(self):
        """
        P0: Verify state is NOT saved when validation fails.

        AAA Pattern:
        1. Arrange - Create invalid input, mock state_manager
        2. Act - Call qg_preflight.validate()
        3. Assert - state_manager.save() NOT called
        """
        # Arrange
        input_data = {
            "credential_strategy": "invalid",
            "test_data_location": "shared"
        }

        # Act
        with patch('tools.gates.qg_preflight.StateManager') as MockStateManager:
            mock_instance = MagicMock()
            MockStateManager.return_value = mock_instance
            result = QGPreflight.validate(input_data)

            # Assert
            assert result["status"] == "fail", "Validation should fail"
            mock_instance.save.assert_not_called()


class TestEdgeCases:
    """
    Test suite for edge case validation.

    Tests organized by: edge case type
    """

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_empty_string_credential_strategy(self):
        """
        P1: Verify empty string credential strategy fails validation.

        AAA Pattern:
        1. Arrange - Create input with empty string strategy
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "credential_strategy": "",
            "test_data_location": "shared"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty string credential strategy should fail"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_null_value_handled(self):
        """
        P1: Verify None values are handled as failures.

        AAA Pattern:
        1. Arrange - Create input with None value
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "credential_strategy": None,
            "test_data_location": "shared"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "None value should fail"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_case_sensitivity(self):
        """
        P1: Verify case sensitivity is enforced.

        AAA Pattern:
        1. Arrange - Create input with uppercase value
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns fail status (case sensitive)
        """
        # Arrange
        input_data = {
            "credential_strategy": "STATIC",
            "test_data_location": "shared"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Uppercase value should fail (case sensitive)"


class TestErrorHandling:
    """
    Test suite for error handling and fix hints.

    Tests organized by: error response format
    """

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_fix_hint_provided_on_fail(self):
        """
        P0: Verify fix_hint is provided on validation failure.

        AAA Pattern:
        1. Arrange - Create invalid input
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns fix_hint in response
        """
        # Arrange
        input_data = {
            "credential_strategy": "invalid",
            "test_data_location": "shared"
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail"
        assert "fix_hint" in result, "Should include fix_hint"
        assert len(result["fix_hint"]) > 0, "fix_hint should not be empty"

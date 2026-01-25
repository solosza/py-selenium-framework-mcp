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
    def test_valid_credential_strategy_static(self, mock_pre_check):
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
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        # Mock infrastructure exists so scaffolding doesn't trigger
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            MockPath.return_value = mock_path
            result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Static credential strategy should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_credential_strategy_dynamic(self, mock_pre_check):
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
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            MockPath.return_value = mock_path
            result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Dynamic credential strategy should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_credential_strategy_self_contained(self, mock_pre_check):
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
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            MockPath.return_value = mock_path
            result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Self-contained credential strategy should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_credential_strategy_none(self, mock_pre_check):
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
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            MockPath.return_value = mock_path
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
    def test_valid_test_data_location_shared(self, mock_pre_check):
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
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            MockPath.return_value = mock_path
            result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Shared test data location should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_test_data_location_workflow(self, mock_pre_check):
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
            "test_data_location": "workflow",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            MockPath.return_value = mock_path
            result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Workflow test data location should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_test_data_location_both(self, mock_pre_check):
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
            "test_data_location": "both",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            MockPath.return_value = mock_path
            result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Both test data location should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_valid_test_data_location_none(self, mock_pre_check):
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
            "test_data_location": "none",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            MockPath.return_value = mock_path
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
    def test_both_fields_valid_passes(self, mock_pre_check):
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
            "test_data_location": "both",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            MockPath.return_value = mock_path
            result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Both valid fields should pass"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_state_saved_on_pass(self, mock_pre_check):
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
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        # Mock StateManager in utils.state_manager where base_gate imports it
        with patch('utils.state_manager.StateManager') as MockStateManager:
            with patch('tools.gates.qg_preflight.Path') as MockPath:
                # Mock infrastructure exists
                mock_path = MagicMock()
                mock_path.exists.return_value = True
                MockPath.return_value = mock_path

                mock_instance = MagicMock()
                MockStateManager.return_value = mock_instance
                result = QGPreflight.validate(input_data)

                # Assert
                assert result["status"] == "pass", "Validation should pass"
                mock_instance.save.assert_called_once()
                call_kwargs = mock_instance.save.call_args.kwargs
                assert call_kwargs["step"] == 2, "Should save to step 2"
                assert "credential_strategy" in call_kwargs["data"], "Should include credential_strategy"
                assert "test_data_location" in call_kwargs["data"], "Should include test_data_location"


class TestInvalidInputs:
    """
    Test suite for invalid input validation.

    Tests organized by: failure type
    """

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_invalid_credential_strategy_fails(self, mock_pre_check):
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
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Invalid credential strategy should fail"
        assert "error" in result, "Should include error message"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_invalid_test_data_location_fails(self, mock_pre_check):
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
            "test_data_location": "invalid_location",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Invalid test data location should fail"
        assert "error" in result, "Should include error message"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_missing_credential_strategy_fails(self, mock_pre_check):
        """
        P0: Verify missing credential strategy fails validation.

        AAA Pattern:
        1. Arrange - Create input without credential_strategy
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Missing credential strategy should fail"
        assert "error" in result, "Should include error message"
        assert "credential_strategy" in result["error"], "Error should mention missing field"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_missing_test_data_location_fails(self, mock_pre_check):
        """
        P0: Verify missing test data location fails validation.

        AAA Pattern:
        1. Arrange - Create input without test_data_location
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "credential_strategy": "static",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Missing test data location should fail"
        assert "error" in result, "Should include error message"
        assert "test_data_location" in result["error"], "Error should mention missing field"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_both_invalid_fails(self, mock_pre_check):
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
            "test_data_location": "bad_location",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Both invalid fields should fail"
        assert "error" in result, "Should include error message"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_no_state_saved_on_fail(self, mock_pre_check):
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
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
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
    def test_empty_string_credential_strategy(self, mock_pre_check):
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
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty string credential strategy should fail"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_null_value_handled(self, mock_pre_check):
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
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "None value should fail"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_case_sensitivity(self, mock_pre_check):
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
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
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
    def test_teach_provided_on_fail(self, mock_pre_check):
        """
        P0: Verify teach is provided on validation failure.

        AAA Pattern:
        1. Arrange - Create invalid input
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns teach in response
        """
        # Arrange
        input_data = {
            "credential_strategy": "invalid",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail"
        assert "teach" in result, "Should include teach"
        assert len(result["teach"]) > 0, "teach should not be empty"


class TestScaffoldingInfrastructure:
    """
    Test suite for test data infrastructure scaffolding (DEF-060).

    Tests organized by: scaffolding scenarios
    """

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_returns_needs_retry_when_tests_data_missing(self, mock_pre_check):
        """
        P0: Verify NEEDS_RETRY returned when tests/data/ doesn't exist.

        AAA Pattern:
        1. Arrange - Mock Path.exists() to return False, input with 'static' strategy
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns NEEDS_RETRY with scaffolding instructions
        """
        # Arrange
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            # Mock tests/data directory doesn't exist
            mock_data_dir = MagicMock()
            mock_data_dir.exists.return_value = False

            # Mock tests/data/test_users.json doesn't exist
            mock_cred_file = MagicMock()
            mock_cred_file.exists.return_value = False

            # Setup Path() to return appropriate mocks
            def path_side_effect(path_str):
                if path_str == "tests/data":
                    return mock_data_dir
                elif path_str == "tests/data/test_users.json":
                    return mock_cred_file
                return MagicMock()

            MockPath.side_effect = path_side_effect

            result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "NEEDS_RETRY", "Should return NEEDS_RETRY when infrastructure missing"
        assert "scaffolding_needed" in result, "Should include scaffolding instructions"
        assert len(result["scaffolding_needed"]) > 0, "Should have at least one scaffolding item"

        # Verify scaffolding instructions include directory and file
        paths = [item["path"] for item in result["scaffolding_needed"]]
        assert "tests/data" in paths, "Should include tests/data directory"
        assert "tests/data/test_users.json" in paths, "Should include credential file"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_creates_credential_file_for_static_strategy(self, mock_pre_check):
        """
        P0: Verify credential file scaffolding for 'static' strategy.

        AAA Pattern:
        1. Arrange - Mock directory exists, file doesn't, input with 'static' strategy
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns NEEDS_RETRY with credential file template
        """
        # Arrange
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            # Mock tests/data directory exists
            mock_data_dir = MagicMock()
            mock_data_dir.exists.return_value = True

            # Mock tests/data/test_users.json doesn't exist
            mock_cred_file = MagicMock()
            mock_cred_file.exists.return_value = False

            def path_side_effect(path_str):
                if path_str == "tests/data":
                    return mock_data_dir
                elif path_str == "tests/data/test_users.json":
                    return mock_cred_file
                return MagicMock()

            MockPath.side_effect = path_side_effect

            result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "NEEDS_RETRY", "Should return NEEDS_RETRY"
        assert "scaffolding_needed" in result, "Should include scaffolding"

        # Find credential file in scaffolding
        cred_file_item = next((item for item in result["scaffolding_needed"]
                               if item["path"] == "tests/data/test_users.json"), None)

        assert cred_file_item is not None, "Should include credential file"
        assert "template" in cred_file_item, "Should include JSON template"
        assert "default_user" in cred_file_item["template"], "Template should have default_user key"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_creates_credential_file_for_dynamic_strategy(self, mock_pre_check):
        """
        P0: Verify credential file scaffolding for 'dynamic' strategy.

        AAA Pattern:
        1. Arrange - Input with 'dynamic' strategy, mock file doesn't exist
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns NEEDS_RETRY with credential file
        """
        # Arrange
        input_data = {
            "credential_strategy": "dynamic",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            mock_data_dir = MagicMock()
            mock_data_dir.exists.return_value = True

            mock_cred_file = MagicMock()
            mock_cred_file.exists.return_value = False

            def path_side_effect(path_str):
                if path_str == "tests/data":
                    return mock_data_dir
                elif path_str == "tests/data/test_users.json":
                    return mock_cred_file
                return MagicMock()

            MockPath.side_effect = path_side_effect

            result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "NEEDS_RETRY", "Should return NEEDS_RETRY for dynamic strategy"
        paths = [item["path"] for item in result["scaffolding_needed"]]
        assert "tests/data/test_users.json" in paths, "Should include credential file for dynamic"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_no_credential_file_for_self_contained(self, mock_pre_check):
        """
        P1: Verify no credential file for 'self-contained' strategy.

        AAA Pattern:
        1. Arrange - Input with 'self-contained' strategy, mock directory doesn't exist
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns NEEDS_RETRY with directory only, NO credential file
        """
        # Arrange
        input_data = {
            "credential_strategy": "self-contained",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            # Mock tests/data directory doesn't exist
            mock_data_dir = MagicMock()
            mock_data_dir.exists.return_value = False

            def path_side_effect(path_str):
                if path_str == "tests/data":
                    return mock_data_dir
                return MagicMock()

            MockPath.side_effect = path_side_effect

            result = QGPreflight.validate(input_data)

        # Assert
        if result["status"] == "NEEDS_RETRY":
            paths = [item["path"] for item in result["scaffolding_needed"]]
            assert "tests/data" in paths, "Should include directory"
            assert "tests/data/test_users.json" not in paths, \
                "Should NOT include credential file for self-contained"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_no_credential_file_for_none_strategy(self, mock_pre_check):
        """
        P1: Verify no credential file for 'none' strategy.

        AAA Pattern:
        1. Arrange - Input with 'none' strategy, mock directory doesn't exist
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns NEEDS_RETRY with directory only, NO credential file
        """
        # Arrange
        input_data = {
            "credential_strategy": "none",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            # Mock tests/data directory doesn't exist
            mock_data_dir = MagicMock()
            mock_data_dir.exists.return_value = False

            def path_side_effect(path_str):
                if path_str == "tests/data":
                    return mock_data_dir
                return MagicMock()

            MockPath.side_effect = path_side_effect

            result = QGPreflight.validate(input_data)

        # Assert
        if result["status"] == "NEEDS_RETRY":
            paths = [item["path"] for item in result["scaffolding_needed"]]
            assert "tests/data/test_users.json" not in paths, \
                "Should NOT include credential file for none strategy"

    @pytest.mark.unit
    @pytest.mark.qg_preflight
    def test_no_needs_retry_when_infrastructure_exists(self, mock_pre_check):
        """
        P0: Verify no NEEDS_RETRY when infrastructure already exists.

        AAA Pattern:
        1. Arrange - Mock all files/directories exist, valid input
        2. Act - Call qg_preflight.validate()
        3. Assert - Returns pass status (no NEEDS_RETRY)
        """
        # Arrange
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        # Act
        with patch('tools.gates.qg_preflight.Path') as MockPath:
            # Mock everything exists
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            MockPath.return_value = mock_path

            result = QGPreflight.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Should pass when infrastructure exists"
        assert "scaffolding_needed" not in result, "Should NOT include scaffolding when files exist"


# ==============================================================================
# Layer 1: Validation Helper Tests (Direct method testing)
# ==============================================================================

class TestLayer1CredentialStrategyHelper:
    """
    Layer 1: Direct tests for _is_valid_credential_strategy helper.

    Tests the validation logic in isolation.
    """

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_valid_static(self):
        """L1: 'static' is valid."""
        assert QGPreflight._is_valid_credential_strategy("static") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_valid_dynamic(self):
        """L1: 'dynamic' is valid."""
        assert QGPreflight._is_valid_credential_strategy("dynamic") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_valid_self_contained(self):
        """L1: 'self-contained' is valid."""
        assert QGPreflight._is_valid_credential_strategy("self-contained") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_valid_none(self):
        """L1: 'none' is valid."""
        assert QGPreflight._is_valid_credential_strategy("none") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_invalid_string(self):
        """L1: Invalid string is rejected."""
        assert QGPreflight._is_valid_credential_strategy("invalid") is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_none_value_rejected(self):
        """L1: None value is rejected."""
        assert QGPreflight._is_valid_credential_strategy(None) is False


class TestLayer1TestDataLocationHelper:
    """
    Layer 1: Direct tests for _is_valid_test_data_location helper.
    """

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_valid_shared(self):
        """L1: 'shared' is valid."""
        assert QGPreflight._is_valid_test_data_location("shared") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_valid_workflow(self):
        """L1: 'workflow' is valid."""
        assert QGPreflight._is_valid_test_data_location("workflow") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_valid_both(self):
        """L1: 'both' is valid."""
        assert QGPreflight._is_valid_test_data_location("both") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_valid_none(self):
        """L1: 'none' is valid."""
        assert QGPreflight._is_valid_test_data_location("none") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_invalid_string(self):
        """L1: Invalid string is rejected."""
        assert QGPreflight._is_valid_test_data_location("invalid") is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_none_value_rejected(self):
        """L1: None value is rejected."""
        assert QGPreflight._is_valid_test_data_location(None) is False


class TestLayer1BrowserConfigHelper:
    """
    Layer 1: Direct tests for _validate_browser_config helper.

    Returns None if valid, fail_response dict if invalid.
    """

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_valid_headless_false(self):
        """L1: headless=False is valid (required for pair programming)."""
        result = QGPreflight._validate_browser_config({"headless": False})
        assert result is None, "Valid config should return None"

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_invalid_headless_true(self):
        """L1: headless=True is rejected (pair programming requires visible browser)."""
        result = QGPreflight._validate_browser_config({"headless": True})
        assert result is not None, "headless=True should fail"
        assert result["status"] == "fail"

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_invalid_not_dict(self):
        """L1: Non-dict browser_config is rejected."""
        result = QGPreflight._validate_browser_config("not a dict")
        assert result is not None
        assert result["status"] == "fail"

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_invalid_missing_headless_key(self):
        """L1: Missing 'headless' key is rejected."""
        result = QGPreflight._validate_browser_config({})
        assert result is not None
        assert result["status"] == "fail"

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_valid_with_extra_keys(self):
        """L1: Extra keys in browser_config are allowed."""
        result = QGPreflight._validate_browser_config({
            "headless": False,
            "window_size": "1920x1080"
        })
        assert result is None, "Extra keys should be allowed"


class TestLayer1TimeoutConfigHelper:
    """
    Layer 1: Direct tests for _validate_timeout_config helper.
    """

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_valid_enabled_with_threshold(self):
        """L1: enabled=True with valid threshold is valid."""
        result = QGPreflight._validate_timeout_config({
            "enabled": True,
            "threshold_seconds": 30
        })
        assert result is None, "Valid config should return None"

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_valid_disabled_no_threshold(self):
        """L1: enabled=False without threshold is valid."""
        result = QGPreflight._validate_timeout_config({"enabled": False})
        assert result is None, "Disabled config doesn't need threshold"

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_invalid_not_dict(self):
        """L1: Non-dict timeout_config is rejected."""
        result = QGPreflight._validate_timeout_config("not a dict")
        assert result is not None
        assert result["status"] == "fail"

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_invalid_missing_enabled_key(self):
        """L1: Missing 'enabled' key is rejected."""
        result = QGPreflight._validate_timeout_config({"threshold_seconds": 30})
        assert result is not None
        assert result["status"] == "fail"

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_invalid_enabled_missing_threshold(self):
        """L1: enabled=True without threshold is rejected."""
        result = QGPreflight._validate_timeout_config({"enabled": True})
        assert result is not None
        assert result["status"] == "fail"

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.preflight
    def test_invalid_negative_threshold(self):
        """L1: Negative threshold is rejected."""
        result = QGPreflight._validate_timeout_config({
            "enabled": True,
            "threshold_seconds": -5
        })
        assert result is not None
        assert result["status"] == "fail"


# ==============================================================================
# Layer 2: Edge Case Tests
# ==============================================================================

class TestLayer2EdgeCases:
    """
    Layer 2: Edge case and boundary tests.
    """

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.preflight
    def test_empty_string_credential_strategy(self):
        """L2: Empty string credential_strategy is rejected."""
        assert QGPreflight._is_valid_credential_strategy("") is False

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.preflight
    def test_empty_string_test_data_location(self):
        """L2: Empty string test_data_location is rejected."""
        assert QGPreflight._is_valid_test_data_location("") is False

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.preflight
    def test_case_sensitivity_credential_strategy(self):
        """L2: Credential strategy is case-sensitive (STATIC != static)."""
        assert QGPreflight._is_valid_credential_strategy("STATIC") is False
        assert QGPreflight._is_valid_credential_strategy("Static") is False

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.preflight
    def test_case_sensitivity_test_data_location(self):
        """L2: Test data location is case-sensitive (SHARED != shared)."""
        assert QGPreflight._is_valid_test_data_location("SHARED") is False
        assert QGPreflight._is_valid_test_data_location("Shared") is False

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.preflight
    def test_threshold_zero_rejected(self):
        """L2: Zero threshold is rejected (must be positive)."""
        result = QGPreflight._validate_timeout_config({
            "enabled": True,
            "threshold_seconds": 0
        })
        assert result is not None
        assert result["status"] == "fail"

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.preflight
    def test_threshold_float_accepted(self):
        """L2: Float threshold is accepted."""
        result = QGPreflight._validate_timeout_config({
            "enabled": True,
            "threshold_seconds": 30.5
        })
        assert result is None, "Float threshold should be valid"

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.preflight
    def test_enabled_not_boolean_rejected(self):
        """L2: Non-boolean enabled is rejected."""
        result = QGPreflight._validate_timeout_config({
            "enabled": "true",  # string, not bool
            "threshold_seconds": 30
        })
        assert result is not None
        assert result["status"] == "fail"

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.preflight
    def test_headless_not_boolean_rejected(self):
        """L2: Non-boolean headless is rejected (string 'false')."""
        result = QGPreflight._validate_browser_config({"headless": "false"})
        assert result is not None
        assert result["status"] == "fail"


# ==============================================================================
# Task 3.0: Teach Content Validation Tests (DD-50 Smart Gate Pattern)
# ==============================================================================

class TestTeachContentValidation:
    """
    Task 3.0: Verify teach content provides actionable guidance.

    DD-50: Smart gates provide fix data, not just block.
    """

    @pytest.mark.unit
    @pytest.mark.preflight
    @pytest.mark.teach
    def test_response_uses_teach_key(self, mock_pre_check):
        """3.1: Gate response uses 'teach' key (not 'fix_hint')."""
        input_data = {
            "credential_strategy": "invalid",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        result = QGPreflight.validate(input_data)

        assert result["status"] == "fail"
        assert "teach" in result, "Response should use 'teach' key"
        assert "fix_hint" not in result, "Response should NOT use 'fix_hint' key"

    @pytest.mark.unit
    @pytest.mark.preflight
    @pytest.mark.teach
    def test_teach_credential_strategy_includes_valid_options(self, mock_pre_check):
        """3.2: Teach for invalid credential_strategy includes valid options list."""
        input_data = {
            "credential_strategy": "invalid",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        result = QGPreflight.validate(input_data)

        assert result["status"] == "fail"
        teach = result["teach"]
        # Should list all valid options
        assert "static" in teach, "Teach should mention 'static'"
        assert "dynamic" in teach, "Teach should mention 'dynamic'"
        assert "self-contained" in teach, "Teach should mention 'self-contained'"
        assert "none" in teach, "Teach should mention 'none'"

    @pytest.mark.unit
    @pytest.mark.preflight
    @pytest.mark.teach
    def test_teach_test_data_location_includes_valid_options(self, mock_pre_check):
        """3.3: Teach for invalid test_data_location includes valid options list."""
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "invalid",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        result = QGPreflight.validate(input_data)

        assert result["status"] == "fail"
        teach = result["teach"]
        # Should list all valid options
        assert "shared" in teach, "Teach should mention 'shared'"
        assert "workflow" in teach, "Teach should mention 'workflow'"
        assert "both" in teach, "Teach should mention 'both'"
        assert "none" in teach, "Teach should mention 'none'"

    @pytest.mark.unit
    @pytest.mark.preflight
    @pytest.mark.teach
    def test_teach_browser_config_explains_headless(self, mock_pre_check):
        """3.4: Teach for invalid browser_config explains headless requirement."""
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {"headless": True},  # Wrong - should be False
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        result = QGPreflight.validate(input_data)

        assert result["status"] == "fail"
        teach = result["teach"]
        assert "headless" in teach.lower(), "Teach should mention headless"
        assert "false" in teach.lower(), "Teach should mention false"

    @pytest.mark.unit
    @pytest.mark.preflight
    @pytest.mark.teach
    def test_teach_timeout_config_explains_threshold(self, mock_pre_check):
        """3.5: Teach for invalid timeout_config explains threshold requirement."""
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True}  # Missing threshold_seconds
        }

        result = QGPreflight.validate(input_data)

        assert result["status"] == "fail"
        teach = result["teach"]
        assert "threshold" in teach.lower(), "Teach should mention threshold"

    @pytest.mark.unit
    @pytest.mark.preflight
    @pytest.mark.teach
    def test_teach_includes_example_format(self, mock_pre_check):
        """3.6: Teach includes example of correct format."""
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {},  # Missing headless
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        result = QGPreflight.validate(input_data)

        assert result["status"] == "fail"
        teach = result["teach"]
        # Should show example format
        assert "{" in teach or ":" in teach, "Teach should include format example"

    @pytest.mark.unit
    @pytest.mark.preflight
    @pytest.mark.teach
    def test_teach_is_actionable(self, mock_pre_check):
        """3.7: Teach is actionable (contains directive language)."""
        input_data = {
            "credential_strategy": "invalid",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        result = QGPreflight.validate(input_data)

        assert result["status"] == "fail"
        teach = result["teach"].lower()
        # Should contain actionable language
        actionable = (
            "must be" in teach or
            "should be" in teach or
            "one of" in teach or
            "must" in teach
        )
        assert actionable, f"Teach should be actionable, got: {result['teach']}"


# ==============================================================================
# Task 4.0: State Integration Tests (FR-2.6)
# ==============================================================================

class TestStateIntegration:
    """
    Task 4.0: State integration tests for Step 2 gate.

    Verifies FR-2.6: State checkpoint on gate PASS.
    """

    @pytest.mark.integration
    @pytest.mark.preflight
    @pytest.mark.state
    def test_state_saved_with_all_config_fields(self, mock_pre_check):
        """4.1: State saved with all 4 config fields on gate PASS."""
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        with patch('utils.state_manager.StateManager') as MockStateManager:
            with patch('tools.gates.qg_preflight.Path') as MockPath:
                mock_path = MagicMock()
                mock_path.exists.return_value = True
                MockPath.return_value = mock_path

                mock_instance = MagicMock()
                MockStateManager.return_value = mock_instance

                result = QGPreflight.validate(input_data)

                assert result["status"] == "pass"
                mock_instance.save.assert_called_once()

                # Verify all 4 fields are in saved data
                call_kwargs = mock_instance.save.call_args.kwargs
                saved_data = call_kwargs["data"]
                assert "credential_strategy" in saved_data
                assert "test_data_location" in saved_data
                assert "browser_config" in saved_data
                assert "timeout_config" in saved_data

    @pytest.mark.integration
    @pytest.mark.preflight
    @pytest.mark.state
    def test_state_saved_to_step_2(self, mock_pre_check):
        """4.3: State saved with step=2."""
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        with patch('utils.state_manager.StateManager') as MockStateManager:
            with patch('tools.gates.qg_preflight.Path') as MockPath:
                mock_path = MagicMock()
                mock_path.exists.return_value = True
                MockPath.return_value = mock_path

                mock_instance = MagicMock()
                MockStateManager.return_value = mock_instance

                result = QGPreflight.validate(input_data)

                assert result["status"] == "pass"
                call_kwargs = mock_instance.save.call_args.kwargs
                assert call_kwargs["step"] == 2, "Should save to step 2"

    @pytest.mark.integration
    @pytest.mark.preflight
    @pytest.mark.state
    def test_state_includes_config_values(self, mock_pre_check):
        """4.4: State includes actual config values."""
        input_data = {
            "credential_strategy": "dynamic",
            "test_data_location": "workflow",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 60}
        }

        with patch('utils.state_manager.StateManager') as MockStateManager:
            with patch('tools.gates.qg_preflight.Path') as MockPath:
                mock_path = MagicMock()
                mock_path.exists.return_value = True
                MockPath.return_value = mock_path

                mock_instance = MagicMock()
                MockStateManager.return_value = mock_instance

                result = QGPreflight.validate(input_data)

                assert result["status"] == "pass"
                call_kwargs = mock_instance.save.call_args.kwargs
                saved_data = call_kwargs["data"]

                # Verify actual values are preserved
                assert saved_data["credential_strategy"] == "dynamic"
                assert saved_data["test_data_location"] == "workflow"
                assert saved_data["browser_config"]["headless"] is False
                assert saved_data["timeout_config"]["threshold_seconds"] == 60

    @pytest.mark.integration
    @pytest.mark.preflight
    @pytest.mark.state
    def test_state_manager_uses_run_id(self, mock_pre_check):
        """4.5: StateManager initialized with run_id for isolation."""
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        with patch('utils.state_manager.StateManager') as MockStateManager:
            with patch('tools.gates.qg_preflight.Path') as MockPath:
                mock_path = MagicMock()
                mock_path.exists.return_value = True
                MockPath.return_value = mock_path

                mock_instance = MagicMock()
                MockStateManager.return_value = mock_instance

                result = QGPreflight.validate(input_data)

                assert result["status"] == "pass"
                # Verify StateManager was called with run_id
                call_kwargs = MockStateManager.call_args.kwargs
                assert "run_id" in call_kwargs, "StateManager should be initialized with run_id"

    @pytest.mark.integration
    @pytest.mark.preflight
    @pytest.mark.state
    def test_no_state_saved_on_validation_failure(self, mock_pre_check):
        """State NOT saved when validation fails."""
        input_data = {
            "credential_strategy": "invalid",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        with patch('utils.state_manager.StateManager') as MockStateManager:
            mock_instance = MagicMock()
            MockStateManager.return_value = mock_instance

            result = QGPreflight.validate(input_data)

            assert result["status"] == "fail"
            mock_instance.save.assert_not_called()


# ==============================================================================
# Task 5.0: Audit Integration Tests (FR-2.7)
# ==============================================================================

class TestAuditIntegration:
    """
    Task 5.0: Audit integration tests for Step 2 gate.

    Verifies FR-2.7: Audit logging on gate PASS.
    """

    @pytest.mark.integration
    @pytest.mark.preflight
    @pytest.mark.audit
    def test_audit_event_logged_on_gate_pass(self, mock_pre_check):
        """5.1: Audit event logged on gate PASS."""
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        with patch('tools.gates.base_gate.BaseGate.get_audit_logger') as MockGetAuditLogger:
            with patch('tools.gates.base_gate.BaseGate._enforce_audit_write', return_value=None):
                with patch('utils.state_manager.StateManager'):
                    with patch('tools.gates.qg_preflight.Path') as MockPath:
                        mock_path = MagicMock()
                        mock_path.exists.return_value = True
                        MockPath.return_value = mock_path

                        # Setup mock audit logger
                        mock_audit_logger = MagicMock()
                        mock_audit_logger.run_id = "test-run-id"
                        MockGetAuditLogger.return_value = mock_audit_logger

                        result = QGPreflight.validate(input_data)

                        assert result["status"] == "pass"
                        # Verify log_gate was called
                        mock_audit_logger.log_gate.assert_called()

    @pytest.mark.integration
    @pytest.mark.preflight
    @pytest.mark.audit
    def test_audit_event_has_step_2_field(self, mock_pre_check):
        """5.2: Audit event has step=2 field."""
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        with patch('tools.gates.base_gate.BaseGate.get_audit_logger') as MockGetAuditLogger:
            with patch('tools.gates.base_gate.BaseGate._enforce_audit_write', return_value=None):
                with patch('utils.state_manager.StateManager'):
                    with patch('tools.gates.qg_preflight.Path') as MockPath:
                        mock_path = MagicMock()
                        mock_path.exists.return_value = True
                        MockPath.return_value = mock_path

                        mock_audit_logger = MagicMock()
                        mock_audit_logger.run_id = "test-run-id"
                        MockGetAuditLogger.return_value = mock_audit_logger

                        result = QGPreflight.validate(input_data)

                        assert result["status"] == "pass"
                        # Verify step=2 in log_gate call
                        call_kwargs = mock_audit_logger.log_gate.call_args.kwargs
                        assert call_kwargs["step"] == 2, "Audit event should have step=2"

    @pytest.mark.integration
    @pytest.mark.preflight
    @pytest.mark.audit
    def test_audit_event_has_gate_qg_preflight(self, mock_pre_check):
        """5.3: Audit event has gate='qg_preflight'."""
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        with patch('tools.gates.base_gate.BaseGate.get_audit_logger') as MockGetAuditLogger:
            with patch('tools.gates.base_gate.BaseGate._enforce_audit_write', return_value=None):
                with patch('utils.state_manager.StateManager'):
                    with patch('tools.gates.qg_preflight.Path') as MockPath:
                        mock_path = MagicMock()
                        mock_path.exists.return_value = True
                        MockPath.return_value = mock_path

                        mock_audit_logger = MagicMock()
                        mock_audit_logger.run_id = "test-run-id"
                        MockGetAuditLogger.return_value = mock_audit_logger

                        result = QGPreflight.validate(input_data)

                        assert result["status"] == "pass"
                        # Verify gate_name='qg_preflight' in log_gate call
                        call_kwargs = mock_audit_logger.log_gate.call_args.kwargs
                        assert call_kwargs["gate_name"] == "qg_preflight", \
                            "Audit event should have gate='qg_preflight'"

    @pytest.mark.integration
    @pytest.mark.preflight
    @pytest.mark.audit
    def test_audit_metadata_includes_all_config_fields(self, mock_pre_check):
        """5.4: Audit metadata includes all 4 config fields."""
        input_data = {
            "credential_strategy": "dynamic",
            "test_data_location": "workflow",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 60}
        }

        with patch('tools.gates.base_gate.BaseGate.get_audit_logger') as MockGetAuditLogger:
            with patch('tools.gates.base_gate.BaseGate._enforce_audit_write', return_value=None):
                with patch('utils.state_manager.StateManager'):
                    with patch('tools.gates.qg_preflight.Path') as MockPath:
                        mock_path = MagicMock()
                        mock_path.exists.return_value = True
                        MockPath.return_value = mock_path

                        mock_audit_logger = MagicMock()
                        mock_audit_logger.run_id = "test-run-id"
                        MockGetAuditLogger.return_value = mock_audit_logger

                        result = QGPreflight.validate(input_data)

                        assert result["status"] == "pass"
                        # Verify metadata includes all 4 config fields
                        call_kwargs = mock_audit_logger.log_gate.call_args.kwargs
                        metadata = call_kwargs.get("metadata", {})
                        assert "credential_strategy" in metadata, \
                            "Metadata should include credential_strategy"
                        assert "test_data_location" in metadata, \
                            "Metadata should include test_data_location"
                        assert "browser_config" in metadata, \
                            "Metadata should include browser_config"
                        assert "timeout_config" in metadata, \
                            "Metadata should include timeout_config"
                        # Verify actual values are preserved
                        assert metadata["credential_strategy"] == "dynamic"
                        assert metadata["test_data_location"] == "workflow"

    @pytest.mark.integration
    @pytest.mark.preflight
    @pytest.mark.audit
    def test_audit_appends_not_overwrites(self, mock_pre_check):
        """5.5: Audit appends (log_gate called once per validation, not clear)."""
        input_data = {
            "credential_strategy": "static",
            "test_data_location": "shared",
            "browser_config": {"headless": False},
            "timeout_config": {"enabled": True, "threshold_seconds": 30}
        }

        with patch('tools.gates.base_gate.BaseGate.get_audit_logger') as MockGetAuditLogger:
            with patch('tools.gates.base_gate.BaseGate._enforce_audit_write', return_value=None):
                with patch('utils.state_manager.StateManager'):
                    with patch('tools.gates.qg_preflight.Path') as MockPath:
                        mock_path = MagicMock()
                        mock_path.exists.return_value = True
                        MockPath.return_value = mock_path

                        mock_audit_logger = MagicMock()
                        mock_audit_logger.run_id = "test-run-id"
                        MockGetAuditLogger.return_value = mock_audit_logger

                        # First validation
                        result1 = QGPreflight.validate(input_data)
                        assert result1["status"] == "pass"
                        first_call_count = mock_audit_logger.log_gate.call_count

                        # Second validation (simulates Step 2 after Step 1)
                        result2 = QGPreflight.validate(input_data)
                        assert result2["status"] == "pass"
                        second_call_count = mock_audit_logger.log_gate.call_count

                        # Each validation should add to log (append behavior)
                        # Not reset or overwrite
                        assert second_call_count > first_call_count, \
                            "Audit should append, not overwrite (call count should increase)"

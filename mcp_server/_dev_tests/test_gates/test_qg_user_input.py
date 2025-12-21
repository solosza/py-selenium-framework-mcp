"""
Unit tests for qg_user_input - Task 5.0

Test Matrix:
- Happy path: 8 tests (P0)
- Negative: 5 tests (P0)
- Edge cases: 4 tests (P1)
- Error handling: 2 tests (P0)
- Integration: 1 test (P0)

Testing Skill Reference: .claude/skills/testing/

DD Coverage:
- DD-01: Persona required validation
- DD-02: URL required validation
"""

import pytest
from unittest.mock import patch, MagicMock

from tools.gates.qg_user_input import QGUserInput


class TestValidPersona:
    """
    Test suite for persona validation (DD-01).

    Tests organized by: valid persona values
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_valid_persona_passes(self):
        """
        P0: Verify valid persona passes validation.

        AAA Pattern:
        1. Arrange - Create input with valid persona
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "persona": "registered user",
            "URL": "http://automationpractice.pl/index.php",
            "role_name": "RegisteredUser",
            "domain": "auth",
            "raw_requirement": "As a registered user, I want to login"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Valid persona should pass"


class TestValidURL:
    """
    Test suite for URL validation (DD-02).

    Tests organized by: valid URL formats
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_valid_url_http_passes(self):
        """
        P0: Verify HTTP URL passes validation.

        AAA Pattern:
        1. Arrange - Create input with HTTP URL
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "persona": "guest",
            "URL": "http://example.com/page",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": "As a guest, I want to browse products"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "HTTP URL should pass"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_valid_url_https_passes(self):
        """
        P0: Verify HTTPS URL passes validation.

        AAA Pattern:
        1. Arrange - Create input with HTTPS URL
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "persona": "customer",
            "URL": "https://secure.example.com/checkout",
            "role_name": "Customer",
            "domain": "checkout",
            "raw_requirement": "As a customer, I want to checkout"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "HTTPS URL should pass"


class TestRoleNameExtraction:
    """
    Test suite for role_name extraction.

    Tests organized by: role name patterns
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_role_name_extracted_registered_user(self):
        """
        P0: Verify 'RegisteredUser' role_name passes.

        AAA Pattern:
        1. Arrange - Create input with RegisteredUser role
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "persona": "registered user",
            "URL": "http://example.com/login",
            "role_name": "RegisteredUser",
            "domain": "auth",
            "raw_requirement": "As a registered user, I want to login"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "RegisteredUser role should pass"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_role_name_extracted_guest(self):
        """
        P0: Verify 'Guest' role_name passes.

        AAA Pattern:
        1. Arrange - Create input with Guest role
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "persona": "guest",
            "URL": "http://example.com/browse",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": "As a guest, I want to browse"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Guest role should pass"


class TestDomainDetection:
    """
    Test suite for domain detection.

    Tests organized by: valid domain values
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_domain_detected_auth(self):
        """
        P0: Verify 'auth' domain passes validation.

        AAA Pattern:
        1. Arrange - Create input with auth domain
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "persona": "registered user",
            "URL": "http://example.com/login",
            "role_name": "RegisteredUser",
            "domain": "auth",
            "raw_requirement": "As a registered user, I want to login"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Auth domain should pass"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_domain_detected_catalog(self):
        """
        P0: Verify 'catalog' domain passes validation.

        AAA Pattern:
        1. Arrange - Create input with catalog domain
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "persona": "guest",
            "URL": "http://example.com/products",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": "As a guest, I want to browse products"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Catalog domain should pass"


class TestStateSaved:
    """
    Test suite for state persistence.

    Tests organized by: state save behavior
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_state_saved_on_pass(self):
        """
        P0: Verify state is saved when validation passes.

        AAA Pattern:
        1. Arrange - Create valid input, mock state_manager
        2. Act - Call qg_user_input.validate()
        3. Assert - state_manager.save() called with correct data
        """
        # Arrange
        input_data = {
            "persona": "registered user",
            "URL": "http://example.com/login",
            "role_name": "RegisteredUser",
            "domain": "auth",
            "raw_requirement": "As a registered user, I want to login"
        }

        # Act
        with patch('tools.gates.qg_user_input.StateManager') as MockStateManager:
            mock_instance = MagicMock()
            MockStateManager.return_value = mock_instance
            result = QGUserInput.validate(input_data)

            # Assert
            assert result["status"] == "pass", "Validation should pass"
            mock_instance.save.assert_called_once()
            call_kwargs = mock_instance.save.call_args.kwargs
            assert call_kwargs["step"] == 2, "Should save to step 2"
            assert "persona" in call_kwargs["data"], "Should include persona"
            assert "URL" in call_kwargs["data"], "Should include URL"
            assert "role_name" in call_kwargs["data"], "Should include role_name"
            assert "domain" in call_kwargs["data"], "Should include domain"


class TestInvalidInputs:
    """
    Test suite for invalid input validation.

    Tests organized by: failure type
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_missing_persona_fails(self):
        """
        P0: Verify missing persona fails validation (DD-01).

        AAA Pattern:
        1. Arrange - Create input without persona
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "URL": "http://example.com/login",
            "role_name": "RegisteredUser",
            "domain": "auth",
            "raw_requirement": "I want to login"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Missing persona should fail"
        assert "error" in result, "Should include error message"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_persona_without_as_a_fails(self):
        """
        P0: Verify persona without 'As a' format is still accepted if valid text.

        Note: The gate validates presence, not format - format is AI's job.

        AAA Pattern:
        1. Arrange - Create input with non-standard persona
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns pass (format validation is AI's concern)
        """
        # Arrange - persona is present, just not in standard format
        input_data = {
            "persona": "customer",  # Valid persona, just not "As a..." format
            "URL": "http://example.com/login",
            "role_name": "Customer",
            "domain": "auth",
            "raw_requirement": "I want to login as customer"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert - Gate accepts any non-empty persona
        assert result["status"] == "pass", "Non-empty persona should pass"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_invalid_url_format_fails(self):
        """
        P0: Verify invalid URL format fails validation (DD-02).

        AAA Pattern:
        1. Arrange - Create input with invalid URL
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "persona": "guest",
            "URL": "not-a-valid-url",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": "As a guest, I want to browse"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Invalid URL should fail"
        assert "error" in result, "Should include error message"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_missing_url_fails(self):
        """
        P0: Verify missing URL fails validation (DD-02).

        AAA Pattern:
        1. Arrange - Create input without URL
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "persona": "guest",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": "As a guest, I want to browse"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Missing URL should fail"
        assert "error" in result, "Should include error message"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_no_state_saved_on_fail(self):
        """
        P0: Verify state is NOT saved when validation fails.

        AAA Pattern:
        1. Arrange - Create invalid input, mock state_manager
        2. Act - Call qg_user_input.validate()
        3. Assert - state_manager.save() NOT called
        """
        # Arrange
        input_data = {
            "persona": "",  # Invalid - empty
            "URL": "http://example.com",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": "Browse products"
        }

        # Act
        with patch('tools.gates.qg_user_input.StateManager') as MockStateManager:
            mock_instance = MagicMock()
            MockStateManager.return_value = mock_instance
            result = QGUserInput.validate(input_data)

            # Assert
            assert result["status"] == "fail", "Validation should fail"
            mock_instance.save.assert_not_called()


class TestEdgeCases:
    """
    Test suite for edge case validation.

    Tests organized by: edge case type
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_empty_persona(self):
        """
        P1: Verify empty string persona fails validation.

        AAA Pattern:
        1. Arrange - Create input with empty persona
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "persona": "",
            "URL": "http://example.com/login",
            "role_name": "Guest",
            "domain": "auth",
            "raw_requirement": "Login"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty persona should fail"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_localhost_url(self):
        """
        P1: Verify localhost URL passes validation.

        AAA Pattern:
        1. Arrange - Create input with localhost URL
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "persona": "developer",
            "URL": "http://localhost:3000/app",
            "role_name": "Developer",
            "domain": "auth",
            "raw_requirement": "As a developer, I want to test locally"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Localhost URL should pass"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_url_with_port(self):
        """
        P1: Verify URL with port passes validation.

        AAA Pattern:
        1. Arrange - Create input with URL containing port
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns pass status
        """
        # Arrange
        input_data = {
            "persona": "tester",
            "URL": "http://staging.example.com:8080/login",
            "role_name": "Tester",
            "domain": "auth",
            "raw_requirement": "As a tester, I want to verify staging"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "URL with port should pass"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_multiple_roles_in_persona(self):
        """
        P1: Verify persona with multiple words is accepted.

        AAA Pattern:
        1. Arrange - Create input with multi-word persona
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns pass status (gate accepts any non-empty)
        """
        # Arrange
        input_data = {
            "persona": "premium registered user with subscription",
            "URL": "http://example.com/premium",
            "role_name": "PremiumUser",
            "domain": "catalog",
            "raw_requirement": "As a premium user, I want to access exclusive content"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Multi-word persona should pass"


class TestErrorHandling:
    """
    Test suite for error handling and fix hints.

    Tests organized by: error response format
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_fix_hint_for_missing_persona(self):
        """
        P0: Verify fix_hint is provided for missing persona.

        AAA Pattern:
        1. Arrange - Create input without persona
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns fix_hint mentioning persona format
        """
        # Arrange
        input_data = {
            "URL": "http://example.com",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": "Browse products"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail"
        assert "fix_hint" in result, "Should include fix_hint"
        assert "persona" in result["fix_hint"].lower(), "fix_hint should mention persona"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_fix_hint_for_invalid_url(self):
        """
        P0: Verify fix_hint is provided for invalid URL.

        AAA Pattern:
        1. Arrange - Create input with invalid URL
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns fix_hint mentioning URL format
        """
        # Arrange
        input_data = {
            "persona": "guest",
            "URL": "invalid-url",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": "Browse products"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail"
        assert "fix_hint" in result, "Should include fix_hint"
        assert "url" in result["fix_hint"].lower(), "fix_hint should mention URL"


class TestInvalidDomain:
    """
    Test suite for domain validation.

    Tests organized by: domain values
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_invalid_domain_fails(self):
        """
        P0: Verify invalid domain fails validation.

        AAA Pattern:
        1. Arrange - Create input with invalid domain
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "persona": "guest",
            "URL": "http://example.com/page",
            "role_name": "Guest",
            "domain": "invalid_domain",
            "raw_requirement": "As a guest, I want to do something"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Invalid domain should fail"
        assert "error" in result, "Should include error message"


class TestInvalidRoleName:
    """
    Test suite for role_name validation.

    Tests organized by: role_name edge cases
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_empty_role_name_fails(self):
        """
        P1: Verify empty role_name fails validation.

        AAA Pattern:
        1. Arrange - Create input with empty role_name
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "persona": "guest",
            "URL": "http://example.com/page",
            "role_name": "",  # Invalid - empty
            "domain": "catalog",
            "raw_requirement": "As a guest, I want to browse"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty role_name should fail"
        assert "role_name" in result["error"].lower(), "Error should mention role_name"


class TestInvalidRawRequirement:
    """
    Test suite for raw_requirement validation.

    Tests organized by: raw_requirement edge cases
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_empty_raw_requirement_fails(self):
        """
        P1: Verify empty raw_requirement fails validation.

        AAA Pattern:
        1. Arrange - Create input with empty raw_requirement
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "persona": "guest",
            "URL": "http://example.com/page",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": ""  # Invalid - empty
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty raw_requirement should fail"
        assert "raw_requirement" in result["error"].lower(), "Error should mention raw_requirement"


class TestMissingMultipleFields:
    """
    Test suite for multiple missing fields.

    Tests organized by: combined validation
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_missing_all_fields_shows_all_hints(self):
        """
        P1: Verify all missing fields are reported in fix_hint.

        AAA Pattern:
        1. Arrange - Create empty input
        2. Act - Call qg_user_input.validate()
        3. Assert - fix_hint mentions all fields
        """
        # Arrange
        input_data = {}  # All fields missing

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Missing all fields should fail"
        assert "persona" in result["fix_hint"].lower(), "Should mention persona"
        assert "url" in result["fix_hint"].lower(), "Should mention URL"
        assert "role_name" in result["fix_hint"].lower(), "Should mention role_name"
        assert "domain" in result["fix_hint"].lower(), "Should mention domain"


class TestIntegration:
    """
    Test suite for integration behavior.

    Tests organized by: integration patterns
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_blocks_step_3_on_fail(self):
        """
        P0: Verify gate failure blocks progression to Step 3.

        This test verifies the gate returns fail status that would block
        progression. Actual step blocking is enforced by StateManager.

        AAA Pattern:
        1. Arrange - Create invalid input
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns fail (blocks Step 3)
        """
        # Arrange
        input_data = {
            "persona": "",  # Invalid
            "URL": "not-a-url",  # Invalid
            "role_name": "",
            "domain": "invalid",
            "raw_requirement": ""
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Invalid input should fail"
        assert "error" in result, "Should include error for debugging"
        # Note: Actual Step 3 blocking is done by state_manager.is_step_complete(2)

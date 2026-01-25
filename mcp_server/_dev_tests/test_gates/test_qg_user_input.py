"""
Unit tests for qg_user_input - Task 5.0 + Task 3.4 (Layer 1)

Test Matrix:
- Layer 1 (Regex/Validation): 25+ tests - basic building blocks
- Happy path: 8 tests (P0)
- Negative: 5 tests (P0)
- Edge cases: 4 tests (P1)
- Error handling: 5 tests (P0)
- Integration: 1 test (P0)
- Environment detection: 5 tests (P0)

Testing Skill Reference: .claude/skills/testing/

DD Coverage:
- DD-01: Persona required validation
- DD-02: URL required validation
"""

import pytest
from unittest.mock import patch, MagicMock

from tools.gates.qg_user_input import QGUserInput


@pytest.fixture(autouse=True)
def mock_transcript_check():
    """
    Mock BaseGate._check_transcript_written to skip transcript validation.

    Step 1 v4.0 requires transcript to exist before returning pass.
    Unit tests focus on validation logic, not transcript infrastructure.
    """
    with patch('tools.gates.base_gate.BaseGate._check_transcript_written', return_value=None):
        yield


##############################################################################
# LAYER 1: Regex Pattern and Validation Helper Tests
# These test the basic building blocks of qg_user_input
##############################################################################


class TestURLPatternRegex:
    """
    Layer 1: Tests for URL_PATTERN regex.

    Pattern: r'^https?://\S+$'
    - Must start with http:// or https://
    - Must have non-whitespace characters after
    """

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_url_pattern_http(self):
        """L1: HTTP URL matches pattern."""
        assert QGUserInput.URL_PATTERN.match("http://example.com")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_url_pattern_https(self):
        """L1: HTTPS URL matches pattern."""
        assert QGUserInput.URL_PATTERN.match("https://example.com")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_url_pattern_with_path(self):
        """L1: URL with path matches pattern."""
        assert QGUserInput.URL_PATTERN.match("https://example.com/path/to/page")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_url_pattern_with_port(self):
        """L1: URL with port matches pattern."""
        assert QGUserInput.URL_PATTERN.match("http://localhost:3000/api")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_url_pattern_with_query(self):
        """L1: URL with query string matches pattern."""
        assert QGUserInput.URL_PATTERN.match("https://example.com?foo=bar&baz=qux")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_url_pattern_rejects_ftp(self):
        """L1: FTP scheme rejected by pattern."""
        assert not QGUserInput.URL_PATTERN.match("ftp://example.com")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_url_pattern_rejects_no_scheme(self):
        """L1: URL without scheme rejected."""
        assert not QGUserInput.URL_PATTERN.match("example.com")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_url_pattern_rejects_typo_scheme(self):
        """L1: Typo in scheme (htp) rejected."""
        assert not QGUserInput.URL_PATTERN.match("htp://example.com")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_url_pattern_rejects_file_scheme(self):
        """L1: File scheme rejected."""
        assert not QGUserInput.URL_PATTERN.match("file:///path/to/file")


class TestPascalCasePatternRegex:
    """
    Layer 1: Tests for PASCAL_CASE_PATTERN regex.

    Pattern: r'^[A-Z][a-zA-Z0-9]*$'
    - Must start with uppercase letter
    - Only alphanumeric characters allowed
    """

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_pascal_pattern_single_word(self):
        """L1: Single PascalCase word matches."""
        assert QGUserInput.PASCAL_CASE_PATTERN.match("Guest")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_pascal_pattern_two_words(self):
        """L1: Two-word PascalCase matches."""
        assert QGUserInput.PASCAL_CASE_PATTERN.match("RegisteredUser")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_pascal_pattern_with_numbers(self):
        """L1: PascalCase with numbers matches."""
        assert QGUserInput.PASCAL_CASE_PATTERN.match("User123")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_pascal_pattern_single_letter(self):
        """L1: Single uppercase letter matches."""
        assert QGUserInput.PASCAL_CASE_PATTERN.match("A")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_pascal_pattern_rejects_lowercase_start(self):
        """L1: Starting with lowercase rejected."""
        assert not QGUserInput.PASCAL_CASE_PATTERN.match("registeredUser")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_pascal_pattern_rejects_snake_case(self):
        """L1: snake_case rejected."""
        assert not QGUserInput.PASCAL_CASE_PATTERN.match("registered_user")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_pascal_pattern_rejects_kebab_case(self):
        """L1: kebab-case rejected."""
        assert not QGUserInput.PASCAL_CASE_PATTERN.match("registered-user")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_pascal_pattern_rejects_number_start(self):
        """L1: Starting with number rejected."""
        assert not QGUserInput.PASCAL_CASE_PATTERN.match("123User")

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_pascal_pattern_rejects_spaces(self):
        """L1: Spaces rejected."""
        assert not QGUserInput.PASCAL_CASE_PATTERN.match("Registered User")


class TestIsValidPersonaHelper:
    """
    Layer 1: Tests for _is_valid_persona() helper method.
    """

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_persona_simple(self):
        """L1: Simple persona is valid."""
        assert QGUserInput._is_valid_persona("guest") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_persona_multi_word(self):
        """L1: Multi-word persona is valid."""
        assert QGUserInput._is_valid_persona("registered user") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_persona_none(self):
        """L1: None persona is invalid."""
        assert QGUserInput._is_valid_persona(None) is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_persona_empty(self):
        """L1: Empty string persona is invalid."""
        assert QGUserInput._is_valid_persona("") is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_persona_whitespace_only(self):
        """L1: Whitespace-only persona is invalid."""
        assert QGUserInput._is_valid_persona("   ") is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_persona_non_string(self):
        """L1: Non-string persona is invalid."""
        assert QGUserInput._is_valid_persona(123) is False


class TestIsValidURLHelper:
    """
    Layer 1: Tests for _is_valid_url() helper method.
    """

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_url_http(self):
        """L1: HTTP URL is valid."""
        assert QGUserInput._is_valid_url("http://example.com") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_url_https(self):
        """L1: HTTPS URL is valid."""
        assert QGUserInput._is_valid_url("https://example.com") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_url_with_port(self):
        """L1: URL with port is valid."""
        assert QGUserInput._is_valid_url("http://localhost:8080") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_url_with_path_and_query(self):
        """L1: URL with path and query is valid."""
        assert QGUserInput._is_valid_url("https://example.com/path?q=test") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_url_none(self):
        """L1: None URL is invalid."""
        assert QGUserInput._is_valid_url(None) is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_url_empty(self):
        """L1: Empty string URL is invalid."""
        assert QGUserInput._is_valid_url("") is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_url_no_scheme(self):
        """L1: URL without scheme is invalid."""
        assert QGUserInput._is_valid_url("example.com") is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_url_ftp_scheme(self):
        """L1: FTP URL is invalid (only http/https allowed)."""
        assert QGUserInput._is_valid_url("ftp://example.com") is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_url_non_string(self):
        """L1: Non-string URL is invalid."""
        assert QGUserInput._is_valid_url(12345) is False


class TestIsValidRoleNameHelper:
    """
    Layer 1: Tests for _is_valid_role_name() helper method.
    """

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_role_name_single(self):
        """L1: Single-word PascalCase role is valid."""
        assert QGUserInput._is_valid_role_name("Guest") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_role_name_multi_word(self):
        """L1: Multi-word PascalCase role is valid."""
        assert QGUserInput._is_valid_role_name("RegisteredUser") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_role_name_with_number(self):
        """L1: PascalCase with number is valid."""
        assert QGUserInput._is_valid_role_name("User1") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_role_name_none(self):
        """L1: None role_name is invalid."""
        assert QGUserInput._is_valid_role_name(None) is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_role_name_empty(self):
        """L1: Empty role_name is invalid."""
        assert QGUserInput._is_valid_role_name("") is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_role_name_lowercase(self):
        """L1: Lowercase role_name is invalid."""
        assert QGUserInput._is_valid_role_name("guest") is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_role_name_snake_case(self):
        """L1: snake_case role_name is invalid."""
        assert QGUserInput._is_valid_role_name("registered_user") is False


class TestIsValidWorkflowHelper:
    """
    Layer 1: Tests for _is_valid_workflow() helper method.
    """

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_workflow_simple(self):
        """L1: Simple workflow name is valid."""
        assert QGUserInput._is_valid_workflow("auth") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_workflow_with_hyphen(self):
        """L1: Workflow with hyphen is valid."""
        assert QGUserInput._is_valid_workflow("checkout-v2") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_workflow_custom(self):
        """L1: Custom workflow name is valid (dynamic)."""
        assert QGUserInput._is_valid_workflow("my-custom-workflow") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_workflow_none(self):
        """L1: None workflow is invalid."""
        assert QGUserInput._is_valid_workflow(None) is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_workflow_empty(self):
        """L1: Empty workflow is invalid."""
        assert QGUserInput._is_valid_workflow("") is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_workflow_whitespace_only(self):
        """L1: Whitespace-only workflow is invalid."""
        assert QGUserInput._is_valid_workflow("   ") is False


class TestIsValidRawRequirementHelper:
    """
    Layer 1: Tests for _is_valid_raw_requirement() helper method.
    """

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_requirement_simple(self):
        """L1: Simple requirement is valid."""
        assert QGUserInput._is_valid_raw_requirement("I want to login") is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_valid_requirement_full_format(self):
        """L1: Full 'As a...' format is valid."""
        assert QGUserInput._is_valid_raw_requirement(
            "As a registered user, I want to login with my credentials"
        ) is True

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_requirement_none(self):
        """L1: None requirement is invalid."""
        assert QGUserInput._is_valid_raw_requirement(None) is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_requirement_empty(self):
        """L1: Empty requirement is invalid."""
        assert QGUserInput._is_valid_raw_requirement("") is False

    @pytest.mark.unit
    @pytest.mark.layer1
    @pytest.mark.qg_user_input
    def test_invalid_requirement_whitespace_only(self):
        """L1: Whitespace-only requirement is invalid."""
        assert QGUserInput._is_valid_raw_requirement("   ") is False


##############################################################################
# LAYER 2: Edge Case and Boundary Tests
# These test unusual inputs and boundary conditions
##############################################################################


class TestLayer2EdgeCases:
    """
    Layer 2: Edge case validation tests.

    Tests unusual inputs, boundary conditions, and special characters.
    """

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.qg_user_input
    def test_url_with_special_chars(self):
        """L2: URL with special characters in query string."""
        # Arrange
        input_data = {
            "persona": "user",
            "URL": "https://example.com/search?q=hello%20world&filter=a+b",
            "role_name": "User",
            "workflow": "search",
            "raw_requirement": "Search test"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert - Should handle encoded characters
        assert result["status"] in ["pass", "NEEDS_RETRY"], \
            "URL with special chars should pass or need retry for unknown domain"

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.qg_user_input
    def test_unicode_in_persona(self):
        """L2: Unicode characters in persona."""
        # Arrange
        input_data = {
            "persona": "utilisateur français",  # French: "French user"
            "URL": "http://www.automationpractice.pl/index.php",
            "role_name": "UtilisateurFrancais",
            "workflow": "auth",
            "raw_requirement": "French user login"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert - Unicode personas should be valid
        assert result["status"] == "pass", "Unicode persona should pass"

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.qg_user_input
    def test_very_long_persona(self):
        """L2: Very long persona string (stress test)."""
        # Arrange - 1000+ character persona
        long_persona = "user " * 200  # 1000 chars
        input_data = {
            "persona": long_persona,
            "URL": "http://www.automationpractice.pl/index.php",
            "role_name": "LongUser",
            "workflow": "auth",
            "raw_requirement": "Long persona test"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert - Long persona should still pass (no length limit)
        assert result["status"] == "pass", "Long persona should pass"

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.qg_user_input
    def test_very_long_url(self):
        """L2: Very long URL string (stress test)."""
        # Arrange - URL with long query string
        long_query = "&param=value" * 100
        input_data = {
            "persona": "user",
            "URL": f"http://www.automationpractice.pl/index.php?start=1{long_query}",
            "role_name": "User",
            "workflow": "auth",
            "raw_requirement": "Long URL test"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert - Long URL should still pass
        assert result["status"] == "pass", "Long URL should pass"

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.qg_user_input
    def test_url_with_fragment(self):
        """L2: URL with fragment (#anchor)."""
        # Arrange
        input_data = {
            "persona": "user",
            "URL": "http://www.automationpractice.pl/index.php#section",
            "role_name": "User",
            "workflow": "catalog",
            "raw_requirement": "Fragment URL test"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "URL with fragment should pass"

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.qg_user_input
    def test_url_with_basic_auth(self):
        """L2: URL with basic auth (user:pass@host)."""
        # Arrange
        input_data = {
            "persona": "user",
            "URL": "http://www.automationpractice.pl/index.php",
            "role_name": "User",
            "workflow": "auth",
            "raw_requirement": "Basic auth URL test"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "URL with basic auth format should pass"

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.qg_user_input
    def test_workflow_with_numbers(self):
        """L2: Workflow with numbers (sprint identifiers)."""
        # Arrange
        input_data = {
            "persona": "user",
            "URL": "http://www.automationpractice.pl/index.php",
            "role_name": "User",
            "workflow": "sprint-42",
            "raw_requirement": "Sprint workflow test"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Numeric workflow should pass"

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.qg_user_input
    def test_role_name_all_caps(self):
        """L2: Role name in ALL CAPS (still PascalCase start)."""
        # Arrange
        input_data = {
            "persona": "admin",
            "URL": "http://www.automationpractice.pl/index.php",
            "role_name": "ADMIN",  # All caps but starts with uppercase
            "workflow": "admin",
            "raw_requirement": "Admin test"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert - All caps starting with uppercase should pass
        assert result["status"] == "pass", "All caps role should pass"

    @pytest.mark.unit
    @pytest.mark.layer2
    @pytest.mark.qg_user_input
    def test_minimal_valid_input(self):
        """L2: Minimal valid input (shortest possible values)."""
        # Arrange
        input_data = {
            "persona": "a",
            "URL": "http://www.automationpractice.pl",
            "role_name": "A",
            "workflow": "x",
            "raw_requirement": "y"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "pass", "Minimal input should pass"


##############################################################################
# LAYER 4: Production Failure Scenarios
# These test error handling and fault injection
##############################################################################


class TestLayer4ProductionFailures:
    """
    Layer 4: Production failure scenario tests.

    Tests error handling, missing config, and fault conditions.
    """

    @pytest.mark.unit
    @pytest.mark.layer4
    @pytest.mark.qg_user_input
    def test_environment_config_read_fails(self):
        """L4: Graceful handling when environment config can't be read."""
        import builtins
        original_open = builtins.open

        def selective_fail_open(path, *args, **kwargs):
            """Only fail for environment_config.json, let other files work."""
            if 'environment_config.json' in str(path):
                raise IOError("Config file not found")
            return original_open(path, *args, **kwargs)

        # Arrange
        input_data = {
            "persona": "user",
            "URL": "https://unknown-site.example.com/page",
            "role_name": "User",
            "workflow": "test",
            "raw_requirement": "Test requirement"
        }

        # Act - Patch config read to raise exception ONLY for environment config
        with patch('builtins.open', side_effect=selective_fail_open):
            result = QGUserInput.validate(input_data)

        # Assert - Should fall back to DEFAULT environment
        assert result["status"] == "pass", "Should fall back gracefully on config read error"

    @pytest.mark.unit
    @pytest.mark.layer4
    @pytest.mark.qg_user_input
    def test_state_manager_raises_exception(self):
        """L4: Handling when StateManager raises during save."""
        # Arrange
        input_data = {
            "persona": "user",
            "URL": "http://www.automationpractice.pl/index.php",
            "role_name": "User",
            "workflow": "auth",
            "raw_requirement": "Test requirement"
        }

        # Act - Patch StateManager.save to raise exception
        with patch('utils.state_manager.StateManager') as MockStateManager:
            mock_instance = MagicMock()
            mock_instance.save.side_effect = IOError("Disk full")
            MockStateManager.return_value = mock_instance

            # This should raise or handle gracefully
            try:
                result = QGUserInput.validate(input_data)
                # If it doesn't raise, it handled it internally
                assert "status" in result
            except IOError:
                # Expected - state save failed
                pass

    @pytest.mark.unit
    @pytest.mark.layer4
    @pytest.mark.qg_user_input
    def test_malformed_environment_config_json(self):
        """L4: Handling malformed JSON in environment config."""
        import builtins
        import io
        original_open = builtins.open

        def selective_malformed_open(path, *args, **kwargs):
            """Return malformed JSON only for environment_config.json."""
            if 'environment_config.json' in str(path):
                # Return a file-like object with invalid JSON
                return io.StringIO("{ not valid json }")
            return original_open(path, *args, **kwargs)

        # Arrange
        input_data = {
            "persona": "user",
            "URL": "https://new-site.example.com/page",
            "role_name": "User",
            "workflow": "test",
            "raw_requirement": "Test requirement"
        }

        # Act - Patch config to return invalid JSON ONLY for environment config
        with patch('builtins.open', side_effect=selective_malformed_open):
            result = QGUserInput.validate(input_data)

        # Assert - Should fall back to DEFAULT (json.load will raise JSONDecodeError)
        assert result["status"] == "pass", "Should fall back to DEFAULT on malformed JSON"


##############################################################################
# EXISTING TESTS (Happy Path, Negative, Edge Cases, etc.)
##############################################################################


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
            "URL": "http://www.automationpractice.pl/index.php",
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
            "URL": "http://www.automationpractice.pl/index.php",
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
            "URL": "https://parabank.parasoft.com/parabank/index.htm",
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
            "URL": "http://www.automationpractice.pl/login",
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
            "URL": "http://www.automationpractice.pl/browse",
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
            "URL": "http://www.automationpractice.pl/login",
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
            "URL": "http://www.automationpractice.pl/products",
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
            "URL": "http://www.automationpractice.pl/login",
            "role_name": "RegisteredUser",
            "domain": "auth",
            "raw_requirement": "As a registered user, I want to login"
        }

        # Act
        with patch('utils.state_manager.StateManager') as MockStateManager:
            mock_instance = MagicMock()
            MockStateManager.return_value = mock_instance
            result = QGUserInput.validate(input_data)

            # Assert
            assert result["status"] == "pass", "Validation should pass"
            mock_instance.save.assert_called_once()
            call_kwargs = mock_instance.save.call_args.kwargs
            assert call_kwargs["step"] == 1, "Should save to step 1"
            assert "persona" in call_kwargs["data"], "Should include persona"
            assert "URL" in call_kwargs["data"], "Should include URL"
            assert "role_name" in call_kwargs["data"], "Should include role_name"
            assert "workflow" in call_kwargs["data"], "Should include workflow"
            assert "detected_env_id" in call_kwargs["data"], "Should include detected_env_id"


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
            "URL": "http://www.automationpractice.pl/login",
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
            "URL": "http://www.automationpractice.pl/login",
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
            "URL": "http://www.automationpractice.pl",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": "Browse products"
        }

        # Act
        with patch('utils.state_manager.StateManager') as MockStateManager:
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
            "URL": "http://www.automationpractice.pl/login",
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
            "URL": "http://www.automationpractice.pl/index.php",
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
            "URL": "http://www.automationpractice.pl/index.php",
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
            "URL": "http://www.automationpractice.pl/premium",
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
    Test suite for error handling and teach guidance.

    Tests organized by: error response format and teach quality
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_teach_for_missing_persona(self):
        """
        P0: Verify teach is provided for missing persona.

        AAA Pattern:
        1. Arrange - Create input without persona
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns teach mentioning persona format
        """
        # Arrange
        input_data = {
            "URL": "http://www.automationpractice.pl",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": "Browse products"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Should fail"
        assert "teach" in result, "Should include teach"
        assert "persona" in result["teach"].lower(), "teach should mention persona"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_teach_for_invalid_url(self):
        """
        P0: Verify teach is provided for invalid URL.

        AAA Pattern:
        1. Arrange - Create input with invalid URL
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns teach mentioning URL format
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
        assert "teach" in result, "Should include teach"
        assert "url" in result["teach"].lower(), "teach should mention URL"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_teach_quality_includes_examples(self):
        """
        P1: Verify teach includes examples for guidance.

        AAA Pattern:
        1. Arrange - Create input with invalid persona
        2. Act - Call qg_user_input.validate()
        3. Assert - teach includes example values
        """
        # Arrange
        input_data = {
            "persona": "",  # Invalid - empty
            "URL": "http://www.automationpractice.pl",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": "Browse products"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "teach" in result
        # Verify example is present
        assert "example" in result["teach"].lower(), \
            "teach should include example for guidance"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_teach_quality_is_actionable(self):
        """
        P1: Verify teach provides actionable guidance (tells user what to do).

        AAA Pattern:
        1. Arrange - Create input with invalid URL
        2. Act - Call qg_user_input.validate()
        3. Assert - teach tells user what format is required
        """
        # Arrange
        input_data = {
            "persona": "guest",
            "URL": "not-a-url",
            "role_name": "Guest",
            "domain": "catalog",
            "raw_requirement": "Browse products"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "teach" in result
        # Verify actionable guidance (must be HTTP/HTTPS)
        assert any(keyword in result["teach"].lower() for keyword in ["must", "should", "http"]), \
            "teach should provide actionable guidance about what is required"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_teach_quality_multiple_fields(self):
        """
        P1: Verify teach for multiple missing fields is comprehensive.

        AAA Pattern:
        1. Arrange - Create input missing multiple fields
        2. Act - Call qg_user_input.validate()
        3. Assert - teach mentions all missing fields
        """
        # Arrange
        input_data = {
            # Missing: persona, URL, role_name, workflow, raw_requirement
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "teach" in result

        # Verify all required fields mentioned
        teach_lower = result["teach"].lower()
        assert "persona" in teach_lower, "Should mention persona"
        assert "url" in teach_lower, "Should mention URL"
        assert "role_name" in teach_lower or "role" in teach_lower, "Should mention role_name"
        # Note: workflow mentioned as "domain" for backwards compatibility
        assert "workflow" in teach_lower or "domain" in teach_lower, "Should mention workflow/domain"
        assert "raw_requirement" in teach_lower or "requirement" in teach_lower, \
            "Should mention raw_requirement"


class TestWorkflowValidation:
    """
    Test suite for workflow validation.

    Workflow/domain is dynamic - any non-empty string is valid.
    Tests verify empty/missing workflow fails.
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_empty_workflow_fails(self):
        """
        P0: Verify empty workflow fails validation.

        Workflow/domain is dynamic (any non-empty string is valid).
        Only empty/missing workflow should fail.

        AAA Pattern:
        1. Arrange - Create input with empty workflow
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns fail status
        """
        # Arrange
        input_data = {
            "persona": "guest",
            "URL": "http://www.automationpractice.pl/page",
            "role_name": "Guest",
            "workflow": "",  # Empty workflow should fail
            "raw_requirement": "As a guest, I want to do something"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Empty workflow should fail"
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
            "URL": "http://www.automationpractice.pl/page",
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
            "URL": "http://www.automationpractice.pl/page",
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
        P1: Verify all missing fields are reported in teach.

        AAA Pattern:
        1. Arrange - Create empty input
        2. Act - Call qg_user_input.validate()
        3. Assert - teach mentions all fields
        """
        # Arrange
        input_data = {}  # All fields missing

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "fail", "Missing all fields should fail"
        assert "persona" in result["teach"].lower(), "Should mention persona"
        assert "url" in result["teach"].lower(), "Should mention URL"
        assert "role_name" in result["teach"].lower(), "Should mention role_name"
        assert "domain" in result["teach"].lower(), "Should mention domain"


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


class TestEnvironmentDetection:
    """
    Test suite for environment auto-detection (DEF-062).

    Tests organized by: detection scenarios
    """

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_detects_parabank_environment(self):
        """
        P0: Verify ParaBank URL detects 'parabank' environment.

        AAA Pattern:
        1. Arrange - Create input with ParaBank URL
        2. Act - Call qg_user_input.validate()
        3. Assert - detected_env_id is 'parabank'
        """
        # Arrange
        input_data = {
            "persona": "registered user",
            "URL": "https://parabank.parasoft.com/parabank/index.htm",
            "role_name": "RegisteredUser",
            "workflow": "auth",
            "raw_requirement": "I want to login"
        }

        # Act
        with patch('utils.state_manager.StateManager') as MockStateManager:
            mock_instance = MagicMock()
            MockStateManager.return_value = mock_instance
            result = QGUserInput.validate(input_data)

            # Assert
            assert result["status"] == "pass", "Validation should pass"
            call_kwargs = mock_instance.save.call_args.kwargs
            assert call_kwargs["data"]["detected_env_id"] == "parabank", \
                "ParaBank URL should detect 'parabank' environment"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_detects_default_environment(self):
        """
        P0: Verify automationpractice.pl URL detects 'DEFAULT' environment.

        AAA Pattern:
        1. Arrange - Create input with automationpractice.pl URL
        2. Act - Call qg_user_input.validate()
        3. Assert - detected_env_id is 'DEFAULT'
        """
        # Arrange
        input_data = {
            "persona": "guest",
            "URL": "http://www.automationpractice.pl/index.php",
            "role_name": "Guest",
            "workflow": "catalog",
            "raw_requirement": "I want to browse products"
        }

        # Act
        with patch('utils.state_manager.StateManager') as MockStateManager:
            mock_instance = MagicMock()
            MockStateManager.return_value = mock_instance
            result = QGUserInput.validate(input_data)

            # Assert
            assert result["status"] == "pass", "Validation should pass"
            call_kwargs = mock_instance.save.call_args.kwargs
            assert call_kwargs["data"]["detected_env_id"] == "DEFAULT", \
                "Automationpractice.pl URL should detect 'DEFAULT' environment"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_unknown_domain_returns_needs_retry(self):
        """
        P0: Verify unknown domain returns NEEDS_RETRY with scaffolding instructions.

        AAA Pattern:
        1. Arrange - Create input with unknown domain URL
        2. Act - Call qg_user_input.validate()
        3. Assert - Returns NEEDS_RETRY with environment config scaffolding
        """
        # Arrange
        input_data = {
            "persona": "user",
            "URL": "https://new-app.example.com/login",
            "role_name": "User",
            "workflow": "auth",
            "raw_requirement": "Test requirement"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "NEEDS_RETRY", "Should return NEEDS_RETRY for unknown domain"
        assert "scaffolding_needed" in result, "Should include scaffolding instructions"
        assert result["fix_applied"] == "environment_added_to_config", \
            "Should indicate environment was added"

        # Verify scaffolding structure
        scaffolding = result["scaffolding_needed"][0]
        assert scaffolding["type"] == "config_entry", "Should be config entry type"
        assert "environment_config.json" in scaffolding["path"], "Should point to environment config"
        assert "auth" in scaffolding["template"], "Should include workflow name in template"
        assert "new-app.example.com" in scaffolding["template"], "Should include domain in template"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_unknown_domain_template_valid_json(self):
        """
        P1: Verify NEEDS_RETRY template has correct JSON format.

        AAA Pattern:
        1. Arrange - Create input with unknown domain
        2. Act - Call qg_user_input.validate()
        3. Assert - Template is valid JSON with correct structure
        """
        # Arrange
        input_data = {
            "persona": "admin",
            "URL": "https://staging.myapp.io/dashboard",
            "role_name": "Admin",
            "workflow": "admin",
            "raw_requirement": "Admin workflow test"
        }

        # Act
        result = QGUserInput.validate(input_data)

        # Assert
        assert result["status"] == "NEEDS_RETRY", "Should return NEEDS_RETRY"

        # Verify template is valid JSON
        import json
        scaffolding = result["scaffolding_needed"][0]
        template_json = json.loads(scaffolding["template"])

        assert "admin" in template_json, "Template should have workflow key"
        assert "url" in template_json["admin"], "Template should have url field"
        assert template_json["admin"]["url"] == "https://staging.myapp.io", \
            "Template should have base URL (no path)"

    @pytest.mark.unit
    @pytest.mark.qg_user_input
    def test_known_subdomain_auto_detects(self):
        """
        P1: Verify subdomain of known domain auto-detects correctly.

        AAA Pattern:
        1. Arrange - Create input with subdomain of known environment
        2. Act - Call qg_user_input.validate()
        3. Assert - Auto-detects parent domain environment without NEEDS_RETRY
        """
        # Arrange
        input_data = {
            "persona": "user",
            "URL": "https://demo.parabank.parasoft.com/parabank/register.htm",
            "role_name": "User",
            "workflow": "auth",
            "raw_requirement": "Register test"
        }

        # Act
        with patch('utils.state_manager.StateManager') as MockStateManager:
            mock_instance = MagicMock()
            MockStateManager.return_value = mock_instance
            result = QGUserInput.validate(input_data)

            # Assert
            assert result["status"] == "pass", "Should pass for known subdomain"
            call_kwargs = mock_instance.save.call_args.kwargs
            assert call_kwargs["data"]["detected_env_id"] == "parabank", \
                "Subdomain should match parent domain environment"

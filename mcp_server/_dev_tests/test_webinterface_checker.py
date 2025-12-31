"""
Unit Tests - WebInterface Checker (Task 7.0)

Tests the WebInterfaceChecker module:
- method_exists() for valid/invalid methods
- get_method_signature() returns correct signature
- get_available_methods() lists all public methods
- get_method_info() returns full method details
- validate_method_call() checks argument counts
- Similar method suggestions for typos

Following testing skill conventions.
"""

import pytest
from typing import List

from mcp_server.utils.webinterface_checker import (
    WebInterfaceChecker,
    MethodInfo,
    MethodSignature,
    MethodParameter,
    create_checker,
    method_exists_in_webinterface,
    get_webinterface_methods
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def checker():
    """Create a WebInterfaceChecker with real WebInterface."""
    return WebInterfaceChecker()


@pytest.fixture
def mock_class():
    """Create a mock class for testing introspection."""

    class MockWebInterface:
        """Mock WebInterface for testing."""

        def __init__(self, driver, config, logger):
            self.driver = driver
            self.config = config
            self.logger = logger

        def click(self, by, value, timeout=None) -> None:
            """Click an element."""
            pass

        def type_text(self, by, value, text: str, clear_first: bool = True, timeout=None) -> None:
            """Type text into an element."""
            pass

        def find_element(self, by, value, timeout=None):
            """Find a single element."""
            pass

        def get_text(self, by, value, timeout=None) -> str:
            """Get element text."""
            return ""

        def _private_method(self) -> None:
            """Private method."""
            pass

        def method_no_params(self) -> bool:
            """Method with no parameters."""
            return True

    return MockWebInterface


@pytest.fixture
def mock_checker(mock_class):
    """Create checker with mock class."""
    return WebInterfaceChecker(mock_class)


# =============================================================================
# TEST: Method Exists
# =============================================================================

class TestMethodExists:
    """Test method_exists() functionality."""

    @pytest.mark.webinterface_checker
    def test_exists_for_known_method(self, checker):
        """Returns True for known WebInterface methods."""
        assert checker.method_exists("click") is True
        assert checker.method_exists("type_text") is True
        assert checker.method_exists("find_element") is True

    @pytest.mark.webinterface_checker
    def test_not_exists_for_unknown_method(self, checker):
        """Returns False for non-existent methods."""
        assert checker.method_exists("nonexistent_method") is False
        assert checker.method_exists("fake_click") is False

    @pytest.mark.webinterface_checker
    def test_exists_for_private_method(self, checker):
        """Returns True for private methods (they exist)."""
        # _take_screenshot exists but is private
        assert checker.method_exists("_take_screenshot") is True

    @pytest.mark.webinterface_checker
    def test_not_exists_for_dunder_methods(self, checker):
        """Skips __dunder__ methods."""
        assert checker.method_exists("__init__") is False
        assert checker.method_exists("__repr__") is False

    @pytest.mark.webinterface_checker
    def test_exists_with_mock_class(self, mock_checker):
        """Works with mock class."""
        assert mock_checker.method_exists("click") is True
        assert mock_checker.method_exists("type_text") is True
        assert mock_checker.method_exists("not_real") is False


# =============================================================================
# TEST: Get Method Signature
# =============================================================================

class TestGetMethodSignature:
    """Test get_method_signature() functionality."""

    @pytest.mark.webinterface_checker
    def test_returns_signature_for_valid_method(self, checker):
        """Returns MethodSignature for valid methods."""
        sig = checker.get_method_signature("click")
        assert sig is not None
        assert isinstance(sig, MethodSignature)
        assert sig.name == "click"

    @pytest.mark.webinterface_checker
    def test_signature_has_parameters(self, checker):
        """Signature includes method parameters."""
        sig = checker.get_method_signature("click")
        assert len(sig.parameters) > 0
        param_names = [p.name for p in sig.parameters]
        assert "by" in param_names
        assert "value" in param_names

    @pytest.mark.webinterface_checker
    def test_signature_has_optional_params(self, checker):
        """Identifies optional parameters with defaults."""
        sig = checker.get_method_signature("click")
        timeout_param = next((p for p in sig.parameters if p.name == "timeout"), None)
        assert timeout_param is not None
        assert timeout_param.has_default is True

    @pytest.mark.webinterface_checker
    def test_signature_has_return_type(self, checker):
        """Captures return type annotation."""
        sig = checker.get_method_signature("get_text")
        assert sig.return_annotation is not None
        assert "str" in sig.return_annotation

    @pytest.mark.webinterface_checker
    def test_returns_none_for_invalid_method(self, checker):
        """Returns None for non-existent methods."""
        sig = checker.get_method_signature("not_a_method")
        assert sig is None

    @pytest.mark.webinterface_checker
    def test_signature_has_docstring(self, mock_checker):
        """Captures method docstring."""
        sig = mock_checker.get_method_signature("click")
        assert sig.docstring is not None
        assert "Click" in sig.docstring


# =============================================================================
# TEST: Get Method Info
# =============================================================================

class TestGetMethodInfo:
    """Test get_method_info() functionality."""

    @pytest.mark.webinterface_checker
    def test_returns_info_for_valid_method(self, checker):
        """Returns MethodInfo for valid methods."""
        info = checker.get_method_info("click")
        assert info is not None
        assert isinstance(info, MethodInfo)

    @pytest.mark.webinterface_checker
    def test_info_includes_signature(self, checker):
        """MethodInfo includes signature."""
        info = checker.get_method_info("click")
        assert info.signature is not None
        assert info.signature.name == "click"

    @pytest.mark.webinterface_checker
    def test_info_identifies_public_methods(self, mock_checker):
        """Correctly identifies public methods."""
        info = mock_checker.get_method_info("click")
        assert info.is_public is True

    @pytest.mark.webinterface_checker
    def test_info_identifies_private_methods(self, mock_checker):
        """Correctly identifies private methods."""
        info = mock_checker.get_method_info("_private_method")
        assert info is not None
        assert info.is_public is False

    @pytest.mark.webinterface_checker
    def test_info_includes_category(self, checker):
        """Includes category for categorized methods."""
        info = checker.get_method_info("click")
        assert info.category == "Interaction"

        info = checker.get_method_info("navigate_to")
        assert info.category == "Navigation"

    @pytest.mark.webinterface_checker
    def test_returns_none_for_invalid_method(self, checker):
        """Returns None for non-existent methods."""
        info = checker.get_method_info("fake_method")
        assert info is None


# =============================================================================
# TEST: Get Available Methods
# =============================================================================

class TestGetAvailableMethods:
    """Test get_available_methods() functionality."""

    @pytest.mark.webinterface_checker
    def test_returns_list_of_method_info(self, checker):
        """Returns list of MethodInfo objects."""
        methods = checker.get_available_methods()
        assert isinstance(methods, list)
        assert len(methods) > 0
        assert all(isinstance(m, MethodInfo) for m in methods)

    @pytest.mark.webinterface_checker
    def test_default_returns_public_only(self, mock_checker):
        """By default only returns public methods."""
        methods = mock_checker.get_available_methods(public_only=True)
        assert all(m.is_public for m in methods)
        names = [m.name for m in methods]
        assert "_private_method" not in names

    @pytest.mark.webinterface_checker
    def test_can_include_private_methods(self, mock_checker):
        """Can include private methods when requested."""
        methods = mock_checker.get_available_methods(public_only=False)
        names = [m.name for m in methods]
        assert "_private_method" in names

    @pytest.mark.webinterface_checker
    def test_methods_sorted_by_category(self, checker):
        """Methods are sorted by category then name."""
        methods = checker.get_available_methods()
        categories = [m.category for m in methods if m.category]
        # Categories should be in sorted order
        assert categories == sorted(categories)

    @pytest.mark.webinterface_checker
    def test_includes_common_methods(self, checker):
        """Includes common WebInterface methods."""
        methods = checker.get_available_methods()
        names = [m.name for m in methods]
        assert "click" in names
        assert "type_text" in names
        assert "find_element" in names
        assert "navigate_to" in names


# =============================================================================
# TEST: Get Methods By Category
# =============================================================================

class TestGetMethodsByCategory:
    """Test get_methods_by_category() functionality."""

    @pytest.mark.webinterface_checker
    def test_returns_methods_in_category(self, checker):
        """Returns methods in specified category."""
        methods = checker.get_methods_by_category("Navigation")
        assert len(methods) > 0
        assert all(m.category == "Navigation" for m in methods)

    @pytest.mark.webinterface_checker
    def test_navigation_category(self, checker):
        """Navigation category has expected methods."""
        methods = checker.get_methods_by_category("Navigation")
        names = [m.name for m in methods]
        assert "navigate_to" in names
        assert "refresh_page" in names
        assert "go_back" in names

    @pytest.mark.webinterface_checker
    def test_interaction_category(self, checker):
        """Interaction category has expected methods."""
        methods = checker.get_methods_by_category("Interaction")
        names = [m.name for m in methods]
        assert "click" in names
        assert "type_text" in names
        assert "get_text" in names

    @pytest.mark.webinterface_checker
    def test_wait_category(self, checker):
        """Wait category has expected methods."""
        methods = checker.get_methods_by_category("Wait")
        names = [m.name for m in methods]
        assert "wait_for_element_visible" in names

    @pytest.mark.webinterface_checker
    def test_empty_for_invalid_category(self, checker):
        """Returns empty list for invalid category."""
        methods = checker.get_methods_by_category("InvalidCategory")
        assert methods == []


# =============================================================================
# TEST: Get Method Names
# =============================================================================

class TestGetMethodNames:
    """Test get_method_names() functionality."""

    @pytest.mark.webinterface_checker
    def test_returns_list_of_strings(self, checker):
        """Returns list of method name strings."""
        names = checker.get_method_names()
        assert isinstance(names, list)
        assert all(isinstance(n, str) for n in names)

    @pytest.mark.webinterface_checker
    def test_public_only_by_default(self, mock_checker):
        """Default returns only public method names."""
        names = mock_checker.get_method_names(public_only=True)
        assert "_private_method" not in names
        assert "click" in names


# =============================================================================
# TEST: Validate Method Call
# =============================================================================

class TestValidateMethodCall:
    """Test validate_method_call() functionality."""

    @pytest.mark.webinterface_checker
    def test_valid_for_existing_method(self, mock_checker):
        """Returns valid=True for existing public methods."""
        result = mock_checker.validate_method_call("click")
        assert result["valid"] is True

    @pytest.mark.webinterface_checker
    def test_invalid_for_nonexistent_method(self, mock_checker):
        """Returns valid=False for non-existent methods."""
        result = mock_checker.validate_method_call("fake_method")
        assert result["valid"] is False
        assert "does not exist" in result["reason"]

    @pytest.mark.webinterface_checker
    def test_invalid_for_private_method(self, mock_checker):
        """Returns valid=False for private methods."""
        result = mock_checker.validate_method_call("_private_method")
        assert result["valid"] is False
        assert "private" in result["reason"]

    @pytest.mark.webinterface_checker
    def test_suggests_similar_methods(self, mock_checker):
        """Suggests similar methods for typos."""
        result = mock_checker.validate_method_call("clik")  # typo of "click"
        assert result["valid"] is False
        assert "similar_methods" in result
        assert "click" in result["similar_methods"]

    @pytest.mark.webinterface_checker
    def test_arg_count_too_few(self, mock_checker):
        """Detects too few arguments."""
        # click requires by and value (2 required params)
        result = mock_checker.validate_method_call("click", arg_count=1)
        assert result["valid"] is False
        assert "requires at least" in result["reason"]

    @pytest.mark.webinterface_checker
    def test_arg_count_correct(self, mock_checker):
        """Accepts correct argument count."""
        result = mock_checker.validate_method_call("click", arg_count=2)
        assert result["valid"] is True

    @pytest.mark.webinterface_checker
    def test_arg_count_with_optional(self, mock_checker):
        """Accepts argument count including optional params."""
        # click has by, value (required) and timeout (optional)
        result = mock_checker.validate_method_call("click", arg_count=3)
        assert result["valid"] is True

    @pytest.mark.webinterface_checker
    def test_arg_count_too_many(self, mock_checker):
        """Detects too many arguments."""
        result = mock_checker.validate_method_call("method_no_params", arg_count=2)
        assert result["valid"] is False
        assert "at most" in result["reason"]


# =============================================================================
# TEST: Method Parameter
# =============================================================================

class TestMethodParameter:
    """Test MethodParameter dataclass."""

    @pytest.mark.webinterface_checker
    def test_repr_simple(self):
        """Simple parameter repr."""
        param = MethodParameter(name="value")
        assert str(param) == "value"

    @pytest.mark.webinterface_checker
    def test_repr_with_annotation(self):
        """Parameter with annotation."""
        param = MethodParameter(name="text", annotation="str")
        assert "text" in str(param)
        assert "str" in str(param)

    @pytest.mark.webinterface_checker
    def test_repr_with_default(self):
        """Parameter with default value."""
        param = MethodParameter(
            name="timeout",
            annotation="int",
            has_default=True,
            default_value=10
        )
        assert "timeout" in str(param)
        assert "10" in str(param)


# =============================================================================
# TEST: Method Signature
# =============================================================================

class TestMethodSignature:
    """Test MethodSignature dataclass."""

    @pytest.mark.webinterface_checker
    def test_repr_no_params(self):
        """Signature with no parameters."""
        sig = MethodSignature(name="quit")
        assert str(sig) == "quit()"

    @pytest.mark.webinterface_checker
    def test_repr_with_return(self):
        """Signature with return type."""
        sig = MethodSignature(name="get_text", return_annotation="str")
        assert "get_text()" in str(sig)
        assert "-> str" in str(sig)


# =============================================================================
# TEST: Convenience Functions
# =============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    @pytest.mark.webinterface_checker
    def test_create_checker(self, mock_class):
        """create_checker() creates working instance."""
        checker = create_checker(mock_class)
        assert checker is not None
        assert checker.method_exists("click") is True

    @pytest.mark.webinterface_checker
    def test_method_exists_in_webinterface(self):
        """method_exists_in_webinterface() works end-to-end."""
        # This test uses the real WebInterface
        assert method_exists_in_webinterface("click") is True
        assert method_exists_in_webinterface("not_a_method") is False

    @pytest.mark.webinterface_checker
    def test_get_webinterface_methods(self):
        """get_webinterface_methods() returns method list."""
        methods = get_webinterface_methods()
        assert isinstance(methods, list)
        assert "click" in methods
        assert "type_text" in methods


# =============================================================================
# TEST: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.webinterface_checker
    def test_empty_method_name(self, checker):
        """Handles empty method name."""
        assert checker.method_exists("") is False
        sig = checker.get_method_signature("")
        assert sig is None

    @pytest.mark.webinterface_checker
    def test_none_class_loads_real(self):
        """None class parameter loads real WebInterface."""
        checker = WebInterfaceChecker(None)
        # Should work if framework is importable
        methods = checker.get_method_names()
        # Either returns methods or empty if import fails
        assert isinstance(methods, list)

    @pytest.mark.webinterface_checker
    def test_caching_works(self, mock_checker):
        """Methods are cached after first load."""
        # First call loads
        mock_checker.method_exists("click")
        assert mock_checker._loaded is True

        # Subsequent calls use cache
        mock_checker.method_exists("type_text")
        assert mock_checker._loaded is True

    @pytest.mark.webinterface_checker
    def test_find_similar_empty_cache(self):
        """Similar method search handles empty cache."""
        checker = WebInterfaceChecker()
        # Before loading
        similar = checker._find_similar_methods("click")
        # Should not error, may return empty or try to load
        assert isinstance(similar, list)


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

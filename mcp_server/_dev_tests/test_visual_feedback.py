"""
Unit Tests - Visual Feedback (Task 6.0)

Tests the VisualFeedback module:
- Headless mode gracefully skips visuals
- highlight_valid/invalid inject correct CSS
- show_pipeline_header displays 3-step status
- update_step_status updates individual steps
- show_results_panel displays element list
- cleanup removes injected elements

Following testing skill conventions.
"""

import pytest
from typing import Any, List

from mcp_server.utils.visual_feedback import (
    VisualFeedback,
    create_visual_feedback,
    format_validation_summary,
    format_scope_summary,
    VALIDATION_CSS,
    CLEANUP_JS
)


# =============================================================================
# FIXTURES
# =============================================================================

class MockBrowserEvaluate:
    """Mock Playwright browser_evaluate for testing."""

    def __init__(self):
        self.calls: List[str] = []
        self.return_value: Any = True

    def __call__(self, js: str) -> Any:
        self.calls.append(js)
        return self.return_value

    def reset(self):
        self.calls = []

    @property
    def call_count(self) -> int:
        return len(self.calls)

    def last_call_contains(self, text: str) -> bool:
        if not self.calls:
            return False
        return text in self.calls[-1]


@pytest.fixture
def mock_evaluate():
    """Create a mock browser_evaluate function."""
    return MockBrowserEvaluate()


@pytest.fixture
def visual_feedback(mock_evaluate):
    """Create a VisualFeedback with mock evaluate function."""
    return VisualFeedback(evaluate_fn=mock_evaluate)


@pytest.fixture
def headless_feedback():
    """Create a VisualFeedback in headless mode (no evaluate function)."""
    return VisualFeedback()


# =============================================================================
# TEST: Headless Mode
# =============================================================================

class TestHeadlessMode:
    """Test headless mode gracefully skips all visuals."""

    @pytest.mark.visual_feedback
    def test_headless_detected_when_no_evaluate_fn(self, headless_feedback):
        """Detects headless mode when no evaluate function provided."""
        assert headless_feedback.is_headless is True

    @pytest.mark.visual_feedback
    def test_headless_not_detected_with_evaluate_fn(self, visual_feedback):
        """Not headless when evaluate function provided."""
        assert visual_feedback.is_headless is False

    @pytest.mark.visual_feedback
    def test_headless_initialize_returns_false(self, headless_feedback):
        """initialize() returns False in headless mode."""
        result = headless_feedback.initialize()
        assert result is False

    @pytest.mark.visual_feedback
    def test_headless_highlight_valid_returns_false(self, headless_feedback):
        """highlight_valid() returns False in headless mode."""
        result = headless_feedback.highlight_valid("e72")
        assert result is False

    @pytest.mark.visual_feedback
    def test_headless_highlight_invalid_returns_false(self, headless_feedback):
        """highlight_invalid() returns False in headless mode."""
        result = headless_feedback.highlight_invalid("e72", "NOT_VISIBLE")
        assert result is False

    @pytest.mark.visual_feedback
    def test_headless_show_pipeline_header_returns_false(self, headless_feedback):
        """show_pipeline_header() returns False in headless mode."""
        result = headless_feedback.show_pipeline_header()
        assert result is False

    @pytest.mark.visual_feedback
    def test_headless_cleanup_returns_false(self, headless_feedback):
        """cleanup() returns False in headless mode."""
        result = headless_feedback.cleanup()
        assert result is False


# =============================================================================
# TEST: Initialize
# =============================================================================

class TestInitialize:
    """Test initialization of visual feedback."""

    @pytest.mark.visual_feedback
    def test_initialize_injects_css(self, visual_feedback, mock_evaluate):
        """initialize() injects CSS styles."""
        visual_feedback.initialize()

        # Should have made calls to inject CSS and create overlay
        assert mock_evaluate.call_count >= 2

    @pytest.mark.visual_feedback
    def test_initialize_sets_initialized_flag(self, visual_feedback):
        """initialize() sets _initialized flag."""
        assert visual_feedback.is_initialized is False
        visual_feedback.initialize()
        assert visual_feedback.is_initialized is True

    @pytest.mark.visual_feedback
    def test_initialize_returns_true_on_success(self, visual_feedback):
        """initialize() returns True on success."""
        result = visual_feedback.initialize()
        assert result is True


# =============================================================================
# TEST: Highlight Valid
# =============================================================================

class TestHighlightValid:
    """Test highlighting valid elements."""

    @pytest.mark.visual_feedback
    def test_highlight_valid_calls_evaluate(self, visual_feedback, mock_evaluate):
        """highlight_valid() calls evaluate function."""
        visual_feedback.highlight_valid("e72")
        assert mock_evaluate.call_count == 1

    @pytest.mark.visual_feedback
    def test_highlight_valid_uses_correct_ref(self, visual_feedback, mock_evaluate):
        """highlight_valid() includes the element ref."""
        visual_feedback.highlight_valid("e72")
        assert mock_evaluate.last_call_contains("e72")

    @pytest.mark.visual_feedback
    def test_highlight_valid_sets_is_valid_true(self, visual_feedback, mock_evaluate):
        """highlight_valid() sets isValid to true."""
        visual_feedback.highlight_valid("e72")
        assert mock_evaluate.last_call_contains("true")

    @pytest.mark.visual_feedback
    def test_highlight_valid_returns_true(self, visual_feedback):
        """highlight_valid() returns True on success."""
        result = visual_feedback.highlight_valid("e72")
        assert result is True


# =============================================================================
# TEST: Highlight Invalid
# =============================================================================

class TestHighlightInvalid:
    """Test highlighting invalid elements."""

    @pytest.mark.visual_feedback
    def test_highlight_invalid_calls_evaluate(self, visual_feedback, mock_evaluate):
        """highlight_invalid() calls evaluate function."""
        visual_feedback.highlight_invalid("e99", "NOT_VISIBLE")
        assert mock_evaluate.call_count == 1

    @pytest.mark.visual_feedback
    def test_highlight_invalid_uses_correct_ref(self, visual_feedback, mock_evaluate):
        """highlight_invalid() includes the element ref."""
        visual_feedback.highlight_invalid("e99", "NOT_VISIBLE")
        assert mock_evaluate.last_call_contains("e99")

    @pytest.mark.visual_feedback
    def test_highlight_invalid_includes_error_category(self, visual_feedback, mock_evaluate):
        """highlight_invalid() includes error category."""
        visual_feedback.highlight_invalid("e99", "NOT_VISIBLE")
        assert mock_evaluate.last_call_contains("NOT_VISIBLE")

    @pytest.mark.visual_feedback
    def test_highlight_invalid_sets_is_valid_false(self, visual_feedback, mock_evaluate):
        """highlight_invalid() sets isValid to false."""
        visual_feedback.highlight_invalid("e99", "NOT_INTERACTABLE")
        assert mock_evaluate.last_call_contains("false")

    @pytest.mark.visual_feedback
    def test_highlight_invalid_returns_true(self, visual_feedback):
        """highlight_invalid() returns True on success."""
        result = visual_feedback.highlight_invalid("e99", "NOT_VISIBLE")
        assert result is True


# =============================================================================
# TEST: Highlight Element (Generic)
# =============================================================================

class TestHighlightElement:
    """Test generic highlight_element method."""

    @pytest.mark.visual_feedback
    def test_highlight_element_valid_status(self, visual_feedback, mock_evaluate):
        """highlight_element() with 'valid' status calls highlight_valid."""
        visual_feedback.highlight_element("e72", "valid")
        assert mock_evaluate.last_call_contains("true")

    @pytest.mark.visual_feedback
    def test_highlight_element_invalid_status(self, visual_feedback, mock_evaluate):
        """highlight_element() with 'invalid' status calls highlight_invalid."""
        visual_feedback.highlight_element("e99", "invalid", "NOT_VISIBLE")
        assert mock_evaluate.last_call_contains("false")
        assert mock_evaluate.last_call_contains("NOT_VISIBLE")


# =============================================================================
# TEST: Pipeline Header
# =============================================================================

class TestPipelineHeader:
    """Test 3-step pipeline header display."""

    @pytest.mark.visual_feedback
    def test_show_pipeline_header_initializes_if_needed(self, visual_feedback, mock_evaluate):
        """show_pipeline_header() initializes if not already initialized."""
        visual_feedback.show_pipeline_header()
        # Should call initialize (CSS + overlay) plus step updates
        assert mock_evaluate.call_count >= 3

    @pytest.mark.visual_feedback
    def test_show_pipeline_header_with_scope_result(self, visual_feedback, mock_evaluate):
        """show_pipeline_header() displays scope discovery result."""
        scope = format_scope_summary(1, ["LoginPage"])
        visual_feedback.show_pipeline_header(scope_result=scope)

        # Should contain step 1 update with scope info
        calls_text = " ".join(mock_evaluate.calls)
        assert "ScopeDiscovery" in calls_text
        assert "Single Page" in calls_text or "1" in calls_text

    @pytest.mark.visual_feedback
    def test_show_pipeline_header_with_validation_results(self, visual_feedback, mock_evaluate):
        """show_pipeline_header() displays validation results."""
        validation = format_validation_summary(4, 0)
        visual_feedback.show_pipeline_header(validation_results=validation)

        calls_text = " ".join(mock_evaluate.calls)
        assert "RuntimeValidator" in calls_text
        assert "4 Valid" in calls_text

    @pytest.mark.visual_feedback
    def test_show_pipeline_header_with_kb_status(self, visual_feedback, mock_evaluate):
        """show_pipeline_header() displays KB status."""
        visual_feedback.show_pipeline_header(kb_status="Patterns Ready")

        calls_text = " ".join(mock_evaluate.calls)
        assert "KnowledgeBase" in calls_text
        assert "Patterns Ready" in calls_text

    @pytest.mark.visual_feedback
    def test_show_pipeline_header_pending_without_results(self, visual_feedback, mock_evaluate):
        """show_pipeline_header() shows PENDING when no results provided."""
        visual_feedback.show_pipeline_header()

        calls_text = " ".join(mock_evaluate.calls)
        assert "PENDING" in calls_text


# =============================================================================
# TEST: Update Step Status
# =============================================================================

class TestUpdateStepStatus:
    """Test updating individual step status."""

    @pytest.mark.visual_feedback
    def test_update_step_status_calls_evaluate(self, visual_feedback, mock_evaluate):
        """update_step_status() calls evaluate function."""
        visual_feedback.update_step_status(1, "ScopeDiscovery", "OK", "Single Page")
        assert mock_evaluate.call_count == 1

    @pytest.mark.visual_feedback
    def test_update_step_status_includes_step_number(self, visual_feedback, mock_evaluate):
        """update_step_status() includes step number."""
        visual_feedback.update_step_status(2, "RuntimeValidator", "OK", "4 Valid")
        # Step number should be in the JS call
        assert "2" in mock_evaluate.calls[-1]

    @pytest.mark.visual_feedback
    def test_update_step_status_includes_step_name(self, visual_feedback, mock_evaluate):
        """update_step_status() includes step name."""
        visual_feedback.update_step_status(1, "ScopeDiscovery", "OK", "Done")
        assert mock_evaluate.last_call_contains("ScopeDiscovery")

    @pytest.mark.visual_feedback
    def test_update_step_status_includes_status(self, visual_feedback, mock_evaluate):
        """update_step_status() includes status."""
        visual_feedback.update_step_status(1, "Test", "FAIL", "Error occurred")
        assert mock_evaluate.last_call_contains("FAIL")


# =============================================================================
# TEST: Results Panel
# =============================================================================

class TestResultsPanel:
    """Test element-by-element results panel."""

    @pytest.mark.visual_feedback
    def test_show_results_panel_with_results(self, visual_feedback, mock_evaluate):
        """show_results_panel() displays all results."""
        results = [
            {"element_name": "Email", "ref": "e72", "is_valid": True},
            {"element_name": "Password", "ref": "e75", "is_valid": True},
            {"element_name": "Hidden", "ref": "e99", "is_valid": False, "error_category": "NOT_VISIBLE"}
        ]
        visual_feedback.show_results_panel(results)

        # Should have called evaluate for each result
        assert mock_evaluate.call_count == 3

    @pytest.mark.visual_feedback
    def test_show_results_panel_includes_element_names(self, visual_feedback, mock_evaluate):
        """show_results_panel() includes element names."""
        results = [{"element_name": "Email Field", "ref": "e72", "is_valid": True}]
        visual_feedback.show_results_panel(results)
        assert mock_evaluate.last_call_contains("Email Field")

    @pytest.mark.visual_feedback
    def test_add_result_single_item(self, visual_feedback, mock_evaluate):
        """add_result() adds single result to panel."""
        visual_feedback.add_result("Sign in", "e79", True)
        assert mock_evaluate.call_count == 1
        assert mock_evaluate.last_call_contains("Sign in")


# =============================================================================
# TEST: Cleanup
# =============================================================================

class TestCleanup:
    """Test cleanup of injected elements."""

    @pytest.mark.visual_feedback
    def test_cleanup_calls_evaluate(self, visual_feedback, mock_evaluate):
        """cleanup() calls evaluate function."""
        visual_feedback.initialize()
        mock_evaluate.reset()

        visual_feedback.cleanup()
        assert mock_evaluate.call_count == 1

    @pytest.mark.visual_feedback
    def test_cleanup_resets_initialized_flag(self, visual_feedback):
        """cleanup() resets _initialized flag."""
        visual_feedback.initialize()
        assert visual_feedback.is_initialized is True

        visual_feedback.cleanup()
        assert visual_feedback.is_initialized is False

    @pytest.mark.visual_feedback
    def test_cleanup_returns_true(self, visual_feedback):
        """cleanup() returns True on success."""
        result = visual_feedback.cleanup()
        assert result is True


# =============================================================================
# TEST: Error Handling
# =============================================================================

class TestErrorHandling:
    """Test error handling when evaluate fails."""

    @pytest.mark.visual_feedback
    def test_highlight_valid_handles_exception(self, mock_evaluate):
        """highlight_valid() handles exceptions gracefully."""
        def raise_error(js):
            raise RuntimeError("Browser disconnected")

        vf = VisualFeedback(evaluate_fn=raise_error)
        result = vf.highlight_valid("e72")
        assert result is False

    @pytest.mark.visual_feedback
    def test_highlight_invalid_handles_exception(self, mock_evaluate):
        """highlight_invalid() handles exceptions gracefully."""
        def raise_error(js):
            raise RuntimeError("Browser disconnected")

        vf = VisualFeedback(evaluate_fn=raise_error)
        result = vf.highlight_invalid("e72", "NOT_VISIBLE")
        assert result is False

    @pytest.mark.visual_feedback
    def test_cleanup_handles_exception(self, mock_evaluate):
        """cleanup() handles exceptions gracefully."""
        def raise_error(js):
            raise RuntimeError("Browser disconnected")

        vf = VisualFeedback(evaluate_fn=raise_error)
        result = vf.cleanup()
        assert result is False


# =============================================================================
# TEST: Convenience Functions
# =============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    @pytest.mark.visual_feedback
    def test_create_visual_feedback_with_evaluate(self, mock_evaluate):
        """create_visual_feedback() creates working instance."""
        vf = create_visual_feedback(evaluate_fn=mock_evaluate)
        assert vf is not None
        assert vf.is_headless is False

    @pytest.mark.visual_feedback
    def test_create_visual_feedback_headless(self):
        """create_visual_feedback() without evaluate is headless."""
        vf = create_visual_feedback()
        assert vf.is_headless is True

    @pytest.mark.visual_feedback
    def test_format_validation_summary(self):
        """format_validation_summary() creates correct dict."""
        result = format_validation_summary(5, 2)
        assert result["valid_count"] == 5
        assert result["error_count"] == 2

    @pytest.mark.visual_feedback
    def test_format_scope_summary(self):
        """format_scope_summary() creates correct dict."""
        result = format_scope_summary(2, ["LoginPage", "DashboardPage"])
        assert result["page_count"] == 2
        assert len(result["pages"]) == 2
        assert result["pages"][0]["name"] == "LoginPage"


# =============================================================================
# TEST: CSS Constants
# =============================================================================

class TestCSSConstants:
    """Test CSS constants are properly defined."""

    @pytest.mark.visual_feedback
    def test_validation_css_contains_highlight_classes(self):
        """VALIDATION_CSS contains required highlight classes."""
        assert "qa-element-highlight-valid" in VALIDATION_CSS
        assert "qa-element-highlight-invalid" in VALIDATION_CSS

    @pytest.mark.visual_feedback
    def test_validation_css_contains_green_color(self):
        """VALIDATION_CSS uses green for valid elements."""
        assert "#00ff00" in VALIDATION_CSS

    @pytest.mark.visual_feedback
    def test_validation_css_contains_red_color(self):
        """VALIDATION_CSS uses red for invalid elements."""
        assert "#ff0000" in VALIDATION_CSS

    @pytest.mark.visual_feedback
    def test_validation_css_contains_overlay_class(self):
        """VALIDATION_CSS contains overlay class."""
        assert "qa-validation-overlay" in VALIDATION_CSS


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

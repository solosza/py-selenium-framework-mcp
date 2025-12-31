"""
Unit tests for QGDiscoveredElements - Task 2.0

Test suite for Step 5 quality gate with per-page discovery extensions.

Test Matrix:
- PRE validation: 8 tests (P0)
- POST validation: 6 tests (P0)
- Scope validation: 4 tests (P1) - NEW Task 2.0
- Per-page tracking: 4 tests (P1) - NEW Task 2.0
- Discovery progress: 3 tests (P1) - NEW Task 2.0

Testing Skill Reference: .claude/skills/testing/
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.gates.qg_discovered_elements import QGDiscoveredElements
from utils.state_manager import StateManager


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def mock_state_manager(tmp_path):
    """Create a StateManager with temp file for test isolation."""
    state_file = tmp_path / "test_workflow_state.json"
    manager = StateManager(state_file=str(state_file))
    # Mark Step 4 as complete (prerequisite for Step 5)
    manager.save(4, {"test_scenarios": [{"given": "...", "when": "...", "then": "..."}]})
    return manager


@pytest.fixture
def valid_pre_input():
    """Valid PRE mode input data."""
    return {
        "mode": "PRE",
        "url": "http://example.com/login",
        "page_name": "LoginPage",
        "credential_strategy": "static",
        "discovery_method": "playwright"
    }


@pytest.fixture
def valid_post_input():
    """Valid POST mode input data."""
    return {
        "mode": "POST",
        "page_name": "LoginPage",
        "elements": [
            {
                "suggested_name": "EMAIL_INPUT",
                "element_type": "textbox",
                "locator_id": "#email",
                "locator_css": "input[name='email']",
                "locator_xpath": "//input[@id='email']"
            },
            {
                "suggested_name": "SUBMIT_BUTTON",
                "element_type": "button",
                "locator_css": "button[type='submit']",
                "locator_id": "",
                "locator_xpath": ""
            }
        ]
    }


@pytest.fixture
def multi_page_scope_result():
    """Scope result for multi-page workflow."""
    return {
        "page_count": 3,
        "pages": [
            {"name": "LoginPage", "order": 1},
            {"name": "DashboardPage", "order": 2},
            {"name": "SettingsPage", "order": 3}
        ]
    }


@pytest.fixture
def single_page_scope_result():
    """Scope result for single-page workflow."""
    return {
        "page_count": 1,
        "pages": [
            {"name": "MainPage", "order": 1}
        ]
    }


# ============================================================================
# PRE VALIDATION TESTS
# ============================================================================

class TestQGDiscoveredElementsPREValidation:
    """PRE mode validation tests."""

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_pre_valid_input_passes(self, mock_state_manager, valid_pre_input):
        """
        P0: Valid PRE input should pass validation.

        AAA Pattern:
        1. Arrange - Set up valid input with Step 4 complete
        2. Act - Validate PRE
        3. Assert - Returns pass status
        """
        # Arrange
        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            # Act
            result = QGDiscoveredElements.validate(valid_pre_input)

        # Assert
        assert result["status"] == "pass", f"Valid PRE input should pass, got {result}"

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_pre_missing_url_fails(self, mock_state_manager, valid_pre_input):
        """
        P0: Missing URL should fail PRE validation.
        """
        # Arrange
        del valid_pre_input["url"]

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            # Act
            result = QGDiscoveredElements.validate(valid_pre_input)

        # Assert
        assert result["status"] == "fail"
        assert "url" in result["error"].lower()

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_pre_invalid_url_format_fails(self, mock_state_manager, valid_pre_input):
        """
        P0: URL without http/https should fail.
        """
        # Arrange
        valid_pre_input["url"] = "example.com/login"

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            # Act
            result = QGDiscoveredElements.validate(valid_pre_input)

        # Assert
        assert result["status"] == "fail"
        assert "http" in result["error"].lower()

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_pre_missing_credential_strategy_fails(self, mock_state_manager, valid_pre_input):
        """
        P0: Missing credential_strategy should fail (IC-05-01).
        """
        # Arrange
        del valid_pre_input["credential_strategy"]

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            # Act
            result = QGDiscoveredElements.validate(valid_pre_input)

        # Assert
        assert result["status"] == "fail"
        assert "credential_strategy" in result["error"].lower()

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_pre_invalid_discovery_method_fails(self, mock_state_manager, valid_pre_input):
        """
        P0: Invalid discovery_method should fail (DD-33).
        """
        # Arrange
        valid_pre_input["discovery_method"] = "invalid"

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            # Act
            result = QGDiscoveredElements.validate(valid_pre_input)

        # Assert
        assert result["status"] == "fail"
        assert "discovery_method" in result["error"].lower()

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_pre_step4_incomplete_fails(self, tmp_path, valid_pre_input):
        """
        P0: Should fail if Step 4 is not complete.
        """
        # Arrange - Create state manager WITHOUT Step 4 complete
        state_file = tmp_path / "test_workflow_state.json"
        manager = StateManager(state_file=str(state_file))
        # Don't save Step 4

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=manager):
            # Act
            result = QGDiscoveredElements.validate(valid_pre_input)

        # Assert
        assert result["status"] == "fail"
        assert "step 4" in result["error"].lower()


# ============================================================================
# POST VALIDATION TESTS
# ============================================================================

class TestQGDiscoveredElementsPOSTValidation:
    """POST mode validation tests."""

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_post_valid_input_passes(self, mock_state_manager, valid_post_input):
        """
        P0: Valid POST input should pass validation.
        """
        # Arrange
        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager

            # Act
            result = QGDiscoveredElements.validate(valid_post_input)

        # Assert
        assert result["status"] == "pass", f"Valid POST input should pass, got {result}"

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_post_empty_elements_fails(self, mock_state_manager, valid_post_input):
        """
        P0: Empty elements array should fail.
        """
        # Arrange
        valid_post_input["elements"] = []

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager

            # Act
            result = QGDiscoveredElements.validate(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "empty" in result["error"].lower()

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_post_element_missing_locator_fails(self, mock_state_manager, valid_post_input):
        """
        P0: Element without any valid locator should fail (IC-05-03).
        """
        # Arrange
        valid_post_input["elements"] = [{
            "suggested_name": "BUTTON",
            "element_type": "button",
            "locator_id": "",
            "locator_css": "",
            "locator_xpath": ""
        }]

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager

            # Act
            result = QGDiscoveredElements.validate(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "locator" in result["error"].lower()

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_post_non_pascal_case_page_name_fails(self, mock_state_manager, valid_post_input):
        """
        P0: Non-PascalCase page_name should fail (IC-05-02).
        """
        # Arrange
        valid_post_input["page_name"] = "login_page"  # snake_case

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager

            # Act
            result = QGDiscoveredElements.validate(valid_post_input)

        # Assert
        assert result["status"] == "fail"
        assert "pascalcase" in result["error"].lower()

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_post_saves_to_state(self, mock_state_manager, valid_post_input):
        """
        P0: Successful POST should save to Step 5 state.
        """
        # Arrange
        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager

            # Act
            result = QGDiscoveredElements.validate(valid_post_input)

        # Assert
        assert result["status"] == "pass"
        step_5_state = mock_state_manager.get_step(5)
        assert step_5_state is not None
        assert "discovered_elements" in step_5_state
        assert "page_name" in step_5_state


# ============================================================================
# SCOPE VALIDATION TESTS (Task 2.0)
# ============================================================================

class TestQGDiscoveredElementsScopeValidation:
    """Task 2.0: Scope result validation tests."""

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    @pytest.mark.scope_discovery
    def test_pre_with_valid_scope_result_passes(
        self, mock_state_manager, valid_pre_input, multi_page_scope_result
    ):
        """
        P1: PRE with valid scope_result and matching page_name should pass.
        """
        # Arrange
        valid_pre_input["scope_result"] = multi_page_scope_result
        valid_pre_input["page_name"] = "LoginPage"  # In scope

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            # Act
            result = QGDiscoveredElements.validate(valid_pre_input)

        # Assert
        assert result["status"] == "pass", f"Valid scope should pass, got {result}"

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    @pytest.mark.scope_discovery
    def test_pre_page_not_in_scope_fails(
        self, mock_state_manager, valid_pre_input, multi_page_scope_result
    ):
        """
        P1: PRE with page_name not in scope should fail.
        """
        # Arrange
        valid_pre_input["scope_result"] = multi_page_scope_result
        valid_pre_input["page_name"] = "UnknownPage"  # NOT in scope

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            # Act
            result = QGDiscoveredElements.validate(valid_pre_input)

        # Assert
        assert result["status"] == "fail"
        assert "not found in scope" in result["error"].lower()

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    @pytest.mark.scope_discovery
    def test_pre_single_page_scope_allows_any_page_name(
        self, mock_state_manager, valid_pre_input, single_page_scope_result
    ):
        """
        P1: Single-page scope should allow page_name different from scope.

        For single-page workflows, we're less strict about page_name matching
        because there's no multi-page navigation to track.
        """
        # Arrange
        valid_pre_input["scope_result"] = single_page_scope_result
        valid_pre_input["page_name"] = "LoginPage"  # Different from MainPage

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            # Act
            result = QGDiscoveredElements.validate(valid_pre_input)

        # Assert
        assert result["status"] == "pass", \
            "Single-page scope should not enforce page_name match"

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    @pytest.mark.scope_discovery
    def test_pre_invalid_scope_result_structure_fails(
        self, mock_state_manager, valid_pre_input
    ):
        """
        P1: Invalid scope_result structure should fail.
        """
        # Arrange
        valid_pre_input["scope_result"] = {"invalid": "structure"}  # Missing page_count

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            # Act
            result = QGDiscoveredElements.validate(valid_pre_input)

        # Assert
        assert result["status"] == "fail"
        assert "page_count" in result["error"].lower()


# ============================================================================
# PER-PAGE TRACKING TESTS (Task 2.0)
# ============================================================================

class TestQGDiscoveredElementsPerPageTracking:
    """Task 2.0: Per-page element tracking tests."""

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    @pytest.mark.per_page_discovery
    def test_post_saves_per_page_elements(
        self, mock_state_manager, valid_post_input, multi_page_scope_result
    ):
        """
        P1: POST should save elements under discovered_pages[page_name].
        """
        # Arrange
        valid_post_input["scope_result"] = multi_page_scope_result
        valid_post_input["page_name"] = "LoginPage"

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager

            # Act
            result = QGDiscoveredElements.validate(valid_post_input)

        # Assert
        assert result["status"] == "pass"
        step_5_state = mock_state_manager.get_step(5)
        assert "discovered_pages" in step_5_state
        assert "LoginPage" in step_5_state["discovered_pages"]
        assert step_5_state["discovered_pages"]["LoginPage"] == valid_post_input["elements"]

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    @pytest.mark.per_page_discovery
    def test_post_accumulates_multiple_pages(
        self, mock_state_manager, valid_post_input, multi_page_scope_result
    ):
        """
        P1: Multiple POST calls should accumulate pages in discovered_pages.
        """
        # Arrange
        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager

            # Act - First page
            valid_post_input["scope_result"] = multi_page_scope_result
            valid_post_input["page_name"] = "LoginPage"
            result1 = QGDiscoveredElements.validate(valid_post_input)

            # Act - Second page
            valid_post_input["page_name"] = "DashboardPage"
            valid_post_input["elements"] = [{
                "suggested_name": "MENU",
                "element_type": "navigation",
                "locator_css": "nav.main-menu"
            }]
            result2 = QGDiscoveredElements.validate(valid_post_input)

        # Assert
        assert result1["status"] == "pass"
        assert result2["status"] == "pass"
        step_5_state = mock_state_manager.get_step(5)
        assert "LoginPage" in step_5_state["discovered_pages"]
        assert "DashboardPage" in step_5_state["discovered_pages"]
        assert step_5_state["pages_discovered"] == 2

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    @pytest.mark.per_page_discovery
    def test_post_tracks_discovery_progress(
        self, mock_state_manager, valid_post_input, multi_page_scope_result
    ):
        """
        P1: POST should track discovery progress against scope.
        """
        # Arrange
        valid_post_input["scope_result"] = multi_page_scope_result
        valid_post_input["page_name"] = "LoginPage"

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager

            # Act
            result = QGDiscoveredElements.validate(valid_post_input)

        # Assert
        assert result["status"] == "pass"
        step_5_state = mock_state_manager.get_step(5)
        assert step_5_state["pages_discovered"] == 1
        assert step_5_state["total_pages"] == 3
        assert step_5_state["discovery_complete"] is False

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    @pytest.mark.per_page_discovery
    def test_post_marks_complete_when_all_pages_discovered(
        self, mock_state_manager, valid_post_input, single_page_scope_result
    ):
        """
        P1: POST should mark discovery_complete=True when all pages discovered.
        """
        # Arrange
        valid_post_input["scope_result"] = single_page_scope_result
        valid_post_input["page_name"] = "MainPage"

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager

            # Act
            result = QGDiscoveredElements.validate(valid_post_input)

        # Assert
        assert result["status"] == "pass"
        step_5_state = mock_state_manager.get_step(5)
        assert step_5_state["discovery_complete"] is True


# ============================================================================
# DISCOVERY PROGRESS HELPER TESTS (Task 2.0)
# ============================================================================

class TestQGDiscoveredElementsProgressHelpers:
    """Task 2.0: Discovery progress helper method tests."""

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    @pytest.mark.per_page_discovery
    def test_get_discovery_progress_returns_status(
        self, mock_state_manager, valid_post_input, multi_page_scope_result
    ):
        """
        P1: get_discovery_progress() should return current discovery status.
        """
        # Arrange - Save some discovery progress
        valid_post_input["scope_result"] = multi_page_scope_result
        valid_post_input["page_name"] = "LoginPage"

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager
            QGDiscoveredElements.validate(valid_post_input)

            # Act
            progress = QGDiscoveredElements.get_discovery_progress()

        # Assert
        assert "discovered_pages" in progress
        assert "pages_discovered" in progress
        assert "total_pages" in progress
        assert "discovery_complete" in progress
        assert progress["pages_discovered"] == 1
        assert progress["total_pages"] == 3

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    @pytest.mark.per_page_discovery
    def test_is_discovery_complete_returns_false_when_incomplete(
        self, mock_state_manager, valid_post_input, multi_page_scope_result
    ):
        """
        P1: is_discovery_complete() should return False when pages remain.
        """
        # Arrange
        valid_post_input["scope_result"] = multi_page_scope_result
        valid_post_input["page_name"] = "LoginPage"

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager
            QGDiscoveredElements.validate(valid_post_input)

            # Act
            is_complete = QGDiscoveredElements.is_discovery_complete()

        # Assert
        assert is_complete is False

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    @pytest.mark.per_page_discovery
    def test_is_discovery_complete_returns_true_when_complete(
        self, mock_state_manager, valid_post_input, single_page_scope_result
    ):
        """
        P1: is_discovery_complete() should return True when all pages discovered.
        """
        # Arrange
        valid_post_input["scope_result"] = single_page_scope_result
        valid_post_input["page_name"] = "MainPage"

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager
            QGDiscoveredElements.validate(valid_post_input)

            # Act
            is_complete = QGDiscoveredElements.is_discovery_complete()

        # Assert
        assert is_complete is True


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestQGDiscoveredElementsEdgeCases:
    """Edge case tests."""

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_pre_without_scope_result_passes(
        self, mock_state_manager, valid_pre_input
    ):
        """
        P1: PRE without scope_result should still pass (backward compat).
        """
        # Arrange - No scope_result in input

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            # Act
            result = QGDiscoveredElements.validate(valid_pre_input)

        # Assert
        assert result["status"] == "pass", \
            "PRE without scope_result should pass for backward compatibility"

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_invalid_mode_fails(self, mock_state_manager):
        """
        P1: Invalid mode should fail with helpful error.
        """
        # Arrange
        input_data = {"mode": "INVALID"}

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            # Act
            result = QGDiscoveredElements.validate(input_data)

        # Assert
        assert result["status"] == "fail"
        assert "mode" in result["error"].lower()

    @pytest.mark.unit
    @pytest.mark.qg_discovered_elements
    def test_element_with_only_xpath_locator_passes(
        self, mock_state_manager, valid_post_input
    ):
        """
        P1: Element with only XPath locator (no ID/CSS) should pass.
        """
        # Arrange
        valid_post_input["elements"] = [{
            "suggested_name": "CUSTOM_ELEMENT",
            "element_type": "custom",
            "locator_id": "",
            "locator_css": "",
            "locator_xpath": "//div[@data-testid='custom']"
        }]

        with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=mock_state_manager):
            QGDiscoveredElements._state_manager = mock_state_manager

            # Act
            result = QGDiscoveredElements.validate(valid_post_input)

        # Assert
        assert result["status"] == "pass", \
            "Element with only XPath locator should pass IC-05-03"

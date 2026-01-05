"""
Tests for qg_discovery_complete.py - Discovery Complete Checkpoint Gate.

NEW gate for DEF-045 - Two-Pass Discovery validation.

Test Coverage:
- PRE validation: Step 5 completion check
- PRE validation: discovered_pages structure validation
- PRE validation: Both input and output elements present
- PRE validation: Single-page workflow
- PRE validation: Multi-page workflow
- Backward compatibility: Old flat structure handling
- Error messages and fix hints
"""

import pytest
from unittest.mock import Mock, patch

from tools.gates.qg_discovery_complete import QGDiscoveryComplete


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_state_manager():
    """Mock StateManager for testing."""
    mock = Mock()
    mock.is_step_complete = Mock(return_value=True)
    mock.get_step = Mock(return_value={})
    return mock


@pytest.fixture
def single_page_complete():
    """Step 5 state with single page - both input and output complete."""
    return {
        "discovered_pages": {
            "LoginPage": {
                "input_elements": [
                    {"suggested_name": "EMAIL_INPUT", "element_type": "textbox"},
                    {"suggested_name": "PASSWORD_INPUT", "element_type": "textbox"},
                ],
                "output_elements": [
                    {"suggested_name": "SUCCESS_MESSAGE", "element_type": "text"},
                ]
            }
        },
        "total_pages": 1,
        "pages_discovered": 1,
        "discovery_complete": True
    }


@pytest.fixture
def single_page_input_only():
    """Step 5 state with single page - only input elements (missing output)."""
    return {
        "discovered_pages": {
            "LoginPage": {
                "input_elements": [
                    {"suggested_name": "EMAIL_INPUT", "element_type": "textbox"},
                ]
            }
        },
        "total_pages": 1,
        "pages_discovered": 0,
        "discovery_complete": False
    }


@pytest.fixture
def multi_page_complete():
    """Step 5 state with multi-page - all pages have both types."""
    return {
        "discovered_pages": {
            "LoginPage": {
                "input_elements": [
                    {"suggested_name": "EMAIL_INPUT", "element_type": "textbox"},
                ],
                "output_elements": [
                    {"suggested_name": "SUCCESS_MESSAGE", "element_type": "text"},
                ]
            },
            "CartPage": {
                "input_elements": [
                    {"suggested_name": "QUANTITY_INPUT", "element_type": "textbox"},
                ],
                "output_elements": [
                    {"suggested_name": "ITEM_ADDED_MESSAGE", "element_type": "text"},
                ]
            },
            "CheckoutPage": {
                "input_elements": [
                    {"suggested_name": "ADDRESS_INPUT", "element_type": "textbox"},
                ],
                "output_elements": [
                    {"suggested_name": "ORDER_CONFIRMATION", "element_type": "text"},
                ]
            }
        },
        "total_pages": 3,
        "pages_discovered": 3,
        "discovery_complete": True
    }


@pytest.fixture
def multi_page_incomplete():
    """Step 5 state with multi-page - some pages missing output."""
    return {
        "discovered_pages": {
            "LoginPage": {
                "input_elements": [
                    {"suggested_name": "EMAIL_INPUT", "element_type": "textbox"},
                ],
                "output_elements": [
                    {"suggested_name": "SUCCESS_MESSAGE", "element_type": "text"},
                ]
            },
            "CartPage": {
                "input_elements": [
                    {"suggested_name": "QUANTITY_INPUT", "element_type": "textbox"},
                ],
                # Missing output_elements
            },
            "CheckoutPage": {
                # Missing input_elements AND output_elements
            }
        },
        "total_pages": 3,
        "pages_discovered": 1,
        "discovery_complete": False
    }


@pytest.fixture
def backward_compat_flat_structure():
    """Step 5 state with old flat structure (backward compatibility test)."""
    return {
        "discovered_pages": {
            "LoginPage": [
                {"suggested_name": "EMAIL_INPUT", "element_type": "textbox"},
            ]
        },
        "total_pages": 1,
        "pages_discovered": 0,
        "discovery_complete": False
    }


# ============================================================================
# Test Class: PRE Validation - Step 5 Completion
# ============================================================================

class TestPREStep5Completion:
    """Test PRE validation checks Step 5 completion."""

    def test_pre_step_5_not_complete_fails(self, mock_state_manager):
        """Test PRE fails when Step 5 is not complete."""
        mock_state_manager.is_step_complete.return_value = False

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert result["status"] == "fail"
        assert "Step 5 is not complete" in result["error"]
        assert "Complete Step 5" in result["fix_hint"]

    def test_pre_step_5_complete_continues(self, mock_state_manager, single_page_complete):
        """Test PRE continues validation when Step 5 is complete."""
        mock_state_manager.is_step_complete.return_value = True
        mock_state_manager.get_step.return_value = single_page_complete

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert result["status"] == "pass"


# ============================================================================
# Test Class: PRE Validation - discovered_pages Structure
# ============================================================================

class TestPREDiscoveredPagesStructure:
    """Test PRE validation of discovered_pages structure."""

    def test_pre_discovered_pages_missing_fails(self, mock_state_manager):
        """Test PRE fails when discovered_pages is missing from state."""
        mock_state_manager.get_step.return_value = {}

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert result["status"] == "fail"
        assert "No pages discovered" in result["error"]
        assert "discovered_pages is empty" in result["error"]

    def test_pre_discovered_pages_empty_dict_fails(self, mock_state_manager):
        """Test PRE fails when discovered_pages is an empty dict."""
        mock_state_manager.get_step.return_value = {"discovered_pages": {}}

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert result["status"] == "fail"
        assert "No pages discovered" in result["error"]


# ============================================================================
# Test Class: PRE Validation - Single Page Complete
# ============================================================================

class TestPRESinglePageComplete:
    """Test PRE validation for single-page workflows."""

    def test_pre_single_page_both_types_passes(self, mock_state_manager, single_page_complete):
        """Test PRE passes when single page has both input and output elements."""
        mock_state_manager.get_step.return_value = single_page_complete

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert result["status"] == "pass"

    def test_pre_single_page_input_only_fails(self, mock_state_manager, single_page_input_only):
        """Test PRE fails when single page has only input elements (missing output)."""
        mock_state_manager.get_step.return_value = single_page_input_only

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert result["status"] == "fail"
        assert "0/1 pages have both input and output" in result["error"]
        assert "LoginPage (missing: output)" in result["fix_hint"]

    def test_pre_single_page_output_only_fails(self, mock_state_manager):
        """Test PRE fails when single page has only output elements (missing input)."""
        state = {
            "discovered_pages": {
                "LoginPage": {
                    "output_elements": [
                        {"suggested_name": "SUCCESS_MESSAGE", "element_type": "text"},
                    ]
                }
            }
        }
        mock_state_manager.get_step.return_value = state

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert result["status"] == "fail"
        assert "LoginPage (missing: input)" in result["fix_hint"]

    def test_pre_single_page_both_missing_fails(self, mock_state_manager):
        """Test PRE fails when single page has neither input nor output elements."""
        state = {
            "discovered_pages": {
                "LoginPage": {}
            }
        }
        mock_state_manager.get_step.return_value = state

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert result["status"] == "fail"
        assert "LoginPage (missing: input, output)" in result["fix_hint"]


# ============================================================================
# Test Class: PRE Validation - Multi-Page Complete
# ============================================================================

class TestPREMultiPageComplete:
    """Test PRE validation for multi-page workflows."""

    def test_pre_multi_page_all_complete_passes(self, mock_state_manager, multi_page_complete):
        """Test PRE passes when all pages in multi-page workflow have both types."""
        mock_state_manager.get_step.return_value = multi_page_complete

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert result["status"] == "pass"

    def test_pre_multi_page_incomplete_fails(self, mock_state_manager, multi_page_incomplete):
        """Test PRE fails when some pages in multi-page workflow are incomplete."""
        mock_state_manager.get_step.return_value = multi_page_incomplete

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert result["status"] == "fail"
        assert "1/3 pages have both input and output" in result["error"]
        assert "CartPage (missing: output)" in result["fix_hint"]
        assert "CheckoutPage (missing: input, output)" in result["fix_hint"]

    def test_pre_multi_page_progress_tracking(self, mock_state_manager):
        """Test PRE shows correct progress for multi-page workflows."""
        state = {
            "discovered_pages": {
                "Page1": {
                    "input_elements": [{"suggested_name": "INPUT1"}],
                    "output_elements": [{"suggested_name": "OUTPUT1"}]
                },
                "Page2": {
                    "input_elements": [{"suggested_name": "INPUT2"}],
                    "output_elements": [{"suggested_name": "OUTPUT2"}]
                },
                "Page3": {
                    "input_elements": [{"suggested_name": "INPUT3"}],
                    # Missing output
                },
                "Page4": {
                    # Missing both
                }
            }
        }
        mock_state_manager.get_step.return_value = state

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert result["status"] == "fail"
        assert "2/4 pages have both input and output" in result["error"]


# ============================================================================
# Test Class: Backward Compatibility
# ============================================================================

class TestBackwardCompatibility:
    """Test backward compatibility with old flat structure."""

    def test_pre_old_flat_structure_treated_as_input_only(self, mock_state_manager, backward_compat_flat_structure):
        """Test PRE treats old flat structure as input-only (missing output)."""
        mock_state_manager.get_step.return_value = backward_compat_flat_structure

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert result["status"] == "fail"
        assert "LoginPage (missing: output)" in result["fix_hint"]


# ============================================================================
# Test Class: POST Validation (Not Applicable)
# ============================================================================

class TestPOSTValidation:
    """Test POST validation (not applicable for checkpoint gates)."""

    def test_post_always_passes(self):
        """Test POST validation always passes (checkpoint is PRE-only)."""
        result = QGDiscoveryComplete.validate_post({})

        assert result["status"] == "pass"


# ============================================================================
# Test Class: Error Messages and Fix Hints
# ============================================================================

class TestErrorMessagesAndFixHints:
    """Test error messages and fix hints are clear and actionable."""

    def test_error_message_shows_progress(self, mock_state_manager, multi_page_incomplete):
        """Test error message shows clear progress (N/M pages complete)."""
        mock_state_manager.get_step.return_value = multi_page_incomplete

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert "1/3 pages" in result["error"]

    def test_fix_hint_lists_incomplete_pages(self, mock_state_manager, multi_page_incomplete):
        """Test fix hint lists all incomplete pages with what's missing."""
        mock_state_manager.get_step.return_value = multi_page_incomplete

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert "CartPage (missing: output)" in result["fix_hint"]
        assert "CheckoutPage (missing: input, output)" in result["fix_hint"]

    def test_fix_hint_mentions_two_pass_discovery(self, mock_state_manager, single_page_input_only):
        """Test fix hint mentions two-pass discovery (PASS 1 and PASS 2)."""
        mock_state_manager.get_step.return_value = single_page_input_only

        with patch.object(QGDiscoveryComplete, '_get_state_manager', return_value=mock_state_manager):
            result = QGDiscoveryComplete.validate_pre({})

        assert "PASS 1" in result["fix_hint"]
        assert "PASS 2" in result["fix_hint"]

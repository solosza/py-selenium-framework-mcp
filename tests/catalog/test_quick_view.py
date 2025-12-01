"""
Catalog Tests - Quick View Modal.

Tests opening and interacting with quick view modal.
Uses GuestUser role to orchestrate quick view workflows.
"""

import pytest
from pathlib import Path
import sys

# Add framework to path
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from roles.guest.guest_user import GuestUser
from pages.catalog.quick_view_modal import QuickViewModal
from resources.utilities import autologger


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_open_quick_view_modal(web_interface, config):
    """
    Test opening quick view modal for first product.

    Uses GuestUser role to orchestrate the quick view workflow.

    Steps:
        1. Create GuestUser role
        2. Call view_product_quick_view() for first product
        3. Verify modal opens via POM

    Expected Result:
        Quick view modal opens and displays product details.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)
    quick_view_modal = QuickViewModal(web_interface)

    # Act: Use role to open quick view
    guest.view_product_quick_view("Dresses", product_index=0)

    # Assert: Verify modal opened via POM state-check
    assert quick_view_modal.is_modal_open(), "Quick view modal should be open"

    # Cleanup: Close modal using role
    guest.close_quick_view()


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_open_quick_view_second_product(web_interface, config):
    """
    Test opening quick view for second product.

    Uses GuestUser role to orchestrate the quick view workflow.

    Steps:
        1. Create GuestUser role
        2. Call view_product_quick_view() for second product
        3. Verify modal opens via POM

    Expected Result:
        Quick view modal opens for second product.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)
    quick_view_modal = QuickViewModal(web_interface)

    # Act: Use role to open quick view for second product
    guest.view_product_quick_view("Women", product_index=1)

    # Assert: Verify modal opened via POM state-check
    assert quick_view_modal.is_modal_open(), "Quick view modal should be open for second product"

    # Cleanup: Close modal using role
    guest.close_quick_view()


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_close_quick_view_modal(web_interface, config):
    """
    Test opening and closing quick view modal.

    Uses GuestUser role to orchestrate the workflow.

    Steps:
        1. Create GuestUser role
        2. Call view_product_quick_view() to open modal
        3. Call close_quick_view() to close modal
        4. Verify modal closes via POM

    Expected Result:
        Quick view modal opens and closes successfully.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)
    quick_view_modal = QuickViewModal(web_interface)

    # Act: Use role to open quick view
    guest.view_product_quick_view("Dresses", product_index=0)
    assert quick_view_modal.is_modal_open(), "Quick view should open"

    # Act: Use role to close quick view
    guest.close_quick_view()

    # Assert: Verify modal closed via POM state-check
    assert not quick_view_modal.is_modal_open(), "Quick view modal should be closed"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_quick_view_invalid_product_index(web_interface, config):
    """
    Test that invalid product index handles gracefully.

    Uses GuestUser role to test error handling.

    Steps:
        1. Create GuestUser role
        2. Attempt to view product at invalid index 999
        3. Verify modal does NOT open (graceful handling)

    Expected Result:
        Invalid product index is handled gracefully, modal not opened.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)
    quick_view_modal = QuickViewModal(web_interface)

    # Act: Use role to attempt invalid product index
    # This may raise an exception or simply not open the modal
    try:
        guest.view_product_quick_view("T-shirts", product_index=999)
    except Exception:
        pass  # Expected - invalid index should fail

    # Assert: Modal should not be open
    assert not quick_view_modal.is_modal_open(), "Modal should not open for invalid index"

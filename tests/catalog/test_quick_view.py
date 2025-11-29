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
        3. Verify modal opens successfully

    Expected Result:
        Quick view modal opens and displays product details.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to open quick view
    quick_view_result = guest.view_product_quick_view("Dresses", product_index=0)

    # Assert: Verify modal opened
    assert quick_view_result is True, "Failed to open quick view modal"

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
        3. Verify modal opens

    Expected Result:
        Quick view modal opens for second product.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to open quick view for second product
    quick_view_result = guest.view_product_quick_view("Women", product_index=1)

    # Assert: Verify modal opened
    assert quick_view_result is True, "Failed to open quick view for second product"

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
        4. Verify modal closes successfully

    Expected Result:
        Quick view modal opens and closes successfully.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to open quick view
    quick_view_result = guest.view_product_quick_view("Dresses", product_index=0)
    assert quick_view_result is True, "Quick view should open"

    # Act: Use role to close quick view
    close_result = guest.close_quick_view()

    # Assert: Verify modal closed
    assert close_result is True, "Failed to close quick view modal"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_quick_view_invalid_product_index(web_interface, config):
    """
    Test that invalid product index fails gracefully.

    Uses GuestUser role to test error handling.

    Steps:
        1. Create GuestUser role
        2. Attempt to view product at invalid index 999
        3. Verify operation returns False

    Expected Result:
        Invalid product index returns False.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to attempt invalid product index
    quick_view_result = guest.view_product_quick_view("T-shirts", product_index=999)

    # Assert: Verify operation failed
    assert quick_view_result is False, "Invalid product index should fail"

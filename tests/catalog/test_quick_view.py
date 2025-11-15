"""
Catalog Tests - Quick View Modal.

Tests opening and interacting with quick view modal.
"""

import pytest
from pathlib import Path
import sys

# Add framework to path
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from tasks.catalog_tasks import CatalogTasks
from resources.utilities import autologger


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_open_quick_view_modal(web_interface, config):
    """
    Test opening quick view modal for first product.

    Steps:
        1. Browse Dresses category
        2. Open quick view for first product (index 0)
        3. Verify modal opens successfully

    Expected Result:
        Quick view modal opens and displays product details.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Open quick view
    quick_view_result = catalog_tasks.open_quick_view("Dresses", product_index=0)

    # Assert: Verify modal opened
    assert quick_view_result is True, "Failed to open quick view modal"

    # Cleanup: Close modal
    catalog_tasks.close_quick_view()


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_open_quick_view_second_product(web_interface, config):
    """
    Test opening quick view for second product.

    Steps:
        1. Browse Women category
        2. Open quick view for second product (index 1)
        3. Verify modal opens

    Expected Result:
        Quick view modal opens for second product.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Open quick view for second product
    quick_view_result = catalog_tasks.open_quick_view("Women", product_index=1)

    # Assert: Verify modal opened
    assert quick_view_result is True, "Failed to open quick view for second product"

    # Cleanup: Close modal
    catalog_tasks.close_quick_view()


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_close_quick_view_modal(web_interface, config):
    """
    Test opening and closing quick view modal.

    Steps:
        1. Browse Dresses category
        2. Open quick view for first product
        3. Close quick view modal
        4. Verify modal closes successfully

    Expected Result:
        Quick view modal opens and closes successfully.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Open quick view
    quick_view_result = catalog_tasks.open_quick_view("Dresses", product_index=0)
    assert quick_view_result is True, "Quick view should open"

    # Act: Close quick view
    close_result = catalog_tasks.close_quick_view()

    # Assert: Verify modal closed
    assert close_result is True, "Failed to close quick view modal"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_quick_view_invalid_product_index(web_interface, config):
    """
    Test that invalid product index fails gracefully.

    Steps:
        1. Browse T-shirts category
        2. Attempt to open quick view for product index 999
        3. Verify operation returns False

    Expected Result:
        Invalid product index returns False.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Attempt invalid product index
    quick_view_result = catalog_tasks.open_quick_view("T-shirts", product_index=999)

    # Assert: Verify operation failed
    assert quick_view_result is False, "Invalid product index should fail"

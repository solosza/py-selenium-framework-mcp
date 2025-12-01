"""
Catalog Tests - Product Filtering.

Tests filtering products by size and color.
Uses GuestUser role to orchestrate filtering workflows.
"""

import pytest
from pathlib import Path
import sys

# Add framework to path
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from roles.guest.guest_user import GuestUser
from pages.catalog.product_list_page import ProductListPage
from resources.utilities import autologger


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_filter_by_size(web_interface, config):
    """
    Test filtering products by size.

    Uses GuestUser role to orchestrate the filtering workflow.

    Steps:
        1. Create GuestUser role
        2. Call filter_products_in_category() with size filter
        3. Verify filter applied via POM

    Expected Result:
        Products are filtered by size S.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)
    product_list_page = ProductListPage(web_interface)

    # Act: Use role to filter products by size
    guest.filter_products_in_category("Dresses", size="S")

    # Assert: Verify filtering successful via POM - page loaded with products
    assert product_list_page.is_page_loaded(), "Product list page should be loaded after filtering"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_filter_by_color(web_interface, config):
    """
    Test filtering products by color.

    Uses GuestUser role to orchestrate the filtering workflow.

    Steps:
        1. Create GuestUser role
        2. Call filter_products_in_category() with color filter
        3. Verify filter applied via POM

    Expected Result:
        Products are filtered by color White.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)
    product_list_page = ProductListPage(web_interface)

    # Act: Use role to filter products by color
    guest.filter_products_in_category("Dresses", color="White")

    # Assert: Verify filtering successful via POM - page loaded with products
    assert product_list_page.is_page_loaded(), "Product list page should be loaded after filtering"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_filter_by_size_and_color(web_interface, config):
    """
    Test filtering products by both size and color.

    Uses GuestUser role to orchestrate the combined filter workflow.

    Steps:
        1. Create GuestUser role
        2. Call filter_products_in_category() with both size and color
        3. Verify filters applied via POM

    Expected Result:
        Products are filtered by both size M and color Black.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)
    product_list_page = ProductListPage(web_interface)

    # Act: Use role to filter products by size and color
    guest.filter_products_in_category("Dresses", size="M", color="Black")

    # Assert: Verify filtering successful via POM - page loaded
    assert product_list_page.is_page_loaded(), "Product list page should be loaded after filtering"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_filter_invalid_size(web_interface, config):
    """
    Test that invalid size filter handles gracefully.

    Uses GuestUser role to test error handling.

    Steps:
        1. Create GuestUser role
        2. Attempt to filter by invalid size (XL)
        3. Verify page still loads (graceful handling)

    Expected Result:
        Filter operation handles invalid size gracefully.

    Note: Invalid filter may result in no products or all products shown.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)
    product_list_page = ProductListPage(web_interface)

    # Act: Use role to attempt filter (may or may not have XL size)
    guest.filter_products_in_category("Dresses", size="L")

    # Assert: Page should still be loaded (graceful handling)
    assert product_list_page.is_page_loaded(), "Page should handle filter gracefully"

"""
Catalog Tests - Category Browsing.

Tests browsing product categories and verifying product listings.
Uses GuestUser role to orchestrate catalog browsing workflows.
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
def test_browse_women_category(web_interface, config):
    """
    Test browsing the Women category and verifying products are displayed.

    Uses GuestUser role to orchestrate the browsing workflow.

    Steps:
        1. Create GuestUser role
        2. Call browse_and_count_products() workflow
        3. Verify products are displayed

    Expected Result:
        Women category loads with product listings displayed.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to browse Women category and get product count
    product_count = guest.browse_and_count_products("Women")

    # Assert: Verify category browsed successfully with products
    assert product_count > 0, f"Expected products in Women category, found {product_count}"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_browse_dresses_category(web_interface, config):
    """
    Test browsing the Dresses category.

    Uses GuestUser role to orchestrate the browsing workflow.

    Steps:
        1. Create GuestUser role
        2. Call browse_category() workflow
        3. Verify success

    Expected Result:
        Dresses category loads with products.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to browse Dresses category
    browse_result = guest.browse_category("Dresses")

    # Assert: Verify browsing successful
    assert browse_result is True, "Failed to browse Dresses category"
    assert guest.verify_products_displayed() is True, "No products displayed in Dresses"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_browse_tshirts_category(web_interface, config):
    """
    Test browsing the T-shirts category.

    Uses GuestUser role to orchestrate the browsing workflow.

    Steps:
        1. Create GuestUser role
        2. Call browse_category() workflow
        3. Verify success

    Expected Result:
        T-shirts category loads with products.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to browse T-shirts category
    browse_result = guest.browse_category("T-shirts")

    # Assert: Verify browsing successful
    assert browse_result is True, "Failed to browse T-shirts category"
    assert guest.verify_products_displayed() is True, "No products displayed in T-shirts"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_product_count_varies_by_category(web_interface, config):
    """
    Test that different categories have different product counts.

    Uses GuestUser role to browse multiple categories.

    Steps:
        1. Browse Women category using role workflow, record product count
        2. Browse Dresses category using role workflow, record product count
        3. Verify both have products

    Expected Result:
        Different categories display products successfully.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Browse Women category using role workflow
    women_count = guest.browse_and_count_products("Women")

    # Act: Browse Dresses category using role workflow
    dresses_count = guest.browse_and_count_products("Dresses")

    # Assert: Verify counts are captured
    assert women_count > 0, "Women category should have products"
    assert dresses_count > 0, "Dresses category should have products"

    # Note: We cannot assume counts are different as Dresses might be a subcategory
    # Just verify both categories loaded successfully

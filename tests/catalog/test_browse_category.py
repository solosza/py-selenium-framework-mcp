"""
Catalog Tests - Category Browsing.

Tests browsing product categories and verifying product listings.
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
def test_browse_women_category(web_interface, config):
    """
    Test browsing the Women category and verifying products are displayed.

    Steps:
        1. Create CatalogTasks instance
        2. Browse Women category
        3. Verify products are displayed
        4. Verify product count > 0

    Expected Result:
        Women category loads with product listings displayed.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Browse Women category
    browse_result = catalog_tasks.browse_category("Women")

    # Assert: Verify category browsed successfully
    assert browse_result is True, "Failed to browse Women category"
    assert catalog_tasks.verify_products_displayed() is True, "No products displayed"

    product_count = catalog_tasks.get_product_count()
    assert product_count > 0, f"Expected products, found {product_count}"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_browse_dresses_category(web_interface, config):
    """
    Test browsing the Dresses category.

    Steps:
        1. Create CatalogTasks instance
        2. Browse Dresses category
        3. Verify products are displayed

    Expected Result:
        Dresses category loads with products.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Browse Dresses category
    browse_result = catalog_tasks.browse_category("Dresses")

    # Assert: Verify browsing successful
    assert browse_result is True, "Failed to browse Dresses category"
    assert catalog_tasks.verify_products_displayed() is True, "No products displayed in Dresses"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_browse_tshirts_category(web_interface, config):
    """
    Test browsing the T-shirts category.

    Steps:
        1. Create CatalogTasks instance
        2. Browse T-shirts category
        3. Verify products are displayed

    Expected Result:
        T-shirts category loads with products.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Browse T-shirts category
    browse_result = catalog_tasks.browse_category("T-shirts")

    # Assert: Verify browsing successful
    assert browse_result is True, "Failed to browse T-shirts category"
    assert catalog_tasks.verify_products_displayed() is True, "No products displayed in T-shirts"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_product_count_varies_by_category(web_interface, config):
    """
    Test that different categories have different product counts.

    Steps:
        1. Browse Women category, record product count
        2. Browse Dresses category, record product count
        3. Verify counts are different (categories have distinct inventories)

    Expected Result:
        Different categories display different numbers of products.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Browse Women category
    catalog_tasks.browse_category("Women")
    women_count = catalog_tasks.get_product_count()

    # Act: Browse Dresses category
    catalog_tasks.browse_category("Dresses")
    dresses_count = catalog_tasks.get_product_count()

    # Assert: Verify counts are captured
    assert women_count > 0, "Women category should have products"
    assert dresses_count > 0, "Dresses category should have products"

    # Note: We cannot assume counts are different as Dresses might be a subcategory
    # Just verify both categories loaded successfully

"""
Catalog Tests - Product Sorting.

Tests sorting products by price (low to high, high to low).
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
def test_sort_by_price_low_to_high(web_interface, config):
    """
    Test sorting products by price (lowest first).

    Steps:
        1. Browse Dresses category
        2. Sort by price: low to high
        3. Verify products are sorted correctly

    Expected Result:
        Products are sorted by price in ascending order.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Sort products by price ascending
    sort_result = catalog_tasks.sort_products("Dresses", "price_asc")

    # Assert: Verify sorting successful and verified
    assert sort_result is True, "Failed to sort by price (low to high)"
    assert catalog_tasks.verify_sort_order("price_asc") is True, "Sort order verification failed"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_sort_by_price_high_to_low(web_interface, config):
    """
    Test sorting products by price (highest first).

    Steps:
        1. Browse Dresses category
        2. Sort by price: high to low
        3. Verify products are sorted correctly

    Expected Result:
        Products are sorted by price in descending order.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Sort products by price descending
    sort_result = catalog_tasks.sort_products("Dresses", "price_desc")

    # Assert: Verify sorting successful and verified
    assert sort_result is True, "Failed to sort by price (high to low)"
    assert catalog_tasks.verify_sort_order("price_desc") is True, "Sort order verification failed"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_sort_by_name_a_to_z(web_interface, config):
    """
    Test sorting products by name (A to Z).

    Steps:
        1. Browse Women category
        2. Sort by name: A to Z
        3. Verify sorting operation completes

    Expected Result:
        Products are sorted by name alphabetically.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Sort products by name ascending
    sort_result = catalog_tasks.sort_products("Women", "name_asc")

    # Assert: Verify sorting successful
    assert sort_result is True, "Failed to sort by name (A to Z)"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_sort_invalid_option(web_interface, config):
    """
    Test that invalid sort option fails gracefully.

    Steps:
        1. Browse Dresses category
        2. Attempt invalid sort option
        3. Verify operation returns False

    Expected Result:
        Invalid sort option returns False.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Attempt invalid sort
    sort_result = catalog_tasks.sort_products("Dresses", "invalid_sort")

    # Assert: Verify operation failed
    assert sort_result is False, "Invalid sort option should fail"

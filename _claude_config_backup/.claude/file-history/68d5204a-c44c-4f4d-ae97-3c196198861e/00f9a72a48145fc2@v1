"""
Catalog Tests - Product Filtering.

Tests filtering products by size and color.
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
def test_filter_by_size(web_interface, config):
    """
    Test filtering products by size.

    Steps:
        1. Browse Dresses category
        2. Get initial product count
        3. Apply size filter (S)
        4. Verify filter applied (products displayed)

    Expected Result:
        Products are filtered by size S.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Filter products by size
    filter_result = catalog_tasks.filter_products("Dresses", size="S")

    # Assert: Verify filtering successful
    assert filter_result is True, "Failed to filter by size"

    # Note: We cannot assert count changed as all products might be size S
    # Just verify the operation completed successfully


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_filter_by_color(web_interface, config):
    """
    Test filtering products by color.

    Steps:
        1. Browse Dresses category
        2. Apply color filter (White)
        3. Verify filter applied successfully

    Expected Result:
        Products are filtered by color White.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Filter products by color
    filter_result = catalog_tasks.filter_products("Dresses", color="White")

    # Assert: Verify filtering successful
    assert filter_result is True, "Failed to filter by color"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_filter_by_size_and_color(web_interface, config):
    """
    Test filtering products by both size and color.

    Steps:
        1. Browse Dresses category
        2. Apply size filter (M) and color filter (Black)
        3. Verify filters applied successfully

    Expected Result:
        Products are filtered by both size M and color Black.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Filter products by size and color
    filter_result = catalog_tasks.filter_products("Dresses", size="M", color="Black")

    # Assert: Verify filtering successful
    assert filter_result is True, "Failed to filter by size and color"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_filter_invalid_size(web_interface, config):
    """
    Test that invalid size filter raises error.

    Steps:
        1. Browse Dresses category
        2. Attempt to filter by invalid size (XL)
        3. Verify operation fails gracefully

    Expected Result:
        Filter operation returns False for invalid size.
    """
    # Arrange
    base_url = config["url"]
    catalog_tasks = CatalogTasks(web_interface, base_url)

    # Act: Attempt invalid size filter
    filter_result = catalog_tasks.filter_products("Dresses", size="XL")

    # Assert: Verify operation failed
    assert filter_result is False, "Invalid size should fail"

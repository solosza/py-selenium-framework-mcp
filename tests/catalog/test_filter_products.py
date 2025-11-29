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
        3. Verify filter applied successfully

    Expected Result:
        Products are filtered by size S.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to filter products by size
    filter_result = guest.filter_products_in_category("Dresses", size="S")

    # Assert: Verify filtering successful
    assert filter_result is True, "Failed to filter by size"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_filter_by_color(web_interface, config):
    """
    Test filtering products by color.

    Uses GuestUser role to orchestrate the filtering workflow.

    Steps:
        1. Create GuestUser role
        2. Call filter_products_in_category() with color filter
        3. Verify filter applied successfully

    Expected Result:
        Products are filtered by color White.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to filter products by color
    filter_result = guest.filter_products_in_category("Dresses", color="White")

    # Assert: Verify filtering successful
    assert filter_result is True, "Failed to filter by color"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_filter_by_size_and_color(web_interface, config):
    """
    Test filtering products by both size and color.

    Uses GuestUser role to orchestrate the combined filter workflow.

    Steps:
        1. Create GuestUser role
        2. Call filter_products_in_category() with both size and color
        3. Verify filters applied successfully

    Expected Result:
        Products are filtered by both size M and color Black.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to filter products by size and color
    filter_result = guest.filter_products_in_category("Dresses", size="M", color="Black")

    # Assert: Verify filtering successful
    assert filter_result is True, "Failed to filter by size and color"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_filter_invalid_size(web_interface, config):
    """
    Test that invalid size filter raises error.

    Uses GuestUser role to test error handling.

    Steps:
        1. Create GuestUser role
        2. Attempt to filter by invalid size (XL)
        3. Verify operation fails gracefully

    Expected Result:
        Filter operation returns False for invalid size.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to attempt invalid size filter
    filter_result = guest.filter_products_in_category("Dresses", size="XL")

    # Assert: Verify operation failed
    assert filter_result is False, "Invalid size should fail"

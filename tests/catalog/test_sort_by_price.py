"""
Catalog Tests - Product Sorting.

Tests sorting products by price (low to high, high to low).
Uses GuestUser role to orchestrate sorting workflows.
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
def test_sort_by_price_low_to_high(web_interface, config):
    """
    Test sorting products by price (lowest first).

    Uses GuestUser role to orchestrate the sorting workflow.

    Steps:
        1. Create GuestUser role
        2. Call sort_products_in_category() with price_asc
        3. Verify products are sorted correctly

    Expected Result:
        Products are sorted by price in ascending order.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to sort products by price ascending
    sort_result = guest.sort_products_in_category("Dresses", "price_asc")

    # Assert: Verify sorting successful (role verifies sort order internally)
    assert sort_result is True, "Failed to sort by price (low to high)"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_sort_by_price_high_to_low(web_interface, config):
    """
    Test sorting products by price (highest first).

    Uses GuestUser role to orchestrate the sorting workflow.

    Steps:
        1. Create GuestUser role
        2. Call sort_products_in_category() with price_desc
        3. Verify products are sorted correctly

    Expected Result:
        Products are sorted by price in descending order.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to sort products by price descending
    sort_result = guest.sort_products_in_category("Dresses", "price_desc")

    # Assert: Verify sorting successful (role verifies sort order internally)
    assert sort_result is True, "Failed to sort by price (high to low)"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_sort_by_name_a_to_z(web_interface, config):
    """
    Test sorting products by name (A to Z).

    Uses GuestUser role to orchestrate the sorting workflow.

    Steps:
        1. Create GuestUser role
        2. Call sort_products_in_category() with name_asc
        3. Verify sorting operation completes

    Expected Result:
        Products are sorted by name alphabetically.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to sort products by name ascending
    sort_result = guest.sort_products_in_category("Women", "name_asc")

    # Assert: Verify sorting successful
    assert sort_result is True, "Failed to sort by name (A to Z)"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_sort_invalid_option(web_interface, config):
    """
    Test that invalid sort option fails gracefully.

    Uses GuestUser role to test error handling.

    Steps:
        1. Create GuestUser role
        2. Attempt invalid sort option
        3. Verify operation returns False

    Expected Result:
        Invalid sort option returns False.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)

    # Act: Use role to attempt invalid sort
    sort_result = guest.sort_products_in_category("Dresses", "invalid_sort")

    # Assert: Verify operation failed
    assert sort_result is False, "Invalid sort option should fail"

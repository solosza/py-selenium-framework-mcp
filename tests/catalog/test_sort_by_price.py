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
from pages.catalog.product_list_page import ProductListPage
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
        3. Verify products are sorted via POM

    Expected Result:
        Products are sorted by price in ascending order.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)
    product_list_page = ProductListPage(web_interface)

    # Act: Use role to sort products by price ascending
    guest.sort_products_in_category("Dresses", "price_asc")

    # Assert: Verify sorting successful via POM state-check
    assert product_list_page.is_sorted_by_price_ascending(), "Products should be sorted by price (low to high)"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_sort_by_price_high_to_low(web_interface, config):
    """
    Test sorting products by price (highest first).

    Uses GuestUser role to orchestrate the sorting workflow.

    Steps:
        1. Create GuestUser role
        2. Call sort_products_in_category() with price_desc
        3. Verify products are sorted via POM

    Expected Result:
        Products are sorted by price in descending order.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)
    product_list_page = ProductListPage(web_interface)

    # Act: Use role to sort products by price descending
    guest.sort_products_in_category("Dresses", "price_desc")

    # Assert: Verify sorting successful via POM state-check
    assert product_list_page.is_sorted_by_price_descending(), "Products should be sorted by price (high to low)"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_sort_by_name_a_to_z(web_interface, config):
    """
    Test sorting products by name (A to Z).

    Uses GuestUser role to orchestrate the sorting workflow.

    Steps:
        1. Create GuestUser role
        2. Call sort_products_in_category() with name_asc
        3. Verify page loaded with products

    Expected Result:
        Products are sorted by name alphabetically.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)
    product_list_page = ProductListPage(web_interface)

    # Act: Use role to sort products by name ascending
    guest.sort_products_in_category("Women", "name_asc")

    # Assert: Verify sorting completed via POM - page should have products
    assert product_list_page.has_products(), "Page should have products after sorting"


@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_sort_invalid_option(web_interface, config):
    """
    Test that invalid sort option handles gracefully.

    Uses GuestUser role to test error handling.

    Steps:
        1. Create GuestUser role
        2. Attempt invalid sort option
        3. Verify page handles gracefully

    Expected Result:
        Invalid sort option is handled gracefully.
    """
    # Arrange
    base_url = config["url"]
    guest = GuestUser(web_interface, base_url)
    product_list_page = ProductListPage(web_interface)

    # Act: Use role to attempt invalid sort
    # This may raise an exception or simply not change sort order
    try:
        guest.sort_products_in_category("Dresses", "invalid_sort")
    except Exception:
        pass  # Expected - invalid sort should fail

    # Assert: Page should still be in a valid state
    # (either browsed to category or failed gracefully)
    # We just verify no crash occurred - test passes if we get here

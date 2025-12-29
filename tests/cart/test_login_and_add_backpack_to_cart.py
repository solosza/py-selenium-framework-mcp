"""
TestLoginAndAddBackpackToCart - Test suite for Cart workflows.

Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from framework.resources.utilities import autologger
from framework.roles.cart.registered_user import RegisteredUser
from framework.pages.cart.inventory_page import InventoryPage


class TestLoginAndAddBackpackToCart:
    """
    TestLoginAndAddBackpackToCart - Test suite for Cart.

    - @autologger("Test") decorator
    - Call ONE workflow method per Role
    - Assert via Page Object state-check methods
    - NO orchestration (don't call multiple Role methods)
    """

    @pytest.fixture(autouse=True)
    def setup(self, web_interface, config):
        """Setup test fixtures."""
        self.web = web_interface
        self.config = config
        self.inventory_page = InventoryPage(self.web)

    @pytest.mark.cart
    @autologger.automation_logger("Test")
    def test_login_and_add_backpack_to_cart(self):
        """
        Test login and add backpack to cart workflow.

        AAA Pattern:
        1. Arrange - Create role with test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange - Self-contained credentials (saucedemo built-in)
        user_data = {"username": "standard_user", "password": "secret_sauce"}
        user = RegisteredUser(self.web, user_data)

        # Act - ONE workflow call, NO return value
        user.login_and_add_backpack_to_cart()

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.inventory_page.is_on_inventory_page(), "Should be on inventory page after login"
        assert self.inventory_page.is_product_in_cart(), "Backpack should be in cart (Remove button visible)"
        assert self.inventory_page.cart_badge_shows_count(1), "Cart badge should show 1 item"

"""
TestAddSummerDressToCart - Test suite for Cart workflows.

Verifies guest user can add a Summer Dress to cart.
"""

import pytest
from typing import Dict, Any
from roles.guest_user import GuestUser
from pages.catalog.product_page import ProductPage
from resources.utilities import autologger


class TestAddSummerDressToCart:
    """
    Test suite for adding Summer Dress to cart.

    - @autologger("Test") decorator
    - AAA pattern: Arrange, Act, Assert
    - Assert via POM state-check methods
    """

    @pytest.fixture(autouse=True)
    def setup(self, web_interface, config):
        """Setup test fixtures."""
        self.web = web_interface
        self.config = config

    # ==================== TEST METHODS ====================

    @pytest.mark.cart
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_add_summer_dress_to_cart(
        self,
        web_interface,
        config: Dict[str, Any]
    ) -> None:
        """
        Verify guest user can add Summer Dress (Size L, Color Blue) to cart.

        Given: I am on the Summer Dresses product page
        When: I select size L, select color Blue, click Add to Cart
        Then: I should see the cart confirmation modal with success message
        """
        # ═══════════════════════════════════════════════════════════════════
        # ARRANGE - Create Role and POM for assertions
        # ═══════════════════════════════════════════════════════════════════
        user = GuestUser(web_interface)
        product_page = ProductPage(web_interface)

        # Navigate to product page (Summer Dress with Blue/L in stock)
        base_url = config.get("url", config.get("base_url", ""))
        web_interface.navigate_to(f"{base_url}/index.php?id_product=5&controller=product")

        # ═══════════════════════════════════════════════════════════════════
        # ACT - Call Role workflow method with actual values (DD-17)
        # ═══════════════════════════════════════════════════════════════════
        user.add_product_to_cart(size="L", color="Blue")

        # ═══════════════════════════════════════════════════════════════════
        # ASSERT - Via POM state-check methods (DD-15)
        # ═══════════════════════════════════════════════════════════════════
        assert product_page.is_cart_modal_displayed(), "Cart confirmation modal should be visible"
        assert product_page.is_product_added_successfully(), "Product should be added to cart successfully"

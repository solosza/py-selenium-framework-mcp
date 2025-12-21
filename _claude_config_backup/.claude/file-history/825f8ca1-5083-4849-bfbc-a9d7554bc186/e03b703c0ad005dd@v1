"""
Cart Tasks - Shopping cart workflow operations.

This module provides high-level task methods that orchestrate page objects
to accomplish cart-related workflows like adding products and proceeding to checkout.
"""

import time
from interfaces.web_interface import WebInterface
from pages.catalog.product_detail_page import ProductDetailPage
from pages.cart.cart_page import CartPage
from resources.utilities import autologger


class CartTasks:
    """Cart task workflows for adding products and managing cart."""

    def __init__(self, web: WebInterface, base_url: str):
        """
        Initialize CartTasks.

        Args:
            web: WebInterface instance
            base_url: Application base URL
        """
        self.web = web
        self.base_url = base_url
        self.product_detail_page = ProductDetailPage(web)
        self.cart_page = CartPage(web)

    # ==================== ADD TO CART METHODS ====================

    @autologger.automation_logger("Task")
    def add_product_to_cart(self, product_url: str, size: str = None, color: str = None, quantity: int = 1) -> None:
        """
        Add a product to cart from product detail page.

        Args:
            product_url: Full URL to product detail page
            size: Optional size to select (e.g., "S", "M", "L")
            color: Optional color to select (e.g., "Green", "Blue")
            quantity: Quantity to add (default 1)
        """
        # Navigate to product detail page
        self.web.navigate_to(product_url)

        # Verify page loaded
        if not self.product_detail_page.is_page_loaded():
            self.web.logger.error("Product detail page did not load")
            return

        # Select size if specified
        if size:
            self.product_detail_page.select_size(size)
            self.web.logger.info(f"Selected size: {size}")

        # Select color if specified
        if color:
            self.product_detail_page.select_color_by_name(color)
            self.web.logger.info(f"Selected color: {color}")

        # Set quantity if more than 1
        if quantity > 1:
            self.product_detail_page.set_quantity(quantity)
            self.web.logger.info(f"Set quantity: {quantity}")

        # Click Add to Cart
        self.product_detail_page.click_add_to_cart()

        # Wait for modal
        time.sleep(2)

        # Verify modal displayed
        if not self.product_detail_page.is_add_to_cart_modal_displayed():
            self.web.logger.error("Add to cart modal did not appear")
            return

        self.web.logger.info("Product added to cart successfully")

    @autologger.automation_logger("Task")
    def add_product_and_proceed_to_checkout(self, product_url: str, size: str = None, color: str = None, quantity: int = 1) -> None:
        """
        Add product to cart and proceed to checkout.

        Args:
            product_url: Full URL to product detail page
            size: Optional size to select
            color: Optional color to select
            quantity: Quantity to add
        """
        # Add product to cart
        self.add_product_to_cart(product_url, size, color, quantity)

        # Click Proceed to checkout in modal
        self.product_detail_page.click_proceed_to_checkout()

        # Wait for cart page
        time.sleep(2)

        # Verify cart page loaded
        if not self.cart_page.is_page_loaded():
            self.web.logger.error("Cart page did not load")
            return

        self.web.logger.info("Navigated to cart page")

    # ==================== CART NAVIGATION METHODS ====================

    @autologger.automation_logger("Task")
    def navigate_to_cart(self) -> None:
        """Navigate to cart page."""
        cart_url = f"{self.base_url}?controller=order"
        self.web.navigate_to(cart_url)

        if not self.cart_page.is_page_loaded():
            self.web.logger.error("Cart page did not load")
            return

        self.web.logger.info("Navigated to cart page")

    @autologger.automation_logger("Task")
    def proceed_from_cart_to_checkout(self) -> None:
        """
        Click proceed to checkout from cart page.

        Assumes already on cart page with items.
        """
        if not self.cart_page.has_items():
            self.web.logger.error("Cart is empty, cannot proceed to checkout")
            return

        self.cart_page.click_proceed_to_checkout()
        self.web.logger.info("Proceeding to checkout from cart")

    # ==================== CART VERIFICATION METHODS ====================

    @autologger.automation_logger("Task")
    def verify_cart_has_items(self) -> bool:
        """
        Verify cart has items.

        Returns:
            True if cart has items
        """
        return self.cart_page.has_items()

    @autologger.automation_logger("Task")
    def get_cart_item_count(self) -> int:
        """
        Get number of items in cart.

        Returns:
            Item count
        """
        return self.cart_page.get_item_count()

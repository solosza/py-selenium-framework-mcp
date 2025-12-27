"""
CartTasks - Task module for cart operations.

Orchestrates ProductPage POM methods for add-to-cart workflow.
"""

from interfaces.web_interface import WebInterface
from pages.catalog.product_page import ProductPage
from resources.utilities import autologger


class CartTasks:
    """
    Task module for Cart operations.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    - Uses fluent POM API
    """

    def __init__(self, web: WebInterface):
        """
        Compose Page Objects - NO decorator on constructor.
        NO base_url parameter - POM gets URL from web.config.
        """
        self.web = web
        self.product_page = ProductPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def add_to_cart(self, size: str, color: str) -> None:
        """
        Single domain operation: add product to cart with specified options.

        Args:
            size: Product size (S, M, L)
            color: Product color (Blue, Black, Orange, Yellow)

        NO return value - test asserts via product_page.is_product_added_successfully()
        """
        # Select size
        self.product_page.select_size(size)

        # Select color based on parameter
        if color.lower() == "blue":
            self.product_page.click_color_blue()
        elif color.lower() == "black":
            self.product_page.click_color_black()
        elif color.lower() == "orange":
            self.product_page.click_color_orange()
        elif color.lower() == "yellow":
            self.product_page.click_color_yellow()

        # Wait for stock status to update (AJAX) before clicking Add to Cart
        self.product_page.wait_for_in_stock()

        # Click add to cart
        self.product_page.click_add_to_cart()

        # NO return - test asserts via product_page.is_product_added_successfully()

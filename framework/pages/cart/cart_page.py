"""
CartPage - Shopping cart page object.

This page represents the shopping cart summary (Step 01 of checkout).
Handles viewing cart contents and proceeding to checkout.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class CartPage:
    """Page Object for Shopping Cart page."""

    def __init__(self, web: WebInterface):
        """
        Initialize CartPage.

        Args:
            web: WebInterface instance
        """
        self.web = web

    # ==================== LOCATORS ====================

    CART_TITLE = (By.CSS_SELECTOR, "#cart_title")
    CART_SUMMARY_TABLE = (By.CSS_SELECTOR, "#cart_summary")
    CART_ITEMS = (By.CSS_SELECTOR, "#cart_summary tbody tr")
    PRODUCT_NAME = (By.CSS_SELECTOR, ".cart_description .product-name a")
    PRODUCT_PRICE = (By.CSS_SELECTOR, ".cart_unit .price")
    PRODUCT_QUANTITY = (By.CSS_SELECTOR, "input.cart_quantity_input")
    TOTAL_PRODUCTS = (By.CSS_SELECTOR, "#total_product")
    TOTAL_SHIPPING = (By.CSS_SELECTOR, "#total_shipping")
    TOTAL_PRICE = (By.CSS_SELECTOR, "#total_price")
    PROCEED_TO_CHECKOUT_BTN = (By.CSS_SELECTOR, "a.standard-checkout")
    EMPTY_CART_MESSAGE = (By.CSS_SELECTOR, ".alert-warning")
    DELETE_ITEM_BTN = (By.CSS_SELECTOR, ".cart_quantity_delete")

    # ==================== PAGE METHODS ====================

    def is_page_loaded(self) -> bool:
        """
        Verify cart page is loaded.

        Returns:
            True if cart summary table is visible
        """
        return self.web.is_element_displayed(*self.CART_SUMMARY_TABLE, timeout=10)

    # ==================== CART ITEM METHODS ====================

    def get_item_count(self) -> int:
        """
        Get number of items in cart.

        Returns:
            Count of items in cart
        """
        items = self.web.find_elements(*self.CART_ITEMS)
        return len(items)

    def has_items(self) -> bool:
        """
        Check if cart has any items.

        Returns:
            True if cart has items
        """
        return self.get_item_count() > 0

    def is_cart_empty(self) -> bool:
        """
        Check if cart is empty.

        Returns:
            True if cart shows empty message
        """
        return self.web.is_element_displayed(*self.EMPTY_CART_MESSAGE, timeout=3)

    def get_product_names(self) -> list:
        """
        Get list of product names in cart.

        Returns:
            List of product names
        """
        elements = self.web.find_elements(*self.PRODUCT_NAME)
        return [el.text.strip() for el in elements]

    def get_total_price(self) -> str:
        """
        Get cart total price.

        Returns:
            Total price as string (e.g., "$23.40")
        """
        element = self.web.find_element(*self.TOTAL_PRICE)
        return element.text.strip()

    # ==================== NAVIGATION METHODS ====================

    def click_proceed_to_checkout(self) -> "CartPage":
        """
        Click proceed to checkout button.

        Returns:
            self for method chaining
        """
        self.web.click(*self.PROCEED_TO_CHECKOUT_BTN)
        return self

    def delete_item_by_index(self, index: int) -> "CartPage":
        """
        Delete item from cart by index.

        Args:
            index: Item index (0-based)

        Returns:
            self for method chaining
        """
        delete_btns = self.web.find_elements(*self.DELETE_ITEM_BTN)
        if index < len(delete_btns):
            delete_btns[index].click()
        return self

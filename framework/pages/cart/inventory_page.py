"""
InventoryPage - Page Object Model for Saucedemo Inventory

Provides atomic UI interactions for the inventory/products page.
"""

from selenium.webdriver.common.by import By
from framework.interfaces.web_interface import WebInterface


class InventoryPage:
    """
    Page Object for Saucedemo Inventory Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    # ==================== LOCATORS (Class Constants) ====================
    BACKPACK_ADD_TO_CART = (By.CSS_SELECTOR, "[data-test='add-to-cart-sauce-labs-backpack']")
    BACKPACK_REMOVE = (By.CSS_SELECTOR, "[data-test='remove-sauce-labs-backpack']")
    SHOPPING_CART_LINK = (By.CSS_SELECTOR, "[data-test='shopping-cart-link']")
    CART_BADGE = (By.CSS_SELECTOR, ".shopping_cart_badge")
    INVENTORY_LIST = (By.CSS_SELECTOR, ".inventory_list")
    PRODUCT_TITLE = (By.CSS_SELECTOR, ".inventory_item_name")

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def click_add_backpack_to_cart(self) -> "InventoryPage":
        """Click Add to Cart for Sauce Labs Backpack."""
        self.web.click(*self.BACKPACK_ADD_TO_CART)
        return self

    def click_remove_backpack(self) -> "InventoryPage":
        """Click Remove for Sauce Labs Backpack."""
        self.web.click(*self.BACKPACK_REMOVE)
        return self

    def click_shopping_cart(self) -> "InventoryPage":
        """Click the shopping cart link."""
        self.web.click(*self.SHOPPING_CART_LINK)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_on_inventory_page(self) -> bool:
        """Check if on inventory page by checking for inventory list."""
        return self.web.is_element_displayed(*self.INVENTORY_LIST, timeout=5)

    def cart_badge_shows_count(self, expected_count: int = 1) -> bool:
        """Check if cart badge shows expected count."""
        if not self.web.is_element_displayed(*self.CART_BADGE, timeout=5):
            return False
        badge_text = self.web.get_text(*self.CART_BADGE)
        return badge_text == str(expected_count)

    def is_product_in_cart(self) -> bool:
        """Check if product was added (Remove button visible instead of Add)."""
        return self.web.is_element_displayed(*self.BACKPACK_REMOVE, timeout=5)

    def get_cart_badge_count(self) -> int:
        """Get the cart badge count as integer."""
        if not self.web.is_element_displayed(*self.CART_BADGE, timeout=3):
            return 0
        badge_text = self.web.get_text(*self.CART_BADGE)
        return int(badge_text) if badge_text.isdigit() else 0

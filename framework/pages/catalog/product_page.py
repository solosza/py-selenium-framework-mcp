"""
ProductPage - Page Object Model

Page Object for the product detail page.
Provides atomic UI interactions for selecting product options and adding to cart.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class ProductPage:
    """
    Page Object for Product Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    # ==================== LOCATORS (Class Constants) ====================
    SIZE_DROPDOWN = (By.CSS_SELECTOR, "select#group_1")
    COLOR_BLUE = (By.CSS_SELECTOR, "ul#color_to_pick_list a[name='Blue']")
    COLOR_BLACK = (By.CSS_SELECTOR, "ul#color_to_pick_list a[name='Black']")
    COLOR_ORANGE = (By.CSS_SELECTOR, "ul#color_to_pick_list a[name='Orange']")
    COLOR_YELLOW = (By.CSS_SELECTOR, "ul#color_to_pick_list a[name='Yellow']")
    QUANTITY_INPUT = (By.CSS_SELECTOR, "input#quantity_wanted")
    ADD_TO_CART_BTN = (By.CSS_SELECTOR, "button.exclusive[name='Submit']")
    CART_MODAL_SUCCESS_MSG = (By.CSS_SELECTOR, "#layer_cart h2")
    CONTINUE_SHOPPING_BTN = (By.CSS_SELECTOR, "span.continue.btn")
    PROCEED_TO_CHECKOUT_LINK = (By.CSS_SELECTOR, "a.btn-proceed-checkout")
    CLOSE_MODAL_BTN = (By.CSS_SELECTOR, "span.cross")
    IN_STOCK_INDICATOR = (By.CSS_SELECTOR, "#availability_value")

    # ==================== CONSTRUCTOR ====================
    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== ATOMIC METHODS (One UI Action) ====================
    def select_size(self, size: str) -> "ProductPage":
        """Select product size from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.SIZE_DROPDOWN, size)
        return self

    def click_color_blue(self) -> "ProductPage":
        """Click the Blue color option."""
        self.web.click(*self.COLOR_BLUE)
        return self

    def click_color_black(self) -> "ProductPage":
        """Click the Black color option."""
        self.web.click(*self.COLOR_BLACK)
        return self

    def click_color_orange(self) -> "ProductPage":
        """Click the Orange color option."""
        self.web.click(*self.COLOR_ORANGE)
        return self

    def click_color_yellow(self) -> "ProductPage":
        """Click the Yellow color option."""
        self.web.click(*self.COLOR_YELLOW)
        return self

    def enter_quantity(self, qty: str) -> "ProductPage":
        """Enter product quantity."""
        self.web.clear(*self.QUANTITY_INPUT)
        self.web.type_text(*self.QUANTITY_INPUT, qty)
        return self

    def click_add_to_cart(self) -> "ProductPage":
        """Click the Add to Cart button."""
        self.web.click(*self.ADD_TO_CART_BTN)
        return self

    def click_continue_shopping(self) -> "ProductPage":
        """Click Continue Shopping button on cart modal."""
        self.web.click(*self.CONTINUE_SHOPPING_BTN)
        return self

    def click_proceed_to_checkout(self) -> "ProductPage":
        """Click Proceed to Checkout link on cart modal."""
        self.web.click(*self.PROCEED_TO_CHECKOUT_LINK)
        return self

    def click_close_modal(self) -> "ProductPage":
        """Click the close button on cart modal."""
        self.web.click(*self.CLOSE_MODAL_BTN)
        return self

    def wait_for_in_stock(self, timeout: int = 10) -> "ProductPage":
        """Wait for product to show 'In stock' status after size/color selection."""
        self.web.wait_for_text_in_element(*self.IN_STOCK_INDICATOR, "In stock", timeout)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================
    def is_cart_modal_displayed(self) -> bool:
        """Check if cart confirmation modal is visible."""
        return self.web.is_element_displayed(*self.CART_MODAL_SUCCESS_MSG, timeout=5)

    def is_product_added_successfully(self) -> bool:
        """Check if product was added to cart successfully."""
        if not self.is_cart_modal_displayed():
            return False
        msg_text = self.web.get_text(*self.CART_MODAL_SUCCESS_MSG)
        return "successfully added" in msg_text.lower()

    def is_in_stock(self) -> bool:
        """Check if product is in stock."""
        try:
            text = self.web.get_text(*self.IN_STOCK_INDICATOR)
            return "in stock" in text.lower()
        except Exception:
            return False

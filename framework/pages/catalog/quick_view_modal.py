"""
Quick View Modal - Product quick view popup page object.

This modal appears when clicking "Quick view" on a product.
Allows viewing product details without leaving the catalog page.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from interfaces.web_interface import WebInterface


class QuickViewModal(BasePage):
    """
    Page Object for Quick View modal popup.

    Provides methods for viewing product details, selecting options,
    and adding to cart from the quick view overlay.
    """

    def __init__(self, web: WebInterface):
        """
        Initialize QuickViewModal.

        Args:
            web: WebInterface instance
        """
        super().__init__(web)

    # ==================== LOCATORS ====================

    # Modal container
    MODAL_CONTAINER = (By.CSS_SELECTOR, ".fancybox-overlay")
    MODAL_IFRAME = (By.CSS_SELECTOR, ".fancybox-iframe")
    CLOSE_BUTTON = (By.CSS_SELECTOR, ".fancybox-close")

    # Product details
    PRODUCT_NAME = (By.CSS_SELECTOR, "h1[itemprop='name']")
    PRODUCT_PRICE = (By.ID, "our_price_display")
    PRODUCT_IMAGE = (By.ID, "bigpic")
    PRODUCT_DESCRIPTION = (By.ID, "short_description_content")

    # Product options - Size
    SIZE_DROPDOWN = (By.ID, "group_1")

    # Product options - Color (displayed as images/swatches)
    COLOR_OPTIONS = (By.CSS_SELECTOR, "#color_to_pick_list li a")

    # Quantity
    QUANTITY_INPUT = (By.ID, "quantity_wanted")
    QUANTITY_UP = (By.CSS_SELECTOR, ".product_quantity_up")
    QUANTITY_DOWN = (By.CSS_SELECTOR, ".product_quantity_down")

    # Actions
    ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, ".exclusive")
    VIEW_FULL_DETAILS = (By.CSS_SELECTOR, "[title='View full details']")

    # Availability
    AVAILABILITY_STATUS = (By.ID, "availability_value")
    IN_STOCK_LABEL = (By.ID, "availability_statut")

    # ==================== PAGE METHODS ====================

    def is_modal_open(self) -> bool:
        """
        Check if quick view modal is open.

        Returns:
            True if modal container is visible
        """
        return self.web.is_element_displayed(*self.MODAL_CONTAINER, timeout=10)

    def switch_to_modal_iframe(self):
        """
        Switch context to modal iframe.

        Quick view modal content is inside an iframe, so we need to switch to it.

        Returns:
            self for method chaining
        """
        self.web.switch_to_frame(*self.MODAL_IFRAME)
        return self

    def switch_back_from_iframe(self):
        """
        Switch context back from iframe to main page.

        Returns:
            self for method chaining
        """
        self.web.switch_to_default_content()
        return self

    def close_modal(self):
        """
        Close quick view modal.

        Returns:
            self for method chaining
        """
        # Switch back to main context if in iframe
        self.switch_back_from_iframe()

        # Click close button
        self.web.click(*self.CLOSE_BUTTON)
        return self

    # ==================== PRODUCT DETAILS METHODS ====================

    def get_product_name(self) -> str:
        """
        Get product name from modal.

        Returns:
            Product name
        """
        return self.web.get_text(*self.PRODUCT_NAME)

    def get_product_price(self) -> str:
        """
        Get product price from modal.

        Returns:
            Product price as string
        """
        return self.web.get_text(*self.PRODUCT_PRICE)

    def get_product_description(self) -> str:
        """
        Get product short description.

        Returns:
            Product description text
        """
        return self.web.get_text(*self.PRODUCT_DESCRIPTION)

    # ==================== PRODUCT OPTIONS METHODS ====================

    def select_size(self, size: str):
        """
        Select product size from dropdown.

        Args:
            size: Size option (e.g., "S", "M", "L")

        Returns:
            self for method chaining
        """
        self.web.select_dropdown_by_visible_text(*self.SIZE_DROPDOWN, text=size)
        return self

    def select_color_by_index(self, index: int):
        """
        Select product color by index.

        Args:
            index: Color option index (0-based)

        Returns:
            self for method chaining
        """
        color_elements = self.web.find_elements(*self.COLOR_OPTIONS)
        if index >= len(color_elements):
            raise IndexError(f"Color index {index} out of range")

        color_elements[index].click()
        return self

    def set_quantity(self, quantity: int):
        """
        Set product quantity.

        Args:
            quantity: Desired quantity (must be > 0)

        Returns:
            self for method chaining
        """
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")

        # Clear and enter quantity
        self.web.type_text(*self.QUANTITY_INPUT, text=str(quantity), clear_first=True)
        return self

    def increase_quantity(self):
        """
        Increase quantity by 1 using + button.

        Returns:
            self for method chaining
        """
        self.web.click(*self.QUANTITY_UP)
        return self

    def decrease_quantity(self):
        """
        Decrease quantity by 1 using - button.

        Returns:
            self for method chaining
        """
        self.web.click(*self.QUANTITY_DOWN)
        return self

    def get_quantity(self) -> int:
        """
        Get current quantity value.

        Returns:
            Current quantity as integer
        """
        value = self.web.get_attribute(*self.QUANTITY_INPUT, attribute="value")
        return int(value or "1")

    # ==================== ACTIONS ====================

    def click_add_to_cart(self):
        """
        Click Add to Cart button.

        Returns:
            self for method chaining
        """
        self.web.click(*self.ADD_TO_CART_BUTTON)
        return self

    def click_view_full_details(self):
        """
        Click link to view full product details page.

        Returns:
            self for method chaining
        """
        self.web.click(*self.VIEW_FULL_DETAILS)
        return self

    # ==================== VALIDATION METHODS ====================

    def is_product_available(self) -> bool:
        """
        Check if product is in stock.

        Returns:
            True if product shows as available
        """
        try:
            status_text = self.web.get_text(*self.AVAILABILITY_STATUS)
            return "In stock" in status_text
        except Exception:
            return False

    def get_availability_status(self) -> str:
        """
        Get product availability status text.

        Returns:
            Availability status
        """
        return self.web.get_text(*self.AVAILABILITY_STATUS)

    def is_add_to_cart_enabled(self) -> bool:
        """
        Check if Add to Cart button is enabled.

        Returns:
            True if button is clickable
        """
        return self.web.is_element_clickable(*self.ADD_TO_CART_BUTTON, timeout=3)

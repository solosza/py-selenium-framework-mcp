"""
ProductsPage - Page Object Model

Page Object for the products browsing and cart interaction page.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class ProductsPage:
    """
    Page Object for Products Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    # ==================== LOCATORS (Class Constants) ====================
    SEARCH_BOX = (By.CSS_SELECTOR, "#search_product")
    SEARCH_BTN = (By.CSS_SELECTOR, "#submit_search")
    ADD_TO_CART_BTN = (By.CSS_SELECTOR, ".productinfo .add-to-cart")
    ADDED_HEADING = (By.CSS_SELECTOR, ".modal-content h4")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".modal-content p")
    VIEW_CART_LINK = (By.CSS_SELECTOR, "a[href='/view_cart']")
    CONTINUE_SHOPPING_BTN = (By.CSS_SELECTOR, ".modal-content button")

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== NAVIGATION ====================
    def navigate(self) -> "ProductsPage":
        """Navigate to products page. Gets URL from WebInterface config."""
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/products")
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================
    def enter_search_text(self, text: str) -> "ProductsPage":
        """Enter text into search box."""
        self.web.type_text(*self.SEARCH_BOX, text)
        return self

    def click_search_btn(self) -> "ProductsPage":
        """Click the search button."""
        self.web.click(*self.SEARCH_BTN)
        return self

    def click_add_to_cart_btn(self) -> "ProductsPage":
        """Click add to cart button (first product)."""
        self.web.click(*self.ADD_TO_CART_BTN)
        return self

    def click_view_cart_link(self) -> "ProductsPage":
        """Click view cart link in modal."""
        self.web.click(*self.VIEW_CART_LINK)
        return self

    def click_continue_shopping_btn(self) -> "ProductsPage":
        """Click continue shopping button in modal."""
        self.web.click(*self.CONTINUE_SHOPPING_BTN)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================
    def is_page_loaded(self) -> bool:
        """Check if products page is loaded."""
        return self.web.is_element_displayed(*self.SEARCH_BOX, timeout=5)

    def is_add_to_cart_modal_visible(self) -> bool:
        """Check if add to cart success modal is visible."""
        return self.web.is_element_displayed(*self.ADDED_HEADING, timeout=5)

    def get_modal_heading(self) -> str:
        """Get the modal heading text."""
        return self.web.get_text(*self.ADDED_HEADING)

    def get_modal_message(self) -> str:
        """Get the modal message text."""
        return self.web.get_text(*self.SUCCESS_MESSAGE)

    def is_registration_successful(self) -> bool:
        """Check if registration was successful (account created heading visible)."""
        account_heading = (By.CSS_SELECTOR, "h2.title")
        try:
            heading_text = self.web.get_text(*account_heading)
            return "ACCOUNT CREATED" in heading_text.upper()
        except:
            return False

    def is_logged_in(self) -> bool:
        """Check if user is logged in (logout link visible in header)."""
        logout_link = (By.CSS_SELECTOR, "a[href='/logout']")
        return self.web.is_element_displayed(*logout_link, timeout=3)

    def is_product_in_cart(self) -> bool:
        """Check if product was added to cart (success modal visible)."""
        return self.is_add_to_cart_modal_visible()

    def has_cart_items(self) -> bool:
        """Check if cart has items (cart badge shows count)."""
        cart_link = (By.CSS_SELECTOR, "a[href='/view_cart']")
        return self.web.is_element_displayed(*cart_link, timeout=3)

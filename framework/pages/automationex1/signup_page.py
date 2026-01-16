"""
SignupPage - Page Object Model

Page Object for the signup/registration entry form.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class SignupPage:
    """
    Page Object for Signup Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    # ==================== LOCATORS (Class Constants) ====================
    NAME = (By.CSS_SELECTOR, "input[name='name']")
    EMAIL = (By.CSS_SELECTOR, "input[data-qa='signup-email']")
    SIGNUP_BTN = (By.CSS_SELECTOR, "button[data-qa='signup-button']")

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== NAVIGATION ====================
    def navigate(self) -> "SignupPage":
        """Navigate to signup page. Gets URL from WebInterface config."""
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/login")
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================
    def enter_name(self, text: str) -> "SignupPage":
        """Enter text into name field."""
        self.web.type_text(*self.NAME, text)
        return self

    def enter_email(self, text: str) -> "SignupPage":
        """Enter text into email field."""
        self.web.type_text(*self.EMAIL, text)
        return self

    def click_signup_btn(self) -> "SignupPage":
        """Click the signup button."""
        self.web.click(*self.SIGNUP_BTN)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================
    def is_page_loaded(self) -> bool:
        """Check if signup form is visible."""
        return self.web.is_element_displayed(*self.NAME, timeout=5)

    def is_registration_successful(self) -> bool:
        """Check if registration was successful (redirected away from signup page)."""
        return not self.web.is_element_displayed(*self.SIGNUP_BTN, timeout=2)

    def is_logged_in(self) -> bool:
        """Check if user is logged in (logout link visible in header)."""
        logout_link = (By.CSS_SELECTOR, "a[href='/logout']")
        return self.web.is_element_displayed(*logout_link, timeout=3)

    def is_product_in_cart(self) -> bool:
        """Check if products exist in cart (cart badge visible)."""
        cart_badge = (By.CSS_SELECTOR, ".cart .badge")
        return self.web.is_element_displayed(*cart_badge, timeout=3)

    def has_cart_items(self) -> bool:
        """Check if cart has items (cart count > 0)."""
        cart_badge = (By.CSS_SELECTOR, ".cart .badge")
        if not self.web.is_element_displayed(*cart_badge, timeout=3):
            return False
        try:
            count_text = self.web.get_text(*cart_badge)
            return int(count_text) > 0
        except (ValueError, Exception):
            return False

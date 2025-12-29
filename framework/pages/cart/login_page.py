"""
LoginPage - Page Object Model for Saucedemo Login

Provides atomic UI interactions for the login page.
"""

from selenium.webdriver.common.by import By
from framework.interfaces.web_interface import WebInterface


class LoginPage:
    """
    Page Object for Saucedemo Login Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    # ==================== LOCATORS (Class Constants) ====================
    USERNAME_INPUT = (By.CSS_SELECTOR, "[data-test='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "[data-test='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "[data-test='login-button']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== NAVIGATION ====================

    def navigate(self) -> "LoginPage":
        """Navigate to the login page."""
        self.web.navigate_to("https://www.saucedemo.com")
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_username(self, username: str) -> "LoginPage":
        """Enter username into the username field."""
        self.web.type_text(*self.USERNAME_INPUT, username)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        """Enter password into the password field."""
        self.web.type_text(*self.PASSWORD_INPUT, password)
        return self

    def click_login(self) -> "LoginPage":
        """Click the login button."""
        self.web.click(*self.LOGIN_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_login_page_displayed(self) -> bool:
        """Check if login page is displayed."""
        return self.web.is_element_displayed(*self.LOGIN_BUTTON, timeout=5)

    def is_error_displayed(self) -> bool:
        """Check if error message is displayed."""
        return self.web.is_element_displayed(*self.ERROR_MESSAGE, timeout=5)

    def get_error_message(self) -> str:
        """Get the error message text."""
        return self.web.get_text(*self.ERROR_MESSAGE)

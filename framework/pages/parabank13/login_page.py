"""
LoginPage - Page Object Model

Page Object representing the login page.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class LoginPage:
    """
    Page Object for Login Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== LOCATORS (Class Constants) ====================
    USERNAME = (By.CSS_SELECTOR, "input[name='username']")
    PASSWORD = (By.CSS_SELECTOR, "input[name='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "input.button[value='Log In']")
    LOGOUT_LINK = (By.LINK_TEXT, "Log Out")

    # ==================== NAVIGATION ====================

    def navigate(self) -> "LoginPage":
        """Navigate to Login page (DD-49: URL from config)."""
        self.web.navigate_to(self.web.config['url'] + '/parabank/index.htm')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_username(self, username: str) -> "LoginPage":
        """Enter username."""
        self.web.type_text(*self.USERNAME, username)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        """Enter password."""
        self.web.type_text(*self.PASSWORD, password)
        return self

    def click_login(self) -> "LoginPage":
        """Click login button."""
        self.web.click(*self.LOGIN_BUTTON)
        return self

    def click_logout(self) -> "LoginPage":
        """Click logout link."""
        self.web.click(*self.LOGOUT_LINK)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_logged_in(self) -> bool:
        """Check if user is logged in by verifying logout link is displayed."""
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)

    def is_logged_out(self) -> bool:
        """Check if user is logged out by verifying login button is displayed."""
        return self.web.is_element_displayed(*self.LOGIN_BUTTON, timeout=5)

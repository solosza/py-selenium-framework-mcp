"""
LoginPage - Page Object Model for ParaBank Login.

Provides atomic UI interactions for the login form.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class LoginPage:
    """
    Page Object for ParaBank Login Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, browser: BrowserInterface):
        """Compose BrowserInterface - NO inheritance."""
        self.browser = browser

    # ==================== LOCATORS (Class Constants) ====================
    USERNAME = (By.CSS_SELECTOR, "input[name='username']")
    PASSWORD = (By.CSS_SELECTOR, "input[name='password']")
    LOGIN_BTN = (By.XPATH, "//input[@value='Log In']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error")

    # ==================== NAVIGATION ====================

    def navigate(self) -> "LoginPage":
        """Navigate to login page."""
        self.browser.navigate_to(self.browser.config['url'] + '/parabank/index.htm')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_username(self, username: str) -> "LoginPage":
        """Enter username."""
        self.browser.enter_text(*self.USERNAME, username)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        """Enter password."""
        self.browser.enter_text(*self.PASSWORD, password)
        return self

    def click_login(self) -> "LoginPage":
        """Click login button."""
        self.browser.click(*self.LOGIN_BTN)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def has_error_message(self) -> bool:
        """Check if error message is displayed."""
        return self.browser.is_element_displayed(*self.ERROR_MESSAGE, timeout=3)

    def get_error_text(self) -> str:
        """Get error message text."""
        return self.browser.get_text(*self.ERROR_MESSAGE)

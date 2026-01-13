"""
LoginPage - Page Object Model

Page Object representing a single page in the application.
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
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[name='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "input[value='Log In']")
    WELCOME_MESSAGE = (By.CSS_SELECTOR, "p.smallText")
    ACCOUNTS_OVERVIEW_HEADING = (By.XPATH, "//h1[text()='Accounts Overview']")

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_username(self, text: str) -> "LoginPage":
        """Enter text into username input field."""
        self.web.type_text(*self.USERNAME_INPUT, text)
        return self

    def enter_password(self, text: str) -> "LoginPage":
        """Enter text into password input field."""
        self.web.type_text(*self.PASSWORD_INPUT, text)
        return self

    def click_login(self) -> "LoginPage":
        """Click the login button."""
        self.web.click(*self.LOGIN_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_on_accounts_overview(self) -> bool:
        """Check if accounts overview heading is displayed."""
        return self.web.is_element_displayed(*self.ACCOUNTS_OVERVIEW_HEADING, timeout=5)

    def is_account_list_visible(self) -> bool:
        """Check if welcome message is visible (indicates successful login)."""
        return self.web.is_element_displayed(*self.WELCOME_MESSAGE, timeout=5)


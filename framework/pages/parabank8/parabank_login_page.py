"""
ParabankLoginPage - Page Object Model

Page Object representing a single page in the application.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class ParabankLoginPage:
    """
    Page Object for Parabank Login Page.

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
    ERROR_HEADING = (By.CSS_SELECTOR, "h1")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "p")
    ACCOUNTS_OVERVIEW_HEADING = (By.XPATH, "//h1[text()='Accounts Overview']")

    # ==================== NAVIGATION ====================

    def navigate(self) -> "ParabankLoginPage":
        """Navigate to login page."""
        self.web.navigate_to(self.web.config['url'] + '/parabank/index.htm')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_username(self, text: str) -> "ParabankLoginPage":
        """Enter text into username input."""
        self.web.type_text(*self.USERNAME_INPUT, text)
        return self

    def enter_password(self, text: str) -> "ParabankLoginPage":
        """Enter text into password input."""
        self.web.type_text(*self.PASSWORD_INPUT, text)
        return self

    def click_login(self) -> "ParabankLoginPage":
        """Click login button."""
        self.web.click(*self.LOGIN_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_on_account_overview(self) -> bool:
        """Check if on account overview page (after successful login)."""
        return self.web.is_element_displayed(*self.ACCOUNTS_OVERVIEW_HEADING, timeout=5)

    def is_account_details_visible(self) -> bool:
        """Check if account details (table) visible."""
        accounts_table = (By.ID, "accountTable")
        return self.web.is_element_displayed(*accounts_table, timeout=5)

    def has_error_message(self) -> bool:
        """Check if error message displayed (invalid login)."""
        return self.web.is_element_displayed(*self.ERROR_HEADING, timeout=3) and \
               self.web.is_element_displayed(*self.ERROR_MESSAGE, timeout=3)
"""
ParabankIndexPage - Page Object Model

Page Object representing a single page in the application.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class ParabankIndexPage:
    """
    Page Object for Parabank Index Page.

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
    LOG_IN = (By.CSS_SELECTOR, "input.button")
    LOG_OUT_LINK = (By.XPATH, "//a[contains(text(), 'Log Out')]")
    ACCOUNTS_OVERVIEW_LINK = (By.XPATH, "//a[contains(text(), 'Accounts Overview')]")

    # ==================== NAVIGATION ====================
    
    def navigate(self) -> "ParabankIndexPage":
        """Navigate to Parabank Index page."""
        self.web.navigate_to(self.web.config['url'] + '/index.htm')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_username(self, username: str) -> "ParabankIndexPage":
        """Enter username."""
        self.web.type_text(*self.USERNAME, text=username)
        return self  # Fluent API

    def enter_password(self, password: str) -> "ParabankIndexPage":
        """Enter password."""
        self.web.type_text(*self.PASSWORD, text=password)
        return self  # Fluent API

    def click_log_in(self) -> "ParabankIndexPage":
        """Click log in button."""
        self.web.click(*self.LOG_IN)
        return self

    def click_log_out_link(self) -> "ParabankIndexPage":
        """Click log out link."""
        self.web.click(*self.LOG_OUT_LINK)
        return self

    def click_accounts_overview_link(self) -> "ParabankIndexPage":
        """Click accounts overview link."""
        self.web.click(*self.ACCOUNTS_OVERVIEW_LINK)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_logged_in(self) -> bool:
        """Check if is logged in by verifying Log Out link is visible."""
        return self.web.is_element_displayed(*self.LOG_OUT_LINK, timeout=5)

    def is_account_overview_visible(self) -> bool:
        """Check if is account overview visible by verifying Accounts Overview link is present."""
        return self.web.is_element_displayed(*self.ACCOUNTS_OVERVIEW_LINK, timeout=5)

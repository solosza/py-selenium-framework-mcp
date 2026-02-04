"""
AccountsOverviewPage - Page Object Model for ParaBank Accounts Overview.

Provides atomic UI interactions for the accounts overview page after login.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class AccountsOverviewPage:
    """
    Page Object for ParaBank Accounts Overview Page.

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
    WELCOME_MESSAGE = (By.XPATH, "//p[contains(text(),'Welcome')]")
    ACCOUNTS_TABLE = (By.ID, "accountTable")
    TRANSFER_FUNDS_LINK = (By.XPATH, "//a[text()='Transfer Funds']")
    LOGOUT_LINK = (By.XPATH, "//a[text()='Log Out']")

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def click_transfer_funds(self) -> "AccountsOverviewPage":
        """Click Transfer Funds link."""
        self.browser.click(*self.TRANSFER_FUNDS_LINK)
        return self

    def click_logout(self) -> "AccountsOverviewPage":
        """Click Logout link."""
        self.browser.click(*self.LOGOUT_LINK)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_logged_in(self) -> bool:
        """Check if user is logged in by looking for welcome message."""
        return self.browser.is_element_displayed(*self.WELCOME_MESSAGE, timeout=10)

    def get_welcome_text(self) -> str:
        """Get welcome message text."""
        return self.browser.get_text(*self.WELCOME_MESSAGE)

    def is_accounts_table_visible(self) -> bool:
        """Check if accounts table is visible."""
        return self.browser.is_element_displayed(*self.ACCOUNTS_TABLE, timeout=5)

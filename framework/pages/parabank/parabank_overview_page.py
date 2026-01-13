"""
ParabankOverviewPage - Page Object Model

Page Object representing a single page in the application.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class ParabankOverviewPage:
    """
    Page Object for Parabank Overview Page.

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
    LOG_OUT_LINK = (By.XPATH, "//a[contains(text(), 'Log Out')]")
    ACCOUNTS_OVERVIEW_LINK = (By.XPATH, "//a[contains(text(), 'Accounts Overview')]")
    ACCOUNT_TABLE = (By.CSS_SELECTOR, "#accountTable")

    # ==================== NAVIGATION ====================
    
    def navigate(self) -> "ParabankOverviewPage":
        """Navigate to Parabank Overview page."""
        self.web.navigate_to(self.web.config['url'] + '/overview.htm')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def click_log_out_link(self) -> "ParabankOverviewPage":
        """Click log out link."""
        self.web.click(*self.LOG_OUT_LINK)
        return self

    def click_accounts_overview_link(self) -> "ParabankOverviewPage":
        """Click accounts overview link."""
        self.web.click(*self.ACCOUNTS_OVERVIEW_LINK)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_logged_in(self) -> bool:
        """Check if is logged in by verifying Log Out link is visible."""
        return self.web.is_element_displayed(*self.LOG_OUT_LINK, timeout=5)

    def is_account_overview_visible(self) -> bool:
        """Check if is account overview visible by verifying account table is displayed."""
        return self.web.is_element_displayed(*self.ACCOUNT_TABLE, timeout=5)

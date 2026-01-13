"""
AccountOverviewPage - Page Object Model

Page Object for ParaBank account overview page (after login).
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class AccountOverviewPage:
    """
    Page Object for Account Overview Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # LOCATORS - Class-level constants, UPPER_SNAKE_CASE
    # ═══════════════════════════════════════════════════════════════════════════
    LOGOUT_LINK = (By.CSS_SELECTOR, "a[href='logout.htm']")
    WELCOME_MESSAGE = (By.CSS_SELECTOR, "p.smallText")
    ACCOUNTS_OVERVIEW_HEADING = (By.CSS_SELECTOR, "h1.title")
    ACCOUNTS_TABLE = (By.CSS_SELECTOR, "#accountTable")

    # ═══════════════════════════════════════════════════════════════════════════
    # CONSTRUCTOR - Compose WebInterface, NO inheritance
    # ═══════════════════════════════════════════════════════════════════════════
    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ═══════════════════════════════════════════════════════════════════════════
    # NAVIGATION - POM owns navigation, gets URL from WebInterface.config
    # ═══════════════════════════════════════════════════════════════════════════
    def navigate(self) -> "AccountOverviewPage":
        """Navigate to this page. Gets URL from WebInterface config."""
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/overview.htm")
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # ATOMIC METHODS - One action per method, return self for chaining
    # ═══════════════════════════════════════════════════════════════════════════
    def click_logout(self) -> "AccountOverviewPage":
        """Click the logout link."""
        self.web.click(*self.LOGOUT_LINK)
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # STATE-CHECK METHODS - For test assertions, return bool
    # ═══════════════════════════════════════════════════════════════════════════
    def is_account_overview_visible(self) -> bool:
        """Check if account overview page is visible."""
        return self.web.is_element_displayed(*self.ACCOUNTS_OVERVIEW_HEADING, timeout=5)

    def is_logged_in(self) -> bool:
        """Check if user is logged in (logout link visible)."""
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)

    def is_welcome_message_displayed(self) -> bool:
        """Check if welcome message is visible."""
        return self.web.is_element_displayed(*self.WELCOME_MESSAGE, timeout=3)

    def get_welcome_message(self) -> str:
        """Get the welcome message text."""
        return self.web.get_text(*self.WELCOME_MESSAGE)

    def is_accounts_table_displayed(self) -> bool:
        """Check if accounts table is visible."""
        return self.web.is_element_displayed(*self.ACCOUNTS_TABLE, timeout=5)

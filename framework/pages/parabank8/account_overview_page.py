"""
AccountOverviewPage - Page Object Model

Page Object representing a single page in the application.
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

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== LOCATORS (Class Constants) ====================
    ACCOUNTS_OVERVIEW_HEADING = (By.XPATH, "//h1[text()='Accounts Overview']")
    ACCOUNTS_TABLE = (By.ID, "accountTable")
    WELCOME_MESSAGE = (By.CSS_SELECTOR, "p.smallText")
    TOTAL_BALANCE = (By.XPATH, "//td[text()='Total']/following-sibling::td")
    ACCOUNT_SERVICES_HEADING = (By.XPATH, "//h2[text()='Account Services']")

    # ==================== NAVIGATION ====================

    def navigate(self) -> "AccountOverviewPage":
        """Navigate to account overview page."""
        self.web.navigate_to(self.web.config['url'] + '/parabank/overview.htm')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def get_total_balance(self) -> str:
        """Get total balance text from table."""
        return self.web.get_text(*self.TOTAL_BALANCE)

    def get_welcome_message(self) -> str:
        """Get welcome message text."""
        return self.web.get_text(*self.WELCOME_MESSAGE)

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_on_account_overview(self) -> bool:
        """Check if on account overview page."""
        return self.web.is_element_displayed(*self.ACCOUNTS_OVERVIEW_HEADING, timeout=5)

    def is_account_details_visible(self) -> bool:
        """Check if account details (table) visible."""
        return self.web.is_element_displayed(*self.ACCOUNTS_TABLE, timeout=5)

    def has_welcome_message(self) -> bool:
        """Check if welcome message is displayed."""
        return self.web.is_element_displayed(*self.WELCOME_MESSAGE, timeout=3)

    def has_account_services(self) -> bool:
        """Check if account services menu is visible."""
        return self.web.is_element_displayed(*self.ACCOUNT_SERVICES_HEADING, timeout=3)
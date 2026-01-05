"""
AccountsOverviewPage - Page Object Model

Page Object representing the ParaBank Accounts Overview and Account Activity pages.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class AccountsOverviewPage:
    """
    Page Object for Accounts Overview and Account Activity Pages.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== NAVIGATION ====================
    def navigate(self) -> "AccountsOverviewPage":
        """Navigate to accounts overview page using config URL."""
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/overview.htm")
        return self

    # ==================== LOCATORS (Class Constants) ====================
    # Overview page locators
    ACCOUNTS_TABLE = (By.CSS_SELECTOR, "#accountTable")
    ACCOUNT_LINKS = (By.CSS_SELECTOR, "a[href*='activity.htm?id=']")
    TOTAL_BALANCE = (By.CSS_SELECTOR, "#accountTable tbody tr:last-child td:nth-child(2)")

    # Account Activity page locators
    ACTIVITY_HEADING = (By.CSS_SELECTOR, "#rightPanel h1.title")
    TRANSACTION_TABLE = (By.CSS_SELECTOR, "#transactionTable")
    TRANSACTION_ROWS = (By.CSS_SELECTOR, "#transactionTable tbody tr")
    TRANSACTION_DESCRIPTION = (By.CSS_SELECTOR, "#transactionTable tbody td a")
    TRANSACTION_CREDIT_AMOUNT = (By.CSS_SELECTOR, "#transactionTable tbody td:nth-child(4)")

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def click_account(self, account_id: str) -> "AccountsOverviewPage":
        """Click on an account link to view its activity."""
        account_link = (By.CSS_SELECTOR, f"a[href*='activity.htm?id={account_id}']")
        self.web.click(*account_link)
        return self

    def click_first_account(self) -> "AccountsOverviewPage":
        """Click on the first account in the list."""
        self.web.click(*self.ACCOUNT_LINKS)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def has_transaction_in_history(self) -> bool:
        """Check if transaction table contains any transfer entries."""
        try:
            text = self.web.get_text(*self.TRANSACTION_DESCRIPTION, timeout=5)
            return "Funds Transfer" in text
        except Exception:
            return False

    def has_transaction_amount(self) -> bool:
        """Check if transaction amount is visible in the activity table."""
        try:
            text = self.web.get_text(*self.TRANSACTION_CREDIT_AMOUNT, timeout=5)
            return "$" in text
        except Exception:
            return False

    def get_transaction_amount(self) -> str:
        """Get the transaction amount from the first transaction row."""
        return self.web.get_text(*self.TRANSACTION_CREDIT_AMOUNT, timeout=5)

    def is_accounts_table_displayed(self) -> bool:
        """Check if accounts overview table is displayed."""
        try:
            return self.web.is_element_displayed(*self.ACCOUNTS_TABLE, timeout=5)
        except Exception:
            return False

    def get_total_balance(self) -> str:
        """Get the total balance from the accounts overview."""
        return self.web.get_text(*self.TOTAL_BALANCE, timeout=5)

"""
TransferFundsPage - Page Object Model for ParaBank Transfer Funds.

Provides atomic UI interactions for the transfer funds form.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class TransferFundsPage:
    """
    Page Object for ParaBank Transfer Funds Page.

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
    AMOUNT = (By.ID, "amount")
    FROM_ACCOUNT = (By.ID, "fromAccountId")
    TO_ACCOUNT = (By.ID, "toAccountId")
    TRANSFER_BTN = (By.XPATH, "//input[@value='Transfer']")
    TRANSFER_COMPLETE_HEADING = (By.XPATH, "//h1[text()='Transfer Complete!']")
    CONFIRMATION_MESSAGE = (By.XPATH, "//p[contains(.,'has been transferred')]")

    # ==================== NAVIGATION ====================

    def navigate(self) -> "TransferFundsPage":
        """Navigate to transfer funds page."""
        self.browser.navigate_to(self.browser.config['url'] + '/parabank/transfer.htm')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_amount(self, amount: str) -> "TransferFundsPage":
        """Enter transfer amount."""
        self.browser.enter_text(*self.AMOUNT, amount)
        return self

    def select_from_account(self, account_id: str) -> "TransferFundsPage":
        """Select source account."""
        self.browser.select_dropdown_by_visible_text(*self.FROM_ACCOUNT, account_id)
        return self

    def select_to_account(self, account_id: str) -> "TransferFundsPage":
        """Select destination account."""
        self.browser.select_dropdown_by_visible_text(*self.TO_ACCOUNT, account_id)
        return self

    def click_transfer(self) -> "TransferFundsPage":
        """Click transfer button."""
        self.browser.click(*self.TRANSFER_BTN)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_transfer_complete(self) -> bool:
        """Check if transfer was completed successfully."""
        return self.browser.is_element_displayed(*self.TRANSFER_COMPLETE_HEADING, timeout=10)

    def get_confirmation_message(self) -> str:
        """Get transfer confirmation message."""
        return self.browser.get_text(*self.CONFIRMATION_MESSAGE)

    def has_transfer_confirmation(self) -> bool:
        """Check if transfer confirmation message is displayed."""
        return self.browser.is_element_displayed(*self.CONFIRMATION_MESSAGE, timeout=5)

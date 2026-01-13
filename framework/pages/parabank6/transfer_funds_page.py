"""
TransferFundsPage - Page Object Model

Page Object representing a single page in the application.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class TransferFundsPage:
    """
    Page Object for Transfer Funds Page.

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
    AMOUNT_INPUT = (By.CSS_SELECTOR, "#amount")
    FROM_ACCOUNT_DROPDOWN = (By.CSS_SELECTOR, "#fromAccountId")
    TO_ACCOUNT_DROPDOWN = (By.CSS_SELECTOR, "#toAccountId")
    TRANSFER_BUTTON = (By.CSS_SELECTOR, "input.button[value='Transfer']")
    CONFIRMATION_HEADING = (By.CSS_SELECTOR, "h1")
    TRANSFER_MESSAGE = (By.CSS_SELECTOR, "div#showResult p")

    # ==================== NAVIGATION ====================
    def navigate(self) -> "TransferFundsPage":
        """Navigate to transfer funds page."""
        self.web.navigate_to(self.web.config['url'] + '/transfer.htm')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================
    def enter_amount(self, amount: str) -> "TransferFundsPage":
        """Enter transfer amount."""
        self.web.type_text(*self.AMOUNT_INPUT, amount)
        return self

    def select_from_account(self, account_id: str) -> "TransferFundsPage":
        """Select source account from dropdown."""
        self.web.select_dropdown_by_value(*self.FROM_ACCOUNT_DROPDOWN, account_id)
        return self

    def select_to_account(self, account_id: str) -> "TransferFundsPage":
        """Select destination account from dropdown."""
        self.web.select_dropdown_by_value(*self.TO_ACCOUNT_DROPDOWN, account_id)
        return self

    def click_transfer(self) -> "TransferFundsPage":
        """Click transfer button."""
        self.web.click(*self.TRANSFER_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================
    def is_transfer_confirmed(self) -> bool:
        """Check if transfer confirmation is displayed."""
        return self.web.is_element_displayed(*self.CONFIRMATION_HEADING, timeout=5)

    def are_balances_updated(self) -> bool:
        """Check if transfer message is displayed (indicates balances updated)."""
        return self.web.is_element_displayed(*self.TRANSFER_MESSAGE, timeout=5)

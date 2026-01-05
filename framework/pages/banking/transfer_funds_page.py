"""
TransferFundsPage - Page Object Model

Page Object representing the ParaBank Transfer Funds page.
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

    # ==================== NAVIGATION ====================
    def navigate(self) -> "TransferFundsPage":
        """Navigate to transfer funds page using config URL."""
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/transfer.htm")
        return self

    # ==================== LOCATORS (Class Constants) ====================
    AMOUNT_INPUT = (By.CSS_SELECTOR, "#amount")
    FROM_ACCOUNT_SELECT = (By.CSS_SELECTOR, "#fromAccountId")
    TO_ACCOUNT_SELECT = (By.CSS_SELECTOR, "#toAccountId")
    TRANSFER_BUTTON = (By.CSS_SELECTOR, "input[value='Transfer']")

    # State-check locators
    TRANSFER_COMPLETE_HEADING = (By.CSS_SELECTOR, "#rightPanel h1")
    TRANSFER_CONFIRMATION_MESSAGE = (By.CSS_SELECTOR, "#rightPanel p")

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_amount(self, amount: str) -> "TransferFundsPage":
        """Enter transfer amount."""
        self.web.type_text(*self.AMOUNT_INPUT, amount)
        return self

    def select_from_account(self, account_id: str) -> "TransferFundsPage":
        """Select source account for transfer."""
        self.web.select_dropdown_by_visible_text(*self.FROM_ACCOUNT_SELECT, account_id)
        return self

    def select_to_account(self, account_id: str) -> "TransferFundsPage":
        """Select destination account for transfer."""
        self.web.select_dropdown_by_visible_text(*self.TO_ACCOUNT_SELECT, account_id)
        return self

    def click_transfer(self) -> "TransferFundsPage":
        """Click the Transfer button."""
        self.web.click(*self.TRANSFER_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_transfer_confirmed(self) -> bool:
        """Check if transfer was successfully completed."""
        try:
            text = self.web.get_text(*self.TRANSFER_COMPLETE_HEADING, timeout=5)
            return "Transfer Complete" in text
        except Exception:
            return False

    def has_transfer_amount(self) -> bool:
        """Check if transfer amount is displayed in confirmation."""
        try:
            text = self.web.get_text(*self.TRANSFER_CONFIRMATION_MESSAGE, timeout=5)
            return "has been transferred" in text
        except Exception:
            return False

    def get_confirmation_message(self) -> str:
        """Get the transfer confirmation message."""
        return self.web.get_text(*self.TRANSFER_CONFIRMATION_MESSAGE, timeout=5)

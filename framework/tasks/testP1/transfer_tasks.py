"""
TransferTasks - Task module for transfer operations.

Orchestrates page objects to perform fund transfer workflows.
"""

from interfaces.browser_interface import BrowserInterface
from pages.testP1.accounts_overview_page import AccountsOverviewPage
from pages.testP1.transfer_funds_page import TransferFundsPage
from resources.utilities import autologger


class TransferTasks:
    """
    Task module for transfer fund operations.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    - Uses fluent POM API
    """

    def __init__(self, browser: BrowserInterface):
        """
        Compose Page Objects - NO decorator on constructor.

        Args:
            browser: BrowserInterface instance
        """
        self.browser = browser
        self.accounts_overview_page = AccountsOverviewPage(browser)
        self.transfer_funds_page = TransferFundsPage(browser)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def transfer_funds(self, amount: str, from_account: str, to_account: str) -> None:
        """
        Transfer funds between accounts.

        Args:
            amount: Amount to transfer
            from_account: Source account ID
            to_account: Destination account ID

        NO return value - test asserts via POM.
        """
        # Navigate to transfer funds page
        self.accounts_overview_page.click_transfer_funds()

        # Fill form and submit
        (self.transfer_funds_page
            .enter_amount(amount)
            .select_from_account(from_account)
            .select_to_account(to_account)
            .click_transfer())
        # NO return

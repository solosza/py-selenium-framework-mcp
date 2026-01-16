"""
Open a new checking account by selecting account type and from account

This module provides high-level task methods that orchestrate page objects
to accomplish business workflows.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from pages.parabank13.open_account_page import OpenAccountPage


class OpenAccountTasks:
    """
    Task module for Open Account operations.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    - Uses fluent POM API
    """

    def __init__(self, web: WebInterface):
        """
        Compose Page Objects - NO decorator on constructor.

        Args:
            web: WebInterface instance
        """
        self.web = web
        self.open_account_page = OpenAccountPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def open_new_checking_account(self, account_type: str) -> None:
        """
        Open a new checking account.

        Args:
            account_type: Type of account (CHECKING or SAVINGS)

        NOTE: Uses the default selected account (first account in dropdown) for initial deposit transfer.

        NO return value - test asserts via POM state-check methods.
        """
        (self.open_account_page
            .navigate()
            .select_account_type(account_type)
            .click_open_account())
        # NO return - test asserts via POM

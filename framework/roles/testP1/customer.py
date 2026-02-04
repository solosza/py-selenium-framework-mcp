"""
Customer - Role for authenticated ParaBank customer.

Orchestrates complete business workflows using Task modules.
"""

from interfaces.browser_interface import BrowserInterface
from resources.utilities import autologger
from tasks.testP1.auth_tasks import AuthTasks
from tasks.testP1.transfer_tasks import TransferTasks


class Customer:
    """
    Customer role - orchestrates complete business workflows.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - Workflow methods call MULTIPLE tasks
    - NO return values
    - NO locators
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, browser_interface: BrowserInterface, username: str, password: str):
        """
        Initialize and compose Task modules.

        Args:
            browser_interface: BrowserInterface instance
            username: Customer username
            password: Customer password
        """
        self.browser = browser_interface
        self.username = username
        self.password = password
        self.auth_tasks = AuthTasks(browser_interface)
        self.transfer_tasks = TransferTasks(browser_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def login_and_transfer_funds(self, amount: str, from_account: str, to_account: str) -> None:
        """
        Complete workflow: Login and transfer funds.

        This workflow method orchestrates MULTIPLE task operations:
        1. Log in with credentials
        2. Transfer funds between accounts

        Args:
            amount: Amount to transfer
            from_account: Source account ID
            to_account: Destination account ID

        NO return value - test asserts via POM state-check methods.
        """
        self.auth_tasks.log_in(self.username, self.password)
        self.transfer_tasks.transfer_funds(amount, from_account, to_account)
        # NO return - test asserts via POM

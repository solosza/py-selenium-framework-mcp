"""New Customer Role - Complete banking onboarding workflow."""
from typing import Dict, Any
from framework.interfaces.web_interface import WebInterface
from framework.tasks.test10.banking_tasks import BankingTasks
from framework.resources.utilities import autologger


class NewCustomer:
    """
    Role representing a new customer completing banking onboarding.

    This role orchestrates the complete workflow:
    1. Register for an account
    2. Open a new checking account
    3. Transfer funds to the new account
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, base_url: str):
        self.web = web_interface
        self.base_url = base_url
        # Compose task modules
        self.banking_tasks = BankingTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def complete_banking_onboarding(self, user_data: Dict[str, Any], transfer_amount: str = "100") -> None:
        """
        Complete the full banking onboarding workflow.

        This orchestrates multiple tasks into a complete user journey:
        1. Register new user account
        2. Open new checking account (auto-logged in after registration)
        3. Transfer funds to the new account

        Args:
            user_data: Dictionary with registration data
            transfer_amount: Amount to transfer to new account

        Note: NO return value - test asserts via POM state-check methods
        """
        # Step 1: Register new user (auto-logs in after registration)
        self.banking_tasks.register_new_user(user_data)

        # Step 2: Open new checking account
        self.banking_tasks.open_checking_account()

        # Step 3: Transfer funds to the new account
        self.banking_tasks.transfer_funds(transfer_amount)

    @autologger.automation_logger("Role")
    def register_and_verify(self, user_data: Dict[str, Any]) -> None:
        """
        Register a new user and verify success.

        Shorter workflow - just registration, no account operations.

        Args:
            user_data: Dictionary with registration data
        """
        self.banking_tasks.register_new_user(user_data)

    @autologger.automation_logger("Role")
    def open_account_and_transfer(self, transfer_amount: str = "100") -> None:
        """
        Open account and transfer funds (assumes already logged in).

        Args:
            transfer_amount: Amount to transfer
        """
        self.banking_tasks.open_checking_account()
        self.banking_tasks.transfer_funds(transfer_amount)

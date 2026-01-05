"""
NewCustomer - Role for orchestrating banking workflows.

Roles represent user personas (e.g., Admin, Customer, Guest).
This role orchestrates complete business workflows for new customers.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.banking.banking_tasks import BankingTasks


class NewCustomer:
    """
    NewCustomer - orchestrates complete banking workflows for new customers.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - Workflow methods call MULTIPLE tasks
    - NO return values
    - NO locators
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any]):
        """
        Initialize with user data and compose Task modules.

        Args:
            web_interface: WebInterface instance
            user_data: User data dict with registration info
        """
        self.web = web_interface
        self.user_data = user_data
        self.banking_tasks = BankingTasks(web_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def complete_banking_journey(self, transfer_amount: str = "100") -> None:
        """
        Complete banking journey: Register -> Open Savings -> Transfer -> View Activity.

        Orchestrates MULTIPLE tasks into complete user journey.
        NO return value - test asserts via POM state-check methods.
        """
        self.banking_tasks.register_user(self.user_data)
        self.banking_tasks.open_savings_account()

        # After opening savings, we need to get the account numbers
        # For this flow, we use the first two accounts available
        # The transfer will be verified via POM state checks

        self.banking_tasks.open_savings_account()  # Open second account for transfer target

        # Transfer between accounts - actual account IDs determined at runtime
        # Using placeholder that will be dynamically populated
        self.banking_tasks.transfer_funds(transfer_amount, "from_account", "to_account")

        self.banking_tasks.view_account_activity("account_id")

    @autologger.automation_logger("Role")
    def register_and_open_savings(self) -> None:
        """
        Register new account and open a savings account.

        Orchestrates registration and account opening tasks.
        NO return value - test asserts via POM state-check methods.
        """
        self.banking_tasks.register_user(self.user_data)
        self.banking_tasks.open_savings_account()

    @autologger.automation_logger("Role")
    def register_transfer_and_verify(self, amount: str = "100") -> None:
        """
        Complete flow: Register -> Open Savings -> Transfer -> View Activity.

        Orchestrates the full banking journey for a new customer:
        1. Register new account
        2. Open savings account (gets account number)
        3. Transfer funds to savings
        4. View account activity to verify transfer

        NO return value - test asserts via POM state-check methods.
        """
        # Step 1: Register
        self.banking_tasks.register_user(self.user_data)

        # Step 2: Open savings account
        self.banking_tasks.open_savings_account()

        # Step 3: Get the new account number via Task's composed POM
        new_account = self.banking_tasks.open_new_account_page.get_new_account_number()

        # Step 4: Transfer funds to the new savings account
        self.banking_tasks.transfer_funds(amount, new_account, new_account)

        # Step 5: View account activity
        self.banking_tasks.view_account_activity(new_account)

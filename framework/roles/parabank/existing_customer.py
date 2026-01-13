"""
ExistingCustomer - Role for orchestrating business workflows.

Roles represent user personas (e.g., Admin, Customer, Guest).
This role orchestrates complete business workflows using Task modules.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.parabank.parabank_tasks import ParabankTasks


class ExistingCustomer:
    """
    ExistingCustomer - orchestrates complete business workflows.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - Workflow methods call MULTIPLE tasks
    - NO return values
    - NO locators
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any], base_url: str):
        """
        Initialize with credentials and compose Task modules.

        Args:
            web_interface: WebInterface instance
            user_data: User data dict with username/password
            base_url: Application base URL
        """
        self.web = web_interface
        self.base_url = base_url
        self.user_data = user_data
        self.username = user_data.get('username')
        self.password = user_data.get('password')

        # Validate required credentials
        if not self.username or not self.password:
            raise ValueError(f"ExistingCustomer requires username and password in user_data")

        self.parabank_tasks = ParabankTasks(web_interface, base_url)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def complete_banking_workflow(self, account_type: str, from_account_id: str, transfer_amount: str, to_account_id: str) -> None:
        """
        Execute complete banking workflow: login, open account, transfer funds.
        
        This orchestrates MULTIPLE task methods into a complete user journey.

        NO return value - test asserts via POM state-check methods.
        """
        # Step 1: Login
        self.parabank_tasks.login(self.username, self.password)
        
        # Step 2: Open new savings account
        self.parabank_tasks.open_new_account(account_type, from_account_id)
        
        # Step 3: Transfer funds
        self.parabank_tasks.transfer_funds(transfer_amount, from_account_id, to_account_id)
        
        # NO return - test asserts via POM state-check methods

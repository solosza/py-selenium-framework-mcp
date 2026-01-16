"""
RegisteredUser - Role for orchestrating business workflows.

Roles represent user personas (e.g., Admin, Customer, Guest).
This role orchestrates complete business workflows using Task modules.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.parabank13.auth_tasks import AuthTasks
from tasks.parabank13.open_account_tasks import OpenAccountTasks


class RegisteredUser:
    """
    RegisteredUser - orchestrates complete business workflows.

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
        Initialize with credentials and compose Task modules.

        Args:
            web_interface: WebInterface instance
            user_data: User data dict with username/password
        """
        self.web = web_interface
        self.user_data = user_data

        # Dynamic credential resolution - works with any field names
        self.username = (
            user_data.get('username') or
            user_data.get('email') or
            user_data.get('user_id') or
            user_data.get('login')
        )
        self.password = (
            user_data.get('password') or
            user_data.get('pin') or
            user_data.get('secret')
        )

        # Validate credentials present
        if not self.username or not self.password:
            raise ValueError(f"RegisteredUser requires username and password. Got: {list(user_data.keys())}")

        self.auth_tasks = AuthTasks(web_interface)
        self.open_account_tasks = OpenAccountTasks(web_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def open_new_checking_account(self, account_type: str) -> None:
        """
        Execute open new checking account workflow.

        Complete workflow: Login -> Open Account

        Args:
            account_type: Type of account (CHECKING or SAVINGS)

        NOTE: Uses the default selected account (first account in dropdown) for initial deposit transfer.

        NO return value - test asserts via POM state-check methods.
        """
        # Step 1: Authenticate
        self.auth_tasks.log_in(self.username, self.password)

        # Step 2: Open new account
        self.open_account_tasks.open_new_checking_account(account_type)
        # NO return - test asserts via POM

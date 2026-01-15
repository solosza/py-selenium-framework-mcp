"""
Parabank11RegisteredUser - Role for orchestrating business workflows.

Roles represent user personas (e.g., Admin, Customer, Guest).
This role orchestrates complete business workflows using Task modules.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.parabank11.parabank11_tasks import Parabank11Tasks
from tasks.parabank11.parabank11_auth_tasks import Parabank11AuthTasks


class Parabank11RegisteredUser:
    """
    Parabank11RegisteredUser - orchestrates complete business workflows.

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

        # Dynamic credential resolution (DEF-063)
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

        # Validate required credentials
        if not self.username or not self.password:
            raise ValueError(f"Parabank11RegisteredUser requires username and password. Got: {list(user_data.keys())}")

        # Compose Task modules
        self.auth_tasks = Parabank11AuthTasks(web_interface)
        self.parabank11_tasks = Parabank11Tasks(web_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def open_new_checking_account(self, account_type: str, from_account_id: str) -> None:
        """
        Complete workflow: Login then open new checking account.

        Orchestrates MULTIPLE tasks:
        - Authenticate user via AuthTasks
        - Open new account via Parabank11Tasks

        NO return value - test asserts via POM state-check methods.
        """
        # First, login
        self.auth_tasks.log_in(self.username, self.password)

        # Then, open account
        self.parabank11_tasks.open_new_checking_account(account_type, from_account_id)
        # NO return - test asserts via open_account_page.is_account_opened()

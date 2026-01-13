"""
RegisteredUser - Role for orchestrating business workflows.

Roles represent user personas (e.g., Admin, Customer, Guest).
This role orchestrates complete business workflows using Task modules.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.parabank7.parabank7_tasks import Parabank7Tasks


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
            user_data: User data dict with email/password
        """
        self.web = web_interface
        self.user_data = user_data
        self.email = user_data.get('email')
        self.password = user_data.get('password')

        # Validate required credentials
        if not self.email or not self.password:
            raise ValueError(f"RegisteredUser requires email and password in user_data")

        # Compose Task - NO base_url parameter (Task 26.0 fix)
        self.parabank7_tasks = Parabank7Tasks(web_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def login_and_view_account_overview(self) -> None:
        """
        Execute login and view account overview workflow.

        NO return value - test asserts via POM state-check methods.
        """
        self.parabank7_tasks.login_and_view_account_overview(self.email, self.password)
        # NO return - test asserts via POM

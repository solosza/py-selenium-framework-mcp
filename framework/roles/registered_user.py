"""
RegisteredUser - Role for orchestrating business workflows.

Roles represent user personas (e.g., Admin, Customer, Guest).
This role orchestrates complete business workflows using Task modules.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.parabank8.parabank8_tasks import Parabank8Tasks


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
        self.username = user_data.get('username')
        self.password = user_data.get('password')

        # Validate required credentials
        if not self.username or not self.password:
            raise ValueError(f"RegisteredUser requires username and password in user_data")

        self.parabank8_tasks = Parabank8Tasks(web_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def login_and_view_account_overview(self) -> None:
        """
        Login and view account overview workflow.
        
        Orchestrates: navigate + enter credentials + submit + verify overview.

        NO return value - test asserts via POM state-check methods.
        """
        self.parabank8_tasks.log_in(self.username, self.password)
        # NO return - test asserts via POM
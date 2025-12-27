"""
GuestUser - Role representing a guest user persona.

Orchestrates AuthTasks for user registration workflow.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.auth.auth_tasks import AuthTasks
from resources.utilities import autologger


class GuestUser:
    """Role representing a guest user who can register for an account."""

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web: WebInterface, user_data: Dict[str, Any]):
        """
        Compose WebInterface + Tasks, NO inheritance, NO base_url.

        Args:
            web: WebInterface instance
            user_data: User registration data (email, password, first_name, last_name)
        """
        self.web = web
        self.user_data = user_data
        self.email = user_data.get("email")
        self.password = user_data.get("password")
        self.first_name = user_data.get("first_name")
        self.last_name = user_data.get("last_name")

        # Compose Task modules - NO base_url passed
        self.auth_tasks = AuthTasks(web)

    @autologger.automation_logger("Role")
    def register_account(self) -> None:
        """
        Complete workflow: Register a new user account.

        Orchestrates AuthTasks to complete registration.
        NO return value - test asserts via POM state methods.
        """
        self.auth_tasks.register_user(self.user_data)
        # NO return - test asserts via registration_page.is_account_created()

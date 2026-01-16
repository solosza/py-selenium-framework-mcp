"""
Authentication tasks for parabank13 workflow.

This module provides high-level task methods that orchestrate page objects
to accomplish authentication workflows.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from pages.parabank13.login_page import LoginPage


class AuthTasks:
    """
    Task module for Authentication operations.

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
        self.login_page = LoginPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def log_in(self, username: str, password: str) -> None:
        """
        Log in to the application.

        Args:
            username: Username for authentication
            password: Password for authentication

        NO return value - test asserts via POM state-check methods.
        """
        (self.login_page
            .navigate()
            .enter_username(username)
            .enter_password(password)
            .click_login())
        # NO return - test asserts via POM

    @autologger.automation_logger("Task")
    def log_out(self) -> None:
        """
        Log out from the application.

        NO return value - test asserts via POM state-check methods.
        """
        self.login_page.click_logout()
        # NO return - test asserts via POM

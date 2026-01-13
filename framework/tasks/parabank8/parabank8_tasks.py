"""
Login to ParaBank and view account overview

This module provides high-level task methods that orchestrate page objects
to accomplish business workflows.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from pages.parabank8.parabank_login_page import ParabankLoginPage


class Parabank8Tasks:
    """
    Task module for parabank8 workflow operations.

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
        self.parabank_login_page = ParabankLoginPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def log_in(self, username: str, password: str) -> None:
        """
        Complete login operation. Single domain operation: authenticate user.

        NO return value - test asserts via POM state-check methods.
        """
        (self.parabank_login_page
            .navigate()
            .enter_username(username)
            .enter_password(password)
            .click_login())
        # NO return - test asserts via POM
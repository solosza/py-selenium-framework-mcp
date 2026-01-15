"""
Parabank11AuthTasks - ParaBank-specific authentication workflows.

Task module for ParaBank authentication using ParabankLoginPage.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from pages.parabank11.parabank_login_page import ParabankLoginPage


class Parabank11AuthTasks:
    """
    Parabank11AuthTasks - ParaBank authentication workflows.

    - @autologger("Task") on workflow methods
    - Composes ParabankLoginPage (uses username field, not email)
    - NO return values
    - NO locators
    """

    def __init__(self, web: WebInterface):
        """Compose Page Objects - NO inheritance."""
        self.web = web
        self.login_page = ParabankLoginPage(web)

    @autologger.automation_logger("Task")
    def log_in(self, username: str, password: str) -> None:
        """
        Login workflow for ParaBank application.

        Uses ParabankLoginPage which expects username field (not email).
        NO return value - test asserts via login_page.is_logged_in()
        """
        self.login_page.navigate()
        (self.login_page
            .enter_username(username)
            .enter_password(password)
            .click_login())
        # NO return - test asserts via login_page.is_logged_in()

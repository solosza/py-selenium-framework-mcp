"""
AuthTasks - Task module for authentication operations.

Orchestrates page objects to perform login/logout workflows.
"""

from interfaces.browser_interface import BrowserInterface
from pages.testP1.login_page import LoginPage
from pages.testP1.accounts_overview_page import AccountsOverviewPage
from resources.utilities import autologger


class AuthTasks:
    """
    Task module for authentication operations.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    - Uses fluent POM API
    """

    def __init__(self, browser: BrowserInterface):
        """
        Compose Page Objects - NO decorator on constructor.

        Args:
            browser: BrowserInterface instance
        """
        self.browser = browser
        self.login_page = LoginPage(browser)
        self.accounts_overview_page = AccountsOverviewPage(browser)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def log_in(self, username: str, password: str) -> None:
        """
        Log in with provided credentials.

        Args:
            username: User's username
            password: User's password

        NO return value - test asserts via POM.
        """
        (self.login_page
            .navigate()
            .enter_username(username)
            .enter_password(password)
            .click_login())
        # NO return

    @autologger.automation_logger("Task")
    def log_out(self) -> None:
        """
        Log out from the application.

        NO return value - test asserts via POM.
        """
        self.accounts_overview_page.click_logout()
        # NO return

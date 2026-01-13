"""
ParabankTasks - Task Module

Orchestrates ParaBank page objects for domain operations.
NO return values - tests assert via POM state-check methods.
"""

from interfaces.web_interface import WebInterface
from pages.parabank.parabank_index_page import ParabankIndexPage
from pages.parabank.parabank_overview_page import ParabankOverviewPage
from resources.utilities import autologger


class ParabankTasks:
    """
    Task module for ParaBank operations.

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
        self.parabank_index_page = ParabankIndexPage(web)
        self.parabank_overview_page = ParabankOverviewPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def login_and_view_overview(self, username: str, password: str) -> None:
        """
        Login to ParaBank and navigate to account overview.

        Args:
            username: User's username
            password: User's password

        NO return value - test asserts via POM.
        """
        (self.parabank_index_page
            .navigate()
            .enter_username(username)
            .enter_password(password)
            .click_log_in())
        # NO return

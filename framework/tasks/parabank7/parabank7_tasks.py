"""
Parabank7Tasks - Task Module

Task module for ParaBank operations.
Orchestrates page objects to accomplish business workflows.
"""

from interfaces.web_interface import WebInterface
from pages.parabank7.parabank_index_page import ParabankIndexPage
from pages.parabank7.account_overview_page import AccountOverviewPage
from resources.utilities import autologger


class Parabank7Tasks:
    """
    Task module for ParaBank workflow operations.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    - Uses fluent POM API
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # CONSTRUCTOR - Compose WebInterface + POMs, NO inheritance, NO base_url
    # ═══════════════════════════════════════════════════════════════════════════
    def __init__(self, web: WebInterface):
        """
        Compose Page Objects - NO decorator on constructor.

        Args:
            web: WebInterface instance
        """
        self.web = web
        # Compose page objects - they get URL from self.web.config
        self.login_page = ParabankIndexPage(web)
        self.overview_page = AccountOverviewPage(web)

    # ═══════════════════════════════════════════════════════════════════════════
    # TASK METHODS - Single domain operation, return None, use @autologger
    # ═══════════════════════════════════════════════════════════════════════════
    @autologger.automation_logger("Task")
    def login_and_view_account_overview(self, username: str, password: str) -> None:
        """
        Single domain operation: login to ParaBank and view account overview.

        NO return value - test asserts via overview_page.is_account_overview_visible()
        """
        # POM handles navigation (gets URL from self.web.config)
        (self.login_page
            .navigate()
            .enter_username(username)
            .enter_password(password)
            .click_login())

        # NO return statement

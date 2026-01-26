"""
ClawdbotTasks - Task module for search operations

This module provides high-level task methods that orchestrate page objects
to accomplish business workflows.
"""

from interfaces.web_interface import WebInterface
from pages.clawdbot.sales_leads_page import SalesLeadsPage
from resources.utilities import autologger


class ClawdbotTasks:
    """
    Task module for Clawdbot operations.

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
        self.sales_leads_page = SalesLeadsPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def search_for_sales_representative(self, search_term: str) -> None:
        """
        Search for a sales representative in the leads page.

        Args:
            search_term: The search term to use (e.g., "sales representative")

        NO return value - test asserts via POM.
        """
        (self.sales_leads_page
            .navigate()
            .enter_search_text(search_term)
            .wait_for_results())
        # NO return

    @autologger.automation_logger("Task")
    def view_first_lead(self) -> None:
        """
        View the first lead in the search results.

        NO return value - test asserts via POM.
        """
        self.sales_leads_page.click_view_first_lead()
        # NO return

    @autologger.automation_logger("Task")
    def clear_search(self) -> None:
        """
        Clear the search input.

        NO return value - test asserts via POM.
        """
        self.sales_leads_page.clear_search()
        # NO return

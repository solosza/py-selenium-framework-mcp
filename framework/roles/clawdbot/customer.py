"""
Customer - Role for orchestrating business workflows.

Roles represent user personas (e.g., Admin, Customer, Guest).
This role orchestrates complete business workflows using Task modules.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.clawdbot.clawdbot_tasks import ClawdbotTasks


class Customer:
    """
    Customer - orchestrates complete business workflows.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - Workflow methods call MULTIPLE tasks
    - NO return values
    - NO locators
    - NO credentials required (credential_strategy='none')
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface):
        """
        Initialize and compose Task modules.

        Args:
            web_interface: WebInterface instance

        Note: No credentials required (credential_strategy='none' from Step 2)
        """
        self.web = web_interface
        self.clawdbot_tasks = ClawdbotTasks(web_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def search_for_sales_representative(self, search_term: str = "sales representative") -> None:
        """
        Execute search for sales representative workflow.

        Args:
            search_term: The search term to use

        NO return value - test asserts via POM state-check methods.
        """
        self.clawdbot_tasks.search_for_sales_representative(search_term)
        # NO return - test asserts via POM

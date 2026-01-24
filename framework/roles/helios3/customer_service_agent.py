"""
CustomerServiceAgent - Role for orchestrating business workflows.

Roles represent user personas (e.g., Admin, Customer, Guest).
This role orchestrates complete business workflows using Task modules.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.helios3.helios3_tasks import Helios3Tasks


class CustomerServiceAgent:
    """
    CustomerServiceAgent - orchestrates complete business workflows.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - Workflow methods call MULTIPLE tasks
    - NO return values
    - NO locators
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface):
        """
        Initialize and compose Task modules.

        Args:
            web_interface: WebInterface instance
        """
        self.web = web_interface
        self.helios3_tasks = Helios3Tasks(web_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def submit_form(self, text: str) -> None:
        """
        Execute submit form workflow.

        NO return value - test asserts via POM state-check methods.
        """
        self.helios3_tasks.submit_form(text)
        # NO return - test asserts via POM

    @autologger.automation_logger("Role")
    def perform_new_inquiry_btn(self) -> None:
        """
        Execute new inquiry button workflow.

        NO return value - test asserts via POM state-check methods.
        """
        self.helios3_tasks.do_new_inquiry_btn()
        # NO return - test asserts via POM

    @autologger.automation_logger("Role")
    def perform_filter_btn(self) -> None:
        """
        Execute filter button workflow.

        NO return value - test asserts via POM state-check methods.
        """
        self.helios3_tasks.do_filter_btn()
        # NO return - test asserts via POM

"""
CustomerServiceAgent - Role for orchestrating business workflows.

Roles represent user personas (e.g., Admin, Customer, Guest).
This role orchestrates complete business workflows using Task modules.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.helios6.inquiry_tasks import InquiryTasks


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

        # Compose tasks - they get URL from self.web.config
        self.inquiry_tasks = InquiryTasks(web_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def click_new_inquiry_button(self) -> None:
        """
        Execute click new inquiry button workflow.

        NO return value - test asserts via POM state-check methods.
        """
        self.inquiry_tasks.click_new_inquiry_button()
        # NO return - test asserts via POM

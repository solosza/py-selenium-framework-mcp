"""
CustomerServiceAgent - Role for orchestrating business workflows.

Roles represent user personas (e.g., Admin, Customer, Guest).
This role orchestrates complete business workflows using Task modules.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.helios2.helios2_tasks import Helios2Tasks


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
        self.helios2_tasks = Helios2Tasks(web_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def create_sales_inquiry(self, customer_firstname: str, customer_lastname: str, customer_email: str, customer_title: str, assigned_user: str, inquiry_type: str, inquiry_source: str, inquiry_status: str) -> None:
        """
        Execute create sales inquiry workflow.

        NO return value - test asserts via POM state-check methods.
        """
        self.helios2_tasks.create_sales_inquiry(customer_firstname, customer_lastname, customer_email, customer_title, assigned_user, inquiry_type, inquiry_source, inquiry_status)
        # NO return - test asserts via POM

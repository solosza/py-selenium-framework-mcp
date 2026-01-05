"""
Sales Representative Role for Helios Digital Retail.

Represents a sales rep who can create and manage inquiries.
"""
from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.inquiries.inquiries_tasks import InquiriesTasks
from resources.utilities import autologger


class SalesRepresentative:
    """Role class for sales representative workflows."""

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any]):
        """
        Initialize SalesRepresentative with WebInterface and credentials.

        Args:
            web_interface: WebInterface instance for browser interactions
            user_data: Dict with email, password
        """
        self.web = web_interface
        self.user_data = user_data
        self.email = user_data.get('email')
        self.password = user_data.get('password')

        # Compose task modules
        self.inquiries_tasks = InquiriesTasks(web_interface)

    @autologger.automation_logger("Role")
    def create_inquiry(self, customer_data: dict, inquiry_data: dict) -> None:
        """
        Complete workflow: Navigate to inquiries and create new inquiry.

        Args:
            customer_data: Dict with first_name, last_name, contact_type, contact_id
            inquiry_data: Dict with type, source, status
        """
        self.inquiries_tasks.navigate_to_inquiries()
        self.inquiries_tasks.create_inquiry(customer_data, inquiry_data)
        # NO return - test asserts via POM state-check methods

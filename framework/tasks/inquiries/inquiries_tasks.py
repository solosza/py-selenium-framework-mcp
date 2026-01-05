"""
Task module for Inquiry operations.

Orchestrates InquiryPage methods for creating and managing inquiries.
"""
from interfaces.web_interface import WebInterface
from pages.inquiries.inquiry_page import InquiryPage
from resources.utilities import autologger


class InquiriesTasks:
    """Task class for inquiry-related operations."""

    def __init__(self, web: WebInterface):
        """
        Initialize InquiriesTasks with WebInterface.

        Args:
            web: WebInterface instance for browser interactions
        """
        self.web = web
        self.inquiry_page = InquiryPage(web)

    @autologger.automation_logger("Task")
    def navigate_to_inquiries(self) -> None:
        """Navigate to the Inquiries page."""
        self.inquiry_page.navigate()

    @autologger.automation_logger("Task")
    def create_inquiry(self, customer_data: dict, inquiry_data: dict) -> None:
        """
        Create a new inquiry with customer information.

        Navigates through the multi-step wizard:
        1. Search - Enter customer name
        2. Customer - Enter contact details
        3. Contacts - Skip
        4. Address - Skip
        5. Inquiry - Select type, source, status

        Args:
            customer_data: Dict with first_name, last_name, contact_type, contact_id
            inquiry_data: Dict with type, source, status
        """
        # Click + New Inquiry to start wizard
        self.inquiry_page.click_new_inquiry()

        # Step 1: Search - Enter customer name AND contact details (all on same page)
        (self.inquiry_page
            .enter_customer_firstname(customer_data["first_name"])
            .enter_customer_lastname(customer_data["last_name"])
            .select_contact_type(customer_data.get("contact_type", "Email"))
            .enter_contact_identifier(customer_data["contact_id"])
            .click_search_next())

        # Step 2: Customer - Pre-filled, just click Next
        self.inquiry_page.click_customer_next()

        # Step 3: Contacts - Pre-filled, just click Next
        self.inquiry_page.click_contacts_next()

        # Step 4: Address - Optional, just click Next
        self.inquiry_page.click_address_next()

        # Step 5: Inquiry - Fill inquiry details and complete
        (self.inquiry_page
            .select_inquiry_type(inquiry_data["type"])
            .select_inquiry_source(inquiry_data["source"])
            .select_inquiry_status(inquiry_data["status"])
            .click_complete())

        # NO return - test asserts via inquiry_page.is_inquiry_created()

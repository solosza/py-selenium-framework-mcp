"""
Create sales inquiry for customer with dynamically generated name and email, set inquiry type to Sales, source to Phone, status to Open

This module provides high-level task methods that orchestrate page objects
to accomplish business workflows.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from pages.helios1.inquiries_page import InquiriesPage


class Helios2Tasks:
    """
    Task module for Helios2 operations.

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
        self.inquiries_page = InquiriesPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def create_sales_inquiry(self, customer_firstname: str, customer_lastname: str, 
                             customer_email: str, customer_title: str, 
                             assigned_user: str, inquiry_type: str, 
                             inquiry_source: str, inquiry_status: str) -> None:
        """
        Create sales inquiry with dynamic customer data through 5-step wizard.

        Args:
            customer_firstname: Customer first name
            customer_lastname: Customer last name
            customer_email: Customer email contact
            customer_title: Customer title (Mr, Mrs, Ms)
            assigned_user: Assigned user name
            inquiry_type: Inquiry type (Sales, Feedback, etc.)
            inquiry_source: Inquiry source (Email, Phone, etc.)
            inquiry_status: Inquiry status (Open, Action Required, etc.)

        NO return value - test asserts via POM state-check methods.
        """
        # Step 1: Click New Inquiry button
        self.inquiries_page.click_new_inquiry_button()
        
        # Step 2: Search for customer (wizard step 1)
        (self.inquiries_page
            .enter_search_firstname(customer_firstname)
            .enter_search_lastname(customer_lastname)
            .select_search_contact_type("Email")
            .enter_search_contact_identifier(customer_email)
            .click_search_next_button())
        
        # Step 3: Fill customer form (wizard step 2)
        (self.inquiries_page
            .select_customer_title(customer_title)
            .select_customer_assigned_user(assigned_user)
            .click_customer_submit_button())
        
        # Step 4: Skip contacts form (wizard step 3 - email auto-added)
        self.inquiries_page.click_contact_submit_button()
        
        # Step 5: Skip address form (wizard step 4)
        self.inquiries_page.click_address_submit_button()
        
        # Step 6: Complete inquiry form (wizard step 5)
        (self.inquiries_page
            .select_inquiry_type(inquiry_type)
            .select_inquiry_source(inquiry_source)
            .select_inquiry_status(inquiry_status)
            .click_inquiry_complete_button())
        
        # NO return - test asserts via POM

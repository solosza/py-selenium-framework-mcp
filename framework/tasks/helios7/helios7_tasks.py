"""
Search for customer and submit new inquiry with customer details, contact information, and inquiry specifics

This module provides high-level task methods that orchestrate page objects
to accomplish business workflows.
"""

from interfaces.web_interface import WebInterface
from pages.helios7.customer_search_page import CustomerSearchPage
from pages.helios7.customer_details_page import CustomerDetailsPage
from pages.helios7.contacts_page import ContactsPage
from pages.helios7.address_page import AddressPage
from pages.helios7.inquiry_form_page import InquiryFormPage
from resources.utilities import autologger


class Helios7Tasks:
    """
    Task module for Helios7 operations.

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
        self.customer_search_page = CustomerSearchPage(web)
        self.customer_details_page = CustomerDetailsPage(web)
        self.contacts_page = ContactsPage(web)
        self.address_page = AddressPage(web)
        self.inquiry_form_page = InquiryFormPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def search_and_create_customer(self, first_name: str, last_name: str, contact_type: str, contact_identifier: str) -> None:
        """
        Search for customer and create if not exists.

        Args:
            first_name: Customer first name
            last_name: Customer last name
            contact_type: Contact type (Email, Phone, etc.)
            contact_identifier: contact_identifier (email, phone number, etc.)

        NO return value - test asserts via POM.
        """
        # Navigate and open wizard
        (self.customer_search_page
            .navigate()
            .click_new_inquiry()
            .wait_for_form_visible()
            .enter_first_name(first_name)
            .enter_last_name(last_name)
            .select_contact_type(contact_type)
            .enter_contact_identifier(contact_identifier)
            .click_next())
        # NO return

    @autologger.automation_logger("Task")
    def submit_inquiry(self, inquiry_type: str, source: str, status: str) -> None:
        """
        Submit new inquiry with specified details.

        Args:
            inquiry_type: Type of inquiry (Feedback, Information, Service, etc.)
            source: Inquiry source (Dealership, Email, Phone, etc.)
            status: Inquiry status (New, Progress, Action Required, etc.)

        NO return value - test asserts via POM.
        """
        # Navigate through intermediate wizard steps (Customer Details, Contacts, Address)
        # Click Next buttons to reach Inquiry form
        self.customer_details_page.click_next()
        self.contacts_page.click_next()
        self.address_page.click_next()

        (self.inquiry_form_page
            .wait_for_form_visible()
            .select_type(inquiry_type)
            .select_source(source)
            .select_status(status)
            .click_complete())
        # NO return

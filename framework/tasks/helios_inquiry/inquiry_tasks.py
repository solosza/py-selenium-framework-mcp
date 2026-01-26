"""
InquiryTasks - Task module for helios-inquiry workflow

Orchestrates page objects for inquiry creation workflow.
"""

from interfaces.web_interface import WebInterface
from pages.helios_inquiry.customer_search_page import CustomerSearchPage
from pages.helios_inquiry.customer_form_page import CustomerFormPage
from pages.helios_inquiry.contacts_form_page import ContactsFormPage
from pages.helios_inquiry.address_form_page import AddressFormPage
from pages.helios_inquiry.inquiry_form_page import InquiryFormPage
from resources.utilities import autologger


class InquiryTasks:
    """
    Task module for Helios Inquiry operations.

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
        self.customer_form_page = CustomerFormPage(web)
        self.contacts_form_page = ContactsFormPage(web)
        self.address_form_page = AddressFormPage(web)
        self.inquiry_form_page = InquiryFormPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def search_customer(self, first_name: str, last_name: str, contact_type: str, contact_identifier: str) -> None:
        """
        Search for customer and proceed to customer form.

        Args:
            first_name: Customer first name
            last_name: Customer last name
            contact_type: Contact type (Email, Phone, etc.)
            contact_identifier: Contact identifier (email, phone number, etc.)

        NO return value - test asserts via POM.
        """
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
    def complete_customer_form(self) -> None:
        """
        Complete customer form step (usually pre-filled).

        NO return value - test asserts via POM.
        """
        (self.customer_form_page
            .wait_for_form_visible()
            .click_next())
        # NO return

    @autologger.automation_logger("Task")
    def complete_contacts_form(self) -> None:
        """
        Complete contacts form step.

        NO return value - test asserts via POM.
        """
        (self.contacts_form_page
            .wait_for_form_visible()
            .click_next())
        # NO return

    @autologger.automation_logger("Task")
    def complete_address_form(self) -> None:
        """
        Complete address form step (optional, can skip).

        NO return value - test asserts via POM.
        """
        (self.address_form_page
            .wait_for_form_visible()
            .click_next())
        # NO return

    @autologger.automation_logger("Task")
    def submit_inquiry(self, inquiry_type: str, source: str, status: str) -> None:
        """
        Submit new inquiry with specified details.

        Args:
            inquiry_type: Type of inquiry (Feedback, Information, Service, etc.)
            source: Inquiry source (Dealership, Email, Phone, etc.)
            status: Inquiry status (New, In Progress, Action Required, etc.)

        NO return value - test asserts via POM.
        """
        (self.inquiry_form_page
            .wait_for_form_visible()
            .select_type(inquiry_type)
            .select_source(source)
            .select_status(status)
            .click_complete())
        # NO return

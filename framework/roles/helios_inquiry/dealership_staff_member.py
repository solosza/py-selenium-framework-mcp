"""
DealershipStaffMember - Role for orchestrating inquiry workflows.

Roles represent user personas. This role orchestrates complete
business workflows for dealership staff using Task modules.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.helios_inquiry.inquiry_tasks import InquiryTasks


class DealershipStaffMember:
    """
    DealershipStaffMember - orchestrates complete business workflows.

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
        self.inquiry_tasks = InquiryTasks(web_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def create_inquiry_for_new_customer(
        self,
        first_name: str,
        last_name: str,
        contact_type: str,
        contact_identifier: str,
        inquiry_type: str,
        source: str,
        status: str
    ) -> None:
        """
        Complete workflow: Search/create customer and submit inquiry.

        This workflow method orchestrates MULTIPLE task operations:
        1. Search customer (Step 1)
        2. Complete customer form (Step 2)
        3. Complete contacts form (Step 3)
        4. Complete address form (Step 4)
        5. Submit inquiry (Step 5)

        Args:
            first_name: Customer first name
            last_name: Customer last name
            contact_type: Contact type (Email, Phone, etc.)
            contact_identifier: Contact identifier
            inquiry_type: Type of inquiry
            source: Inquiry source
            status: Inquiry status

        NO return value - test asserts via POM state-check methods.
        """
        # Step 1: Search customer
        self.inquiry_tasks.search_customer(first_name, last_name, contact_type, contact_identifier)

        # Steps 2-4: Navigate through wizard
        self.inquiry_tasks.complete_customer_form()
        self.inquiry_tasks.complete_contacts_form()
        self.inquiry_tasks.complete_address_form()

        # Step 5: Submit inquiry
        self.inquiry_tasks.submit_inquiry(inquiry_type, source, status)
        # NO return - test asserts via POM

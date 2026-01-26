"""
TestCreateInquiry - Test suite for helios-inquiry workflow.

Test suite for creating a new customer inquiry through the dealership portal.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from faker import Faker
from resources.utilities import autologger
from roles.helios_inquiry.dealership_staff_member import DealershipStaffMember
from pages.helios_inquiry.inquiry_form_page import InquiryFormPage


class TestCreateInquiry:
    """
    TestCreateInquiry - Test suite for inquiry creation workflow.

    - @autologger("Test") decorator
    - Call ONE Role workflow method
    - Assert via Page Object state-check methods
    - NO orchestration (Role handles workflow)
    """

    @pytest.fixture(autouse=True)
    def setup(self, web_interface):
        """Setup test fixtures."""
        self.web = web_interface
        self.inquiry_form_page = InquiryFormPage(self.web)

    # ==================== TEST METHODS ====================

    @pytest.mark.helios_inquiry
    @autologger.automation_logger("Test")
    def test_create_inquiry_for_new_customer(self):
        """
        Test complete workflow: create customer and submit inquiry.

        AAA Pattern:
        1. Arrange - Create role (no credentials needed) + generate unique test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange - Generate unique customer data using Faker
        fake = Faker()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()

        user = DealershipStaffMember(self.web)

        # Act - ONE workflow call that orchestrates the entire flow
        user.create_inquiry_for_new_customer(
            first_name=first_name,
            last_name=last_name,
            contact_type="Email",
            contact_identifier=email,
            inquiry_type="Service",
            source="Dealership",
            status="New"
        )

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.inquiry_form_page.is_inquiry_created(), "Inquiry should be created successfully"

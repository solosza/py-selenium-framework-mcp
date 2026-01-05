"""
Test suite for Inquiry creation workflow.

Tests sales representative creating new inquiries in Helios Digital Retail.
"""
import pytest
from faker import Faker
from roles.sales_representative import SalesRepresentative
from pages.inquiries.inquiry_page import InquiryPage
from resources.utilities import autologger

fake = Faker()


class TestCreateNewInquiry:
    """Test class for inquiry creation scenarios."""

    @pytest.mark.inquiries
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_sales_rep_can_create_new_inquiry(self, web_interface, config):
        """
        Test that a sales representative can create a new inquiry.

        Given a sales representative is on the Inquiries page
        When they create a new inquiry with unique customer information:
            - Customer: [Faker-generated unique name]
            - Contact: Email - [Faker-generated unique email]
            - Inquiry Type: New Vehicle
            - Source: Website
            - Status: New
        Then the inquiry should be created successfully
        And the inquiry should appear in the inquiry list

        Note: Uses unique data to trigger 5-step "new customer" wizard flow
        (avoids matching existing customers which would trigger 2-step flow).
        """
        # ARRANGE
        user_data = {
            "email": "sales@helios.com",
            "password": "SalesPass123"
        }
        user = SalesRepresentative(web_interface, user_data)

        # Use unique data to trigger 5-step "new customer" wizard flow
        customer_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "contact_type": "Email",
            "contact_id": fake.email()
        }

        inquiry_data = {
            "type": "New Vehicle",
            "source": "Website",
            "status": "New"
        }

        inquiry_page = InquiryPage(web_interface)

        # ACT
        user.create_inquiry(customer_data, inquiry_data)

        # ASSERT
        assert inquiry_page.is_inquiry_created(), "Inquiry should be created successfully"

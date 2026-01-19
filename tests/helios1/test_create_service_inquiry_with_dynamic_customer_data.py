"""
TestCreateServiceInquiryWithDynamicCustomerData - Test suite for Helios1 workflows.

Test suite for Helios1 workflows.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from faker import Faker
from resources.utilities import autologger
from roles.helios1.sales_representative import SalesRepresentative
from pages.helios1.inquiries_page import InquiriesPage


class TestCreateServiceInquiryWithDynamicCustomerData:
    """
    TestCreateServiceInquiryWithDynamicCustomerData - Test suite for Helios1.

    - @autologger("Test") decorator
    - Load data from fixtures
    - Call ONE workflow method per Role
    - Assert via Page Object state-check methods
    - NO orchestration (don't call multiple Role methods)
    """

    @pytest.fixture(autouse=True)
    def setup(self, web_interface, config):
        """Setup test fixtures."""
        self.web = web_interface
        self.config = config
        self.inquiries_page = InquiriesPage(self.web)
        self.fake = Faker()

    # ==================== TEST METHODS ====================

    @pytest.mark.helios1
    @autologger.automation_logger("Test")
    def test_create_service_inquiry_with_dynamic_customer_data(self):
        """
        Test create service inquiry with dynamic customer data.

        AAA Pattern:
        1. Arrange - Create role with dynamic test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange - Generate dynamic customer data
        customer_firstname = self.fake.first_name()
        customer_lastname = self.fake.last_name()
        customer_email = self.fake.email()
        
        user = SalesRepresentative(self.web)
        
        # Navigate to inquiries page
        self.inquiries_page.navigate()

        # Act - ONE workflow call, NO return value
        user.create_service_inquiry(
            customer_firstname=customer_firstname,
            customer_lastname=customer_lastname,
            customer_email=customer_email,
            customer_title="Mr",
            assigned_user="Test User",
            inquiry_type="Service",
            inquiry_source="Email",
            inquiry_status="New"
        )

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.inquiries_page.is_inquiry_created(), "Inquiry should be created successfully"
        assert self.inquiries_page.is_inquiry_in_list(), "Inquiry should appear in the inquiries list"

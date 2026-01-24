"""
Test: Create Sales Inquiry with Dynamic Customer Data

Test Layer - Uses Role to orchestrate workflow and POM to assert state.
This is Layer 4 of the 4-layer architecture (Page → Task → Role → Test).
"""

import pytest
from interfaces.web_interface import WebInterface
from roles.helios3.customer_service_agent import CustomerServiceAgent
from pages.helios3.inquiries_page import InquiriesPage
from resources.utilities import autologger


class TestCreateSalesInquiryWithDynamicCustomerData:
    """
    Test create sales inquiry with dynamic customer data.

    - @autologger("Test") on test methods
    - Calls ONE role workflow method
    - Asserts via POM state-check methods
    - AAA pattern (Arrange, Act, Assert)
    """

    @pytest.fixture(autouse=True)
    def setup(self, web_interface):
        """Setup test fixtures."""
        self.web = web_interface
        self.base_url = self.web.config['url']
        self.inquiries_page = InquiriesPage(web_interface)

    @pytest.mark.helios3
    @autologger.automation_logger("Test")
    def test_submit_form(self):
        """
        Test that customer service agent can submit form.

        Scenario: Submit Form
        Given: Customer service agent is on Inquiries page
        When: Agent enters search text and submits
        Then: Inquiry is visible and has inquiry type
        """
        # Arrange
        user_data = {"email": "testuser@example.com", "password": "TestPass123"}
        customer_service_agent = CustomerServiceAgent(self.web, user_data, self.base_url)

        # Act - ONE call to workflow method (no return value)
        customer_service_agent.submit_form("text_value")

        # Assert - Via POM state-check methods
        assert self.inquiries_page.is_inquiry_visible(), "Is Inquiry Visible"
        assert self.inquiries_page.has_inquiry_type(), "Has Inquiry Type"

    @pytest.mark.helios3
    @autologger.automation_logger("Test")
    def test_new_inquiry_btn(self):
        """
        Test that customer service agent can click new inquiry button.

        Scenario: New Inquiry Button
        Given: Customer service agent is on Inquiries page
        When: Agent clicks new inquiry button
        Then: Inquiry is visible
        """
        # Arrange
        user_data = {"email": "testuser@example.com", "password": "TestPass123"}
        customer_service_agent = CustomerServiceAgent(self.web, user_data, self.base_url)

        # Act - ONE call to workflow method (no return value)
        customer_service_agent.perform_new_inquiry_btn()

        # Assert - Via POM state-check methods
        assert self.inquiries_page.is_inquiry_visible(), "Is Inquiry Visible"

    @pytest.mark.helios3
    @autologger.automation_logger("Test")
    def test_filter_btn(self):
        """
        Test that customer service agent can click filter button.

        Scenario: Filter Button
        Given: Customer service agent is on Inquiries page
        When: Agent clicks filter button
        Then: Inquiry type is visible
        """
        # Arrange
        user_data = {"email": "testuser@example.com", "password": "TestPass123"}
        customer_service_agent = CustomerServiceAgent(self.web, user_data, self.base_url)

        # Act - ONE call to workflow method (no return value)
        customer_service_agent.perform_filter_btn()

        # Assert - Via POM state-check methods
        assert self.inquiries_page.has_inquiry_type(), "Has Inquiry Type"

"""
Test for CustomerServiceAgent clicking new inquiry button.

Tests the workflow: Customer Service Agent performs new inquiry btn action.
"""

import pytest
from interfaces.web_interface import WebInterface
from roles.workflow5.customer_service_agent import CustomerServiceAgent
from pages.workflow5.inquiries_page import InquiriesPage
from resources.utilities import autologger


class TestCustomerServiceAgentClicksNewInquiryButton:
    """Test CustomerServiceAgent clicks new inquiry button workflow."""

    @pytest.fixture(autouse=True)
    def setup(self, web_interface, config):
        """Setup test fixtures."""
        self.web = web_interface
        self.config = config
        self.base_url = config.get("url", config.get("base_url", ""))
        self.inquiries_page = InquiriesPage(self.web)

    @pytest.mark.workflow5
    @autologger.automation_logger("Test")
    def test_perform_new_inquiry_btn(self):
        """
        Test that Customer Service Agent can click new inquiry button.

        Given: Customer Service Agent is ready
        When: Customer Service Agent performs new inquiry btn action
        Then: New inquiry btn is clickable
        """
        # Arrange
        customer_service_agent = CustomerServiceAgent(self.web)

        # Act
        customer_service_agent.perform_new_inquiry_btn()

        # Assert
        assert self.inquiries_page.is_new_inquiry_btn_clickable(), "New inquiry btn should be clickable"

"""
TestClickNewInquiryButton - Test suite for Helios6 workflows.

Test suite for Helios6 workflows.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.helios6.customer_service_agent import CustomerServiceAgent
from pages.helios6.inquiries_page import InquiriesPage


class TestClickNewInquiryButton:
    """
    TestClickNewInquiryButton - Test suite for Helios6.

    - @autologger("Test") decorator
    - Load data from fixtures
    - Call ONE workflow method per Role
    - Assert via Page Object state-check methods
    - NO orchestration (don't call multiple Role methods)
    """

    @pytest.fixture(autouse=True)
    def setup(self, web_interface):
        """Setup test fixtures."""
        self.web = web_interface
        self.inquiries_page = InquiriesPage(self.web)

    # ==================== TEST METHODS ====================

    @pytest.mark.helios6
    @autologger.automation_logger("Test")
    def test_click_new_inquiry_button(self):
        """
        Test click new inquiry button workflow.

        AAA Pattern:
        1. Arrange - Create role (no credentials needed - already logged in)
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange - Role does not require credentials (credential_strategy='none')
        customer_service_agent = CustomerServiceAgent(self.web)

        # Act - ONE workflow call, NO return value
        customer_service_agent.click_new_inquiry_button()

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.inquiries_page.is_inquiry_form_visible(), "Inquiry creation form should be visible after clicking New Inquiry button"

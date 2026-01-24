"""
TestIClickTheNewInquiryButton - Test suite for Helios5 workflows.

Test suite for Helios5 workflows.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.helios5.customer_service_agent import CustomerServiceAgent
from pages.helios5.inquiries_page import InquiriesPage


class TestIClickTheNewInquiryButton:
    """
    TestIClickTheNewInquiryButton - Test suite for Helios5.

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
        self.base_url = config.get("url", config.get("base_url", ""))
        self.inquiries_page = InquiriesPage(self.web)

    # ==================== TEST METHODS ====================

    @pytest.mark.helios5
    @autologger.automation_logger("Test")
    def test_perform_new_inquiry_btn(self):
        """
        Test perform new inquiry btn workflow.

        AAA Pattern:
        1. Arrange - Create role with test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange
        customer_service_agent = CustomerServiceAgent(self.web)

        # Act - ONE workflow call, NO return value
        customer_service_agent.perform_new_inquiry_btn()

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.inquiries_page.is_new_inquiry_btn_clickable(), "New Inquiry button should be clickable"

"""
TestSearchSalesRepresentative - Test suite for Clawdbot workflows.

Test suite for searching for a sales representative in the Helios Portal.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.clawdbot.customer import Customer
from pages.clawdbot.sales_leads_page import SalesLeadsPage


class TestSearchSalesRepresentative:
    """
    TestSearchSalesRepresentative - Test suite for search functionality.

    - @autologger("Test") decorator
    - Call ONE Role workflow method
    - Assert via Page Object state-check methods
    - NO orchestration (Role handles workflow)
    """

    @pytest.fixture(autouse=True)
    def setup(self, web_interface):
        """Setup test fixtures."""
        self.web = web_interface
        self.sales_leads_page = SalesLeadsPage(self.web)

    # ==================== TEST METHODS ====================

    @pytest.mark.clawdbot
    @autologger.automation_logger("Test")
    def test_customer_can_search_for_sales_representative(self):
        """
        Test that a customer can search for a sales representative.

        AAA Pattern:
        1. Arrange - Create role (no credentials needed)
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange
        customer = Customer(self.web)

        # Act - ONE workflow call
        customer.search_for_sales_representative("sales representative")

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.sales_leads_page.has_search_results(), "Search results table should be displayed"
        assert self.sales_leads_page.is_search_results_displayed(), "Results container should be visible"

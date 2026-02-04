"""
Test Customer Transfer Funds - E2E test for ParaBank transfer workflow.

Tests that a customer can log in and transfer funds between accounts.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.testP1.customer import Customer
from pages.testP1.transfer_funds_page import TransferFundsPage
from pages.testP1.accounts_overview_page import AccountsOverviewPage


class TestCustomerTransferFunds:
    """
    TestCustomerTransferFunds - E2E test for login and transfer.

    - @autologger("Test") decorator
    - Call ONE Role workflow method
    - Assert via Page Object state-check methods
    - NO orchestration (Role handles workflow)
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, test_users):
        """Setup test fixtures."""
        self.browser = browser
        self.test_users = test_users
        self.transfer_funds_page = TransferFundsPage(self.browser)
        self.accounts_overview_page = AccountsOverviewPage(self.browser)

    # ==================== TEST METHODS ====================

    @pytest.mark.testP1
    @pytest.mark.transfer
    @autologger.automation_logger("Test")
    def test_customer_can_login_and_transfer_funds(self):
        """
        Test that a customer can log in and transfer funds.

        BDD:
        Given I am on the ParaBank login page
        When I enter username 'john' and password 'demo' and click login
        Then I should see the accounts overview page

        Given I am logged in and on the accounts overview page
        When I click Transfer Funds, select accounts, enter amount, click Transfer
        Then I should see the transfer complete confirmation

        AAA Pattern:
        1. Arrange - Create customer role with credentials
        2. Act - Call ONE workflow method (login_and_transfer_funds)
        3. Assert - Use POM state-check methods
        """
        # Arrange
        user_data = self.test_users["john_demo"]
        customer = Customer(
            self.browser,
            username=user_data["username"],
            password=user_data["password"]
        )

        # Act - ONE workflow call that orchestrates login + transfer
        customer.login_and_transfer_funds(
            amount="100",
            from_account="13344",
            to_account="13344"
        )

        # Assert - Via Page Object state-check methods
        assert self.transfer_funds_page.is_transfer_complete(), "Transfer should be complete"
        assert self.transfer_funds_page.has_transfer_confirmation(), "Should show transfer confirmation"

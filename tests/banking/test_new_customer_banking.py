"""
TestNewCustomerBanking - Test suite for Banking workflows.

Tests new customer registration and banking operations on ParaBank.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
import uuid
from resources.utilities import autologger
from roles.new_customer import NewCustomer
from pages.banking.registration_page import RegistrationPage
from pages.banking.open_new_account_page import OpenNewAccountPage
from pages.banking.transfer_funds_page import TransferFundsPage
from pages.banking.accounts_overview_page import AccountsOverviewPage


class TestNewCustomerBanking:
    """
    Test suite for new customer banking workflows.

    - @autologger("Test") decorator
    - Load data from fixtures
    - Call ONE workflow method per test
    - Assert via Page Object state-check methods
    """

    @pytest.fixture(autouse=True)
    def setup(self, web_interface):
        """Setup test fixtures."""
        self.web = web_interface
        self.registration_page = RegistrationPage(self.web)
        self.open_new_account_page = OpenNewAccountPage(self.web)
        self.transfer_funds_page = TransferFundsPage(self.web)
        self.accounts_overview_page = AccountsOverviewPage(self.web)

    @pytest.fixture
    def new_user_data(self):
        """Generate unique user data for registration."""
        unique_id = str(uuid.uuid4())[:8]
        return {
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test Street",
            "city": "Testville",
            "state": "TX",
            "zip_code": "12345",
            "phone": "555-1234",
            "ssn": "123-45-6789",
            "username": f"testuser_{unique_id}",
            "password": "Test1234!"
        }

    # ==================== TEST METHODS ====================

    @pytest.mark.banking
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_new_customer_complete_banking_journey(self, new_user_data):
        """
        Test that a new customer can complete the full banking journey.

        Scenario: Complete banking journey
        Given a new customer
        When they register, open savings, transfer funds, and view activity
        Then they should see the transfer in transaction history
        """
        # Arrange
        customer = NewCustomer(self.web, new_user_data)

        # Act - ONE workflow method call (Role orchestrates the full journey)
        customer.register_transfer_and_verify("100")

        # Assert - Via POM state-check methods
        assert self.accounts_overview_page.has_transaction_in_history(), "Transfer should appear in transaction history"
        assert self.accounts_overview_page.has_transaction_amount(), "Transaction amount should be visible"

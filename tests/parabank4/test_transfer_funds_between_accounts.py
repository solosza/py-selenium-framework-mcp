"""
TestTransferFundsBetweenAccounts - Test suite for Parabank4 workflows.

Test suite for Parabank4 workflows.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.registered_para_bank_user import RegisteredParaBankUser
from pages.parabank4.transfer_funds_page import TransferFundsPage


class TestTransferFundsBetweenAccounts:
    """
    TestTransferFundsBetweenAccounts - Test suite for Parabank4.

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
        self.transfer_funds_page = TransferFundsPage(self.web)

    # ==================== TEST METHODS ====================

    @pytest.mark.parabank4
    @autologger.automation_logger("Test")
    def test_transfer_funds(self, test_users):
        """
        Test that a registered ParaBank user can transfer funds between checking and savings accounts.

        AAA Pattern:
        1. Arrange - Create role with test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange
        user_data = test_users.get("registered_user", {"email": "john", "password": "demo"})
        user = RegisteredParaBankUser(self.web, user_data, self.base_url)

        # Act - ONE workflow call, NO return value
        user.transfer_funds("100", "12456", "12567")

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.transfer_funds_page.is_transfer_confirmed(), "Transfer confirmation message should be visible"
        assert self.transfer_funds_page.is_transfer_successful(), "Transfer should be marked as successful"
        assert self.transfer_funds_page.are_balances_updated(), "Account balances should be updated"
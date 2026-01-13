"""
Verify existing customer can login, open savings account, transfer funds, and view transaction history

Test suite for Parabank workflows.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.parabank.existing_customer import ExistingCustomer
from pages.parabank.account_activity_page import AccountActivityPage


class TestExistingCustomerCompletesBankingWorkflow:
    """
    TestExistingCustomerCompletesBankingWorkflow - Test suite for Parabank.

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
        self.account_activity_page = AccountActivityPage(self.web)

    # ==================== TEST METHODS ====================

    @pytest.mark.parabank
    @autologger.automation_logger("Test")
    def test_complete_banking_workflow(self):
        """
        Test complete banking workflow workflow.

        AAA Pattern:
        1. Arrange - Create role with test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange - Use static credentials and hardcoded test data (MVP)
        user_data = {"username": "john", "password": "demo"}
        customer = ExistingCustomer(self.web, user_data, self.base_url)

        # Hardcoded test data for MVP (can refactor to fixture later)
        account_type = "SAVINGS"  # From user story: "open a new savings account"
        from_account_id = "12345"  # Checking account ID
        transfer_amount = "100"  # From user story: "transfer $100"
        to_account_id = "54321"  # Savings account ID

        # Act - ONE workflow call with actual parameter values (DD-17)
        customer.complete_banking_workflow(
            account_type=account_type,
            from_account_id=from_account_id,
            transfer_amount=transfer_amount,
            to_account_id=to_account_id
        )

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.account_activity_page.is_transaction_visible(), "Transaction should be visible in account history"
        assert self.account_activity_page.has_recent_transaction(), "Recent transaction should exist"

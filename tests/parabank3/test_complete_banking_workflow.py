"""
TestCompleteBankingWorkflow - E2E test for complete banking workflow.

Tests the complete workflow: open new savings account, transfer $100, verify transaction.
"""

import pytest
from resources.utilities import autologger
from roles.parabank3.existing_customer import ExistingCustomer
from pages.parabank3.open_new_account_page import OpenNewAccountPage
from pages.parabank3.transfer_funds_page import TransferFundsPage
from pages.parabank3.account_activity_page import AccountActivityPage


class TestCompleteBankingWorkflow:
    """
    E2E test suite for complete banking workflow.

    User Story: As an existing customer, I want to login, open a new savings account,
    transfer $100 from checking to savings, and verify the transaction.
    """

    @pytest.mark.parabank3
    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_complete_banking_workflow(self, web_interface, config):
        """
        Test complete banking workflow: open account, transfer funds, verify transaction.

        AAA Pattern:
        - Arrange: Create role and page objects with test credentials
        - Act: Execute complete workflow via role methods
        - Assert: Verify state via POM state-check methods
        """
        # ARRANGE
        user_data = {"username": "john", "password": "demo"}
        base_url = config.get("url", config.get("base_url", ""))
        
        customer = ExistingCustomer(web_interface, user_data, base_url)
        open_account_page = OpenNewAccountPage(web_interface)
        transfer_page = TransferFundsPage(web_interface)
        activity_page = AccountActivityPage(web_interface)

        # ACT
        customer.open_new_account("SAVINGS", "13344")
        new_savings_account_id = open_account_page.get_new_account_id()
        customer.transfer_funds("100", "13344", new_savings_account_id)
        customer.navigate_to_account_activity()

        # ASSERT
        assert open_account_page.is_account_opened(), "New savings account should be opened"
        assert transfer_page.is_transfer_complete(), "$100 transfer should be complete"
        assert activity_page.is_transaction_visible(), "Transaction should be visible in history"
        assert activity_page.has_correct_amount("$100.00"), "Transaction should show $100"

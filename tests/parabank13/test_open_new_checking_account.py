"""
TestOpenNewCheckingAccount - Test suite for Parabank13 workflows.

Test suite for Parabank13 workflows.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.parabank13.registered_user import RegisteredUser
from pages.parabank13.open_account_page import OpenAccountPage


class TestOpenNewCheckingAccount:
    """
    TestOpenNewCheckingAccount - Test suite for Parabank13.

    - @autologger("Test") decorator
    - Load data from fixtures
    - Call ONE workflow method per Role
    - Assert via Page Object state-check methods
    - NO orchestration (don't call multiple Role methods)
    """

    @pytest.fixture(autouse=True)
    def setup(self, web_interface, test_users):
        """Setup test fixtures."""
        self.web = web_interface
        self.test_users = test_users
        self.open_account_page = OpenAccountPage(self.web)

    # ==================== TEST METHODS ====================

    @pytest.mark.parabank13
    @autologger.automation_logger("Test")
    def test_open_new_checking_account(self):
        """
        Test open new checking account workflow.

        AAA Pattern:
        1. Arrange - Create role with test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange
        user_data = self.test_users["john_demo"]
        user = RegisteredUser(self.web, user_data)

        # Act - ONE workflow call, NO return value (uses default account for transfer)
        user.open_new_checking_account("CHECKING")

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.open_account_page.is_account_opened_successfully(), "Account should be opened successfully"
        assert self.open_account_page.has_success_message(), "Success message should be displayed"
        assert self.open_account_page.get_new_account_number(), "New account number should be displayed"

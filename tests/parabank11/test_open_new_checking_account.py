"""
TestOpenNewCheckingAccount - Test suite for Parabank11 workflows.

Test suite for Parabank11 workflows.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.parabank11.registered_user import Parabank11RegisteredUser
from pages.parabank11.open_account_page import OpenAccountPage


class TestOpenNewCheckingAccount:
    """
    TestOpenNewCheckingAccount - Test suite for Parabank11.

    - @autologger("Test") decorator
    - Load data from fixtures
    - Call ONE workflow method per Role
    - Assert via Page Object state-check methods
    - NO orchestration (don't call multiple Role methods)
    """

    @pytest.fixture(autouse=True)
    def setup(self, web_interface, config, test_users):
        """Setup test fixtures."""
        self.web = web_interface
        self.config = config
        self.base_url = config.get("url", config.get("base_url", ""))
        self.open_account_page = OpenAccountPage(self.web)
        self.test_users = test_users

    # ==================== TEST METHODS ====================

    @pytest.mark.parabank11
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
        user_data = self.test_users.get("john_demo", {"username": "john", "password": "demo"})
        user = Parabank11RegisteredUser(self.web, user_data, self.base_url)

        # Act - ONE workflow call, NO return value
        user.open_new_checking_account("0", "13344")

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.open_account_page.is_account_opened(), "Account should be opened successfully"
        assert self.open_account_page.has_account_number(), "New account number should be displayed"


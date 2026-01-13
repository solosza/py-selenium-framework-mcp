"""
TestLoginAndViewAccountOverview - Test suite for Parabank8 workflows.

Test suite for Parabank8 workflows.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.parabank8.parabank_login_page import ParabankLoginPage


class TestLoginAndViewAccountOverview:
    """
    TestLoginAndViewAccountOverview - Test suite for Parabank8.

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
        self.test_users = test_users
        self.parabank_login_page = ParabankLoginPage(self.web)

    # ==================== TEST METHODS ====================

    @pytest.mark.parabank8
    @autologger.automation_logger("Test")
    def test_login_and_view_account_overview(self):
        """
        Test login and view account overview workflow.

        AAA Pattern:
        1. Arrange - Create role with test data from test_users fixture
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange - Read from test_users fixture (static strategy)
        user_data = self.test_users["parabank8"]["john"]
        user = RegisteredUser(self.web, user_data)

        # Act - ONE workflow call, NO return value
        user.login_and_view_account_overview()

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.parabank_login_page.is_on_account_overview(), "Should be on account overview page"
        assert self.parabank_login_page.is_account_details_visible(), "Account details should be visible"
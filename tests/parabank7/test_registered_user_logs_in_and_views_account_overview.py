"""
TestRegisteredUserLogsInAndViewsAccountOverview - Test suite for Parabank7 workflows.

Test suite for Parabank7 workflows.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.parabank7.registered_user import RegisteredUser
from pages.parabank7.account_overview_page import AccountOverviewPage


class TestRegisteredUserLogsInAndViewsAccountOverview:
    """
    TestRegisteredUserLogsInAndViewsAccountOverview - Test suite for Parabank7.

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
        self.overview_page = AccountOverviewPage(self.web)

    # ==================== TEST METHODS ====================

    @pytest.mark.parabank7
    @autologger.automation_logger("Test")
    def test_login_and_view_account_overview(self):
        """
        Test login and view account overview workflow.

        AAA Pattern:
        1. Arrange - Create role with test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange
        user_data = self.test_users["parabank"]["valid_user"]
        user = RegisteredUser(self.web, user_data)

        # Act - ONE workflow call, NO return value
        user.login_and_view_account_overview()

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.overview_page.is_logged_in(), "User should be logged in"
        assert self.overview_page.is_account_overview_visible(), "Account overview should be visible"

"""
TestLoginAndViewAccountOverview - Test suite for Parabank workflows.

Test suite for Parabank workflows.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.parabank.parabank_index_page import ParabankIndexPage


class TestLoginAndViewAccountOverview:
    """
    TestLoginAndViewAccountOverview - Test suite for Parabank.

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
        self.parabank_index_page = ParabankIndexPage(self.web)

    # ==================== TEST METHODS ====================

    @pytest.mark.parabank
    @autologger.automation_logger("Test")
    def test_login_and_view_overview(self):
        """
        Test login and view overview workflow.

        AAA Pattern:
        1. Arrange - Create role with test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange
        user_data = {"username": "john", "password": "demo"}
        user = RegisteredUser(self.web, user_data)

        # Act - ONE workflow call, NO return value
        user.login_and_view_overview()

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.parabank_index_page.is_logged_in(), "User should be logged in"
        assert self.parabank_index_page.is_account_overview_visible(), "Account overview should be visible"

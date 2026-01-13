"""
TestCompleteAccountSetupAndTransaction - Test suite for Parabank2 workflows.

Test suite for Parabank2 workflows.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.parabank2.parabank_registration_page import ParabankRegistrationPage


class TestCompleteAccountSetupAndTransaction:
    """
    TestCompleteAccountSetupAndTransaction - Test suite for Parabank2.

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
        self.parabank_registration_page = ParabankRegistrationPage(self.web)

    # ==================== TEST METHODS ====================

    @pytest.mark.parabank2
    @autologger.automation_logger("Test")
    def test_submit_form(self):
        """
        Test submit form workflow.

        AAA Pattern:
        1. Arrange - Create role with test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange
        user_data = {"email": "testuser@example.com", "password": "TestPass123"}
        user = RegisteredUser(self.web, user_data, self.base_url)

        # Act - ONE workflow call, NO return value
        user.submit_form()

        # Assert - Via Page Object state-check methods (NOT return value)
        assert self.parabank_registration_page.is_registered(), "Is Registered"
        assert self.parabank_registration_page.has_savings_account(), "Has Savings Account"

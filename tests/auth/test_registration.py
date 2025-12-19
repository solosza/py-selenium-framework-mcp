"""
Test Registration - Account creation tests.

Tests the account registration workflow for new users.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
import time
from resources.utilities import autologger
from roles.new_user import NewUser
from pages.auth.registration_page import RegistrationPage


class TestRegistration:
    """
    Test suite for account registration.

    - @autologger("Test") decorator
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
        self.registration_page = RegistrationPage(web_interface)

    # ==================== TEST METHODS ====================

    @pytest.mark.auth
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_successful_registration(self):
        """
        Test that a new user can create an account successfully.

        Scenario: Successful account registration
        Given I am on the authentication page
        When I enter a unique email address and click create account
        And I fill in the registration form with valid personal details
        And I submit the registration form
        Then I should be logged in (account created successfully)

        AAA Pattern:
        1. Arrange - Create NewUser with unique test data
        2. Act - Call register() workflow method (no return value)
        3. Assert - Use RegistrationPage.is_account_created() state-check
        """
        # Arrange - Generate unique email using timestamp
        unique_email = f"testuser_{int(time.time())}@test.com"
        user_data = {
            "email": unique_email,
            "firstname": "Test",
            "lastname": "User",
            "password": "TestPass123!"
        }
        user = NewUser(self.web, user_data, self.base_url)

        # Act - ONE workflow call, NO return value
        user.register()

        # Assert - Via Page Object state-check method (DD-15)
        assert self.registration_page.is_account_created(), \
            f"Account should be created for {unique_email}"

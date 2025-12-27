"""
Test: Guest user successfully registers a new account.

Tests the registration workflow for a guest user.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from faker import Faker
from resources.utilities import autologger
from roles.guest_user import GuestUser
from pages.auth.registration_page import RegistrationPage


fake = Faker()


class TestGuestUserRegistration:
    """Test suite for guest user registration."""

    @pytest.fixture(autouse=True)
    def setup(self, web_interface, config):
        """Setup test fixtures."""
        self.web = web_interface
        self.config = config
        self.registration_page = RegistrationPage(web_interface)

    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_guest_user_successfully_registers_a_new_account(self):
        """
        Test that a guest user can register a new account.

        Given I am on the registration page
        When I enter a valid email address and click create account
        And I fill out the registration form with valid personal details
        And I submit the registration form
        Then I should see my account is created and I am logged in
        """
        # Arrange - Generate unique test data (self-contained strategy)
        user_data = {
            "email": fake.email(),
            "password": "TestPass123!",
            "first_name": fake.first_name(),
            "last_name": fake.last_name()
        }
        guest = GuestUser(self.web, user_data)

        # Act - ONE workflow call, NO return value
        guest.register_account()

        # Assert - Via POM state-check methods
        assert self.registration_page.is_account_created(), "Account should be created"
        assert self.registration_page.is_logged_in(), "User should be logged in after registration"

"""
AuthTasks - Task module for authentication operations.

Orchestrates RegistrationPage POM methods for user registration workflow.
"""

from interfaces.web_interface import WebInterface
from pages.auth.registration_page import RegistrationPage
from resources.utilities import autologger


class AuthTasks:
    """Task module for authentication domain operations."""

    def __init__(self, web: WebInterface):
        """Compose WebInterface + POMs, NO inheritance, NO base_url."""
        self.web = web
        self.registration_page = RegistrationPage(web)

    @autologger.automation_logger("Task")
    def register_user(self, user_data: dict) -> None:
        """
        Register a new user account.

        Single domain operation: complete user registration.
        NO return value - test asserts via registration_page.is_account_created()

        Args:
            user_data: Dict with email, password, first_name, last_name
        """
        # Navigate to registration page and enter email
        (self.registration_page
            .navigate()
            .enter_email_for_create(user_data["email"])
            .click_create_account())

        # Fill out registration form
        (self.registration_page
            .select_gender_mr()
            .enter_first_name(user_data["first_name"])
            .enter_last_name(user_data["last_name"])
            .enter_password(user_data["password"])
            .click_register())

        # NO return - test asserts via registration_page.is_account_created()

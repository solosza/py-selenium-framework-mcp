"""
Common Tasks - Reusable authentication and navigation workflows.

This module provides high-level task methods that orchestrate page objects
to accomplish common user workflows like login, logout, and registration.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from pages.auth.authentication_page import AuthenticationPage
from pages.auth.registration_page import RegistrationPage
from resources.utilities import autologger


class CommonTasks:
    """Common task workflows for authentication and navigation."""

    # URL patterns
    ACCOUNT_PAGE_URL_PATTERN = "controller=my-account"
    AUTH_PAGE_URL_PATTERN = "controller=authentication"

    def __init__(self, web: WebInterface, base_url: str):
        """
        Initialize CommonTasks.

        Args:
            web: WebInterface instance
            base_url: Application base URL
        """
        self.web = web
        self.base_url = base_url
        self.auth_page = AuthenticationPage(web)
        self.reg_page = RegistrationPage(web)

    # ==================== NAVIGATION METHODS ====================

    @autologger.automation_logger("Task")
    def navigate_to_login_page(self) -> None:
        """Navigate to the authentication/login page."""
        auth_url = f"{self.base_url}?controller=authentication"
        self.web.navigate_to(auth_url)

    @autologger.automation_logger("Task")
    def navigate_to_home_page(self) -> None:
        """Navigate to the home page."""
        self.web.navigate_to(self.base_url)

    # ==================== LOGIN METHODS ====================

    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        """
        Complete login workflow.

        Navigates to login page, enters credentials, and submits.
        Tests should verify success via auth_page.is_signed_in().

        Args:
            email: User email address
            password: User password
        """
        # Navigate to login page
        self.navigate_to_login_page()

        # Verify page loaded
        if not self.auth_page.is_page_loaded():
            self.web.logger.error("Authentication page did not load")
            return

        # Enter credentials and submit (chain atomic POM methods)
        (self.auth_page
            .enter_login_email(email)
            .enter_login_password(password)
            .click_sign_in())

        # Wait for page transition
        try:
            self.web.wait_for_url_contains(self.ACCOUNT_PAGE_URL_PATTERN, timeout=10)
            self.web.logger.info(f"Successfully logged in as: {email}")
        except Exception:
            # Check for login error
            if self.auth_page.is_login_error_displayed():
                error_msg = self.auth_page.get_error_message()
                self.web.logger.error(f"Login error: {error_msg}")
            else:
                self.web.logger.error("Login did not redirect to account page")

    # ==================== LOGOUT METHODS ====================

    @autologger.automation_logger("Task")
    def log_out(self) -> None:
        """
        Complete logout workflow.

        Clicks logout link. Tests should verify via auth_page.is_signed_out().
        """
        # Check if already logged out
        if self.auth_page.is_signed_out():
            self.web.logger.warning("User is already logged out")
            return

        # Click logout link using page object method
        self.auth_page.click_logout()

        # Wait for logout to complete (sign in link becomes visible) - use POM method
        try:
            self.auth_page.wait_for_sign_in_link_visible(timeout=10)
            self.web.logger.info("Successfully logged out")
        except Exception:
            self.web.logger.error("Logout transition did not complete")

    # ==================== REGISTRATION METHODS ====================

    @autologger.automation_logger("Task")
    def register_new_user(self, user_data: Dict[str, Any]) -> None:
        """
        Complete new user registration workflow.

        Navigates to registration page, submits email, and fills registration form.
        Tests should verify via auth_page.is_signed_in().

        Args:
            user_data: Dictionary containing user information
                Required keys: email, first_name, last_name, password, address (dict)
                Optional keys: gender, dob (dict), company, newsletter, special_offers

                Address dict required keys: address1, city, state, zipcode, country, phone
                Address dict optional keys: address2, additional_info, alias

                DOB dict keys: day, month, year
        """
        # Navigate to authentication page
        self.navigate_to_login_page()

        # Verify page loaded
        if not self.auth_page.is_page_loaded():
            self.web.logger.error("Authentication page did not load")
            return

        # Submit email to initiate registration (chain atomic POM methods)
        email = user_data['email']
        (self.auth_page
            .enter_registration_email(email)
            .click_create_account())

        # Check if registration form loaded (is_page_loaded has built-in wait)
        if not self.reg_page.is_page_loaded():
            self.web.logger.error("Registration form page did not load")

            # Check for email error (already registered)
            if self.auth_page.is_registration_email_error_displayed():
                error_msg = self.auth_page.get_error_message()
                self.web.logger.error(f"Registration email error: {error_msg}")
            return

        # Verify email was pre-filled
        prefilled_email = self.reg_page.get_email_value()
        if prefilled_email.lower() != email.lower():
            self.web.logger.warning(f"Email mismatch: expected {email}, got {prefilled_email}")

        # Fill registration form using atomic POM methods (fluent chain)
        # Personal information
        if user_data.get('gender'):
            self.reg_page.select_gender(user_data['gender'])

        (self.reg_page
            .enter_first_name(user_data['first_name'])
            .enter_last_name(user_data['last_name'])
            .enter_password(user_data['password']))

        # Date of birth (optional)
        dob = user_data.get('dob')
        if dob:
            self.reg_page.select_date_of_birth(dob['day'], dob['month'], dob['year'])

        # Address information
        address = user_data.get('address', {})
        (self.reg_page
            .enter_address(address.get('address1', ''))
            .enter_city(address.get('city', ''))
            .select_state(address.get('state', ''))
            .enter_zip_code(address.get('zipcode', ''))
            .enter_mobile_phone(address.get('phone', '')))

        # Submit registration
        self.reg_page.click_register()

        # Wait for account page or error
        try:
            self.web.wait_for_url_contains(self.ACCOUNT_PAGE_URL_PATTERN, timeout=10)
            self.web.logger.info(f"Successfully registered new user: {email}")
        except Exception:
            # Check for form validation errors
            if self.reg_page.has_error_message():
                error_msg = self.reg_page.get_error_message()
                self.web.logger.error(f"Registration form errors: {error_msg}")
            else:
                self.web.logger.error("Registration did not redirect to account page")

    # ==================== VERIFICATION METHODS ====================

    @autologger.automation_logger("Task")
    def get_current_user_state(self) -> str:
        """
        Get current authentication state.

        Returns:
            "logged_in", "logged_out", or "unknown"
        """
        if self.auth_page.is_signed_in():
            return "logged_in"
        elif self.auth_page.is_signed_out():
            return "logged_out"
        else:
            return "unknown"

    # ==================== ACCOUNT PAGE METHODS ====================

    @autologger.automation_logger("Task")
    def navigate_to_my_account(self) -> None:
        """Navigate to My Account page using header link (must be logged in)."""
        if not self.auth_page.is_signed_in():
            self.web.logger.warning("Cannot navigate to My Account - user not logged in")
            return

        self.auth_page.click_my_account()

"""
Common Tasks - Reusable authentication and navigation workflows.

This module provides high-level task methods that orchestrate page objects
to accomplish common user workflows like login, logout, and registration.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from pages.common.authentication_page import AuthenticationPage
from pages.common.registration_page import RegistrationPage


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

    def navigate_to_login_page(self) -> None:
        """Navigate to the authentication/login page."""
        auth_url = f"{self.base_url}?controller=authentication"
        self.web.navigate_to(auth_url)

    def navigate_to_home_page(self) -> None:
        """Navigate to the home page."""
        self.web.navigate_to(self.base_url)

    # ==================== LOGIN METHODS ====================

    def log_in(self, email: str, password: str) -> bool:
        """
        Complete login workflow.

        Navigates to login page, enters credentials, submits, and verifies success.

        Args:
            email: User email address
            password: User password

        Returns:
            True if login successful, False otherwise
        """
        # Navigate to login page
        self.navigate_to_login_page()

        # Verify page loaded
        if not self.auth_page.is_page_loaded():
            self.web.logger.error("Authentication page did not load")
            return False

        # Enter credentials and submit (chain atomic POM methods)
        (self.auth_page
            .enter_login_email(email)
            .enter_login_password(password)
            .click_sign_in())

        # Wait for page transition
        try:
            self.web.wait_for_url_contains(self.ACCOUNT_PAGE_URL_PATTERN, timeout=10)
        except Exception:
            # Check for login error
            if self.auth_page.is_login_error_displayed():
                error_msg = self.auth_page.get_error_message()
                self.web.logger.error(f"Login error: {error_msg}")
                return False

            self.web.logger.error("Login did not redirect to account page")
            return False

        # Verify logged in using page object method
        logged_in = self.verify_logged_in()

        if logged_in:
            self.web.logger.info(f"Successfully logged in as: {email}")
        else:
            self.web.logger.error(f"Login failed for: {email}")

        return logged_in

    # ==================== LOGOUT METHODS ====================

    def log_out(self) -> bool:
        """
        Complete logout workflow.

        Clicks logout link and verifies user is signed out.

        Returns:
            True if logout successful, False otherwise
        """
        # Check if already logged out
        if not self.verify_logged_in():
            self.web.logger.warning("User is already logged out")
            return True

        # Click logout link using page object method
        self.auth_page.click_logout()

        # Wait for logout to complete (sign in link becomes visible) - use POM method
        try:
            self.auth_page.wait_for_sign_in_link_visible(timeout=10)
        except Exception:
            self.web.logger.error("Logout transition did not complete")
            return False

        # Verify logged out using page object method
        logged_out = self.verify_logged_out()

        if logged_out:
            self.web.logger.info("Successfully logged out")
        else:
            self.web.logger.error("Logout failed")

        return logged_out

    # ==================== REGISTRATION METHODS ====================

    def register_new_user(self, user_data: Dict[str, Any]) -> bool:
        """
        Complete new user registration workflow.

        Navigates to registration page, submits email, fills registration form,
        and verifies successful account creation.

        Args:
            user_data: Dictionary containing user information
                Required keys: email, first_name, last_name, password, address (dict)
                Optional keys: gender, dob (dict), company, newsletter, special_offers

                Address dict required keys: address1, city, state, zipcode, country, phone
                Address dict optional keys: address2, additional_info, alias

                DOB dict keys: day, month, year

        Returns:
            True if registration successful, False otherwise
        """
        # Navigate to authentication page
        self.navigate_to_login_page()

        # Verify page loaded
        if not self.auth_page.is_page_loaded():
            self.web.logger.error("Authentication page did not load")
            return False

        # Submit email to initiate registration (chain atomic POM methods)
        email = user_data['email']
        (self.auth_page
            .enter_registration_email(email)
            .click_create_account())

        # Wait a moment for page transition
        self.web.driver.implicitly_wait(2)

        # Check if registration form loaded
        if not self.reg_page.is_page_loaded():
            self.web.logger.error("Registration form page did not load")

            # Check for email error (already registered)
            if self.auth_page.is_registration_email_error_displayed():
                error_msg = self.auth_page.get_error_message()
                self.web.logger.error(f"Registration email error: {error_msg}")
                return False

            return False

        # Verify email was pre-filled
        prefilled_email = self.reg_page.get_email_value()
        if prefilled_email.lower() != email.lower():
            self.web.logger.warning(f"Email mismatch: expected {email}, got {prefilled_email}")

        # Fill and submit registration form using page object method
        self.reg_page.register_user(user_data)

        # Wait for account page or error
        try:
            self.web.wait_for_url_contains(self.ACCOUNT_PAGE_URL_PATTERN, timeout=10)
        except Exception:
            # Check for form validation errors
            if self.reg_page.has_error_message():
                error_msg = self.reg_page.get_error_message()
                self.web.logger.error(f"Registration form errors: {error_msg}")
                return False

            self.web.logger.error("Registration did not redirect to account page")
            return False

        # Verify logged in (successful registration auto-logs in) using page object method
        registered = self.verify_logged_in()

        if registered:
            self.web.logger.info(f"Successfully registered new user: {email}")
        else:
            self.web.logger.error(f"Registration failed for: {email}")

        return registered

    # ==================== VERIFICATION METHODS ====================

    def verify_logged_in(self) -> bool:
        """
        Verify user is logged in.

        Uses page object method to check for logout link presence.

        Returns:
            True if user is logged in, False otherwise
        """
        # Use BasePage inherited method
        is_logged_in = self.auth_page.is_signed_in()

        if is_logged_in:
            self.web.logger.debug("User is logged in")
        else:
            self.web.logger.debug("User is not logged in")

        return is_logged_in

    def verify_logged_out(self) -> bool:
        """
        Verify user is logged out.

        Uses page object method to check for sign in link presence.

        Returns:
            True if user is logged out, False otherwise
        """
        # Use BasePage inherited method
        is_logged_out = self.auth_page.is_signed_out()

        if is_logged_out:
            self.web.logger.debug("User is logged out")
        else:
            self.web.logger.debug("User is still logged in")

        return is_logged_out

    def get_current_user_state(self) -> str:
        """
        Get current authentication state.

        Returns:
            "logged_in", "logged_out", or "unknown"
        """
        if self.verify_logged_in():
            return "logged_in"
        elif self.verify_logged_out():
            return "logged_out"
        else:
            return "unknown"

    # ==================== ACCOUNT PAGE METHODS ====================

    def navigate_to_my_account(self) -> None:
        """Navigate to My Account page using header link (must be logged in)."""
        if not self.verify_logged_in():
            self.web.logger.warning("Cannot navigate to My Account - user not logged in")
            return

        # Use BasePage inherited method
        self.auth_page.click_my_account()

    def is_on_account_page(self) -> bool:
        """
        Check if currently on the My Account page.

        Returns:
            True if URL contains account page pattern
        """
        current_url = self.auth_page.get_page_url()
        return self.ACCOUNT_PAGE_URL_PATTERN in current_url

    def is_on_auth_page(self) -> bool:
        """
        Check if currently on the authentication/login page.

        Returns:
            True if URL contains authentication page pattern
        """
        current_url = self.auth_page.get_page_url()
        return self.AUTH_PAGE_URL_PATTERN in current_url

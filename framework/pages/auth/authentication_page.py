"""
Authentication Page - Login and registration initiation page object.

URL: http://www.automationpractice.pl/index.php?controller=authentication
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from interfaces.web_interface import WebInterface


class AuthenticationPage(BasePage):
    """
    Page Object for the Authentication page (login and account creation).

    This page contains:
    - Login form for returning customers
    - Email submission form for new account creation
    """

    def __init__(self, web: WebInterface):
        """
        Initialize AuthenticationPage.

        Args:
            web: WebInterface instance
        """
        super().__init__(web)

    # ==================== LOCATORS ====================

    # Page header
    AUTH_HEADER = (By.XPATH, "//*[text()='Authentication']")

    # Login form (Returning Customer)
    LOGIN_EMAIL = (By.ID, "email")
    LOGIN_PASSWORD = (By.ID, "passwd")
    SUBMIT_LOGIN = (By.ID, "SubmitLogin")
    FORGOT_PASSWORD_LINK = (By.CSS_SELECTOR, ".lost_password.form-group")

    # Registration section (New Customer)
    EMAIL_CREATE = (By.ID, "email_create")
    SUBMIT_CREATE = (By.ID, "SubmitCreate")

    # Error messages
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")
    ERROR_LIST = (By.CSS_SELECTOR, ".alert-danger ol li")

    # ==================== PAGE METHODS ====================

    def is_page_loaded(self) -> bool:
        """
        Verify authentication page is loaded.

        Returns:
            True if authentication header is visible
        """
        return self.web.is_element_displayed(*self.AUTH_HEADER, timeout=5)

    # ==================== LOGIN METHODS ====================

    def enter_login_email(self, email: str):
        """
        Enter email in login form.

        Args:
            email: Email address

        Returns:
            self for method chaining
        """
        self.web.type_text(*self.LOGIN_EMAIL, text=email)
        return self

    def enter_login_password(self, password: str):
        """
        Enter password in login form.

        Args:
            password: Password

        Returns:
            self for method chaining
        """
        self.web.type_text(*self.LOGIN_PASSWORD, text=password)
        return self

    def click_sign_in(self):
        """
        Click the Sign In button to submit login form.

        Returns:
            self for method chaining
        """
        self.web.click(*self.SUBMIT_LOGIN)
        return self

    def click_forgot_password(self):
        """
        Click the Forgot Password link.

        Returns:
            self for method chaining
        """
        self.web.click(*self.FORGOT_PASSWORD_LINK)
        return self

    # ==================== REGISTRATION INITIATION METHODS ====================

    def enter_registration_email(self, email: str):
        """
        Enter email to create new account.

        Args:
            email: Email address for new account

        Returns:
            self for method chaining
        """
        self.web.type_text(*self.EMAIL_CREATE, text=email)
        return self

    def click_create_account(self):
        """
        Click Create Account button to proceed to registration form.

        Returns:
            self for method chaining
        """
        self.web.click(*self.SUBMIT_CREATE)
        return self

    # ==================== ERROR MESSAGE METHODS ====================

    def has_error_message(self) -> bool:
        """
        Check if error message is displayed.

        Returns:
            True if error message container is visible
        """
        return self.web.is_element_displayed(*self.ERROR_MESSAGE, timeout=5)

    def get_error_message(self) -> str:
        """
        Get error message text.

        Returns:
            Error message text (all errors concatenated if multiple)
        """
        if not self.has_error_message():
            return ""

        try:
            # Try to get individual error items from list
            error_items = self.web.find_elements(*self.ERROR_LIST)
            if error_items:
                errors = [item.text for item in error_items]
                return "; ".join(errors)

            # Fallback: get entire error container text
            return self.web.get_text(*self.ERROR_MESSAGE)
        except Exception:
            return ""

    def is_login_error_displayed(self) -> bool:
        """
        Check if login-specific error is displayed.

        Returns:
            True if authentication failed error is shown
        """
        if not self.has_error_message():
            return False

        error_text = self.get_error_message()
        return "Authentication failed" in error_text or "Invalid email" in error_text

    def is_registration_email_error_displayed(self) -> bool:
        """
        Check if registration email error is displayed.

        Returns:
            True if email validation error is shown
        """
        if not self.has_error_message():
            return False

        error_text = self.get_error_message()
        return "Invalid email address" in error_text or "already been registered" in error_text

    # ==================== VALIDATION METHODS ====================

    def is_login_form_visible(self) -> bool:
        """
        Check if login form is visible.

        Returns:
            True if login email field is displayed
        """
        return self.web.is_element_displayed(*self.LOGIN_EMAIL, timeout=5)

    def is_registration_form_visible(self) -> bool:
        """
        Check if registration email form is visible.

        Returns:
            True if email create field is displayed
        """
        return self.web.is_element_displayed(*self.EMAIL_CREATE, timeout=5)

    def get_login_email_value(self) -> str:
        """
        Get current value in login email field.

        Returns:
            Email field value
        """
        return self.web.get_attribute(*self.LOGIN_EMAIL, attribute="value") or ""

    def get_registration_email_value(self) -> str:
        """
        Get current value in registration email field.

        Returns:
            Email field value
        """
        return self.web.get_attribute(*self.EMAIL_CREATE, attribute="value") or ""

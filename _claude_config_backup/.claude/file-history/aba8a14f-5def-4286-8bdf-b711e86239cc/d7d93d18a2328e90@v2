"""
LoginPage - Authentication page object.

Represents the login/authentication page and provides methods for interaction.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from interfaces.web_interface import WebInterface


class LoginPage(BasePage):
    """
    LoginPage - Page Object Model

    Represents the login page and provides methods for interaction.
    Inherits common header/footer methods from BasePage.
    """

    def __init__(self, web: WebInterface):
        """
        Initialize LoginPage.

        Args:
            web: WebInterface instance
        """
        super().__init__(web)

    # ==================== LOCATORS ====================

    SUBMIT_LOGIN = (By.CSS_SELECTOR, "#SubmitLogin")
    EMAIL = (By.CSS_SELECTOR, "#email")
    PASSWD = (By.CSS_SELECTOR, "#passwd")

    # ==================== INTERACTION METHODS ====================

    def click_submit_login(self) -> "LoginPage":
        """Click submit login button."""
        self.web.click(*self.SUBMIT_LOGIN)
        return self

    def enter_email(self, text: str) -> "LoginPage":
        """
        Enter text into EMAIL field.

        Args:
            text: Text to enter
        """
        self.web.type_text(*self.EMAIL, text)
        return self

    def enter_passwd(self, text: str) -> "LoginPage":
        """
        Enter text into PASSWD field.

        Args:
            text: Text to enter
        """
        self.web.type_text(*self.PASSWD, text)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_page_loaded(self) -> bool:
        """
        Check if login page is loaded.

        Returns:
            True if login form is visible
        """
        return self.web.is_element_displayed(*self.EMAIL, timeout=5)

    def has_error_message(self) -> bool:
        """
        Check if error message is displayed.

        Returns:
            True if error alert is visible
        """
        ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")
        return self.web.is_element_displayed(*ERROR_MESSAGE, timeout=3)

    def get_error_message(self) -> str:
        """
        Get error message text.

        Returns:
            Error message text or empty string
        """
        ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")
        if not self.has_error_message():
            return ""
        return self.web.get_text(*ERROR_MESSAGE)

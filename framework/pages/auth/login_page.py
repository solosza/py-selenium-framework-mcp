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

    SUBMITLOGIN = (By.CSS_SELECTOR, "#SubmitLogin")
    EMAIL = (By.CSS_SELECTOR, "#email")
    PASSWD = (By.CSS_SELECTOR, "#passwd")

    # ==================== INTERACTION METHODS ====================

    def click_submitlogin(self) -> "LoginPage":
        """Click SUBMITLOGIN button."""
        self.web.click(*self.SUBMITLOGIN)
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

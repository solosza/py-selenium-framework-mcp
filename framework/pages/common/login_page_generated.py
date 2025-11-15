from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class LoginPage:
    """
    LoginPage - Page Object Model

    Represents the page and provides methods for interaction.
    """

    def __init__(self, web: WebInterface):
        """
        Initialize LoginPage.

        Args:
            web: WebInterface instance
        """
        self.web = web

    # ==================== LOCATORS ====================

    SUBMITLOGIN = (By.CSS_SELECTOR, "#SubmitLogin")
    EMAIL = (By.CSS_SELECTOR, "#email")
    PASSWD = (By.CSS_SELECTOR, "#passwd")


    # ==================== INTERACTION METHODS ====================

    def click_submitlogin(self) -> None:
        """Click SUBMITLOGIN button."""
        self.web.click(*self.SUBMITLOGIN)

    def enter_email(self, text: str) -> None:
        """
        Enter text into EMAIL field.

        Args:
            text: Text to enter
        """
        self.web.type_text(*self.EMAIL, text)

    def enter_passwd(self, text: str) -> None:
        """
        Enter text into PASSWD field.

        Args:
            text: Text to enter
        """
        self.web.type_text(*self.PASSWD, text)


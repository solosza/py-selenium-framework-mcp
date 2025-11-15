from selenium.webdriver.common.by import By
from framework.pages.base_page import BasePage
from framework.interfaces.web_interface import WebInterface


class LoginPage(BasePage):
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
        super().__init__(web)

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
        self.web.send_keys(*self.EMAIL, text)

    def enter_passwd(self, text: str) -> None:
        """
        Enter text into PASSWD field.

        Args:
            text: Text to enter
        """
        self.web.send_keys(*self.PASSWD, text)


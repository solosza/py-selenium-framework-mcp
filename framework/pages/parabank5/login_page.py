from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class LoginPage:
    """Page Object for ParaBank login page."""

    # LOCATORS
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[name='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")
    LOGIN_BTN = (By.CSS_SELECTOR, "input.button[value='Log In']")
    WELCOME_MESSAGE = (By.CSS_SELECTOR, "p.smallText")
    LOGOUT_LINK = (By.CSS_SELECTOR, "a[href*='logout']")

    def __init__(self, web: WebInterface):
        self.web = web

    def navigate(self) -> "LoginPage":
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/index.htm")
        return self

    def enter_username(self, text: str) -> "LoginPage":
        self.web.type_text(*self.USERNAME_INPUT, text)
        return self

    def enter_password(self, text: str) -> "LoginPage":
        self.web.type_text(*self.PASSWORD_INPUT, text)
        return self

    def click_login(self) -> "LoginPage":
        self.web.click(*self.LOGIN_BTN)
        return self

    def is_logged_in(self) -> bool:
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)

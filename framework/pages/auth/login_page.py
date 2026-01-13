
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface

class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")

    def __init__(self, web: WebInterface):
        self.web = web

    def navigate(self) -> "LoginPage":
        self.web.navigate_to(self.web.config["url"] + "/login")
        return self

    def enter_email(self, text: str) -> "LoginPage":
        self.web.type_text(*self.EMAIL, text)
        return self

    def is_logged_in(self) -> bool:
        return self.web.is_element_displayed(By.CSS_SELECTOR, ".logout")

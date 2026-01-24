
from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from pages.auth.login_page import LoginPage


class AuthTasks:
    def __init__(self, web: WebInterface):
        """Compose Page Objects - NO base_url."""
        self.web = web
        self.login_page = LoginPage(web)

    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        self.login_page.navigate()
        (self.login_page
            .enter_email(email)
            .enter_password(password)
            .click_submit())

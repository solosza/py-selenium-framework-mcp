"""ParaBank Home Page - Login functionality."""
from selenium.webdriver.common.by import By
from framework.interfaces.web_interface import WebInterface


class ParabankHomePage:
    """Page object for ParaBank homepage with login form."""

    # Locators - Input elements
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[name='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "input[value='Log In']")
    REGISTER_LINK = (By.CSS_SELECTOR, "a[href*='register.htm']")

    # Locators - Output elements
    LOGIN_ERROR_MESSAGE = (By.CSS_SELECTOR, ".error")
    WELCOME_MESSAGE = (By.CSS_SELECTOR, "#leftPanel p.smallText")

    def __init__(self, web: WebInterface):
        self.web = web

    def navigate(self, base_url: str) -> "ParabankHomePage":
        """Navigate to the ParaBank homepage."""
        self.web.navigate_to(f"{base_url}/parabank/index.htm")
        return self

    # Atomic action methods - return self for chaining
    def enter_username(self, username: str) -> "ParabankHomePage":
        """Enter username in the login form."""
        self.web.type_text(*self.USERNAME_INPUT, username)
        return self

    def enter_password(self, password: str) -> "ParabankHomePage":
        """Enter password in the login form."""
        self.web.type_text(*self.PASSWORD_INPUT, password)
        return self

    def click_login(self) -> "ParabankHomePage":
        """Click the Log In button."""
        self.web.click(*self.LOGIN_BUTTON)
        return self

    def click_register(self) -> "ParabankHomePage":
        """Click the Register link."""
        self.web.click(*self.REGISTER_LINK)
        return self

    # State-check methods for assertions
    def is_login_error_displayed(self) -> bool:
        """Check if login error message is displayed."""
        return self.web.is_element_displayed(*self.LOGIN_ERROR_MESSAGE, timeout=5)

    def get_login_error_message(self) -> str:
        """Get the login error message text."""
        return self.web.get_text(*self.LOGIN_ERROR_MESSAGE)

    def is_welcome_message_displayed(self) -> bool:
        """Check if welcome message is displayed (logged in state)."""
        return self.web.is_element_displayed(*self.WELCOME_MESSAGE, timeout=5)

    def get_welcome_message(self) -> str:
        """Get the welcome message text."""
        return self.web.get_text(*self.WELCOME_MESSAGE)

"""
ParabankIndexPage - Page Object Model

Page Object for ParaBank login/index page.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class ParabankIndexPage:
    """
    Page Object for Parabank Index Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # LOCATORS - Class-level constants, UPPER_SNAKE_CASE
    # ═══════════════════════════════════════════════════════════════════════════
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[name='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "input[value='Log In']")
    REGISTER_LINK = (By.CSS_SELECTOR, "a[href='register.htm']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "p.error")
    CUSTOMER_LOGIN_HEADING = (By.CSS_SELECTOR, "h2")

    # ═══════════════════════════════════════════════════════════════════════════
    # CONSTRUCTOR - Compose WebInterface, NO inheritance
    # ═══════════════════════════════════════════════════════════════════════════
    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ═══════════════════════════════════════════════════════════════════════════
    # NAVIGATION - POM owns navigation, gets URL from WebInterface.config
    # ═══════════════════════════════════════════════════════════════════════════
    def navigate(self) -> "ParabankIndexPage":
        """Navigate to this page. Gets URL from WebInterface config."""
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/index.htm")
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # ATOMIC METHODS - One action per method, return self for chaining
    # ═══════════════════════════════════════════════════════════════════════════
    def enter_username(self, text: str) -> "ParabankIndexPage":
        """Enter text into username field."""
        self.web.type_text(*self.USERNAME_INPUT, text)
        return self

    def enter_password(self, text: str) -> "ParabankIndexPage":
        """Enter text into password field."""
        self.web.type_text(*self.PASSWORD_INPUT, text)
        return self

    def click_login(self) -> "ParabankIndexPage":
        """Click the login button."""
        self.web.click(*self.LOGIN_BUTTON)
        return self

    def click_register(self) -> "ParabankIndexPage":
        """Click the register link."""
        self.web.click(*self.REGISTER_LINK)
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # STATE-CHECK METHODS - For test assertions, return bool
    # ═══════════════════════════════════════════════════════════════════════════
    def is_logged_in(self) -> bool:
        """Check if user is logged in (login button no longer visible)."""
        return not self.web.is_element_displayed(*self.LOGIN_BUTTON, timeout=2)

    def is_error_displayed(self) -> bool:
        """Check if error message is visible."""
        return self.web.is_element_displayed(*self.ERROR_MESSAGE, timeout=3)

    def is_page_loaded(self) -> bool:
        """Check if page is fully loaded."""
        return self.web.is_element_displayed(*self.CUSTOMER_LOGIN_HEADING, timeout=5)

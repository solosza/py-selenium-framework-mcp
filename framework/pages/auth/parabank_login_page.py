"""
ParabankLoginPage - Page Object Model

Page Object representing a single page in the application.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class ParabankLoginPage:
    """
    Page Object for Parabank Login Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== LOCATORS (Class Constants) ====================
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[name='username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "input[type='submit'][value='Log In']")
    WELCOME_MESSAGE = (By.CSS_SELECTOR, "p.smallText")
    LOGOUT_LINK = (By.CSS_SELECTOR, "a[href='logout.htm']")

    # ==================== NAVIGATION ====================

    def navigate(self) -> "ParabankLoginPage":
        """Navigate to Parabank login page."""
        self.web.navigate_to(f"{self.web.config['url']}/parabank/index.htm")
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_username(self, text: str) -> "ParabankLoginPage":
        """Enter text into username field."""
        self.web.type_text(*self.USERNAME_INPUT, text)
        return self

    def enter_password(self, text: str) -> "ParabankLoginPage":
        """Enter text into password field."""
        self.web.type_text(*self.PASSWORD_INPUT, text)
        return self

    def click_login(self) -> "ParabankLoginPage":
        """Click the login button."""
        self.web.click(*self.LOGIN_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_logged_in(self) -> bool:
        """Check if user is logged in by verifying logout link is visible."""
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)

    def is_account_overview_visible(self) -> bool:
        """Check if account overview is visible by checking welcome message."""
        return self.web.is_element_displayed(*self.WELCOME_MESSAGE, timeout=5)

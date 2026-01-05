"""
OpenNewAccountPage - Page Object Model

Page Object representing the ParaBank Open New Account page.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class OpenNewAccountPage:
    """
    Page Object for Open New Account Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== NAVIGATION ====================
    def navigate(self) -> "OpenNewAccountPage":
        """Navigate to open new account page using config URL."""
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/openaccount.htm")
        return self

    # ==================== LOCATORS (Class Constants) ====================
    ACCOUNT_TYPE_SELECT = (By.CSS_SELECTOR, "#type")
    FROM_ACCOUNT_SELECT = (By.CSS_SELECTOR, "#fromAccountId")
    OPEN_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "input[value='Open New Account']")

    # State-check locators
    ACCOUNT_OPENED_HEADING = (By.CSS_SELECTOR, "#rightPanel h1")
    CONFIRMATION_MESSAGE = (By.CSS_SELECTOR, "#rightPanel p")
    NEW_ACCOUNT_LINK = (By.CSS_SELECTOR, "#rightPanel a[href*='activity.htm']")

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def select_account_type(self, account_type: str) -> "OpenNewAccountPage":
        """Select account type (CHECKING or SAVINGS)."""
        self.web.select_dropdown_by_visible_text(*self.ACCOUNT_TYPE_SELECT, account_type)
        return self

    def select_from_account(self, account_id: str) -> "OpenNewAccountPage":
        """Select source account for initial deposit."""
        self.web.select_dropdown_by_visible_text(*self.FROM_ACCOUNT_SELECT, account_id)
        return self

    def click_open_account(self) -> "OpenNewAccountPage":
        """Click the Open New Account button."""
        self.web.click(*self.OPEN_ACCOUNT_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_account_created(self) -> bool:
        """Check if account was successfully created."""
        try:
            text = self.web.get_text(*self.ACCOUNT_OPENED_HEADING, timeout=5)
            return "Account Opened" in text
        except Exception:
            return False

    def has_account_number(self) -> bool:
        """Check if new account number is displayed."""
        try:
            return self.web.is_element_displayed(*self.NEW_ACCOUNT_LINK, timeout=5)
        except Exception:
            return False

    def get_new_account_number(self) -> str:
        """Get the new account number from the confirmation page."""
        return self.web.get_text(*self.NEW_ACCOUNT_LINK, timeout=5)

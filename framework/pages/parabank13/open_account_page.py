"""
OpenAccountPage - Page Object Model

Page Object representing a single page in the application.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class OpenAccountPage:
    """
    Page Object for Open Account Page.

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
    ACCOUNT_TYPE_DROPDOWN = (By.CSS_SELECTOR, "#type")
    FROM_ACCOUNT_DROPDOWN = (By.CSS_SELECTOR, "#fromAccountId")
    OPEN_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "input.button[value='Open New Account']")
    SUCCESS_HEADING = (By.CSS_SELECTOR, "h1.title")
    SUCCESS_MESSAGE = (By.XPATH, "//p[contains(text(), 'Congratulations')]")
    NEW_ACCOUNT_NUMBER = (By.CSS_SELECTOR, "#newAccountId")

    # ==================== NAVIGATION ====================

    def navigate(self) -> "OpenAccountPage":
        """Navigate to Open Account page (DD-49: URL from config)."""
        self.web.navigate_to(self.web.config['url'] + '/parabank/openaccount.htm')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def select_account_type(self, account_type: str) -> "OpenAccountPage":
        """Select account type from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.ACCOUNT_TYPE_DROPDOWN, account_type)
        return self

    def select_from_account(self, account_number: str) -> "OpenAccountPage":
        """Select from account from dropdown by visible text (account number)."""
        self.web.select_dropdown_by_visible_text(*self.FROM_ACCOUNT_DROPDOWN, account_number)
        return self

    def click_open_account(self) -> "OpenAccountPage":
        """Click Open New Account button."""
        self.web.click(*self.OPEN_ACCOUNT_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_account_opened_successfully(self) -> bool:
        """Check if account opened successfully by verifying success heading."""
        return self.web.is_element_displayed(*self.SUCCESS_HEADING, timeout=5)

    def has_success_message(self) -> bool:
        """Check if success message is displayed."""
        return self.web.is_element_displayed(*self.SUCCESS_MESSAGE, timeout=5)

    def get_new_account_number(self) -> str:
        """Get the new account number from the success page."""
        return self.web.get_text(*self.NEW_ACCOUNT_NUMBER)

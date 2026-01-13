"""
ParabankRegistrationPage - Page Object Model

Page Object representing a single page in the application.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class ParabankRegistrationPage:
    """
    Page Object for Parabank Registration Page.

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
    FIRST_NAME = (By.ID, "customer.firstName")
    LAST_NAME = (By.ID, "customer.lastName")
    ADDRESS = (By.ID, "customer.address.street")
    CITY = (By.ID, "customer.address.city")
    STATE = (By.ID, "customer.address.state")
    ZIP_CODE = (By.ID, "customer.address.zipCode")
    PHONE = (By.ID, "customer.phoneNumber")
    SSN = (By.ID, "customer.ssn")
    USERNAME = (By.ID, "customer.username")
    PASSWORD = (By.ID, "customer.password")
    CONFIRM_PASSWORD = (By.ID, "repeatedPassword")
    REGISTER_BTN = (By.CSS_SELECTOR, "input[value='Register']")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, "p.title")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "span.error")

    # ==================== NAVIGATION ====================

    def navigate(self) -> "ParabankRegistrationPage":
        """Navigate to registration page."""
        self.web.navigate_to(self.web.config['url'] + '/parabank/register.htm')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_first_name(self, text: str) -> "ParabankRegistrationPage":
        """Enter first name."""
        self.web.type_text(*self.FIRST_NAME, text)
        return self

    def enter_last_name(self, text: str) -> "ParabankRegistrationPage":
        """Enter last name."""
        self.web.type_text(*self.LAST_NAME, text)
        return self

    def enter_address(self, text: str) -> "ParabankRegistrationPage":
        """Enter address."""
        self.web.type_text(*self.ADDRESS, text)
        return self

    def enter_city(self, text: str) -> "ParabankRegistrationPage":
        """Enter city."""
        self.web.type_text(*self.CITY, text)
        return self

    def enter_state(self, text: str) -> "ParabankRegistrationPage":
        """Enter state."""
        self.web.type_text(*self.STATE, text)
        return self

    def enter_zip_code(self, text: str) -> "ParabankRegistrationPage":
        """Enter zip code."""
        self.web.type_text(*self.ZIP_CODE, text)
        return self

    def enter_phone(self, text: str) -> "ParabankRegistrationPage":
        """Enter phone number."""
        self.web.type_text(*self.PHONE, text)
        return self

    def enter_ssn(self, text: str) -> "ParabankRegistrationPage":
        """Enter SSN."""
        self.web.type_text(*self.SSN, text)
        return self

    def enter_username(self, text: str) -> "ParabankRegistrationPage":
        """Enter username."""
        self.web.type_text(*self.USERNAME, text)
        return self

    def enter_password(self, text: str) -> "ParabankRegistrationPage":
        """Enter password."""
        self.web.type_text(*self.PASSWORD, text)
        return self

    def enter_confirm_password(self, text: str) -> "ParabankRegistrationPage":
        """Enter confirm password."""
        self.web.type_text(*self.CONFIRM_PASSWORD, text)
        return self

    def click_register_btn(self) -> "ParabankRegistrationPage":
        """Click register button."""
        self.web.click(*self.REGISTER_BTN)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_registered(self) -> bool:
        """Check if registration was successful."""
        return self.web.is_element_displayed(*self.SUCCESS_MESSAGE, timeout=5)

    def has_savings_account(self) -> bool:
        """Check if savings account exists (placeholder for cross-page state)."""
        return False

    def is_transfer_complete(self) -> bool:
        """Check if transfer is complete (placeholder for cross-page state)."""
        return False

    def is_transaction_visible(self) -> bool:
        """Check if transaction is visible (placeholder for cross-page state)."""
        return False

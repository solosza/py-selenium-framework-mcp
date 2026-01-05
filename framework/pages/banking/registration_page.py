"""
RegistrationPage - Page Object Model

Page Object representing the ParaBank registration page.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class RegistrationPage:
    """
    Page Object for Registration Page.

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
    def navigate(self) -> "RegistrationPage":
        """Navigate to registration page using config URL."""
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/register.htm")
        return self

    # ==================== LOCATORS (Class Constants) ====================
    FIRST_NAME_INPUT = (By.CSS_SELECTOR, "input[id='customer.firstName']")
    LAST_NAME_INPUT = (By.CSS_SELECTOR, "input[id='customer.lastName']")
    ADDRESS_INPUT = (By.CSS_SELECTOR, "input[id='customer.address.street']")
    CITY_INPUT = (By.CSS_SELECTOR, "input[id='customer.address.city']")
    STATE_INPUT = (By.CSS_SELECTOR, "input[id='customer.address.state']")
    ZIP_CODE_INPUT = (By.CSS_SELECTOR, "input[id='customer.address.zipCode']")
    PHONE_INPUT = (By.CSS_SELECTOR, "input[id='customer.phoneNumber']")
    SSN_INPUT = (By.CSS_SELECTOR, "input[id='customer.ssn']")
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[id='customer.username']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[id='customer.password']")
    CONFIRM_PASSWORD_INPUT = (By.CSS_SELECTOR, "input[id='repeatedPassword']")
    REGISTER_BUTTON = (By.CSS_SELECTOR, "input[value='Register']")

    # State-check locators
    WELCOME_HEADING = (By.CSS_SELECTOR, "#rightPanel h1")
    CONFIRMATION_MESSAGE = (By.CSS_SELECTOR, "#rightPanel p")

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_first_name(self, text: str) -> "RegistrationPage":
        """Enter first name in the input field."""
        self.web.type_text(*self.FIRST_NAME_INPUT, text)
        return self

    def enter_last_name(self, text: str) -> "RegistrationPage":
        """Enter last name in the input field."""
        self.web.type_text(*self.LAST_NAME_INPUT, text)
        return self

    def enter_address(self, text: str) -> "RegistrationPage":
        """Enter address in the input field."""
        self.web.type_text(*self.ADDRESS_INPUT, text)
        return self

    def enter_city(self, text: str) -> "RegistrationPage":
        """Enter city in the input field."""
        self.web.type_text(*self.CITY_INPUT, text)
        return self

    def enter_state(self, text: str) -> "RegistrationPage":
        """Enter state in the input field."""
        self.web.type_text(*self.STATE_INPUT, text)
        return self

    def enter_zip_code(self, text: str) -> "RegistrationPage":
        """Enter zip code in the input field."""
        self.web.type_text(*self.ZIP_CODE_INPUT, text)
        return self

    def enter_phone(self, text: str) -> "RegistrationPage":
        """Enter phone number in the input field."""
        self.web.type_text(*self.PHONE_INPUT, text)
        return self

    def enter_ssn(self, text: str) -> "RegistrationPage":
        """Enter SSN in the input field."""
        self.web.type_text(*self.SSN_INPUT, text)
        return self

    def enter_username(self, text: str) -> "RegistrationPage":
        """Enter username in the input field."""
        self.web.type_text(*self.USERNAME_INPUT, text)
        return self

    def enter_password(self, text: str) -> "RegistrationPage":
        """Enter password in the input field."""
        self.web.type_text(*self.PASSWORD_INPUT, text)
        return self

    def enter_confirm_password(self, text: str) -> "RegistrationPage":
        """Enter password confirmation in the input field."""
        self.web.type_text(*self.CONFIRM_PASSWORD_INPUT, text)
        return self

    def click_register(self) -> "RegistrationPage":
        """Click the Register button."""
        self.web.click(*self.REGISTER_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_registration_confirmed(self) -> bool:
        """Check if registration was successful by looking for confirmation message."""
        try:
            text = self.web.get_text(*self.CONFIRMATION_MESSAGE, timeout=5)
            return "Your account was created successfully" in text
        except Exception:
            return False

    def has_welcome_message(self) -> bool:
        """Check if welcome message with username is displayed."""
        try:
            text = self.web.get_text(*self.WELCOME_HEADING, timeout=5)
            return text.startswith("Welcome ")
        except Exception:
            return False

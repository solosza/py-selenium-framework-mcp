"""ParaBank Registration Page."""
from selenium.webdriver.common.by import By
from framework.interfaces.web_interface import WebInterface


class RegistrationPage:
    """Page object for ParaBank registration form."""

    # Locators - Personal Information
    FIRST_NAME_INPUT = (By.ID, "customer.firstName")
    LAST_NAME_INPUT = (By.ID, "customer.lastName")
    ADDRESS_INPUT = (By.ID, "customer.address.street")
    CITY_INPUT = (By.ID, "customer.address.city")
    STATE_INPUT = (By.ID, "customer.address.state")
    ZIP_CODE_INPUT = (By.ID, "customer.address.zipCode")
    PHONE_INPUT = (By.ID, "customer.phoneNumber")
    SSN_INPUT = (By.ID, "customer.ssn")

    # Locators - Account Credentials
    USERNAME_INPUT = (By.ID, "customer.username")
    PASSWORD_INPUT = (By.ID, "customer.password")
    CONFIRM_PASSWORD_INPUT = (By.ID, "repeatedPassword")
    REGISTER_BUTTON = (By.CSS_SELECTOR, "input[value='Register']")

    # Locators - Output elements
    WELCOME_HEADING = (By.XPATH, "//h1[contains(text(),'Welcome')]")
    SUCCESS_MESSAGE = (By.XPATH, "//p[contains(text(),'Your account was created successfully')]")
    USERNAME_ERROR = (By.ID, "customer.username.errors")

    def __init__(self, web: WebInterface):
        self.web = web

    def navigate(self, base_url: str) -> "RegistrationPage":
        """Navigate to the registration page."""
        self.web.navigate_to(f"{base_url}/parabank/register.htm")
        return self

    # Atomic action methods - return self for chaining
    def enter_first_name(self, first_name: str) -> "RegistrationPage":
        """Enter first name."""
        self.web.type_text(*self.FIRST_NAME_INPUT, first_name)
        return self

    def enter_last_name(self, last_name: str) -> "RegistrationPage":
        """Enter last name."""
        self.web.type_text(*self.LAST_NAME_INPUT, last_name)
        return self

    def enter_address(self, address: str) -> "RegistrationPage":
        """Enter street address."""
        self.web.type_text(*self.ADDRESS_INPUT, address)
        return self

    def enter_city(self, city: str) -> "RegistrationPage":
        """Enter city."""
        self.web.type_text(*self.CITY_INPUT, city)
        return self

    def enter_state(self, state: str) -> "RegistrationPage":
        """Enter state."""
        self.web.type_text(*self.STATE_INPUT, state)
        return self

    def enter_zip_code(self, zip_code: str) -> "RegistrationPage":
        """Enter zip code."""
        self.web.type_text(*self.ZIP_CODE_INPUT, zip_code)
        return self

    def enter_phone(self, phone: str) -> "RegistrationPage":
        """Enter phone number."""
        self.web.type_text(*self.PHONE_INPUT, phone)
        return self

    def enter_ssn(self, ssn: str) -> "RegistrationPage":
        """Enter SSN."""
        self.web.type_text(*self.SSN_INPUT, ssn)
        return self

    def enter_username(self, username: str) -> "RegistrationPage":
        """Enter username."""
        self.web.type_text(*self.USERNAME_INPUT, username)
        return self

    def enter_password(self, password: str) -> "RegistrationPage":
        """Enter password."""
        self.web.type_text(*self.PASSWORD_INPUT, password)
        return self

    def enter_confirm_password(self, password: str) -> "RegistrationPage":
        """Enter password confirmation."""
        self.web.type_text(*self.CONFIRM_PASSWORD_INPUT, password)
        return self

    def click_register(self) -> "RegistrationPage":
        """Click the Register button."""
        self.web.click(*self.REGISTER_BUTTON)
        return self

    # State-check methods for assertions
    def is_registration_successful(self) -> bool:
        """Check if registration was successful (welcome heading displayed)."""
        return self.web.is_element_displayed(*self.WELCOME_HEADING, timeout=10)

    def get_welcome_heading_text(self) -> str:
        """Get the welcome heading text."""
        return self.web.get_text(*self.WELCOME_HEADING)

    def is_success_message_displayed(self) -> bool:
        """Check if success message is displayed."""
        return self.web.is_element_displayed(*self.SUCCESS_MESSAGE, timeout=5)

    def get_success_message(self) -> str:
        """Get the success message text."""
        return self.web.get_text(*self.SUCCESS_MESSAGE)

    def is_username_error_displayed(self) -> bool:
        """Check if username error is displayed."""
        return self.web.is_element_displayed(*self.USERNAME_ERROR, timeout=3)

    def get_username_error(self) -> str:
        """Get the username error message."""
        return self.web.get_text(*self.USERNAME_ERROR)

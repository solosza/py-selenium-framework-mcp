"""
RegistrationPage - Page Object Model

Page Object for user registration on the e-commerce site.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class RegistrationPage:
    """Page Object for Registration Page."""

    # ==================== LOCATORS (Class Constants) ====================
    GENDER_MR = (By.CSS_SELECTOR, "#id_gender1")
    GENDER_MRS = (By.CSS_SELECTOR, "#id_gender2")
    FIRST_NAME = (By.CSS_SELECTOR, "#customer_firstname")
    LAST_NAME = (By.CSS_SELECTOR, "#customer_lastname")
    EMAIL = (By.CSS_SELECTOR, "#email")
    PASSWORD = (By.CSS_SELECTOR, "#passwd")
    BIRTH_DAY = (By.CSS_SELECTOR, "#days")
    BIRTH_MONTH = (By.CSS_SELECTOR, "#months")
    BIRTH_YEAR = (By.CSS_SELECTOR, "#years")
    NEWSLETTER = (By.CSS_SELECTOR, "#newsletter")
    SPECIAL_OFFERS = (By.CSS_SELECTOR, "#optin")
    REGISTER_BTN = (By.CSS_SELECTOR, "#submitAccount")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")
    ACCOUNT_LINK = (By.CSS_SELECTOR, "a.account")
    LOGOUT_LINK = (By.CSS_SELECTOR, "a.logout")
    EMAIL_CREATE = (By.CSS_SELECTOR, "#email_create")
    CREATE_ACCOUNT_BTN = (By.CSS_SELECTOR, "#SubmitCreate")

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== NAVIGATION ====================
    def navigate(self) -> "RegistrationPage":
        """Navigate to registration page. Gets URL from WebInterface config."""
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/index.php?controller=authentication")
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================
    def enter_email_for_create(self, email: str) -> "RegistrationPage":
        """Enter email in create account section."""
        self.web.type_text(*self.EMAIL_CREATE, email)
        return self

    def click_create_account(self) -> "RegistrationPage":
        """Click create account button."""
        self.web.click(*self.CREATE_ACCOUNT_BTN)
        return self

    def select_gender_mr(self) -> "RegistrationPage":
        """Select Mr. gender option."""
        self.web.click(*self.GENDER_MR)
        return self

    def select_gender_mrs(self) -> "RegistrationPage":
        """Select Mrs. gender option."""
        self.web.click(*self.GENDER_MRS)
        return self

    def enter_first_name(self, text: str) -> "RegistrationPage":
        """Enter first name."""
        self.web.type_text(*self.FIRST_NAME, text)
        return self

    def enter_last_name(self, text: str) -> "RegistrationPage":
        """Enter last name."""
        self.web.type_text(*self.LAST_NAME, text)
        return self

    def enter_email(self, text: str) -> "RegistrationPage":
        """Enter email in registration form."""
        self.web.type_text(*self.EMAIL, text)
        return self

    def enter_password(self, text: str) -> "RegistrationPage":
        """Enter password."""
        self.web.type_text(*self.PASSWORD, text)
        return self

    def select_birth_day(self, day: str) -> "RegistrationPage":
        """Select birth day from dropdown."""
        self.web.select_by_visible_text(*self.BIRTH_DAY, day)
        return self

    def select_birth_month(self, month: str) -> "RegistrationPage":
        """Select birth month from dropdown."""
        self.web.select_by_visible_text(*self.BIRTH_MONTH, month)
        return self

    def select_birth_year(self, year: str) -> "RegistrationPage":
        """Select birth year from dropdown."""
        self.web.select_by_visible_text(*self.BIRTH_YEAR, year)
        return self

    def check_newsletter(self) -> "RegistrationPage":
        """Check newsletter checkbox."""
        self.web.click(*self.NEWSLETTER)
        return self

    def check_special_offers(self) -> "RegistrationPage":
        """Check special offers checkbox."""
        self.web.click(*self.SPECIAL_OFFERS)
        return self

    def click_register(self) -> "RegistrationPage":
        """Click register button."""
        self.web.click(*self.REGISTER_BTN)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================
    def is_page_loaded(self) -> bool:
        """Check if registration page is loaded."""
        return self.web.is_element_displayed(*self.EMAIL_CREATE, timeout=5)

    def is_registration_form_displayed(self) -> bool:
        """Check if registration form is displayed after email entry."""
        return self.web.is_element_displayed(*self.FIRST_NAME, timeout=5)

    def is_account_created(self) -> bool:
        """Check if account was successfully created."""
        return self.web.is_element_displayed(*self.ACCOUNT_LINK, timeout=5)

    def is_logged_in(self) -> bool:
        """Check if user is logged in (logout link visible)."""
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)

    def is_error_displayed(self) -> bool:
        """Check if error message is displayed."""
        return self.web.is_element_displayed(*self.ERROR_MESSAGE, timeout=3)

    def get_error_message(self) -> str:
        """Get the error message text."""
        return self.web.get_text(*self.ERROR_MESSAGE)

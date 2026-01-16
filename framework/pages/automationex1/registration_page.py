"""
RegistrationPage - Page Object Model

Page Object for the user registration form.
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

    # ==================== LOCATORS (Class Constants) ====================
    TITLE_MR = (By.CSS_SELECTOR, "input[value='Mr']")
    TITLE_MRS = (By.CSS_SELECTOR, "input[value='Mrs']")
    PASSWORD = (By.CSS_SELECTOR, "input[data-qa='password']")
    DAY = (By.CSS_SELECTOR, "select[data-qa='days']")
    MONTH = (By.CSS_SELECTOR, "select[data-qa='months']")
    YEAR = (By.CSS_SELECTOR, "select[data-qa='years']")
    FIRST_NAME = (By.CSS_SELECTOR, "input[data-qa='first_name']")
    LAST_NAME = (By.CSS_SELECTOR, "input[data-qa='last_name']")
    ADDRESS = (By.CSS_SELECTOR, "input[data-qa='address']")
    COUNTRY = (By.CSS_SELECTOR, "select[data-qa='country']")
    STATE = (By.CSS_SELECTOR, "input[data-qa='state']")
    CITY = (By.CSS_SELECTOR, "input[data-qa='city']")
    ZIPCODE = (By.CSS_SELECTOR, "input[data-qa='zipcode']")
    MOBILE = (By.CSS_SELECTOR, "input[data-qa='mobile_number']")
    CREATE_ACCOUNT_BTN = (By.CSS_SELECTOR, "button[data-qa='create-account']")
    ACCOUNT_CREATED_HEADING = (By.CSS_SELECTOR, "h2.title")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".col-sm-9.col-sm-offset-1 p")
    CONTINUE_BTN = (By.CSS_SELECTOR, "a[data-qa='continue-button']")

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== NAVIGATION ====================
    def navigate(self) -> "RegistrationPage":
        """Navigate to registration page. Gets URL from WebInterface config."""
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/signup")
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================
    def click_title_mr(self) -> "RegistrationPage":
        """Select Mr title radio button."""
        self.web.click(*self.TITLE_MR)
        return self

    def click_title_mrs(self) -> "RegistrationPage":
        """Select Mrs title radio button."""
        self.web.click(*self.TITLE_MRS)
        return self

    def enter_password(self, text: str) -> "RegistrationPage":
        """Enter password."""
        self.web.type_text(*self.PASSWORD, text)
        return self

    def select_day(self, value: str) -> "RegistrationPage":
        """Select day from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.DAY, value)
        return self

    def select_month(self, value: str) -> "RegistrationPage":
        """Select month from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.MONTH, value)
        return self

    def select_year(self, value: str) -> "RegistrationPage":
        """Select year from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.YEAR, value)
        return self

    def enter_first_name(self, text: str) -> "RegistrationPage":
        """Enter first name."""
        self.web.type_text(*self.FIRST_NAME, text)
        return self

    def enter_last_name(self, text: str) -> "RegistrationPage":
        """Enter last name."""
        self.web.type_text(*self.LAST_NAME, text)
        return self

    def enter_address(self, text: str) -> "RegistrationPage":
        """Enter address."""
        self.web.type_text(*self.ADDRESS, text)
        return self

    def select_country(self, value: str) -> "RegistrationPage":
        """Select country from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.COUNTRY, value)
        return self

    def enter_state(self, text: str) -> "RegistrationPage":
        """Enter state."""
        self.web.type_text(*self.STATE, text)
        return self

    def enter_city(self, text: str) -> "RegistrationPage":
        """Enter city."""
        self.web.type_text(*self.CITY, text)
        return self

    def enter_zipcode(self, text: str) -> "RegistrationPage":
        """Enter zipcode."""
        self.web.type_text(*self.ZIPCODE, text)
        return self

    def enter_mobile(self, text: str) -> "RegistrationPage":
        """Enter mobile number."""
        self.web.type_text(*self.MOBILE, text)
        return self

    def click_create_account_btn(self) -> "RegistrationPage":
        """Click create account button."""
        self.web.click(*self.CREATE_ACCOUNT_BTN)
        return self

    def click_continue_btn(self) -> "RegistrationPage":
        """Click continue button on success page."""
        self.web.click(*self.CONTINUE_BTN)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================
    def is_page_loaded(self) -> bool:
        """Check if registration form is visible."""
        return self.web.is_element_displayed(*self.PASSWORD, timeout=5)

    def is_registration_successful(self) -> bool:
        """Check if registration was successful (success heading visible)."""
        return self.web.is_element_displayed(*self.ACCOUNT_CREATED_HEADING, timeout=10)

    def get_success_heading(self) -> str:
        """Get the success heading text."""
        return self.web.get_text(*self.ACCOUNT_CREATED_HEADING)

    def get_success_message(self) -> str:
        """Get the success message text."""
        return self.web.get_text(*self.SUCCESS_MESSAGE)

    def is_logged_in(self) -> bool:
        """Check if user is logged in (logout link visible in header)."""
        logout_link = (By.CSS_SELECTOR, "a[href='/logout']")
        return self.web.is_element_displayed(*logout_link, timeout=3)

    def is_product_in_cart(self) -> bool:
        """Check if products exist in cart (cart badge visible)."""
        cart_badge = (By.CSS_SELECTOR, ".cart .badge")
        return self.web.is_element_displayed(*cart_badge, timeout=3)

    def has_cart_items(self) -> bool:
        """Check if cart has items (cart count > 0)."""
        cart_badge = (By.CSS_SELECTOR, ".cart .badge")
        if not self.web.is_element_displayed(*cart_badge, timeout=3):
            return False
        try:
            count_text = self.web.get_text(*cart_badge)
            return int(count_text) > 0
        except (ValueError, Exception):
            return False

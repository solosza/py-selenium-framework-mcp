"""
Registration Page - Account registration form page object.

URL: http://www.automationpractice.pl/index.php?controller=authentication&account_creation
"""

from selenium.webdriver.common.by import By
from typing import Dict, Any, Optional
from pages.base_page import BasePage
from interfaces.web_interface import WebInterface


class RegistrationPage(BasePage):
    """
    Page Object for the Account Registration form.

    This page contains:
    - Personal information fields (title, name, email, password, DOB)
    - Address information fields
    - Contact information fields
    - Newsletter/offers preferences
    - Form submission
    """

    def __init__(self, web: WebInterface):
        """
        Initialize RegistrationPage.

        Args:
            web: WebInterface instance
        """
        super().__init__(web)

    # ==================== LOCATORS ====================

    # Personal Information
    GENDER_MR = (By.ID, "id_gender1")
    GENDER_MRS = (By.ID, "id_gender2")
    CUSTOMER_FIRSTNAME = (By.ID, "customer_firstname")
    CUSTOMER_LASTNAME = (By.ID, "customer_lastname")
    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "passwd")

    # Date of Birth
    DAY = (By.ID, "days")
    MONTH = (By.ID, "months")
    YEAR = (By.ID, "years")

    # Newsletter & Offers
    NEWSLETTER = (By.ID, "newsletter")
    SPECIAL_OFFERS = (By.ID, "optin")

    # Address Information
    ADDRESS_FIRSTNAME = (By.ID, "firstname")
    ADDRESS_LASTNAME = (By.ID, "lastname")
    COMPANY = (By.ID, "company")
    ADDRESS1 = (By.ID, "address1")
    ADDRESS2 = (By.ID, "address2")
    CITY = (By.ID, "city")
    STATE = (By.ID, "id_state")
    POSTCODE = (By.ID, "postcode")
    COUNTRY = (By.ID, "id_country")
    ADDITIONAL_INFO = (By.ID, "other")

    # Contact Information
    HOME_PHONE = (By.ID, "phone")
    MOBILE_PHONE = (By.ID, "phone_mobile")

    # Address Alias
    ALIAS = (By.ID, "alias")

    # Submit
    SUBMIT_ACCOUNT = (By.ID, "submitAccount")

    # Success/Error Messages
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".alert-success")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")
    ERROR_LIST = (By.CSS_SELECTOR, ".alert-danger ol li")

    # ==================== PERSONAL INFORMATION METHODS ====================

    def select_gender_mr(self) -> "RegistrationPage":
        """Select 'Mr.' title."""
        self.web.click(*self.GENDER_MR)
        return self

    def select_gender_mrs(self) -> "RegistrationPage":
        """Select 'Mrs.' title."""
        self.web.click(*self.GENDER_MRS)
        return self

    def select_gender(self, gender: str):
        """
        Select gender/title by name.

        Args:
            gender: 'mr' or 'mrs' (case-insensitive)

        Returns:
            self for method chaining
        """
        gender_lower = gender.lower()
        if gender_lower in ['mr', 'mr.', 'male', '1']:
            self.select_gender_mr()
        elif gender_lower in ['mrs', 'mrs.', 'female', '2']:
            self.select_gender_mrs()
        else:
            raise ValueError(f"Invalid gender value: {gender}. Use 'mr' or 'mrs'.")
        return self

    def select_title(self, title: str):
        """
        Select title (Mr/Mrs) - alias for select_gender().

        Args:
            title: 'Mr' or 'Mrs' (case-insensitive)

        Returns:
            self for method chaining
        """
        return self.select_gender(title)

    def enter_customer_firstname(self, firstname: str) -> "RegistrationPage":
        """
        Enter customer first name.

        Args:
            firstname: First name
        """
        self.web.type_text(*self.CUSTOMER_FIRSTNAME, text=firstname)
        return self

    def enter_customer_lastname(self, lastname: str) -> "RegistrationPage":
        """
        Enter customer last name.

        Args:
            lastname: Last name
        """
        self.web.type_text(*self.CUSTOMER_LASTNAME, text=lastname)
        return self

    def enter_password(self, password: str) -> "RegistrationPage":
        """
        Enter password.

        Args:
            password: Password (min 5 characters)
        """
        self.web.type_text(*self.PASSWORD, text=password)
        return self

    # ==================== WRAPPER METHODS (Test-Friendly Names) ====================

    def enter_first_name(self, first_name: str):
        """Wrapper for enter_customer_firstname - test-friendly name."""
        return self.enter_customer_firstname(first_name)

    def enter_last_name(self, last_name: str):
        """Wrapper for enter_customer_lastname - test-friendly name."""
        return self.enter_customer_lastname(last_name)

    def enter_address(self, address: str):
        """Wrapper for enter_address1 - test-friendly name."""
        return self.enter_address1(address)

    def enter_zip_code(self, zip_code: str):
        """Wrapper for enter_postcode - test-friendly name."""
        return self.enter_postcode(zip_code)

    # ==================== ORIGINAL METHODS ====================

    def select_date_of_birth(self, day: str, month: str, year: str):
        """
        Select date of birth.

        Args:
            day: Day (1-31)
            month: Month name (January, February, etc.) or number (1-12)
            year: Year (e.g., 1990)
        """
        self.web.select_dropdown_by_value(*self.DAY, option_value=str(day))

        # Handle month as number or name
        if month.isdigit():
            self.web.select_dropdown_by_value(*self.MONTH, option_value=str(month))
        else:
            self.web.select_dropdown_by_visible_text(*self.MONTH, text=month)

        self.web.select_dropdown_by_value(*self.YEAR, option_value=str(year))
        return self

    def check_newsletter(self) -> "RegistrationPage":
        """Check the newsletter checkbox."""
        if not self.is_newsletter_checked():
            self.web.click(*self.NEWSLETTER)
        return self

    def uncheck_newsletter(self) -> "RegistrationPage":
        """Uncheck the newsletter checkbox."""
        if self.is_newsletter_checked():
            self.web.click(*self.NEWSLETTER)
        return self

    def check_special_offers(self) -> "RegistrationPage":
        """Check the special offers checkbox."""
        if not self.is_special_offers_checked():
            self.web.click(*self.SPECIAL_OFFERS)
        return self

    def uncheck_special_offers(self) -> "RegistrationPage":
        """Uncheck the special offers checkbox."""
        if self.is_special_offers_checked():
            self.web.click(*self.SPECIAL_OFFERS)
        return self

    def is_newsletter_checked(self) -> bool:
        """
        Check if newsletter checkbox is selected.

        Returns:
            True if checked
        """
        checkbox = self.web.find_element(*self.NEWSLETTER)
        return checkbox.is_selected()

    def is_special_offers_checked(self) -> bool:
        """
        Check if special offers checkbox is selected.

        Returns:
            True if checked
        """
        checkbox = self.web.find_element(*self.SPECIAL_OFFERS)
        return checkbox.is_selected()

    # ==================== ADDRESS INFORMATION METHODS ====================

    def enter_address_firstname(self, firstname: str) -> "RegistrationPage":
        """
        Enter first name for address.

        Args:
            firstname: First name
        """
        self.web.type_text(*self.ADDRESS_FIRSTNAME, text=firstname)
        return self

    def enter_address_lastname(self, lastname: str) -> "RegistrationPage":
        """
        Enter last name for address.

        Args:
            lastname: Last name
        """
        self.web.type_text(*self.ADDRESS_LASTNAME, text=lastname)
        return self

    def enter_company(self, company: str) -> "RegistrationPage":
        """
        Enter company name (optional).

        Args:
            company: Company name
        """
        self.web.type_text(*self.COMPANY, text=company)
        return self

    def enter_address1(self, address: str):
        """
        Enter address line 1.

        Args:
            address: Street address

        Returns:
            self for method chaining
        """
        self.web.type_text(*self.ADDRESS1, text=address)
        return self

    def enter_address2(self, address: str) -> "RegistrationPage":
        """
        Enter address line 2 (optional).

        Args:
            address: Additional address info
        """
        self.web.type_text(*self.ADDRESS2, text=address)
        return self

    def enter_city(self, city: str) -> "RegistrationPage":
        """
        Enter city.

        Args:
            city: City name
        """
        self.web.type_text(*self.CITY, text=city)
        return self

    def select_state(self, state: str) -> "RegistrationPage":
        """
        Select state from dropdown.

        Args:
            state: State name (e.g., "Alabama", "Alaska")
        """
        self.web.select_dropdown_by_visible_text(*self.STATE, text=state)
        return self

    def enter_postcode(self, postcode: str) -> "RegistrationPage":
        """
        Enter postal/zip code.

        Args:
            postcode: Zip/postal code (5 digits for US)
        """
        self.web.type_text(*self.POSTCODE, text=postcode)
        return self

    def select_country(self, country: str) -> "RegistrationPage":
        """
        Select country from dropdown.

        Args:
            country: Country name (e.g., "United States")
        """
        self.web.select_dropdown_by_visible_text(*self.COUNTRY, text=country)
        return self

    def enter_additional_info(self, info: str) -> "RegistrationPage":
        """
        Enter additional information (optional).

        Args:
            info: Additional information text
        """
        self.web.type_text(*self.ADDITIONAL_INFO, text=info)
        return self

    # ==================== CONTACT INFORMATION METHODS ====================

    def enter_home_phone(self, phone: str) -> "RegistrationPage":
        """
        Enter home phone number (optional).

        Args:
            phone: Home phone number
        """
        self.web.type_text(*self.HOME_PHONE, text=phone)
        return self

    def enter_mobile_phone(self, phone: str) -> "RegistrationPage":
        """
        Enter mobile phone number (required).

        Args:
            phone: Mobile phone number
        """
        self.web.type_text(*self.MOBILE_PHONE, text=phone)
        return self

    # ==================== ADDRESS ALIAS METHODS ====================

    def enter_address_alias(self, alias: str) -> "RegistrationPage":
        """
        Enter address alias.

        Args:
            alias: Address alias (e.g., "Home", "Work")
        """
        self.web.type_text(*self.ALIAS, text=alias, clear_first=True)
        return self

    # ==================== FORM SUBMISSION METHODS ====================

    def click_register(self):
        """
        Click the Register button to submit registration form.

        Returns:
            self for method chaining
        """
        self.web.click(*self.SUBMIT_ACCOUNT)
        return self

    # NOTE: Composite methods (fill_registration_form, register_user) removed.
    # These belong in the Task layer, not POM. See DEF-001 in DEFECT_LOG.md.

    # ==================== ERROR & SUCCESS MESSAGE METHODS ====================

    def has_error_message(self) -> bool:
        """
        Check if error message is displayed.

        Returns:
            True if error message container is visible
        """
        return self.web.is_element_displayed(*self.ERROR_MESSAGE, timeout=5)

    def has_success_message(self) -> bool:
        """
        Check if success message is displayed.

        Returns:
            True if success message container is visible
        """
        return self.web.is_element_displayed(*self.SUCCESS_MESSAGE, timeout=5)

    def get_error_message(self) -> str:
        """
        Get error message text.

        Returns:
            Error message text (all errors concatenated if multiple)
        """
        if not self.has_error_message():
            return ""

        try:
            # Try to get individual error items from list
            error_items = self.web.find_elements(*self.ERROR_LIST)
            if error_items:
                errors = [item.text for item in error_items]
                return "; ".join(errors)

            # Fallback: get entire error container text
            return self.web.get_text(*self.ERROR_MESSAGE)
        except Exception:
            return ""

    def get_success_message(self) -> str:
        """
        Get success message text.

        Returns:
            Success message text
        """
        if not self.has_success_message():
            return ""

        return self.web.get_text(*self.SUCCESS_MESSAGE)

    # ==================== VALIDATION METHODS ====================

    def is_page_loaded(self) -> bool:
        """
        Verify registration form page is loaded.

        Returns:
            True if submit account button is visible
        """
        return self.web.is_element_displayed(*self.SUBMIT_ACCOUNT, timeout=5)

    def get_email_value(self) -> str:
        """
        Get email field value (pre-filled, read-only).

        Returns:
            Email address
        """
        return self.web.get_attribute(*self.EMAIL, attribute="value") or ""

    def is_email_readonly(self) -> bool:
        """
        Check if email field is read-only.

        Returns:
            True if email field is disabled/readonly
        """
        readonly_attr = self.web.get_attribute(*self.EMAIL, attribute="readonly")
        disabled_attr = self.web.get_attribute(*self.EMAIL, attribute="disabled")
        return bool(readonly_attr or disabled_attr)

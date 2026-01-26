"""
CustomerFormPage - Page Object Model for Inquiry Wizard Step 2

Handles customer details form in the New Inquiry wizard.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class CustomerFormPage:
    """
    Page Object for Customer Form (Step 2 of Inquiry Wizard).

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
    TITLE_SELECT = (By.CSS_SELECTOR, "[aria-label='customer_add_input_title']")
    FIRST_NAME_INPUT = (By.CSS_SELECTOR, "[aria-label='customer_add_input_firstname']")
    MIDDLE_NAME_INPUT = (By.CSS_SELECTOR, "[aria-label='customer_add_input_middlename']")
    LAST_NAME_INPUT = (By.CSS_SELECTOR, "[aria-label='customer_add_input_lastname']")
    COMPANY_INPUT = (By.CSS_SELECTOR, "[aria-label='customer_add_input_company']")
    REFERENCE_NUMBER_INPUT = (By.CSS_SELECTOR, "[aria-label='customer_add_input_referencenumber']")
    ASSIGNED_USER_SELECT = (By.CSS_SELECTOR, "[aria-label='customer_add_input_assigneduserid']")
    PREVIOUS_BUTTON = (By.CSS_SELECTOR, "[aria-label='customer_add button_previous']")
    NEXT_BUTTON = (By.CSS_SELECTOR, "[aria-label='customer_add_button_submit']")

    # Output elements
    VALIDATION_ALERT = (By.CSS_SELECTOR, "[aria-label='alert_message_validation']")
    ALERT_CLOSE_BUTTON = (By.CSS_SELECTOR, "[aria-label='alert_close']")

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def wait_for_form_visible(self, timeout: int = 10) -> "CustomerFormPage":
        """Wait for customer form to be visible."""
        self.web.wait_for_element_visible(*self.FIRST_NAME_INPUT, timeout=timeout)
        return self

    def select_title(self, value: str) -> "CustomerFormPage":
        """Select title from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.TITLE_SELECT, value)
        return self

    def enter_middle_name(self, text: str) -> "CustomerFormPage":
        """Enter middle name."""
        self.web.type_text(*self.MIDDLE_NAME_INPUT, text)
        return self

    def enter_company(self, text: str) -> "CustomerFormPage":
        """Enter company name."""
        self.web.type_text(*self.COMPANY_INPUT, text)
        return self

    def enter_reference_number(self, text: str) -> "CustomerFormPage":
        """Enter reference number."""
        self.web.type_text(*self.REFERENCE_NUMBER_INPUT, text)
        return self

    def select_assigned_user(self, value: str) -> "CustomerFormPage":
        """Select assigned user from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.ASSIGNED_USER_SELECT, value)
        return self

    def click_previous(self) -> "CustomerFormPage":
        """Click previous button."""
        self.web.click(*self.PREVIOUS_BUTTON)
        return self

    def click_next(self) -> "CustomerFormPage":
        """Click next button."""
        self.web.click(*self.NEXT_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_form_displayed(self) -> bool:
        """Check if customer form is displayed."""
        return self.web.is_element_displayed(*self.FIRST_NAME_INPUT, timeout=5)

    def is_validation_error_displayed(self) -> bool:
        """Check if validation error alert is displayed."""
        return self.web.is_element_displayed(*self.VALIDATION_ALERT, timeout=3)

    def get_first_name(self) -> str:
        """Get first name value."""
        return self.web.get_attribute(*self.FIRST_NAME_INPUT, "value")

    def get_last_name(self) -> str:
        """Get last name value."""
        return self.web.get_attribute(*self.LAST_NAME_INPUT, "value")

"""
AddressFormPage - Page Object Model for Inquiry Wizard Step 4

Handles address form in the New Inquiry wizard.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class AddressFormPage:
    """
    Page Object for Address Form (Step 4 of Inquiry Wizard).

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
    TYPE_UNKNOWN_CHECKBOX = (By.CSS_SELECTOR, "[aria-label='address_add_input_type']:nth-of-type(1)")
    TYPE_BILLING_CHECKBOX = (By.CSS_SELECTOR, "[aria-label='address_add_input_type']:nth-of-type(2)")
    TYPE_MAILING_CHECKBOX = (By.CSS_SELECTOR, "[aria-label='address_add_input_type']:nth-of-type(3)")
    TYPE_DELIVERY_CHECKBOX = (By.CSS_SELECTOR, "[aria-label='address_add_input_type']:nth-of-type(4)")
    NAME_INPUT = (By.CSS_SELECTOR, "[aria-label='address_add_input_name']")
    LINE1_INPUT = (By.CSS_SELECTOR, "[aria-label='address_add_input_line1']")
    LINE2_INPUT = (By.CSS_SELECTOR, "[aria-label='address_add_input_line2']")
    LINE3_INPUT = (By.CSS_SELECTOR, "[aria-label='address_add_input_line3']")
    CITY_INPUT = (By.CSS_SELECTOR, "[aria-label='address_add_input_city']")
    POSTAL_CODE_INPUT = (By.CSS_SELECTOR, "[aria-label='address_add_input_postalcode']")
    COUNTRY_SELECT = (By.CSS_SELECTOR, "[aria-label='address_add_input_country']")
    PREVIOUS_BUTTON = (By.CSS_SELECTOR, "[aria-label='address_add button_previous']")
    NEXT_BUTTON = (By.CSS_SELECTOR, "[aria-label='address_add_button_submit']")

    # Output elements
    VALIDATION_ALERT = (By.CSS_SELECTOR, "[aria-label='alert_message_validation']")
    ALERT_CLOSE_BUTTON = (By.CSS_SELECTOR, "[aria-label='alert_close']")

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def wait_for_form_visible(self, timeout: int = 10) -> "AddressFormPage":
        """Wait for address form to be visible."""
        self.web.wait_for_element_visible(*self.NEXT_BUTTON, timeout=timeout)
        return self

    def enter_name(self, text: str) -> "AddressFormPage":
        """Enter address name."""
        self.web.type_text(*self.NAME_INPUT, text)
        return self

    def enter_line1(self, text: str) -> "AddressFormPage":
        """Enter address line 1."""
        self.web.type_text(*self.LINE1_INPUT, text)
        return self

    def enter_line2(self, text: str) -> "AddressFormPage":
        """Enter address line 2."""
        self.web.type_text(*self.LINE2_INPUT, text)
        return self

    def enter_line3(self, text: str) -> "AddressFormPage":
        """Enter address line 3."""
        self.web.type_text(*self.LINE3_INPUT, text)
        return self

    def enter_city(self, text: str) -> "AddressFormPage":
        """Enter city."""
        self.web.type_text(*self.CITY_INPUT, text)
        return self

    def enter_postal_code(self, text: str) -> "AddressFormPage":
        """Enter postal code."""
        self.web.type_text(*self.POSTAL_CODE_INPUT, text)
        return self

    def select_country(self, value: str) -> "AddressFormPage":
        """Select country from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.COUNTRY_SELECT, value)
        return self

    def click_previous(self) -> "AddressFormPage":
        """Click previous button."""
        self.web.click(*self.PREVIOUS_BUTTON)
        return self

    def click_next(self) -> "AddressFormPage":
        """Click next button."""
        self.web.click(*self.NEXT_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_form_displayed(self) -> bool:
        """Check if address form is displayed."""
        return self.web.is_element_displayed(*self.NEXT_BUTTON, timeout=5)

    def is_validation_error_displayed(self) -> bool:
        """Check if validation error alert is displayed."""
        return self.web.is_element_displayed(*self.VALIDATION_ALERT, timeout=3)

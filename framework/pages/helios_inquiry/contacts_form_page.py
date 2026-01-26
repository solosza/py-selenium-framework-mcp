"""
ContactsFormPage - Page Object Model for Inquiry Wizard Step 3

Handles contacts form in the New Inquiry wizard.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class ContactsFormPage:
    """
    Page Object for Contacts Form (Step 3 of Inquiry Wizard).

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
    CONTACT_TYPE_SELECT = (By.CSS_SELECTOR, "[aria-label='contact_add_input_type']")
    CONTACT_IDENTIFIER_INPUT = (By.CSS_SELECTOR, "[aria-label='contact_add_input_identifier']")
    IS_PREFERRED_RADIO = (By.CSS_SELECTOR, "[aria-label='contact_add_input_ispreferred']")
    ADD_CONTACT_BUTTON = (By.CSS_SELECTOR, "[aria-label='contact_add_button_add']")
    PREVIOUS_BUTTON = (By.CSS_SELECTOR, "[aria-label='contact_add button_previous']")
    NEXT_BUTTON = (By.CSS_SELECTOR, "[aria-label='contact_add_button_submit']")

    # Output elements
    VALIDATION_ALERT = (By.CSS_SELECTOR, "[aria-label='alert_message_validation']")
    ALERT_CLOSE_BUTTON = (By.CSS_SELECTOR, "[aria-label='alert_close']")

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def wait_for_form_visible(self, timeout: int = 10) -> "ContactsFormPage":
        """Wait for contacts form to be visible."""
        self.web.wait_for_element_visible(*self.CONTACT_IDENTIFIER_INPUT, timeout=timeout)
        return self

    def enter_contact_identifier(self, text: str) -> "ContactsFormPage":
        """Enter contact identifier."""
        self.web.clear_and_type(*self.CONTACT_IDENTIFIER_INPUT, text)
        return self

    def click_add_contact(self) -> "ContactsFormPage":
        """Click add contact button."""
        self.web.click(*self.ADD_CONTACT_BUTTON)
        return self

    def click_previous(self) -> "ContactsFormPage":
        """Click previous button."""
        self.web.click(*self.PREVIOUS_BUTTON)
        return self

    def click_next(self) -> "ContactsFormPage":
        """Click next button."""
        self.web.click(*self.NEXT_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_form_displayed(self) -> bool:
        """Check if contacts form is displayed."""
        return self.web.is_element_displayed(*self.CONTACT_IDENTIFIER_INPUT, timeout=5)

    def is_validation_error_displayed(self) -> bool:
        """Check if validation error alert is displayed."""
        return self.web.is_element_displayed(*self.VALIDATION_ALERT, timeout=3)

    def get_contact_identifier(self) -> str:
        """Get contact identifier value."""
        return self.web.get_attribute(*self.CONTACT_IDENTIFIER_INPUT, "value")

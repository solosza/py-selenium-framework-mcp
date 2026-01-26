"""
CustomerSearchPage - Page Object Model for Inquiry Wizard Step 1

Handles customer search form in the New Inquiry wizard.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class CustomerSearchPage:
    """
    Page Object for Customer Search (Step 1 of Inquiry Wizard).

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
    NEW_INQUIRY_BUTTON = (By.CSS_SELECTOR, "[aria-label='inquiry_view_button_add']")
    FIRST_NAME_INPUT = (By.CSS_SELECTOR, "[aria-label='customer_search_input_firstname']")
    LAST_NAME_INPUT = (By.CSS_SELECTOR, "[aria-label='customer_search_input_lastname']")
    CONTACT_TYPE_SELECT = (By.CSS_SELECTOR, "[aria-label='contact_search_input_type']")
    CONTACT_IDENTIFIER_INPUT = (By.CSS_SELECTOR, "[aria-label='contact_search_input_identifier']")
    NEXT_BUTTON = (By.CSS_SELECTOR, "[aria-label='customer_search_button_next']")
    CANCEL_BUTTON = (By.CSS_SELECTOR, "[aria-label='customer_search button_cancel']")
    CLOSE_BUTTON = (By.CSS_SELECTOR, "[aria-label='customer_add_button_close']")

    # Output elements
    VALIDATION_ALERT = (By.CSS_SELECTOR, "[aria-label='alert_message_validation']")
    ALERT_CLOSE_BUTTON = (By.CSS_SELECTOR, "[aria-label='alert_close']")

    # ==================== NAVIGATION ====================

    def navigate(self) -> "CustomerSearchPage":
        """Navigate to inquiries page."""
        self.web.navigate_to(self.web.config['url'] + '/Portal/Inquiries')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def click_new_inquiry(self) -> "CustomerSearchPage":
        """Click new inquiry button to open wizard."""
        self.web.click(*self.NEW_INQUIRY_BUTTON)
        return self

    def wait_for_form_visible(self, timeout: int = 10) -> "CustomerSearchPage":
        """Wait for customer search form to be visible."""
        self.web.wait_for_element_visible(*self.FIRST_NAME_INPUT, timeout=timeout)
        return self

    def enter_first_name(self, text: str) -> "CustomerSearchPage":
        """Enter text into first name input."""
        self.web.type_text(*self.FIRST_NAME_INPUT, text)
        return self

    def enter_last_name(self, text: str) -> "CustomerSearchPage":
        """Enter text into last name input."""
        self.web.type_text(*self.LAST_NAME_INPUT, text)
        return self

    def select_contact_type(self, value: str) -> "CustomerSearchPage":
        """Select option from contact type dropdown."""
        self.web.select_dropdown_by_visible_text(*self.CONTACT_TYPE_SELECT, value)
        return self

    def enter_contact_identifier(self, text: str) -> "CustomerSearchPage":
        """Enter text into contact identifier input."""
        self.web.type_text(*self.CONTACT_IDENTIFIER_INPUT, text)
        return self

    def click_next(self) -> "CustomerSearchPage":
        """Click next button."""
        self.web.click(*self.NEXT_BUTTON)
        return self

    def click_cancel(self) -> "CustomerSearchPage":
        """Click cancel button."""
        self.web.click(*self.CANCEL_BUTTON)
        return self

    def click_close(self) -> "CustomerSearchPage":
        """Click close button."""
        self.web.click(*self.CLOSE_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_form_displayed(self) -> bool:
        """Check if search form is displayed."""
        return self.web.is_element_displayed(*self.FIRST_NAME_INPUT, timeout=5)

    def is_validation_error_displayed(self) -> bool:
        """Check if validation error alert is displayed."""
        return self.web.is_element_displayed(*self.VALIDATION_ALERT, timeout=3)

    def get_validation_message(self) -> str:
        """Get validation error message text."""
        return self.web.get_text(*self.VALIDATION_ALERT)

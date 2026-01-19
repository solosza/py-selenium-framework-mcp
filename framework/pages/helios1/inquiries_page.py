"""
InquiriesPage - Page Object Model

Page Object representing the Inquiries wizard flow in the application.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class InquiriesPage:
    """
    Page Object for Inquiries Page (5-step wizard).

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
    SEARCH_FIRSTNAME = (By.CSS_SELECTOR, "[aria-label='customer_search_input_firstname']")
    SEARCH_LASTNAME = (By.CSS_SELECTOR, "[aria-label='customer_search_input_lastname']")
    SEARCH_CONTACT_TYPE = (By.CSS_SELECTOR, "[aria-label='contact_search_input_type']")
    SEARCH_CONTACT_IDENTIFIER = (By.CSS_SELECTOR, "[aria-label='contact_search_input_identifier']")
    SEARCH_NEXT_BUTTON = (By.CSS_SELECTOR, "[aria-label='customer_search_button_next']")
    CUSTOMER_TITLE = (By.CSS_SELECTOR, "[aria-label='customer_add_input_title']")
    CUSTOMER_FIRSTNAME = (By.CSS_SELECTOR, "[aria-label='customer_add_input_firstname']")
    CUSTOMER_LASTNAME = (By.CSS_SELECTOR, "[aria-label='customer_add_input_lastname']")
    CUSTOMER_ASSIGNED_USER = (By.CSS_SELECTOR, "[aria-label='customer_add_input_assigneduserid']")
    CUSTOMER_SUBMIT_BUTTON = (By.CSS_SELECTOR, "[aria-label='customer_add_button_submit']")
    CONTACT_SUBMIT_BUTTON = (By.CSS_SELECTOR, "[aria-label='contact_add_button_submit']")
    ADDRESS_SUBMIT_BUTTON = (By.CSS_SELECTOR, "[aria-label='address_add_button_submit']")
    INQUIRY_TYPE = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_type']")
    INQUIRY_SOURCE = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_source']")
    INQUIRY_VEHICLE_NOTES = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_desiredvehicle']")
    INQUIRY_ASSIGNED_USER = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_assigneduserid']")
    INQUIRY_STATUS = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_status']")
    INQUIRY_COMPLETE_BUTTON = (By.CSS_SELECTOR, "[aria-label='inquiry_add_button_submit']")

    # ==================== NAVIGATION ====================
    def navigate(self) -> "InquiriesPage":
        """Navigate to Inquiries page."""
        self.web.navigate_to(self.web.config['url'] + '/Portal/Inquiries')
        import time
        time.sleep(5)
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================
    def click_new_inquiry_button(self) -> "InquiriesPage":
        """Click new inquiry button."""
        self.web.click(*self.NEW_INQUIRY_BUTTON)
        return self

    def enter_search_firstname(self, text: str) -> "InquiriesPage":
        """Enter search firstname."""
        self.web.type_text(*self.SEARCH_FIRSTNAME, text)
        return self

    def enter_search_lastname(self, text: str) -> "InquiriesPage":
        """Enter search lastname."""
        self.web.type_text(*self.SEARCH_LASTNAME, text)
        return self

    def select_search_contact_type(self, value: str) -> "InquiriesPage":
        """Select search contact type from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.SEARCH_CONTACT_TYPE, value)
        return self

    def enter_search_contact_identifier(self, text: str) -> "InquiriesPage":
        """Enter search contact identifier."""
        self.web.type_text(*self.SEARCH_CONTACT_IDENTIFIER, text)
        return self

    def click_search_next_button(self) -> "InquiriesPage":
        """Click search next button."""
        self.web.click(*self.SEARCH_NEXT_BUTTON)
        return self

    def select_customer_title(self, value: str) -> "InquiriesPage":
        """Select customer title from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.CUSTOMER_TITLE, value)
        return self

    def enter_customer_firstname(self, text: str) -> "InquiriesPage":
        """Enter customer firstname."""
        self.web.type_text(*self.CUSTOMER_FIRSTNAME, text)
        return self

    def enter_customer_lastname(self, text: str) -> "InquiriesPage":
        """Enter customer lastname."""
        self.web.type_text(*self.CUSTOMER_LASTNAME, text)
        return self

    def select_customer_assigned_user(self, value: str) -> "InquiriesPage":
        """Select customer assigned user from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.CUSTOMER_ASSIGNED_USER, value)
        return self

    def click_customer_submit_button(self) -> "InquiriesPage":
        """Click customer submit button."""
        self.web.click(*self.CUSTOMER_SUBMIT_BUTTON)
        return self

    def click_contact_submit_button(self) -> "InquiriesPage":
        """Click contact submit button."""
        self.web.click(*self.CONTACT_SUBMIT_BUTTON)
        return self

    def click_address_submit_button(self) -> "InquiriesPage":
        """Click address submit button."""
        self.web.click(*self.ADDRESS_SUBMIT_BUTTON)
        return self

    def select_inquiry_type(self, value: str) -> "InquiriesPage":
        """Select inquiry type from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.INQUIRY_TYPE, value)
        return self

    def select_inquiry_source(self, value: str) -> "InquiriesPage":
        """Select inquiry source from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.INQUIRY_SOURCE, value)
        return self

    def enter_inquiry_vehicle_notes(self, text: str) -> "InquiriesPage":
        """Enter inquiry vehicle notes."""
        self.web.type_text(*self.INQUIRY_VEHICLE_NOTES, text)
        return self

    def select_inquiry_assigned_user(self, value: str) -> "InquiriesPage":
        """Select inquiry assigned user from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.INQUIRY_ASSIGNED_USER, value)
        return self

    def select_inquiry_status(self, value: str) -> "InquiriesPage":
        """Select inquiry status from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.INQUIRY_STATUS, value)
        return self

    def click_inquiry_complete_button(self) -> "InquiriesPage":
        """Click inquiry complete button."""
        self.web.click(*self.INQUIRY_COMPLETE_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================
    def is_inquiry_created(self) -> bool:
        """Check if inquiry was created successfully."""
        table_locator = (By.CSS_SELECTOR, "table")
        return self.web.is_element_displayed(*table_locator, timeout=10)

    def is_inquiry_in_list(self) -> bool:
        """Check if inquiry appears in the inquiries list."""
        rows_locator = (By.CSS_SELECTOR, "tbody tr")
        return len(self.web.driver.find_elements(*rows_locator)) > 0

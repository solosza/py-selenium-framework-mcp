"""
InquiryFormPage - Page Object Model for Inquiry Wizard Step 5 + Confirmation

Handles inquiry form and confirmation display in the New Inquiry wizard.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class InquiryFormPage:
    """
    Page Object for Inquiry Form (Step 5 of Inquiry Wizard) and Confirmation.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== LOCATORS - FORM (Input) ====================
    INQUIRY_TYPE_SELECT = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_type']")
    INQUIRY_SOURCE_SELECT = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_source']")
    VEHICLE_NOTES_INPUT = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_desiredvehicle']")
    ASSIGNED_USER_SELECT = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_assigneduserid']")
    STATUS_SELECT = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_status']")
    PREVIOUS_BUTTON = (By.CSS_SELECTOR, "[aria-label='inquiry_add button_previous']")
    COMPLETE_BUTTON = (By.CSS_SELECTOR, "[aria-label='inquiry_add_button_submit']")

    # ==================== LOCATORS - CONFIRMATION (Output) ====================
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, "[aria-label='alert_message_validation']")
    ALERT_CLOSE_BUTTON = (By.CSS_SELECTOR, "[aria-label='alert_close']")
    INQUIRY_TITLE = (By.CSS_SELECTOR, "[aria-label='inquiry_view_title_inquiry']")
    CREATE_DATE_VALUE = (By.CSS_SELECTOR, "[aria-label='inquiry_view_value_createdate']")
    CUSTOMER_NAME_VALUE = (By.CSS_SELECTOR, "[aria-label='inquiry_view_value_customername']")
    CUSTOMER_CONTACT_VALUE = (By.CSS_SELECTOR, "[aria-label='inquiry_view_value_customercontact']")
    TYPE_VALUE = (By.CSS_SELECTOR, "[aria-label='inquiry_view_value_type']")
    SOURCE_VALUE = (By.CSS_SELECTOR, "[aria-label='inquiry_view_value_source']")
    ASSIGNED_USER_VALUE = (By.CSS_SELECTOR, "[aria-label='inquiry_view_value_assignedusername']")
    STATUS_VALUE = (By.CSS_SELECTOR, "[aria-label='inquiry_view_value_status']")
    EDIT_BUTTON = (By.CSS_SELECTOR, "[aria-label='inquiry_view_button_edit']")
    BACK_BUTTON = (By.CSS_SELECTOR, "[aria-label='inquiry_view_button_back']")
    DELETE_BUTTON = (By.CSS_SELECTOR, "[aria-label='inquiry_view_button_remove']")
    VIEW_CUSTOMER_LINK = (By.CSS_SELECTOR, "[aria-label='inquiry_view_button_customer']")

    # Notes section
    NOTE_CONTENT_INPUT = (By.CSS_SELECTOR, "[aria-label='note_add_value_content']")
    NOTE_SUBMIT_BUTTON = (By.CSS_SELECTOR, "[aria-label='note_add_button_submit']")

    # ==================== ATOMIC METHODS - FORM ====================

    def wait_for_form_visible(self, timeout: int = 10) -> "InquiryFormPage":
        """Wait for inquiry form to be visible."""
        self.web.wait_for_element_visible(*self.INQUIRY_TYPE_SELECT, timeout=timeout)
        return self

    def select_type(self, value: str) -> "InquiryFormPage":
        """Select inquiry type."""
        self.web.select_dropdown_by_visible_text(*self.INQUIRY_TYPE_SELECT, value)
        return self

    def select_source(self, value: str) -> "InquiryFormPage":
        """Select inquiry source."""
        self.web.select_dropdown_by_visible_text(*self.INQUIRY_SOURCE_SELECT, value)
        return self

    def enter_vehicle_notes(self, text: str) -> "InquiryFormPage":
        """Enter vehicle notes."""
        self.web.type_text(*self.VEHICLE_NOTES_INPUT, text)
        return self

    def select_assigned_user(self, value: str) -> "InquiryFormPage":
        """Select assigned user."""
        self.web.select_dropdown_by_visible_text(*self.ASSIGNED_USER_SELECT, value)
        return self

    def select_status(self, value: str) -> "InquiryFormPage":
        """Select inquiry status."""
        self.web.select_dropdown_by_visible_text(*self.STATUS_SELECT, value)
        return self

    def click_previous(self) -> "InquiryFormPage":
        """Click previous button."""
        self.web.click(*self.PREVIOUS_BUTTON)
        return self

    def click_complete(self) -> "InquiryFormPage":
        """Click complete button to submit inquiry."""
        self.web.click(*self.COMPLETE_BUTTON)
        return self

    # ==================== ATOMIC METHODS - CONFIRMATION ====================

    def click_back(self) -> "InquiryFormPage":
        """Click back button."""
        self.web.click(*self.BACK_BUTTON)
        return self

    def click_edit(self) -> "InquiryFormPage":
        """Click edit button."""
        self.web.click(*self.EDIT_BUTTON)
        return self

    def click_delete(self) -> "InquiryFormPage":
        """Click delete button."""
        self.web.click(*self.DELETE_BUTTON)
        return self

    def click_view_customer(self) -> "InquiryFormPage":
        """Click view customer link."""
        self.web.click(*self.VIEW_CUSTOMER_LINK)
        return self

    def enter_note(self, text: str) -> "InquiryFormPage":
        """Enter note content."""
        self.web.type_text(*self.NOTE_CONTENT_INPUT, text)
        return self

    def click_submit_note(self) -> "InquiryFormPage":
        """Click submit note button."""
        self.web.click(*self.NOTE_SUBMIT_BUTTON)
        return self

    def close_alert(self) -> "InquiryFormPage":
        """Close the success/validation alert."""
        self.web.click(*self.ALERT_CLOSE_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_form_displayed(self) -> bool:
        """Check if inquiry form is displayed."""
        return self.web.is_element_displayed(*self.INQUIRY_TYPE_SELECT, timeout=5)

    def is_inquiry_created(self) -> bool:
        """Check if inquiry was created successfully (success message displayed)."""
        return self.web.is_element_displayed(*self.SUCCESS_MESSAGE, timeout=10)

    def is_confirmation_displayed(self) -> bool:
        """Check if inquiry confirmation page is displayed."""
        return self.web.is_element_displayed(*self.CUSTOMER_NAME_VALUE, timeout=10)

    def get_success_message(self) -> str:
        """Get success message text."""
        return self.web.get_text(*self.SUCCESS_MESSAGE)

    def get_customer_name(self) -> str:
        """Get displayed customer name."""
        return self.web.get_text(*self.CUSTOMER_NAME_VALUE)

    def get_inquiry_type(self) -> str:
        """Get displayed inquiry type."""
        return self.web.get_text(*self.TYPE_VALUE)

    def get_inquiry_source(self) -> str:
        """Get displayed inquiry source."""
        return self.web.get_text(*self.SOURCE_VALUE)

    def get_inquiry_status(self) -> str:
        """Get displayed inquiry status."""
        return self.web.get_text(*self.STATUS_VALUE)

    def get_assigned_user(self) -> str:
        """Get displayed assigned user."""
        return self.web.get_text(*self.ASSIGNED_USER_VALUE)

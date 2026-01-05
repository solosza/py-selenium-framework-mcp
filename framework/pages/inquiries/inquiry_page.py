"""
Page Object for Inquiry Page - Helios Digital Retail Portal.

Handles multi-step wizard for creating new inquiries.
"""
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class InquiryPage:
    """Page Object for the Inquiries page with wizard workflow."""

    # ═══════════════════════════════════════════════════════════════════════════
    # LOCATORS - Class-level constants, UPPER_SNAKE_CASE
    # ═══════════════════════════════════════════════════════════════════════════

    # Main page elements
    NEW_INQUIRY_BUTTON = (By.CSS_SELECTOR, "[aria-label='inquiry_view_button_add']")
    INQUIRY_LIST_TABLE = (By.CSS_SELECTOR, "[aria-label='inquiry_view_grid']")

    # Step 1: Search - Customer and contact fields (all on same page)
    CUSTOMER_FIRSTNAME_INPUT = (By.CSS_SELECTOR, "[aria-label='customer_search_input_firstname']")
    CUSTOMER_LASTNAME_INPUT = (By.CSS_SELECTOR, "[aria-label='customer_search_input_lastname']")
    CONTACT_TYPE_SELECT = (By.CSS_SELECTOR, "[aria-label='contact_search_input_type']")
    CONTACT_IDENTIFIER_INPUT = (By.CSS_SELECTOR, "[aria-label='contact_search_input_identifier']")
    SEARCH_NEXT_BUTTON = (By.CSS_SELECTOR, "[aria-label='customer_search_button_next']")

    # Step 2: Customer - Next button
    CUSTOMER_NEXT_BUTTON = (By.CSS_SELECTOR, "[aria-label='customer_add_button_submit']")

    # Step 3: Contacts - Next button
    CONTACTS_NEXT_BUTTON = (By.CSS_SELECTOR, "[aria-label='contact_add_button_submit']")

    # Step 4: Address - Next button
    ADDRESS_NEXT_BUTTON = (By.CSS_SELECTOR, "[aria-label='address_add_button_submit']")

    # Step 5: Inquiry - Final form
    INQUIRY_TYPE_SELECT = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_type']")
    INQUIRY_SOURCE_SELECT = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_source']")
    INQUIRY_STATUS_SELECT = (By.CSS_SELECTOR, "[aria-label='inquiry_add_value_status']")
    COMPLETE_BUTTON = (By.CSS_SELECTOR, "[aria-label='inquiry_add_button_submit']")

    # Success indicators
    SUCCESS_ALERT = (By.CSS_SELECTOR, "[aria-label='alert_message_validation']")

    # ═══════════════════════════════════════════════════════════════════════════
    # CONSTRUCTOR - Compose WebInterface, NO inheritance
    # ═══════════════════════════════════════════════════════════════════════════
    def __init__(self, web: WebInterface):
        """Initialize with WebInterface composition."""
        self.web = web

    # ═══════════════════════════════════════════════════════════════════════════
    # NAVIGATION
    # ═══════════════════════════════════════════════════════════════════════════
    def navigate(self) -> "InquiryPage":
        """Navigate to the Inquiries page."""
        url = self.web.config.get("url", "https://heliosdigital-retail-qa.azurewebsites.net")
        self.web.navigate_to(f"{url}/Portal/Inquiries")
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # ATOMIC METHODS - One action per method, return self for chaining
    # ═══════════════════════════════════════════════════════════════════════════

    # Main page actions
    def click_new_inquiry(self) -> "InquiryPage":
        """Click the + New Inquiry button."""
        self.web.click_js(*self.NEW_INQUIRY_BUTTON)
        return self

    # Step 1: Search
    def enter_customer_firstname(self, text: str) -> "InquiryPage":
        """Enter customer first name in search."""
        self.web.type_text(*self.CUSTOMER_FIRSTNAME_INPUT, text)
        return self

    def enter_customer_lastname(self, text: str) -> "InquiryPage":
        """Enter customer last name in search."""
        self.web.type_text(*self.CUSTOMER_LASTNAME_INPUT, text)
        return self

    def click_search_next(self) -> "InquiryPage":
        """Click Next on search step."""
        self.web.click_js(*self.SEARCH_NEXT_BUTTON)
        return self

    # Step 2: Customer
    def select_contact_type(self, option: str) -> "InquiryPage":
        """Select contact type from dropdown."""
        self.web.select_dropdown_by_visible_text(*self.CONTACT_TYPE_SELECT, option)
        return self

    def enter_contact_identifier(self, text: str) -> "InquiryPage":
        """Enter contact identifier (email/phone)."""
        self.web.type_text(*self.CONTACT_IDENTIFIER_INPUT, text)
        return self

    def click_customer_next(self) -> "InquiryPage":
        """Click Next on customer details step."""
        self.web.click_js(*self.CUSTOMER_NEXT_BUTTON)
        return self

    # Step 3: Contacts
    def click_contacts_next(self) -> "InquiryPage":
        """Click Next on contacts step."""
        self.web.click_js(*self.CONTACTS_NEXT_BUTTON)
        return self

    # Step 4: Address
    def click_address_next(self) -> "InquiryPage":
        """Click Next on address step."""
        self.web.click_js(*self.ADDRESS_NEXT_BUTTON)
        return self

    # Step 5: Inquiry
    def select_inquiry_type(self, option: str) -> "InquiryPage":
        """Select inquiry type (e.g., New Vehicle)."""
        self.web.select_dropdown_by_visible_text(*self.INQUIRY_TYPE_SELECT, option)
        return self

    def select_inquiry_source(self, option: str) -> "InquiryPage":
        """Select inquiry source (e.g., Website)."""
        self.web.select_dropdown_by_visible_text(*self.INQUIRY_SOURCE_SELECT, option)
        return self

    def select_inquiry_status(self, option: str) -> "InquiryPage":
        """Select inquiry status (e.g., New)."""
        self.web.select_dropdown_by_visible_text(*self.INQUIRY_STATUS_SELECT, option)
        return self

    def click_complete(self) -> "InquiryPage":
        """Click Complete to submit the inquiry."""
        self.web.click_js(*self.COMPLETE_BUTTON)
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # STATE-CHECK METHODS - For test assertions, return bool
    # ═══════════════════════════════════════════════════════════════════════════
    def is_page_loaded(self) -> bool:
        """Check if the Inquiries page is loaded."""
        return self.web.is_element_displayed(*self.NEW_INQUIRY_BUTTON, timeout=10)

    def is_inquiry_created(self) -> bool:
        """Check if inquiry was created successfully (success alert appears)."""
        return self.web.is_element_displayed(*self.SUCCESS_ALERT, timeout=5)

    def is_inquiry_in_list(self) -> bool:
        """Check if inquiry list/grid is visible with entries."""
        return self.web.is_element_displayed(*self.INQUIRY_LIST_TABLE, timeout=5)

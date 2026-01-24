"""
InquiriesPage - Page Object Model

Page Object representing the Inquiries page where users can view and create inquiries.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class InquiriesPage:
    """
    Page Object for Inquiries Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    # ==================== LOCATORS (Class Constants) ====================
    NEW_INQUIRY_BTN = (By.CSS_SELECTOR, "[aria-label='inquiry_view_button_add']")

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== NAVIGATION ====================
    def navigate(self) -> "InquiriesPage":
        """Navigate to this page. Gets URL from WebInterface config."""
        self.web.navigate_to(self.web.config["url"] + "/Portal/Inquiries")
        # Wait for the New Inquiry button to be visible (page fully loaded)
        self.web.wait_for_element_visible(*self.NEW_INQUIRY_BTN, timeout=30)
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================
    def click_new_inquiry_btn(self) -> "InquiriesPage":
        """Click the New Inquiry button."""
        self.web.click(*self.NEW_INQUIRY_BTN)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================
    def is_inquiry_form_visible(self) -> bool:
        """Check if inquiry creation form is visible after clicking New Inquiry button."""
        # The inquiry wizard modal appears with a search step first
        return self.web.is_element_displayed(By.CSS_SELECTOR, "[aria-label='customer_add_button_close']", timeout=5)

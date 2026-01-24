"""
InquiriesPage - Page Object Model

Page Object representing a single page in the application.
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

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== LOCATORS (Class Constants) ====================
    NEW_INQUIRY_BTN = (By.ID, "inquiry_view_button_add")

    # ==================== NAVIGATION ====================

    def navigate(self) -> "InquiriesPage":
        """Navigate to Inquiries page."""
        self.web.navigate_to(self.web.config['url'] + '/Portal/Inquiries')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def click_new_inquiry_btn(self) -> "InquiriesPage":
        """Click the New Inquiry button."""
        self.web.click(*self.NEW_INQUIRY_BTN)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_new_inquiry_btn_clickable(self) -> bool:
        """Check if New Inquiry button is clickable."""
        return self.web.is_element_displayed(*self.NEW_INQUIRY_BTN, timeout=5)

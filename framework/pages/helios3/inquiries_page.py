"""
InquiriesPage - Page Object Model for Inquiries page.

Pages encapsulate UI element locators and provide atomic interaction methods.
This is Layer 1 of the 4-layer architecture (Page → Task → Role → Test).
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class InquiriesPage:
    """
    InquiriesPage - atomic UI interactions.

    - Locators as class constants (UPPER_SNAKE_CASE)
    - Atomic methods return self for chaining
    - NO @autologger (logging happens at Task/Role level)
    - NO inheritance (compose WebInterface directly)
    - State-check methods for test assertions (is_*/has_*/get_*)
    """

    def __init__(self, web: WebInterface):
        """
        Initialize page with WebInterface.

        Args:
            web: WebInterface instance for browser automation
        """
        self.web = web

    # ==================== LOCATORS ====================

    NEW_INQUIRY_BTN = (By.CSS_SELECTOR, "[aria-label='inquiry_view_button_add']")
    SEARCH_INPUT = (By.CSS_SELECTOR, "[aria-label='search_view_input_search']")
    FILTER_BTN = (By.CSS_SELECTOR, "[aria-label='search_view_button_filter']")

    # ==================== NAVIGATION ====================

    def navigate(self) -> "InquiriesPage":
        """
        Navigate to Inquiries page.

        Returns:
            self for method chaining
        """
        self.web.navigate_to(self.web.config['url'] + '/Portal/Inquiries')
        return self

    # ==================== ACTION METHODS ====================

    def click_new_inquiry_btn(self) -> "InquiriesPage":
        """
        Click new inquiry button.

        Returns:
            self for method chaining
        """
        self.web.click(*self.NEW_INQUIRY_BTN)
        return self

    def enter_search_input(self, text: str) -> "InquiriesPage":
        """
        Enter text into search input.

        Args:
            text: Text to enter

        Returns:
            self for method chaining
        """
        self.web.type_text(*self.SEARCH_INPUT, text)
        return self

    def click_filter_btn(self) -> "InquiriesPage":
        """
        Click filter button.

        Returns:
            self for method chaining
        """
        self.web.click(*self.FILTER_BTN)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_inquiry_visible(self) -> bool:
        """
        Check if inquiry row is displayed.

        Returns:
            True if inquiry row is visible, False otherwise
        """
        return self.web.is_element_displayed(By.CSS_SELECTOR, "table tbody tr", timeout=5)

    def has_inquiry_type(self) -> bool:
        """
        Check if inquiry type cell is displayed.

        Returns:
            True if inquiry type cell is visible, False otherwise
        """
        return self.web.is_element_displayed(By.CSS_SELECTOR, "[aria-label='inquiry_view_value_type']", timeout=5)

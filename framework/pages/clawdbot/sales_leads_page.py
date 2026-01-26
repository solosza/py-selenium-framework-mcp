"""
SalesLeadsPage - Page Object Model

Page Object representing the Sales Leads page in the Helios Portal.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class SalesLeadsPage:
    """
    Page Object for Sales Leads Page.

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
    # Input elements (discovered in PASS 1)
    SEARCH_INPUT = (By.CSS_SELECTOR, "[aria-label='search_view_input_search']")
    CANCEL_BUTTON = (By.CSS_SELECTOR, "[aria-label='search_view_button_cancel']")
    FILTER_BUTTON = (By.CSS_SELECTOR, "[aria-label='search_view_button_filter']")
    VIEW_LEAD_BUTTON = (By.CSS_SELECTOR, "[aria-label='lead_view_button_view']")

    # Output elements (discovered in PASS 2)
    RESULTS_TABLE = (By.CSS_SELECTOR, "table")
    CUSTOMER_HEADER = (By.CSS_SELECTOR, "[aria-label='lead_view_label_customername']")
    STATUS_HEADER = (By.CSS_SELECTOR, "[aria-label='lead_view_label_status']")
    RESULTS_CONTAINER = (By.CSS_SELECTOR, "main")
    LEADS_TITLE = (By.CSS_SELECTOR, "[aria-label='lead_view_title_leads']")

    # ==================== NAVIGATION ====================

    def navigate(self) -> "SalesLeadsPage":
        """Navigate to Sales Leads page."""
        self.web.navigate_to(self.web.config['url'] + '/Portal/Sales/Leads')
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_search_text(self, text: str) -> "SalesLeadsPage":
        """Enter text into search input (live search - filters as you type)."""
        self.web.type_text(*self.SEARCH_INPUT, text)
        return self

    def clear_search(self) -> "SalesLeadsPage":
        """Clear search input by clicking cancel button."""
        self.web.click(*self.CANCEL_BUTTON)
        return self

    def click_filter(self) -> "SalesLeadsPage":
        """Click filter button."""
        self.web.click(*self.FILTER_BUTTON)
        return self

    def click_view_first_lead(self) -> "SalesLeadsPage":
        """Click view button on first lead in results."""
        self.web.click(*self.VIEW_LEAD_BUTTON)
        return self

    def wait_for_results(self, timeout: int = 5) -> "SalesLeadsPage":
        """Wait for search results to update."""
        self.web.wait_for_element_visible(*self.RESULTS_TABLE, timeout=timeout)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def has_search_results(self) -> bool:
        """Check if search results table is displayed."""
        return self.web.is_element_displayed(*self.RESULTS_TABLE, timeout=5)

    def is_search_results_displayed(self) -> bool:
        """Check if results container is visible."""
        return self.web.is_element_displayed(*self.RESULTS_CONTAINER, timeout=5)

    def is_on_leads_page(self) -> bool:
        """Check if on leads page by verifying title."""
        return self.web.is_element_displayed(*self.LEADS_TITLE, timeout=5)

    def get_search_input_value(self) -> str:
        """Get current value in search input."""
        return self.web.get_element_attribute(*self.SEARCH_INPUT, "value")

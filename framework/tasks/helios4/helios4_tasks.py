"""
Helios4Tasks - Task module for orchestrating Inquiries page workflows.

Tasks orchestrate page object methods for single domain operations.
This is Layer 2 of the 4-layer architecture (Page → Task → Role → Test).
"""

from interfaces.web_interface import WebInterface
from pages.helios4.inquiries_page import InquiriesPage
from resources.utilities import autologger


class Helios4Tasks:
    """
    Helios4Tasks - orchestrates single domain operations.

    - @autologger("Task") on workflow methods
    - Composes page objects
    - NO locators (delegate to page objects)
    - NO return values (tests assert via POM state-check methods)
    """

    def __init__(self, web: WebInterface):
        """
        Initialize and compose page objects.

        Args:
            web: WebInterface instance
        """
        self.web = web
        self.inquiries_page = InquiriesPage(web)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Task")
    def submit_form(self, text: str) -> None:
        """
        Submit form with text input.

        NO return value - test asserts via POM state-check methods.
        """
        # Navigate to page first (DD-49: Tasks call pom.navigate())
        self.inquiries_page.navigate()

        # Wait for page to fully load (slow site)
        import time
        time.sleep(3)

        (self.inquiries_page
            .enter_search_input(text))
        # NO return - test asserts via POM

    @autologger.automation_logger("Task")
    def do_new_inquiry_btn(self) -> None:
        """
        Click new inquiry button.

        NO return value - test asserts via POM state-check methods.
        """
        # Navigate to page first (DD-49: Tasks call pom.navigate())
        self.inquiries_page.navigate()

        # Wait for page to fully load (slow site)
        import time
        time.sleep(3)

        (self.inquiries_page
            .click_new_inquiry_btn())
        # NO return - test asserts via POM

    @autologger.automation_logger("Task")
    def do_filter_btn(self) -> None:
        """
        Click filter button.

        NO return value - test asserts via POM state-check methods.
        """
        # Navigate to page first (DD-49: Tasks call pom.navigate())
        self.inquiries_page.navigate()

        # Wait for page to fully load (slow site)
        import time
        time.sleep(3)

        (self.inquiries_page
            .click_filter_btn())
        # NO return - test asserts via POM

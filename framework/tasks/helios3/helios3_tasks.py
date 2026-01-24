"""
Helios3Tasks - Task module for orchestrating Inquiries page workflows.

Tasks orchestrate page object methods for single domain operations.
This is Layer 2 of the 4-layer architecture (Page → Task → Role → Test).
"""

from interfaces.web_interface import WebInterface
from pages.helios3.inquiries_page import InquiriesPage
from resources.utilities import autologger


class Helios3Tasks:
    """
    Helios3Tasks - orchestrates single domain operations.

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
        (self.inquiries_page
            .enter_search_input(text))
        # NO return - test asserts via POM

    @autologger.automation_logger("Task")
    def do_new_inquiry_btn(self) -> None:
        """
        Click new inquiry button.

        NO return value - test asserts via POM state-check methods.
        """
        (self.inquiries_page
            .click_new_inquiry_btn())
        # NO return - test asserts via POM

    @autologger.automation_logger("Task")
    def do_filter_btn(self) -> None:
        """
        Click filter button.

        NO return value - test asserts via POM state-check methods.
        """
        (self.inquiries_page
            .click_filter_btn())
        # NO return - test asserts via POM

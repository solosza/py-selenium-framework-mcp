"""
Inquiry management operations including creating new inquiries

This module provides high-level task methods that orchestrate page objects
to accomplish business workflows.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from pages.helios6.inquiries_page import InquiriesPage


class InquiryTasks:
    """
    Task module for Inquiry operations.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    - Uses fluent POM API
    """

    def __init__(self, web: WebInterface):
        """
        Compose Page Objects - NO decorator on constructor.

        Args:
            web: WebInterface instance
        """
        self.web = web
        # Compose page objects - they get URL from self.web.config
        self.inquiries_page = InquiriesPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def click_new_inquiry_button(self) -> None:
        """
        Navigate to Inquiries page and click the New Inquiry button.

        NO return value - test asserts via POM state-check methods.
        """
        (self.inquiries_page
            .navigate()
            .click_new_inquiry_btn())
        # NO return - test asserts via POM

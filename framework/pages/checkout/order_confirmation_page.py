"""
OrderConfirmationPage - Order confirmation page object.

This page represents the final order confirmation after successful checkout.
Displays order reference, total, and success message.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class OrderConfirmationPage:
    """Page Object for Order Confirmation page."""

    def __init__(self, web: WebInterface):
        """
        Initialize OrderConfirmationPage.

        Args:
            web: WebInterface instance
        """
        self.web = web

    # ==================== LOCATORS ====================

    PAGE_HEADING = (By.CSS_SELECTOR, "h1.page-heading")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".cheque-indent strong")
    ORDER_CONFIRMATION_BOX = (By.CSS_SELECTOR, ".box")
    ORDER_REFERENCE = (By.CSS_SELECTOR, ".box")
    ORDER_AMOUNT = (By.CSS_SELECTOR, ".box span.price")
    VIEW_ORDER_HISTORY_LINK = (By.CSS_SELECTOR, "a[href*='controller=history']")
    BACK_TO_ORDERS_LINK = (By.CSS_SELECTOR, "a.button-exclusive")

    # ==================== PAGE METHODS ====================

    def is_page_loaded(self) -> bool:
        """
        Verify order confirmation page is loaded.

        Returns:
            True if confirmation box is visible
        """
        return self.web.is_element_displayed(*self.ORDER_CONFIRMATION_BOX, timeout=10)

    # ==================== VERIFICATION METHODS ====================

    def is_order_confirmed(self) -> bool:
        """
        Check if order is confirmed successfully.

        Returns:
            True if success message displayed
        """
        if not self.is_page_loaded():
            return False

        # Check for "Your order on My Store is complete." message
        success_element = self.web.find_element(*self.SUCCESS_MESSAGE)
        return "complete" in success_element.text.lower()

    def get_confirmation_message(self) -> str:
        """
        Get the confirmation success message.

        Returns:
            Confirmation message text
        """
        element = self.web.find_element(*self.SUCCESS_MESSAGE)
        return element.text.strip()

    def get_order_reference(self) -> str:
        """
        Extract order reference from confirmation.

        Returns:
            Order reference code (e.g., "IDLGGNCYP")
        """
        box = self.web.find_element(*self.ORDER_CONFIRMATION_BOX)
        text = box.text

        # Parse reference from text like "Your order reference is: IDLGGNCYP"
        if "reference" in text.lower():
            import re
            match = re.search(r'reference[:\s]+([A-Z0-9]+)', text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""

    def get_order_amount(self) -> str:
        """
        Get order amount from confirmation.

        Returns:
            Order amount as string (e.g., "$23.40")
        """
        try:
            element = self.web.find_element(*self.ORDER_AMOUNT)
            return element.text.strip()
        except Exception:
            return ""

    def get_page_heading(self) -> str:
        """
        Get page heading text.

        Returns:
            Page heading text
        """
        element = self.web.find_element(*self.PAGE_HEADING)
        return element.text.strip()

    # ==================== NAVIGATION METHODS ====================

    def click_view_order_history(self) -> "OrderConfirmationPage":
        """
        Click view order history link.

        Returns:
            self for method chaining
        """
        self.web.click(*self.VIEW_ORDER_HISTORY_LINK)
        return self

    def click_back_to_orders(self) -> "OrderConfirmationPage":
        """
        Click back to orders button.

        Returns:
            self for method chaining
        """
        self.web.click(*self.BACK_TO_ORDERS_LINK)
        return self

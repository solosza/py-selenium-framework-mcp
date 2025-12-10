"""
Checkout Tasks - Checkout workflow operations.

This module provides high-level task methods that orchestrate page objects
to accomplish checkout-related workflows from address to payment confirmation.
"""

import time
from interfaces.web_interface import WebInterface
from pages.cart.cart_page import CartPage
from pages.checkout.checkout_page import CheckoutPage
from pages.checkout.order_confirmation_page import OrderConfirmationPage
from resources.utilities import autologger


class CheckoutTasks:
    """Checkout task workflows for completing purchase."""

    def __init__(self, web: WebInterface, base_url: str):
        """
        Initialize CheckoutTasks.

        Args:
            web: WebInterface instance
            base_url: Application base URL
        """
        self.web = web
        self.base_url = base_url
        self.cart_page = CartPage(web)
        self.checkout_page = CheckoutPage(web)
        self.order_confirmation_page = OrderConfirmationPage(web)

    # ==================== CHECKOUT FLOW METHODS ====================

    @autologger.automation_logger("Task")
    def complete_checkout(self, payment_method: str = "bank_wire") -> None:
        """
        Complete entire checkout process from cart to order confirmation.

        Assumes user is logged in and cart has items.
        Steps: Cart -> Address -> Shipping -> Payment -> Confirm

        Args:
            payment_method: Payment method ("bank_wire" or "check")
        """
        # Step 1: From cart, proceed to checkout
        self.web.logger.info("Starting checkout from cart...")
        self.cart_page.click_proceed_to_checkout()
        time.sleep(3)

        # Step 2: Address page - wait for it and click proceed
        self.web.logger.info("Waiting for address step...")
        max_wait = 10
        for i in range(max_wait):
            if self.checkout_page.is_address_step():
                self.web.logger.info("Address step detected")
                break
            time.sleep(1)
        else:
            self.web.logger.error("Address step not reached within timeout")

        self.web.logger.info("Processing address step...")
        self.checkout_page.click_proceed_address()
        time.sleep(3)
        self.web.logger.info("Completed address step")

        # Step 3: Shipping page - wait for it, accept terms, proceed
        self.web.logger.info("Waiting for shipping step...")
        for i in range(max_wait):
            if self.checkout_page.is_shipping_step():
                self.web.logger.info("Shipping step detected")
                break
            time.sleep(1)
        else:
            self.web.logger.error("Shipping step not reached within timeout")

        self.web.logger.info("Processing shipping step...")
        self.checkout_page.accept_terms()
        time.sleep(0.5)
        self.checkout_page.click_proceed_shipping()
        time.sleep(3)
        self.web.logger.info("Completed shipping step")

        # Step 4: Payment page - wait for it, select payment method
        self.web.logger.info("Waiting for payment step...")
        for i in range(max_wait):
            if self.checkout_page.is_payment_step():
                self.web.logger.info("Payment step detected")
                break
            time.sleep(1)
        else:
            self.web.logger.error("Payment step not reached within timeout")

        self.web.logger.info("Processing payment step...")
        if payment_method == "bank_wire":
            self.checkout_page.select_pay_by_bank_wire()
        else:
            self.checkout_page.select_pay_by_check()
        time.sleep(3)
        self.web.logger.info(f"Selected payment method: {payment_method}")

        # Step 5: Confirm order - wait for confirm button and click
        self.web.logger.info("Confirming order...")
        self.checkout_page.click_confirm_order()
        time.sleep(3)

        # Verify order confirmation
        if self.order_confirmation_page.is_order_confirmed():
            ref = self.order_confirmation_page.get_order_reference()
            self.web.logger.info(f"Order confirmed! Reference: {ref}")
        else:
            self.web.logger.error("Order confirmation not displayed")

    @autologger.automation_logger("Task")
    def proceed_to_address_step(self) -> None:
        """Proceed from cart to address step (for logged-in users)."""
        self.cart_page.click_proceed_to_checkout()
        time.sleep(2)

        if not self.checkout_page.is_address_step():
            self.web.logger.warning("Did not reach address step - may need login")

    @autologger.automation_logger("Task")
    def complete_address_step(self) -> None:
        """Complete address step with default address."""
        if not self.checkout_page.is_address_step():
            self.web.logger.error("Not on address step")
            return

        self.checkout_page.click_proceed_address()
        time.sleep(2)
        self.web.logger.info("Address step completed")

    @autologger.automation_logger("Task")
    def complete_shipping_step(self) -> None:
        """Complete shipping step - accept terms and proceed."""
        if not self.checkout_page.is_shipping_step():
            self.web.logger.error("Not on shipping step")
            return

        self.checkout_page.accept_terms()
        time.sleep(0.5)
        self.checkout_page.click_proceed_shipping()
        time.sleep(2)
        self.web.logger.info("Shipping step completed")

    @autologger.automation_logger("Task")
    def complete_payment_step(self, payment_method: str = "bank_wire") -> None:
        """
        Complete payment step - select method and confirm.

        Args:
            payment_method: "bank_wire" or "check"
        """
        if not self.checkout_page.is_payment_step():
            self.web.logger.error("Not on payment step")
            return

        if payment_method == "bank_wire":
            self.checkout_page.select_pay_by_bank_wire()
        else:
            self.checkout_page.select_pay_by_check()

        time.sleep(2)
        self.checkout_page.click_confirm_order()
        time.sleep(3)
        self.web.logger.info("Payment confirmed")

    # ==================== VERIFICATION METHODS ====================

    @autologger.automation_logger("Task")
    def verify_order_complete(self) -> bool:
        """
        Verify order was completed successfully.

        Returns:
            True if order confirmation displayed
        """
        return self.order_confirmation_page.is_order_confirmed()

    @autologger.automation_logger("Task")
    def get_order_reference(self) -> str:
        """
        Get order reference from confirmation page.

        Returns:
            Order reference string
        """
        return self.order_confirmation_page.get_order_reference()

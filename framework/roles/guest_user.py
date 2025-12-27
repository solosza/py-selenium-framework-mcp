"""
GuestUser - Role representing a guest user persona.

Orchestrates AuthTasks for user registration workflow.
Orchestrates CartTasks for add-to-cart workflow.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.auth.auth_tasks import AuthTasks
from tasks.cart.cart_tasks import CartTasks
from resources.utilities import autologger


class GuestUser:
    """Role representing a guest user who can register or add items to cart."""

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web: WebInterface, user_data: Dict[str, Any] = None):
        """
        Compose WebInterface + Tasks, NO inheritance, NO base_url.

        Args:
            web: WebInterface instance
            user_data: Optional user data (email, password, first_name, last_name)
        """
        self.web = web
        self.user_data = user_data or {}
        self.email = self.user_data.get("email")
        self.password = self.user_data.get("password")
        self.first_name = self.user_data.get("first_name")
        self.last_name = self.user_data.get("last_name")

        # Compose Task modules - NO base_url passed
        self.auth_tasks = AuthTasks(web)
        self.cart_tasks = CartTasks(web)

    @autologger.automation_logger("Role")
    def register_account(self) -> None:
        """
        Complete workflow: Register a new user account.

        Orchestrates AuthTasks to complete registration.
        NO return value - test asserts via POM state methods.
        """
        self.auth_tasks.register_user(self.user_data)
        # NO return - test asserts via registration_page.is_account_created()

    @autologger.automation_logger("Role")
    def add_product_to_cart(self, size: str, color: str) -> None:
        """
        Workflow: Add a product to cart with specified options.

        Args:
            size: Product size (S, M, L)
            color: Product color (Blue, Black, Orange, Yellow)

        NO return value - test asserts via product_page.is_product_added_successfully()
        """
        self.cart_tasks.add_to_cart(size, color)
        # NO return - test asserts via POM state methods

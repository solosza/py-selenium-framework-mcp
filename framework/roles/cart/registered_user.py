"""
RegisteredUser - Role for authenticated user workflows on Saucedemo.

Orchestrates multiple tasks into complete business workflows.
"""

from typing import Dict, Any
from framework.interfaces.web_interface import WebInterface
from framework.tasks.cart.cart_tasks import CartTasks
from framework.resources.utilities import autologger


class RegisteredUser:
    """
    Role representing an authenticated user on Saucedemo.

    - Composes Task modules
    - Each method = complete workflow (orchestrates multiple tasks)
    - Uses @autologger.automation_logger("Role") decorator
    - NO return values - tests assert via POM state-check methods
    - NO locators - delegates to Tasks which delegate to POMs
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web: WebInterface, user_data: Dict[str, Any]):
        """
        Initialize RegisteredUser with WebInterface and credentials.

        Args:
            web: WebInterface instance
            user_data: Dict containing username and password
        """
        self.web = web
        self.user_data = user_data
        self.username = user_data.get("username")
        self.password = user_data.get("password")

        # Compose Task modules
        self.cart_tasks = CartTasks(web)

    @autologger.automation_logger("Role")
    def login_and_add_backpack_to_cart(self) -> None:
        """
        Complete workflow: Login to Saucedemo and add Sauce Labs Backpack to cart.

        Orchestrates multiple task methods into a complete user journey.
        NO return value - test asserts via POM state-check methods.
        """
        self.cart_tasks.login(self.username, self.password)
        self.cart_tasks.add_backpack_to_cart()

"""
CartTasks - Task layer for Saucedemo cart workflow.

Orchestrates page object methods for single domain operations.
"""

from framework.interfaces.web_interface import WebInterface
from framework.pages.cart.login_page import LoginPage
from framework.pages.cart.inventory_page import InventoryPage
from framework.resources.utilities import autologger


class CartTasks:
    """
    Task class for cart-related operations on Saucedemo.

    - Composes page objects
    - Each method = one domain operation
    - Uses @autologger.automation_logger("Task") decorator
    - NO return values - tests assert via POM state-check methods
    - NO locators - delegates to page objects
    """

    def __init__(self, web: WebInterface):
        """
        Initialize CartTasks with page objects.

        Args:
            web: WebInterface instance
        """
        self.web = web
        self.login_page = LoginPage(web)
        self.inventory_page = InventoryPage(web)

    @autologger.automation_logger("Task")
    def login(self, username: str, password: str):
        """
        Single domain operation: authenticate user on Saucedemo.

        Args:
            username: Saucedemo username
            password: Saucedemo password

        NO return value - test asserts via inventory_page.is_on_inventory_page()
        """
        (self.login_page
            .navigate()
            .enter_username(username)
            .enter_password(password)
            .click_login())

    @autologger.automation_logger("Task")
    def add_backpack_to_cart(self):
        """
        Single domain operation: add Sauce Labs Backpack to cart.

        NO return value - test asserts via inventory_page.is_product_in_cart()
        """
        self.inventory_page.click_add_backpack_to_cart()

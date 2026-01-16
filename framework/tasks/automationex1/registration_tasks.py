"""
User registration and product cart operations for automationexercise.com workflow

This module provides high-level task methods that orchestrate page objects
to accomplish business workflows.
"""

from interfaces.web_interface import WebInterface
from pages.automationex1.signup_page import SignupPage
from pages.automationex1.registration_page import RegistrationPage
from pages.automationex1.products_page import ProductsPage
from resources.utilities import autologger


class RegistrationTasks:
    """
    Task module for registration and cart operations.

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
            web: WebInterface instance (contains config with URL)
        """
        self.web = web
        # Compose page objects - they get URL from self.web.config
        self.signup_page = SignupPage(web)
        self.registration_page = RegistrationPage(web)
        self.products_page = ProductsPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def register_account(self, user_data: dict) -> None:
        """
        Single domain operation: Register a new user account.

        Args:
            user_data: Dictionary containing user registration info
                       (name, email, password, first_name, last_name, etc.)

        NO return value - test asserts via registration_page.is_registration_successful()
        """
        # Navigate to signup page and enter initial info
        (self.signup_page
            .navigate()
            .enter_name(user_data["name"])
            .enter_email(user_data["email"])
            .click_signup_btn())

        # Fill out registration form
        (self.registration_page
            .click_title_mr()
            .enter_password(user_data["password"])
            .select_day(user_data.get("day", "1"))
            .select_month(user_data.get("month", "January"))
            .select_year(user_data.get("year", "1990"))
            .enter_first_name(user_data["first_name"])
            .enter_last_name(user_data["last_name"])
            .enter_address(user_data["address"])
            .select_country(user_data.get("country", "United States"))
            .enter_state(user_data["state"])
            .enter_city(user_data["city"])
            .enter_zipcode(user_data["zipcode"])
            .enter_mobile(user_data["mobile"])
            .click_create_account_btn())

        # Click continue after success
        self.registration_page.click_continue_btn()

        # NO return - test asserts via registration_page.is_registration_successful()

    @autologger.automation_logger("Task")
    def add_product_to_cart(self) -> None:
        """
        Single domain operation: Add first product to shopping cart.

        NO return value - test asserts via products_page.is_product_in_cart()
        """
        # Navigate to products and add first product to cart
        (self.products_page
            .navigate()
            .click_add_to_cart_btn())

        # NO return - test asserts via products_page.is_product_in_cart()

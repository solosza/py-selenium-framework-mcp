"""
NewUser - Role for orchestrating business workflows.

Roles represent user personas (e.g., Admin, Customer, Guest).
This role orchestrates complete business workflows using Task modules.
"""

import json
from typing import Dict, Any
from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.automationex1.registration_tasks import RegistrationTasks


class NewUser:
    """
    NewUser - orchestrates complete business workflows.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - Workflow methods call MULTIPLE tasks
    - NO return values
    - NO locators
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface):
        """
        Initialize and compose Task modules.

        Args:
            web_interface: WebInterface instance (contains config with URL)
        """
        self.web = web_interface
        
        # Dynamic strategy: Read from config file (after registration)
        with open('tests/automationex1/data/test_users.json') as f:
            users = json.load(f)
            self.user_data = users.get('new_user')
        
        # Compose tasks - NO base_url passed (POMs get URL from self.web.config)
        self.registration_tasks = RegistrationTasks(web_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def register_and_add_to_cart(self) -> None:
        """
        Complete workflow: Register new account AND add product to cart.
        
        This is what makes Role different from Task:
        - Role orchestrates MULTIPLE task methods
        - Role represents a complete user journey/story
        
        Uses self.user_data read from config file.

        NO return value - test asserts via POM state-check methods.
        """
        # Step 1: Register account with user data from config
        self.registration_tasks.register_account(self.user_data)
        
        # Step 2: Add product to cart
        self.registration_tasks.add_product_to_cart()
        
        # NO return - test asserts via POM

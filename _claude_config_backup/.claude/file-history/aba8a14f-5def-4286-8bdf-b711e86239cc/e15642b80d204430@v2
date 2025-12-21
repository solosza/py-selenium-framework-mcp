"""
Registered User Role - Authenticated user with full e-commerce capabilities.

This role represents a logged-in customer who can:
- Browse product catalog
- Add products to cart
- Complete checkout process
- View order history
- Manage account settings
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.common.common_tasks import CommonTasks
from resources.utilities import autologger


class RegisteredUser:
    """
    Registered User role with full e-commerce workflow capabilities.

    This role orchestrates high-level business workflows for authenticated users
    by composing task modules (authentication, catalog, cart, checkout).
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any], base_url: str):
        """
        Initialize RegisteredUser with credentials and task orchestrators.

        Args:
            web_interface: WebInterface instance for browser interactions
            user_data: Dictionary containing user credentials and profile data
                Required keys: email, password
                Optional keys: first_name, last_name, address, phone, etc.
            base_url: Application base URL for navigation
        """
        self.web = web_interface
        self.user_data = user_data
        self.email = user_data.get('email')
        self.password = user_data.get('password')

        # Validate required credentials
        if not self.email or not self.password:
            raise ValueError("RegisteredUser requires email and password in user_data")

        # Compose task modules
        self.common_tasks = CommonTasks(web_interface, base_url)

    # ==================== AUTHENTICATION WORKFLOWS ====================

    @autologger.automation_logger("Role")
    def login(self) -> bool:
        """
        Log in to the application.

        High-level business workflow that orchestrates authentication.

        Returns:
            True if login successful, False otherwise
        """
        return self.common_tasks.log_in(self.email, self.password)

    @autologger.automation_logger("Role")
    def logout(self) -> bool:
        """
        Log out from the application.

        High-level business workflow that completes logout process.

        Returns:
            True if logout successful, False otherwise
        """
        return self.common_tasks.log_out()

    @autologger.automation_logger("Role")
    def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in.

        Returns:
            True if logged in, False otherwise
        """
        return self.common_tasks.verify_logged_in()

    @autologger.automation_logger("Role")
    def register(self) -> bool:
        """
        Register as a new user.

        Complete registration workflow that orchestrates:
        1. Navigate to authentication page
        2. Submit email to initiate registration
        3. Fill out registration form with user data
        4. Submit form and verify account created

        Returns:
            True if registration successful and user is logged in, False otherwise
        """
        return self.common_tasks.register_new_user(self.user_data)

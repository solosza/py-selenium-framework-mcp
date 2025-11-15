"""
RegisteredUser Role.

This role represents a user with specific capabilities and permissions.
"""

from typing import Dict, Any
from roles.role import Role
from interfaces.web_interface import WebInterface
from tasks.common_tasks import CommonTasks


class RegisteredUser(Role):
    """
    RegisteredUser role with workflow capabilities.

    Capabilities: can_login, can_logout
    """

    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any], base_url: str):
        """
        Initialize RegisteredUser.

        Args:
            web_interface: WebInterface instance for browser interactions
            user_data: Dictionary containing user credentials and profile data
            base_url: Application base URL for navigation
        """
        super().__init__(web_interface, user_data)

        # Validate required credentials
        if not self.has_credentials():
            raise ValueError("RegisteredUser requires email and password in user_data")

        # Compose task modules
        self.common_tasks = CommonTasks(web_interface, base_url)

        # TODO: Add additional task modules as needed

    # ==================== AUTHENTICATION WORKFLOWS ====================

    def login(self) -> bool:
        """
        Log in to the application.

        High-level business workflow that orchestrates authentication.

        Returns:
            True if login successful, False otherwise
        """
        return self.common_tasks.log_in(self.email, self.password)

    def logout(self) -> bool:
        """
        Log out from the application.

        Returns:
            True if logout successful, False otherwise
        """
        return self.common_tasks.log_out()

    def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in.

        Returns:
            True if logged in, False otherwise
        """
        return self.common_tasks.verify_logged_in()

    # TODO: Add role-specific workflow methods

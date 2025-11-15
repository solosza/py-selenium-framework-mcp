"""
Base Role class for test automation framework.

Roles represent user personas (e.g., guest user, registered user, admin)
and encapsulate their credentials and capabilities.
"""

from typing import Dict, Optional, Any
from interfaces.web_interface import WebInterface


class Role:
    """
    Base Role class representing a user persona in the system.

    Roles encapsulate:
    - User credentials (email, password)
    - User profile data (name, address, etc.)
    - WebInterface instance for performing actions
    """

    def __init__(self, web_interface: WebInterface, user_data: Optional[Dict[str, Any]] = None):
        """
        Initialize Role with WebInterface and optional user data.

        Args:
            web_interface: WebInterface instance for browser interactions
            user_data: Optional dictionary containing user credentials and profile data
        """
        self.web = web_interface
        self.user_data = user_data or {}

        # Extract common user attributes
        self.email = self.user_data.get('email')
        self.password = self.user_data.get('password')
        self.first_name = self.user_data.get('first_name')
        self.last_name = self.user_data.get('last_name')
        self.company = self.user_data.get('company', '')
        self.address = self.user_data.get('address')
        self.role_type = self.user_data.get('role', 'unknown')

    def get_full_name(self) -> Optional[str]:
        """
        Get user's full name.

        Returns:
            Full name string or None if not available
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None

    def has_credentials(self) -> bool:
        """
        Check if role has login credentials.

        Returns:
            True if email and password are present, False otherwise
        """
        return bool(self.email and self.password)

    def has_address(self) -> bool:
        """
        Check if role has a saved address.

        Returns:
            True if address data is present, False otherwise
        """
        return bool(self.address)

    def get_user_data(self) -> Dict[str, Any]:
        """
        Get complete user data dictionary.

        Returns:
            Dictionary containing all user data
        """
        return self.user_data.copy()

    def get_email(self) -> Optional[str]:
        """
        Get user's email address.

        Returns:
            Email string or None
        """
        return self.email

    def get_password(self) -> Optional[str]:
        """
        Get user's password.

        Returns:
            Password string or None
        """
        return self.password

    def get_address(self) -> Optional[Dict[str, str]]:
        """
        Get user's address data.

        Returns:
            Address dictionary or None
        """
        return self.address.copy() if self.address else None

    def __repr__(self) -> str:
        """
        String representation of Role.

        Returns:
            String describing the role
        """
        if self.email:
            return f"Role(type='{self.role_type}', email='{self.email}')"
        return f"Role(type='{self.role_type}', anonymous=True)"

    def __str__(self) -> str:
        """
        Human-readable string representation.

        Returns:
            String describing the role
        """
        if self.has_credentials():
            return f"{self.role_type.replace('_', ' ').title()}: {self.email}"
        return f"{self.role_type.replace('_', ' ').title()} (anonymous)"

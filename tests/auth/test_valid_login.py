"""
Authentication Tests - Valid Login.

Tests successful login workflow for registered users.
"""

import pytest
from pathlib import Path
import sys

# Add framework to path
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from roles.registered_user import RegisteredUser
from resources.utilities import autologger


@pytest.mark.smoke
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_valid_login_registered_user(web_interface, config, test_users):
    """
    Test that a registered user can log in with valid credentials.

    Steps:
        1. Create RegisteredUser with valid credentials
        2. Call login() method
        3. Verify login successful (returns True)
        4. Verify user is logged in (is_logged_in() returns True)

    Expected Result:
        User successfully logs in and session is authenticated.
    """
    # Arrange: Get test user data
    user_data = test_users["registered_user"]
    base_url = config["url"]

    # Act: Create user and attempt login
    user = RegisteredUser(web_interface, user_data, base_url)
    login_result = user.login()

    # Assert: Verify login successful
    assert login_result is True, f"Login failed for user: {user_data['email']}"
    assert user.is_logged_in() is True, "User should be logged in after successful login"


@pytest.mark.smoke
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_valid_login_then_logout(web_interface, config, test_users):
    """
    Test that a registered user can log in and then log out.

    Steps:
        1. Create RegisteredUser with valid credentials
        2. Call login() method
        3. Verify login successful
        4. Call logout() method
        5. Verify logout successful (returns True)
        6. Verify user is logged out (is_logged_in() returns False)

    Expected Result:
        User successfully logs in, then logs out, and session ends.
    """
    # Arrange: Get test user data
    user_data = test_users["registered_user_2"]
    base_url = config["url"]

    # Act: Login
    user = RegisteredUser(web_interface, user_data, base_url)
    login_result = user.login()

    # Assert: Verify login successful
    assert login_result is True, f"Login failed for user: {user_data['email']}"
    assert user.is_logged_in() is True, "User should be logged in"

    # Act: Logout
    logout_result = user.logout()

    # Assert: Verify logout successful
    assert logout_result is True, "Logout should return True"
    assert user.is_logged_in() is False, "User should be logged out after logout"

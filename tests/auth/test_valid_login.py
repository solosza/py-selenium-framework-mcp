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

from roles.auth.registered_user import RegisteredUser
from pages.common.home_page import HomePage
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
        3. Verify user is logged in via HomePage state-check

    Expected Result:
        User successfully logs in and session is authenticated.
    """
    # Arrange: Get test user data and create POM for assertions
    user_data = test_users["registered_user"]
    base_url = config["url"]
    home_page = HomePage(web_interface)

    # Act: Create user and attempt login
    user = RegisteredUser(web_interface, user_data, base_url)
    user.login()

    # Assert: Verify login successful via POM state-check
    assert home_page.is_logout_link_visible(), f"Login failed for user: {user_data['email']}"


@pytest.mark.smoke
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_valid_login_then_logout(web_interface, config, test_users):
    """
    Test that a registered user can log in and then log out.

    Steps:
        1. Create RegisteredUser with valid credentials
        2. Call login() method
        3. Verify login successful via POM
        4. Call logout() method
        5. Verify user is logged out via POM

    Expected Result:
        User successfully logs in, then logs out, and session ends.
    """
    # Arrange: Get test user data and create POM for assertions
    user_data = test_users["registered_user_2"]
    base_url = config["url"]
    home_page = HomePage(web_interface)

    # Act: Login
    user = RegisteredUser(web_interface, user_data, base_url)
    user.login()

    # Assert: Verify login successful via POM
    assert home_page.is_logout_link_visible(), f"Login failed for user: {user_data['email']}"

    # Act: Logout
    user.logout()

    # Assert: Verify logout successful via POM
    assert home_page.is_login_link_visible(), "User should be logged out after logout"

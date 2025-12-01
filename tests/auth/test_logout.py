"""
Test suite for user logout scenarios.

Tests cover:
- Successful logout from logged-in state
- Session cleared after logout
- Multiple logout attempts handled gracefully

Prerequisites: Tests require valid user credentials for login before logout.
"""

import sys
import pytest
from pathlib import Path

# Add framework to path
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from resources.utilities import autologger
from roles.auth.registered_user import RegisteredUser
from pages.common.home_page import HomePage


@pytest.mark.smoke
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_logout_after_successful_login(web_interface, config, test_users):
    """
    Test successful logout after user logs in.

    Steps:
        1. Create RegisteredUser with valid credentials
        2. Perform login
        3. Verify user is logged in via POM
        4. Perform logout
        5. Verify user is logged out via POM

    Expected Result:
        User successfully logs out and session is cleared.

    Note: Test will skip if login fails (user doesn't exist on live site).
    """
    # Arrange
    user_data = test_users["registered_user"]
    base_url = config["url"]
    home_page = HomePage(web_interface)

    # Act: Create user and login
    user = RegisteredUser(web_interface, user_data, base_url)
    user.login()

    # Skip test if login fails (expected for non-existent test users)
    if not home_page.is_logout_link_visible():
        pytest.skip("Cannot test logout - login failed (user doesn't exist on live site)")

    # Act: Logout
    user.logout()

    # Assert: Verify logout successful via POM
    assert home_page.is_login_link_visible(), "User should be logged out after logout"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_logout_session_cleared(web_interface, config, test_users):
    """
    Test that session is completely cleared after logout.

    Steps:
        1. Login as registered user
        2. Verify user is logged in via POM
        3. Logout
        4. Verify user is logged out (session cleared) via POM

    Expected Result:
        After logout, user session is completely cleared.

    Note: Test will skip if login fails.
    """
    # Arrange
    user_data = test_users["registered_user_2"]
    base_url = config["url"]
    home_page = HomePage(web_interface)

    # Act: Login
    user = RegisteredUser(web_interface, user_data, base_url)
    user.login()

    if not home_page.is_logout_link_visible():
        pytest.skip("Cannot test session clearing - login failed")

    # Act: Logout
    user.logout()

    # Assert: Session should be cleared (user logged out) via POM
    assert home_page.is_login_link_visible(), "User should be logged out after logout"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_multiple_logout_attempts(web_interface, config, test_users):
    """
    Test that multiple logout attempts don't cause errors.

    Steps:
        1. Login as registered user
        2. Perform logout
        3. Attempt logout again
        4. Verify no error occurs

    Expected Result:
        Multiple logout attempts handled gracefully.

    Note: Test will skip if login fails.
    """
    # Arrange
    user_data = test_users["registered_user_2"]
    base_url = config["url"]
    home_page = HomePage(web_interface)

    # Act: Login
    user = RegisteredUser(web_interface, user_data, base_url)
    user.login()

    if not home_page.is_logout_link_visible():
        pytest.skip("Cannot test multiple logouts - login failed")

    # Act: First logout
    user.logout()
    assert home_page.is_login_link_visible(), "First logout should succeed"

    # Act: Second logout attempt (already logged out - should handle gracefully)
    user.logout()

    # Assert: Should remain logged out
    assert home_page.is_login_link_visible(), "User should remain logged out"

"""
Test suite for user logout scenarios.

Tests cover:
- Successful logout from logged-in state
- Session cleared after logout
- User redirected to appropriate page after logout
- Cannot access protected pages after logout

Prerequisites: Tests require valid user credentials for login before logout.
"""

import sys
import pytest
from pathlib import Path

# Add framework to path
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from resources.utilities import autologger
from roles.registered_user import RegisteredUser
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
        3. Verify user is logged in
        4. Perform logout
        5. Verify user is logged out
        6. Verify logout link no longer visible

    Expected Result:
        User successfully logs out and session is cleared.

    Note: Test will skip if login fails (user doesn't exist on live site).
    """
    # Arrange
    user_data = test_users["registered_user"]
    base_url = config["url"]

    # Act: Login
    user = RegisteredUser(web_interface, user_data, base_url)
    login_result = user.login()

    # Skip test if login fails (expected for non-existent test users)
    if not login_result:
        pytest.skip("Cannot test logout - login failed (user doesn't exist on live site)")

    # Verify logged in before logout
    assert user.is_logged_in(), "User should be logged in before logout"

    # Act: Logout
    logout_result = user.logout()

    # Assert: Verify logout successful
    assert logout_result is True, "Logout should return True"
    assert not user.is_logged_in(), "User should not be logged in after logout"

    # Verify logout link no longer visible (sign-in link should be visible instead)
    home_page = HomePage(web_interface)
    assert not home_page.is_logout_link_visible(), "Logout link should not be visible after logout"
    assert home_page.is_login_link_visible(), "Login link should be visible after logout"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_logout_session_cleared(web_interface, config, test_users):
    """
    Test that session is completely cleared after logout.

    Steps:
        1. Login as registered user
        2. Navigate to account page (protected)
        3. Verify access granted
        4. Logout
        5. Attempt to navigate back to account page
        6. Verify redirected to login (session cleared)

    Expected Result:
        After logout, user cannot access protected pages without re-authenticating.

    Note: Test will skip if login fails.
    """
    # Arrange
    user_data = test_users["registered_user_2"]
    base_url = config["url"]

    # Act: Login
    user = RegisteredUser(web_interface, user_data, base_url)
    login_result = user.login()

    if not login_result:
        pytest.skip("Cannot test session clearing - login failed")

    # Navigate to account page (protected page)
    web_interface.navigate_to(base_url + "?controller=my-account")
    assert "my-account" in web_interface.get_current_url(), "Should be on account page while logged in"

    # Act: Logout
    user.logout()

    # Attempt to access protected page after logout
    web_interface.navigate_to(base_url + "?controller=my-account")

    # Assert: Should be redirected to authentication page
    current_url = web_interface.get_current_url()
    assert "authentication" in current_url or "login" in current_url, \
        "Should be redirected to login page when accessing protected page after logout"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_logout_redirect_to_home(web_interface, config, test_users):
    """
    Test that logout redirects user to appropriate page.

    Steps:
        1. Login as registered user
        2. Perform logout
        3. Verify redirected to home page or authentication page

    Expected Result:
        User is redirected to home/auth page after logout.

    Note: Test will skip if login fails.
    """
    # Arrange
    user_data = test_users["registered_user"]
    base_url = config["url"]

    # Act: Login
    user = RegisteredUser(web_interface, user_data, base_url)
    login_result = user.login()

    if not login_result:
        pytest.skip("Cannot test logout redirect - login failed")

    # Act: Logout
    user.logout()

    # Assert: Verify redirected to appropriate page
    current_url = web_interface.get_current_url()
    # Could redirect to home page or authentication page
    assert any(page in current_url for page in ["index.php", "authentication", "controller=authentication"]), \
        f"Should redirect to home or auth page after logout, got: {current_url}"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_logout_link_visibility_when_logged_out(web_interface, config):
    """
    Test that logout link is not visible when user is logged out.

    Steps:
        1. Navigate to home page (not logged in)
        2. Verify logout link is not visible
        3. Verify login link is visible

    Expected Result:
        Logout link hidden, login link visible when not authenticated.
    """
    # Arrange
    base_url = config["url"]
    home_page = HomePage(web_interface)

    # Act: Navigate to home page without logging in
    web_interface.navigate_to(base_url)

    # Assert: Verify logout link not visible, login link visible
    assert not home_page.is_logout_link_visible(), "Logout link should not be visible when logged out"
    assert home_page.is_login_link_visible(), "Login link should be visible when logged out"


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

    # Act: Login
    user = RegisteredUser(web_interface, user_data, base_url)
    login_result = user.login()

    if not login_result:
        pytest.skip("Cannot test multiple logouts - login failed")

    # Act: First logout
    first_logout = user.logout()
    assert first_logout is True, "First logout should succeed"

    # Act: Second logout attempt (already logged out)
    second_logout = user.logout()

    # Assert: Should handle gracefully (return False or True, but no error)
    assert isinstance(second_logout, bool), "Logout should return boolean even when already logged out"
    assert not user.is_logged_in(), "User should remain logged out"

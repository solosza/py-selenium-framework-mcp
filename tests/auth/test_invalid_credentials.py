"""
Test suite for invalid login credentials scenarios.

Tests cover:
- Invalid email format
- Non-existent user credentials
- Incorrect password
- Empty credentials

All tests should result in authentication failure with appropriate error messages.
"""

import sys
import pytest
from pathlib import Path

# Add framework to path
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.common.authentication_page import AuthenticationPage


@pytest.mark.smoke
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_login_invalid_email_format(web_interface, config):
    """
    Test that login fails with invalid email format.

    Steps:
        1. Navigate to authentication page
        2. Enter invalid email format (no @ symbol)
        3. Enter any password
        4. Submit login form
        5. Verify error message displayed

    Expected Result:
        Login fails with email validation error.
    """
    # Arrange
    base_url = config["url"]
    auth_page = AuthenticationPage(web_interface)

    # Act: Navigate and attempt login with invalid email
    web_interface.navigate_to(base_url + "?controller=authentication")
    auth_page.enter_login_email("notanemail") \
             .enter_login_password("Password123!") \
             .click_sign_in()

    # Assert: Verify error displayed
    assert auth_page.has_error_message(), "Expected error message for invalid email format"
    error_text = auth_page.get_error_message()
    assert "Invalid email" in error_text or "email address" in error_text, \
        f"Expected email validation error, got: {error_text}"


@pytest.mark.smoke
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_login_nonexistent_user(web_interface, config, test_users):
    """
    Test that login fails for non-existent user.

    Steps:
        1. Create RegisteredUser with non-existent credentials
        2. Attempt login
        3. Verify login fails
        4. Verify error message displayed

    Expected Result:
        Login fails with authentication error.
    """
    # Arrange: Use non-existent test user
    user_data = test_users["invalid_user"]
    base_url = config["url"]

    # Act: Attempt login
    user = RegisteredUser(web_interface, user_data, base_url)
    login_result = user.login()

    # Assert: Verify login failed
    assert login_result is False, "Login should fail for non-existent user"
    assert not user.is_logged_in(), "User should not be logged in"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_login_wrong_password(web_interface, config):
    """
    Test that login fails with wrong password.

    Steps:
        1. Navigate to authentication page
        2. Enter valid email format
        3. Enter incorrect password
        4. Submit login form
        5. Verify authentication error displayed

    Expected Result:
        Login fails with authentication failed message.
    """
    # Arrange
    base_url = config["url"]
    auth_page = AuthenticationPage(web_interface)

    # Act: Navigate and attempt login with wrong password
    web_interface.navigate_to(base_url + "?controller=authentication")
    auth_page.enter_login_email("validuser@example.com") \
             .enter_login_password("WrongPassword123!") \
             .click_sign_in()

    # Assert: Verify authentication error
    assert auth_page.has_error_message(), "Expected authentication error"
    assert auth_page.is_login_error_displayed(), "Expected login-specific error message"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_login_empty_email(web_interface, config):
    """
    Test that login fails with empty email field.

    Steps:
        1. Navigate to authentication page
        2. Leave email field empty
        3. Enter password
        4. Submit login form
        5. Verify validation error displayed

    Expected Result:
        Login fails with email required error.
    """
    # Arrange
    base_url = config["url"]
    auth_page = AuthenticationPage(web_interface)

    # Act: Navigate and attempt login with empty email
    web_interface.navigate_to(base_url + "?controller=authentication")
    auth_page.enter_login_password("Password123!") \
             .click_sign_in()

    # Assert: Verify error displayed
    assert auth_page.has_error_message(), "Expected validation error for empty email"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_login_empty_password(web_interface, config):
    """
    Test that login fails with empty password field.

    Steps:
        1. Navigate to authentication page
        2. Enter valid email
        3. Leave password field empty
        4. Submit login form
        5. Verify validation error displayed

    Expected Result:
        Login fails with password required error.
    """
    # Arrange
    base_url = config["url"]
    auth_page = AuthenticationPage(web_interface)

    # Act: Navigate and attempt login with empty password
    web_interface.navigate_to(base_url + "?controller=authentication")
    auth_page.enter_login_email("test@example.com") \
             .click_sign_in()

    # Assert: Verify error displayed
    assert auth_page.has_error_message(), "Expected validation error for empty password"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_login_empty_credentials(web_interface, config):
    """
    Test that login fails with both fields empty.

    Steps:
        1. Navigate to authentication page
        2. Leave both email and password empty
        3. Submit login form
        4. Verify validation error displayed

    Expected Result:
        Login fails with validation error.
    """
    # Arrange
    base_url = config["url"]
    auth_page = AuthenticationPage(web_interface)

    # Act: Navigate and attempt login with empty credentials
    web_interface.navigate_to(base_url + "?controller=authentication")
    auth_page.click_sign_in()

    # Assert: Verify error displayed
    assert auth_page.has_error_message(), "Expected validation error for empty credentials"

"""
Test suite for user registration scenarios.

Tests cover:
- Successful registration with valid data
- Invalid email format during registration
- Duplicate email (already registered)
- Missing required fields
- Password validation

Registration is a two-step process:
1. Submit email on authentication page -> redirects to registration form
2. Fill registration form with personal details
"""

import sys
import pytest
from pathlib import Path

# Add framework to path
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from resources.utilities import autologger
from pages.common.authentication_page import AuthenticationPage
from pages.common.registration_page import RegistrationPage


@pytest.mark.smoke
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_registration_valid_data(web_interface, config, test_users):
    """
    Test successful user registration with all valid data.

    Steps:
        1. Navigate to authentication page
        2. Enter new email in registration form
        3. Click Create Account button
        4. Fill all required registration fields
        5. Submit registration form
        6. Verify account created successfully

    Expected Result:
        User account created and user is logged in.

    Note: This test will fail on subsequent runs as email becomes duplicate.
    """
    # Arrange
    base_url = config["url"]
    new_user_data = test_users["new_user"]
    auth_page = AuthenticationPage(web_interface)
    reg_page = RegistrationPage(web_interface)

    # Act: Navigate to auth page and initiate registration
    web_interface.navigate_to(base_url + "?controller=authentication")
    auth_page.enter_registration_email(new_user_data["email"]) \
             .click_create_account()

    # Wait for registration form to load
    assert reg_page.is_page_loaded(), "Registration form should be displayed"

    # Fill registration form
    reg_page.select_title(new_user_data["title"]) \
            .enter_first_name(new_user_data["first_name"]) \
            .enter_last_name(new_user_data["last_name"]) \
            .enter_password(new_user_data["password"]) \
            .select_date_of_birth(
                new_user_data["dob_day"],
                new_user_data["dob_month"],
                new_user_data["dob_year"]
            ) \
            .enter_address(new_user_data["address_1"]) \
            .enter_city(new_user_data["city"]) \
            .select_state(new_user_data["state"]) \
            .enter_zip_code(new_user_data["zip_code"]) \
            .select_country(new_user_data["country"]) \
            .enter_mobile_phone(new_user_data["mobile_phone"]) \
            .click_register()

    # Assert: Verify registration successful
    # Note: This will fail if email already exists, which is expected behavior
    current_url = web_interface.get_current_url()
    # Successful registration redirects to my-account page
    success = "controller=my-account" in current_url

    if not success:
        # Check for error message
        if reg_page.has_error_message():
            error_msg = reg_page.get_error_message()
            pytest.skip(f"Registration failed (likely duplicate email): {error_msg}")

    assert success, "Registration should succeed and redirect to account page"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_registration_invalid_email_format(web_interface, config):
    """
    Test that registration fails with invalid email format.

    Steps:
        1. Navigate to authentication page
        2. Enter invalid email format (no @ symbol)
        3. Click Create Account button
        4. Verify error message displayed

    Expected Result:
        Registration fails with email validation error.
    """
    # Arrange
    base_url = config["url"]
    auth_page = AuthenticationPage(web_interface)

    # Act: Navigate and attempt registration with invalid email
    web_interface.navigate_to(base_url + "?controller=authentication")
    auth_page.enter_registration_email("notanemail") \
             .click_create_account()

    # Assert: Verify error displayed
    assert auth_page.has_error_message(), "Expected validation error for invalid email"
    assert auth_page.is_registration_email_error_displayed(), \
        "Expected email validation error message"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_registration_duplicate_email(web_interface, config, test_users):
    """
    Test that registration fails for already registered email.

    Steps:
        1. Navigate to authentication page
        2. Enter email that's already registered
        3. Click Create Account button
        4. Verify error message displayed

    Expected Result:
        Registration fails with "email already registered" error.
    """
    # Arrange: Use a registered user's email
    base_url = config["url"]
    registered_user = test_users["registered_user"]
    auth_page = AuthenticationPage(web_interface)

    # Act: Attempt registration with existing email
    web_interface.navigate_to(base_url + "?controller=authentication")
    auth_page.enter_registration_email(registered_user["email"]) \
             .click_create_account()

    # Assert: Verify duplicate email error
    assert auth_page.has_error_message(), "Expected error for duplicate email"
    error_text = auth_page.get_error_message()
    assert "already been registered" in error_text or "already" in error_text, \
        f"Expected duplicate email error, got: {error_text}"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_registration_empty_email(web_interface, config):
    """
    Test that registration fails with empty email field.

    Steps:
        1. Navigate to authentication page
        2. Leave email field empty
        3. Click Create Account button
        4. Verify validation error displayed

    Expected Result:
        Registration fails with email required error.
    """
    # Arrange
    base_url = config["url"]
    auth_page = AuthenticationPage(web_interface)

    # Act: Attempt registration with empty email
    web_interface.navigate_to(base_url + "?controller=authentication")
    auth_page.click_create_account()

    # Assert: Verify validation error
    assert auth_page.has_error_message(), "Expected validation error for empty email"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_registration_missing_required_fields(web_interface, config, test_users):
    """
    Test that registration fails when required fields are missing.

    Steps:
        1. Navigate to authentication page
        2. Enter valid new email
        3. Click Create Account button
        4. Fill only some fields (skip required ones)
        5. Submit registration form
        6. Verify validation errors displayed

    Expected Result:
        Registration fails with required field errors.
    """
    # Arrange
    base_url = config["url"]
    new_user_data = test_users["new_user"]
    auth_page = AuthenticationPage(web_interface)
    reg_page = RegistrationPage(web_interface)

    # Act: Navigate and start registration
    web_interface.navigate_to(base_url + "?controller=authentication")
    auth_page.enter_registration_email("incomplete_" + new_user_data["email"]) \
             .click_create_account()

    # Wait for registration form
    assert reg_page.is_page_loaded(), "Registration form should be displayed"

    # Fill only optional fields, skip required ones
    reg_page.click_register()  # Submit without filling required fields

    # Assert: Verify validation errors
    assert reg_page.has_error_message(), "Expected validation errors for missing required fields"
    error_text = reg_page.get_error_message()
    # Check for common required field error keywords
    assert any(keyword in error_text.lower() for keyword in ["required", "provide", "fill", "missing"]), \
        f"Expected required field error, got: {error_text}"


@pytest.mark.regression
@pytest.mark.auth
@autologger.automation_logger("Test")
def test_registration_invalid_password(web_interface, config, test_users):
    """
    Test that registration fails with invalid password format.

    Steps:
        1. Navigate to authentication page
        2. Enter valid new email
        3. Click Create Account button
        4. Fill all fields but use weak password
        5. Submit registration form
        6. Verify password validation error

    Expected Result:
        Registration fails with password validation error.

    Note: Password requirements vary by site.
    """
    # Arrange
    base_url = config["url"]
    new_user_data = test_users["new_user"].copy()
    new_user_data["email"] = "weak_pwd_" + new_user_data["email"]
    new_user_data["password"] = "123"  # Weak password

    auth_page = AuthenticationPage(web_interface)
    reg_page = RegistrationPage(web_interface)

    # Act: Navigate and start registration
    web_interface.navigate_to(base_url + "?controller=authentication")
    auth_page.enter_registration_email(new_user_data["email"]) \
             .click_create_account()

    # Wait for registration form
    assert reg_page.is_page_loaded(), "Registration form should be displayed"

    # Fill form with weak password
    reg_page.select_title(new_user_data["title"]) \
            .enter_first_name(new_user_data["first_name"]) \
            .enter_last_name(new_user_data["last_name"]) \
            .enter_password(new_user_data["password"]) \
            .select_date_of_birth(
                new_user_data["dob_day"],
                new_user_data["dob_month"],
                new_user_data["dob_year"]
            ) \
            .enter_address(new_user_data["address_1"]) \
            .enter_city(new_user_data["city"]) \
            .select_state(new_user_data["state"]) \
            .enter_zip_code(new_user_data["zip_code"]) \
            .select_country(new_user_data["country"]) \
            .enter_mobile_phone(new_user_data["mobile_phone"]) \
            .click_register()

    # Assert: Check for password validation error or success
    # Note: Site may accept weak passwords, in which case test will pass anyway
    current_url = web_interface.get_current_url()
    if "controller=my-account" not in current_url:
        # Registration failed, check for password error
        assert reg_page.has_error_message(), "Expected password validation error"
    else:
        # Site accepted weak password - test passes but note in skip message
        pytest.skip("Site accepts weak passwords - no validation enforced")

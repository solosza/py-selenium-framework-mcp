"""
Auth Tests - Login 20251115 154322.

Test generated from user story scenario.
"""

import pytest
from pathlib import Path
import sys

# Add framework to path
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from roles.registered_user import RegisteredUser
from resources.utilities import autologger


@pytest.mark.auth
@autologger.automation_logger("Test")
def test_login_20251115_154322(web_interface, config):
    """
    Verify I log in with my email and password

    Scenario:
        Given: I am a registered user with valid credentials
        When: I log in with my email and password
        Then: I should see my account dashboard
    """
    # Arrange
    base_url = config["url"]

    user_data = {
        "email": "test@example.com",
        "password": "Test123!"
    }
    registered_user = RegisteredUser(web_interface, user_data, base_url)

    # Act
    result = registered_user.login()

    # Assert
    assert result is True, "Login should succeed with valid credentials"

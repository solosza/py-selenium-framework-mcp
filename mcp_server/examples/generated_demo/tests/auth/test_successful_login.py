"""
Auth Tests - Successful Login.

Test generated from user story scenario.
"""

import pytest
from pathlib import Path
import sys

# Add framework to path
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from tasks.auth_tasks import AuthTasks
from resources.utilities import autologger


@pytest.mark.auth
@autologger.automation_logger("Test")
def test_successful_login(web_interface, config):
    """
    Verify user can log in with valid credentials

    Scenario:
        Given: user is on login page
        When: user enters valid email and password
        Then: user is logged in successfully
    """
    # Arrange
    base_url = config["url"]
    auth_tasks = AuthTasks(web_interface, base_url)

    test_email = "test@example.com"
    test_password = "Test123!"

    # Act
    result = auth_tasks.login(test_email, test_password)

    # Assert
    assert result is True, "Login should succeed with valid credentials"

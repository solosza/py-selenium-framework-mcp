"""
Auth Tests - Fixed Generated Test.

Test using fixed code generator output.
"""

import pytest
from pathlib import Path
import sys

# Add framework to path
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from tasks.auth_tasks_fixed import AuthTasks
from resources.utilities import autologger


@pytest.mark.auth
@autologger.automation_logger("Test")
def test_fixed_login(web_interface, config):
    """
    Test login using FIXED generated code from code_generator.

    This test uses files generated AFTER fixing import paths.
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

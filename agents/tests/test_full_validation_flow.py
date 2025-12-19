"""
Test Full Validation Flow for DEF-VA-001 Fix.

This test verifies:
1. Supervisor correctly gets scenario from SQA Agent
2. Without content_map, returns ORCHESTRATOR_PENDING (fix for DEF-VA-001)
3. Visual workflow logger shows correct step-by-step flow
4. With content_map, proceeds to Reviewer validation
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.supervisor import _test_run_scenario, _test_run_validation_suite


async def test_orchestrator_pending():
    """
    Test Case 1: Verify ORCHESTRATOR_PENDING status when no artifacts provided.

    Expected Behavior (per DEF-VA-001 fix):
    - Step 1: Supervisor -> SQA Agent (SUCCESS)
    - Step 2: SQA Agent -> AI Orchestrator (FAILED - no content_map)
    - Step 3-4: SKIPPED
    - Status: PENDING
    - failure_type: ORCHESTRATOR_PENDING
    """
    print("\n" + "=" * 70)
    print("TEST 1: ORCHESTRATOR_PENDING (No artifacts provided)")
    print("=" * 70 + "\n")

    # Run scenario WITHOUT content_map - should block
    result = await _test_run_scenario("QA-EASY-001", content_map=None)

    print("\n--- RESULT ---")
    print(f"Status: {result['status']}")
    print(f"Failure Type: {result['failure_type']}")
    print(f"Human Intervention Required: {result['human_intervention_required']}")

    # Assertions
    assert result['status'] == 'PENDING', f"Expected PENDING, got {result['status']}"
    assert result['failure_type'] == 'ORCHESTRATOR_PENDING', f"Expected ORCHESTRATOR_PENDING, got {result['failure_type']}"
    assert result['human_intervention_required'] == True, "Should require human intervention"

    print("\n[PASS] Test 1: Correctly returns ORCHESTRATOR_PENDING")
    return True


async def test_with_valid_artifacts():
    """
    Test Case 2: Verify flow proceeds when content_map is provided.

    Expected Behavior:
    - Step 1: Supervisor -> SQA Agent (SUCCESS)
    - Step 2: SQA Agent -> AI Orchestrator (SUCCESS - content_map provided)
    - Step 3: AI Orchestrator -> Reviewer (SUCCESS/FAIL based on DD checks)
    - Step 4: Reviewer -> Supervisor (Report generated)
    """
    print("\n" + "=" * 70)
    print("TEST 2: Full Flow with Valid Artifacts")
    print("=" * 70 + "\n")

    # Good artifact content (follows DDs)
    good_page = '''"""
Registration Page Object.
"""
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface

class RegistrationPage:
    """Page object for registration page."""

    # Locators
    EMAIL = (By.CSS_SELECTOR, "#email_create")
    SUBMIT_BTN = (By.CSS_SELECTOR, "#SubmitCreate")
    ACCOUNT_CREATED = (By.CSS_SELECTOR, ".account")

    def __init__(self, web: WebInterface):
        self.web = web

    def enter_email(self, email: str) -> "RegistrationPage":
        self.web.type_text(*self.EMAIL, email)
        return self

    def click_create(self) -> "RegistrationPage":
        self.web.click(*self.SUBMIT_BTN)
        return self

    def is_account_created(self) -> bool:
        return self.web.is_element_displayed(*self.ACCOUNT_CREATED)
'''

    good_task = '''"""
Auth Tasks for authentication workflows.
"""
from interfaces.web_interface import WebInterface
from pages.auth.registration_page import RegistrationPage
from resources.utilities import autologger

class AuthTasks:
    def __init__(self, web: WebInterface, base_url: str):
        self.web = web
        self.base_url = base_url
        self.registration_page = RegistrationPage(web)

    @autologger.automation_logger("Task")
    def create_account(self, email: str):
        """Create new account with email."""
        self.web.navigate_to(f"{self.base_url}?controller=authentication")
        (self.registration_page
            .enter_email(email)
            .click_create())
'''

    good_role = '''"""
New User role.
"""
from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.auth.auth_tasks import AuthTasks
from resources.utilities import autologger

class NewUser:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web: WebInterface, user_data: Dict[str, Any], base_url: str):
        self.web = web
        self.user_data = user_data
        self.email = user_data.get('email')
        self.auth_tasks = AuthTasks(web, base_url)

    @autologger.automation_logger("Role")
    def register(self):
        """Register new account."""
        self.auth_tasks.create_account(self.email)
'''

    good_test = '''"""
Test Registration.
"""
import pytest
from roles.new_user import NewUser
from pages.auth.registration_page import RegistrationPage
from resources.utilities import autologger

class TestRegistration:
    @pytest.fixture(autouse=True)
    def setup(self, web_interface, config):
        self.web = web_interface
        self.config = config
        self.registration_page = RegistrationPage(web_interface)

    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_successful_registration(self):
        """Test new user can register."""
        # Arrange
        user_data = {"email": "test@example.com"}
        user = NewUser(self.web, user_data, self.config["url"])

        # Act
        user.register()

        # Assert - via POM state-check method (DD-15)
        assert self.registration_page.is_account_created(), "Account should be created"
'''

    content_map = {
        "framework/pages/auth/registration_page.py": good_page,
        "framework/tasks/auth/auth_tasks.py": good_task,
        "framework/roles/new_user.py": good_role,
        "tests/auth/test_registration.py": good_test
    }

    result = await _test_run_scenario("QA-EASY-001", content_map=content_map)

    print("\n--- RESULT ---")
    print(f"Status: {result['status']}")
    print(f"Review Status: {result['review_status']}")
    print(f"Violations: {len(result['violations'])}")
    print(f"Execution Passed: {result['execution_passed']}")

    # Assertions
    assert result['status'] == 'PASSED', f"Expected PASSED, got {result['status']}"
    assert result['review_status'] == 'APPROVE', f"Expected APPROVE, got {result['review_status']}"

    print("\n[PASS] Test 2: Full flow completed successfully")
    return True


async def test_dd_violation_detected():
    """
    Test Case 3: Verify DD violation causes REJECT.

    Expected Behavior:
    - Step 3: Reviewer detects DD violation
    - Status: FAILED
    - failure_type: TYPE_1_REVIEW_REJECT
    """
    print("\n" + "=" * 70)
    print("TEST 3: DD Violation Detection (Type 1 Failure)")
    print("=" * 70 + "\n")

    # Bad task with DD-03 violation (locators in Task)
    bad_task = '''"""
Auth Tasks - WITH DD-03 VIOLATION.
"""
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface
from resources.utilities import autologger

class AuthTasks:
    def __init__(self, web: WebInterface, base_url: str):
        self.web = web
        self.base_url = base_url

    @autologger.automation_logger("Task")
    def create_account(self, email: str):
        # DD-03 VIOLATION: Locators should only be in Page Objects!
        self.web.type_text(By.ID, "email_create", email)
        self.web.click(By.CSS_SELECTOR, "#SubmitCreate")
'''

    content_map = {
        "framework/tasks/auth/auth_tasks.py": bad_task
    }

    result = await _test_run_scenario("QA-EASY-001", content_map=content_map)

    print("\n--- RESULT ---")
    print(f"Status: {result['status']}")
    print(f"Failure Type: {result['failure_type']}")
    print(f"Review Status: {result['review_status']}")
    print(f"Blocking Violations: {result['blocking_violations']}")

    # Assertions
    assert result['status'] == 'FAILED', f"Expected FAILED, got {result['status']}"
    assert result['failure_type'] == 'TYPE_1_REVIEW_REJECT', f"Expected TYPE_1_REVIEW_REJECT, got {result['failure_type']}"
    assert result['review_status'] == 'REJECT', f"Expected REJECT, got {result['review_status']}"

    print("\n[PASS] Test 3: DD violation correctly detected and rejected")
    return True


async def main():
    """Run all validation tests."""
    print("\n" + "=" * 70)
    print("DEF-VA-001 FIX VALIDATION TESTS")
    print("Testing Four-Component Architecture")
    print("=" * 70)

    results = []

    try:
        results.append(await test_orchestrator_pending())
    except AssertionError as e:
        print(f"\n[FAIL] Test 1: {e}")
        results.append(False)

    try:
        results.append(await test_with_valid_artifacts())
    except AssertionError as e:
        print(f"\n[FAIL] Test 2: {e}")
        results.append(False)

    try:
        results.append(await test_dd_violation_detected())
    except AssertionError as e:
        print(f"\n[FAIL] Test 3: {e}")
        results.append(False)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed - DEF-VA-001 fix verified!")
        print("Ready to mark defect as RESOLVED")
        return True
    else:
        print("\n[FAILURE] Some tests failed - DEF-VA-001 fix incomplete")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

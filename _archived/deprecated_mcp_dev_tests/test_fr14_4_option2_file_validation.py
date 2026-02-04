"""
Test FR-14.4: File Existence Validation (Option 2 - Semantic Validation)

Tests that qg_save_run PRE validation catches missing test data files
when credential_strategy="static" and test_data_location="workflow".

Expected Behavior:
- Gate should detect missing tests/data/test_users.json
- Gate should return status="fail" (not NEEDS_RETRY - file checks are structural)
- Error should mention missing file and static strategy
- Response should include actionable fix_hint
"""

import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add mcp_server to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.gates.qg_save_run import QGSaveRun
from utils.state_manager import StateManager


def test_file_existence_validation():
    """
    Test that qg_save_run PRE validation catches missing test_users.json
    when credential_strategy="static".
    """
    print("\n" + "="*80)
    print("TEST: FR-14.4 File Existence Validation (Option 2)")
    print("="*80)

    # Step 1: Setup test data
    print("\n[SETUP] Creating test parameters...")

    pom_code = """
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface

class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")
    PASSWORD = (By.CSS_SELECTOR, "#passwd")

    def __init__(self, web: WebInterface):
        self.web = web

    def enter_email(self, text: str) -> "LoginPage":
        self.web.type_text(*self.EMAIL, text)
        return self
"""

    task_code = """
from interfaces.web_interface import WebInterface
from pages.auth.login_page import LoginPage
from resources.utilities import autologger

class AuthTasks:
    def __init__(self, web: WebInterface, base_url: str):
        self.web = web
        self.login_page = LoginPage(web)

    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str):
        self.login_page.enter_email(email).enter_password(password)
"""

    role_code = """
from interfaces.web_interface import WebInterface
from tasks.auth_tasks import AuthTasks
from resources.utilities import autologger

class RegisteredUser:
    def __init__(self, web: WebInterface, user_data: dict, base_url: str):
        self.web = web
        self.auth_tasks = AuthTasks(web, base_url)

    @autologger.automation_logger("Role")
    def login(self):
        self.auth_tasks.log_in(self.email, self.password)
"""

    test_code = """
import pytest
from roles.registered_user import RegisteredUser

@pytest.mark.auth
def test_login(web_interface, config, test_data):
    user = RegisteredUser(web_interface, test_data["user"], config["url"])
    user.login()
    assert True
"""

    params = {
        "mode": "PRE",
        "pom_code": pom_code,
        "task_code": task_code,
        "role_code": role_code,
        "test_code": test_code
    }

    print(f"[OK] Test parameters created")
    print(f"  - Mode: PRE")
    print(f"  - All code modules provided")

    # Step 2: Mock state manager to set credential_strategy and test_data_location
    print("\n[SETUP] Mocking state manager with credential_strategy='static', test_data_location='workflow'...")

    mock_state_manager = MagicMock(spec=StateManager)
    mock_state_manager.get_step.side_effect = lambda step: {
        1: {"credential_strategy": "static", "test_data_location": "workflow"},
        2: {"workflow": "auth"}
    }.get(step, None)

    print(f"[OK] State manager mocked")
    print(f"  - Step 1: credential_strategy='static', test_data_location='workflow'")
    print(f"  - Step 2: workflow='auth'")

    # Step 3: Mock file system so test_users.json DOES NOT EXIST
    print("\n[SETUP] Mocking file system - test_users.json DOES NOT EXIST...")

    # Mock Path.exists() to return False only for test_users.json
    def mock_path_exists(self):
        path_str = str(self)

        # Workflow data directory exists
        if "tests/auth/data" in path_str or "tests\\auth\\data" in path_str:
            if "test_users.json" not in path_str:  # Directory check
                print(f"  [MOCK] {path_str} -> True (workflow directory exists)")
                return True

        # test_users.json DOES NOT EXIST
        if "test_users.json" in path_str:
            print(f"  [MOCK] {path_str} -> False (file missing)")
            return False

        # Other paths exist by default
        return True

    # Step 4: Execute qg_save_run PRE validation
    print("\n[EXECUTE] Calling QGSaveRun.validate_pre()...")

    try:
        with patch.object(QGSaveRun, '_get_state_manager', return_value=mock_state_manager):
            # Patch Path.exists at the pathlib level since it's imported locally
            with patch('pathlib.Path.exists', mock_path_exists):
                result = QGSaveRun.validate_pre(params)

        print(f"\n[RESULT] Gate response received")

    except Exception as e:
        print(f"\n[ERROR] Unexpected exception: {e}")
        import traceback
        traceback.print_exc()
        result = {"status": "error", "error": str(e)}

    # Step 5: Validate results
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)

    validation_results = []

    # Check 1: Status should be "fail" (not NEEDS_RETRY)
    print("\n[CHECK 1] Status should be 'fail'...")
    if result.get("status") == "fail":
        print("[PASS] Gate returned status='fail'")
        validation_results.append(("Status Check", "PASS"))
    else:
        print(f"[FAIL] Expected status='fail', got '{result.get('status')}'")
        validation_results.append(("Status Check", "FAIL"))

    # Check 2: Error should mention missing file
    print("\n[CHECK 2] Error should mention missing test_users.json...")
    error_msg = result.get("error", "")
    if "test_users.json" in error_msg.lower() or "missing" in error_msg.lower():
        print(f"[PASS] Error mentions missing file: '{error_msg[:100]}...'")
        validation_results.append(("Error Message Check", "PASS"))
    else:
        print(f"[FAIL] Error does not mention missing file: '{error_msg}'")
        validation_results.append(("Error Message Check", "FAIL"))

    # Check 3: Error should mention static strategy
    print("\n[CHECK 3] Error should mention 'static' strategy...")
    if "static" in error_msg.lower():
        print(f"[PASS] Error mentions static strategy")
        validation_results.append(("Strategy Reference Check", "PASS"))
    else:
        print(f"[FAIL] Error does not mention static strategy")
        validation_results.append(("Strategy Reference Check", "FAIL"))

    # Check 4: Response should include fix_hint
    print("\n[CHECK 4] Response should include fix_hint...")
    fix_hint = result.get("fix_hint", "")
    if fix_hint:
        print(f"[PASS] fix_hint provided: '{fix_hint[:100]}...'")
        validation_results.append(("Fix Hint Check", "PASS"))
    else:
        print(f"[FAIL] No fix_hint provided")
        validation_results.append(("Fix Hint Check", "FAIL"))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, status in validation_results if status == "PASS")
    total = len(validation_results)

    print(f"\nChecks Passed: {passed}/{total}")
    for check_name, status in validation_results:
        print(f"  [{status}] {check_name}")

    overall_status = "PASS" if passed == total else "FAIL"
    print(f"\n{'='*80}")
    print(f"OVERALL TEST STATUS: {overall_status}")
    print(f"{'='*80}")

    # Print full gate response
    print("\n" + "="*80)
    print("FULL GATE RESPONSE")
    print("="*80)
    print(json.dumps(result, indent=2))

    return {
        "test": "FR-14.4 File Existence Validation (Option 2)",
        "status": overall_status,
        "checks_passed": passed,
        "checks_total": total,
        "validation_results": validation_results,
        "gate_response": result
    }


if __name__ == "__main__":
    result = test_file_existence_validation()

    # Exit with appropriate code
    sys.exit(0 if result["status"] == "PASS" else 1)

"""
Test Tools 5 → 6 → 4 chaining to verify COMPLETE code generation.

This test verifies:
1. Tool 5 discovers elements
2. Tool 6 generates COMPLETE POM with methods
3. Tool 4 generates COMPLETE task workflows using POM methods
"""

import asyncio
import json
from tool_05_discover_page_elements import discover_page_elements
from tool_06_generate_page_object import generate_page_object
from tool_04_generate_task import generate_task


async def test_complete_workflow():
    """Test full workflow from element discovery to task generation."""
    print("=" * 80)
    print("[TEST] TOOLS 5 -> 6 -> 4 COMPLETE WORKFLOW")
    print("=" * 80)

    # STEP 1: Discover elements from login page
    print("\n[STEP 1] Discovering page elements...")
    print("-" * 80)

    tool5_args = {
        "url": "http://www.automationpractice.pl/index.php?controller=authentication",
        "element_types": ["inputs", "buttons"]
    }

    tool5_result_str = await discover_page_elements(tool5_args)
    tool5_result = json.loads(tool5_result_str)

    if tool5_result.get("status") != "success":
        print(f"[ERROR] Tool 5 failed: {tool5_result.get('error')}")
        return

    elements_discovered = tool5_result.get("elements", [])
    print(f"✓ Discovered {len(elements_discovered)} elements")

    # STEP 2: Generate POM from discovered elements
    print("\n[STEP 2] Generating POM with methods...")
    print("-" * 80)

    tool6_args = {
        "page_name": "LoginPage",
        "elements": elements_discovered,
        "workflow": "auth"
    }

    tool6_result_str = await generate_page_object(tool6_args)
    tool6_result = json.loads(tool6_result_str)

    if tool6_result.get("status") != "success":
        print(f"[ERROR] Tool 6 failed: {tool6_result.get('error')}")
        return

    pom_code = tool6_result.get("code", "")
    pom_file_path = tool6_result.get("file_path", "")
    print(f"✓ Generated POM: {tool6_result.get('page_name')}")
    print(f"✓ File path: {pom_file_path}")
    print(f"✓ Elements: {tool6_result.get('elements_count')}")

    # Count methods in POM
    pom_methods = [line.strip() for line in pom_code.split('\n') if line.strip().startswith('def ') and '__init__' not in line]
    print(f"✓ Methods generated: {len(pom_methods)}")

    # STEP 3: Generate Task with complete workflows using POM
    print("\n[STEP 3] Generating Task with complete workflows...")
    print("-" * 80)

    tool4_args = {
        "task_name": "AuthTasks",
        "workflow_description": "Authentication workflows: login, logout, password recovery",
        "page_objects": [
            {
                "name": "LoginPage",
                "file_path": pom_file_path,
                "code": pom_code
            }
        ]
    }

    tool4_result_str = await generate_task(tool4_args)
    tool4_result = json.loads(tool4_result_str)

    if tool4_result.get("status") != "success":
        print(f"[ERROR] Tool 4 failed: {tool4_result.get('error')}")
        if "traceback" in tool4_result:
            print(tool4_result["traceback"])
        return

    task_code = tool4_result.get("code", "")
    print(f"✓ Generated Task: {tool4_result.get('task_name')}")
    print(f"✓ File path: {tool4_result.get('file_path')}")
    print(f"✓ Page objects used: {tool4_result.get('page_objects_used')}")
    print(f"✓ Workflows: {tool4_result.get('workflows_generated')}")

    # STEP 4: Verify generated task code
    print("\n[STEP 4] Verifying Task code quality...")
    print("-" * 80)

    # Check for imports
    has_login_page_import = "from pages.auth.loginpage import LoginPage" in task_code
    print(f"{'[OK]' if has_login_page_import else '[FAIL]'} LoginPage imported: {has_login_page_import}")

    # Check for page object initialization
    has_page_init = "self.login_page = LoginPage(web)" in task_code
    print(f"{'[OK]' if has_page_init else '[FAIL]'} LoginPage initialized: {has_page_init}")

    # Check for complete login workflow (no NotImplementedError)
    has_login_method = "def login(self, email: str, password: str) -> bool:" in task_code
    has_no_not_implemented = "raise NotImplementedError" not in task_code
    print(f"{'[OK]' if has_login_method else '[FAIL]'} login() method exists: {has_login_method}")
    print(f"{'[OK]' if has_no_not_implemented else '[FAIL]'} No NotImplementedError: {has_no_not_implemented}")

    # Check for POM method usage
    has_enter_email = "self.login_page.enter_email" in task_code
    has_enter_passwd = "self.login_page.enter_passwd" in task_code
    has_click_submit = "self.login_page.click_submitlogin" in task_code
    print(f"{'[OK]' if has_enter_email else '[FAIL]'} Uses enter_email(): {has_enter_email}")
    print(f"{'[OK]' if has_enter_passwd else '[FAIL]'} Uses enter_passwd(): {has_enter_passwd}")
    print(f"{'[OK]' if has_click_submit else '[FAIL]'} Uses click_submitlogin(): {has_click_submit}")

    # Check for logout workflow
    has_logout_method = "def logout(self) -> bool:" in task_code
    print(f"{'[OK]' if has_logout_method else '[FAIL]'} logout() method exists: {has_logout_method}")

    # STEP 5: Display generated code
    print("\n[STEP 5] Generated Task Code")
    print("-" * 80)
    print(task_code)

    # FINAL VERIFICATION
    print("\n" + "=" * 80)
    all_checks = [
        has_login_page_import,
        has_page_init,
        has_login_method,
        has_no_not_implemented,
        has_enter_email,
        has_enter_passwd,
        has_click_submit,
        has_logout_method
    ]

    if all(all_checks):
        print("[SUCCESS] TOOLS 5->6->4 CHAINING SUCCESSFUL")
        print("[OK] AuthTasks generated with COMPLETE workflows (no scaffolding)")
        print("[OK] POM methods properly used in task workflows")
        print("[OK] login() and logout() workflows fully implemented")
    else:
        print("[FAILURE] Some checks failed")
        failed_count = sum(1 for check in all_checks if not check)
        print(f"✗ {failed_count}/{len(all_checks)} checks failed")

    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_complete_workflow())

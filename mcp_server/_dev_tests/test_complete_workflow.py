"""
Test Complete MCP Workflow: Tools 1->2->3->4->5->6

End-to-end test demonstrating the complete code generation workflow:
1. User Story -> Test Scenarios (Tool 1)
2. Test Scenario -> Pytest Test (Tool 2)
3. Test Requirements -> Role Class (Tool 3)
4. Test Requirements -> Task Class (Tool 4)
5. Page URL -> Discovered Elements (Tool 5)
6. Discovered Elements -> Page Object Model (Tool 6)
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tools.tool_01_generate_tests_from_user_story import generate_tests_from_user_story
from tools.tool_02_generate_test_template import generate_test_template as gen_test_template
from tools.tool_03_generate_role import generate_role
from tools.tool_04_generate_task import generate_task
from tools.tool_05_discover_page_elements import discover_elements
from tools.tool_06_generate_page_object import generate_page_object


async def test_complete_workflow():
    """Test complete code generation workflow."""

    print("=" * 100)
    print("TESTING COMPLETE MCP WORKFLOW: Tools 1->2->3->4->5->6")
    print("=" * 100)

    # ========== STEP 1: User Story -> Test Scenarios ==========
    print("\n[STEP 1] User Story -> Test Scenarios (Tool 1)")
    print("-" * 100)

    user_story = """
    As a registered user
    I want to log in to my account
    So that I can access my personalized shopping experience

    Acceptance Criteria:
    - User can log in with valid credentials
    - User sees error message with invalid credentials
    - User is redirected to My Account page after successful login

    Scenario: Successful login with valid credentials
    Given user is on the login page
    When user enters valid email and password
    And user clicks the Sign In button
    Then user is logged in successfully
    And user is redirected to My Account page
    """

    tool1_args = {
        "user_story": user_story,
        "workflow": "auth"
    }

    tool1_result_str = await generate_tests_from_user_story(tool1_args)
    tool1_result = json.loads(tool1_result_str)

    if tool1_result["status"] != "success":
        print(f"[FAIL] Tool 1 failed: {tool1_result.get('error')}")
        return False

    print(f"[PASS] Tool 1: Generated {len(tool1_result['scenarios'])} test scenarios")
    scenario = tool1_result["scenarios"][0]
    print(f"  Scenario: {scenario['name']}")
    print(f"  Given: {scenario['given']}")
    print(f"  When: {scenario['when']}")
    print(f"  Then: {scenario['then']}")

    # ========== STEP 2: Test Scenario -> Pytest Test ==========
    print("\n[STEP 2] Test Scenario -> Pytest Test (Tool 2)")
    print("-" * 100)

    tool2_args = {
        "test_name": scenario["name"],
        "workflow": "auth",
        "scenario": scenario
    }

    tool2_result_str = await gen_test_template(tool2_args)
    tool2_result = json.loads(tool2_result_str)

    if tool2_result["status"] != "success":
        print(f"[FAIL] Tool 2 failed: {tool2_result.get('error')}")
        return False

    print(f"[PASS] Tool 2: Generated test code")
    print(f"  Test name: {tool2_result['test_name']}")
    print(f"  File path: {tool2_result['file_path']}")
    print(f"\n  Generated test preview (first 500 chars):")
    print("  " + tool2_result["code"][:500].replace("\n", "\n  "))

    # ========== STEP 3: Test Requirements -> Role Class ==========
    print("\n[STEP 3] Test Requirements -> Role Class (Tool 3)")
    print("-" * 100)

    tool3_args = {
        "role_name": "RegisteredUser",
        "capabilities": ["can_login", "can_logout"],
        "credentials": {"email": "test@example.com", "password": "Test123!"}
    }

    tool3_result_str = await generate_role(tool3_args)
    tool3_result = json.loads(tool3_result_str)

    if tool3_result["status"] != "success":
        print(f"[FAIL] Tool 3 failed: {tool3_result.get('error')}")
        return False

    print(f"[PASS] Tool 3: Generated role class")
    print(f"  Role name: {tool3_result['role_name']}")
    print(f"  File path: {tool3_result['file_path']}")
    print(f"  Capabilities: {', '.join(tool3_result['capabilities'])}")

    # ========== STEP 4: Test Requirements -> Task Class ==========
    print("\n[STEP 4] Test Requirements -> Task Class (Tool 4)")
    print("-" * 100)

    tool4_args = {
        "task_name": "AuthTasks",
        "workflow_description": "Authentication workflows: login, logout, password recovery"
    }

    tool4_result_str = await generate_task(tool4_args)
    tool4_result = json.loads(tool4_result_str)

    if tool4_result["status"] != "success":
        print(f"[FAIL] Tool 4 failed: {tool4_result.get('error')}")
        return False

    print(f"[PASS] Tool 4: Generated task class")
    print(f"  Task name: {tool4_result['task_name']}")
    print(f"  File path: {tool4_result['file_path']}")

    # ========== STEP 5: Page URL -> Discovered Elements ==========
    print("\n[STEP 5] Page URL -> Discovered Elements (Tool 5)")
    print("-" * 100)

    tool5_args = {
        "url": "http://www.automationpractice.pl/index.php?controller=authentication",
        "headless": True
    }

    tool5_result_str = await discover_elements(tool5_args)
    tool5_result = json.loads(tool5_result_str)

    if tool5_result["status"] != "success":
        print(f"[FAIL] Tool 5 failed: {tool5_result.get('error')}")
        return False

    print(f"[PASS] Tool 5: Discovered {tool5_result['total_elements']} elements")
    print(f"  Elements by type: {tool5_result['elements_by_type']}")

    # Filter relevant auth elements
    auth_elements = []
    for elem in tool5_result["elements"]:
        name = elem["suggested_name"]
        if any(keyword in name.lower() for keyword in ["email", "passwd", "submit", "login"]):
            auth_elements.append(elem)

    print(f"  Filtered to {len(auth_elements)} auth-related elements")

    # ========== STEP 6: Discovered Elements -> Page Object Model ==========
    print("\n[STEP 6] Discovered Elements -> Page Object Model (Tool 6)")
    print("-" * 100)

    tool6_args = {
        "page_name": "LoginPage",
        "elements": auth_elements,
        "workflow": "auth"
    }

    tool6_result_str = await generate_page_object(tool6_args)
    tool6_result = json.loads(tool6_result_str)

    if tool6_result["status"] != "success":
        print(f"[FAIL] Tool 6 failed: {tool6_result.get('error')}")
        return False

    print(f"[PASS] Tool 6: Generated page object model")
    print(f"  Page name: {tool6_result['page_name']}")
    print(f"  File path: {tool6_result['file_path']}")
    print(f"  Elements count: {tool6_result['elements_count']}")

    # ========== SUMMARY ==========
    print("\n" + "=" * 100)
    print("[SUCCESS] COMPLETE WORKFLOW TEST PASSED!")
    print("=" * 100)

    print("\nGenerated Components Summary:")
    print(f"  1. Test Scenarios: {len(tool1_result['scenarios'])} scenarios from user story")
    print(f"  2. Test File: {tool2_result['file_path']}")
    print(f"  3. Role Class: {tool3_result['file_path']}")
    print(f"  4. Task Class: {tool4_result['file_path']}")
    print(f"  5. Elements Discovered: {tool5_result['total_elements']} total, {len(auth_elements)} relevant")
    print(f"  6. Page Object: {tool6_result['file_path']}")

    print("\nComplete Framework Structure Generated:")
    print("  /tests/auth/")
    print(f"    {tool2_result['test_name']}.py        <- Test with AAA pattern")
    print("  /framework/roles/")
    print(f"    registereduser.py                    <- Role with login capability")
    print("  /framework/tasks/")
    print(f"    authtasks.py                         <- Auth workflow methods")
    print("  /framework/pages/auth/")
    print(f"    loginpage.py                         <- Page object with {tool6_result['elements_count']} locators")

    print("\nWorkflow Chain Verified:")
    print("  User Story -> Scenarios -> Test -> Role -> Task -> Elements -> POM")
    print("  [Tool 1]   -> [Tool 2]   -> [Tool 3] -> [Tool 4] -> [Tool 5] -> [Tool 6]")
    print("     ✓             ✓            ✓           ✓            ✓           ✓")

    print("\n" + "=" * 100)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_complete_workflow())
    sys.exit(0 if success else 1)

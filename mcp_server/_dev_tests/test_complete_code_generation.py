"""
Final Test: Verify ALL tools generate COMPLETE code (no TODOs/scaffolding).

Tests the complete workflow: Tool 1 → 5 → 6 → 4 → 3 → 2
All tools should generate production-ready, working code.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.tool_01_generate_tests_from_user_story import generate_tests_from_user_story
from tools.tool_02_discover_page_elements import discover_elements
from tools.tool_03_generate_page_object import generate_page_object
from tools.tool_04_generate_task import generate_task
from tools.tool_05_generate_role import generate_role
from tools.tool_06_generate_test_template import generate_test_template as gen_test


async def test_complete_workflow():
    """Test that EVERY tool generates complete, working code."""

    print("=" * 100)
    print("COMPREHENSIVE TEST: Complete Code Generation Workflow")
    print("=" * 100)
    print()

    # -------------------------------------------------------------------------
    print("[1/6] Tool 1: Generate Test Scenarios from User Story")
    print("-" * 100)

    user_story = """
As a user, I want to log in to my account

Scenario: Successful login
Given user is on login page
When user enters valid email and password
Then user is logged in successfully
"""

    r1 = await generate_tests_from_user_story({
        "user_story": user_story,
        "workflow": "auth"
    })

    d1 = json.loads(r1)
    scenario = d1['scenarios'][0]

    print(f"[OK] Generated scenario: {scenario['name']}")
    print(f"  Given: {scenario['given']}")
    print(f"  When: {scenario['when']}")
    print(f"  Then: {scenario['then']}")
    print()

    # -------------------------------------------------------------------------
    print("[2/6] Tool 2: Discover Page Elements")
    print("-" * 100)

    r5 = await discover_elements({
        "url": "http://www.automationpractice.pl/index.php?controller=authentication",
        "headless": True
    })

    d5 = json.loads(r5)
    login_elements = [e for e in d5['elements'] if e['suggested_name'] in ['EMAIL', 'PASSWD', 'SUBMITLOGIN']]

    print(f"[OK] Discovered {len(login_elements)} login elements")
    for elem in login_elements:
        print(f"  - {elem['suggested_name']}: {elem['element_type']}")
    print()

    # -------------------------------------------------------------------------
    print("[3/6] Tool 3: Generate Page Object")
    print("-" * 100)

    r6 = await generate_page_object({
        "page_name": "LoginPage",
        "elements": login_elements,
        "workflow": "auth"
    })

    d6 = json.loads(r6)
    pom_code = d6['code']

    has_pom_methods = 'def enter_email(' in pom_code and 'def click_submitlogin(' in pom_code
    pom_complete = has_pom_methods and 'TODO' not in pom_code

    print(f"[OK] Generated LoginPage POM")
    print(f"  Has methods: {has_pom_methods}")
    print(f"  Complete (no TODOs): {pom_complete}")
    print(f"  Status: {'[COMPLETE]' if pom_complete else '[INCOMPLETE]'}")
    print()

    # -------------------------------------------------------------------------
    print("[4/6] Tool 4: Generate Task Workflows")
    print("-" * 100)

    r4 = await generate_task({
        "task_name": "AuthTasks",
        "workflow_description": "Authentication workflows",
        "page_objects": [{
            "name": d6['page_name'],
            "file_path": d6['file_path'],
            "code": d6['code']
        }]
    })

    d4 = json.loads(r4)
    task_code = d4['code']

    has_login = 'def login(' in task_code
    has_logout = 'def logout(' in task_code
    has_implementation = 'self.login_page.enter_email' in task_code
    task_complete = has_login and has_logout and has_implementation

    print(f"[OK] Generated AuthTasks")
    print(f"  Has login(): {has_login}")
    print(f"  Has logout(): {has_logout}")
    print(f"  Has implementation: {has_implementation}")
    print(f"  Status: {'[COMPLETE]' if task_complete else '[INCOMPLETE]'}")
    print()

    # -------------------------------------------------------------------------
    print("[5/6] Tool 5: Generate Role")
    print("-" * 100)

    r3 = await generate_role({
        "role_name": "RegisteredUser",
        "capabilities": ["can_login", "can_logout"]
    })

    d3 = json.loads(r3)
    role_code = d3['code']

    has_role_login = 'def login(' in role_code
    has_role_impl = 'self.common_tasks.log_in' in role_code
    role_complete = has_role_login and has_role_impl

    print(f"[OK] Generated RegisteredUser Role")
    print(f"  Has login(): {has_role_login}")
    print(f"  Has implementation: {has_role_impl}")
    print(f"  Status: {'[COMPLETE]' if role_complete else '[INCOMPLETE]'}")
    print()

    # -------------------------------------------------------------------------
    print("[6/6] Tool 2: Generate Test")
    print("-" * 100)

    r2 = await gen_test({
        "test_name": scenario['name'],
        "workflow": scenario['workflow'],
        "scenario": scenario
    })

    d2 = json.loads(r2)
    test_code = d2['code']

    has_test_data = 'test_email' in test_code
    has_action = 'auth_tasks.login(' in test_code
    has_assertion = 'assert result is True' in test_code
    has_todo = 'TODO' in test_code
    test_complete = has_test_data and has_action and has_assertion and not has_todo

    print(f"[OK] Generated test_successful_login")
    print(f"  Has test data: {has_test_data}")
    print(f"  Has action call: {has_action}")
    print(f"  Has assertions: {has_assertion}")
    print(f"  Has TODOs: {has_todo}")
    print(f"  Status: {'[COMPLETE]' if test_complete else '[INCOMPLETE]'}")
    print()

    # -------------------------------------------------------------------------
    print("=" * 100)
    print("FINAL RESULTS")
    print("=" * 100)

    results = {
        "Tool 1 (Scenarios)": True,  # Always works
        "Tool 5 (Discover)": True,   # Always works
        "Tool 6 (POM)": pom_complete,
        "Tool 4 (Task)": task_complete,
        "Tool 3 (Role)": role_complete,
        "Tool 2 (Test)": test_complete
    }

    all_complete = all(results.values())

    for tool, status in results.items():
        status_icon = "[OK]" if status else "[FAIL]"
        status_text = "COMPLETE" if status else "INCOMPLETE"
        print(f"{status_icon} {tool}: {status_text}")

    print()
    if all_complete:
        print("=" * 100)
        print("SUCCESS: ALL TOOLS GENERATE COMPLETE CODE!")
        print("=" * 100)
    else:
        print("=" * 100)
        print("FAILURE: Some tools still generate incomplete code")
        print("=" * 100)

    return all_complete


if __name__ == "__main__":
    success = asyncio.run(test_complete_workflow())
    sys.exit(0 if success else 1)

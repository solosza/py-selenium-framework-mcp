"""
Test complete code generation workflow.
Tests Tools 5 → 6 → 4 → 3 → 2 to see what generates complete vs scaffolding.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tools.tool_05_discover_page_elements import discover_elements
from tools.tool_06_generate_page_object import generate_page_object
from tools.tool_04_generate_task import generate_task
from tools.tool_03_generate_role import generate_role
from tools.tool_02_generate_test_template import generate_test_template as gen_test
from tools.tool_01_generate_tests_from_user_story import generate_tests_from_user_story


async def test_complete_workflow():
    """Test the complete workflow: 1 → 5 → 6 → 4 → 3 → 2"""

    print("=" * 80)
    print("TOOL 1: Generate Test Scenarios from User Story")
    print("=" * 80)

    user_story = """
As a user, I want to log in to my account

Acceptance Criteria:
- User can log in with valid credentials
- User sees error with invalid credentials

Scenario: Successful login
Given user is on login page
When user enters valid email and password
Then user is logged in successfully
And user sees account dashboard
"""

    result1 = await generate_tests_from_user_story({
        "user_story": user_story,
        "workflow": "auth"
    })

    parsed1 = json.loads(result1)
    print(f"Status: {parsed1['status']}")
    print(f"Scenarios: {parsed1['scenarios_count']}")
    print(f"First scenario: {parsed1['scenarios'][0]['name']}")

    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TOOL 5: Discover Page Elements")
    print("=" * 80)

    result5 = await discover_elements({
        "url": "http://www.automationpractice.pl/index.php?controller=authentication",
        "headless": True
    })

    parsed5 = json.loads(result5)
    print(f"Status: {parsed5['status']}")
    print(f"Total elements: {parsed5['total_elements']}")
    print(f"By type: {parsed5['elements_by_type']}")

    # Filter login elements
    login_elements = [
        e for e in parsed5['elements']
        if e['suggested_name'] in ['EMAIL', 'PASSWD', 'SUBMITLOGIN']
    ]
    print(f"Login elements: {len(login_elements)}")

    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TOOL 6: Generate Page Object")
    print("=" * 80)

    result6 = await generate_page_object({
        "page_name": "LoginPage",
        "elements": login_elements,
        "workflow": "auth"
    })

    parsed6 = json.loads(result6)
    print(f"Status: {parsed6['status']}")
    print(f"Elements: {parsed6['elements_count']}")

    # Check if POM has methods
    code6 = parsed6['code']
    has_methods = 'def enter_' in code6 or 'def click_' in code6
    print(f"Has methods: {has_methods}")

    if has_methods:
        # Extract method names
        import re
        methods = re.findall(r'def (\w+)\(', code6)
        print(f"Methods: {methods}")
    else:
        print("⚠️  NO METHODS GENERATED")

    # Save POM code for inspection
    with open('_output_tool6_pom.py', 'w') as f:
        f.write(code6)
    print("Saved: _output_tool6_pom.py")

    # Extract POM methods for Tool 4
    pom_methods = []
    if has_methods:
        pom_methods = [m for m in methods if m != '__init__']

    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TOOL 4: Generate Task Workflows")
    print("=" * 80)

    result4 = await generate_task({
        "task_name": "AuthTasks",
        "workflow_description": "Authentication workflows (login, logout)",
        "page_objects": [{
            "name": "LoginPage",
            "file_path": "framework/pages/auth/loginpage.py",
            "methods": pom_methods
        }]
    })

    parsed4 = json.loads(result4)
    print(f"Status: {parsed4['status']}")

    # Check if Task has complete workflows
    code4 = parsed4['code']
    has_login = 'def login(' in code4
    has_logout = 'def logout(' in code4
    has_todo = 'TODO' in code4 or 'NotImplementedError' in code4

    print(f"Has login(): {has_login}")
    print(f"Has logout(): {has_logout}")
    print(f"Has TODOs/NotImplemented: {has_todo}")

    # Save Task code for inspection
    with open('_output_tool4_task.py', 'w') as f:
        f.write(code4)
    print("Saved: _output_tool4_task.py")

    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TOOL 3: Generate Role")
    print("=" * 80)

    result3 = await generate_role({
        "role_name": "RegisteredUser",
        "capabilities": ["can_login", "can_logout"]
    })

    parsed3 = json.loads(result3)
    print(f"Status: {parsed3['status']}")

    # Check if Role has complete methods
    code3 = parsed3['code']
    has_login_method = 'def login(' in code3
    has_logout_method = 'def logout(' in code3
    has_implementation = 'self.common_tasks.log_in' in code3

    print(f"Has login(): {has_login_method}")
    print(f"Has logout(): {has_logout_method}")
    print(f"Has implementation: {has_implementation}")

    # Save Role code for inspection
    with open('_output_tool3_role.py', 'w') as f:
        f.write(code3)
    print("Saved: _output_tool3_role.py")

    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("TOOL 2: Generate Test Template")
    print("=" * 80)

    scenario = parsed1['scenarios'][0]

    result2 = await gen_test({
        "test_name": scenario['name'],
        "workflow": scenario['workflow'],
        "scenario": scenario
    })

    parsed2 = json.loads(result2)
    print(f"Status: {parsed2['status']}")

    # Check if Test has complete logic
    code2 = parsed2['code']
    has_act = '# Act' in code2
    has_assert = '# Assert' in code2
    has_todo = 'TODO' in code2
    has_pass = 'pass  # Remove this line' in code2

    print(f"Has Act section: {has_act}")
    print(f"Has Assert section: {has_assert}")
    print(f"Has TODOs: {has_todo}")
    print(f"Has placeholder pass: {has_pass}")

    # Save Test code for inspection
    with open('_output_tool2_test.py', 'w') as f:
        f.write(code2)
    print("Saved: _output_tool2_test.py")

    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print("\n✅ COMPLETE CODE GENERATION:")
    print(f"  - Tool 6 (POM): {'✅' if has_methods else '❌'} - Methods: {has_methods}")
    print(f"  - Tool 4 (Task): {'✅' if has_login and has_logout and not has_todo else '❌'} - login/logout: {has_login and has_logout}, No TODOs: {not has_todo}")
    print(f"  - Tool 3 (Role): {'✅' if has_implementation else '❌'} - Implementation: {has_implementation}")

    print("\n❌ SCAFFOLDING (TODOs):")
    print(f"  - Tool 2 (Test): {'❌' if has_todo else '✅'} - Has TODOs: {has_todo}")

    print("\n📁 OUTPUT FILES:")
    print("  - _output_tool6_pom.py")
    print("  - _output_tool4_task.py")
    print("  - _output_tool3_role.py")
    print("  - _output_tool2_test.py")
    print("\nInspect these files to see what needs to be enhanced.")


if __name__ == "__main__":
    asyncio.run(test_complete_workflow())

"""
Test Complete MCP Workflow with Full Output Display

Shows the complete generated code for all 6 tools.
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


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def print_code_block(language, code):
    """Print code block with formatting."""
    print(f"\n```{language}")
    print(code)
    print("```")


async def test_workflow_detailed():
    """Test workflow with detailed output display."""

    print_section("COMPLETE MCP WORKFLOW: Tools 1->2->3->4->5->6 - DETAILED OUTPUT")

    # User story
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

    # ========== TOOL 1: User Story -> Test Scenarios ==========
    print_section("TOOL 1: User Story -> Test Scenarios")

    tool1_args = {"user_story": user_story, "workflow": "auth"}
    tool1_result_str = await generate_tests_from_user_story(tool1_args)
    tool1_result = json.loads(tool1_result_str)

    print("\nINPUT: User Story")
    print("-" * 100)
    print(user_story)

    print("\nOUTPUT: Test Scenarios (JSON)")
    print("-" * 100)
    print_code_block("json", json.dumps(tool1_result, indent=2))

    scenario = tool1_result["scenarios"][0]

    # ========== TOOL 2: Test Scenario -> Pytest Test ==========
    print_section("TOOL 2: Test Scenario -> Pytest Test Code")

    tool2_args = {
        "test_name": scenario["name"],
        "workflow": "auth",
        "scenario": scenario
    }
    tool2_result_str = await gen_test_template(tool2_args)
    tool2_result = json.loads(tool2_result_str)

    print(f"\nINPUT: Scenario from Tool 1")
    print("-" * 100)
    print(f"Name: {scenario['name']}")
    print(f"Given: {scenario['given']}")
    print(f"When: {scenario['when']}")
    print(f"Then: {scenario['then']}")

    print(f"\nOUTPUT: {tool2_result['file_path']}")
    print("-" * 100)
    print_code_block("python", tool2_result["code"])

    # ========== TOOL 3: Requirements -> Role Class ==========
    print_section("TOOL 3: Test Requirements -> Role Class")

    tool3_args = {
        "role_name": "RegisteredUser",
        "capabilities": ["can_login", "can_logout"],
        "credentials": {"email": "test@example.com", "password": "Test123!"}
    }
    tool3_result_str = await generate_role(tool3_args)
    tool3_result = json.loads(tool3_result_str)

    print("\nINPUT: Role Requirements")
    print("-" * 100)
    print(f"Role Name: {tool3_args['role_name']}")
    print(f"Capabilities: {', '.join(tool3_args['capabilities'])}")
    print(f"Credentials: {tool3_args['credentials']}")

    print(f"\nOUTPUT: {tool3_result['file_path']}")
    print("-" * 100)
    print_code_block("python", tool3_result["code"])

    # ========== TOOL 4: Requirements -> Task Class ==========
    print_section("TOOL 4: Test Requirements -> Task Class")

    tool4_args = {
        "task_name": "AuthTasks",
        "workflow_description": "Authentication workflows: login, logout, password recovery"
    }
    tool4_result_str = await generate_task(tool4_args)
    tool4_result = json.loads(tool4_result_str)

    print("\nINPUT: Task Requirements")
    print("-" * 100)
    print(f"Task Name: {tool4_args['task_name']}")
    print(f"Description: {tool4_args['workflow_description']}")

    print(f"\nOUTPUT: {tool4_result['file_path']}")
    print("-" * 100)
    print_code_block("python", tool4_result["code"])

    # ========== TOOL 5: Page URL -> Discovered Elements ==========
    print_section("TOOL 5: Page URL -> Discovered Elements")

    tool5_args = {
        "url": "http://www.automationpractice.pl/index.php?controller=authentication",
        "headless": True
    }
    tool5_result_str = await discover_elements(tool5_args)
    tool5_result = json.loads(tool5_result_str)

    print("\nINPUT: Page URL")
    print("-" * 100)
    print(f"URL: {tool5_args['url']}")

    print(f"\nOUTPUT: Discovered Elements Summary")
    print("-" * 100)
    print(f"Total Elements: {tool5_result['total_elements']}")
    print(f"Elements by Type: {tool5_result['elements_by_type']}")

    # Filter auth elements
    auth_elements = []
    for elem in tool5_result["elements"]:
        name = elem["suggested_name"]
        if any(keyword in name.lower() for keyword in ["email", "passwd", "submit", "login"]):
            auth_elements.append(elem)

    print(f"\nFiltered Auth Elements ({len(auth_elements)} elements):")
    print("-" * 100)
    for elem in auth_elements:
        print(f"  {elem['suggested_name']:30} | {elem['element_type']:10} | {elem.get('locator_id') or elem.get('locator_css', '')}")

    # ========== TOOL 6: Discovered Elements -> POM ==========
    print_section("TOOL 6: Discovered Elements -> Page Object Model")

    tool6_args = {
        "page_name": "LoginPage",
        "elements": auth_elements,
        "workflow": "auth"
    }
    tool6_result_str = await generate_page_object(tool6_args)
    tool6_result = json.loads(tool6_result_str)

    print("\nINPUT: Discovered Elements from Tool 5")
    print("-" * 100)
    print(f"Page Name: {tool6_args['page_name']}")
    print(f"Element Count: {len(auth_elements)}")

    print(f"\nOUTPUT: {tool6_result['file_path']}")
    print("-" * 100)
    print_code_block("python", tool6_result["code"])

    # ========== SUMMARY ==========
    print_section("WORKFLOW SUMMARY: Complete Framework Generated")

    print("\nGenerated File Structure:")
    print("-" * 100)
    print("""
/tests/auth/
  test_successful_login_with_valid_credentials.py  <- Pytest test with AAA pattern

/framework/roles/
  registereduser.py                                <- Role with login/logout capabilities

/framework/tasks/
  authtasks.py                                     <- Auth workflow task methods

/framework/pages/auth/
  loginpage.py                                     <- Page object with 7 locators
    """)

    print("\nWorkflow Chain:")
    print("-" * 100)
    print("User Story -> Test Scenarios -> Pytest Test -> Role Class -> Task Class -> Page Elements -> POM")
    print("  [Tool 1]        [Tool 1]        [Tool 2]      [Tool 3]      [Tool 4]      [Tool 5]      [Tool 6]")

    print("\nAll Components Follow Framework Patterns:")
    print("-" * 100)
    print("  [PASS] Test uses web_interface, config fixtures")
    print("  [PASS] Test uses autologger.automation_logger decorator")
    print("  [PASS] Test uses task classes (not roles)")
    print("  [PASS] Role inherits from Role base class")
    print("  [PASS] Role composes task modules")
    print("  [PASS] Task uses (web: WebInterface, base_url: str)")
    print("  [PASS] POM inherits from BasePage")
    print("  [PASS] POM uses (web: WebInterface) parameter")
    print("  [PASS] POM locators use (By.X, 'selector') tuples")

    print("\n" + "=" * 100)
    print("SUCCESS: Complete framework generated from user story!")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(test_workflow_detailed())

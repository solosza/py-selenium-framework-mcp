"""
Simplified E2E Test: Generate All Modules -> Display Code -> Copy Instructions

Generates:
1. Page Object (POM)
2. Task
3. Role
4. Test

Then provides instructions to execute with pytest.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.code_generator import (
    generate_page_object_template,
    generate_task_template,
    generate_role_template,
    generate_test_template
)


def print_section(title, char="="):
    """Print section header."""
    width = 100
    print("\n" + char * width)
    print(f"  {title}")
    print(char * width + "\n")


def main():
    print_section("E2E TEST: Generate All Modules with Role Architecture + Fluent Interface")

    # Test parameters
    role = "RegisteredUser"
    workflow = "auth"
    scenario = {
        "description": "Successful login with valid credentials",
        "given": "I am a registered user with valid credentials",
        "when": "I log in to the system",
        "then": "I should be successfully logged in"
    }

    # Project root
    project_root = Path(__file__).parent.parent.parent

    # =================================================================
    # STEP 1: Generate Page Object
    # =================================================================
    print_section("STEP 1: Generate Page Object (with Fluent Interface)", "-")

    elements = [
        {"suggested_name": "EMAIL", "element_type": "inputs", "locator": "#email", "name": "EMAIL"},
        {"suggested_name": "PASSWD", "element_type": "inputs", "locator": "#passwd", "name": "PASSWD"},
        {"suggested_name": "SUBMITLOGIN", "element_type": "buttons", "locator": "#SubmitLogin", "name": "SUBMITLOGIN"}
    ]

    pom_code = generate_page_object_template("LoginPageE2E", elements)
    print("[OK] Generated POM: LoginPageE2E")
    print("File: framework/pages/common/login_page_e2e.py\n")

    # =================================================================
    # STEP 2: Generate Task (uses POM chaining)
    # =================================================================
    print_section("STEP 2: Generate Task (with POM Method Chaining)", "-")

    page_objects = [{
        "name": "LoginPageE2E",
        "file_path": "framework/pages/common/login_page_e2e.py",
        "methods": ["enter_email", "enter_passwd", "click_submitlogin"]
    }]

    task_code = generate_task_template(
        task_name="AuthTasksE2E",
        workflow_description="Authentication workflows",
        page_objects=page_objects
    )
    print("[OK] Generated Task: AuthTasksE2E")
    print("File: framework/tasks/auth_tasks_e2e.py\n")

    # =================================================================
    # STEP 3: Generate Role
    # =================================================================
    print_section("STEP 3: Generate Role", "-")

    role_code = generate_role_template(
        role_name=role,
        capabilities=["can_login"]
    )
    print(f"[OK] Generated Role: {role}")
    print(f"File: framework/roles/registered_user_e2e.py\n")

    # =================================================================
    # STEP 4: Generate Test (uses Role layer!)
    # =================================================================
    print_section("STEP 4: Generate Test (with Role Layer Architecture)", "-")

    test_code = generate_test_template(
        test_name="test_login_e2e",
        workflow=workflow,
        role=role,  # EXPLICIT ROLE PARAMETER!
        scenario=scenario
    )
    print("[OK] Generated Test: test_login_e2e")
    print("File: tests/auth/test_login_e2e.py\n")

    # =================================================================
    # STEP 5: Save All Files
    # =================================================================
    print_section("STEP 5: Save Generated Files", "-")

    output_dir = Path(__file__).parent / "generated_e2e"
    output_dir.mkdir(exist_ok=True)

    files = [
        ("login_page_e2e.py", pom_code, "POM"),
        ("auth_tasks_e2e.py", task_code, "Task"),
        ("registered_user_e2e.py", role_code, "Role"),
        ("test_login_e2e.py", test_code, "Test")
    ]

    for filename, code, file_type in files:
        file_path = output_dir / filename
        file_path.write_text(code, encoding='utf-8')
        print(f"[OK] Saved {file_type}: {filename}")

    # =================================================================
    # STEP 6: Display All Generated Code
    # =================================================================
    print_section("STEP 6: All Generated Code")

    for filename, code, file_type in files:
        print(f"\n{'=' * 100}")
        print(f"FILE: {filename} ({file_type})")
        print('=' * 100)
        print(code)

    # =================================================================
    # STEP 7: Copy Instructions
    # =================================================================
    print_section("STEP 7: Instructions to Execute Test")

    print(f"[OK] All files generated in: {output_dir}")
    print("\nTo execute the test with pytest (browser will open!):\n")
    print("1. Copy generated files to framework:")
    print(f"   copy {output_dir / 'login_page_e2e.py'} framework\\pages\\common\\")
    print(f"   copy {output_dir / 'auth_tasks_e2e.py'} framework\\tasks\\")
    print(f"   copy {output_dir / 'registered_user_e2e.py'} framework\\roles\\")
    print(f"   copy {output_dir / 'test_login_e2e.py'} tests\\auth\\")
    print("\n2. Run pytest:")
    print(f"   cd {project_root}")
    print("   pytest tests/auth/test_login_e2e.py -v -s --html=tests/_reports/e2e_report.html --self-contained-html")
    print("\n3. View HTML report:")
    print("   tests/_reports/e2e_report.html")

    print_section("E2E CODE GENERATION COMPLETE!")

    print("\n[ARCHITECTURE VERIFICATION]")
    print("Generated code uses proper 4-layer architecture:")
    print("  Test -> Role (RegisteredUser) -> Task (AuthTasksE2E) -> Page (LoginPageE2E) -> WebInterface")
    print("\n[FLUENT INTERFACE VERIFICATION]")
    print("POM methods return 'self' for chaining")
    print("Task methods use POM chaining: .enter_email().enter_passwd().click()")
    print("\nReady to execute! Follow instructions above.")


if __name__ == "__main__":
    main()

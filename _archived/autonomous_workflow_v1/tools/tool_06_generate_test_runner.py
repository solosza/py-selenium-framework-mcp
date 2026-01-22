"""
Tool 6: generate_test_runner

Generate pytest test runner code from scenario.
Final step - generates executable test code AFTER all infrastructure is built (Tools 1-5).

METADATA-DRIVEN ARCHITECTURE:
- Accepts Role metadata from Tool 5 (workflow_methods[])
- Accepts POM metadata from Tool 3 (state_methods[])
- Generates Test methods that call actual Role methods
- Generates assertions using actual POM state methods
- No hardcoded method names - all derived from metadata

Tool 1 generates test SCENARIOS (Given-When-Then).
Tool 6 generates test RUNNER (pytest code that executes the scenario).
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use dedicated generator with metadata support
from utils.generators.test_generator import (
    generate_test as generate_test_code,
    generate_test_with_metadata,
    get_file_path
)


async def generate_test_runner(arguments: dict) -> str:
    """
    Generate pytest test runner code using METADATA from Tools 3 and 5.

    METADATA-DRIVEN: Accepts Role and POM metadata to generate Test methods
    that call actual Role methods and assert via actual POM state methods.

    Args:
        arguments: {
            "test_name": str - Test function name or class name
            "workflow": str - Workflow category or folder
            "role_metadata": dict - Role metadata from Tool 5 (preferred)
            "pom_metadata": dict - POM metadata from Tool 3 (preferred)
            "role": str - Legacy: Role class name (deprecated)
            "scenario": dict - Optional scenario with given/when/then (from Tool 1)
            "role_import": str - Legacy: custom import statement for role
        }

    Returns:
        JSON string with generated pytest runner code and metadata
    """
    test_name = arguments.get("test_name", "")
    workflow = arguments.get("workflow", "")
    role_metadata = arguments.get("role_metadata")  # NEW: metadata from Tool 5
    pom_metadata = arguments.get("pom_metadata")    # NEW: metadata from Tool 3
    role = arguments.get("role", "")  # Legacy support
    scenario = arguments.get("scenario", {})
    role_import = arguments.get("role_import", None)

    # Validation
    if not test_name:
        return json.dumps({
            "error": "test_name is required",
            "status": "error"
        }, indent=2)

    if not workflow:
        return json.dumps({
            "error": "workflow is required (auth, catalog, cart, checkout, or custom folder)",
            "status": "error"
        }, indent=2)

    # Ensure test_name starts with 'test_' or 'Test'
    if not test_name.startswith("test_") and not test_name.startswith("Test"):
        test_name = f"test_{test_name}"

    # Determine test class name from test_name
    # test_browse_category -> TestBrowseCategory
    if test_name.startswith("Test"):
        test_class_name = test_name
    else:
        test_class_name = "Test" + "".join(word.capitalize() for word in test_name.replace("test_", "").split("_"))

    try:
        # PREFERRED: Use metadata from Tools 3 and 5
        if role_metadata and pom_metadata:
            # Generate test using metadata-driven approach
            generation_result = generate_test_with_metadata(
                test_class_name=test_class_name,
                role_metadata=role_metadata,
                pom_metadata=pom_metadata,
                workflow=workflow,
                test_description=scenario.get("description", "") if scenario else None
            )

            test_code = generation_result["code"]
            test_metadata = generation_result["metadata"]

            result = {
                "status": "success",
                "test_name": test_name,
                "test_class_name": test_class_name,
                "workflow": workflow,
                "file_path": test_metadata.get("file_path", ""),
                "code": test_code,
                # METADATA for downstream (reporting, validation)
                "metadata": test_metadata,
                "role_used": test_metadata.get("role_used", ""),
                "page_used": test_metadata.get("page_used", ""),
                "test_methods_generated": len(test_metadata.get("test_methods", [])),
                "architecture": f"Test -> {test_metadata.get('role_used', 'Role')} -> Task -> Page -> WebInterface",
                "next_steps": [
                    "Save test code to suggested file path",
                    "Run pytest to execute the test",
                    "Test uses actual Role workflow methods from metadata",
                    "Assertions use actual POM state methods from metadata"
                ]
            }

            return json.dumps(result, indent=2)

        # LEGACY: Fall back to non-metadata approach
        roles = []
        pages = []

        if role:
            # Convert role name to import path
            if role_import and role_import.startswith("from "):
                parts = role_import.split(" import ")
                role_import_path = parts[0].replace("from ", "").strip()
            else:
                role_import_path = role_import or f"roles.{role.lower().replace('user', '_user')}"

            roles.append({
                "name": role,
                "import_path": role_import_path
            })

        # Generate test code using legacy generator
        test_code = generate_test_code(
            test_class_name=test_class_name,
            roles=roles if roles else None,
            pages=pages if pages else None,
            workflow_type=workflow,
            test_description=scenario.get("description", "") if scenario else None
        )

        file_path = get_file_path(test_class_name, workflow)

        result = {
            "status": "success",
            "test_name": test_name,
            "test_class_name": test_class_name,
            "workflow": workflow,
            "role": role,
            "file_path": file_path,
            "code": test_code,
            "architecture": f"Test -> {role or 'Role'} -> Task -> Page -> WebInterface",
            "next_steps": [
                "Save this test code to the suggested file path",
                f"Ensure {role or 'Role'} role exists in framework/roles/",
                "Ensure supporting Task and Page objects exist",
                "Run pytest to execute the test"
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        import traceback
        return json.dumps({
            "error": f"Failed to generate test template: {str(e)}",
            "status": "error",
            "traceback": traceback.format_exc()
        }, indent=2)


# For standalone testing
if __name__ == "__main__":
    import asyncio

    # Test with role_metadata and pom_metadata (new format)
    test_role_metadata = {
        "class_name": "RegisteredUser",
        "import_path": "roles.registered_user",
        "composed_tasks": ["AuthTasks"],
        "workflow_methods": [
            {
                "name": "login",
                "params": [],
                "calls": ["auth_tasks.log_in"]
            }
        ]
    }

    test_pom_metadata = {
        "class_name": "LoginPage",
        "import_path": "pages.auth.login_page",
        "action_methods": [
            {"name": "enter_email", "params": ["text: str"]},
            {"name": "enter_passwd", "params": ["text: str"]},
            {"name": "click_submitlogin", "params": []}
        ],
        "state_methods": [
            {"name": "is_logged_in", "params": []},
            {"name": "is_account_page_displayed", "params": []}
        ]
    }

    test_args = {
        "test_name": "test_login",
        "workflow": "auth",
        "role_metadata": test_role_metadata,
        "pom_metadata": test_pom_metadata,
        "scenario": {
            "description": "Verify user can login with valid credentials"
        }
    }

    result = asyncio.run(generate_test_runner(test_args))
    print(result)

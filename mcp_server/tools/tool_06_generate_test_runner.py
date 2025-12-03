"""
Tool 6: generate_test_runner

Generate pytest test runner code from scenario.
Final step - generates executable test code AFTER all infrastructure is built (Tools 1-5).

Tool 1 generates test SCENARIOS (Given-When-Then).
Tool 6 generates test RUNNER (pytest code that executes the scenario).

REFACTORED: Now uses dedicated test_generator from utils/generators/
which embeds patterns from FRAMEWORK.md Section 4.4.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# NEW: Use dedicated generator with embedded patterns
from utils.generators.test_generator import (
    generate_test as generate_test_code,
    get_file_path
)


async def generate_test_runner(arguments: dict) -> str:
    """
    Generate pytest test runner code from scenario.

    Args:
        arguments: {
            "test_name": str - Test function name
            "workflow": str - Workflow category or folder
            "role": str - Role class name (e.g., RegisteredUser, GuestUser, PayrollManager)
            "scenario": dict - Optional scenario with given/when/then (from Tool 1)
            "role_import": str - Optional custom import statement for role
        }

    Returns:
        JSON string with generated pytest runner code
    """
    test_name = arguments.get("test_name", "")
    workflow = arguments.get("workflow", "")
    role = arguments.get("role", "RegisteredUser")  # Default role
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

    if not role:
        return json.dumps({
            "error": "role is required (e.g., RegisteredUser, GuestUser, PayrollManager)",
            "status": "error"
        }, indent=2)

    # Ensure test_name starts with 'test_'
    if not test_name.startswith("test_"):
        test_name = f"test_{test_name}"

    try:
        # Build role and page configurations for generator
        roles = []
        pages = []

        if role:
            # Convert role name to import path
            # Handle both formats:
            # - Full import: "from roles.devtest2.dev_guest_user import DevGuestUser"
            # - Path only: "roles.devtest2.dev_guest_user"
            if role_import and role_import.startswith("from "):
                # Extract path from full import statement: "from X import Y" -> "X"
                parts = role_import.split(" import ")
                role_import_path = parts[0].replace("from ", "").strip()
            else:
                role_import_path = role_import or f"roles.{role.lower().replace('user', '_user')}"

            roles.append({
                "name": role,
                "import_path": role_import_path
            })

        # Determine test class name from test_name
        # test_browse_category -> TestBrowseCategory
        test_class_name = "Test" + "".join(word.capitalize() for word in test_name.replace("test_", "").split("_"))

        # Generate test code using NEW generator with embedded FRAMEWORK.md patterns
        test_code = generate_test_code(
            test_class_name=test_class_name,
            roles=roles if roles else None,
            pages=pages if pages else None,
            workflow_type=workflow,
            test_description=scenario.get("description", "") if scenario else None
        )

        # Get suggested file path using NEW generator utility
        file_path = get_file_path(test_class_name, workflow)

        # Return result
        result = {
            "status": "success",
            "test_name": test_name,
            "workflow": workflow,
            "role": role,  # Include role in response
            "file_path": file_path,
            "code": test_code,
            "architecture": f"Test -> {role} -> Task -> Page -> WebInterface",
            "next_steps": [
                "Save this test code to the suggested file path",
                f"Ensure {role} role exists in framework/roles/",
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

    # Test with catalog browse scenario
    test_args = {
        "test_name": "test_browse_category",
        "workflow": "catalog",
        "role": "GuestUser",
        "scenario": {
            "description": "Verify user can browse product categories"
        }
    }

    result = asyncio.run(generate_test_runner(test_args))
    print(result)

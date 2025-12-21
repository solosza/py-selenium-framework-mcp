"""
Tool 6: generate_test_template

Generate pytest test code from scenario.
Final step - generates test AFTER all infrastructure is built (Tools 2-5).
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.code_generator import generate_test_template, get_file_path_for_component


async def generate_test_template(arguments: dict) -> str:
    """
    Generate pytest test template from scenario.

    Args:
        arguments: {
            "test_name": str - Test function name
            "workflow": str - Workflow category
            "role": str - Role class name (e.g., RegisteredUser, GuestUser, PayrollManager)
            "scenario": dict - Optional scenario with given/when/then
        }

    Returns:
        JSON string with generated test code
    """
    test_name = arguments.get("test_name", "")
    workflow = arguments.get("workflow", "")
    role = arguments.get("role", "RegisteredUser")  # Default role
    scenario = arguments.get("scenario", {})

    # Validation
    if not test_name:
        return json.dumps({
            "error": "test_name is required",
            "status": "error"
        }, indent=2)

    if not workflow:
        return json.dumps({
            "error": "workflow is required (auth, catalog, cart, checkout)",
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
        # Generate test code using code_generator WITH ROLE PARAMETER
        from utils.code_generator import generate_test_template as gen_test
        test_code = gen_test(test_name, workflow, role, scenario)

        # Get suggested file path
        file_path = get_file_path_for_component("test", test_name, workflow)

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

    # Test with scenario from Tool 1
    test_scenario = {
        "name": "test_add_product_to_cart",
        "description": "Verify user can add product to cart",
        "given": "user is on product detail page",
        "when": "user clicks \"Add to Cart\" button",
        "then": "product is added to cart AND cart counter increments by 1",
        "workflow": "cart"
    }

    test_args = {
        "test_name": test_scenario["name"],
        "workflow": test_scenario["workflow"],
        "scenario": test_scenario
    }

    result = asyncio.run(generate_test_template(test_args))
    print(result)

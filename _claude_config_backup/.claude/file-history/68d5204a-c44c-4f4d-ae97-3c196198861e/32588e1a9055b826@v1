"""
Tool 5: generate_role

Generate role class from test requirements.
Uses output from Tool 4 (generate_task).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.code_generator import generate_role_template, get_file_path_for_component


async def generate_role(arguments: dict) -> str:
    """
    Generate role class template.

    Args:
        arguments: {
            "role_name": str - Role name (e.g., RegisteredUser)
            "capabilities": list - Optional capabilities
            "credentials": dict - Optional credentials
        }

    Returns:
        JSON string with generated role code
    """
    role_name = arguments.get("role_name", "")
    capabilities = arguments.get("capabilities", [])
    credentials = arguments.get("credentials", {})

    if not role_name:
        return json.dumps({
            "error": "role_name is required",
            "status": "error"
        }, indent=2)

    try:
        # Generate role code
        role_code = generate_role_template(role_name, capabilities, credentials)

        # Get file path
        file_path = get_file_path_for_component("role", role_name)

        result = {
            "status": "success",
            "role_name": role_name,
            "file_path": file_path,
            "capabilities": capabilities,
            "code": role_code,
            "next_steps": [
                "Save role code to suggested file path",
                "Implement capability methods",
                "Use role in tests"
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        import traceback
        return json.dumps({
            "error": f"Failed to generate role: {str(e)}",
            "status": "error",
            "traceback": traceback.format_exc()
        }, indent=2)


if __name__ == "__main__":
    import asyncio

    test_args = {
        "role_name": "RegisteredUser",
        "capabilities": ["can_login", "can_logout"],
        "credentials": {"email": "test@example.com", "password": "Test123!"}
    }

    result = asyncio.run(generate_role(test_args))
    print(result)

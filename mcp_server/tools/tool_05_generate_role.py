"""
Tool 5: generate_role

Generate role class from test requirements.
Uses output from Tool 4 (generate_task).

REFACTORED: Now uses dedicated role_generator from utils/generators/
which embeds patterns from FRAMEWORK.md Section 4.3.

IMPORTANT: Before generating, checks if a role already exists for the workflow.
If it does, returns existing role info instead of creating duplicates.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# NEW: Use dedicated generator with embedded patterns
from utils.generators.role_generator import (
    generate_role as generate_role_code,
    get_file_path
)

# Keep existing capability discovery from old module (until fully migrated)
from utils.code_generator import (
    discover_existing_capabilities,
    can_assemble_workflow
)


async def generate_role(arguments: dict) -> str:
    """
    Generate role class template.

    CHECKS EXISTING FIRST: If a role already exists for this workflow,
    returns existing role info instead of generating duplicate code.

    Args:
        arguments: {
            "role_name": str - Role name (e.g., RegisteredUser)
            "workflow": str - Workflow type (auth, catalog, cart, checkout)
            "capabilities": list - Optional capabilities
            "credentials": dict - Optional credentials
            "task_class": str - Optional task class to use
            "task_import": str - Optional import statement for task class
            "force_generate": bool - Skip existing check (default: False)
        }

    Returns:
        JSON string with generated role code OR existing role info
    """
    role_name = arguments.get("role_name", "")
    workflow = arguments.get("workflow", "")
    capabilities = arguments.get("capabilities", [])
    credentials = arguments.get("credentials", {})
    task_class = arguments.get("task_class", None)
    task_import = arguments.get("task_import", None)
    force_generate = arguments.get("force_generate", False)

    if not role_name:
        return json.dumps({
            "error": "role_name is required",
            "status": "error"
        }, indent=2)

    try:
        # CHECK EXISTING FIRST (unless force_generate is True)
        if not force_generate and workflow:
            existing = can_assemble_workflow(workflow)

            if existing.get("existing_role"):
                # Role already exists for this workflow - USE IT
                return json.dumps({
                    "status": "existing_found",
                    "message": f"Role '{existing['existing_role']}' already exists for '{workflow}' workflow",
                    "existing_role": existing["existing_role"],
                    "existing_methods": existing["existing_role_methods"],
                    "recommendation": existing["recommendation"],
                    "action": "USE_EXISTING",
                    "next_steps": [
                        f"Use existing role: {existing['existing_role']}",
                        f"Available methods: {existing['existing_role_methods']}",
                        "Generate test using this role"
                    ]
                }, indent=2)

            # No role but tasks exist - can create role using existing tasks
            if existing.get("existing_tasks"):
                # Proceed with generation, but inform about existing tasks
                task_class = task_class or existing["existing_tasks"][0]

        # Transform task class to generator format
        task_modules = []
        if task_class:
            # Convert task class name to import path
            import_path = task_import or f"tasks.{task_class.lower().replace('tasks', '_tasks')}"
            task_modules.append({
                "name": task_class,
                "import_path": import_path
            })

        # Determine role type based on workflow or name
        role_type = "guest" if "guest" in role_name.lower() else "authenticated"
        if workflow in ("cart", "checkout", "auth"):
            role_type = "authenticated"

        # Generate role code using NEW generator with embedded FRAMEWORK.md patterns
        role_code = generate_role_code(
            role_name=role_name,
            task_modules=task_modules if task_modules else None,
            role_type=role_type,
            requires_credentials=(role_type == "authenticated")
        )

        # Get file path using NEW generator utility
        file_path = get_file_path(role_name)

        result = {
            "status": "success",
            "role_name": role_name,
            "file_path": file_path,
            "workflow": workflow,
            "capabilities": capabilities,
            "using_task": task_class,
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
        "role_name": "GuestUser",
        "workflow": "catalog",
        "task_class": "CatalogTasks",
        "task_import": "tasks.catalog.catalog_tasks",
        "force_generate": True  # Force generation to test new generator
    }

    result = asyncio.run(generate_role(test_args))
    print(result)

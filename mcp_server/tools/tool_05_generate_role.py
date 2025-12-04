"""
Tool 5: generate_role

Generate role class from test requirements.
Uses output from Tool 4 (generate_task).

METADATA-DRIVEN ARCHITECTURE:
- Accepts Task metadata from Tool 4 (not just code)
- Uses metadata to generate Role methods that call actual Task methods
- Outputs Role metadata for Tool 6 (Test generator)
- No hardcoded method names - all derived from Task metadata

IMPORTANT: Before generating, checks if a role already exists for the workflow.
If it does, returns existing role info instead of creating duplicates.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Use dedicated generator with metadata support
from utils.generators.role_generator import (
    generate_role as generate_role_code,
    generate_role_with_metadata,
    get_file_path
)

# Keep existing capability discovery from old module (until fully migrated)
from utils.code_generator import discover_existing_capabilities


async def generate_role(arguments: dict) -> str:
    """
    Generate role class using METADATA from Tool 4.

    METADATA-DRIVEN: Accepts Task metadata to generate Role methods that
    call actual Task methods (no hardcoded method names).

    CHECKS EXISTING FIRST: If a role already exists for this workflow/persona,
    returns existing role info instead of generating duplicate code.

    Args:
        arguments: {
            "role_name": str - Role name (e.g., RegisteredUser)
            "workflow": str - Workflow type (auth, catalog, cart, checkout)
            "task_metadata": dict - Task metadata from Tool 4 (preferred)
            "task_class": str - Legacy: task class to use (deprecated)
            "task_import": str - Legacy: import statement for task class
            "force_generate": bool - Skip existing check (default: False)
        }

    Returns:
        JSON string with generated role code, metadata, OR existing role info
    """
    role_name = arguments.get("role_name", "")
    workflow = arguments.get("workflow", "")
    task_metadata = arguments.get("task_metadata")  # NEW: metadata from Tool 4
    task_class = arguments.get("task_class", None)  # Legacy support
    task_import = arguments.get("task_import", None)
    force_generate = arguments.get("force_generate", False)

    if not role_name:
        return json.dumps({
            "error": "role_name is required",
            "status": "error"
        }, indent=2)

    try:
        # CHECK EXISTING FIRST (unless force_generate is True)
        if not force_generate:
            capabilities = discover_existing_capabilities()

            # roles is organized by domain: {"auth": ["RegisteredUser"], "guest": ["GuestUser"]}
            # Flatten all roles across domains for matching
            all_existing_roles = []
            roles_by_domain = capabilities.get("roles", {})
            for domain, roles in roles_by_domain.items():
                all_existing_roles.extend(roles)

            role_name_lower = role_name.lower()

            # Look for matching role
            matching_roles = []
            for role in all_existing_roles:
                if role_name_lower in role.lower() or role.lower() in role_name_lower:
                    matching_roles.append(role)

            if matching_roles:
                # Get methods for existing roles
                role_methods = {}
                for role in matching_roles:
                    methods = capabilities.get("role_methods", {}).get(role, [])
                    role_methods[role] = methods

                return json.dumps({
                    "status": "existing_found",
                    "message": f"Role(s) already exist that match '{role_name}'",
                    "existing_roles": matching_roles,
                    "role_methods": role_methods,
                    "action": "USE_EXISTING",
                    "next_steps": [
                        f"Use existing role(s): {matching_roles}",
                        "Generate test using this role",
                        "Or use force_generate=True to create new role"
                    ]
                }, indent=2)

        # Build Task metadata list for generator
        task_metadata_list = []

        # PREFERRED: Use task_metadata directly from Tool 4
        if task_metadata:
            task_metadata_list.append(task_metadata)

        # LEGACY: Build minimal metadata from task_class if task_metadata not provided
        elif task_class:
            import_path = task_import or f"tasks.common.{task_class.lower()}"
            task_metadata_list.append({
                "class_name": task_class,
                "import_path": import_path,
                "task_methods": []  # No methods known in legacy mode
            })

        # Determine role type based on workflow or name
        role_type = "guest" if "guest" in role_name.lower() else "authenticated"
        if workflow in ("cart", "checkout", "auth"):
            role_type = "authenticated"

        # Generate role code AND metadata using metadata-driven generator
        generation_result = generate_role_with_metadata(
            role_name=role_name,
            task_metadata_list=task_metadata_list if task_metadata_list else None,
            role_type=role_type,
            requires_credentials=(role_type == "authenticated")
        )

        role_code = generation_result["code"]
        role_metadata = generation_result["metadata"]

        # Get file path
        file_path = get_file_path(role_name)

        result = {
            "status": "success",
            "role_name": role_name,
            "file_path": file_path,
            "workflow": workflow,
            "code": role_code,
            # METADATA for downstream tools (Test generator uses this)
            "metadata": role_metadata,
            "task_metadata_used": len(task_metadata_list),
            "workflow_methods_generated": len(role_metadata.get("workflow_methods", [])),
            "next_steps": [
                "Save role code to suggested file path",
                "Pass metadata to Tool 6 (generate_test_runner) for dynamic Test generation",
                "Import role in tests",
                "Use role workflow methods in tests"
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

    # Test with task_metadata (new format from Tool 4)
    test_task_metadata = {
        "class_name": "AuthTasks",
        "import_path": "tasks.auth.auth_tasks",
        "composed_pages": ["LoginPage"],
        "task_methods": [
            {
                "name": "log_in",
                "params": ["email: str", "password: str"],
                "calls": ["enter_email", "enter_passwd", "click_submitlogin"]
            }
        ]
    }

    test_args = {
        "role_name": "RegisteredUser",
        "workflow": "auth",
        "task_metadata": test_task_metadata,
        "force_generate": True  # Force generation to test new generator
    }

    result = asyncio.run(generate_role(test_args))
    print(result)

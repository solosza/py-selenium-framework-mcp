"""
Tool 4: generate_task

Generate task workflow methods from test requirements.

REFACTORED: Now uses dedicated task_generator from utils/generators/
which embeds patterns from FRAMEWORK.md Section 4.2.

IMPORTANT: Before generating, checks if a task already exists for the workflow.
If it does, returns existing task info instead of creating duplicates.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# NEW: Use dedicated generator with embedded patterns
from utils.generators.task_generator import (
    generate_task as generate_task_code,
    get_file_path
)

# Keep existing capability discovery from old module (until fully migrated)
from utils.code_generator import discover_existing_capabilities


def extract_method_names_from_pom(pom_code: str) -> list:
    """
    Extract method names from generated POM code.

    Args:
        pom_code: POM class code as string

    Returns:
        List of method names (e.g., ['enter_email', 'click_submitlogin'])
    """
    import re

    # Match method definitions: "def method_name(self"
    pattern = r'def\s+([a-z_]+)\(self'
    matches = re.findall(pattern, pom_code)

    # Filter out __init__ and other special methods
    return [m for m in matches if not m.startswith('__')]


async def generate_task(arguments: dict) -> str:
    """
    Generate task class with COMPLETE workflow implementations.

    CHECKS EXISTING FIRST: If a task already exists for this workflow domain,
    returns existing task info instead of generating duplicate code.

    Args:
        arguments: {
            "task_name": str - Task name (e.g., CatalogTasks)
            "workflow": str - Workflow domain (auth, catalog, cart, checkout)
            "workflow_description": str - Optional workflow description
            "page_objects": list - Optional list of page object dicts
            "force_generate": bool - Skip existing check (default: False)
        }

    Returns:
        JSON string with generated task code OR existing task info
    """
    task_name = arguments.get("task_name", "")
    workflow = arguments.get("workflow", "")
    workflow_description = arguments.get("workflow_description", "")
    page_objects_input = arguments.get("page_objects", [])
    force_generate = arguments.get("force_generate", False)

    if not task_name:
        return json.dumps({
            "error": "task_name is required",
            "status": "error"
        }, indent=2)

    try:
        # CHECK EXISTING FIRST (unless force_generate is True)
        if not force_generate and workflow:
            capabilities = discover_existing_capabilities()

            # Check if tasks exist for this workflow domain
            existing_tasks = capabilities.get("tasks", {}).get(workflow, [])
            # Also check common tasks (often handles auth)
            common_tasks = capabilities.get("tasks", {}).get("common", [])

            all_existing = existing_tasks + common_tasks

            if all_existing:
                # Get methods for existing tasks
                task_methods = {}
                for task in all_existing:
                    methods = capabilities.get("task_methods", {}).get(task, [])
                    task_methods[task] = methods

                return json.dumps({
                    "status": "existing_found",
                    "message": f"Task(s) already exist for '{workflow}' workflow",
                    "existing_tasks": all_existing,
                    "task_methods": task_methods,
                    "action": "USE_EXISTING",
                    "next_steps": [
                        f"Use existing task(s): {all_existing}",
                        "Generate Role that uses these tasks",
                        "Or use force_generate=True to create new task"
                    ]
                }, indent=2)

        # Transform page objects to generator format
        page_objects = []
        if page_objects_input:
            for page_obj in page_objects_input:
                page_name = page_obj.get("name", "")
                page_file = page_obj.get("file_path", "")

                if page_name:
                    # Convert file path to import path
                    # e.g., "framework/pages/auth/login_page.py" -> "pages.auth.login_page"
                    import_path = page_file.replace("framework/", "").replace("/", ".").replace(".py", "") if page_file else ""

                    page_objects.append({
                        "name": page_name,
                        "import_path": import_path
                    })

        # Generate task code using NEW generator with embedded FRAMEWORK.md patterns
        task_code = generate_task_code(
            task_name=task_name,
            page_objects=page_objects if page_objects else None,
            workflow_type=workflow,
            task_description=workflow_description
        )

        # Get file path using NEW generator utility
        file_path = get_file_path(task_name, workflow or "common")

        result = {
            "status": "success",
            "task_name": task_name,
            "file_path": file_path,
            "workflow": workflow,
            "code": task_code,
            "page_objects_used": len(page_objects),
            "workflows_generated": "COMPLETE" if page_objects else "PLACEHOLDER",
            "next_steps": [
                "Save task code to suggested file path",
                "Import task in role classes",
                "Use task methods in tests",
                "Verify workflows execute correctly"
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        import traceback
        return json.dumps({
            "error": f"Failed to generate task: {str(e)}",
            "status": "error",
            "traceback": traceback.format_exc()
        }, indent=2)


if __name__ == "__main__":
    import asyncio

    test_args = {
        "task_name": "CatalogTasks",
        "workflow": "catalog",
        "workflow_description": "Browse and filter product catalog",
        "page_objects": [
            {"name": "ProductListPage", "file_path": "framework/pages/catalog/product_list_page.py"}
        ],
        "force_generate": True  # Force generation to test new generator
    }

    result = asyncio.run(generate_task(test_args))
    print(result)

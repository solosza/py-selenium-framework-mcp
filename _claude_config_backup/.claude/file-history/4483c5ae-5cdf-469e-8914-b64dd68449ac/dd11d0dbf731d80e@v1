"""
Tool 4: generate_task

Generate task workflow methods from test requirements.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.code_generator import generate_task_template, get_file_path_for_component


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

    Args:
        arguments: {
            "task_name": str - Task name (e.g., CatalogTasks)
            "workflow_description": str - Optional workflow description
            "page_objects": list - Optional list of page object dicts from Tool 6:
                [{
                    "name": str - Page class name (e.g., LoginPage)
                    "file_path": str - Page file path
                    "code": str - POM code (to extract methods)
                }]
        }

    Returns:
        JSON string with generated task code
    """
    task_name = arguments.get("task_name", "")
    workflow_description = arguments.get("workflow_description", "")
    page_objects_input = arguments.get("page_objects", [])

    if not task_name:
        return json.dumps({
            "error": "task_name is required",
            "status": "error"
        }, indent=2)

    try:
        # Transform page objects to include extracted methods
        page_objects = []
        if page_objects_input:
            for page_obj in page_objects_input:
                page_name = page_obj.get("name", "")
                page_file = page_obj.get("file_path", "")
                page_code = page_obj.get("code", "")

                if page_name and page_file:
                    # Extract method names from POM code
                    methods = extract_method_names_from_pom(page_code)

                    page_objects.append({
                        "name": page_name,
                        "file_path": page_file,
                        "methods": methods
                    })

        # Generate task code with complete workflows
        task_code = generate_task_template(
            task_name,
            workflow_description,
            page_objects if page_objects else None
        )

        # Get file path
        file_path = get_file_path_for_component("task", task_name)

        result = {
            "status": "success",
            "task_name": task_name,
            "file_path": file_path,
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
        "task_name": "CartTasks",
        "workflow_description": "Manage shopping cart operations: add, remove, update quantities"
    }

    result = asyncio.run(generate_task(test_args))
    print(result)

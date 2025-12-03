"""
Tool 4: generate_task

Generate task workflow methods from test requirements.

METADATA-DRIVEN ARCHITECTURE:
- Accepts POM metadata from Tool 3 (not just code)
- Uses metadata to generate Task methods that call actual POM methods
- Outputs Task metadata for Tool 5 (Role generator)
- No hardcoded method names - all derived from POM metadata

IMPORTANT: Before generating, checks if a task already exists for the workflow.
If it does, returns existing task info instead of creating duplicates.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Use dedicated generator with metadata support
from utils.generators.task_generator import (
    generate_task_with_metadata,
    get_file_path
)

# Keep existing capability discovery from old module (until fully migrated)
from utils.code_generator import discover_existing_capabilities


async def generate_task(arguments: dict) -> str:
    """
    Generate task class using METADATA from Tool 3.

    METADATA-DRIVEN: Accepts POM metadata to generate Task methods that
    call actual POM methods (no hardcoded method names).

    CHECKS EXISTING FIRST: If a task already exists for this workflow domain,
    returns existing task info instead of generating duplicate code.

    Args:
        arguments: {
            "task_name": str - Task name (e.g., CatalogTasks)
            "workflow": str - Workflow domain (auth, catalog, cart, checkout)
            "workflow_description": str - Optional workflow description
            "pom_metadata": dict - POM metadata from Tool 3 (preferred)
            "page_objects": list - Legacy: list of page object dicts (deprecated)
            "force_generate": bool - Skip existing check (default: False)
            "base_url_path": str - URL path for navigation (optional)
        }

    Returns:
        JSON string with generated task code, metadata, OR existing task info
    """
    task_name = arguments.get("task_name", "")
    workflow = arguments.get("workflow", "")
    workflow_description = arguments.get("workflow_description", "")
    pom_metadata = arguments.get("pom_metadata")  # NEW: metadata from Tool 3
    page_objects_input = arguments.get("page_objects", [])  # Legacy support
    force_generate = arguments.get("force_generate", False)
    base_url_path = arguments.get("base_url_path", "")

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

        # Build POM metadata list for generator
        pom_metadata_list = []

        # PREFERRED: Use pom_metadata directly from Tool 3
        if pom_metadata:
            pom_metadata_list.append(pom_metadata)

        # LEGACY: Extract from page_objects if pom_metadata not provided
        elif page_objects_input:
            for page_obj in page_objects_input:
                # Check if this has metadata (new format)
                if "metadata" in page_obj:
                    pom_metadata_list.append(page_obj["metadata"])
                else:
                    # Legacy format - build minimal metadata
                    page_name = page_obj.get("name", "")
                    page_file = page_obj.get("file_path", "")

                    if page_name:
                        import_path = page_file.replace("framework/", "").replace("/", ".").replace(".py", "") if page_file else ""
                        pom_metadata_list.append({
                            "class_name": page_name,
                            "import_path": import_path,
                            "action_methods": [],
                            "state_methods": []
                        })

        # Generate task code AND metadata using metadata-driven generator
        generation_result = generate_task_with_metadata(
            task_name=task_name,
            pom_metadata_list=pom_metadata_list if pom_metadata_list else None,
            task_description=workflow_description,
            base_url_path=base_url_path,
            workflow=workflow or "common"
        )

        task_code = generation_result["code"]
        task_metadata = generation_result["metadata"]

        # Get file path
        file_path = get_file_path(task_name, workflow or "common")

        result = {
            "status": "success",
            "task_name": task_name,
            "file_path": file_path,
            "workflow": workflow,
            "code": task_code,
            # METADATA for downstream tools (Role generator uses this)
            "metadata": task_metadata,
            "pom_metadata_used": len(pom_metadata_list),
            "task_methods_generated": len(task_metadata.get("task_methods", [])),
            "next_steps": [
                "Save task code to suggested file path",
                "Pass metadata to Tool 5 (generate_role) for dynamic Role generation",
                "Import task in role classes",
                "Use task methods in tests"
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

"""
Tool 3: generate_page_object

Generate Page Object Model code from discovered elements.
Uses output from Tool 2 (discover_page_elements).

REFACTORED: Now uses dedicated page_object_generator from utils/generators/
which embeds patterns from FRAMEWORK.md Section 4.1.

IMPORTANT: Before generating, checks if a page already exists for the workflow.
If it does, returns existing page info instead of creating duplicates.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# NEW: Use dedicated generator with embedded patterns and metadata support
from utils.generators.page_object_generator import (
    generate_page_object as generate_pom_code,
    generate_page_object_with_metadata,
    get_file_path
)

# Keep existing capability discovery from old module (until fully migrated)
from utils.code_generator import discover_existing_capabilities


def _detect_workflow_type(page_name: str, workflow: str = "") -> str:
    """Detect workflow type from page name or workflow argument."""
    combined = f"{page_name} {workflow}".lower()

    # Auth keywords
    if any(kw in combined for kw in ["auth", "login", "logout", "register", "signin"]):
        return "auth"

    # Catalog keywords
    if any(kw in combined for kw in ["catalog", "category", "product", "browse", "filter", "sort"]):
        return "catalog"

    # Cart keywords
    if any(kw in combined for kw in ["cart", "basket", "shopping"]):
        return "cart"

    return ""


async def generate_page_object(arguments: dict) -> str:
    """
    Generate POM code from discovered elements.

    CHECKS EXISTING FIRST: If a page already exists for this workflow,
    returns existing page info instead of generating duplicate code.

    Args:
        arguments: {
            "page_name": str - Page class name (e.g., LoginPage)
            "elements": list - List of element dicts from Tool 2
            "workflow": str - Optional workflow for file path (e.g., "auth")
            "force_generate": bool - Skip existing check (default: False)
            "expected_states": list - Optional list of expected state dicts from AI Step 2
                Each dict has {name, description} - generates state-check methods
                Example: [{"name": "is_logged_in", "description": "user is logged in"}]
        }

    Returns:
        JSON string with generated POM code OR existing page info
    """
    page_name = arguments.get("page_name", "")
    elements = arguments.get("elements", [])
    workflow = arguments.get("workflow", "")
    force_generate = arguments.get("force_generate", False)
    expected_states = arguments.get("expected_states", [])

    if not page_name:
        return json.dumps({
            "error": "page_name is required",
            "status": "error"
        }, indent=2)

    if not elements:
        return json.dumps({
            "error": "elements list is required (use Tool 2 to discover elements)",
            "status": "error"
        }, indent=2)

    # Detect workflow type from page name or workflow argument
    workflow_type = _detect_workflow_type(page_name, workflow) or workflow

    try:
        # CHECK EXISTING FIRST (unless force_generate is True)
        if not force_generate and workflow_type:
            capabilities = discover_existing_capabilities()

            # Check if pages exist for this workflow domain
            existing_pages = capabilities.get("pages", {}).get(workflow_type, [])

            if existing_pages:
                # Check if a page with similar name already exists
                page_name_lower = page_name.lower()
                matching_pages = [p for p in existing_pages if page_name_lower in p.lower() or p.lower() in page_name_lower]

                if matching_pages:
                    return json.dumps({
                        "status": "existing_found",
                        "message": f"Page(s) already exist for '{workflow_type}' workflow",
                        "existing_pages": existing_pages,
                        "matching_pages": matching_pages,
                        "action": "USE_EXISTING",
                        "next_steps": [
                            f"Use existing page(s): {matching_pages}",
                            "Generate Task that uses these pages",
                            "Or use force_generate=True to create new page"
                        ]
                    }, indent=2)

        # Transform Tool 2 output to generator format
        transformed_elements = []

        for elem in elements:
            # Priority: ID > CSS > XPath
            locator = elem.get("locator_id") or elem.get("locator_css") or elem.get("locator_xpath", "")
            name = elem.get("suggested_name", "")
            element_type = elem.get("element_type", "")

            if locator and name:
                transformed_elements.append({
                    "suggested_name": name,  # Generator expects suggested_name
                    "locator": locator,
                    "element_type": element_type  # PRESERVE for method generation
                })

        # Generate POM code AND metadata using NEW generator
        # Metadata is used by downstream tools (Task, Role, Test generators)
        # expected_states from AI Step 2 generates state-check methods (PRD FR-15, FR-16)
        generation_result = generate_page_object_with_metadata(
            page_name=page_name,
            elements=transformed_elements,
            workflow_type=workflow_type,
            page_description=f"{page_name} - Page Object Model",
            workflow=workflow_type or "common",
            expected_states=expected_states
        )

        pom_code = generation_result["code"]
        metadata = generation_result["metadata"]

        # Get file path using NEW generator utility
        file_path = get_file_path(page_name, workflow_type or "common")

        result = {
            "status": "success",
            "page_name": page_name,
            "file_path": file_path,
            "workflow": workflow_type,
            "elements_count": len(transformed_elements),
            "code": pom_code,
            # METADATA for downstream tools (Task generator uses this)
            "metadata": metadata,
            "next_steps": [
                "Save POM code to suggested file path",
                "Pass metadata to Tool 4 (generate_task) for dynamic Task generation",
                "Import POM in task methods",
                "Use POM methods in task workflows"
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        import traceback
        return json.dumps({
            "error": f"Failed to generate POM: {str(e)}",
            "status": "error",
            "traceback": traceback.format_exc()
        }, indent=2)


if __name__ == "__main__":
    import asyncio

    # Test with sample discovered elements (from Tool 2 output)
    test_elements = [
        {
            "suggested_name": "email",
            "locator_id": "#email",
            "element_type": "inputs"
        },
        {
            "suggested_name": "passwd",
            "locator_id": "#passwd",
            "element_type": "inputs"
        },
        {
            "suggested_name": "submitlogin",
            "locator_id": "#SubmitLogin",
            "element_type": "buttons"
        }
    ]

    test_args = {
        "page_name": "LoginPage",
        "elements": test_elements,
        "workflow": "auth",
        "force_generate": True  # Force generation to test new generator
    }

    result = asyncio.run(generate_page_object(test_args))
    print(result)

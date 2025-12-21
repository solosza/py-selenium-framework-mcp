"""
Tool 3: generate_page_object

Generate Page Object Model code from discovered elements.
Uses output from Tool 2 (discover_page_elements).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.code_generator import generate_page_object_template, get_file_path_for_component


async def generate_page_object(arguments: dict) -> str:
    """
    Generate POM code from discovered elements.

    Args:
        arguments: {
            "page_name": str - Page class name (e.g., LoginPage)
            "elements": list - List of element dicts from Tool 5
            "workflow": str - Optional workflow for file path (e.g., "auth")
        }

    Returns:
        JSON string with generated POM code
    """
    page_name = arguments.get("page_name", "")
    elements = arguments.get("elements", [])
    workflow = arguments.get("workflow", "")

    if not page_name:
        return json.dumps({
            "error": "page_name is required",
            "status": "error"
        }, indent=2)

    if not elements:
        return json.dumps({
            "error": "elements list is required (use Tool 5 to discover elements)",
            "status": "error"
        }, indent=2)

    try:
        # Transform Tool 5 output to code_generator format
        # Tool 5 provides: suggested_name, locator_id, locator_css, locator_xpath
        # code_generator expects: name, locator
        transformed_elements = []

        for elem in elements:
            # Priority: ID > CSS > XPath
            locator = elem.get("locator_id") or elem.get("locator_css") or elem.get("locator_xpath", "")
            name = elem.get("suggested_name", "")
            element_type = elem.get("element_type", "")

            if locator and name:
                transformed_elements.append({
                    "name": name,
                    "locator": locator,
                    "element_type": element_type  # PRESERVE for method generation
                })

        # Generate POM code
        pom_code = generate_page_object_template(page_name, transformed_elements)

        # Get file path
        file_path = get_file_path_for_component("page", page_name, workflow)

        result = {
            "status": "success",
            "page_name": page_name,
            "file_path": file_path,
            "elements_count": len(transformed_elements),
            "code": pom_code,
            "next_steps": [
                "Save POM code to suggested file path",
                "Import POM in task methods",
                "Use POM methods in task workflows",
                "Write tests that use task methods"
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

    # Test with sample discovered elements (from Tool 5 output)
    test_elements = [
        {
            "suggested_name": "EMAIL_CREATE",
            "locator_id": "#email_create",
            "locator_css": "",
            "locator_xpath": "//input[@id='email_create']"
        },
        {
            "suggested_name": "SUBMITCREATE",
            "locator_id": "#SubmitCreate",
            "locator_css": "",
            "locator_xpath": "//button[@id='SubmitCreate']"
        },
        {
            "suggested_name": "EMAIL",
            "locator_id": "#email",
            "locator_css": "",
            "locator_xpath": "//input[@id='email']"
        },
        {
            "suggested_name": "PASSWD",
            "locator_id": "#passwd",
            "locator_css": "",
            "locator_xpath": "//input[@id='passwd']"
        },
        {
            "suggested_name": "SUBMITLOGIN",
            "locator_id": "#SubmitLogin",
            "locator_css": "",
            "locator_xpath": "//button[@id='SubmitLogin']"
        }
    ]

    test_args = {
        "page_name": "LoginPage",
        "elements": test_elements,
        "workflow": "auth"
    }

    result = asyncio.run(generate_page_object(test_args))
    print(result)

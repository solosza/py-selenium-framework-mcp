"""
Test Tools 5->6 Chaining

Verify that Tool 5 (discover elements) output can be used as input to Tool 6 (generate POM).
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tools.tool_05_discover_page_elements import discover_elements
from tools.tool_06_generate_page_object import generate_page_object


async def test_tools_chain():
    """Test complete workflow: discover elements -> generate POM."""

    print("=" * 80)
    print("TESTING TOOLS 5->6 CHAINING")
    print("=" * 80)

    # Step 1: Discover elements using Tool 5
    print("\n[STEP 1] Running Tool 5 - Discover Elements")
    print("-" * 80)

    tool5_args = {
        "url": "http://www.automationpractice.pl/index.php?controller=authentication",
        "headless": True
    }

    tool5_result_str = await discover_elements(tool5_args)
    tool5_result = json.loads(tool5_result_str)

    if tool5_result["status"] != "success":
        print(f"[FAIL] Tool 5 FAILED: {tool5_result.get('error')}")
        return False

    print(f"[PASS] Tool 5 SUCCESS: Discovered {tool5_result['total_elements']} elements")
    print(f"   Elements by type: {tool5_result['elements_by_type']}")

    # Step 2: Filter elements (optional - select only relevant ones)
    print("\n[STEP 2] Filtering Elements for POM")
    print("-" * 80)

    # For login page, we want: email inputs, password input, submit buttons
    relevant_elements = []
    for elem in tool5_result["elements"]:
        name = elem["suggested_name"]
        # Select authentication-related elements
        if any(keyword in name.lower() for keyword in ["email", "passwd", "submit", "login", "create"]):
            relevant_elements.append(elem)

    print(f"[PASS] Filtered to {len(relevant_elements)} relevant elements:")
    for elem in relevant_elements:
        print(f"   - {elem['suggested_name']} ({elem['element_type']})")

    # Step 3: Generate POM using Tool 6
    print("\n[STEP 3] Running Tool 6 - Generate Page Object")
    print("-" * 80)

    tool6_args = {
        "page_name": "LoginPage",
        "elements": relevant_elements,
        "workflow": "auth"
    }

    tool6_result_str = await generate_page_object(tool6_args)
    tool6_result = json.loads(tool6_result_str)

    if tool6_result["status"] != "success":
        print(f"[FAIL] Tool 6 FAILED: {tool6_result.get('error')}")
        return False

    print(f"[PASS] Tool 6 SUCCESS: Generated {tool6_result['page_name']}")
    print(f"   File path: {tool6_result['file_path']}")
    print(f"   Elements count: {tool6_result['elements_count']}")

    # Step 4: Display generated code
    print("\n[STEP 4] Generated POM Code")
    print("-" * 80)
    print(tool6_result["code"])

    # Success
    print("=" * 80)
    print("[SUCCESS] TOOLS 5->6 CHAINING SUCCESSFUL")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_tools_chain())
    sys.exit(0 if success else 1)

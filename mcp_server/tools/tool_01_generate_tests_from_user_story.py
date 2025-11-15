"""
Tool 1: generate_tests_from_user_story

Converts user story into test scenarios (Given-When-Then format).
First tool in the test-first workflow.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.requirements_parser import (
    parse_user_story,
    generate_test_name,
    validate_scenario
)


async def generate_tests_from_user_story(arguments: dict) -> str:
    """
    Convert user story into structured test scenarios.

    Args:
        arguments: {
            "user_story": str - User story with acceptance criteria
            "workflow": str - Target workflow (auth, catalog, cart, checkout)
        }

    Returns:
        JSON string with array of test scenarios
    """
    user_story = arguments.get("user_story", "")
    workflow = arguments.get("workflow", "")

    if not user_story:
        return json.dumps({
            "error": "user_story is required",
            "status": "error"
        }, indent=2)

    if not workflow:
        return json.dumps({
            "error": "workflow is required (auth, catalog, cart, checkout)",
            "status": "error"
        }, indent=2)

    try:
        # Parse user story
        parsed = parse_user_story(user_story)

        # Extract scenarios
        scenarios = parsed["scenarios"]

        if not scenarios:
            return json.dumps({
                "error": "No scenarios found in user story. Please include Given-When-Then scenarios.",
                "status": "error",
                "hint": "Format: Given <context> When <action> Then <expected outcome>"
            }, indent=2)

        # Generate test scenarios
        test_scenarios = []

        for scenario in scenarios:
            if not validate_scenario(scenario):
                continue  # Skip invalid scenarios

            test_name = generate_test_name(scenario, workflow)

            test_scenario = {
                "name": test_name,
                "description": f"Verify {scenario.get('when', 'scenario')}",
                "given": scenario.get("given", ""),
                "when": scenario.get("when", ""),
                "then": scenario.get("then", ""),
                "workflow": workflow
            }

            test_scenarios.append(test_scenario)

        # Return structured JSON
        result = {
            "status": "success",
            "user_story_title": parsed["title"],
            "workflow": workflow,
            "scenarios_count": len(test_scenarios),
            "scenarios": test_scenarios,
            "next_step": "Use generate_test_template to create pytest test code from these scenarios"
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        return json.dumps({
            "error": f"Failed to parse user story: {str(e)}",
            "status": "error",
            "traceback": traceback.format_exc()
        }, indent=2)


# For standalone testing
if __name__ == "__main__":
    import asyncio

    # Test with sample user story
    sample_user_story = """
As a user, I want to add products to my shopping cart

Acceptance Criteria:
- User can add product from product detail page
- Cart counter updates when product is added
- Success confirmation is displayed

Scenario: Add product to cart from detail page
Given user is on product detail page
When user clicks "Add to Cart" button
Then product is added to cart
And cart counter increments by 1
And success modal is displayed
"""

    test_args = {
        "user_story": sample_user_story,
        "workflow": "cart"
    }

    result = asyncio.run(generate_tests_from_user_story(test_args))
    print(result)

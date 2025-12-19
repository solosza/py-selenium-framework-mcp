"""
SR QA Engineer Agent Tool

Simulates a Senior QA Engineer (SDET) who:
1. Provides test requirements (Step 1 input)
2. Instructs AI Orchestrator to invoke the testing skill

Design Decisions:
- DD-VA-01: Four-component architecture (Supervisor, SQA, AI Orchestrator, Reviewer)
- DD-VA-02: SQA Agent MUST invoke skill (not just provide requirements) - CRITICAL
- DD-VA-03: Domain Expert as custom tool (in-process, fast)

Architecture Role:
```
SUPERVISOR (coordinates agents)
    |
    v
SQA AGENT (this tool - provides requirements + invokes skill)
    |
    v
AI ORCHESTRATOR (Claude Code + MCP tools - executes 9-step)
    |
    v
REVIEWER (validates artifacts)
```

Output Format:
{
    "id": "QA-<LEVEL>-<NUM>",
    "persona": "As a <user type>",
    "requirement": "I want to <action> so that <benefit>",
    "url": "<target page URL>",
    "complexity": "easy|mid|hard",
    "expected_artifacts": [...],
    "validation_points": [...],
    "next_action": {
        "instruction": "Invoke skill to trigger AI Orchestrator",
        "skill": "/skill execute-from-step1",
        "input": "<formatted Step 1 input>"
    }
}
"""

import json
from typing import Dict, Any, List
from claude_agent_sdk import tool


# =============================================================================
# Site Knowledge: automationpractice.pl
# =============================================================================

SITE_KNOWLEDGE = {
    "base_url": "http://www.automationpractice.pl/index.php",
    "pages": {
        "home": {
            "url": "http://www.automationpractice.pl/index.php",
            "description": "Main landing page with featured products"
        },
        "authentication": {
            "url": "http://www.automationpractice.pl/index.php?controller=authentication",
            "description": "Login and registration page"
        },
        "women_category": {
            "url": "http://www.automationpractice.pl/index.php?id_category=3&controller=category",
            "description": "Women's clothing category page"
        },
        "product_detail": {
            "url": "http://www.automationpractice.pl/index.php?id_product=1&controller=product",
            "description": "Product detail page (Faded Short Sleeve T-shirts)"
        },
        "cart": {
            "url": "http://www.automationpractice.pl/index.php?controller=order",
            "description": "Shopping cart page"
        },
        "contact": {
            "url": "http://www.automationpractice.pl/index.php?controller=contact",
            "description": "Contact us form"
        }
    },
    "user_types": [
        "new user",
        "registered user",
        "guest user"
    ],
    "features": [
        "authentication",
        "catalog browsing",
        "product search",
        "cart management",
        "checkout",
        "contact form"
    ]
}


# =============================================================================
# Pre-defined Scenarios
# =============================================================================

SCENARIOS: Dict[str, Dict[str, Any]] = {
    # Easy scenarios - static elements, simple flow
    "QA-EASY-001": {
        "id": "QA-EASY-001",
        "name": "Create new account with valid data",
        "complexity": "easy",
        "persona": "new user",
        "requirement": "As a new user, I want to create an account with my email so that I can shop on the site",
        "url": SITE_KNOWLEDGE["pages"]["authentication"]["url"],
        "expected_artifacts": [
            "framework/pages/auth/registration_page.py",
            "framework/tasks/auth/auth_tasks.py",
            "framework/roles/new_user.py",
            "tests/auth/test_registration.py"
        ],
        "validation_points": [
            {"dd_id": "DD-03", "check": "Locators only in RegistrationPage"},
            {"dd_id": "DD-15", "check": "Test uses is_account_created() for assertion"},
            {"dd_id": "DD-17", "check": "Actual email/form values injected"}
        ],
        "notes": "Static form elements, registration flow. Use unique email (timestamp-based)."
    },

    "QA-EASY-002": {
        "id": "QA-EASY-002",
        "name": "Navigate to contact page",
        "complexity": "easy",
        "persona": "guest user",
        "requirement": "As a guest user, I want to navigate to the contact page so that I can see the contact form",
        "url": SITE_KNOWLEDGE["pages"]["home"]["url"],
        "expected_artifacts": [
            "framework/pages/common/header_page.py",
            "framework/pages/contact/contact_page.py",
            "framework/tasks/navigation/navigation_tasks.py",
            "tests/navigation/test_contact_navigation.py"
        ],
        "validation_points": [
            {"dd_id": "DD-03", "check": "Locators only in Page Objects"},
            {"dd_id": "DD-12", "check": "Check existing before generating new"}
        ],
        "notes": "Simple navigation, no dynamic elements"
    },

    # Mid scenarios - some dynamic elements, standard variations
    "QA-MID-001": {
        "id": "QA-MID-001",
        "name": "Browse products by category",
        "complexity": "mid",
        "persona": "guest user",
        "requirement": "As a guest user, I want to browse products in the Women category so that I can see available items",
        "url": SITE_KNOWLEDGE["pages"]["home"]["url"],
        "expected_artifacts": [
            "framework/pages/catalog/category_page.py",
            "framework/tasks/catalog/catalog_tasks.py",
            "framework/roles/guest_user.py",
            "tests/catalog/test_browse_category.py"
        ],
        "validation_points": [
            {"dd_id": "DD-03", "check": "Locators only in CategoryPage"},
            {"dd_id": "DD-09", "check": "expected_states extracted from BDD Then clause"},
            {"dd_id": "DD-12", "check": "Check existing GuestUser before generating"}
        ],
        "notes": "Category navigation, product list rendering"
    },

    "QA-MID-002": {
        "id": "QA-MID-002",
        "name": "Search for product",
        "complexity": "mid",
        "persona": "guest user",
        "requirement": "As a guest user, I want to search for 'dress' so that I can find matching products",
        "url": SITE_KNOWLEDGE["pages"]["home"]["url"],
        "expected_artifacts": [
            "framework/pages/common/search_page.py",
            "framework/pages/catalog/search_results_page.py",
            "framework/tasks/search/search_tasks.py",
            "tests/search/test_product_search.py"
        ],
        "validation_points": [
            {"dd_id": "DD-03", "check": "Locators only in Page Objects"},
            {"dd_id": "DD-17", "check": "Search term 'dress' injected as parameter"}
        ],
        "notes": "Search functionality, results list"
    },

    # Hard scenarios - dynamic content, modals, edge cases
    "QA-HARD-001": {
        "id": "QA-HARD-001",
        "name": "Add product to cart via quick view modal",
        "complexity": "hard",
        "persona": "guest user",
        "requirement": "As a guest user, I want to add a product to cart using the quick view modal so that I can shop faster",
        "url": SITE_KNOWLEDGE["pages"]["women_category"]["url"],
        "expected_artifacts": [
            "framework/pages/catalog/product_list_page.py",
            "framework/pages/catalog/quick_view_modal.py",
            "framework/pages/cart/cart_modal.py",
            "framework/tasks/cart/cart_tasks.py",
            "tests/cart/test_add_to_cart_quickview.py"
        ],
        "validation_points": [
            {"dd_id": "DD-03", "check": "Locators only in Page Objects"},
            {"dd_id": "DD-20", "check": "AI prepares page state for dynamic modal"},
            {"dd_id": "DD-21", "check": "May need SDET collaboration for modal discovery"}
        ],
        "notes": "DYNAMIC: Quick view modal, cart confirmation modal. May trigger DD-21."
    },

    "QA-HARD-002": {
        "id": "QA-HARD-002",
        "name": "Complete checkout as guest",
        "complexity": "hard",
        "persona": "guest user",
        "requirement": "As a guest user with items in cart, I want to complete checkout so that I can purchase products",
        "url": SITE_KNOWLEDGE["pages"]["cart"]["url"],
        "expected_artifacts": [
            "framework/pages/checkout/checkout_page.py",
            "framework/pages/checkout/address_form.py",
            "framework/pages/checkout/payment_page.py",
            "framework/pages/checkout/confirmation_page.py",
            "framework/tasks/checkout/checkout_tasks.py",
            "tests/checkout/test_guest_checkout.py"
        ],
        "validation_points": [
            {"dd_id": "DD-03", "check": "Locators only in Page Objects"},
            {"dd_id": "DD-22", "check": "Multi-step flow, may need stop-and-discuss"}
        ],
        "notes": "COMPLEX: Multi-step checkout, forms, payment. High DD-22 risk."
    }
}


# =============================================================================
# Tool Implementation
# =============================================================================

@tool(
    "get_scenario",
    "Get a pre-defined test scenario for QA validation. Returns Step 1 input for the 9-step MCP tool chain.",
    {
        "level": str,  # "easy", "mid", "hard", or specific ID like "QA-EASY-001"
    }
)
async def get_scenario(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    SR QA Engineer agent tool.

    Returns a test scenario based on complexity level or specific ID.
    Output format matches Step 1 input requirements for the 9-step process.

    Args:
        args: {"level": "easy|mid|hard" or "QA-XXX-NNN"}

    Returns:
        MCP tool response with scenario JSON
    """
    level = args.get("level", "easy").strip()

    # Check if specific scenario ID provided
    if level.upper().startswith("QA-"):
        scenario_id = level.upper()
        if scenario_id in SCENARIOS:
            scenario = SCENARIOS[scenario_id]
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": f"Scenario '{scenario_id}' not found",
                        "available": list(SCENARIOS.keys())
                    }, indent=2)
                }]
            }
    else:
        # Get first scenario matching complexity level
        level_lower = level.lower()
        matching = [s for s in SCENARIOS.values() if s["complexity"] == level_lower]

        if not matching:
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": f"No scenarios found for level '{level}'",
                        "available_levels": ["easy", "mid", "hard"],
                        "available_ids": list(SCENARIOS.keys())
                    }, indent=2)
                }]
            }

        scenario = matching[0]

    # Format Step 1 input for skill invocation
    step1_text = f"""As a {scenario["persona"]}, {scenario["requirement"].split(', I want to ')[1] if ', I want to ' in scenario["requirement"] else scenario["requirement"]}

Target URL: {scenario["url"]}
"""

    # Format output with next_action instruction (DD-VA-02)
    step1_input = {
        "id": scenario["id"],
        "name": scenario["name"],
        "complexity": scenario["complexity"],
        "persona": scenario["persona"],
        "requirement": scenario["requirement"],
        "url": scenario["url"],
        "expected_artifacts": scenario["expected_artifacts"],
        "validation_points": scenario["validation_points"],
        "notes": scenario.get("notes", ""),
        # DD-VA-02: SQA Agent MUST include skill invocation instruction
        "next_action": {
            "instruction": "AI Orchestrator: Invoke the testing skill with the Step 1 input below",
            "skill": "/skill execute-from-step1",
            "step1_input": step1_text,
            "critical": "Do NOT just provide requirements - EXECUTE the skill to trigger artifact generation"
        }
    }

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(step1_input, indent=2)
        }]
    }


@tool(
    "list_scenarios",
    "List all available test scenarios for QA validation.",
    {}
)
async def list_scenarios(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all available scenarios grouped by complexity.
    """
    by_level = {"easy": [], "mid": [], "hard": []}

    for scenario in SCENARIOS.values():
        level = scenario["complexity"]
        by_level[level].append({
            "id": scenario["id"],
            "name": scenario["name"],
            "persona": scenario["persona"]
        })

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(by_level, indent=2)
        }]
    }


@tool(
    "get_site_knowledge",
    "Get knowledge about the target test site (automationpractice.pl).",
    {
        "topic": str  # "pages", "users", "features", or "all"
    }
)
async def get_site_knowledge(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provide site knowledge for scenario generation.
    """
    topic = args.get("topic", "all").lower()

    if topic == "pages":
        result = SITE_KNOWLEDGE["pages"]
    elif topic == "users":
        result = {"user_types": SITE_KNOWLEDGE["user_types"]}
    elif topic == "features":
        result = {"features": SITE_KNOWLEDGE["features"]}
    else:
        result = SITE_KNOWLEDGE

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


# =============================================================================
# Export tools list
# =============================================================================

SR_QA_ENGINEER_TOOLS = [get_scenario, list_scenarios, get_site_knowledge]


# =============================================================================
# Standalone test (uses raw functions, not decorated tools)
# =============================================================================

async def _test_get_scenario(args):
    """Raw implementation for testing."""
    level = args.get("level", "easy").strip()

    if level.upper().startswith("QA-"):
        scenario_id = level.upper()
        if scenario_id in SCENARIOS:
            scenario = SCENARIOS[scenario_id]
        else:
            return {"error": f"Scenario '{scenario_id}' not found"}
    else:
        level_lower = level.lower()
        matching = [s for s in SCENARIOS.values() if s["complexity"] == level_lower]
        if not matching:
            return {"error": f"No scenarios found for level '{level}'"}
        scenario = matching[0]

    # Format Step 1 input for skill invocation
    step1_text = f"""As a {scenario["persona"]}, {scenario["requirement"].split(', I want to ')[1] if ', I want to ' in scenario["requirement"] else scenario["requirement"]}

Target URL: {scenario["url"]}
"""

    return {
        "id": scenario["id"],
        "name": scenario["name"],
        "complexity": scenario["complexity"],
        "persona": scenario["persona"],
        "requirement": scenario["requirement"],
        "url": scenario["url"],
        "expected_artifacts": scenario["expected_artifacts"],
        "validation_points": scenario["validation_points"],
        # DD-VA-02: Include skill invocation instruction
        "next_action": {
            "instruction": "AI Orchestrator: Invoke the testing skill with the Step 1 input below",
            "skill": "/skill execute-from-step1",
            "step1_input": step1_text,
            "critical": "Do NOT just provide requirements - EXECUTE the skill to trigger artifact generation"
        }
    }


if __name__ == "__main__":
    import asyncio

    async def test_tools():
        print("Testing SR QA Engineer tools...\n")

        # Test get_scenario
        print("1. get_scenario(level='easy'):")
        result = await _test_get_scenario({"level": "easy"})
        print(json.dumps(result, indent=2))

        print("\n2. get_scenario(level='QA-HARD-001'):")
        result = await _test_get_scenario({"level": "QA-HARD-001"})
        print(json.dumps(result, indent=2))

        print("\n3. list_scenarios():")
        by_level = {"easy": [], "mid": [], "hard": []}
        for scenario in SCENARIOS.values():
            level = scenario["complexity"]
            by_level[level].append({"id": scenario["id"], "name": scenario["name"]})
        print(json.dumps(by_level, indent=2))

        print("\n4. Available scenarios: ", list(SCENARIOS.keys()))

        print("\n[SUCCESS] All tools working!")

    asyncio.run(test_tools())

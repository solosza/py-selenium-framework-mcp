"""
Visual Demo: Runtime Validation Pipeline

This script demonstrates the integration visually using real page data.
"""

import sys
sys.path.insert(0, r"D:\my_ai_projects\py_sel_framework_mcp")

from mcp_server.utils.scope_discovery import ScopeDiscovery
from mcp_server.utils.runtime_validator import RuntimeValidator, ErrorCategory
from mcp_server.utils.knowledge_base import KnowledgeBase, Pattern

# =============================================================================
# VISUAL HELPERS
# =============================================================================

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_step(num, text):
    print(f"\n{'-' * 40}")
    print(f"  STEP {num}: {text}")
    print(f"{'-' * 40}")

def print_result(label, value, status=""):
    icon = "[OK]" if status == "pass" else "[X]" if status == "fail" else "->"
    print(f"  {icon} {label}: {value}")

def print_element(name, ref, valid, error=None):
    if valid:
        print(f"     [OK] [{ref}] {name} - VALID")
    else:
        print(f"     [X]  [{ref}] {name} - {error}")

# =============================================================================
# REAL PAGE DATA (from Playwright snapshot)
# =============================================================================

# Simulating the snapshot we just captured from automationpractice.pl/authentication
REAL_PAGE_SNAPSHOT = {
    "role": "WebArea",
    "name": "Login - My Shop",
    "url": "http://www.automationpractice.pl/index.php?controller=authentication",
    "children": [
        # Login form elements
        {
            "role": "heading",
            "name": "Already registered?",
            "ref": "e68",
            "hidden": False,
            "disabled": False
        },
        {
            "role": "textbox",
            "name": "Email address",
            "ref": "e72",
            "hidden": False,
            "disabled": False
        },
        {
            "role": "textbox",
            "name": "Password",
            "ref": "e75",
            "hidden": False,
            "disabled": False
        },
        {
            "role": "button",
            "name": "Sign in",
            "ref": "e79",
            "hidden": False,
            "disabled": False
        },
        {
            "role": "link",
            "name": "Forgot your password?",
            "ref": "e77",
            "hidden": False,
            "disabled": False
        },
        # Create account section
        {
            "role": "heading",
            "name": "Create an account",
            "ref": "e56",
            "hidden": False,
            "disabled": False
        },
        {
            "role": "textbox",
            "name": "Email address",  # Different email field
            "ref": "e61",
            "hidden": False,
            "disabled": False
        },
        {
            "role": "button",
            "name": "Create an account",
            "ref": "e63",
            "hidden": False,
            "disabled": False
        },
        # Simulated problematic elements for demo
        {
            "role": "button",
            "name": "Hidden Submit",
            "ref": "demo_hidden",
            "hidden": True,  # Hidden element
            "disabled": False
        },
        {
            "role": "button",
            "name": "Disabled Button",
            "ref": "demo_disabled",
            "hidden": False,
            "disabled": True  # Disabled element
        }
    ]
}

# BDD Scenario for the login workflow
LOGIN_BDD_SCENARIOS = [
    {
        "name": "test_valid_login",
        "given": "I am on the login page at automationpractice.pl",
        "when": "I enter valid email and password and click Sign in",
        "then": "I should see my account dashboard"
    },
    {
        "name": "test_invalid_login",
        "given": "I am on the login page",
        "when": "I enter invalid credentials and click Sign in",
        "then": "I should see an error message on the login page"
    }
]

# Temporary KB with patterns
KB_CONTENT = """# Knowledge Base

## Runtime Validation Patterns

### PATTERN: NOT_VISIBLE - Hidden element

**Context:** symptom=hidden
**Fix:** Wait for element visibility or scroll into view. Check if element is conditionally shown.
**Confidence:** 0.9

---

### PATTERN: NOT_INTERACTABLE - Disabled element

**Context:** symptom=disabled
**Fix:** Wait for element to become enabled. Check form validation or preconditions.
**Confidence:** 0.85

---

### PATTERN: LOCATOR_NOT_FOUND - Missing element

**Context:** any
**Fix:** Verify page fully loaded. Check selector accuracy. Element may be dynamic.
**Confidence:** 0.8

---
"""

# =============================================================================
# MAIN DEMO
# =============================================================================

def run_visual_demo():
    print_header("RUNTIME VALIDATION PIPELINE - VISUAL DEMO")
    print("\n  Target: automationpractice.pl Login Page")
    print("  This demo shows how the 4 modules work together.\n")

    # -------------------------------------------------------------------------
    # STEP 1: Scope Discovery
    # -------------------------------------------------------------------------
    print_step(1, "SCOPE DISCOVERY")
    print("  Analyzing BDD scenarios to determine workflow scope...\n")

    scope = ScopeDiscovery()
    scope_result = scope.analyze_workflow(LOGIN_BDD_SCENARIOS)

    print(f"  BDD Scenarios analyzed: {len(LOGIN_BDD_SCENARIOS)}")
    print(f"  Pages detected: {scope_result.page_count}")
    print(f"  Is single page: {scope_result.is_single_page}")
    print(f"  Pages: {[p.name for p in scope_result.pages]}")

    # -------------------------------------------------------------------------
    # STEP 2: Element Validation
    # -------------------------------------------------------------------------
    print_step(2, "RUNTIME VALIDATION")
    print("  Validating elements from page snapshot...\n")

    validator = RuntimeValidator()

    # Elements to validate
    elements_to_check = [
        ("Email address", "Login email field"),
        ("Password", "Password field"),
        ("Sign in", "Submit button"),
        ("Forgot your password?", "Password reset link"),
        ("Hidden Submit", "Hidden button (will fail)"),
        ("Disabled Button", "Disabled button (will fail)"),
        ("Non-existent element", "Missing element (will fail)")
    ]

    validation_results = []
    print("  Element Validation Results:")
    print("  " + "-" * 50)

    for element_name, description in elements_to_check:
        result = validator.validate_element_from_snapshot(
            REAL_PAGE_SNAPSHOT, element_name
        )

        validation_results.append({
            "name": element_name,
            "description": description,
            "result": result
        })

        if result.is_valid:
            ref = result.details.get("element_info", {}).get("ref", "?")
            print_element(element_name, ref, True)
        else:
            error = result.error_category.value if result.error_category else "UNKNOWN"
            print_element(element_name, "?", False, error)

    # Count results
    valid_count = sum(1 for r in validation_results if r["result"].is_valid)
    invalid_count = len(validation_results) - valid_count

    print("\n  " + "-" * 50)
    print(f"  Summary: {valid_count} valid, {invalid_count} errors")

    # -------------------------------------------------------------------------
    # STEP 3: Knowledge Base Lookup
    # -------------------------------------------------------------------------
    print_step(3, "KNOWLEDGE BASE LOOKUP")
    print("  Finding fixes for validation errors...\n")

    # Create temp KB
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(KB_CONTENT)
        kb_path = f.name

    try:
        kb = KnowledgeBase(kb_path=kb_path)

        print("  Error -> Fix Lookup:")
        print("  " + "-" * 50)

        for item in validation_results:
            if not item["result"].is_valid:
                error_cat = item["result"].error_category
                if error_cat:
                    pattern = kb.find_pattern(error_cat.value)

                    if pattern:
                        print(f"\n  [X] {item['name']}")
                        print(f"      Error: {error_cat.value}")
                        print(f"      Fix: {pattern.fix}")
                        print(f"      Confidence: {pattern.confidence}")
                    else:
                        print(f"\n  [X] {item['name']}")
                        print(f"      Error: {error_cat.value}")
                        print(f"      Fix: No pattern found - ASK USER (DD-22)")

    finally:
        os.unlink(kb_path)

    # -------------------------------------------------------------------------
    # STEP 4: Pipeline Summary
    # -------------------------------------------------------------------------
    print_step(4, "PIPELINE SUMMARY")

    print("""
  +-----------------------------------------------------------+
  |                   PIPELINE FLOW                           |
  +-----------------------------------------------------------+
  |                                                           |
  |   BDD Scenarios                                           |
  |        |                                                  |
  |        v                                                  |
  |   +-------------------+                                   |
  |   | ScopeDiscovery    | --- "How many pages?"             |
  |   +-------------------+                                   |
  |            |                                              |
  |            v                                              |
  |   +-------------------+                                   |
  |   | RuntimeValidator  | --- "Is element usable?"          |
  |   +-------------------+                                   |
  |            |                                              |
  |       +----+----+                                         |
  |       v         v                                         |
  |    VALID     ERROR                                        |
  |      |         |                                          |
  |      |         v                                          |
  |      |   +-------------------+                            |
  |      |   | KnowledgeBase     | --- "What's the fix?"      |
  |      |   +-------------------+                            |
  |      |            |                                       |
  |      |       +----+----+                                  |
  |      |       v         v                                  |
  |      |    PATTERN    NONE                                 |
  |      |    FOUND      FOUND                                |
  |      |       |         |                                  |
  |      |       v         v                                  |
  |      |   Apply Fix   ASK USER                             |
  |      |               (DD-22)                              |
  |      |                                                    |
  |      v                                                    |
  |   PROCEED                                                 |
  |                                                           |
  +-----------------------------------------------------------+
""")

    print("\n  Demo complete!")
    print("  " + "=" * 50)


if __name__ == "__main__":
    run_visual_demo()

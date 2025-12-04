"""
Tool 2: discover_page_elements

Discover interactive elements on a web page using Selenium.
Runs after parsing user story, discovers elements needed for the scenario.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.element_discovery import discover_page_elements


async def discover_elements(arguments: dict) -> str:
    """
    Discover interactive elements on a web page.

    Supports two flows (DD-20):
    - STATIC: Pass URL, Tool 2 creates driver, discovers, closes driver
    - DYNAMIC: Pass driver_session (+ optional scope), Tool 2 uses existing driver,
               discovers within scope, does NOT close driver (AI owns lifecycle)

    Args:
        arguments: {
            "url": str - Page URL to inspect (STATIC flow)
            "headless": bool - Run browser in headless mode (default: True)
            "driver_session": WebDriver - Existing driver instance (DYNAMIC flow, DD-20)
            "scope": str - CSS selector to limit discovery scope (optional, for DYNAMIC)
        }

    Returns:
        JSON string with discovered elements
    """
    url = arguments.get("url", "")
    headless = arguments.get("headless", True)
    driver_session = arguments.get("driver_session", None)
    scope = arguments.get("scope", None)

    # DD-20: Determine flow based on inputs
    is_dynamic_flow = driver_session is not None

    # Validation for STATIC flow
    if not is_dynamic_flow:
        if not url:
            return json.dumps({
                "error": "url is required for static flow (or provide driver_session for dynamic flow)",
                "status": "error"
            }, indent=2)

        # Validate URL format
        if not url.startswith("http"):
            return json.dumps({
                "error": "url must start with http:// or https://",
                "status": "error"
            }, indent=2)

    try:
        # Import Selenium dependencies
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        # DD-20: DYNAMIC flow - use existing driver
        if is_dynamic_flow:
            driver = driver_session
            created_driver = False
            # Get current URL from existing driver for reporting
            url = driver.current_url
        else:
            # STATIC flow - create new driver
            options = Options()
            if headless:
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)
            created_driver = True

        try:
            # Discover elements (with optional scope for dynamic flow)
            elements = discover_page_elements(url, driver, scope=scope)

            # Group elements by type
            grouped = {}
            for elem in elements:
                elem_type = elem["element_type"]
                if elem_type not in grouped:
                    grouped[elem_type] = []
                grouped[elem_type].append(elem)

            # Build metadata for downstream tools (PRD FR-11, FR-12, FR-13, FR-14)
            # This is the standardized format that AI passes to Tool 3
            # Format per FRAMEWORK.md Section 8.5 and PRD Section 6.2:
            # discovered_elements: [{name, type, locator}]
            def get_best_locator(elem):
                """Get the best available locator (priority: id > css > xpath)."""
                if elem.get("locator_id"):
                    return elem["locator_id"]
                elif elem.get("locator_css"):
                    return elem["locator_css"]
                elif elem.get("locator_xpath"):
                    return elem["locator_xpath"]
                return ""

            metadata = {
                "discovered_elements": [
                    {
                        "name": elem.get("suggested_name", ""),
                        "type": elem.get("element_type", ""),
                        "locator": get_best_locator(elem)
                    }
                    for elem in elements
                    if elem.get("suggested_name") and get_best_locator(elem)
                ]
            }

            result = {
                "status": "success",
                "url": url,
                "total_elements": len(elements),
                "elements_by_type": {k: len(v) for k, v in grouped.items()},
                "elements": elements,  # Legacy detailed format for backwards compatibility
                "metadata": metadata,  # Standardized metadata for downstream tools
                "next_steps": [
                    "Review discovered elements",
                    "Select relevant elements for POM",
                    "Use Tool 3 (generate_page_object) to create POM code",
                    "Optionally filter elements before passing to Tool 3"
                ]
            }

            return json.dumps(result, indent=2)

        finally:
            # DD-20: Only clean up driver if WE created it (STATIC flow)
            # For DYNAMIC flow, AI owns driver lifecycle
            if created_driver:
                driver.quit()

    except ImportError as e:
        return json.dumps({
            "error": "Selenium not installed. Run: pip install selenium webdriver-manager",
            "status": "error",
            "details": str(e)
        }, indent=2)

    except Exception as e:
        import traceback
        return json.dumps({
            "error": f"Failed to discover elements: {str(e)}",
            "status": "error",
            "traceback": traceback.format_exc()
        }, indent=2)


if __name__ == "__main__":
    import asyncio

    # Test with Automation Practice login page
    test_args = {
        "url": "http://www.automationpractice.pl/index.php?controller=authentication",
        "headless": True
    }

    result = asyncio.run(discover_elements(test_args))
    print(result)

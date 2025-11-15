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

    Args:
        arguments: {
            "url": str - Page URL to inspect
            "headless": bool - Run browser in headless mode (default: True)
        }

    Returns:
        JSON string with discovered elements
    """
    url = arguments.get("url", "")
    headless = arguments.get("headless", True)

    if not url:
        return json.dumps({
            "error": "url is required",
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

        # Configure driver
        options = Options()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Create driver
        driver = webdriver.Chrome(options=options)

        try:
            # Discover elements
            elements = discover_page_elements(url, driver)

            # Group elements by type
            grouped = {}
            for elem in elements:
                elem_type = elem["element_type"]
                if elem_type not in grouped:
                    grouped[elem_type] = []
                grouped[elem_type].append(elem)

            result = {
                "status": "success",
                "url": url,
                "total_elements": len(elements),
                "elements_by_type": {k: len(v) for k, v in grouped.items()},
                "elements": elements,
                "next_steps": [
                    "Review discovered elements",
                    "Select relevant elements for POM",
                    "Use Tool 6 (generate_page_object) to create POM code",
                    "Optionally filter elements before passing to Tool 6"
                ]
            }

            return json.dumps(result, indent=2)

        finally:
            # Clean up driver
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

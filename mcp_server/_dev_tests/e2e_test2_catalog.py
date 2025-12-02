"""
E2E Test 2: Browse & Filter Products (Medium)

Full MCP tool chain test with GuestUser:
- Tool 1: Parse user story
- Tool 2: Discover page elements (browser visible)
- Tool 3: Generate page object
- Tool 4: Generate task
- Tool 5: Generate role (GuestUser)
- Tool 6: Generate test
- Run pytest with visible browser
- Generate HTML report

Output folder: devtest2/

Usage:
    cd mcp_server/_dev_tests
    python e2e_test2_catalog.py
"""

import asyncio
import json
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime

# Setup paths
SCRIPT_DIR = Path(__file__).parent
MCP_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = MCP_DIR.parent
FRAMEWORK_DIR = PROJECT_ROOT / "framework"
TESTS_DIR = PROJECT_ROOT / "tests"

# Add paths for imports
sys.path.insert(0, str(MCP_DIR))
sys.path.insert(0, str(MCP_DIR / "tools"))
sys.path.insert(0, str(FRAMEWORK_DIR))

# Output folder name
DEV_TEST_FOLDER = "devtest2"

# Test configuration
USER_STORY = """
As a guest user, I want to browse products by category and filter them

Acceptance Criteria:
- User can navigate to a product category
- User can see products listed on the page
- User can filter products by criteria
- User can sort products by price

Scenario: Browse women's clothing category
Given user is on the homepage
When user clicks on Women category
Then user sees a list of products in the Women category
"""

WORKFLOW = "catalog"
CATEGORY_PAGE_URL = "http://www.automationpractice.pl/index.php?id_category=3&controller=category"


def print_section(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_file_contents(file_path, code):
    """Print file contents with header."""
    print(f"\n{'-' * 70}")
    print(f"FILE: {file_path}")
    print(f"{'-' * 70}")
    print(code)
    print(f"{'-' * 70}")


def create_devtest_folders():
    """Create devtest2 folders in framework structure."""
    folders = [
        FRAMEWORK_DIR / "pages" / DEV_TEST_FOLDER,
        FRAMEWORK_DIR / "tasks" / DEV_TEST_FOLDER,
        FRAMEWORK_DIR / "roles" / DEV_TEST_FOLDER,
        TESTS_DIR / DEV_TEST_FOLDER,
        TESTS_DIR / "_reports",
    ]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {folder.relative_to(PROJECT_ROOT)}")

    # Create __init__.py files for Python imports
    for folder in folders[:-1]:  # Exclude _reports
        init_file = folder / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")

    return folders


def save_file(file_path: Path, content: str):
    """Save content to file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    print(f"  Saved: {file_path.relative_to(PROJECT_ROOT)}")


async def run_e2e_test():
    """Run the full E2E MCP test."""

    print_section("E2E TEST 2: BROWSE & FILTER PRODUCTS (GuestUser)")
    print(f"\nProject root: {PROJECT_ROOT}")
    print(f"Output folder: {DEV_TEST_FOLDER}/")
    print(f"Workflow: {WORKFLOW}")

    # Step 0: Create folders
    print_section("STEP 0: Create devtest2 folders")
    create_devtest_folders()

    # ========== TOOL 1: Parse User Story ==========
    print_section("STEP 1: Parse User Story (Tool 1)")

    from tools.tool_01_generate_tests_from_user_story import generate_tests_from_user_story

    result1 = await generate_tests_from_user_story({
        "user_story": USER_STORY,
        "workflow": WORKFLOW
    })

    parsed = json.loads(result1)
    if parsed.get("status") != "success":
        print(f"ERROR: {parsed.get('error')}")
        return False

    print(f"  Title: {parsed.get('user_story_title')}")
    print(f"  Scenarios found: {parsed.get('scenarios_count')}")

    scenario = parsed.get("scenarios", [])[0]
    print(f"  Test name: {scenario.get('name')}")
    print(f"  Given: {scenario.get('given')}")
    print(f"  When: {scenario.get('when')}")
    print(f"  Then: {scenario.get('then')}")

    # ========== TOOL 2: Discover Elements ==========
    print_section("STEP 2: Discover Page Elements (Tool 2)")
    print(f"  URL: {CATEGORY_PAGE_URL}")
    print(f"  Browser: VISIBLE (headless=False)")
    print("\n  >>> Browser will open now... <<<\n")

    from tools.tool_02_discover_page_elements import discover_elements

    result2 = await discover_elements({
        "url": CATEGORY_PAGE_URL,
        "headless": False  # User can see the browser
    })

    discovered = json.loads(result2)
    if discovered.get("status") != "success":
        print(f"ERROR: {discovered.get('error')}")
        return False

    print(f"  Total elements found: {discovered.get('total_elements')}")
    print(f"  By type: {json.dumps(discovered.get('elements_by_type'), indent=4)}")

    elements = discovered.get("elements", [])

    # Filter to catalog-related elements
    catalog_keywords = ["product", "category", "filter", "sort", "price", "add", "cart", "view", "list"]
    catalog_elements = [e for e in elements if any(k in e.get("suggested_name", "").lower()
                       for k in catalog_keywords)]

    # If not enough catalog elements, include buttons and links
    if len(catalog_elements) < 5:
        catalog_elements = [e for e in elements if e.get("element_type") in ["buttons", "links", "selects"]]

    print(f"\n  Catalog-related elements ({len(catalog_elements)}):")
    for elem in catalog_elements[:15]:  # Show first 15
        print(f"    - {elem.get('suggested_name')}: {elem.get('locator_css') or elem.get('locator_id')}")

    # ========== TOOL 3: Generate Page Object ==========
    print_section("STEP 3: Generate Page Object (Tool 3)")

    from tools.tool_03_generate_page_object import generate_page_object

    result3 = await generate_page_object({
        "page_name": "DevCategoryPage",
        "elements": catalog_elements[:20],  # Limit to 20 elements
        "workflow": DEV_TEST_FOLDER
    })

    pom_result = json.loads(result3)
    if pom_result.get("status") != "success":
        print(f"ERROR: {pom_result.get('error')}")
        return False

    pom_code = pom_result.get("code")
    pom_file = FRAMEWORK_DIR / "pages" / DEV_TEST_FOLDER / "dev_category_page.py"

    save_file(pom_file, pom_code)
    print_file_contents(pom_file.relative_to(PROJECT_ROOT), pom_code)

    # ========== TOOL 4: Generate Task ==========
    print_section("STEP 4: Generate Task (Tool 4)")

    from tools.tool_04_generate_task import generate_task

    result4 = await generate_task({
        "task_name": "DevCatalogTasks",
        "workflow_description": "Catalog browsing and filtering workflows",
        "page_objects": [{
            "name": "DevCategoryPage",
            "file_path": f"pages/{DEV_TEST_FOLDER}/dev_category_page.py",
            "code": pom_code
        }]
    })

    task_result = json.loads(result4)
    if task_result.get("status") != "success":
        print(f"ERROR: {task_result.get('error')}")
        return False

    task_code = task_result.get("code")
    task_file = FRAMEWORK_DIR / "tasks" / DEV_TEST_FOLDER / "dev_catalog_tasks.py"

    save_file(task_file, task_code)
    print_file_contents(task_file.relative_to(PROJECT_ROOT), task_code)

    # ========== TOOL 5: Generate Role (GuestUser) ==========
    print_section("STEP 5: Generate Role - GuestUser (Tool 5)")

    from tools.tool_05_generate_role import generate_role

    result5 = await generate_role({
        "role_name": "DevGuestUser",
        "capabilities": ["can_browse", "can_filter", "can_sort"],
        "task_class": "DevCatalogTasks",
        "task_import": f"from tasks.{DEV_TEST_FOLDER}.dev_catalog_tasks import DevCatalogTasks"
    })

    role_result = json.loads(result5)
    if role_result.get("status") != "success":
        print(f"ERROR: {role_result.get('error')}")
        return False

    role_code = role_result.get("code")
    role_file = FRAMEWORK_DIR / "roles" / DEV_TEST_FOLDER / "dev_guest_user.py"

    save_file(role_file, role_code)
    print_file_contents(role_file.relative_to(PROJECT_ROOT), role_code)

    # ========== TOOL 6: Generate Test ==========
    print_section("STEP 6: Generate Test (Tool 6)")

    from tools.tool_06_generate_test_runner import generate_test_runner

    result6 = await generate_test_runner({
        "test_name": scenario.get("name"),
        "workflow": DEV_TEST_FOLDER,
        "role": "DevGuestUser",
        "scenario": scenario,
        "role_import": f"from roles.{DEV_TEST_FOLDER}.dev_guest_user import DevGuestUser"
    })

    test_result = json.loads(result6)
    if test_result.get("status") != "success":
        print(f"ERROR: {test_result.get('error')}")
        return False

    test_code = test_result.get("code")
    test_file = TESTS_DIR / DEV_TEST_FOLDER / f"{scenario.get('name')}.py"

    save_file(test_file, test_code)
    print_file_contents(test_file.relative_to(PROJECT_ROOT), test_code)

    # ========== RUN PYTEST ==========
    print_section("STEP 7: Run pytest with visible browser")

    report_name = f"devtest2_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    report_path = TESTS_DIR / "_reports" / report_name

    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",
        f"--html={report_path}",
        "--self-contained-html"
    ]

    print(f"  Command: {' '.join(cmd)}")
    print(f"\n  >>> Browser will open for test execution... <<<\n")

    result = subprocess.run(
        cmd,
        cwd=str(TESTS_DIR),
        capture_output=True,
        text=True
    )

    print("\n  PYTEST OUTPUT:")
    print("  " + result.stdout.replace("\n", "\n  "))
    if result.stderr:
        print("\n  STDERR:")
        print("  " + result.stderr.replace("\n", "\n  "))

    # ========== SUMMARY ==========
    print_section("E2E TEST 2 SUMMARY")

    print(f"""
  FILES GENERATED:
    1. framework/pages/{DEV_TEST_FOLDER}/dev_category_page.py    <- Page Object
    2. framework/tasks/{DEV_TEST_FOLDER}/dev_catalog_tasks.py    <- Task (catalog workflows)
    3. framework/roles/{DEV_TEST_FOLDER}/dev_guest_user.py       <- Role (GuestUser)
    4. tests/{DEV_TEST_FOLDER}/{scenario.get('name')}.py         <- Test

  HTML REPORT: tests/_reports/{report_name}
  Report size: {report_path.stat().st_size if report_path.exists() else 'N/A'} bytes

  Open report: file:///{report_path}

  PYTEST EXIT CODE: {result.returncode}
""")

    if result.returncode == 0:
        print("  STATUS: PASSED")
    else:
        print("  STATUS: FAILED (check output above for details)")

    return result.returncode == 0


if __name__ == "__main__":
    success = asyncio.run(run_e2e_test())
    sys.exit(0 if success else 1)

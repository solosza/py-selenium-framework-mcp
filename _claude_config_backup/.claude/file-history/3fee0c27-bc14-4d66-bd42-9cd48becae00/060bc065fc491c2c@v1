# Execute Test from Step 1

**Purpose:** Validate the full 9-step MCP tool chain. If ANY defect is found, fix it and RESTART FROM STEP 1.

---

## Prerequisites (Verify First)

| Check | Command/Action | Fix |
|-------|----------------|-----|
| MCP Server | `/mcp` → qa-automation connected | `pip install -r requirements.txt` then restart |
| Dependencies | `pip install -r requirements.txt` | Check Python 3.8+ |
| Chrome | Browser installed | Install Chrome |
| Target Site | Open http://www.automationpractice.pl | Check internet |

---

## Before Starting

1. Get from user (if not already known):
   - Persona: "As a [role]..."
   - Intent: What they want to do
   - URL: Target page URL
   - Expected outcome: What success looks like

2. Determine test output location:
   - tests/test1/ (simple, single domain)
   - tests/test2/ (medium, multi-domain)
   - Or custom path

3. **DevTest vs Production Folders:**

   ```
   DevTest Mode (tool chain validation):
   ├── tests/test1/          # Test files
   ├── framework/pages/test1/
   ├── framework/tasks/test1/
   └── framework/roles/test1/

   Production Mode (real test suite):
   ├── tests/{domain}/       # e.g., tests/auth/, tests/cart/
   ├── framework/pages/{domain}/
   ├── framework/tasks/{domain}/
   └── framework/roles/auth/  # ALL roles go in auth/ folder
   ```

   **Role Folder Rule:** All roles (GuestUser, RegisteredUser, AdminUser)
   belong in `framework/roles/auth/` - they are authentication personas.

---

## Execute 9-Step Workflow

### Step 1: User Input
- Confirm persona, intent, URL, expected outcome
- If missing, ASK before proceeding (DD-01, DD-02)

### Step 2: AI Processing (no tool call)
- Extract role_name from persona
- Extract domain (auth/catalog/cart/checkout)
- Convert to BDD format (Given/When/Then)
- Extract expected_states from "Then" clause (DD-09)
- Initialize metadata_context

### Step 3: Tool 1 - generate_tests_from_user_story
- Input: BDD user story, workflow/domain
- Output: test_scenarios[] → add to metadata_context

### Step 4: Tool 2 - discover_page_elements

**IMPORTANT: Determine Static vs Dynamic Flow (DD-20)**

```
Are elements visible on page load?
├── YES → STATIC FLOW (normal)
│         Input: { "url": "http://..." }
│
└── NO  → DYNAMIC FLOW (DD-20)
          AI must prepare page state FIRST:
          1. Create WebDriver session
          2. Navigate to URL
          3. Perform interactions (hover, click, wait)
          4. Call Tool 2 with driver_session (not url)
          5. Optionally scope to specific container
```

**AI Autonomous Problem-Solving (DD-21):**

AI should resolve element discovery issues with MINIMAL user interaction.
Assume user is a junior dev/manual tester who needs guidance.
EXHAUST all options before asking for help.

```
When AI encounters issues discovering elements:

1. ANALYZE CONTEXT from metadata:
   - What workflow are we building? (from test_scenarios)
   - What domain? (auth/catalog/cart/checkout)
   - What elements do we NEED for this workflow?

2. AUTONOMOUS TROUBLESHOOTING (do ALL of these before asking user):

   A. CHECK FOR IFRAMES/FRAMES:
      ```python
      # List all iframes on page
      iframes = driver.find_elements(By.TAG_NAME, "iframe")
      frames = driver.find_elements(By.TAG_NAME, "frame")

      # If iframes exist, switch and search:
      for iframe in iframes:
          driver.switch_to.frame(iframe)
          # Try finding element here
          elements = driver.find_elements(By.CSS_SELECTOR, target)
          if elements:
              # Found it! Note: element is inside iframe
              break
          driver.switch_to.default_content()
      ```

   B. CHECK FOR SHADOW DOM:
      ```python
      # JS to pierce shadow DOM
      element = driver.execute_script('''
          const host = document.querySelector('shadow-host-selector');
          return host?.shadowRoot?.querySelector('target-selector');
      ''')
      ```

   C. WAIT FOR DYNAMIC CONTENT:
      ```python
      # Explicit wait for element presence
      from selenium.webdriver.support.ui import WebDriverWait
      from selenium.webdriver.support import expected_conditions as EC

      element = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.CSS_SELECTOR, selector))
      )

      # Wait for AJAX to complete
      driver.execute_script('''
          return document.readyState === 'complete' &&
                 (typeof jQuery === 'undefined' || jQuery.active === 0);
      ''')
      ```

   D. TRY MULTIPLE SELECTOR STRATEGIES:
      ```python
      # CSS Selector
      driver.find_elements(By.CSS_SELECTOR, "#email")
      # XPath
      driver.find_elements(By.XPATH, "//input[@type='email']")
      # Name attribute
      driver.find_elements(By.NAME, "email")
      # Partial text/link
      driver.find_elements(By.PARTIAL_LINK_TEXT, "Login")
      # Data attributes
      driver.find_elements(By.CSS_SELECTOR, "[data-testid='login-btn']")
      ```

   E. JAVASCRIPT DIRECT DOM QUERY:
      ```python
      # When Selenium can't find it, JS might
      elements = driver.execute_script('''
          return Array.from(document.querySelectorAll('input, button, a'))
              .filter(el => el.offsetParent !== null);  // visible only
      ''')

      # Get all interactive elements with their properties
      info = driver.execute_script('''
          return Array.from(document.querySelectorAll('*'))
              .filter(el => ['INPUT','BUTTON','A','SELECT'].includes(el.tagName))
              .map(el => ({
                  tag: el.tagName,
                  id: el.id,
                  name: el.name,
                  class: el.className,
                  type: el.type,
                  text: el.innerText?.substring(0,50),
                  visible: el.offsetParent !== null
              }));
      ''')
      ```

   F. TRIGGER ELEMENT VISIBILITY:
      ```python
      # Scroll into view
      driver.execute_script('arguments[0].scrollIntoView(true);', element)

      # Trigger hover via JS
      driver.execute_script('''
          var event = new MouseEvent('mouseover', {bubbles: true});
          arguments[0].dispatchEvent(event);
      ''', element)

      # Force click via JS (when element "not clickable")
      driver.execute_script('arguments[0].click();', element)

      # Remove overlay blocking element
      driver.execute_script('''
          document.querySelector('.modal-overlay')?.remove();
      ''')
      ```

   G. CHECK PAGE STATE:
      ```python
      # Current URL (did navigation happen?)
      print(driver.current_url)

      # Page source snippet (is content loaded?)
      print(driver.page_source[:2000])

      # Any JS errors in console?
      logs = driver.get_log('browser')

      # Screenshot for debugging
      driver.save_screenshot('debug.png')
      ```

3. ONLY IF ALL ABOVE FAIL - Ask user WITH GUIDED INSTRUCTIONS:

   When asking for help, ALWAYS provide step-by-step instructions
   so user knows exactly how to find what AI needs.

   EXAMPLE - Finding a locator:
   ─────────────────────────────
   "I need the locator for the login submit button. Here's how to find it:

   1. Open the page in Chrome: [URL]
   2. Right-click on the Submit/Login button
   3. Click 'Inspect' (opens DevTools)
   4. Look at the highlighted HTML element
   5. Look for these attributes (in order of preference):
      - id='...'        → best, use: #id_value
      - name='...'      → good, use: [name='value']
      - data-testid='...' → good, use: [data-testid='value']
      - class='...'     → ok if unique, use: .class_name
   6. Tell me what you see, e.g.: <button id='SubmitLogin' class='btn'>

   What attributes do you see on the button?"

   EXAMPLE - Checking for iframe:
   ──────────────────────────────
   "I can't find the form elements. They might be inside an iframe.
   Here's how to check:

   1. Open DevTools (F12)
   2. Press Ctrl+F in the Elements panel
   3. Search for: <iframe
   4. If you find iframe tags:
      - Click the iframe in Elements panel
      - Look for 'id' or 'name' attribute
      - Check if the form is nested inside it
   5. Tell me:
      - How many iframes exist?
      - If form is inside one, what's the iframe's id/name?

   What do you see?"

   EXAMPLE - Element not visible:
   ──────────────────────────────
   "The element exists but isn't visible. Here's how to check why:

   1. Open DevTools (F12)
   2. Find the element in Elements panel
   3. Look at the Styles panel on the right
   4. Check for:
      - display: none
      - visibility: hidden
      - opacity: 0
      - height: 0 or width: 0
   5. Look for parent elements that might be hidden
   6. Check if there's a button/link that reveals this element

   What CSS is hiding the element? Is there a trigger to show it?"

   EXAMPLE - Dynamic content:
   ──────────────────────────
   "The content might load after a user action. Let me guide you:

   1. Open the page in browser
   2. Open DevTools → Network tab
   3. Perform the action you'd normally do (click button, scroll, etc.)
   4. Watch for new network requests (XHR/Fetch)
   5. After content appears, tell me:
      - What action triggered it?
      - What new elements appeared?

   What action makes the content appear?"
```

- Output: discovered_elements[] → add to metadata_context
- Filter elements relevant to intent

### Step 5: Tool 3 - generate_page_object
- CHECK EXISTING first (DD-12): scan framework/pages/{domain}/
- Input: elements, expected_states, domain
- Output: POM code + pom_metadata → add to metadata_context

### Step 6: Tool 4 - generate_task
- CHECK EXISTING first (DD-12): scan framework/tasks/{domain}/
- Input: pom_metadata from Step 5
- Output: Task code + task_metadata → add to metadata_context

### Step 7: Tool 5 - generate_role
- CHECK EXISTING first (DD-12): scan framework/roles/
- Input: task_metadata from Step 6
- Output: Role code + role_metadata → add to metadata_context

### Step 8: Tool 6 - generate_test_runner
- Input: role_metadata + pom_metadata
- Output: Test file with AAA pattern
- Assertions use POM state methods from metadata (DD-15)
- Apply post-processing (DD-16, DD-17, DD-18):
  - DD-16: Override file path to tests/test1/ or tests/test2/
  - DD-17: Inject actual parameter values (not placeholders)
  - DD-18: Validate import paths match file locations

### Step 9: Save & Run
- Save generated code to file paths
- Add __init__.py files if needed
- Run: `pytest {path} -v --headless=False --html=reports/{name}_report.html --self-contained-html`

---

## Defect Handling (CRITICAL)

If ANY error is encountered at ANY step:

1. **STOP** - Do not continue to next step
2. **EXPLAIN** - Tell user:
   - What step failed
   - The exact error message
   - What you think might be the cause
3. **COLLABORATE** - Troubleshoot WITH the user:
   - Propose 1-2 investigation steps
   - Ask user if they want to proceed or have ideas
   - Work together to identify root cause
4. **FIX** - Implement the fix together
5. **RESTART FROM STEP 1** - After fix, do NOT resume mid-workflow
6. **RESOLVE** - Only mark defect RESOLVED after full chain passes

**Example Error Dialogue:**
```
AI: "Step 3 failed with error: 'No scenarios found in user story'

I think the issue is: [hypothesis]

Let me investigate by: [action]

Should I proceed, or do you have a different idea?"
```

**DO NOT:**
- Silently retry without telling user
- Continue to next step after error
- Assume you know the fix without verifying

---

## Success Criteria

The workflow passes ONLY when:
- All 9 steps complete without defects
- Generated test runs with visible browser
- Test assertion passes
- HTML report generated

---

## Tool Invocation Pattern (DD-19)

Always import from `tools/`, never `utils/`:

```python
# CORRECT
from tools.tool_01_generate_tests_from_user_story import generate_tests_from_user_story
from tools.tool_02_discover_page_elements import discover_elements

# WRONG - will cause errors
from utils.element_discovery import discover_page_elements  # NO!
```

---

## Reference

- CLAUDE.md: DD-01 through DD-21, E2E Testing Process
- FRAMEWORK.md Section 8: 9-Step AI Workflow
- docs/DEFECT_LOG.md: Defect tracking format

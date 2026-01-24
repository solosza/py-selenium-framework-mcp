# Gate Validation Audit Report

**Date:** 2026-01-23
**Purpose:** Compare protocol requirements against gate implementations to identify:
1. **Validation Gaps** - Protocol requirements not enforced by gates
2. **NEEDS_RETRY Gaps** - Missing infrastructure that could use scaffolding pattern

---

## Summary

| Step | Protocol | Gate | Validation Gaps | NEEDS_RETRY Gaps | Status |
|------|----------|------|-----------------|------------------|--------|
| 1 | step-01.md | qg_user_input.py | 2 gaps | 1 gap | ⚠️ |
| 2 | step-02.md | qg_preflight.py | 0 gaps | 0 gaps | ✅ |
| 3 | step-03.md | qg_ai_processing.py | 1 gap | 0 gaps | ⚠️ |
| 4 | step-04.md | qg_test_scenarios.py | 1 gap | 0 gaps | ⚠️ |
| 5 | step-05.md | qg_discovered_elements.py | 3 gaps | 2 gaps | ⚠️ |

**Total:** 7 validation gaps, 3 NEEDS_RETRY gaps

---

## Step 1: User Input

### Protocol Requirements (step-01.md)

**POST-ACTION (Line 72-75):**
```
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, user inputs, extracted fields, gate result, timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
```

**Auto-Detection (Line 58-61):**
```
- AUTO-DETECT environment:
  - Check URL against framework/resources/config/environment_config.json
  - If match found → detected_env_id = environment name
  - If no match → ASK user: "Unknown environment. Should I create config for '{url_domain}'?"
```

**Workflow Validation (Line 49-51):**
```
- ASK user: "Workflow identifier?"
  Explanation: "This creates folders at framework/pages/{workflow}/ and tests/{workflow}/
               Use to organize tests by: test run (helios7), feature (checkout-v2), sprint (auth-sprint-2)"
```

### Gate Implementation (qg_user_input.py)

**Currently Validates:**
- ✅ persona (non-empty string) - Lines 72-76
- ✅ URL (valid HTTP/HTTPS format) - Lines 79-84
- ✅ role_name (PascalCase) - Lines 87-92
- ✅ workflow (non-empty string) - Lines 95-99
- ✅ raw_requirement (non-empty) - Lines 102-107
- ✅ Environment detection with NEEDS_RETRY scaffolding - Lines 112-116, 186-258
- ✅ Transcript validation - via universal `validate_and_pass()` helper

### Validation Gaps

**GAP-01-01: Workflow directory validation**
- **Protocol says:** "This creates folders at framework/pages/{workflow}/ and tests/{workflow}/"
- **Gate does:** Only validates workflow is non-empty string
- **Missing:** Check if directories exist, scaffold if missing
- **Impact:** AI can proceed with invalid workflow that has no directory structure
- **Fix:** Add `_check_workflow_directories()` method, return NEEDS_RETRY with scaffolding template

**GAP-01-02: Role name must match persona**
- **Protocol says:** "role_name: Convert persona to PascalCase (sales representative → SalesRepresentative)"
- **Gate does:** Only validates role_name is PascalCase, doesn't verify it matches persona
- **Missing:** Validate role_name is derived from persona (not arbitrary)
- **Impact:** AI could pass mismatched role_name ("GuestUser") for persona ("registered user")
- **Fix:** Add validation logic to check role_name is PascalCase conversion of persona

### NEEDS_RETRY Gaps

**RETRY-01-01: Workflow directory scaffolding**
- **Missing infrastructure:** `framework/pages/{workflow}/` and `tests/{workflow}/` directories
- **Current behavior:** Directories created manually later, causing workflow failures
- **NEEDS_RETRY pattern:** Return scaffolding template with directories to create
- **Fix:** Add to `validate_and_pass()` or create `_check_workflow_directories()`

---

## Step 2: Pre-flight Configuration

### Protocol Requirements (step-02.md)

**POST-ACTION (Line 84-87):**
```
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, user answers, gate result, timestamp
- Append mode (don't overwrite existing content)
```

**Infrastructure Scaffolding (Line 201-248):**
```
DEF-060: Auto-scaffolds test data infrastructure based on strategy.
- tests/data/ directory
- tests/data/test_users.json (if static or dynamic)
- tests/{workflow}/data/ (if workflow or both)
```

### Gate Implementation (qg_preflight.py)

**Currently Validates:**
- ✅ credential_strategy (static/dynamic/self-contained/none) - Lines 56-62
- ✅ test_data_location (shared/workflow/both/none) - Lines 64-70
- ✅ browser_config.headless (must be false) - Lines 73-76
- ✅ timeout_config.enabled (boolean) - Lines 78-82
- ✅ timeout_config.threshold_seconds (positive number if enabled) - Lines 78-82
- ✅ Test data infrastructure scaffolding - Lines 84-91, 196-248
- ✅ Transcript validation - via universal `validate_and_pass()` helper

### Validation Gaps

**NONE** - Step 2 is complete!

### NEEDS_RETRY Gaps

**NONE** - DEF-060 infrastructure scaffolding already implemented!

---

## Step 3: AI Processing

### Protocol Requirements (step-03.md)

**POST-ACTION (Line 53-56):**
```
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, AI analysis (intent, BDD scenarios, expected states), gate result, timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
```

**BDD Structure (Line 40-43):**
```
- CREATE BDD scenario with Given/When/Then structure
- EXTRACT expected_states from "Then" clauses (DD-09)
- DETERMINE intent (action verb from requirement)
```

**Retry Logic (Line 48-50):**
```
- If gate FAIL: AI retries processing (max 3 attempts)
- After 3 failures: STOP → REPORT → USER DECIDES
```

### Gate Implementation (qg_ai_processing.py)

**Currently Validates:**
- ✅ bdd_scenarios (non-empty list with valid Given/When/Then) - Lines 46-52, 92-136
- ✅ expected_states (at least one state from Then clauses) - Lines 54-60, 139-148
- ✅ intent (non-empty action verb) - Lines 62-68, 151-155
- ✅ Transcript validation - via universal `validate_and_pass()` helper

### Validation Gaps

**GAP-03-01: Retry attempt tracking**
- **Protocol says:** "If gate FAIL: AI retries processing (max 3 attempts)"
- **Gate does:** No attempt tracking, no max retry enforcement
- **Missing:** Attempt counter in state, BLOCKED response after 3 failures
- **Impact:** AI could retry indefinitely instead of STOP → REPORT → USER DECIDES
- **Fix:** Add attempt tracking like qg_test_scenarios.py (lines 124-134)
- **Note:** This is a CROSS-CUTTING issue - applies to Step 4 and 5 too

### NEEDS_RETRY Gaps

**NONE** - Step 3 is validation-only (no infrastructure to scaffold)

---

## Step 4: Tool 1 - Generate Tests

### Protocol Requirements (step-04.md)

**POST-ACTION (Line 60-63):**
```
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, tool input/output, PRE/POST gate results, timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
```

**Retry Logic (Line 55-58):**
```
- If PRE-VALIDATE fails: AI fixes input (max 3 attempts)
- If POST-VALIDATE fails: AI retries operation (max 3 attempts)
- After 3 failures: STOP → REPORT → USER DECIDES
```

**Workflow Validation (Line 118-120):**
```
| `workflow` | One of: auth, catalog, cart, checkout |
```

### Gate Implementation (qg_test_scenarios.py)

**Currently Validates:**
- ✅ PRE: Step 3 complete - Lines 67-72
- ✅ PRE: metadata_context present with bdd_scenarios, expected_states, intent - Lines 74-89
- ✅ PRE: workflow is valid (dynamic - any non-empty string) - Lines 91-97
- ✅ POST: test_scenarios present and not empty - Lines 170-184
- ✅ POST: Each scenario has name, given, when, then - Lines 186-200
- ✅ POST: No skeleton code patterns (DD-25) - Lines 202-208
- ✅ Attempt tracking with BLOCKED response - Lines 124-134
- ✅ Transcript validation - via universal `validate_and_pass()` helper

### Validation Gaps

**GAP-04-01: Workflow enum constraint removed**
- **Protocol says:** "workflow | One of: auth, catalog, cart, checkout"
- **Gate does:** "workflow is valid (dynamic - any non-empty string)" - Line 92-93
- **Status:** INTENTIONAL CHANGE (see qg_user_input.py comment line 15-16)
- **Impact:** None - framework is now domain-agnostic
- **Action:** Update protocol to match implementation (remove enum constraint)

### NEEDS_RETRY Gaps

**NONE** - Step 4 is operation-only (Tool 1 generates scenarios, no infrastructure)

---

## Step 5: Tool 2 - Discover Elements

### Protocol Requirements (step-05.md)

**POST-ACTION (Line 174-177):**
```
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, pages discovered, element counts, PRE/POST gate results, timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
```

**Navigation Tracking (Line 44-85):**
```
INITIALIZE NAVIGATION TRACKER (MANDATORY - DD-44 ENFORCEMENT)

BEFORE any navigation, create tracker:
from mcp_server.utils.scope_discovery import create_navigation_tracker
tracker = create_navigation_tracker(evaluate_fn=eval_js)

**CRITICAL:** Call tracker.register_page(url) AFTER EVERY navigation.
```

**DD-33 Decision Point (Line 87-122):**
```
Was Playwright used to prepare page state (login, click, modal, form submit)?
  YES ──► MUST use DD-33 (Playwright snapshot extraction)
          discovery_method = "playwright"
  NO  ──► May use Tool 2
          discovery_method = "tool2"
```

**Visual Feedback Enforcement (Line 128-166):**
```
After discovery, MUST validate each element via RuntimeValidator:
1. INITIALIZE visual feedback
2. For EACH discovered element: validator.validate_element(element)
3. COLLECT validation_results
4. PASS validation_results to qg_discovered_elements POST

**Why Mandatory:** Visual feedback shows user which elements passed/failed validation
in real-time. Skipping RuntimeValidator = no visual highlights = poor user experience.
```

**Two-Pass Discovery (Line 530-711):**
```
PASS 1: INPUT ELEMENT DISCOVERY (for all pages)
  - type="input"
  - textboxes, buttons, dropdowns

PASS 2: OUTPUT ELEMENT DISCOVERY (for all pages)
  - type="output"
  - success messages, error messages, confirmation text

CHECKPOINT: Before Step 6
- Verify ALL pages have BOTH input_elements AND output_elements
```

### Gate Implementation (qg_discovered_elements.py)

**Currently Validates:**
- ✅ PRE: Step 4 complete - Lines 78-83
- ✅ PRE: URL is valid HTTP/HTTPS - Lines 86-103
- ✅ PRE: page_name present - Lines 105-117
- ✅ PRE: credential_strategy valid - Lines 119-131
- ✅ PRE: discovery_method valid (tool2 or playwright) - Lines 133-145
- ✅ PRE: element type valid (input or output) - Lines 147-154
- ✅ PRE: Multi-page scope_result validation (DD-44) - Lines 156-186
- ✅ POST: elements array present and not empty - Lines 611-630
- ✅ POST: Each element has suggested_name, element_type, at least one locator - Lines 633-636
- ✅ POST: page_name is PascalCase - Lines 686-703
- ✅ POST: validation_results structure (DD-46) - Lines 638-683
- ✅ POST: Two-pass discovery tracking (DEF-045) - Lines 706-767
- ✅ Attempt tracking with BLOCKED response - Lines 565-574
- ✅ Transcript validation - via universal `validate_and_pass()` helper
- ✅ Navigation-based scope detection (Task 26.0) - Lines 355-504

### Validation Gaps

**GAP-05-01: Navigation tracker not enforced**
- **Protocol says:** "INITIALIZE NAVIGATION TRACKER (MANDATORY - DD-44 ENFORCEMENT)" (Line 44)
- **Gate does:** Auto-detects multi-page from BDD OR audit log, but doesn't enforce tracker usage
- **Missing:** Check if tracker was initialized, warn if bypassed
- **Impact:** AI could skip tracker.register_page() calls, lose navigation history
- **Fix:** Add protocol guidance to remind AI to use tracker (not a gate check)
- **Note:** Task 26.0 PASS 0 already provides fallback via audit log reading

**GAP-05-02: DD-33 decision enforcement**
- **Protocol says:** "Was Playwright used? YES → MUST use DD-33" (Line 88-93)
- **Gate does:** Validates discovery_method is declared, but doesn't enforce the decision logic
- **Missing:** Detect if Playwright was used (check audit log), block if Tool 2 called after Playwright prep
- **Impact:** AI could use Tool 2 after Playwright navigation (violates DD-33)
- **Fix:** Add `_check_playwright_usage()` - read audit log, enforce DD-33 decision
- **Note:** This is GUIDANCE more than enforcement - AI makes the choice

**GAP-05-03: RuntimeValidator enforcement for tool2**
- **Protocol says:** "After discovery, MUST validate each element via RuntimeValidator" (Line 128-166)
- **Gate does:** Enforces validation_results for tool2, auto-validates for playwright (Lines 638-679)
- **Status:** ALREADY ENFORCED (DEF-058 smart conditional enforcement)
- **Action:** None - gate correctly handles both flows

### NEEDS_RETRY Gaps

**RETRY-05-01: Page directories scaffolding**
- **Missing infrastructure:** `framework/pages/{workflow}/{page_name}/` directories
- **Current behavior:** Directories created manually later when POMs are written
- **NEEDS_RETRY pattern:** Scaffold page directories when multi-page detected
- **Fix:** Add `_check_page_directories()` in PRE validation, return scaffolding template

**RETRY-05-02: RuntimeValidator initialization**
- **Missing setup:** RuntimeValidator + VisualFeedback initialization code
- **Current behavior:** AI must manually import and initialize (easy to forget)
- **NEEDS_RETRY pattern:** Provide initialization template if missing
- **Fix:** Add `_check_runtime_validator_initialized()` - check if validator was used
- **Note:** This might be too intrusive - validator is AI's tool, not infrastructure

---

## Cross-Cutting Issues

### Issue 1: Retry Attempt Tracking Inconsistency

**Problem:** Only Steps 4-5 have attempt tracking (max 3 retries), Steps 1-3 don't.

**Protocol Requirements:**
- Step 1: "No max retries (user provides input, not AI)" - Lines 67-69 (step-01.md)
- Step 2: "No max retries (user provides input, not AI)" - Lines 79-81 (step-02.md)
- Step 3: "If gate FAIL: AI retries processing (max 3 attempts)" - Lines 48-50 (step-03.md)

**Current Implementation:**
- Step 1: ✅ No retry tracking (correct - user input)
- Step 2: ✅ No retry tracking (correct - user input)
- Step 3: ❌ No retry tracking (MISSING - should have max 3)
- Step 4: ✅ Has retry tracking (correct - AI operation)
- Step 5: ✅ Has retry tracking (correct - AI operation)

**Fix:** Add attempt tracking to Step 3 (qg_ai_processing.py) using same pattern as Step 4.

---

## Recommendations

### Priority 1: Critical Gaps (Fix Immediately)

1. **GAP-03-01:** Add retry attempt tracking to Step 3 (qg_ai_processing.py)
   - Pattern: Copy from qg_test_scenarios.py lines 124-134
   - Add: `STEP_NUMBER = 3`, `MAX_ATTEMPTS = 3`, attempt tracking in validate()

### Priority 2: Infrastructure Scaffolding (High Value)

2. **RETRY-01-01:** Workflow directory scaffolding in Step 1
   - Add: `_check_workflow_directories()` method
   - Return: NEEDS_RETRY with mkdir templates for framework/pages/{workflow}/, tests/{workflow}/

3. **RETRY-05-01:** Page directory scaffolding in Step 5
   - Add: `_check_page_directories()` in PRE validation
   - Return: NEEDS_RETRY with mkdir templates for framework/pages/{workflow}/{page_name}/

### Priority 3: Validation Improvements (Medium Value)

4. **GAP-01-02:** Role name derivation validation in Step 1
   - Add: Logic to verify role_name is PascalCase conversion of persona
   - Consider: Fuzzy matching ("sales representative" → "SalesRepresentative", "SalesRep", "SalesRepUser")

5. **GAP-05-02:** DD-33 decision enforcement in Step 5
   - Add: `_check_playwright_usage()` - read audit log for Playwright tool calls
   - Warn: If Playwright used but discovery_method="tool2"

### Priority 4: Documentation Updates (Low Value)

6. **GAP-04-01:** Update step-04.md protocol to reflect dynamic workflow validation
   - Change: Remove hardcoded workflow enum (auth, catalog, cart, checkout)
   - Document: Any non-empty string is valid (domain-agnostic framework)

---

## Implementation Plan

### Phase 1: Add Missing Validation (Priority 1)

**Task 1.1:** Add retry tracking to Step 3
```python
# In qg_ai_processing.py
class QGAIProcessing(BaseGate):
    STEP_NUMBER = 3
    MAX_ATTEMPTS = 3  # From protocol line 48-50

    @classmethod
    def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Check if blocked
        state_manager = cls._get_state_manager()
        if state_manager:
            attempts = state_manager.get_attempt_count(cls.STEP_NUMBER)
            if attempts >= cls.MAX_ATTEMPTS:
                return cls.blocked_response(
                    step=cls.STEP_NUMBER,
                    attempts=attempts,
                    errors=[]
                )

        # Run validation...
        result = cls._validate_internal(input_data)

        # Track attempts
        if state_manager:
            if result.get("status") == "fail":
                state_manager.increment_attempt(cls.STEP_NUMBER)
            elif result.get("status") == "pass":
                state_manager.reset_attempts(cls.STEP_NUMBER)

        return result
```

### Phase 2: Add Infrastructure Scaffolding (Priority 2)

**Task 2.1:** Workflow directory scaffolding in Step 1
```python
# In base_gate.py (universal helper)
@classmethod
def _check_workflow_directories(cls, workflow: str) -> Optional[Dict[str, Any]]:
    """
    Check if workflow directories exist, scaffold if missing.

    Required directories:
    - framework/pages/{workflow}/
    - tests/{workflow}/
    """
    from pathlib import Path

    missing = []

    pages_dir = Path(f"framework/pages/{workflow}")
    if not pages_dir.exists():
        missing.append({
            "type": "directory",
            "path": f"framework/pages/{workflow}",
            "reason": f"Page objects for {workflow} workflow"
        })

    tests_dir = Path(f"tests/{workflow}")
    if not tests_dir.exists():
        missing.append({
            "type": "directory",
            "path": f"tests/{workflow}",
            "reason": f"Tests for {workflow} workflow"
        })

    if missing:
        return {
            "status": "NEEDS_RETRY",
            "fix_applied": "workflow_directories_scaffolded",
            "error": f"Missing workflow directories for '{workflow}'",
            "message": "Create the following directories:",
            "scaffolding_needed": missing
        }

    return None

# In qg_user_input.py validate() - add before validate_and_pass()
workflow_check = cls._check_workflow_directories(workflow)
if workflow_check:
    return workflow_check  # NEEDS_RETRY
```

**Task 2.2:** Page directory scaffolding in Step 5
```python
# In qg_discovered_elements.py validate_pre()
# Add after scope_result validation (line 186)
page_dir_check = cls._check_page_directories(workflow, page_name)
if page_dir_check:
    return page_dir_check  # NEEDS_RETRY

# Helper method in base_gate.py or qg_discovered_elements.py
@classmethod
def _check_page_directories(cls, workflow: str, page_name: str) -> Optional[Dict[str, Any]]:
    """Check if page directory exists for POM generation."""
    from pathlib import Path

    page_dir = Path(f"framework/pages/{workflow}")
    if not page_dir.exists():
        return {
            "status": "NEEDS_RETRY",
            "fix_applied": "page_directory_scaffolded",
            "error": f"Missing page directory for workflow '{workflow}'",
            "message": f"Create directory for {page_name} in workflow {workflow}:",
            "scaffolding_needed": [{
                "type": "directory",
                "path": f"framework/pages/{workflow}",
                "reason": f"Store page objects for {workflow} workflow"
            }]
        }

    return None
```

### Phase 3: Validation Improvements (Priority 3)

**Task 3.1:** Role name derivation validation in Step 1
```python
# In qg_user_input.py
@classmethod
def _is_valid_role_name_for_persona(cls, role_name: str, persona: str) -> bool:
    """
    Check if role_name is a valid PascalCase conversion of persona.

    Examples:
    - "sales representative" → "SalesRepresentative" ✓
    - "sales representative" → "SalesRep" ✓ (abbreviation)
    - "sales representative" → "GuestUser" ✗ (unrelated)
    """
    # Extract words from persona
    persona_words = persona.lower().split()

    # Extract words from role_name (split on capital letters)
    import re
    role_words = re.findall(r'[A-Z][a-z]*', role_name)

    # Check if role_words contains most persona_words
    # Allow abbreviations (e.g., SalesRep for SalesRepresentative)
    matches = 0
    for persona_word in persona_words:
        for role_word in role_words:
            if role_word.lower().startswith(persona_word[:3]):  # Match first 3 chars
                matches += 1
                break

    # At least 50% of persona words should match
    return matches >= len(persona_words) * 0.5

# In validate() - update role_name check (line 87-92)
if not cls._is_valid_role_name(role_name):
    return cls.fail_response(...)

# Add new check
if not cls._is_valid_role_name_for_persona(role_name, persona):
    return cls.fail_response(
        error=f"role_name '{role_name}' doesn't match persona '{persona}'",
        fix_hint=f"role_name must be derived from persona. Expected: {cls._suggest_role_name(persona)}"
    )
```

---

## Summary

**Total Gaps Found:** 7 validation gaps + 3 NEEDS_RETRY gaps = **10 gaps**

**Critical (Fix Now):**
- GAP-03-01: Step 3 retry tracking

**High Value (Next):**
- RETRY-01-01: Workflow directory scaffolding
- RETRY-05-01: Page directory scaffolding

**Medium Value (Later):**
- GAP-01-02: Role name derivation
- GAP-05-02: DD-33 enforcement

**Low Value (Docs):**
- GAP-04-01: Update protocol

**Already Fixed:**
- Step 2: Complete (no gaps)
- Transcript validation: Universal helper enforces across all steps
- Two-pass discovery: Fully implemented
- Navigation tracking: Audit-based PASS 0 provides fallback

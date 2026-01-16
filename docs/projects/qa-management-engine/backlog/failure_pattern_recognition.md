# Failure Pattern Recognition

**Status:** Idea
**Created:** 2026-01-14
**Target Version:** v1.1 (Post-MVP)
**Effort:** 4-5 hours
**Impact:** Medium (speeds debugging, reduces retry loops)

---

## Context

Extracted from HITL function enhancements during Parabank10 validation. Currently, Step 11 returns raw error messages. AI must analyze and suggest fixes manually.

---

## Problem

**Current State:**
- Test fails → raw error returned to AI
- AI analyzes error → suggests fix
- No pattern library (AI reinvents analysis each time)
- No targeted suggestions (generic "check locator" advice)

**Example:**
```
❌ Test failed: Element ACCOUNT_ACTIVITY_LINK not found
```

AI response: "Check if locator is correct. Try different selector."

**What's Missing:**
- Pattern detection (locator type mismatch vs timing issue)
- Targeted suggestions (specific to pattern type)
- Historical learning (remember past issues)

---

## Proposed Solution

**Vision:** Detect common failure patterns and provide targeted fix suggestions

### Features

**Detect common failure patterns:**
1. **Timing issues** (element not ready)
2. **Locator type mismatches** (`<a>` vs `<p>`)
3. **Network timeouts**
4. **Stale element references**
5. **Incorrect wait conditions**

**Provide targeted suggestions** based on pattern

---

## Implementation

### Pattern Library

```python
# mcp_server/tools/gates/failure_patterns.py
class FailurePatternDetector:
    PATTERNS = {
        "timing": {
            "indicators": [
                "element not found",
                "timeout waiting for element",
                "element not visible"
            ],
            "suggestion": "Add explicit wait or increase timeout"
        },
        "locator_mismatch": {
            "indicators": [
                "expected <a> but found <p>",
                "wrong element type"
            ],
            "suggestion": "Update locator to match actual element type"
        },
        "network_timeout": {
            "indicators": [
                "connection timeout",
                "network error",
                "failed to load page"
            ],
            "suggestion": "Check network connection or increase page load timeout"
        },
        "stale_element": {
            "indicators": [
                "stale element reference",
                "element is no longer attached to DOM"
            ],
            "suggestion": "Re-locate element before interaction"
        }
    }

    def detect_pattern(self, error_message: str) -> dict:
        """Detect failure pattern from error message."""
        for pattern_name, pattern_data in self.PATTERNS.items():
            for indicator in pattern_data["indicators"]:
                if indicator.lower() in error_message.lower():
                    return {
                        "pattern": pattern_name,
                        "suggestion": pattern_data["suggestion"],
                        "confidence": "high"
                    }

        return {"pattern": "unknown", "suggestion": "Review error logs", "confidence": "low"}
```

### Enhanced Step 11 Output

```python
# mcp_server/tools/gates/qg_execution.py
def _analyze_failure(self, test_result: dict) -> dict:
    """Analyze failure and detect pattern."""
    detector = FailurePatternDetector()
    pattern_result = detector.detect_pattern(test_result["error"])

    return {
        "test_failed": True,
        "error": test_result["error"],
        "pattern_detected": pattern_result["pattern"],
        "suggested_fix": pattern_result["suggestion"],
        "confidence": pattern_result["confidence"],
        "additional_context": self._get_failure_context(test_result)
    }
```

---

## Example Output

**Before:**
```
❌ Test failed: Element ACCOUNT_ACTIVITY_LINK not found
```

**After:**
```
❌ Test failed: Element ACCOUNT_ACTIVITY_LINK not found

PATTERN DETECTED: Locator Type Mismatch
Confidence: High

CONTEXT:
- Expected: <a> (link)
- Found: <p> (paragraph) with similar text "Account Activity"

SUGGESTED FIX:
Update locator from:
  ACCOUNT_ACTIVITY_LINK = (By.CSS_SELECTOR, "a.activity-link")
To:
  ACCOUNT_ACTIVITY_TEXT = (By.CSS_SELECTOR, "p.activity-text")

Or verify if element type changed in latest UI update.
```

---

## Pattern Examples

### 1. Timing Issue

**Error:** `Element LOGIN_BUTTON not found`

**Detection:**
- Error contains "not found"
- Element exists in snapshot but not interactable

**Suggestion:**
```
PATTERN: Timing Issue
Element exists but not ready for interaction.

SUGGESTED FIX:
Add explicit wait before click:
  self.web.wait_for_element(*self.LOGIN_BUTTON, timeout=10)
  self.web.click(*self.LOGIN_BUTTON)
```

---

### 2. Locator Type Mismatch

**Error:** `Expected <a> but found <p>`

**Detection:**
- Error contains "expected" and "found"
- Element type mismatch

**Suggestion:**
```
PATTERN: Locator Type Mismatch
UI changed element type from link to paragraph.

SUGGESTED FIX:
1. Update locator name:
   ACCOUNT_LINK → ACCOUNT_TEXT

2. Update selector:
   (By.CSS_SELECTOR, "a.account") → (By.CSS_SELECTOR, "p.account")

3. Verify UI hasn't changed unexpectedly
```

---

### 3. Stale Element

**Error:** `StaleElementReferenceException`

**Detection:**
- Error contains "stale element"

**Suggestion:**
```
PATTERN: Stale Element Reference
Element was re-rendered by JavaScript.

SUGGESTED FIX:
Re-locate element before each interaction:
  # BAD
  element = self.web.find_element(*locator)
  element.click()
  element.send_keys("text")  # Fails if DOM updated

  # GOOD
  self.web.click(*locator)  # Re-locates internally
  self.web.type_text(*locator, "text")
```

---

## Value

**Benefits:**
- ✅ Faster debugging (pattern suggests fix immediately)
- ✅ Reduced retry loops (specific guidance)
- ✅ Learning over time (pattern library grows)
- ✅ Consistency (same patterns get same suggestions)

**Success Metric:** 50% reduction in retry attempts due to better guidance

---

## Future Enhancements (v1.2+)

**Learning Memory:**
- Track which suggestions resolved issues
- Build success rate per pattern
- Prioritize high-success suggestions

**Playwright Snapshot Integration:**
- Scan DOM for similar elements on mismatch
- Generate alternative locator suggestions
- Visual diff of expected vs actual element

---

## Implementation Plan

1. Create `FailurePatternDetector` class with initial pattern library
2. Integrate into qg_execution (Step 11)
3. Test with known failure patterns (timing, locator mismatch, network)
4. Add patterns as new issues discovered
5. Update step-11.md protocol with pattern examples

**Effort:** 4-5 hours

---

## Configuration

**Environment Variables:**
```bash
# Pattern detection
PATTERN_DETECTION_ENABLED=true    # Enable pattern detection
PATTERN_CONFIDENCE_THRESHOLD=0.7  # Min confidence to suggest fix

# Pattern library
PATTERN_LIBRARY_PATH=mcp_server/tools/gates/patterns.json  # Custom patterns
```

---

## Next Steps

1. Move to backlog when ready to implement
2. Implement in v1.1 (post-MVP quick win)
3. Test with real-world failures
4. Build pattern library from production issues

# Element Inspector Hints

**Status:** Idea
**Created:** 2026-01-14
**Target Version:** v1.1 (Post-MVP)
**Effort:** 3-4 hours
**Impact:** Medium (faster locator debugging)

---

## Context

Extracted from HITL function enhancements. When element not found, AI currently has no visibility into what similar elements exist on the page.

---

## Problem

**Current State:**
- Test fails: "Element TRANSFER_BUTTON not found"
- AI has no visibility into page DOM
- AI guesses alternative locators blindly
- Multiple retry attempts needed

**What's Missing:**
- DOM inspection on failure
- Similar element detection
- Alternative locator suggestions
- Visual feedback on what exists

---

## Proposed Solution

**Vision:** When element not found, scan DOM for similar elements and suggest alternatives

### Features

**Scan DOM for similar elements:**
1. Similar text content
2. Similar class names
3. Similar IDs
4. Same tag but different selector
5. Same role/aria attributes

**Suggest alternative locators** with confidence score

---

## Implementation

### DOM Scanner

```python
# mcp_server/tools/gates/element_inspector.py
class ElementInspector:
    def __init__(self, playwright_page):
        self.page = playwright_page

    def find_similar_elements(self, target_locator: tuple, target_text: str = None) -> List[dict]:
        """Find elements similar to target on current page."""
        locator_type, locator_value = target_locator
        snapshot = self.page.accessibility_tree()  # Get snapshot

        similar_elements = []

        # 1. Find by similar text
        if target_text:
            similar_elements.extend(self._find_by_text(snapshot, target_text))

        # 2. Find by similar class/id
        similar_elements.extend(self._find_by_attributes(snapshot, locator_value))

        # 3. Find by same tag
        similar_elements.extend(self._find_by_tag(snapshot, locator_type))

        return self._rank_by_similarity(similar_elements, target_locator, target_text)

    def _find_by_text(self, snapshot: dict, target_text: str) -> List[dict]:
        """Find elements with similar text content."""
        results = []
        for element in self._traverse_snapshot(snapshot):
            if "text" in element:
                similarity = self._text_similarity(element["text"], target_text)
                if similarity > 0.6:  # 60% match threshold
                    results.append({
                        "element": element,
                        "similarity": similarity,
                        "match_type": "text"
                    })
        return results

    def _find_by_attributes(self, snapshot: dict, locator_value: str) -> List[dict]:
        """Find elements with similar class/id attributes."""
        results = []
        for element in self._traverse_snapshot(snapshot):
            if "class" in element or "id" in element:
                similarity = self._attribute_similarity(element, locator_value)
                if similarity > 0.5:
                    results.append({
                        "element": element,
                        "similarity": similarity,
                        "match_type": "attribute"
                    })
        return results
```

### Step 11 Integration

```python
# mcp_server/tools/gates/qg_execution.py
def _inspect_page_on_failure(self, error: str, test_code: str) -> dict:
    """Inspect page DOM when element not found."""
    if "not found" not in error.lower():
        return {}

    # Extract target locator from error
    target_locator = self._extract_locator_from_error(error)

    # Scan page for similar elements
    inspector = ElementInspector(self.playwright_page)
    similar_elements = inspector.find_similar_elements(target_locator)

    return {
        "similar_elements_found": len(similar_elements),
        "suggestions": self._generate_locator_suggestions(similar_elements),
        "confidence": "high" if similar_elements else "low"
    }
```

---

## Example Output

**Before:**
```
❌ Element TRANSFER_BUTTON not found
```

**After:**
```
❌ Element TRANSFER_BUTTON not found

SIMILAR ELEMENTS FOUND: 3

1. <button class="btn-transfer"> (id="submit-transfer")
   Match: 85% (similar class name)
   Suggested: TRANSFER_BUTTON = (By.ID, "submit-transfer")

2. <input type="submit" value="Transfer Funds">
   Match: 70% (similar text content)
   Suggested: TRANSFER_SUBMIT = (By.CSS_SELECTOR, "input[value='Transfer Funds']")

3. <a class="transfer-link" href="/transfer">
   Match: 60% (similar text "Transfer")
   Suggested: TRANSFER_LINK = (By.CSS_SELECTOR, "a.transfer-link")

RECOMMENDATION:
Try suggestion #1 first (highest confidence)
```

---

## Similarity Algorithms

### 1. Text Similarity (Levenshtein Distance)

```python
def _text_similarity(self, text1: str, text2: str) -> float:
    """Calculate text similarity using Levenshtein distance."""
    distance = levenshtein_distance(text1.lower(), text2.lower())
    max_len = max(len(text1), len(text2))
    return 1 - (distance / max_len)
```

### 2. Attribute Similarity (Token Match)

```python
def _attribute_similarity(self, element: dict, target: str) -> float:
    """Calculate attribute similarity using token matching."""
    element_tokens = set(element.get("class", "").split() + [element.get("id", "")])
    target_tokens = set(target.split())

    intersection = element_tokens & target_tokens
    union = element_tokens | target_tokens

    return len(intersection) / len(union) if union else 0
```

### 3. Ranking (Combined Score)

```python
def _rank_by_similarity(self, elements: List[dict], target_locator: tuple, target_text: str) -> List[dict]:
    """Rank elements by combined similarity score."""
    for element in elements:
        # Weight: text (40%), attribute (30%), tag (20%), position (10%)
        text_score = element.get("text_similarity", 0) * 0.4
        attr_score = element.get("attr_similarity", 0) * 0.3
        tag_score = element.get("tag_match", 0) * 0.2
        pos_score = element.get("position_score", 0) * 0.1

        element["combined_score"] = text_score + attr_score + tag_score + pos_score

    return sorted(elements, key=lambda x: x["combined_score"], reverse=True)
```

---

## Value

**Benefits:**
- ✅ Faster locator debugging (immediate suggestions)
- ✅ Reduced guesswork (data-driven alternatives)
- ✅ Higher first-retry success rate (prioritized by confidence)
- ✅ Visual feedback (user sees what's actually on page)

**Success Metric:** 80% of locator issues resolved in first retry

---

## Future Enhancements (v1.2+)

**Visual Bounding Boxes:**
- Highlight similar elements in screenshot
- Show expected vs actual element position
- Generate visual diff report

**XPath/CSS Selector Generator:**
- Auto-generate multiple selector options
- Test each selector for uniqueness
- Suggest most robust option

---

## Implementation Plan

1. Create `ElementInspector` class with similarity algorithms
2. Integrate with Playwright snapshot API
3. Add to qg_execution failure handling
4. Test with known "element not found" failures
5. Tune similarity thresholds based on real-world data
6. Update step-11.md protocol

**Effort:** 3-4 hours

---

## Dependencies

- Playwright snapshot/accessibility tree API
- Levenshtein distance library (or custom implementation)

---

## Configuration

**Environment Variables:**
```bash
# Element inspection
ELEMENT_INSPECTION_ENABLED=true     # Enable DOM scanning on failure
TEXT_SIMILARITY_THRESHOLD=0.6       # Min text match (60%)
ATTR_SIMILARITY_THRESHOLD=0.5       # Min attribute match (50%)
MAX_SUGGESTIONS=5                   # Max alternative locators to suggest
```

---

## Next Steps

1. Move to backlog when ready to implement
2. Implement in v1.1 (post-MVP quick win)
3. Test with real-world "element not found" failures
4. Build locator suggestion library

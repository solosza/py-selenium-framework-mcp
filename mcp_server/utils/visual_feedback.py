"""
Visual Feedback - Task 6.0

Single Responsibility: "Show validation results visually in browser"

Provides visual feedback during runtime validation by injecting CSS/HTML
into the browser via Playwright's browser_evaluate.

Features:
- Green outline (3px solid #00ff00) for valid elements
- Red outline (3px solid #ff0000) for invalid elements with error label
- 3-step pipeline status header display
- Element-by-element results panel

Design Notes:
- Uses JavaScript injection via Playwright MCP browser_evaluate
- Gracefully handles headless mode (skips visual injection)
- All injected elements use unique IDs to avoid conflicts
- Cleanup removes all injected elements

PRD Reference: enhanced-runtime-validation FR-81 to FR-88
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

# CSS styles for visual feedback
VALIDATION_CSS = """
.qa-validation-overlay {
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 999999;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12px;
    background: rgba(0, 0, 0, 0.85);
    color: #fff;
    padding: 15px;
    border-radius: 8px;
    max-width: 400px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.qa-pipeline-header {
    font-size: 14px;
    font-weight: bold;
    color: #00ff00;
    margin-bottom: 10px;
    border-bottom: 1px solid #444;
    padding-bottom: 8px;
}

.qa-pipeline-step {
    padding: 4px 0;
    display: flex;
    align-items: center;
}

.qa-step-name {
    flex: 1;
    color: #aaa;
}

.qa-step-status {
    font-weight: bold;
    margin-left: 10px;
}

.qa-step-ok {
    color: #00ff00;
}

.qa-step-fail {
    color: #ff0000;
}

.qa-step-pending {
    color: #ffff00;
}

.qa-results-panel {
    margin-top: 10px;
    border-top: 1px solid #444;
    padding-top: 8px;
}

.qa-result-item {
    padding: 3px 0;
    display: flex;
    align-items: center;
}

.qa-result-ok {
    color: #00ff00;
}

.qa-result-fail {
    color: #ff0000;
}

.qa-result-ref {
    color: #888;
    margin-left: 5px;
    font-size: 10px;
}

.qa-element-highlight-valid {
    outline: 3px solid #00ff00 !important;
    outline-offset: 2px !important;
}

.qa-element-highlight-invalid {
    outline: 3px solid #ff0000 !important;
    outline-offset: 2px !important;
}

.qa-element-label {
    position: absolute;
    background: #ff0000;
    color: white;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 3px;
    z-index: 999998;
    font-family: 'Consolas', monospace;
}
"""

# JavaScript for injecting visual elements
INJECT_CSS_JS = """
(function() {
    if (document.getElementById('qa-validation-styles')) return;
    const style = document.createElement('style');
    style.id = 'qa-validation-styles';
    style.textContent = `%s`;
    document.head.appendChild(style);
})();
"""

HIGHLIGHT_ELEMENT_JS = """
(function(ref, isValid, errorCategory) {
    // Find element by ref attribute or data-ref
    let el = document.querySelector(`[data-ref="${ref}"]`);
    if (!el) {
        // Try finding by aria-label or other means
        const allElements = document.querySelectorAll('*');
        for (const e of allElements) {
            if (e.getAttribute('aria-label') === ref ||
                e.textContent.trim() === ref ||
                e.id === ref) {
                el = e;
                break;
            }
        }
    }

    if (!el) return false;

    // Add highlight class
    el.classList.remove('qa-element-highlight-valid', 'qa-element-highlight-invalid');
    el.classList.add(isValid ? 'qa-element-highlight-valid' : 'qa-element-highlight-invalid');

    // Add error label for invalid elements
    if (!isValid && errorCategory) {
        const label = document.createElement('div');
        label.className = 'qa-element-label qa-injected';
        label.textContent = errorCategory;
        label.style.cssText = `
            position: absolute;
            top: ${el.getBoundingClientRect().top + window.scrollY - 20}px;
            left: ${el.getBoundingClientRect().left + window.scrollX}px;
        `;
        document.body.appendChild(label);
    }

    return true;
})('%s', %s, '%s');
"""

CREATE_OVERLAY_JS = """
(function() {
    // Remove existing overlay
    const existing = document.getElementById('qa-validation-overlay');
    if (existing) existing.remove();

    // Create new overlay
    const overlay = document.createElement('div');
    overlay.id = 'qa-validation-overlay';
    overlay.className = 'qa-validation-overlay';
    overlay.innerHTML = `
        <div class="qa-pipeline-header">RUNTIME VALIDATION PIPELINE</div>
        <div id="qa-pipeline-steps"></div>
        <div id="qa-results-panel" class="qa-results-panel"></div>
    `;
    document.body.appendChild(overlay);
    return true;
})();
"""

UPDATE_STEP_JS = """
(function(stepNum, stepName, status, details) {
    const container = document.getElementById('qa-pipeline-steps');
    if (!container) return false;

    let stepEl = document.getElementById(`qa-step-${stepNum}`);
    if (!stepEl) {
        stepEl = document.createElement('div');
        stepEl.id = `qa-step-${stepNum}`;
        stepEl.className = 'qa-pipeline-step';
        container.appendChild(stepEl);
    }

    const statusClass = status === 'OK' ? 'qa-step-ok' :
                        status === 'FAIL' ? 'qa-step-fail' : 'qa-step-pending';

    stepEl.innerHTML = `
        <span class="qa-step-name">Step ${stepNum}: ${stepName}</span>
        <span class="qa-step-status ${statusClass}">[${status}] ${details}</span>
    `;

    return true;
})(%d, '%s', '%s', '%s');
"""

ADD_RESULT_JS = """
(function(elementName, ref, isValid, errorCategory) {
    const panel = document.getElementById('qa-results-panel');
    if (!panel) return false;

    const item = document.createElement('div');
    item.className = `qa-result-item ${isValid ? 'qa-result-ok' : 'qa-result-fail'}`;

    const icon = isValid ? '[OK]' : '[X]';
    const error = isValid ? '' : ` - ${errorCategory}`;

    item.innerHTML = `
        ${icon} ${elementName}${error}
        <span class="qa-result-ref">[${ref}]</span>
    `;

    panel.appendChild(item);
    return true;
})('%s', '%s', %s, '%s');
"""

CLEANUP_JS = """
(function() {
    // Remove overlay
    const overlay = document.getElementById('qa-validation-overlay');
    if (overlay) overlay.remove();

    // Remove styles
    const styles = document.getElementById('qa-validation-styles');
    if (styles) styles.remove();

    // Remove highlight classes
    document.querySelectorAll('.qa-element-highlight-valid, .qa-element-highlight-invalid')
        .forEach(el => {
            el.classList.remove('qa-element-highlight-valid', 'qa-element-highlight-invalid');
        });

    // Remove labels
    document.querySelectorAll('.qa-injected').forEach(el => el.remove());

    return true;
})();
"""


@dataclass
class VisualFeedback:
    """
    Provides visual feedback during runtime validation.

    Injects CSS/HTML into the browser to highlight validated elements
    and display pipeline status.

    Usage:
        # With Playwright MCP
        visual = VisualFeedback(evaluate_fn=browser_evaluate)
        visual.initialize()
        visual.show_pipeline_header(scope_result, validation_results, "Ready")
        visual.highlight_valid("e72")
        visual.highlight_invalid("e99", "NOT_VISIBLE")
        visual.cleanup()

        # For testing (no browser)
        visual = VisualFeedback()  # headless mode
        visual.highlight_valid("e72")  # no-op, returns False
    """
    evaluate_fn: Optional[Callable[[str], Any]] = None
    _initialized: bool = field(default=False, repr=False)
    _headless: bool = field(default=False, repr=False)

    def __post_init__(self):
        """Detect headless mode if no evaluate function provided."""
        self._headless = self.evaluate_fn is None

    def initialize(self) -> bool:
        """
        Initialize visual feedback by injecting CSS and creating overlay.

        Returns:
            True if initialized, False if headless/failed
        """
        if self._headless:
            return False

        try:
            # Inject CSS
            css_js = INJECT_CSS_JS % VALIDATION_CSS.replace('`', '\\`')
            self._evaluate(css_js)

            # Create overlay
            self._evaluate(CREATE_OVERLAY_JS)

            self._initialized = True
            return True
        except Exception:
            return False

    def highlight_element(self, ref: str, status: str, error_category: str = "") -> bool:
        """
        Highlight an element with validation status.

        Args:
            ref: Element reference (Playwright ref or identifier)
            status: "valid" or "invalid"
            error_category: Error category for invalid elements

        Returns:
            True if highlighted, False if headless/failed
        """
        if self._headless:
            return False

        is_valid = status.lower() == "valid"
        return self.highlight_valid(ref) if is_valid else self.highlight_invalid(ref, error_category)

    def highlight_valid(self, ref: str) -> bool:
        """
        Highlight an element as valid (green outline).

        Args:
            ref: Element reference

        Returns:
            True if highlighted, False if headless/failed
        """
        if self._headless:
            return False

        try:
            js = HIGHLIGHT_ELEMENT_JS % (
                self._escape_js(ref),
                "true",
                ""
            )
            result = self._evaluate(js)
            return result is True
        except Exception:
            return False

    def highlight_invalid(self, ref: str, error_category: str) -> bool:
        """
        Highlight an element as invalid (red outline with label).

        Args:
            ref: Element reference
            error_category: Error category to display

        Returns:
            True if highlighted, False if headless/failed
        """
        if self._headless:
            return False

        try:
            js = HIGHLIGHT_ELEMENT_JS % (
                self._escape_js(ref),
                "false",
                self._escape_js(error_category)
            )
            result = self._evaluate(js)
            return result is True
        except Exception:
            return False

    def show_pipeline_header(
        self,
        scope_result: Optional[Dict[str, Any]] = None,
        validation_results: Optional[Dict[str, Any]] = None,
        kb_status: str = "Ready"
    ) -> bool:
        """
        Display the 3-step pipeline status header.

        Shows:
            Step 1: ScopeDiscovery ......... [OK] Single Page (LoginPage)
            Step 2: RuntimeValidator ....... [OK] 4 Valid, 0 Errors
            Step 3: KnowledgeBase .......... [OK] Patterns Ready

        Args:
            scope_result: Result from ScopeDiscovery
            validation_results: Results from RuntimeValidator
            kb_status: Knowledge base status string

        Returns:
            True if displayed, False if headless/failed
        """
        if self._headless:
            return False

        if not self._initialized:
            self.initialize()

        try:
            # Step 1: ScopeDiscovery
            if scope_result:
                page_count = scope_result.get("page_count", 1)
                pages = scope_result.get("pages", [])
                page_names = ", ".join(p.get("name", "Unknown") for p in pages[:2])
                if page_count > 2:
                    page_names += f" +{page_count - 2} more"
                scope_type = "Single Page" if page_count == 1 else f"{page_count} Pages"
                scope_details = f"{scope_type} ({page_names})"
                self.update_step_status(1, "ScopeDiscovery", "OK", scope_details)
            else:
                self.update_step_status(1, "ScopeDiscovery", "PENDING", "Waiting...")

            # Step 2: RuntimeValidator
            if validation_results:
                valid_count = validation_results.get("valid_count", 0)
                error_count = validation_results.get("error_count", 0)
                self.update_step_status(
                    2, "RuntimeValidator", "OK",
                    f"{valid_count} Valid, {error_count} Errors"
                )
            else:
                self.update_step_status(2, "RuntimeValidator", "PENDING", "Waiting...")

            # Step 3: KnowledgeBase
            kb_state = "OK" if kb_status.lower() in ("ready", "patterns ready") else "PENDING"
            self.update_step_status(3, "KnowledgeBase", kb_state, kb_status)

            return True
        except Exception:
            return False

    def update_step_status(
        self,
        step: int,
        step_name: str,
        status: str,
        details: str
    ) -> bool:
        """
        Update individual pipeline step status.

        Args:
            step: Step number (1, 2, or 3)
            step_name: Step name (e.g., "ScopeDiscovery")
            status: "OK", "FAIL", or "PENDING"
            details: Status details

        Returns:
            True if updated, False if headless/failed
        """
        if self._headless:
            return False

        try:
            js = UPDATE_STEP_JS % (
                step,
                self._escape_js(step_name),
                self._escape_js(status),
                self._escape_js(details)
            )
            result = self._evaluate(js)
            return result is True
        except Exception:
            return False

    def show_results_panel(self, results: List[Dict[str, Any]]) -> bool:
        """
        Show element-by-element validation results.

        Args:
            results: List of validation results with:
                - element_name: str
                - ref: str
                - is_valid: bool
                - error_category: Optional[str]

        Returns:
            True if displayed, False if headless/failed
        """
        if self._headless:
            return False

        try:
            for result in results:
                js = ADD_RESULT_JS % (
                    self._escape_js(result.get("element_name", "Unknown")),
                    self._escape_js(result.get("ref", "?")),
                    "true" if result.get("is_valid", False) else "false",
                    self._escape_js(result.get("error_category", ""))
                )
                self._evaluate(js)
            return True
        except Exception:
            return False

    def add_result(
        self,
        element_name: str,
        ref: str,
        is_valid: bool,
        error_category: str = ""
    ) -> bool:
        """
        Add a single result to the results panel.

        Args:
            element_name: Element name/description
            ref: Element reference
            is_valid: Whether element is valid
            error_category: Error category if invalid

        Returns:
            True if added, False if headless/failed
        """
        if self._headless:
            return False

        try:
            js = ADD_RESULT_JS % (
                self._escape_js(element_name),
                self._escape_js(ref),
                "true" if is_valid else "false",
                self._escape_js(error_category)
            )
            result = self._evaluate(js)
            return result is True
        except Exception:
            return False

    def cleanup(self) -> bool:
        """
        Remove all injected visual elements.

        Returns:
            True if cleaned up, False if headless/failed
        """
        if self._headless:
            return False

        try:
            result = self._evaluate(CLEANUP_JS)
            self._initialized = False
            return result is True
        except Exception:
            return False

    @property
    def is_headless(self) -> bool:
        """Return True if running in headless mode (no browser)."""
        return self._headless

    @property
    def is_initialized(self) -> bool:
        """Return True if visual feedback is initialized."""
        return self._initialized

    def _evaluate(self, js: str) -> Any:
        """Execute JavaScript in browser."""
        if self.evaluate_fn:
            return self.evaluate_fn(js)
        return None

    @staticmethod
    def _escape_js(s: str) -> str:
        """Escape string for JavaScript."""
        if not s:
            return ""
        return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_visual_feedback(
    evaluate_fn: Optional[Callable[[str], Any]] = None
) -> VisualFeedback:
    """
    Create a VisualFeedback instance.

    Args:
        evaluate_fn: Function to evaluate JavaScript in browser
            (e.g., Playwright's browser_evaluate)

    Returns:
        VisualFeedback instance
    """
    return VisualFeedback(evaluate_fn=evaluate_fn)


def format_validation_summary(
    valid_count: int,
    error_count: int
) -> Dict[str, Any]:
    """
    Format validation counts for show_pipeline_header.

    Args:
        valid_count: Number of valid elements
        error_count: Number of invalid elements

    Returns:
        Dict suitable for validation_results parameter
    """
    return {
        "valid_count": valid_count,
        "error_count": error_count
    }


def format_scope_summary(
    page_count: int,
    page_names: List[str]
) -> Dict[str, Any]:
    """
    Format scope discovery for show_pipeline_header.

    Args:
        page_count: Number of pages in workflow
        page_names: List of page names

    Returns:
        Dict suitable for scope_result parameter
    """
    return {
        "page_count": page_count,
        "pages": [{"name": name} for name in page_names]
    }

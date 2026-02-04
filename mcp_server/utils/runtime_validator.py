"""
Runtime Validator - Task 3.0

Single Responsibility: "Is element usable? What's wrong?"

Validates element existence, visibility, and interactability at runtime.
Returns error category (NOT fix suggestion - that's fix_suggester's job).

Error Categories:
- LOCATOR_NOT_FOUND: Element not present in DOM
- NOT_VISIBLE: Element exists but hidden/zero-size
- NOT_INTERACTABLE: Element visible but disabled/covered
- STALE_REFERENCE: Element was valid but is now stale
- METHOD_NOT_FOUND: BrowserInterface method doesn't exist (different concern)

Design Notes:
- Uses Playwright MCP tools (browser_snapshot, browser_evaluate)
- Does NOT suggest fixes (SRP - fix_suggester does that)
- Returns structured ValidationResult for caller to handle

PRD Reference: enhanced-runtime-validation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from utils.visual_feedback import VisualFeedback


class ErrorCategory(Enum):
    """Error categories for element validation failures."""
    LOCATOR_NOT_FOUND = "LOCATOR_NOT_FOUND"
    NOT_VISIBLE = "NOT_VISIBLE"
    NOT_INTERACTABLE = "NOT_INTERACTABLE"
    STALE_REFERENCE = "STALE_REFERENCE"
    METHOD_NOT_FOUND = "METHOD_NOT_FOUND"


@dataclass
class ValidationResult:
    """
    Result of element validation.

    Attributes:
        is_valid: True if element is usable, False otherwise
        error_category: Category of error if validation failed, None if valid
        details: Additional context about the validation
            - locator: The locator that was validated
            - element_info: Info about found element (if any)
            - check_type: Type of check that failed
            - message: Human-readable description
    """
    is_valid: bool
    error_category: Optional[ErrorCategory] = None
    details: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def valid(cls, locator: str, element_info: Optional[Dict] = None) -> "ValidationResult":
        """Create a valid result."""
        return cls(
            is_valid=True,
            error_category=None,
            details={
                "locator": locator,
                "element_info": element_info or {},
                "message": "Element is valid and usable"
            }
        )

    @classmethod
    def invalid(
        cls,
        category: ErrorCategory,
        locator: str,
        message: str,
        **extra_details
    ) -> "ValidationResult":
        """Create an invalid result with error category."""
        return cls(
            is_valid=False,
            error_category=category,
            details={
                "locator": locator,
                "message": message,
                **extra_details
            }
        )


@dataclass
class ElementInfo:
    """Information about an element found in the page."""
    ref: str  # Playwright element reference
    role: Optional[str] = None
    name: Optional[str] = None
    visible: bool = True
    disabled: bool = False
    focused: bool = False

    @classmethod
    def from_snapshot_node(cls, node: Dict[str, Any]) -> "ElementInfo":
        """Create ElementInfo from a Playwright snapshot node."""
        return cls(
            ref=node.get("ref", ""),
            role=node.get("role"),
            name=node.get("name"),
            visible=not node.get("hidden", False),
            disabled=node.get("disabled", False),
            focused=node.get("focused", False)
        )


class RuntimeValidator:
    """
    Validates elements at runtime using Playwright browser tools.

    Single Responsibility: Answer "Is this element usable? If not, what's wrong?"

    Does NOT:
    - Suggest fixes (that's FixSuggester)
    - Apply fixes (that's AI orchestration)
    - Store history (that's AuditLogger)

    Usage:
        validator = RuntimeValidator(browser_snapshot_fn, browser_evaluate_fn)
        result = validator.validate_element("button[type='submit']")
        if not result.is_valid:
            print(f"Error: {result.error_category.value}")
    """

    def __init__(
        self,
        snapshot_fn: Optional[Callable[[], Dict[str, Any]]] = None,
        evaluate_fn: Optional[Callable[[str], Any]] = None,
        visual_feedback: Optional["VisualFeedback"] = None
    ):
        """
        Initialize RuntimeValidator with browser access functions.

        Args:
            snapshot_fn: Function that returns browser accessibility snapshot
            evaluate_fn: Function that evaluates JavaScript in browser
            visual_feedback: Optional VisualFeedback instance for automatic highlighting
        """
        self._snapshot_fn = snapshot_fn
        self._evaluate_fn = evaluate_fn
        self._visual_feedback = visual_feedback
        self._last_snapshot: Optional[Dict[str, Any]] = None

    def validate_element(
        self,
        locator: str,
        check_visibility: bool = True,
        check_interactable: bool = True
    ) -> ValidationResult:
        """
        Validate an element by locator.

        Args:
            locator: CSS selector, XPath, or ref to validate
            check_visibility: Whether to verify element is visible
            check_interactable: Whether to verify element is interactable

        Returns:
            ValidationResult with is_valid, error_category, and details
        """
        if not locator:
            return ValidationResult.invalid(
                ErrorCategory.LOCATOR_NOT_FOUND,
                locator="",
                message="Empty locator provided"
            )

        # Step 1: Check element exists
        existence_result = self._check_element_exists(locator)
        if not existence_result.is_valid:
            self._highlight_element(existence_result, {})
            return existence_result

        element_info = existence_result.details.get("element_info", {})

        # Step 2: Check visibility (if requested)
        if check_visibility:
            visibility_result = self._check_element_visible(locator, element_info)
            if not visibility_result.is_valid:
                self._highlight_element(visibility_result, element_info)
                return visibility_result

        # Step 3: Check interactability (if requested)
        if check_interactable:
            interactable_result = self._check_element_interactable(locator, element_info)
            if not interactable_result.is_valid:
                self._highlight_element(interactable_result, element_info)
                return interactable_result

        # All checks passed
        result = ValidationResult.valid(locator, element_info)

        # Trigger visual highlighting if enabled
        self._highlight_element(result, element_info)

        return result

    def validate_element_from_snapshot(
        self,
        snapshot: Dict[str, Any],
        locator: str,
        check_visibility: bool = True,
        check_interactable: bool = True
    ) -> ValidationResult:
        """
        Validate element using a pre-captured snapshot (for testing/efficiency).

        Args:
            snapshot: Playwright accessibility snapshot
            locator: Locator to find in snapshot
            check_visibility: Whether to verify visibility
            check_interactable: Whether to verify interactability

        Returns:
            ValidationResult
        """
        # Check for empty locator first
        if not locator:
            return ValidationResult.invalid(
                ErrorCategory.LOCATOR_NOT_FOUND,
                locator="",
                message="Empty locator provided"
            )

        self._last_snapshot = snapshot
        return self._validate_from_snapshot(
            snapshot, locator, check_visibility, check_interactable
        )

    def validate_method_exists(self, method_name: str) -> ValidationResult:
        """
        Check if a BrowserInterface method exists.

        Note: This is a placeholder. Actual implementation would use
        BrowserInterfaceChecker. Included here for interface completeness.

        Args:
            method_name: Name of BrowserInterface method

        Returns:
            ValidationResult with METHOD_NOT_FOUND if missing
        """
        # This will delegate to BrowserInterfaceChecker in integration
        # For now, return placeholder that indicates method check needed
        return ValidationResult.invalid(
            ErrorCategory.METHOD_NOT_FOUND,
            locator=f"method:{method_name}",
            message="Method existence check requires BrowserInterfaceChecker"
        )

    def get_last_snapshot(self) -> Optional[Dict[str, Any]]:
        """Return the last snapshot used for validation."""
        return self._last_snapshot

    # =========================================================================
    # PRIVATE VALIDATION METHODS
    # =========================================================================

    def _highlight_element(
        self,
        result: ValidationResult,
        element_info: Dict[str, Any]
    ) -> bool:
        """
        Highlight element based on validation result.

        Args:
            result: Validation result with is_valid and error_category
            element_info: Element info containing ref

        Returns:
            True if highlighted, False if no visual feedback configured
        """
        if not self._visual_feedback:
            return False

        # Get element ref from element_info or result details
        ref = element_info.get("ref", "") or result.details.get("locator", "")
        if not ref:
            return False

        try:
            if result.is_valid:
                return self._visual_feedback.highlight_valid(ref)
            else:
                error_category = result.error_category.value if result.error_category else "UNKNOWN"
                return self._visual_feedback.highlight_invalid(ref, error_category)
        except Exception:
            return False

    def _check_element_exists(self, locator: str) -> ValidationResult:
        """Check if element exists in the page."""
        # Try to get fresh snapshot
        snapshot = self._get_snapshot()
        if snapshot is None:
            return ValidationResult.invalid(
                ErrorCategory.LOCATOR_NOT_FOUND,
                locator=locator,
                message="Could not get page snapshot",
                check_type="existence"
            )

        # Search for element in snapshot
        element = self._find_element_in_snapshot(snapshot, locator)
        if element is None:
            return ValidationResult.invalid(
                ErrorCategory.LOCATOR_NOT_FOUND,
                locator=locator,
                message=f"Element not found with locator: {locator}",
                check_type="existence"
            )

        return ValidationResult.valid(locator, element)

    def _check_element_visible(
        self,
        locator: str,
        element_info: Dict[str, Any]
    ) -> ValidationResult:
        """Check if element is visible."""
        # Check visibility from element info
        if element_info.get("hidden", False):
            return ValidationResult.invalid(
                ErrorCategory.NOT_VISIBLE,
                locator=locator,
                message="Element is hidden",
                check_type="visibility",
                element_info=element_info
            )

        # Additional JS check if evaluate function available
        if self._evaluate_fn:
            try:
                is_visible = self._evaluate_fn(
                    f"(() => {{ "
                    f"const el = document.querySelector('{self._escape_selector(locator)}'); "
                    f"if (!el) return false; "
                    f"const rect = el.getBoundingClientRect(); "
                    f"return rect.width > 0 && rect.height > 0; "
                    f"}})()"
                )
                if is_visible is False:
                    return ValidationResult.invalid(
                        ErrorCategory.NOT_VISIBLE,
                        locator=locator,
                        message="Element has zero dimensions",
                        check_type="visibility",
                        element_info=element_info
                    )
            except Exception:
                # Evaluation failed, trust snapshot info
                pass

        return ValidationResult.valid(locator, element_info)

    def _check_element_interactable(
        self,
        locator: str,
        element_info: Dict[str, Any]
    ) -> ValidationResult:
        """Check if element is interactable (not disabled, not covered)."""
        # Check disabled state
        if element_info.get("disabled", False):
            return ValidationResult.invalid(
                ErrorCategory.NOT_INTERACTABLE,
                locator=locator,
                message="Element is disabled",
                check_type="interactability",
                element_info=element_info
            )

        # Additional JS check for pointer events and coverage
        if self._evaluate_fn:
            try:
                is_interactable = self._evaluate_fn(
                    f"(() => {{ "
                    f"const el = document.querySelector('{self._escape_selector(locator)}'); "
                    f"if (!el) return false; "
                    f"const style = window.getComputedStyle(el); "
                    f"return style.pointerEvents !== 'none' && !el.disabled; "
                    f"}})()"
                )
                if is_interactable is False:
                    return ValidationResult.invalid(
                        ErrorCategory.NOT_INTERACTABLE,
                        locator=locator,
                        message="Element has pointer-events:none or is disabled",
                        check_type="interactability",
                        element_info=element_info
                    )
            except Exception:
                # Evaluation failed, trust snapshot info
                pass

        return ValidationResult.valid(locator, element_info)

    def _validate_from_snapshot(
        self,
        snapshot: Dict[str, Any],
        locator: str,
        check_visibility: bool,
        check_interactable: bool
    ) -> ValidationResult:
        """Validate element from a provided snapshot."""
        # Find element in snapshot
        element = self._find_element_in_snapshot(snapshot, locator)
        if element is None:
            return ValidationResult.invalid(
                ErrorCategory.LOCATOR_NOT_FOUND,
                locator=locator,
                message=f"Element not found in snapshot: {locator}"
            )

        # Check visibility
        if check_visibility:
            if element.get("hidden", False):
                return ValidationResult.invalid(
                    ErrorCategory.NOT_VISIBLE,
                    locator=locator,
                    message="Element is hidden in snapshot",
                    element_info=element
                )

        # Check interactability
        if check_interactable:
            if element.get("disabled", False):
                return ValidationResult.invalid(
                    ErrorCategory.NOT_INTERACTABLE,
                    locator=locator,
                    message="Element is disabled in snapshot",
                    element_info=element
                )

        return ValidationResult.valid(locator, element)

    def _get_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get current page snapshot."""
        if self._snapshot_fn:
            try:
                self._last_snapshot = self._snapshot_fn()
                return self._last_snapshot
            except Exception:
                return None
        return self._last_snapshot

    def _find_element_in_snapshot(
        self,
        snapshot: Dict[str, Any],
        locator: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find element in Playwright accessibility snapshot.

        The snapshot structure varies, but typically has a tree of nodes.
        We search by ref or name matching the locator pattern.
        """
        if not snapshot:
            return None

        # Handle different snapshot formats
        nodes = self._extract_nodes(snapshot)

        for node in nodes:
            if self._node_matches_locator(node, locator):
                return node

        return None

    def _extract_nodes(self, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recursively extract all nodes from snapshot tree."""
        nodes = []

        # Add root if it has relevant info
        if "role" in snapshot or "name" in snapshot or "ref" in snapshot:
            nodes.append(snapshot)

        # Recursively process children
        children = snapshot.get("children", [])
        for child in children:
            if isinstance(child, dict):
                nodes.extend(self._extract_nodes(child))

        return nodes

    def _node_matches_locator(self, node: Dict[str, Any], locator: str) -> bool:
        """
        Check if a snapshot node matches the given locator.

        Matching strategies:
        1. Exact ref match (e.g., "S1.B2" matches ref="S1.B2")
        2. Name contains (e.g., "Sign in" matches name="Sign in to your account")
        3. Role + name combo (e.g., "button:Submit" matches role=button, name=Submit)
        """
        node_ref = node.get("ref", "")
        node_name = node.get("name", "")
        node_role = node.get("role", "")

        # Strategy 1: Exact ref match
        if locator == node_ref:
            return True

        # Strategy 2: Name contains (case-insensitive)
        if node_name and locator.lower() in node_name.lower():
            return True

        # Strategy 3: Role:name pattern
        if ":" in locator:
            parts = locator.split(":", 1)
            if len(parts) == 2:
                search_role, search_name = parts
                if (search_role.lower() == node_role.lower() and
                    search_name.lower() in node_name.lower()):
                    return True

        # Strategy 4: Check if locator looks like CSS selector
        # and name/role contain relevant parts
        if locator.startswith("#") or locator.startswith("."):
            # ID or class selector - check name
            selector_text = locator.lstrip("#.")
            if selector_text.lower() in node_name.lower():
                return True

        return False

    @staticmethod
    def _escape_selector(selector: str) -> str:
        """Escape selector for use in JavaScript."""
        return selector.replace("'", "\\'").replace('"', '\\"')


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def validate_element(
    locator: str,
    snapshot: Optional[Dict[str, Any]] = None,
    snapshot_fn: Optional[Callable[[], Dict[str, Any]]] = None
) -> ValidationResult:
    """
    Convenience function to validate an element.

    Args:
        locator: Locator to validate
        snapshot: Pre-captured snapshot (optional)
        snapshot_fn: Function to get snapshot (optional)

    Returns:
        ValidationResult
    """
    validator = RuntimeValidator(snapshot_fn=snapshot_fn)
    if snapshot:
        return validator.validate_element_from_snapshot(snapshot, locator)
    return validator.validate_element(locator)


def validate_elements(
    locators: List[str],
    snapshot: Optional[Dict[str, Any]] = None,
    snapshot_fn: Optional[Callable[[], Dict[str, Any]]] = None
) -> Dict[str, ValidationResult]:
    """
    Validate multiple elements.

    Args:
        locators: List of locators to validate
        snapshot: Pre-captured snapshot (optional)
        snapshot_fn: Function to get snapshot (optional)

    Returns:
        Dict mapping locator -> ValidationResult
    """
    validator = RuntimeValidator(snapshot_fn=snapshot_fn)
    results = {}

    for locator in locators:
        if snapshot:
            results[locator] = validator.validate_element_from_snapshot(
                snapshot, locator
            )
        else:
            results[locator] = validator.validate_element(locator)

    return results

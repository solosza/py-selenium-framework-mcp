"""
Quality Gate: Discovery Complete Checkpoint (Between Steps 5 and 6).

NEW gate for DEF-045 - Two-Pass Discovery validation checkpoint.

Purpose:
Validates that ALL pages in scope have BOTH input and output elements
discovered before allowing POM generation (Step 6) to proceed.

This checkpoint ensures AI has observed:
- Input elements (forms, buttons) → PASS 1
- Output elements (confirmations, messages) → PASS 2

...for EVERY page in the workflow scope.

PRE-only gate (no POST validation - this is a checkpoint, not a tool wrapper).

Enforces: DEF-045 (two-pass discovery), DD-44 (multi-page discovery)
"""

from typing import Any, Dict

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGDiscoveryComplete(BaseGate):
    """Quality gate checkpoint: Verify all pages have input AND output elements."""

    @classmethod
    def _get_state_manager(cls) -> StateManager:
        """Get StateManager instance. Extracted for testing."""
        # Task 14.0: Use per-run state isolation
        audit_logger = cls.get_audit_logger()
        return StateManager(run_id=audit_logger.run_id)

    @classmethod
    def validate_pre(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PRE validation checkpoint - verify discovery is complete.

        Validates:
        - Step 5 is complete
        - All pages in discovered_pages have BOTH input_elements AND output_elements
        - For single-page: At least one page with both types
        - For multi-page: ALL pages must have both types

        Args:
            input_data: Dict (can be empty - reads from state)

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
        """
        # Check Step 5 completion
        state_manager = cls._get_state_manager()
        if not state_manager.is_step_complete(5):
            return cls.fail_response(
                error="Step 5 is not complete. Cannot validate discovery checkpoint.",
                fix_hint="Complete Step 5 (Discover Elements) first. Run two-pass discovery for all pages in scope."
            )

        # Get Step 5 state
        step_5_state = state_manager.get_step(5) or {}
        discovered_pages = step_5_state.get("discovered_pages", {})

        # Guard against corrupted state (from mixed workflows or old format)
        if not isinstance(discovered_pages, dict):
            return cls.fail_response(
                error="State corruption detected: discovered_pages is not a dict.",
                fix_hint="Clear state and restart workflow from Step 1. Run: StateManager().clear()"
            )

        # Validate discovered_pages exists and is not empty
        if not discovered_pages:
            return cls.fail_response(
                error="No pages discovered in Step 5. discovered_pages is empty.",
                fix_hint="Run Step 5 discovery loop (PASS 1: input elements, PASS 2: output elements) for at least one page."
            )

        # Validate each page has BOTH input_elements AND output_elements
        incomplete_pages = []
        complete_pages = []

        for page_name, page_data in discovered_pages.items():
            # Check if page_data is the new nested structure
            if isinstance(page_data, dict):
                has_input = bool(page_data.get("input_elements"))
                has_output = bool(page_data.get("output_elements"))

                if has_input and has_output:
                    complete_pages.append(page_name)
                else:
                    # Determine what's missing
                    missing = []
                    if not has_input:
                        missing.append("input")
                    if not has_output:
                        missing.append("output")
                    incomplete_pages.append(f"{page_name} (missing: {', '.join(missing)})")
            else:
                # Old flat structure (backward compat) - assume it's input elements only
                incomplete_pages.append(f"{page_name} (missing: output)")

        # Check if discovery is complete
        total_pages = len(discovered_pages)
        pages_discovered = len(complete_pages)

        if incomplete_pages:
            # Discovery incomplete - some pages missing input or output
            missing_details = "\n  - ".join(incomplete_pages)

            return cls.fail_response(
                error=f"Discovery incomplete: {pages_discovered}/{total_pages} pages have both input and output elements.",
                fix_hint=f"Complete two-pass discovery for all pages:\n  - {missing_details}\n\nRun PASS 1 (input) and PASS 2 (output) for each page before proceeding to Step 6."
            )

        # All pages complete - success!
        return cls.pass_response()

    @classmethod
    def validate_post(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST validation not applicable for checkpoint gates.

        This is a PRE-only checkpoint (validates state before Step 6).
        No POST validation needed.
        """
        return cls.pass_response()

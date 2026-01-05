"""
Integration Tests - Runtime Validation Pipeline

Tests the integration between:
- Task 1.0: ScopeDiscovery (analyze BDD scenarios)
- Task 2.0: qg_discovered_elements (per-page tracking)
- Task 3.0: RuntimeValidator (element validation)
- Task 4.0: KnowledgeBase (pattern lookup)

These tests verify the modules work together as a pipeline.
"""

import pytest
import tempfile
import os
from pathlib import Path

# Import all modules we're integrating
from mcp_server.utils.scope_discovery import ScopeDiscovery, ScopeResult
from mcp_server.utils.runtime_validator import (
    RuntimeValidator, ValidationResult, ErrorCategory
)
from mcp_server.utils.knowledge_base import KnowledgeBase, Pattern


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_bdd_scenarios():
    """BDD scenarios for a login workflow."""
    return [
        {
            "name": "test_valid_login",
            "given": "I am on the login page",
            "when": "I enter valid credentials and click submit",
            "then": "I should see my account dashboard"
        },
        {
            "name": "test_invalid_login",
            "given": "I am on the login page",
            "when": "I enter invalid credentials and click submit",
            "then": "I should see an error message on the login page"
        }
    ]


@pytest.fixture
def multi_page_bdd_scenarios():
    """BDD scenarios for a multi-page checkout workflow."""
    return [
        {
            "name": "test_complete_checkout",
            "given": "I am on the cart page with items",
            "when": "I proceed to checkout, fill shipping info, and confirm payment",
            "then": "I should see the order confirmation page"
        }
    ]


@pytest.fixture
def sample_snapshot_valid():
    """A snapshot with valid, usable elements."""
    return {
        "role": "WebArea",
        "name": "Login Page",
        "children": [
            {
                "role": "textbox",
                "name": "Email",
                "ref": "S1.T1",
                "hidden": False,
                "disabled": False
            },
            {
                "role": "textbox",
                "name": "Password",
                "ref": "S1.T2",
                "hidden": False,
                "disabled": False
            },
            {
                "role": "button",
                "name": "Sign in",
                "ref": "S1.B1",
                "hidden": False,
                "disabled": False
            }
        ]
    }


@pytest.fixture
def sample_snapshot_with_errors():
    """A snapshot with problematic elements."""
    return {
        "role": "WebArea",
        "name": "Problem Page",
        "children": [
            {
                "role": "button",
                "name": "Submit",
                "ref": "S1.B1",
                "hidden": True,  # NOT_VISIBLE
                "disabled": False
            },
            {
                "role": "button",
                "name": "Disabled Action",
                "ref": "S1.B2",
                "hidden": False,
                "disabled": True  # NOT_INTERACTABLE
            }
        ]
    }


@pytest.fixture
def temp_kb_file():
    """Create a temporary KB file with patterns."""
    content = """# Knowledge Base

## Runtime Validation Patterns

### PATTERN: NOT_INTERACTABLE - Disabled element

**Context:** symptom=disabled
**Fix:** Wait for element to become enabled or check preconditions
**Confidence:** 0.85

---

### PATTERN: NOT_VISIBLE - Hidden element

**Context:** symptom=hidden
**Fix:** Scroll element into view or wait for visibility
**Confidence:** 0.9

---

### PATTERN: LOCATOR_NOT_FOUND - Element missing

**Context:** symptom=missing
**Fix:** Verify page is fully loaded, check selector accuracy
**Confidence:** 0.8

---

## Specific Patterns

### Pointer Events Interception

When elements intercept pointer events...
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


# =============================================================================
# INTEGRATION TEST: Scope Discovery → Element Validation
# =============================================================================

class TestScopeToValidationIntegration:
    """Test scope discovery feeding into element validation."""

    def test_single_page_scope_then_validate_elements(
        self, sample_bdd_scenarios, sample_snapshot_valid
    ):
        """
        Integration: Analyze scope → Validate elements on that page.

        Flow:
        1. ScopeDiscovery analyzes BDD → determines page list
        2. RuntimeValidator validates elements on each page
        """
        # Step 1: Scope Discovery
        scope = ScopeDiscovery()
        result = scope.analyze_workflow(sample_bdd_scenarios)

        # Verify scope analysis
        assert result.is_single_page is True
        # Page name might be "LoginPage" or contain "login"
        page_names_lower = [p.name.lower() for p in result.pages]
        assert any("login" in name for name in page_names_lower)

        # Step 2: For each page in scope, validate elements
        validator = RuntimeValidator()

        # Validate elements from snapshot
        email_result = validator.validate_element_from_snapshot(
            sample_snapshot_valid, "Email"
        )
        password_result = validator.validate_element_from_snapshot(
            sample_snapshot_valid, "Password"
        )
        submit_result = validator.validate_element_from_snapshot(
            sample_snapshot_valid, "Sign in"
        )

        # All should be valid
        assert email_result.is_valid is True
        assert password_result.is_valid is True
        assert submit_result.is_valid is True

    def test_multi_page_scope_identifies_pages(self, multi_page_bdd_scenarios):
        """
        Integration: Multi-page workflow scope analysis.

        Verifies ScopeDiscovery correctly identifies multiple pages
        that will need separate element discovery passes.
        """
        scope = ScopeDiscovery()
        result = scope.analyze_workflow(multi_page_bdd_scenarios)

        # Should detect multiple pages
        assert result.is_multi_page is True
        assert result.page_count >= 2

        # Should identify cart, checkout, confirmation pages
        page_names_lower = [p.name.lower() for p in result.pages]
        assert any("cart" in name for name in page_names_lower)


# =============================================================================
# INTEGRATION TEST: Validation Error → Knowledge Base Lookup
# =============================================================================

class TestValidationToKnowledgeBaseIntegration:
    """Test validation errors feeding into KB pattern lookup."""

    def test_validation_error_finds_kb_pattern(
        self, sample_snapshot_with_errors, temp_kb_file
    ):
        """
        Integration: Validate element → Get error → Find KB pattern.

        Flow:
        1. RuntimeValidator finds NOT_VISIBLE error
        2. KnowledgeBase.find_pattern() finds matching fix
        """
        # Step 1: Validate element that has error
        validator = RuntimeValidator()
        result = validator.validate_element_from_snapshot(
            sample_snapshot_with_errors, "Submit"
        )

        # Should be invalid with NOT_VISIBLE
        assert result.is_valid is False
        assert result.error_category == ErrorCategory.NOT_VISIBLE

        # Step 2: Look up pattern in KB
        kb = KnowledgeBase(kb_path=temp_kb_file)
        pattern = kb.find_pattern(
            error_category=result.error_category.value,
            context={"symptom": "hidden"}
        )

        # Should find a pattern
        assert pattern is not None
        assert "scroll" in pattern.fix.lower() or "visibility" in pattern.fix.lower()
        assert pattern.confidence >= 0.8

    def test_disabled_element_finds_interactable_pattern(
        self, sample_snapshot_with_errors, temp_kb_file
    ):
        """
        Integration: Disabled element → NOT_INTERACTABLE → KB pattern.
        """
        # Step 1: Validate disabled element
        validator = RuntimeValidator()
        result = validator.validate_element_from_snapshot(
            sample_snapshot_with_errors, "Disabled Action"
        )

        # Should be NOT_INTERACTABLE
        assert result.is_valid is False
        assert result.error_category == ErrorCategory.NOT_INTERACTABLE

        # Step 2: Look up pattern
        kb = KnowledgeBase(kb_path=temp_kb_file)
        pattern = kb.find_pattern(
            error_category=result.error_category.value,
            context={"symptom": "disabled"}
        )

        # Should find pattern
        assert pattern is not None
        assert pattern.error_category == "NOT_INTERACTABLE"

    def test_no_pattern_returns_none(self, temp_kb_file):
        """
        Integration: When no KB pattern exists, returns None.

        This is the expected behavior - caller (AI) decides what to do.
        """
        kb = KnowledgeBase(kb_path=temp_kb_file)

        # Look for a pattern that doesn't exist
        pattern = kb.find_pattern(
            error_category="SOME_UNKNOWN_ERROR",
            context={"weird": "context"}
        )

        # Should return None, not raise exception
        assert pattern is None


# =============================================================================
# INTEGRATION TEST: Full Pipeline
# =============================================================================

class TestFullPipelineIntegration:
    """Test the complete pipeline: Scope → Validate → KB Lookup."""

    def test_full_validation_pipeline_success(
        self, sample_bdd_scenarios, sample_snapshot_valid, temp_kb_file
    ):
        """
        Full pipeline test: BDD → Scope → Validate → No KB needed (success).
        """
        # Step 1: Analyze scope
        scope = ScopeDiscovery()
        scope_result = scope.analyze_workflow(sample_bdd_scenarios)

        assert scope_result.page_count >= 1

        # Step 2: Validate all elements
        validator = RuntimeValidator()
        elements_to_check = ["Email", "Password", "Sign in"]
        validation_results = {}

        for element in elements_to_check:
            validation_results[element] = validator.validate_element_from_snapshot(
                sample_snapshot_valid, element
            )

        # Step 3: Check results - all should pass
        all_valid = all(r.is_valid for r in validation_results.values())
        assert all_valid is True

        # No need to query KB since all passed
        errors = [r for r in validation_results.values() if not r.is_valid]
        assert len(errors) == 0

    def test_full_validation_pipeline_with_error_and_fix(
        self, sample_bdd_scenarios, sample_snapshot_with_errors, temp_kb_file
    ):
        """
        Full pipeline test: BDD → Scope → Validate → Error → KB Fix.
        """
        # Step 1: Analyze scope
        scope = ScopeDiscovery()
        scope_result = scope.analyze_workflow(sample_bdd_scenarios)

        # Step 2: Validate elements (some will fail)
        validator = RuntimeValidator()
        kb = KnowledgeBase(kb_path=temp_kb_file)

        elements_to_check = ["Submit", "Disabled Action"]
        pipeline_results = []

        for element in elements_to_check:
            validation = validator.validate_element_from_snapshot(
                sample_snapshot_with_errors, element
            )

            if not validation.is_valid:
                # Step 3: Look up fix in KB
                pattern = kb.find_pattern(
                    error_category=validation.error_category.value
                )

                pipeline_results.append({
                    "element": element,
                    "error_category": validation.error_category.value,
                    "fix_found": pattern is not None,
                    "suggested_fix": pattern.fix if pattern else None
                })

        # Verify pipeline produced actionable results
        assert len(pipeline_results) == 2

        # Both errors should have fixes available
        for result in pipeline_results:
            assert result["fix_found"] is True
            assert result["suggested_fix"] is not None


# =============================================================================
# INTEGRATION TEST: Pattern Saving Workflow
# =============================================================================

class TestPatternSavingIntegration:
    """Test discovering new patterns and saving to KB."""

    def test_new_pattern_saved_and_retrievable(self):
        """
        Integration: Create new pattern → Save to KB → Retrieve later.

        This simulates: User provides fix → AI saves to KB → Future lookups work.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Knowledge Base\n\n## Runtime Validation Patterns\n\n")
            temp_path = f.name

        try:
            # Step 1: Create KB with no patterns for our error
            kb = KnowledgeBase(kb_path=temp_path)

            # Verify no pattern exists yet
            existing = kb.find_pattern("STALE_REFERENCE")
            assert existing is None

            # Step 2: "User" provides a fix - save it
            new_pattern = Pattern(
                error_category="STALE_REFERENCE",
                context_match={"symptom": "element detached"},
                fix="Re-find element after DOM mutation",
                confidence=0.85,
                source="user_provided"
            )
            kb.save_pattern(new_pattern)

            # Step 3: Reload KB and verify pattern is retrievable
            kb_reloaded = KnowledgeBase(kb_path=temp_path)
            found = kb_reloaded.find_pattern("STALE_REFERENCE")

            assert found is not None
            assert found.fix == "Re-find element after DOM mutation"
            assert found.confidence == 0.85

        finally:
            os.unlink(temp_path)


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

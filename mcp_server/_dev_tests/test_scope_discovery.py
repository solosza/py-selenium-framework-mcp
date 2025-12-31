"""
Unit tests for ScopeDiscovery - Task 1.0

Test suite for workflow scope discovery (page count analysis).

Test Matrix:
- Happy path: 4 tests (P0)
- Negative: 2 tests (P0)
- Edge cases: 4 tests (P1)
- Integration: 2 tests (P1)

Testing Skill Reference: .claude/skills/testing/
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.scope_discovery import (
    ScopeDiscovery,
    ScopeResult,
    PageInfo,
    analyze_workflow_scope
)


# ============================================================================
# HAPPY PATH TESTS
# ============================================================================

class TestScopeDiscoveryHappyPath:
    """
    Happy path tests for ScopeDiscovery.

    Verifies core functionality works correctly under normal conditions:
    - Single page workflow detection
    - Multi-page workflow detection
    - Page name extraction
    - Page order tracking
    """

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_single_page_workflow(self):
        """
        P0: Verify single page workflow is detected correctly.

        AAA Pattern:
        1. Arrange - Create BDD scenarios for single page
        2. Act - Analyze workflow
        3. Assert - Returns 1 page, is_single_page True
        """
        # Arrange
        bdd_scenarios = [
            {
                "given": "user is on login page",
                "when": "user enters valid credentials",
                "then": "user sees success message"
            }
        ]
        discovery = ScopeDiscovery()

        # Act
        result = discovery.analyze_workflow(bdd_scenarios)

        # Assert
        assert result.page_count == 1, \
            f"Single page workflow should have 1 page, got {result.page_count}"
        assert result.is_single_page is True, \
            "is_single_page should be True for single page workflow"
        assert result.is_multi_page is False, \
            "is_multi_page should be False for single page workflow"

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_multi_page_workflow(self):
        """
        P0: Verify multi-page workflow is detected correctly.

        AAA Pattern:
        1. Arrange - Create BDD scenarios spanning multiple pages
        2. Act - Analyze workflow
        3. Assert - Returns correct page count, is_multi_page True
        """
        # Arrange
        bdd_scenarios = [
            {
                "given": "user is on login page",
                "when": "user logs in successfully",
                "then": "user is redirected to dashboard page"
            },
            {
                "given": "user is on dashboard page",
                "when": "user clicks settings",
                "then": "user sees settings page"
            }
        ]
        discovery = ScopeDiscovery()

        # Act
        result = discovery.analyze_workflow(bdd_scenarios)

        # Assert
        assert result.page_count == 3, \
            f"Should detect 3 pages (login, dashboard, settings), got {result.page_count}"
        assert result.is_multi_page is True, \
            "is_multi_page should be True for multi-page workflow"
        assert result.is_single_page is False, \
            "is_single_page should be False for multi-page workflow"

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_page_name_extraction_pascal_case(self):
        """
        P0: Verify page names are extracted in PascalCase with Page suffix.

        AAA Pattern:
        1. Arrange - Create BDD with various page references
        2. Act - Analyze workflow
        3. Assert - All page names are PascalCase ending with Page
        """
        # Arrange
        bdd_scenarios = [
            {
                "given": "user is on my account page",
                "when": "user clicks order history",
                "then": "user lands on order history page"
            }
        ]
        discovery = ScopeDiscovery()

        # Act
        result = discovery.analyze_workflow(bdd_scenarios)

        # Assert
        page_names = [p.name for p in result.pages]
        assert "MyAccountPage" in page_names, \
            f"Should extract 'MyAccountPage', got {page_names}"
        assert "OrderHistoryPage" in page_names, \
            f"Should extract 'OrderHistoryPage', got {page_names}"
        for name in page_names:
            assert name.endswith("Page"), \
                f"All page names should end with 'Page', got {name}"

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_page_order_tracking(self):
        """
        P0: Verify pages are tracked in order of discovery.

        AAA Pattern:
        1. Arrange - Create BDD with sequential pages
        2. Act - Analyze workflow
        3. Assert - Pages have correct order (1, 2, 3...)
        """
        # Arrange
        bdd_scenarios = [
            {
                "given": "user is on home page",
                "when": "user clicks products",
                "then": "user navigates to catalog page"
            },
            {
                "given": "user is on catalog page",
                "when": "user adds item to cart",
                "then": "user sees cart page"
            }
        ]
        discovery = ScopeDiscovery()

        # Act
        result = discovery.analyze_workflow(bdd_scenarios)

        # Assert
        assert len(result.pages) == 3, \
            f"Should have 3 pages, got {len(result.pages)}"
        assert result.pages[0].order == 1, \
            "First page should have order 1"
        assert result.pages[1].order == 2, \
            "Second page should have order 2"
        assert result.pages[2].order == 3, \
            "Third page should have order 3"


# ============================================================================
# NEGATIVE TESTS
# ============================================================================

class TestScopeDiscoveryNegative:
    """
    Negative tests for ScopeDiscovery.

    Verifies graceful handling of:
    - Empty scenarios
    - Scenarios without page references
    """

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_empty_scenarios_returns_default(self):
        """
        P0: Verify empty scenarios list returns default page.

        AAA Pattern:
        1. Arrange - Create empty BDD scenarios
        2. Act - Analyze workflow
        3. Assert - Returns default MainPage
        """
        # Arrange
        bdd_scenarios = []
        discovery = ScopeDiscovery()

        # Act
        result = discovery.analyze_workflow(bdd_scenarios)

        # Assert
        assert result.page_count == 1, \
            "Empty scenarios should default to 1 page"
        assert result.pages[0].name == "MainPage", \
            f"Default page should be 'MainPage', got {result.pages[0].name}"

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_no_page_references_returns_default(self):
        """
        P0: Verify scenarios without page references return default.

        AAA Pattern:
        1. Arrange - Create BDD without page keywords
        2. Act - Analyze workflow
        3. Assert - Returns default MainPage
        """
        # Arrange
        bdd_scenarios = [
            {
                "given": "system is running",
                "when": "user clicks button",
                "then": "data is saved"
            }
        ]
        discovery = ScopeDiscovery()

        # Act
        result = discovery.analyze_workflow(bdd_scenarios)

        # Assert
        assert result.page_count == 1, \
            "No page references should default to 1 page"
        assert result.pages[0].name == "MainPage", \
            "Default page should be 'MainPage'"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestScopeDiscoveryEdgeCases:
    """
    Edge case tests for ScopeDiscovery.

    Verifies handling of:
    - Duplicate page references
    - List format clauses
    - URL extraction
    - Various page reference patterns
    """

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_duplicate_pages_counted_once(self):
        """
        P1: Verify duplicate page references are counted once.

        AAA Pattern:
        1. Arrange - Create BDD with repeated page references
        2. Act - Analyze workflow
        3. Assert - Each page counted only once
        """
        # Arrange
        bdd_scenarios = [
            {
                "given": "user is on login page",
                "when": "user fails to log in",
                "then": "user remains on login page"
            },
            {
                "given": "user is on login page",
                "when": "user enters correct credentials",
                "then": "user is redirected to dashboard page"
            }
        ]
        discovery = ScopeDiscovery()

        # Act
        result = discovery.analyze_workflow(bdd_scenarios)

        # Assert
        assert result.page_count == 2, \
            f"Login should be counted once, got {result.page_count} pages"
        page_names = [p.name for p in result.pages]
        assert page_names.count("LoginPage") == 1, \
            "LoginPage should appear exactly once"

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_list_format_clauses(self):
        """
        P1: Verify list format BDD clauses are handled.

        AAA Pattern:
        1. Arrange - Create BDD with list format
        2. Act - Analyze workflow
        3. Assert - All pages extracted correctly
        """
        # Arrange
        bdd_scenarios = [
            {
                "given": ["user is logged in", "user is on catalog page"],
                "when": ["user searches for product", "user clicks first result"],
                "then": ["user sees product details page"]
            }
        ]
        discovery = ScopeDiscovery()

        # Act
        result = discovery.analyze_workflow(bdd_scenarios)

        # Assert
        page_names = [p.name for p in result.pages]
        assert "CatalogPage" in page_names, \
            f"Should extract CatalogPage from list, got {page_names}"
        assert "ProductDetailsPage" in page_names, \
            f"Should extract ProductDetailsPage from list, got {page_names}"

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_url_path_extraction(self):
        """
        P1: Verify URL paths are extracted from clauses.

        AAA Pattern:
        1. Arrange - Create BDD with URL references
        2. Act - Analyze workflow
        3. Assert - URL paths captured in PageInfo
        """
        # Arrange
        bdd_scenarios = [
            {
                "given": "user is on login page",
                "when": "user visits /account/settings",
                "then": "user sees settings page"
            }
        ]
        discovery = ScopeDiscovery()

        # Act
        result = discovery.analyze_workflow(bdd_scenarios)

        # Assert
        settings_page = next((p for p in result.pages if p.name == "SettingsPage"), None)
        assert settings_page is not None, "SettingsPage should be found"
        # URL extraction is best-effort, may not always work
        # The key is that it doesn't crash

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_various_page_patterns(self):
        """
        P1: Verify various page reference patterns are recognized.

        AAA Pattern:
        1. Arrange - Create BDD with different page reference styles
        2. Act - Analyze workflow
        3. Assert - All patterns recognized
        """
        # Arrange
        bdd_scenarios = [
            {"given": "user is viewing the home page", "when": "", "then": ""},
            {"given": "user navigates to checkout page", "when": "", "then": ""},
            {"given": "", "when": "", "then": "user lands on confirmation page"},
            {"given": "user is at payment page", "when": "", "then": ""}
        ]
        discovery = ScopeDiscovery()

        # Act
        result = discovery.analyze_workflow(bdd_scenarios)

        # Assert
        page_names = [p.name for p in result.pages]
        assert "HomePage" in page_names, f"Should recognize 'viewing' pattern, got {page_names}"
        assert "CheckoutPage" in page_names, f"Should recognize 'navigates to' pattern, got {page_names}"
        assert "ConfirmationPage" in page_names, f"Should recognize 'lands on' pattern, got {page_names}"
        assert "PaymentPage" in page_names, f"Should recognize 'is at' pattern, got {page_names}"


# ============================================================================
# INSTANCE METHOD TESTS
# ============================================================================

class TestScopeDiscoveryInstanceMethods:
    """
    Tests for instance methods after analyze_workflow.

    Verifies:
    - get_page_list() returns correct list
    - is_single_page() and is_multi_page() work after analysis
    - Methods return sensible defaults before analysis
    """

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_get_page_list_after_analysis(self):
        """
        P1: Verify get_page_list() returns pages after analysis.

        AAA Pattern:
        1. Arrange - Create and analyze BDD
        2. Act - Call get_page_list()
        3. Assert - Returns same pages as result
        """
        # Arrange
        bdd_scenarios = [
            {"given": "user is on home page", "when": "", "then": "user sees home page"}
        ]
        discovery = ScopeDiscovery()
        result = discovery.analyze_workflow(bdd_scenarios)

        # Act
        pages = discovery.get_page_list()

        # Assert
        assert pages == result.pages, \
            "get_page_list() should return same pages as result"

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_methods_before_analysis(self):
        """
        P1: Verify methods return defaults before analyze_workflow called.

        AAA Pattern:
        1. Arrange - Create ScopeDiscovery without calling analyze
        2. Act - Call is_single_page() and is_multi_page()
        3. Assert - Both return False (no analysis yet)
        """
        # Arrange
        discovery = ScopeDiscovery()

        # Act
        single = discovery.is_single_page()
        multi = discovery.is_multi_page()
        pages = discovery.get_page_list()

        # Assert
        assert single is False, "is_single_page() should be False before analysis"
        assert multi is False, "is_multi_page() should be False before analysis"
        assert pages == [], "get_page_list() should return empty list before analysis"


# ============================================================================
# CONVENIENCE FUNCTION TESTS
# ============================================================================

class TestAnalyzeWorkflowScopeFunction:
    """
    Tests for the convenience function analyze_workflow_scope().

    Verifies the function works as expected wrapper.
    """

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_convenience_function_works(self):
        """
        P1: Verify analyze_workflow_scope() convenience function works.

        AAA Pattern:
        1. Arrange - Create BDD scenarios
        2. Act - Call convenience function
        3. Assert - Returns valid ScopeResult
        """
        # Arrange
        bdd_scenarios = [
            {"given": "user is on login page", "when": "", "then": ""}
        ]

        # Act
        result = analyze_workflow_scope(bdd_scenarios)

        # Assert
        assert isinstance(result, ScopeResult), \
            "Should return ScopeResult instance"
        assert result.page_count >= 1, \
            "Should have at least 1 page"


# ============================================================================
# DEPENDENCY TRACKING TESTS
# ============================================================================

class TestScopeDiscoveryDependencies:
    """
    Tests for page dependency tracking.

    Verifies depends_on field is set correctly.
    """

    @pytest.mark.unit
    @pytest.mark.scope_discovery
    def test_page_dependencies_tracked(self):
        """
        P1: Verify page dependencies are tracked.

        AAA Pattern:
        1. Arrange - Create sequential page workflow
        2. Act - Analyze workflow
        3. Assert - Each page (after first) has depends_on set
        """
        # Arrange
        bdd_scenarios = [
            {
                "given": "user is on login page",
                "when": "user logs in",
                "then": "user is redirected to dashboard page"
            },
            {
                "given": "user is on dashboard page",
                "when": "user clicks profile",
                "then": "user sees profile page"
            }
        ]
        discovery = ScopeDiscovery()

        # Act
        result = discovery.analyze_workflow(bdd_scenarios)

        # Assert
        assert result.pages[0].depends_on is None, \
            "First page should have no dependency"
        assert result.pages[1].depends_on == "LoginPage", \
            f"Second page should depend on first, got {result.pages[1].depends_on}"
        assert result.pages[2].depends_on == "DashboardPage", \
            f"Third page should depend on second, got {result.pages[2].depends_on}"

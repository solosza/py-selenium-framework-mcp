"""
Scope Discovery Utility

Track pages via URL changes during navigation.
Used before element discovery to understand how many POMs need to be generated.

Single Responsibility: "Track pages via URL changes during navigation"

Integrates with visual_feedback.py to show real-time discovery progress in browser.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import re


@dataclass
class PageInfo:
    """Information about a page in the workflow."""

    name: str  # PascalCase page name (e.g., "LoginPage")
    order: int  # Order in workflow (1-based)
    url: Optional[str] = None  # Full URL or path
    depends_on: Optional[str] = None  # Previous page dependency


@dataclass
class ScopeResult:
    """Result of workflow scope analysis."""

    page_count: int
    pages: List[PageInfo] = field(default_factory=list)

    @property
    def is_single_page(self) -> bool:
        """Convenience check for single page workflow."""
        return self.page_count == 1

    @property
    def is_multi_page(self) -> bool:
        """Convenience check for multi-page workflow."""
        return self.page_count > 1


class ScopeDiscovery:
    """
    Analyze BDD scenarios to discover workflow scope.

    Examines Given/When/Then clauses for navigation patterns
    to determine how many pages are involved in the workflow.
    """

    # Patterns that indicate page transitions (order matters - specific first, fallback last)
    PAGE_TRANSITION_PATTERNS = [
        # Explicit "page" mentions (highest confidence)
        r"(?:is )?(?:on|at|viewing) (?:the )?(.+?) page",  # "on login page", "viewing dashboard page"
        r"navigates? to (?:the )?(.+?) page",  # "navigates to settings page"
        r"redirected to (?:the )?(.+?) page",  # "redirected to confirmation page"
        r"(?:sees?|views?) (?:the )?(.+?) page",  # "sees confirmation page"
        r"lands on (?:the )?(.+?) page",  # "lands on dashboard page"

        # Navigation with destination (medium confidence)
        r"(?:go|goes|proceed|proceeds|move|moves|advance|advances) to (?:the )?(\w+)(?:\s|$)",  # "go to Checkout", "proceed to Address"
        r"(?:navigate|navigates) to (?:the )?(\w+)(?:\s|$)",  # "navigate to Settings"
        r"(?:click|clicks|press|presses).+?(?:to go to|to proceed to|to navigate to) (?:the )?(\w+)(?:\s|$)",  # "click Next to go to Contacts"

        # Section/step transitions (medium confidence)
        r"(?:on|at|in) (?:the )?(\w+) (?:section|step|tab|form|modal|dialog|screen|view)",  # "in the Address section"

        # Initial page from "Given" clause (lower confidence, but important)
        r"^I am on (?:the )?(.+?)$",  # "I am on the Customers portal page" -> extracts "Customers portal page"
    ]

    # Patterns that indicate URL paths
    URL_PATTERNS = [
        r"url[:\s]+['\"]?(/[^\s'\"]+)",  # "url: /login"
        r"path[:\s]+['\"]?(/[^\s'\"]+)",  # "path: /account"
        r"(?:visits?|goes? to|navigates? to)[:\s]+['\"]?(/[^\s'\"]+)",  # "visits /products"
    ]

    def __init__(self, evaluate_fn: Optional[Callable[[str], Any]] = None):
        """
        Initialize ScopeDiscovery.

        Args:
            evaluate_fn: Optional function to evaluate JavaScript in browser
                        (e.g., Playwright's browser_evaluate). If provided,
                        enables visual feedback during discovery.
        """
        self._result: Optional[ScopeResult] = None
        self._discovered_pages: Dict[str, PageInfo] = {}
        self._previous_url: Optional[str] = None
        self._evaluate_fn = evaluate_fn
        self._visual_initialized = False

    def reset(self):
        """Reset all state for a new workflow discovery."""
        self._result = None
        self._discovered_pages = {}
        self._previous_url = None
        self._visual_initialized = False

    def _init_visual_feedback(self) -> bool:
        """Initialize visual feedback overlay in browser."""
        if not self._evaluate_fn or self._visual_initialized:
            return self._visual_initialized

        try:
            # Inject CSS and create overlay
            js = """
            (function() {
                if (document.getElementById('qa-scope-overlay')) return true;

                const style = document.createElement('style');
                style.id = 'qa-scope-styles';
                style.textContent = `
                    #qa-scope-overlay {
                        position: fixed;
                        bottom: 20px;
                        left: 20px;
                        z-index: 999999;
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size: 13px;
                        background: rgba(0, 0, 0, 0.9);
                        color: #00ff00;
                        padding: 15px 20px;
                        border-radius: 8px;
                        border: 2px solid #00ff00;
                        box-shadow: 0 4px 20px rgba(0, 255, 0, 0.3);
                        min-width: 320px;
                    }
                    #qa-scope-overlay .header {
                        font-size: 14px;
                        font-weight: bold;
                        margin-bottom: 10px;
                        padding-bottom: 8px;
                        border-bottom: 1px solid #00ff00;
                    }
                    #qa-scope-overlay .page-list {
                        margin: 0;
                        padding: 0;
                        list-style: none;
                    }
                    #qa-scope-overlay .page-item {
                        padding: 4px 0;
                        display: flex;
                        align-items: center;
                    }
                    #qa-scope-overlay .page-num {
                        color: #ffff00;
                        margin-right: 10px;
                        font-weight: bold;
                    }
                    #qa-scope-overlay .page-name {
                        color: #00ff00;
                        flex: 1;
                    }
                    #qa-scope-overlay .page-url {
                        color: #888;
                        font-size: 11px;
                        margin-left: 10px;
                    }
                    #qa-scope-overlay .status {
                        margin-top: 10px;
                        padding-top: 8px;
                        border-top: 1px solid #444;
                        color: #ffff00;
                    }
                `;
                document.head.appendChild(style);

                const overlay = document.createElement('div');
                overlay.id = 'qa-scope-overlay';
                overlay.innerHTML = `
                    <div class="header">SCOPE DISCOVERY</div>
                    <ul id="qa-page-list" class="page-list"></ul>
                    <div id="qa-scope-status" class="status">Navigating...</div>
                `;
                document.body.appendChild(overlay);
                return true;
            })();
            """
            self._evaluate_fn(js)
            self._visual_initialized = True
            return True
        except Exception:
            return False

    def _update_visual_page(self, page: PageInfo) -> bool:
        """Update visual display with newly discovered page."""
        if not self._evaluate_fn:
            return False

        if not self._visual_initialized:
            self._init_visual_feedback()

        try:
            # Extract path from URL for display
            url_display = page.url or ""
            if url_display:
                url_display = re.sub(r'^https?://[^/]+', '', url_display)

            js = f"""
            (function() {{
                const list = document.getElementById('qa-page-list');
                const status = document.getElementById('qa-scope-status');
                if (!list) return false;

                const item = document.createElement('li');
                item.className = 'page-item';
                item.innerHTML = `
                    <span class="page-num">{page.order}.</span>
                    <span class="page-name">{page.name}</span>
                    <span class="page-url">{url_display}</span>
                `;
                list.appendChild(item);

                if (status) {{
                    status.textContent = 'Pages discovered: {len(self._discovered_pages)}';
                }}
                return true;
            }})();
            """
            self._evaluate_fn(js)
            return True
        except Exception:
            return False

    def _finalize_visual(self) -> bool:
        """Update visual display with final scope result."""
        if not self._evaluate_fn or not self._visual_initialized:
            return False

        try:
            page_count = len(self._discovered_pages)
            js = f"""
            (function() {{
                const status = document.getElementById('qa-scope-status');
                if (status) {{
                    status.innerHTML = '<span style="color: #00ff00;">COMPLETE: {page_count} page(s) discovered</span>';
                }}
                return true;
            }})();
            """
            self._evaluate_fn(js)
            return True
        except Exception:
            return False

    def analyze_workflow(self, bdd_scenarios: List[Dict]) -> ScopeResult:
        """
        Analyze BDD scenarios to determine workflow scope.

        Args:
            bdd_scenarios: List of BDD scenarios with given/when/then keys.
                          Each scenario is a dict with 'given', 'when', 'then' keys.

        Returns:
            ScopeResult with page count and page information
        """
        discovered_pages: Dict[str, PageInfo] = {}
        current_order = 0
        previous_page: Optional[str] = None

        for scenario in bdd_scenarios:
            # Extract text from all clauses
            clauses = []

            # Handle both string and list formats for clauses
            for clause_type in ['given', 'when', 'then']:
                clause_content = scenario.get(clause_type, [])
                if isinstance(clause_content, str):
                    clauses.append(clause_content)
                elif isinstance(clause_content, list):
                    clauses.extend(clause_content)

            # Analyze each clause for page references
            for clause in clauses:
                page_name = self._extract_page_name(clause)
                url_path = self._extract_url_path(clause)

                if page_name and page_name not in discovered_pages:
                    current_order += 1
                    discovered_pages[page_name] = PageInfo(
                        name=page_name,
                        order=current_order,
                        url=url_path,
                        depends_on=previous_page
                    )
                    previous_page = page_name
                elif page_name and url_path and not discovered_pages[page_name].url:
                    # Update URL if we found one later
                    discovered_pages[page_name].url = url_path

        # Sort pages by order and create result
        pages = sorted(discovered_pages.values(), key=lambda p: p.order)

        # Default to single page if no pages detected
        if not pages:
            pages = [PageInfo(name="MainPage", order=1)]

        self._result = ScopeResult(
            page_count=len(pages),
            pages=pages
        )

        return self._result

    def get_page_list(self) -> List[PageInfo]:
        """
        Get the list of discovered pages.

        Returns:
            List of PageInfo objects, or empty list if not analyzed yet.
        """
        if self._result is None:
            return []
        return self._result.pages

    def is_single_page(self) -> bool:
        """
        Check if workflow is single page.

        Returns:
            True if single page, False otherwise.
            Returns False if not analyzed yet.
        """
        if self._result is None:
            return False
        return self._result.is_single_page

    def is_multi_page(self) -> bool:
        """
        Check if workflow spans multiple pages.

        Returns:
            True if multi-page, False otherwise.
            Returns False if not analyzed yet.
        """
        if self._result is None:
            return False
        return self._result.is_multi_page

    def _extract_page_name(self, clause: str) -> Optional[str]:
        """
        Extract page name from BDD clause.

        Args:
            clause: BDD clause text (e.g., "user is on login page")

        Returns:
            PascalCase page name or None if not found
        """
        clause_lower = clause.lower()

        for pattern in self.PAGE_TRANSITION_PATTERNS:
            match = re.search(pattern, clause_lower, re.IGNORECASE)
            if match:
                raw_name = match.group(1).strip()
                return self._to_page_name(raw_name)

        return None

    def _extract_url_path(self, clause: str) -> Optional[str]:
        """
        Extract URL path from BDD clause.

        Args:
            clause: BDD clause text

        Returns:
            URL path or None if not found
        """
        for pattern in self.URL_PATTERNS:
            match = re.search(pattern, clause, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _to_page_name(self, raw_name: str) -> str:
        """
        Convert raw page reference to PascalCase page name.

        Args:
            raw_name: Raw page reference (e.g., "login", "my account")

        Returns:
            PascalCase page name (e.g., "LoginPage", "MyAccountPage")
        """
        # Remove common suffixes that would be redundant
        cleaned = raw_name.strip()
        for suffix in [' page', ' screen', ' view']:
            if cleaned.lower().endswith(suffix):
                cleaned = cleaned[:-len(suffix)]

        # Split on spaces, hyphens, underscores
        words = re.split(r'[\s\-_]+', cleaned)

        # Capitalize each word and join
        pascal_case = ''.join(word.capitalize() for word in words if word)

        # Ensure it ends with "Page"
        if not pascal_case.endswith('Page'):
            pascal_case += 'Page'

        return pascal_case

    def register_page(self, url: str, page_name: Optional[str] = None) -> PageInfo:
        """
        Register a new page discovered through navigation.

        Automatically updates visual feedback if evaluate_fn was provided.

        Args:
            url: The URL of the page (used to detect duplicates)
            page_name: Optional PascalCase page name. If not provided,
                      will be derived from URL path.

        Returns:
            PageInfo for the registered page
        """
        # Normalize URL for comparison (strip query params, trailing slash)
        normalized_url = self._normalize_url(url)

        # Check if already registered
        for page in self._discovered_pages.values():
            if page.url and self._normalize_url(page.url) == normalized_url:
                return page

        # Derive page name from URL if not provided
        if not page_name:
            page_name = self._url_to_page_name(url)

        # Create new page info
        order = len(self._discovered_pages) + 1
        previous_page = list(self._discovered_pages.keys())[-1] if self._discovered_pages else None

        page_info = PageInfo(
            name=page_name,
            order=order,
            url=url,
            depends_on=previous_page
        )

        self._discovered_pages[page_name] = page_info

        # Update visual feedback
        self._update_visual_page(page_info)

        return page_info

    def is_new_page(self, current_url: str, previous_url: Optional[str]) -> bool:
        """
        Check if URL change indicates a new page.

        Args:
            current_url: Current page URL
            previous_url: Previous page URL (None if first page)

        Returns:
            True if this is a new page, False otherwise
        """
        if previous_url is None:
            return True

        return self._normalize_url(current_url) != self._normalize_url(previous_url)

    def get_discovered_pages(self) -> List[PageInfo]:
        """
        Get all pages discovered through navigation.

        Returns:
            List of PageInfo objects in discovery order
        """
        return sorted(self._discovered_pages.values(), key=lambda p: p.order)

    def get_scope_result(self) -> ScopeResult:
        """
        Get scope result from navigation-based discovery.

        Finalizes visual feedback display if enabled.

        Returns:
            ScopeResult with discovered pages
        """
        pages = self.get_discovered_pages()

        if not pages:
            pages = [PageInfo(name="MainPage", order=1)]

        self._result = ScopeResult(
            page_count=len(pages),
            pages=pages
        )

        # Finalize visual feedback
        self._finalize_visual()

        return self._result

    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL for comparison.

        Strips query parameters, fragments, and trailing slashes.
        """
        # Remove query params and fragments
        url = re.sub(r'[?#].*$', '', url)
        # Remove trailing slash
        url = url.rstrip('/')
        return url

    def _url_to_page_name(self, url: str) -> str:
        """
        Derive PascalCase page name from URL.

        Examples:
            /cart.html -> CartPage
            /checkout-step-one.html -> CheckoutStepOnePage
            /inventory -> InventoryPage
        """
        # Extract path from URL
        path = re.sub(r'^https?://[^/]+', '', url)
        path = self._normalize_url(path)

        # Get last path segment
        segments = [s for s in path.split('/') if s]
        if not segments:
            return "MainPage"

        last_segment = segments[-1]

        # Remove file extension
        last_segment = re.sub(r'\.[a-z]+$', '', last_segment, flags=re.IGNORECASE)

        # Convert to PascalCase
        return self._to_page_name(last_segment)


def analyze_workflow_scope(bdd_scenarios: List[Dict]) -> ScopeResult:
    """
    Convenience function to analyze workflow scope from BDD text.

    Note: This is a fallback method. Prefer navigation-based discovery
    using ScopeDiscovery.register_page() for accurate page detection.

    Args:
        bdd_scenarios: List of BDD scenarios with given/when/then keys

    Returns:
        ScopeResult with page count and page information
    """
    discovery = ScopeDiscovery()
    return discovery.analyze_workflow(bdd_scenarios)


def create_navigation_tracker(
    evaluate_fn: Optional[Callable[[str], Any]] = None
) -> "ScopeDiscovery":
    """
    Create a new navigation-based scope tracker.

    Args:
        evaluate_fn: Optional function to evaluate JavaScript in browser.
                    If provided, enables visual feedback overlay showing
                    discovered pages in real-time.

    Usage:
        # Without visual feedback
        tracker = create_navigation_tracker()

        # With visual feedback (Playwright MCP)
        def eval_js(js):
            return mcp__playwright__browser_evaluate(function=js)
        tracker = create_navigation_tracker(evaluate_fn=eval_js)

        # As you navigate through pages:
        if tracker.is_new_page(current_url, previous_url):
            tracker.register_page(current_url)

        # When done:
        result = tracker.get_scope_result()
        print(f"Found {result.page_count} pages")

    Returns:
        ScopeDiscovery instance for tracking pages through navigation
    """
    return ScopeDiscovery(evaluate_fn=evaluate_fn)

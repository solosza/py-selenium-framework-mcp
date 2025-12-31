"""
Scope Discovery Utility

Analyze BDD scenarios to determine workflow scope (page count and dependencies).
Used before element discovery to understand how many POMs need to be generated.

Single Responsibility: "How many pages in this workflow?"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class PageInfo:
    """Information about a page in the workflow."""

    name: str  # PascalCase page name (e.g., "LoginPage")
    order: int  # Order in workflow (1-based)
    entry_url: Optional[str] = None  # URL path if determinable
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

    # Patterns that indicate page transitions
    PAGE_TRANSITION_PATTERNS = [
        r"(?:is )?(?:on|at|viewing) (?:the )?(.+?) page",  # "on login page", "viewing dashboard page"
        r"navigates? to (?:the )?(.+?) page",  # "navigates to settings page"
        r"redirected to (?:the )?(.+?) page",  # "redirected to confirmation page"
        r"(?:sees|views) (?:the )?(.+?) page",  # "sees confirmation page"
        r"lands on (?:the )?(.+?) page",  # "lands on dashboard page"
        r"(?:is )?(?:on|at) (?:the )?(.+?)$",  # "is on home" (fallback)
    ]

    # Patterns that indicate URL paths
    URL_PATTERNS = [
        r"url[:\s]+['\"]?(/[^\s'\"]+)",  # "url: /login"
        r"path[:\s]+['\"]?(/[^\s'\"]+)",  # "path: /account"
        r"(?:visits?|goes? to|navigates? to)[:\s]+['\"]?(/[^\s'\"]+)",  # "visits /products"
    ]

    def __init__(self):
        """Initialize ScopeDiscovery."""
        self._result: Optional[ScopeResult] = None

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
                        entry_url=url_path,
                        depends_on=previous_page
                    )
                    previous_page = page_name
                elif page_name and url_path and not discovered_pages[page_name].entry_url:
                    # Update URL if we found one later
                    discovered_pages[page_name].entry_url = url_path

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


def analyze_workflow_scope(bdd_scenarios: List[Dict]) -> ScopeResult:
    """
    Convenience function to analyze workflow scope.

    Args:
        bdd_scenarios: List of BDD scenarios with given/when/then keys

    Returns:
        ScopeResult with page count and page information
    """
    discovery = ScopeDiscovery()
    return discovery.analyze_workflow(bdd_scenarios)

"""
Quality Gate: Discovered Elements (Step 4).

PRE+POST validation gate for Tool 2 (discover_page_elements) or DD-33 (Playwright snapshot).

PRE Validation:
- Step 3 complete (bdd_scenarios, expected_states, intent exist in state)
- URL present and valid format (http/https)
- page_name present
- credential_strategy present and valid (IC-05-01)
- discovery_method present and valid ("tool2" or "playwright") (DD-33)
- NEW (Task 2.0): If scope_result provided, validate page_name is in scope's page list
- NEW (DD-44): Auto-detect multi-page from BDD, require scope_result if page_count > 1

POST Validation:
- elements array present and not empty
- Each element has: suggested_name, element_type, at least one non-empty locator (IC-05-03)
- page_name is PascalCase (IC-05-02)
- NEW (Task 2.0): Track per-page elements, track discovery progress for multi-page workflows
- NEW (DD-44): Block Step 6 if multi-page and discovery incomplete
- NEW (DD-46): validation_results required (from RuntimeValidator, triggers VisualFeedback)

Enforces: DD-19, DD-20, DD-21, DD-24, DD-33, DD-44, DD-46, IC-05-01, IC-05-02, IC-05-03
"""

import re
from typing import Any, Dict, List, Optional

from .base_gate import BaseGate
from utils.state_manager import StateManager
from utils.scope_discovery import ScopeDiscovery, ScopeResult


class QGDiscoveredElements(BaseGate):
    """Quality gate for Step 4: Discovered Elements."""

    # Step number for this gate (used for attempt tracking)
    STEP_NUMBER = 4

    # Valid credential strategies (from DD-24)
    VALID_CREDENTIAL_STRATEGIES = {"none", "static", "dynamic", "self-contained"}

    # Valid discovery methods (from DD-33)
    VALID_DISCOVERY_METHODS = {"tool2", "playwright"}

    # Valid element types (DEF-045 two-pass discovery)
    VALID_ELEMENT_TYPES = {"input", "output"}

    # PascalCase pattern (IC-05-02): starts with uppercase, alphanumeric
    PASCAL_CASE_PATTERN = re.compile(r'^[A-Z][a-zA-Z0-9]*$')

    @classmethod
    def _get_state_manager(cls) -> StateManager:
        """Get StateManager instance. Extracted for testing."""
        # Task 13.0: Use per-run state isolation
        audit_logger = cls.get_audit_logger()
        return StateManager(run_id=audit_logger.run_id)

    @classmethod
    def validate_pre(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PRE validation before Tool 2 operation or DD-33 snapshot extraction.

        Validates:
        - Step 3 transcript exists (hook validation)
        - Step 3 is complete
        - URL is present and valid format
        - page_name is present
        - credential_strategy is present and valid (IC-05-01)
        - discovery_method is present and valid (DD-33)

        Args:
            input_data: Dict with url, page_name, credential_strategy, discovery_method

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "teach": str}
        """
        # PRE-CHECK: Verify Step 3 transcript was written by hook
        pre_check_error = cls.pre_check_previous_transcript(
            previous_step=3,
            previous_step_name="AI Processing"
        )
        if pre_check_error:
            return pre_check_error

        # Check Step 3 completion
        state_manager = cls._get_state_manager()
        if not state_manager.is_step_complete(3):
            return cls.fail_response(
                error="Step 3 is not complete. Cannot proceed to Step 4.",
                teach="Complete Step 3 (AI Processing) first. Ensure bdd_scenarios, expected_states, and intent are validated."
            )

        # Validate URL
        url = input_data.get("url")
        if url is None:
            return cls.fail_response(
                error="Missing required field: url",
                teach="Provide the target URL from Step 2 state."
            )

        if not isinstance(url, str) or not url.strip():
            return cls.fail_response(
                error="url must be a non-empty string",
                teach="Provide a valid URL like 'http://example.com/page'"
            )

        if not url.startswith("http://") and not url.startswith("https://"):
            return cls.fail_response(
                error="url must start with http:// or https://",
                teach="Use full URL format: http://example.com or https://example.com"
            )

        # Validate page_name
        page_name = input_data.get("page_name")
        if page_name is None:
            return cls.fail_response(
                error="Missing required field: page_name",
                teach="Provide page_name (e.g., 'LoginPage', 'CartPage')."
            )

        if not isinstance(page_name, str) or not page_name.strip():
            return cls.fail_response(
                error="page_name must be a non-empty string",
                teach="Provide a descriptive page name like 'LoginPage'."
            )

        # Validate credential_strategy (IC-05-01)
        credential_strategy = input_data.get("credential_strategy")
        if credential_strategy is None:
            return cls.fail_response(
                error="Missing required field: credential_strategy (IC-05-01)",
                teach=f"Provide credential_strategy from Step 1. Valid options: {', '.join(sorted(cls.VALID_CREDENTIAL_STRATEGIES))}"
            )

        if credential_strategy not in cls.VALID_CREDENTIAL_STRATEGIES:
            return cls.fail_response(
                error=f"Invalid credential_strategy: '{credential_strategy}'",
                teach=f"Use one of: {', '.join(sorted(cls.VALID_CREDENTIAL_STRATEGIES))}"
            )

        # Validate discovery_method (DD-33)
        discovery_method = input_data.get("discovery_method")
        if discovery_method is None:
            return cls.fail_response(
                error="Missing required field: discovery_method (DD-33)",
                teach=f"Declare discovery_method. Use 'playwright' if Playwright prepared page state, 'tool2' for static pages. Valid options: {', '.join(sorted(cls.VALID_DISCOVERY_METHODS))}"
            )

        if discovery_method not in cls.VALID_DISCOVERY_METHODS:
            return cls.fail_response(
                error=f"Invalid discovery_method: '{discovery_method}'",
                teach=f"Use one of: {', '.join(sorted(cls.VALID_DISCOVERY_METHODS))}. Use 'playwright' if Playwright prepared page state."
            )

        # Validate element type (DEF-045 two-pass discovery)
        # Default to "input" for backward compatibility
        element_type = input_data.get("type", "input")
        if element_type not in cls.VALID_ELEMENT_TYPES:
            return cls.fail_response(
                error=f"Invalid type: '{element_type}'",
                teach=f"Use one of: {', '.join(sorted(cls.VALID_ELEMENT_TYPES))}. Use 'input' for forms/buttons (PASS 1), 'output' for messages/confirmations (PASS 2)."
            )

        # DD-44: Auto-detect multi-page from BDD and enforce scope_result
        scope_result = input_data.get("scope_result")
        detected_page_count = cls._detect_page_count_from_bdd(state_manager)

        if detected_page_count > 1 and scope_result is None:
            # SELF-HEALING: Calculate scope_result and provide it to AI
            # Task 26.0: Try navigation-first (PASS 0), fallback to BDD
            calculated_scope = cls._calculate_scope_from_navigation()
            if calculated_scope is None:
                # Fallback to BDD detection
                calculated_scope = cls._calculate_scope_result_from_bdd(state_manager)

            if calculated_scope is not None:
                return {
                    "status": "fail",
                    "error": f"Multi-page workflow detected ({detected_page_count} pages) but scope_result not provided (DD-44)",
                    "teach": "Retry with the provided scope_result included in your next call.",
                    "scope_result": calculated_scope  # ← Self-healing: provide the fix
                }
            else:
                # Fallback if both navigation and BDD calculations fail
                return cls.fail_response(
                    error=f"Multi-page workflow detected ({detected_page_count} pages) but scope_result not provided (DD-44)",
                    teach="Call scope_discovery.analyze_workflow(bdd_scenarios) first, then pass scope_result to this gate."
                )

        # Task 2.0: Validate scope_result if provided (for multi-page workflows)
        if scope_result is not None:
            scope_validation = cls._validate_scope_result(scope_result, page_name)
            if scope_validation is not None:
                return scope_validation

        return cls.pass_response(
            step=5,
            gate_name="qg_discovered_elements",
            mode="PRE",
            metadata={
                "page_name": page_name,
                "url": url,
                "multi_page": scope_result is not None,
                "total_pages": scope_result.get("total_pages") if scope_result else 1
            }
        )

    @classmethod
    def _validate_scope_result(cls, scope_result: Dict[str, Any], page_name: str) -> Optional[Dict[str, Any]]:
        """
        Task 2.0: Validate scope_result structure and page_name membership.

        Args:
            scope_result: Scope analysis result from scope_discovery
            page_name: Page name being discovered

        Returns:
            None if valid, fail_response dict if invalid
        """
        # Validate scope_result structure
        if not isinstance(scope_result, dict):
            return cls.fail_response(
                error="scope_result must be a dictionary",
                teach="Provide scope_result from scope_discovery.analyze_workflow()"
            )

        page_count = scope_result.get("page_count")
        if page_count is None or not isinstance(page_count, int):
            return cls.fail_response(
                error="scope_result missing required field: page_count",
                teach="scope_result must have page_count (int) from scope_discovery"
            )

        pages = scope_result.get("pages", [])
        if not isinstance(pages, list):
            return cls.fail_response(
                error="scope_result.pages must be a list",
                teach="scope_result.pages should be list of PageInfo dicts"
            )

        # For multi-page workflows, validate page_name is in scope
        if page_count > 1:
            page_names_in_scope = cls._extract_page_names(pages)
            if page_name not in page_names_in_scope:
                return cls.fail_response(
                    error=f"page_name '{page_name}' not found in scope's page list",
                    teach=f"page_name must match one from scope discovery. Available: {', '.join(page_names_in_scope)}"
                )

        return None

    @classmethod
    def _extract_page_names(cls, pages: List[Any]) -> List[str]:
        """
        Extract page names from scope_result.pages list.

        Args:
            pages: List of PageInfo dicts or objects

        Returns:
            List of page name strings
        """
        names = []
        for page in pages:
            if isinstance(page, dict):
                name = page.get("name")
            elif hasattr(page, "name"):
                name = page.name
            else:
                continue
            if name and isinstance(name, str):
                names.append(name)
        return names

    @classmethod
    def _detect_page_count_from_bdd(cls, state_manager: StateManager) -> int:
        """
        DD-44: Detect page count from BDD scenarios OR snapshot analysis.

        Priority:
        1. Check if snapshot_analysis was stored in Step 5 state (most reliable)
        2. Fall back to BDD analysis from Step 4 (less reliable)

        Note: Prefer AI calling analyze_snapshot_for_pages() with actual DOM
        and passing scope_result explicitly. BDD analysis is a fallback only.

        Args:
            state_manager: StateManager instance to read state

        Returns:
            Detected page count (defaults to 1 if detection fails)
        """
        try:
            # Priority 1: Check for snapshot-based analysis (more reliable)
            step_5_state = state_manager.get_step(5) or {}
            if step_5_state.get("total_pages", 0) > 1:
                return step_5_state["total_pages"]

            # Priority 2: Fall back to BDD analysis
            step_4_state = state_manager.get_step(4)
            if not step_4_state:
                return 1  # No Step 4 state, assume single page

            test_scenarios = step_4_state.get("test_scenarios", [])
            if not test_scenarios:
                return 1  # No scenarios, assume single page

            # Use ScopeDiscovery to analyze BDD
            discovery = ScopeDiscovery()
            result = discovery.analyze_workflow(test_scenarios)

            return result.page_count

        except Exception:
            # If anything fails, default to single page (don't block workflow)
            return 1

    @classmethod
    def _calculate_scope_result_from_bdd(cls, state_manager: StateManager) -> Optional[Dict[str, Any]]:
        """
        SELF-HEALING: Calculate full scope_result from BDD scenarios.

        This method provides the AI with scope_result when it's missing,
        enabling self-healing workflow continuation.

        Args:
            state_manager: StateManager instance to read state

        Returns:
            scope_result dict with page_count and pages, or None if calculation fails
        """
        try:
            step_4_state = state_manager.get_step(4)
            if not step_4_state:
                return None

            test_scenarios = step_4_state.get("test_scenarios", [])
            if not test_scenarios:
                return None

            # Use ScopeDiscovery to analyze BDD
            discovery = ScopeDiscovery()
            result = discovery.analyze_workflow(test_scenarios)

            # Convert ScopeResult to dict for JSON serialization
            return {
                "page_count": result.page_count,
                "pages": [
                    {
                        "name": page.name,
                        "order": page.order,
                        "url": page.url,
                        "depends_on": page.depends_on
                    }
                    for page in result.pages
                ]
            }

        except Exception:
            # If calculation fails, return None (fallback to original error)
            return None

    @classmethod
    def _read_audit_log_entries(cls) -> Optional[List[Dict[str, Any]]]:
        """
        Task 26.0: Read entries from the audit log JSON file.

        Returns:
            List of audit log entries from "steps" field, or None if read fails
        """
        try:
            audit_logger = cls.get_audit_logger()
            audit_file_path = audit_logger._audit_file

            if not audit_file_path.exists():
                return None

            with open(audit_file_path, 'r') as f:
                import json
                data = json.load(f)

            return data.get("steps", [])

        except Exception:
            # If read fails, return None (fallback to BDD detection)
            return None

    @classmethod
    def _infer_page_name_from_url(cls, url: str) -> str:
        """
        Task 26.0: Infer PascalCase page name from URL.

        Examples:
        - https://example.com/login.htm → LoginPage
        - https://example.com/transfer → TransferPage
        - https://example.com/accounts/overview → AccountsOverviewPage
        - https://example.com/ → HomePage

        Args:
            url: Full URL string

        Returns:
            PascalCase page name with "Page" suffix
        """
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            path = parsed.path.strip('/')

            if not path:
                # Root path
                return "HomePage"

            # Extract segments (e.g., ["accounts", "overview"] or ["login.htm"])
            segments = path.split('/')

            # For multi-segment paths, combine meaningful segments
            # Skip generic segments like "page", "view"
            skip_segments = {"page", "view", "index"}
            meaningful_segments = [s for s in segments if s.lower() not in skip_segments]

            # If only one segment, use it; otherwise combine last 2-3 segments
            if len(meaningful_segments) == 1:
                name_parts = meaningful_segments[0]
            elif len(meaningful_segments) >= 2:
                # Take last 2 segments (e.g., "accounts/overview" → "accounts_overview")
                name_parts = '_'.join(meaningful_segments[-2:])
            else:
                name_parts = "unknown"

            # Remove file extension if present
            name_without_ext = name_parts.split('.')[0]

            # Convert to PascalCase
            words = name_without_ext.replace('_', ' ').replace('-', ' ').split()
            pascal_case = ''.join(word.capitalize() for word in words)

            # Add "Page" suffix if not already present
            if not pascal_case.endswith("Page"):
                pascal_case += "Page"

            return pascal_case

        except Exception:
            # Fallback to generic name
            return "UnknownPage"

    @classmethod
    def _calculate_scope_from_navigation(cls) -> Optional[Dict[str, Any]]:
        """
        Task 26.0: Calculate scope_result from navigation calls in audit log.

        PASS 0: Navigation-first detection (more reliable than BDD).

        Reads audit log for browser_navigate calls, extracts URLs,
        deduplicates, and builds PageInfo objects.

        Returns:
            scope_result dict with page_count and pages, or None if no navigation calls
        """
        try:
            # Read audit log
            entries = cls._read_audit_log_entries()
            if not entries:
                return None

            # Filter for browser_navigate calls
            navigate_calls = [
                e for e in entries
                if e.get("type") == "mcp_tool" and e.get("tool_name") == "browser_navigate"
            ]

            if not navigate_calls:
                return None

            # Extract URLs and deduplicate
            urls = []
            seen_urls = set()
            for call in navigate_calls:
                args = call.get("args", {})
                url = args.get("url")
                if url and url not in seen_urls:
                    urls.append(url)
                    seen_urls.add(url)

            if not urls:
                return None

            # Build PageInfo objects
            pages = []
            for i, url in enumerate(urls):
                page_name = cls._infer_page_name_from_url(url)
                pages.append({
                    "name": page_name,
                    "page_name": page_name,  # Add both fields for compatibility
                    "order": i + 1,
                    "url": url,
                    "depends_on": [],
                    "reason": "navigation detected"  # Distinguish from BDD detection
                })

            # Return scope_result
            return {
                "page_count": len(pages),
                "total_pages": len(pages),  # Add both fields for compatibility
                "pages": pages
            }

        except Exception:
            # If navigation detection fails, return None (fallback to BDD)
            return None

    @classmethod
    def get_discovery_progress(cls) -> Dict[str, Any]:
        """
        Task 2.0: Get current element discovery progress.

        Returns:
            Dict with discovery status:
            - discovered_pages: dict mapping page_name -> elements
            - pages_discovered: number of pages discovered so far
            - total_pages: total pages in scope
            - discovery_complete: True if all pages discovered
            - remaining_pages: list of page names not yet discovered (if scope available)
        """
        state_manager = cls._get_state_manager()
        step_5_state = state_manager.get_step(5) or {}

        discovered_pages = step_5_state.get("discovered_pages", {})
        pages_discovered = step_5_state.get("pages_discovered", 0)
        total_pages = step_5_state.get("total_pages", 0)
        discovery_complete = step_5_state.get("discovery_complete", False)

        return {
            "discovered_pages": discovered_pages,
            "pages_discovered": pages_discovered,
            "total_pages": total_pages,
            "discovery_complete": discovery_complete
        }

    @classmethod
    def is_discovery_complete(cls) -> bool:
        """
        Task 2.0: Check if all pages in scope have been discovered.

        Returns:
            True if discovery_complete flag is set, False otherwise
        """
        state_manager = cls._get_state_manager()
        step_5_state = state_manager.get_step(5) or {}
        return step_5_state.get("discovery_complete", False)

    @classmethod
    def validate_post(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST validation after Tool 2 operation or DD-33 snapshot extraction.

        Validates:
        - elements array is present and not empty
        - Each element has: suggested_name, element_type, at least one non-empty locator (IC-05-03)
        - page_name is PascalCase (IC-05-02)

        On PASS: Saves Step 5 state (enables DD-33 flow where Tool 2 is skipped).

        Args:
            input_data: Dict with elements array and page_name

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "teach": str}
            or {"status": "blocked", ...} if max attempts exceeded
        """
        # P1: Check if blocked due to max attempts
        state_manager = cls._state_manager
        if state_manager:
            attempts = state_manager.get_attempt_count(cls.STEP_NUMBER)
            if attempts >= cls.MAX_ATTEMPTS:
                return cls.blocked_response(
                    step=cls.STEP_NUMBER,
                    attempts=attempts,
                    errors=[]
                )

        # Run actual validation
        result = cls._validate_post_internal(input_data)

        # P2: Extract source from input_data for audit logging
        source = input_data.get("source")

        # P1: Track attempts and log to audit
        if state_manager:
            if result.get("status") == "fail":
                state_manager.increment_attempt(cls.STEP_NUMBER)
                # DEF-040: Log failure to audit (lazy init)
                cls.get_audit_logger().log_gate(
                    step=cls.STEP_NUMBER,
                    gate_name="qg_discovered_elements",
                    mode="POST",
                    result="fail",
                    error=result.get("error"),
                    source=source
                )
            elif result.get("status") == "pass":
                state_manager.reset_attempts(cls.STEP_NUMBER)
                # DEF-040: Log success with source (lazy init)
                cls.get_audit_logger().log_gate(
                    step=cls.STEP_NUMBER,
                    gate_name="qg_discovered_elements",
                    mode="POST",
                    result="pass",
                    source=source
                )

        return result

    @classmethod
    def _validate_post_internal(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal validation logic (separated for attempt tracking)."""
        # Validate elements array
        elements = input_data.get("elements")

        if elements is None:
            return cls.fail_response(
                error="Missing required field: elements",
                teach="Tool 2 must return elements array."
            )

        if not isinstance(elements, list):
            return cls.fail_response(
                error="elements must be a list",
                teach="Tool 2 should return elements as an array."
            )

        if len(elements) == 0:
            return cls.fail_response(
                error="elements is empty. At least one interactive element required.",
                teach="Retry Tool 2 - ensure page has interactive elements or prepare page state (DD-20)."
            )

        # Validate each element
        for i, element in enumerate(elements):
            element_error = cls._validate_element(element, i)
            if element_error:
                return element_error

        # DD-46: Smart conditional enforcement based on discovery_method (DEF-058)
        # - playwright: auto-validate (DD-33 already validated via accessibility tree)
        # - tool2: require validation (Selenium needs explicit validation)
        discovery_method = input_data.get("discovery_method")
        validation_results = input_data.get("validation_results")

        if discovery_method == "playwright":
            # DD-33 flow: Elements already validated by snapshot extraction
            if validation_results is None:
                # SELF-HEALING: Auto-generate validation_results (Smart Gate pattern DD-50)
                validation_results = {
                    "valid_count": len(elements),
                    "error_count": 0,
                    "elements": [
                        {"name": elem.get("suggested_name", "unknown"), "is_valid": True, "source": "snapshot"}
                        for elem in elements
                    ],
                    "note": "Auto-validated via DD-33 snapshot extraction"
                }
                input_data["validation_results"] = validation_results

        elif discovery_method == "tool2":
            # Tool 2 flow: MUST have RuntimeValidator results
            if validation_results is None:
                return cls.fail_response(
                    error="Missing required field: validation_results (DD-46)",
                    teach="Tool 2 elements MUST be validated via RuntimeValidator. "
                             "Call RuntimeValidator.validate_element() for each discovered element. "
                             "RuntimeValidator automatically triggers VisualFeedback for visual highlights. "
                             "Collect results into validation_results dict with valid_count, error_count, elements."
                )

        else:
            # Unknown discovery_method - require validation_results for safety
            if validation_results is None:
                return cls.fail_response(
                    error="Missing required field: validation_results (DD-46)",
                    teach="Call RuntimeValidator.validate_element() for each discovered element. "
                             "RuntimeValidator automatically triggers VisualFeedback for visual highlights. "
                             "Collect results into validation_results dict with valid_count, error_count, elements."
                )

        # Validate validation_results structure
        validation_error = cls._validate_validation_results(validation_results)
        if validation_error:
            return validation_error

        # Validate page_name PascalCase (IC-05-02)
        page_name = input_data.get("page_name")
        if page_name is None:
            return cls.fail_response(
                error="Missing required field: page_name",
                teach="Provide page_name for the discovered elements."
            )

        if not isinstance(page_name, str) or not page_name.strip():
            return cls.fail_response(
                error="page_name must be a non-empty string",
                teach="Provide a descriptive page name."
            )

        if not cls.PASCAL_CASE_PATTERN.match(page_name):
            return cls.fail_response(
                error=f"page_name '{page_name}' is not PascalCase (IC-05-02)",
                teach="Use PascalCase format: 'LoginPage', 'CartModal', 'CheckoutForm'"
            )

        # Task 2.0: Track per-page elements for multi-page workflows
        # DEF-045: Track BOTH input and output elements per page
        state_manager = cls._get_state_manager()
        scope_result = input_data.get("scope_result")
        element_type = input_data.get("type", "input")  # Default to "input" for backward compat

        # Load existing step 5 state to preserve per-page tracking
        existing_state = state_manager.get_step(5) or {}
        discovered_pages = existing_state.get("discovered_pages", {})

        # Guard against corrupted state (from mixed workflows or old format)
        # This self-heals state by overwriting with clean structure on next save
        if not isinstance(discovered_pages, dict):
            discovered_pages = {}

        # DEF-045: Nested structure for two-pass discovery
        # Initialize page structure if first time OR migrate old flat structure
        if page_name not in discovered_pages:
            discovered_pages[page_name] = {}
        elif isinstance(discovered_pages[page_name], list):
            # MIGRATION: Convert old flat structure (list) to new nested structure (dict)
            # Old structure was just a list of elements, preserve as input elements
            old_elements = discovered_pages[page_name]
            discovered_pages[page_name] = {"input_elements": old_elements}

        # Add elements to appropriate type key
        if element_type == "input":
            discovered_pages[page_name]["input_elements"] = elements
        elif element_type == "output":
            discovered_pages[page_name]["output_elements"] = elements

        # Calculate discovery progress
        if scope_result and isinstance(scope_result, dict):
            total_pages = scope_result.get("page_count", 1)
            # DEF-045: Page is discovered when it has BOTH input AND output elements
            pages_discovered = sum(
                1 for page_data in discovered_pages.values()
                if isinstance(page_data, dict) and
                   page_data.get("input_elements") and
                   page_data.get("output_elements")
            )
            discovery_complete = pages_discovered >= total_pages
        else:
            total_pages = 1
            # Single page: check if both types present
            page_data = discovered_pages.get(page_name, {})
            if isinstance(page_data, dict):
                has_both = bool(page_data.get("input_elements") and page_data.get("output_elements"))
            else:
                # Backward compat: old flat structure
                has_both = bool(page_data)
            pages_discovered = 1 if has_both else 0
            discovery_complete = has_both

        # Save enhanced Step 5 state and return pass
        response = cls.validate_and_pass(
            step=5,
            step_name="Discovered Elements",
            gate_name="qg_discovered_elements",
            state_data={
                "discovered_elements": elements,  # Keep for backward compatibility (last elements discovered)
                "page_name": page_name,  # Current page (backward compat)
                "discovered_pages": discovered_pages,  # Task 2.0 + DEF-045: Nested per-page tracking
                "pages_discovered": pages_discovered,  # Task 2.0 + DEF-045: Pages with BOTH types
                "total_pages": total_pages,  # Task 2.0: Total scope
                "discovery_complete": discovery_complete  # Task 2.0 + DEF-045: True if all pages have both types
            },
            metadata={
                "page_name": page_name,
                "elements_count": len(elements),
                "pages_discovered": pages_discovered,
                "total_pages": total_pages,
                "discovery_complete": discovery_complete
            },
            mode="POST"
        )

        # DD-44: Add multi-page progress info to response
        if total_pages > 1:
            response["multi_page_progress"] = {
                "pages_discovered": pages_discovered,
                "total_pages": total_pages,
                "discovery_complete": discovery_complete,
                "remaining_pages": total_pages - pages_discovered
            }
            if not discovery_complete:
                response["hint"] = f"Discovery in progress: {pages_discovered}/{total_pages} pages. Continue discovering remaining pages before proceeding to Step 6."

        return response

    @classmethod
    def _validate_element(cls, element: Any, index: int) -> Dict[str, Any] | None:
        """
        Validate a single element structure.

        Returns fail_response dict if invalid, None if valid.
        """
        if not isinstance(element, dict):
            return cls.fail_response(
                error=f"Element {index} is not a valid object",
                teach="Each element must be a dictionary with suggested_name, element_type, and locators."
            )

        # Check suggested_name
        suggested_name = element.get("suggested_name")
        if suggested_name is None:
            return cls.fail_response(
                error=f"Element {index} missing required field: suggested_name",
                teach="Each element must have a suggested_name."
            )

        if not isinstance(suggested_name, str) or not suggested_name.strip():
            return cls.fail_response(
                error=f"Element {index} suggested_name must be a non-empty string",
                teach="Provide a descriptive name like 'EMAIL_INPUT', 'SUBMIT_BUTTON'."
            )

        # Check element_type
        element_type = element.get("element_type")
        if element_type is None:
            return cls.fail_response(
                error=f"Element {index} missing required field: element_type",
                teach="Each element must have an element_type (e.g., 'textbox', 'button')."
            )

        if not isinstance(element_type, str) or not element_type.strip():
            return cls.fail_response(
                error=f"Element {index} element_type must be a non-empty string",
                teach="Provide element type like 'textbox', 'button', 'link'."
            )

        # Check locators (IC-05-03): at least one non-empty locator required
        locator_id = element.get("locator_id", "")
        locator_css = element.get("locator_css", "")
        locator_xpath = element.get("locator_xpath", "")

        # Check if at least one locator is non-empty
        has_valid_locator = (
            (isinstance(locator_id, str) and locator_id.strip()) or
            (isinstance(locator_css, str) and locator_css.strip()) or
            (isinstance(locator_xpath, str) and locator_xpath.strip())
        )

        if not has_valid_locator:
            return cls.fail_response(
                error=f"Element {index} has no valid locator (IC-05-03)",
                teach="At least one of locator_id, locator_css, or locator_xpath must be non-empty."
            )

        return None

    @classmethod
    def _validate_validation_results(cls, validation_results: Any) -> Dict[str, Any] | None:
        """
        DD-46: Validate validation_results structure from RuntimeValidator.

        Required structure:
        {
            "valid_count": int,
            "error_count": int,
            "elements": [
                {"name": str, "is_valid": bool, "error_category": str|None}
            ]
        }

        Returns:
            None if valid, fail_response dict if invalid
        """
        if not isinstance(validation_results, dict):
            return cls.fail_response(
                error="validation_results must be a dictionary (DD-46)",
                teach="validation_results should be dict with valid_count, error_count, elements"
            )

        # Check valid_count
        valid_count = validation_results.get("valid_count")
        if valid_count is None:
            return cls.fail_response(
                error="validation_results missing required field: valid_count (DD-46)",
                teach="Include valid_count (int) - number of elements that passed validation"
            )
        if not isinstance(valid_count, int):
            return cls.fail_response(
                error="validation_results.valid_count must be an integer (DD-46)",
                teach="valid_count should be count of valid elements"
            )

        # Check error_count
        error_count = validation_results.get("error_count")
        if error_count is None:
            return cls.fail_response(
                error="validation_results missing required field: error_count (DD-46)",
                teach="Include error_count (int) - number of elements that failed validation"
            )
        if not isinstance(error_count, int):
            return cls.fail_response(
                error="validation_results.error_count must be an integer (DD-46)",
                teach="error_count should be count of invalid elements"
            )

        # Check elements array
        elements = validation_results.get("elements")
        if elements is None:
            return cls.fail_response(
                error="validation_results missing required field: elements (DD-46)",
                teach="Include elements array with per-element validation status"
            )
        if not isinstance(elements, list):
            return cls.fail_response(
                error="validation_results.elements must be a list (DD-46)",
                teach="elements should be list of validation results per element"
            )

        # Validate each element result has required fields
        for i, elem_result in enumerate(elements):
            if not isinstance(elem_result, dict):
                return cls.fail_response(
                    error=f"validation_results.elements[{i}] must be a dictionary (DD-46)",
                    teach="Each element result should have name, is_valid, error_category"
                )

            if "name" not in elem_result:
                return cls.fail_response(
                    error=f"validation_results.elements[{i}] missing 'name' field (DD-46)",
                    teach="Each element result must include the element name"
                )

            if "is_valid" not in elem_result:
                return cls.fail_response(
                    error=f"validation_results.elements[{i}] missing 'is_valid' field (DD-46)",
                    teach="Each element result must include is_valid (bool)"
                )

        return None

    @classmethod
    def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation entry point.

        Routes to PRE or POST validation based on mode.

        Args:
            input_data: Dict with "mode" field ("PRE" or "POST") and relevant data

        Returns:
            Validation result
        """
        mode = input_data.get("mode", "").upper()

        if mode == "PRE":
            return cls.validate_pre(input_data)
        elif mode == "POST":
            return cls.validate_post(input_data)
        else:
            return cls.fail_response(
                error=f"Invalid mode: '{mode}'. Must be 'PRE' or 'POST'.",
                teach="Specify mode='PRE' for input validation or mode='POST' for output validation."
            )

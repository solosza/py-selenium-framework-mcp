"""
Quality Gate: Page Object (Step 6).

PRE+POST validation gate for Tool 3 (generate_page_object).

PRE Validation:
- Step 5 complete (discovered_elements, page_name exist in state)
- DD-44: If multi-page workflow, verify is_discovery_complete() == True
- discovered_elements present and not empty
- page_name present and PascalCase
- expected_states present (optional but recommended)

POST Validation:
- code field present and not empty
- metadata field present with required structure
- No skeleton code (DD-25): pass, # Add..., NotImplementedError, # TODO:
- No hardcoded URLs (DD-49): navigate_to must use self.web.config["url"]
- locators array present and not empty
- action_methods present and not empty when locators exist (IC-06-03)
- state_methods present and not empty
- state_methods match expected_states if provided (IC-06-01)
- class_name and import_path present (DD-26)
- WebInterface method calls are valid (Task 8.0)

Enforces: DD-09, DD-25, DD-26, DD-44, DD-49, IC-06-01, IC-06-02, IC-06-03
"""

import re
from typing import Any, Dict, List, Optional

from .base_gate import BaseGate
from utils.state_manager import StateManager
from utils.webinterface_checker import WebInterfaceChecker


class QGPageObject(BaseGate):
    """Quality gate for Step 6: Page Object Generation."""

    # PascalCase pattern (same as IC-05-02): starts with uppercase, alphanumeric
    PASCAL_CASE_PATTERN = re.compile(r'^[A-Z][a-zA-Z0-9]*$')

    # Skeleton code patterns (DD-25, IC-06-02)
    SKELETON_PATTERNS = [
        (r'^\s*pass\s*$', 'pass statement'),
        (r'#\s*[Aa]dd\s+.*\s+as\s+needed', 'placeholder comment'),
        (r'raise\s+NotImplementedError', 'NotImplementedError'),
        (r'#\s*TODO:', 'TODO comment'),
    ]

    # Layer violation patterns - POMs should NOT have these imports
    LAYER_VIOLATION_PATTERNS = [
        (r'from\s+tasks\.', 'Task import in POM'),
        (r'from\s+roles\.', 'Role import in POM'),
        (r'import\s+tasks\.', 'Task import in POM'),
        (r'import\s+roles\.', 'Role import in POM'),
    ]

    # Hardcoded URL patterns (DD-49) - POM navigate() must use self.web.config["url"]
    HARDCODED_URL_PATTERNS = [
        (r'navigate_to\s*\(\s*["\']https?://', 'navigate_to with hardcoded URL'),
        (r'navigate_to\s*\(\s*f?["\']https?://', 'navigate_to with hardcoded URL in f-string'),
    ]

    # Trivial state method pattern - returns True without checking element
    TRIVIAL_STATE_PATTERN = re.compile(
        r'def\s+(is_|has_)\w+\s*\([^)]*\)\s*->\s*bool:\s*\n\s*"""[^"]*"""\s*\n\s*return\s+True\s*$',
        re.MULTILINE
    )

    @classmethod
    def _get_state_manager(cls) -> StateManager:
        """Get StateManager instance. Extracted for testing."""
        # Task 15.0: Use per-run state isolation
        audit_logger = cls.get_audit_logger()
        return StateManager(run_id=audit_logger.run_id)

    @classmethod
    def _import_path_to_file_path(cls, import_path: str) -> str:
        """
        Convert Python import path to file system path.

        Task 15.0 (DEF-051): Helper for immediate file writes.
        Task 25.0 (DEF-055a FIX): Prepend framework/ for pages/tasks/roles paths.

        Args:
            import_path: e.g., "pages.auth.login_page"

        Returns:
            Absolute file path: e.g., "D:/project/framework/pages/auth/login_page.py"
        """
        import os
        from pathlib import Path

        # Convert dots to path separator
        relative_path = import_path.replace(".", os.sep) + ".py"

        # DEF-055a FIX: Prepend framework/ for pages/tasks/roles paths
        # These paths live under framework/ directory, not project root
        framework_prefixes = (
            'pages' + os.sep,
            'tasks' + os.sep,
            'roles' + os.sep,
        )
        if relative_path.startswith(framework_prefixes):
            relative_path = 'framework' + os.sep + relative_path

        # Get project root (3 levels up from mcp_server/tools/gates/)
        project_root = Path(__file__).parent.parent.parent.parent

        # Combine to get absolute path
        file_path = project_root / relative_path

        return str(file_path)

    @classmethod
    def _write_pom_file(cls, file_path: str, code: str) -> None:
        """
        Write POM code to disk immediately.

        Task 15.0 (DEF-051): Ensures multi-page POMs are all saved.

        Args:
            file_path: Absolute path to write file
            code: POM code content
        """
        import os
        from pathlib import Path

        # Ensure parent directory exists
        file_obj = Path(file_path)
        file_obj.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)

    @classmethod
    def validate_pre(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PRE validation before Tool 3 operation.

        Validates:
        - Step 5 is complete
        - discovered_elements present and not empty
        - page_name present and PascalCase
        - expected_states present (optional)

        Args:
            input_data: Dict with discovered_elements, page_name, expected_states

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
        """
        # Check Step 5 completion
        state_manager = cls._get_state_manager()
        if not state_manager.is_step_complete(5):
            return cls.fail_response(
                error="Step 5 is not complete. Cannot proceed to Step 6.",
                fix_hint="Complete Step 5 (Discover Elements) first. Ensure discovered_elements are generated."
            )

        # DD-44: For multi-page workflows, verify all pages are discovered
        step_5_state = state_manager.get_step(5) or {}
        total_pages = step_5_state.get("total_pages", 1)
        discovery_complete = step_5_state.get("discovery_complete", True)

        if total_pages > 1 and not discovery_complete:
            pages_discovered = step_5_state.get("pages_discovered", 0)
            discovered_pages = step_5_state.get("discovered_pages", {})
            discovered_names = list(discovered_pages.keys())

            return cls.fail_response(
                error=f"Multi-page discovery incomplete (DD-44): {pages_discovered}/{total_pages} pages discovered",
                fix_hint=f"Discover all pages before generating POMs. Discovered: {', '.join(discovered_names)}. Remaining: {total_pages - pages_discovered} pages."
            )

        # DEF-045: Support BOTH flat discovered_elements (backward compat) AND dual elements (new)
        # NEW structure (preferred): input_elements + output_elements
        # OLD structure (backward compat): discovered_elements (flat list)
        input_elements = input_data.get("input_elements")
        output_elements = input_data.get("output_elements")
        discovered_elements = input_data.get("discovered_elements")

        # Determine which structure is being used
        using_dual_elements = input_elements is not None or output_elements is not None

        if using_dual_elements:
            # NEW structure - validate both input and output elements
            if input_elements is None:
                return cls.fail_response(
                    error="Missing input_elements. Two-pass discovery requires both input and output elements.",
                    fix_hint="Run Step 5 PASS 1 (input discovery) before generating POM."
                )

            if output_elements is None:
                return cls.fail_response(
                    error="Missing output_elements. Two-pass discovery requires both input and output elements.",
                    fix_hint="Run Step 5 PASS 2 (output discovery) before generating POM."
                )

            if not isinstance(input_elements, list):
                return cls.fail_response(
                    error="input_elements must be a list",
                    fix_hint="Provide input_elements as an array from Step 5 PASS 1."
                )

            if not isinstance(output_elements, list):
                return cls.fail_response(
                    error="output_elements must be a list",
                    fix_hint="Provide output_elements as an array from Step 5 PASS 2."
                )

            # DEF-045: When using dual elements, BOTH types must have elements
            # (If using two-pass discovery, you should have discovered both types)
            if len(input_elements) == 0 or len(output_elements) == 0:
                missing = []
                if len(input_elements) == 0:
                    missing.append("input")
                if len(output_elements) == 0:
                    missing.append("output")

                return cls.fail_response(
                    error=f"Two-pass discovery requires both types. Missing: {', '.join(missing)} elements.",
                    fix_hint=f"Run Step 5 two-pass discovery:\n  - PASS 1 (input) if missing input elements\n  - PASS 2 (output) if missing output elements"
                )

        else:
            # OLD structure (backward compat) - validate flat discovered_elements
            if discovered_elements is None:
                return cls.fail_response(
                    error="Missing required field: discovered_elements",
                    fix_hint="Provide discovered_elements from Step 5 state."
                )

            if not isinstance(discovered_elements, list):
                return cls.fail_response(
                    error="discovered_elements must be a list",
                    fix_hint="Provide discovered_elements as an array from Tool 2 output."
                )

            if len(discovered_elements) == 0:
                return cls.fail_response(
                    error="discovered_elements is empty. At least one element required.",
                    fix_hint="Go back to Step 5 - ensure Tool 2 discovers elements."
                )

        # Validate page_name
        page_name = input_data.get("page_name")

        if page_name is None:
            return cls.fail_response(
                error="Missing required field: page_name",
                fix_hint="Provide page_name (e.g., 'LoginPage', 'CartPage')."
            )

        if not isinstance(page_name, str) or not page_name.strip():
            return cls.fail_response(
                error="page_name must be a non-empty string",
                fix_hint="Provide a descriptive page name like 'LoginPage'."
            )

        if not cls.PASCAL_CASE_PATTERN.match(page_name):
            return cls.fail_response(
                error=f"page_name '{page_name}' is not PascalCase",
                fix_hint="Use PascalCase format: 'LoginPage', 'CartModal', 'CheckoutForm'"
            )

        # expected_states is optional but recommended (don't fail if missing)

        return cls.pass_response(
            step=6,
            gate_name="qg_page_object",
            mode="PRE",
            metadata={
                "page_name": page_name,
                "elements_count": len(discovered_elements) if discovered_elements else 0
            }
        )

    # Step number for this gate (used for attempt tracking)
    STEP_NUMBER = 6

    @classmethod
    def validate_post(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST validation after Tool 3 operation.

        Validates:
        - code field present and not empty
        - No skeleton code (DD-25, IC-06-02)
        - metadata present with required structure (DD-26)
        - locators, action_methods, state_methods arrays valid
        - state_methods match expected_states if provided (IC-06-01)

        Args:
            input_data: Dict with code, metadata, expected_states

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
            or {"status": "blocked", ...} if max attempts exceeded
        """
        # Task 2.0: Check if blocked due to max attempts
        state_manager = cls._state_manager
        if state_manager:
            attempts = state_manager.get_attempt_count(cls.STEP_NUMBER)
            if attempts >= cls.MAX_ATTEMPTS:
                return cls.blocked_response(
                    step=cls.STEP_NUMBER,
                    attempts=attempts,
                    errors=[]  # Error history not tracked in simple impl
                )

        # Run actual validation
        result = cls._validate_post_internal(input_data)

        # Task 2.5: Extract source from input_data
        source = input_data.get("source")

        # Task 2.0: Track attempts and log to audit
        if state_manager:
            if result.get("status") == "fail":
                state_manager.increment_attempt(cls.STEP_NUMBER)
                # DEF-040: Log failure to audit (lazy init)
                cls.get_audit_logger().log_gate(
                    step=cls.STEP_NUMBER,
                    gate_name="qg_page_object",
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
                    gate_name="qg_page_object",
                    mode="POST",
                    result="pass",
                    source=source
                )

        return result

    @classmethod
    def _validate_post_internal(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal validation logic (separated for attempt tracking)."""
        # Validate code field
        code = input_data.get("code")

        if code is None:
            return cls.fail_response(
                error="Missing required field: code",
                fix_hint="Tool 3 must return generated POM code."
            )

        if not isinstance(code, str) or not code.strip():
            return cls.fail_response(
                error="code is empty",
                fix_hint="Tool 3 must generate non-empty POM code."
            )

        # Check for skeleton code (DD-25, IC-06-02)
        skeleton_error = cls._detect_skeleton_code(code)
        if skeleton_error:
            return skeleton_error

        # Check for layer violations (POM should not import Task/Role)
        layer_error = cls._detect_layer_violations(code)
        if layer_error:
            return layer_error

        # Check for hardcoded URLs (DD-49)
        url_error = cls._detect_hardcoded_urls(code)
        if url_error:
            return url_error

        # Check for trivial state methods (skeleton variant)
        trivial_error = cls._detect_trivial_state_methods(code)
        if trivial_error:
            return trivial_error

        # Validate metadata field
        metadata = input_data.get("metadata")

        if metadata is None:
            return cls.fail_response(
                error="Missing required field: metadata",
                fix_hint="Tool 3 must return metadata for downstream tools."
            )

        if not isinstance(metadata, dict):
            return cls.fail_response(
                error="metadata must be a dictionary",
                fix_hint="Tool 3 should return metadata as an object."
            )

        # Validate metadata structure (DD-26)
        metadata_error = cls._validate_metadata_structure(metadata)
        if metadata_error:
            return metadata_error

        # Validate locators
        locators_error = cls._validate_locators(metadata)
        if locators_error:
            return locators_error

        # Validate action_methods (IC-06-03)
        action_error = cls._validate_action_methods(metadata)
        if action_error:
            return action_error

        # Validate state_methods (DD-09)
        state_error = cls._validate_state_methods(metadata)
        if state_error:
            return state_error

        # Validate state_methods match expected_states (IC-06-01)
        expected_states = input_data.get("expected_states")
        if expected_states:
            match_error = cls._validate_state_methods_match(metadata, expected_states)
            if match_error:
                return match_error

        # Task 8.0: Validate WebInterface method calls are valid
        webinterface_error = cls._validate_webinterface_methods(code)
        if webinterface_error:
            return webinterface_error

        # DEF-048: Enforce navigate() method requirement (DD-49 compliance)
        navigate_error = cls._validate_navigate_method(code, metadata)
        if navigate_error:
            return navigate_error

        # Task 8.5.9: Multi-page POM generation tracking
        internal_state_manager = cls._get_state_manager()

        # Get page_name from input (required for multi-page tracking)
        page_name = input_data.get("page_name")
        if not page_name:
            # Fallback to metadata class_name
            page_name = metadata.get("class_name", "UnknownPage")

        # Load existing Step 6 state to preserve per-page tracking
        existing_state = internal_state_manager.get_step(6) or {}
        generated_poms = existing_state.get("generated_poms", {})

        # Add/update this page's POM
        generated_poms[page_name] = {
            "code": code,
            "metadata": metadata
        }

        # Get total_pages from Step 5 state
        step_5_state = internal_state_manager.get_step(5) or {}
        total_pages = step_5_state.get("total_pages", 1)

        # Calculate generation progress
        poms_generated = len(generated_poms)
        generation_complete = poms_generated >= total_pages

        # Save enhanced Step 6 state
        internal_state_manager.save(step=6, data={
            "pom_code": code,  # Keep for backward compatibility
            "pom_metadata": metadata,  # Keep for backward compatibility
            "generated_poms": generated_poms,  # Task 8.5.9: Per-page tracking
            "poms_generated": poms_generated,  # Task 8.5.9: Progress tracking
            "total_poms": total_pages,  # Task 8.5.9: Total scope (from Step 5)
            "generation_complete": generation_complete  # Task 8.5.9: Completion flag
        })

        # Task 15.0 (DEF-051 FIX): Write POM file immediately to disk
        import_path = metadata.get("import_path")
        if import_path:
            file_path = cls._import_path_to_file_path(import_path)
            try:
                # Write file to disk
                cls._write_pom_file(file_path, code)

                # Log file write to audit trail
                audit_logger = cls.get_audit_logger()
                audit_logger.log_file_generated(file_path, step=6)
            except Exception as e:
                # DEF-055b FIX: Log file write failure instead of silently swallowing
                # Don't block (validation already passed) but DO log the error
                audit_logger = cls.get_audit_logger()
                audit_logger.log_gate(
                    step=6,
                    gate_name="qg_page_object",
                    mode="POST",
                    result="warning",
                    error=f"FILE_WRITE_FAILED: {file_path} - {str(e)}"
                )

        # Task 8.5.9: For multi-page workflows, return progress info
        audit_metadata = {
            "page_name": page_name,
            "class_name": metadata.get("class_name"),
            "import_path": metadata.get("import_path"),
            "action_methods_count": len(metadata.get("action_methods", [])),
            "state_methods_count": len(metadata.get("state_methods", []))
        }

        # Add multi-page progress to audit metadata
        if total_pages > 1:
            audit_metadata["multi_page"] = {
                "poms_generated": poms_generated,
                "total_poms": total_pages,
                "generation_complete": generation_complete,
                "page_index": poms_generated  # Which page is this in the sequence
            }

        response = cls.pass_response(
            step=6,
            gate_name="qg_page_object",
            mode="POST",
            metadata=audit_metadata
        )
        if total_pages > 1:
            response["multi_page_progress"] = {
                "poms_generated": poms_generated,
                "total_poms": total_pages,
                "generation_complete": generation_complete,
                "remaining_poms": total_pages - poms_generated
            }
            if not generation_complete:
                response["hint"] = f"POM generation in progress: {poms_generated}/{total_pages} POMs. Continue generating remaining POMs before proceeding to Step 7."

        return response

    @classmethod
    def _detect_skeleton_code(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect skeleton code patterns in generated code.

        Returns fail_response if skeleton detected, None otherwise.
        """
        for pattern, description in cls.SKELETON_PATTERNS:
            if re.search(pattern, code, re.MULTILINE):
                return cls.fail_response(
                    error=f"Skeleton code detected: {description}",
                    fix_hint="AI must complete the code. Remove placeholders, implement all methods."
                )
        return None

    @classmethod
    def _detect_layer_violations(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect layer violation patterns - POM should not import Task/Role.

        Returns fail_response if violation detected, None otherwise.
        """
        for pattern, description in cls.LAYER_VIOLATION_PATTERNS:
            if re.search(pattern, code):
                return cls.fail_response(
                    error=f"Layer violation detected: {description} (architecture violation)",
                    fix_hint="POMs should only import WebInterface. Tasks and Roles are higher layers that use POMs, not the other way around."
                )
        return None

    @classmethod
    def _detect_hardcoded_urls(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect hardcoded URLs in navigate_to calls (DD-49).

        POM navigate() methods must use self.web.config["url"] for base URL,
        not hardcoded http:// or https:// strings.

        Returns fail_response if hardcoded URL detected, None otherwise.
        """
        for pattern, description in cls.HARDCODED_URL_PATTERNS:
            if re.search(pattern, code):
                return cls.fail_response(
                    error=f"Hardcoded URL detected: {description}",
                    fix_hint="POM navigate() must use self.web.config['url'] for base URL. Example: self.web.navigate_to(f\"{self.web.config['url']}/page.htm\")"
                )
        return None

    @classmethod
    def _detect_trivial_state_methods(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect trivial state methods that just return True without element check.

        A proper state method should check an actual element, not just return True.

        Returns fail_response if trivial state method detected, None otherwise.
        """
        if cls.TRIVIAL_STATE_PATTERN.search(code):
            return cls.fail_response(
                error="Trivial state method detected: returns True without checking element",
                fix_hint="State methods must check actual elements. Replace 'return True' with 'return self.web.is_element_displayed(*self.LOCATOR)'."
            )
        return None

    @classmethod
    def _validate_metadata_structure(cls, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate metadata has required fields (DD-26).

        Returns fail_response if invalid, None otherwise.
        """
        # Check class_name
        class_name = metadata.get("class_name")
        if class_name is None or not isinstance(class_name, str) or not class_name.strip():
            return cls.fail_response(
                error="Missing or invalid class_name in metadata",
                fix_hint="Tool 3 must include class_name in metadata."
            )

        # Check import_path
        import_path = metadata.get("import_path")
        if import_path is None or not isinstance(import_path, str) or not import_path.strip():
            return cls.fail_response(
                error="Missing or invalid import_path in metadata",
                fix_hint="Tool 3 must include import_path in metadata."
            )

        return None

    @classmethod
    def _validate_locators(cls, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate locators array in metadata.

        Returns fail_response if invalid, None otherwise.
        """
        locators = metadata.get("locators")

        if locators is None:
            return cls.fail_response(
                error="Missing locators in metadata",
                fix_hint="Tool 3 must include locators array in metadata."
            )

        if not isinstance(locators, list):
            return cls.fail_response(
                error="locators must be a list",
                fix_hint="Tool 3 should return locators as an array."
            )

        if len(locators) == 0:
            return cls.fail_response(
                error="locators is empty. At least one locator required.",
                fix_hint="Check that discovered_elements were processed correctly."
            )

        return None

    @classmethod
    def _validate_action_methods(cls, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate action_methods array in metadata (IC-06-03).

        Returns fail_response if invalid, None otherwise.
        """
        action_methods = metadata.get("action_methods")

        if action_methods is None:
            return cls.fail_response(
                error="Missing action_methods in metadata",
                fix_hint="Tool 3 must include action_methods array in metadata."
            )

        if not isinstance(action_methods, list):
            return cls.fail_response(
                error="action_methods must be a list",
                fix_hint="Tool 3 should return action_methods as an array."
            )

        # IC-06-03: If locators exist but action_methods is empty, it's a data quality issue
        locators = metadata.get("locators", [])
        if len(locators) > 0 and len(action_methods) == 0:
            return cls.fail_response(
                error="action_methods is empty but locators exist (IC-06-03 violation)",
                fix_hint="Element types from Tool 2 may be missing/invalid. Check element_type values."
            )

        # DEF-057: Validate param format (string, not dict) for each action_method
        for method in action_methods:
            method_name = method.get("name", "<unknown>")
            params = method.get("params", [])

            # Validate params are string format per DEF-054 standard
            param_error = cls._validate_param_format(
                params,
                context=f"action_method '{method_name}'"
            )
            if param_error:
                return param_error

        return None

    @classmethod
    def _validate_state_methods(cls, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate state_methods array in metadata (DD-09).

        Returns fail_response if invalid, None otherwise.
        """
        state_methods = metadata.get("state_methods")

        if state_methods is None:
            return cls.fail_response(
                error="Missing state_methods in metadata",
                fix_hint="Tool 3 must include state_methods array in metadata."
            )

        if not isinstance(state_methods, list):
            return cls.fail_response(
                error="state_methods must be a list",
                fix_hint="Tool 3 should return state_methods as an array."
            )

        if len(state_methods) == 0:
            return cls.fail_response(
                error="state_methods is empty. At least one state-check method required.",
                fix_hint="Provide expected_states from Step 3 to generate state-check methods."
            )

        return None

    @classmethod
    def _validate_state_methods_match(
        cls,
        metadata: Dict[str, Any],
        expected_states: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Validate state_methods match expected_states (IC-06-01).

        Each expected_state must have a corresponding state_method.

        Returns fail_response if mismatch, None otherwise.
        """
        state_methods = metadata.get("state_methods", [])
        state_method_names = {m.get("name") for m in state_methods if isinstance(m, dict)}

        missing_methods = []
        for expected in expected_states:
            if isinstance(expected, dict):
                expected_name = expected.get("name")
                if expected_name and expected_name not in state_method_names:
                    missing_methods.append(expected_name)

        if missing_methods:
            return cls.fail_response(
                error=f"state_methods missing for expected_states: {', '.join(missing_methods)} (IC-06-01 violation)",
                fix_hint="Ensure Tool 3 receives expected_states and generates matching state-check methods."
            )

        return None

    @classmethod
    def _validate_navigate_method(cls, code: str, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        DEF-048: Enforce navigate() method requirement (DD-49 compliance).

        All POMs must:
        1. Have a navigate() method in action_methods
        2. Only call self.web.navigate_to() inside navigate() method

        Returns fail_response if invalid, None otherwise.
        """
        action_methods = metadata.get("action_methods", [])
        action_method_names = [m.get("name") for m in action_methods if isinstance(m, dict)]

        # Check 1: Must have navigate() method
        if "navigate" not in action_method_names:
            class_name = metadata.get("class_name", "UnknownPage")
            return cls.fail_response(
                error="POM missing navigate() method (DD-49 violation)",
                fix_hint=f"""
All POMs must have navigate() method for DD-49 compliance.

Pattern:
def navigate(self) -> "{class_name}":
    '''Navigate to this page.'''
    self.web.navigate_to(self.web.config['url'] + '/relative/path')
    return self

Example for LoginPage:
def navigate(self) -> "LoginPage":
    '''Navigate to login page.'''
    self.web.navigate_to(self.web.config['url'] + '/parabank/index.htm')
    return self

Fix: Add navigate() method to the POM.
                """
            )

        # Check 2: navigate_to() should ONLY be in navigate() method
        # Extract navigate() method body
        navigate_method_pattern = re.compile(r'def navigate\(self\).*?(?=\n    def |\n\nclass |\Z)', re.DOTALL)
        navigate_method_match = navigate_method_pattern.search(code)

        if not navigate_method_match:
            # This shouldn't happen since we already checked navigate exists in metadata
            # But if code structure is wrong, fail
            return cls.fail_response(
                error="navigate() method declared in metadata but not found in code",
                fix_hint="Ensure navigate() method exists in the POM code."
            )

        navigate_method_body = navigate_method_match.group(0)

        # Check if navigate_to() appears in code
        if "self.web.navigate_to(" in code:
            # It should ONLY appear in navigate() method body
            code_outside_navigate = code.replace(navigate_method_body, "")
            if "self.web.navigate_to(" in code_outside_navigate:
                return cls.fail_response(
                    error="self.web.navigate_to() found outside navigate() method (DD-49 violation)",
                    fix_hint="""
DD-49: Tasks/Roles must NOT call self.web.navigate_to() directly.
POMs must provide navigate() method for navigation.

Pattern violation detected:
- self.web.navigate_to() found in action method (not navigate())

Fix: Remove direct navigate_to() calls from action methods.
Navigation should ONLY be in navigate() method.
                    """
                )

        return None

    # WebInterface method call pattern: self.web.<method_name>(
    WEBINTERFACE_CALL_PATTERN = re.compile(r'self\.web\.(\w+)\s*\(')

    @classmethod
    def _validate_webinterface_methods(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Task 8.0: Validate WebInterface method calls in POM code.

        Extracts all self.web.<method>() calls and validates each method
        exists in WebInterface. Provides suggestions for typos.

        Returns fail_response if invalid method found, None otherwise.
        """
        # Extract all WebInterface method calls
        method_calls = cls.WEBINTERFACE_CALL_PATTERN.findall(code)

        if not method_calls:
            # No WebInterface calls found - this might be valid for state-only POMs
            return None

        # Create checker instance (lazy load)
        checker = WebInterfaceChecker()

        # Track invalid methods
        invalid_methods = []

        for method_name in set(method_calls):  # Use set to avoid duplicate checks
            result = checker.validate_method_call(method_name)

            if not result.get("valid"):
                suggestion = ""
                similar = result.get("similar_methods", [])
                if similar:
                    suggestion = f" Did you mean: {', '.join(similar)}?"

                invalid_methods.append({
                    "method": method_name,
                    "reason": result.get("reason", "Unknown error"),
                    "suggestion": suggestion
                })

        if invalid_methods:
            # Format error message
            error_details = "; ".join(
                f"'{m['method']}' - {m['reason']}{m['suggestion']}"
                for m in invalid_methods
            )
            return cls.fail_response(
                error=f"Invalid WebInterface method(s) in POM: {error_details}",
                fix_hint="Use valid WebInterface methods. Check mcp_server/utils/webinterface_checker.py for available methods."
            )

        return None

    @classmethod
    def is_generation_complete(cls) -> bool:
        """
        Task 8.5.9: Check if all POMs are generated (for multi-page workflows).

        Returns:
            True if generation_complete flag is True or total_poms <= poms_generated
        """
        state_manager = cls._get_state_manager()
        step_6_state = state_manager.get_step(6) or {}
        return step_6_state.get("generation_complete", False)

    @classmethod
    def get_generation_progress(cls) -> Dict[str, Any]:
        """
        Task 8.5.9: Get current POM generation progress.

        Returns:
            Dict with poms_generated, total_poms, generation_complete, generated_pages
        """
        state_manager = cls._get_state_manager()
        step_6_state = state_manager.get_step(6) or {}
        generated_poms = step_6_state.get("generated_poms", {})

        return {
            "poms_generated": step_6_state.get("poms_generated", 0),
            "total_poms": step_6_state.get("total_poms", 1),
            "generation_complete": step_6_state.get("generation_complete", False),
            "generated_pages": list(generated_poms.keys())
        }

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
                fix_hint="Specify mode='PRE' for input validation or mode='POST' for output validation."
            )

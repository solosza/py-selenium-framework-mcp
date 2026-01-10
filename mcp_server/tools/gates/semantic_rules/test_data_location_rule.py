"""
FR-14.3: Test Data Location Enforcement

Validates that test data imports match the test_data_location chosen in Step 1.

Strategies:
- shared: Test imports from tests/data/ (cross-workflow data)
- workflow: Test imports from tests/{workflow}/data/ (workflow-specific data)
- both: Both patterns allowed
- none: No test data imports expected
"""

import re
from typing import Dict, Any, Optional, List
from .base import SemanticRule


class TestDataLocationRule(SemanticRule):
    """
    Validates that test data imports match test_data_location from Step 1.

    Enforces consistency between Step 1 strategy choice and
    actual test data import patterns.
    """

    @property
    def name(self) -> str:
        return "test_data_location"

    @property
    def description(self) -> str:
        return (
            "Validates that test data imports match test_data_location from Step 1 "
            "(shared, workflow, both, none)"
        )

    def check(self, code: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check test code against test_data_location from Step 1.

        Args:
            code: Generated test code (from Tool 6)
            context: Must contain step_1_config with test_data_location

        Returns:
            NEEDS_RETRY response if location mismatch, None if valid
        """
        # Extract Step 1 config
        step_1_config = context.get("step_1_config", {})
        test_data_location = step_1_config.get("test_data_location", "")

        # If no strategy specified, skip validation
        if not test_data_location:
            return None

        # Normalize strategy
        strategy = test_data_location.lower().strip()

        # Extract test data imports from code
        data_imports = self._extract_data_imports(code)

        # If no data imports found, strategy must be 'none'
        if not data_imports:
            if strategy == "none":
                return None  # Valid - no imports expected
            # Otherwise, skip validation (test might not need data despite strategy)
            return None

        # Validate based on strategy
        if strategy == "shared":
            return self._validate_shared(data_imports)
        elif strategy == "workflow":
            return self._validate_workflow(data_imports, context)
        elif strategy == "both":
            return self._validate_both(data_imports, context)
        elif strategy == "none":
            return self._validate_none(data_imports)
        else:
            # Unknown strategy - skip validation
            return None

    def _extract_data_imports(self, code: str) -> List[Dict[str, str]]:
        """
        Extract data-related imports from test code.

        Returns:
            List of dicts: [{"import_path": "tests.data.products", "module": "products"}, ...]
        """
        imports = []

        # Pattern: from tests.X.data import Y or from tests.data import Y
        # Also: import tests.X.data.Y
        import_patterns = [
            r'from\s+(tests\.[\w.]*\.data[\w.]*)\s+import\s+(\w+)',  # from tests.X.data import Y
            r'from\s+(tests\.data[\w.]*)\s+import\s+(\w+)',           # from tests.data import Y
            r'import\s+(tests\.[\w.]*\.data[\w.]*)',                  # import tests.X.data.Y
            r'import\s+(tests\.data[\w.]*)',                          # import tests.data.Y
        ]

        for pattern in import_patterns:
            for match in re.finditer(pattern, code):
                import_path = match.group(1)
                module = match.group(2) if len(match.groups()) > 1 else import_path.split('.')[-1]

                imports.append({
                    "import_path": import_path,
                    "module": module
                })

        return imports

    def _validate_shared(self, data_imports: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """
        Validate shared strategy.

        Expected: imports from tests.data
        Not expected: imports from tests.{workflow}.data
        """
        for imp in data_imports:
            import_path = imp["import_path"]

            # Check for workflow-specific pattern: tests.{workflow}.data
            # Pattern: tests.X.data where X is not just "data"
            if re.match(r'tests\.\w+\.data', import_path) and not import_path.startswith('tests.data.'):
                # Extract workflow from path (e.g., "parabank" from "tests.parabank.data")
                workflow = import_path.split('.')[1]

                return {
                    "status": "NEEDS_RETRY",
                    "fix_applied": "test_data_location_corrected",
                    "error": (
                        f"Test data location mismatch: imports from 'tests.{workflow}.data' "
                        f"but Step 1 specified 'shared'"
                    ),
                    "message": (
                        f"Update import to shared location. "
                        f"Change: from tests.{workflow}.data import {imp['module']}\n"
                        f"To: from tests.data import {imp['module']}"
                    )
                }

        return None

    def _validate_workflow(
        self,
        data_imports: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Validate workflow strategy.

        Expected: imports from tests.{workflow}.data
        Not expected: imports from tests.data (shared)
        """
        # Try to determine workflow from context
        # Workflow might be in test_scenarios or role_metadata
        workflow = self._extract_workflow(context)

        for imp in data_imports:
            import_path = imp["import_path"]

            # Check for shared pattern: tests.data (not tests.X.data)
            if import_path == "tests.data" or import_path.startswith("tests.data."):
                return {
                    "status": "NEEDS_RETRY",
                    "fix_applied": "test_data_location_corrected",
                    "error": (
                        "Test data location mismatch: imports from 'tests.data' "
                        "but Step 1 specified 'workflow-specific'"
                    ),
                    "message": (
                        f"Update import to workflow-specific location. "
                        f"Change: from tests.data import {imp['module']}\n"
                        f"To: from tests.{workflow}.data import {imp['module']}"
                        if workflow else
                        f"Update import to workflow-specific location (tests.{{workflow}}.data)"
                    )
                }

        return None

    def _validate_both(
        self,
        data_imports: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Validate both strategy.

        Expected: Any combination of tests.data or tests.{workflow}.data is valid
        """
        # Both patterns are valid - no validation needed
        return None

    def _validate_none(self, data_imports: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """
        Validate none strategy.

        Expected: No test data imports
        """
        if data_imports:
            import_examples = ", ".join([imp["import_path"] for imp in data_imports[:3]])
            return {
                "status": "NEEDS_RETRY",
                "fix_applied": "test_data_imports_removed",
                "error": (
                    f"Test data location mismatch: test imports data ({import_examples}) "
                    "but Step 1 specified 'none'"
                ),
                "message": (
                    "Remove test data imports. Step 1 specified no test data needed. "
                    "If test requires data, update Step 1 strategy."
                )
            }

        return None

    def _extract_workflow(self, context: Dict[str, Any]) -> str:
        """
        Extract workflow name from context.

        Tries multiple sources:
        1. test_scenarios metadata
        2. role_metadata
        3. pom_metadata
        4. Default to "workflow"
        """
        # Try test_scenarios
        test_scenarios = context.get("test_scenarios", [])
        if test_scenarios and isinstance(test_scenarios, list) and len(test_scenarios) > 0:
            scenario = test_scenarios[0]
            if isinstance(scenario, dict):
                workflow = scenario.get("workflow")
                if workflow:
                    return workflow

        # Try role_metadata
        role_metadata = context.get("role_metadata", {})
        if isinstance(role_metadata, dict):
            workflow = role_metadata.get("workflow")
            if workflow:
                return workflow

        # Try pom_metadata
        pom_metadata = context.get("pom_metadata", {})
        if isinstance(pom_metadata, dict):
            workflow = pom_metadata.get("workflow")
            if workflow:
                return workflow

        # Default fallback
        return "workflow"

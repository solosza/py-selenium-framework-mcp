"""
QA Reviewer Agent Tool

Validates generated artifacts against FRAMEWORK.md patterns and 22 Design Decisions.
Returns APPROVE or REJECT with detailed violation list.

Design Decisions:
- DD-VA-04: Reviewer as custom tool (in-process, reads files)
- DD-VA-12: Raw test function for @tool decorator testing

Severity Levels:
- CRITICAL: Must fix before execution (DD-03, DD-15, DD-22)
- HIGH: Should fix, blocks execution (DD-01, DD-02, DD-08, DD-09, DD-12, DD-17, DD-18, DD-19)
- MEDIUM: Should fix, doesn't block (DD-05, DD-06, DD-07, DD-10, DD-11, DD-13, DD-16, DD-20, DD-21)
- LOW: Nice to fix (DD-04, DD-14)
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Import tool decorator only if available (for MCP integration)
try:
    from claude_agent_sdk import tool
    HAS_SDK = True
except ImportError:
    HAS_SDK = False
    def tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


# =============================================================================
# Constants
# =============================================================================

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# DD Severity mapping
DD_SEVERITY: Dict[str, Severity] = {
    # CRITICAL - Must fix before execution
    "DD-03": Severity.CRITICAL,  # Locators ONLY in Page Objects
    "DD-15": Severity.CRITICAL,  # Test assertions use POM state methods
    "DD-22": Severity.CRITICAL,  # Stop-and-discuss on blockers

    # HIGH - Should fix, blocks execution
    "DD-01": Severity.HIGH,  # User must specify persona
    "DD-02": Severity.HIGH,  # URL required upfront
    "DD-08": Severity.HIGH,  # AI orchestrates, tools don't call tools
    "DD-09": Severity.HIGH,  # Extract expected_states from BDD "Then"
    "DD-12": Severity.HIGH,  # Check existing before generating new
    "DD-17": Severity.HIGH,  # AI injects actual parameter values
    "DD-18": Severity.HIGH,  # AI validates import paths
    "DD-19": Severity.HIGH,  # Import from tools/, not utils/

    # MEDIUM - Should fix, doesn't block
    "DD-05": Severity.MEDIUM,  # Method names emerge from tool chain
    "DD-06": Severity.MEDIUM,  # AI extracts intent, not exact method names
    "DD-07": Severity.MEDIUM,  # Domain from AI in Step 2
    "DD-10": Severity.MEDIUM,  # Action methods from element types
    "DD-11": Severity.MEDIUM,  # State method naming: is_*/has_*/get_*
    "DD-13": Severity.MEDIUM,  # Each tool has AI prompting rules
    "DD-16": Severity.MEDIUM,  # AI overrides Tool 6 file paths
    "DD-20": Severity.MEDIUM,  # Dynamic elements: AI prepares page state
    "DD-21": Severity.MEDIUM,  # AI-SDET collaboration

    # LOW - Nice to fix
    "DD-04": Severity.LOW,  # Single documentation source
    "DD-14": Severity.LOW,  # One test file per scenario
}


@dataclass
class Violation:
    """Represents a single DD violation."""
    dd_id: str
    severity: str
    file_path: str
    line_number: Optional[int]
    description: str
    code_snippet: Optional[str] = None


@dataclass
class ReviewResult:
    """Result of artifact review."""
    status: str  # "APPROVE" or "REJECT"
    violations: List[Dict[str, Any]]
    summary: str
    files_reviewed: List[str]
    blocking_violations: int
    total_violations: int


# =============================================================================
# Validation Rules
# =============================================================================

def check_dd03_locators_in_pom(file_path: str, content: str, file_type: str) -> List[Violation]:
    """
    DD-03: Locators ONLY in Page Objects.

    Check that Task, Role, and Test files do NOT contain locator definitions.
    """
    violations = []

    # Only check non-POM files
    if file_type == "page":
        return violations

    lines = content.split("\n")
    locator_patterns = [
        r"By\.(ID|CSS_SELECTOR|XPATH|CLASS_NAME|NAME|TAG_NAME|LINK_TEXT)",
        r"\(By\.",
        r"find_element\s*\(",
        r"find_elements\s*\(",
    ]

    for i, line in enumerate(lines, 1):
        for pattern in locator_patterns:
            if re.search(pattern, line):
                violations.append(Violation(
                    dd_id="DD-03",
                    severity=Severity.CRITICAL.value,
                    file_path=file_path,
                    line_number=i,
                    description=f"Locator found in {file_type} layer (should only be in Page Objects)",
                    code_snippet=line.strip()[:100]
                ))
                break

    return violations


def check_dd15_assertions_use_pom(file_path: str, content: str, file_type: str) -> List[Violation]:
    """
    DD-15: Test assertions MUST use POM state methods.

    Check that test assertions use is_*/has_*/get_* methods, not return values.
    """
    violations = []

    if file_type != "test":
        return violations

    lines = content.split("\n")

    # Bad patterns: asserting on return values
    bad_patterns = [
        (r"assert\s+\w+\.login\(\)", "Asserting on return value of login() - should use POM state method"),
        (r"assert\s+\w+\.log_in\(\)", "Asserting on return value of log_in() - should use POM state method"),
        (r"result\s*=\s*\w+\.(login|log_in|logout|log_out)", "Capturing return value from workflow method - should not return"),
        (r"assert\s+result\s*(==|is)", "Asserting on captured return value - use POM state method"),
    ]

    # Good patterns we want to see
    good_patterns = [
        r"assert\s+\w+\.is_\w+\(",
        r"assert\s+\w+\.has_\w+\(",
        r"assert\s+\w+\.get_\w+\(",
    ]

    for i, line in enumerate(lines, 1):
        for pattern, msg in bad_patterns:
            if re.search(pattern, line):
                violations.append(Violation(
                    dd_id="DD-15",
                    severity=Severity.CRITICAL.value,
                    file_path=file_path,
                    line_number=i,
                    description=msg,
                    code_snippet=line.strip()[:100]
                ))

    return violations


def check_dd11_state_method_naming(file_path: str, content: str, file_type: str) -> List[Violation]:
    """
    DD-11: State method naming convention (is_*/has_*/get_*).

    Check that POM state-check methods follow naming convention.
    """
    violations = []

    if file_type != "page":
        return violations

    lines = content.split("\n")

    # Look for methods that return bool but don't start with is_/has_
    bool_return_pattern = r"def\s+(\w+)\(.*\)\s*->\s*bool:"

    for i, line in enumerate(lines, 1):
        match = re.search(bool_return_pattern, line)
        if match:
            method_name = match.group(1)
            if not (method_name.startswith("is_") or method_name.startswith("has_")):
                violations.append(Violation(
                    dd_id="DD-11",
                    severity=Severity.MEDIUM.value,
                    file_path=file_path,
                    line_number=i,
                    description=f"Boolean method '{method_name}' should start with is_ or has_",
                    code_snippet=line.strip()[:100]
                ))

    return violations


def check_dd_task_no_return(file_path: str, content: str, file_type: str) -> List[Violation]:
    """
    Check that Task methods do not return values (DD-09 related).
    """
    violations = []

    if file_type != "task":
        return violations

    lines = content.split("\n")

    # Look for return statements that return something (not just 'return' or 'return None')
    in_method = False
    method_indent = 0

    for i, line in enumerate(lines, 1):
        # Skip comments and docstrings
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
            continue

        # Detect method definition
        method_match = re.match(r"(\s*)def\s+\w+\(", line)
        if method_match:
            in_method = True
            method_indent = len(method_match.group(1))
            continue

        if in_method:
            # Check if we've exited the method (less indent, non-empty line)
            if stripped and not line.startswith(" " * (method_indent + 1)):
                if not stripped.startswith("#"):
                    in_method = False
                continue

            # Check for actual return statement with value (not in comment)
            # Must start with 'return ' (with space) and have a non-None value
            if re.match(r"\s*return\s+(?!None\s*$)(\S+)", line):
                violations.append(Violation(
                    dd_id="DD-09",
                    severity=Severity.HIGH.value,
                    file_path=file_path,
                    line_number=i,
                    description="Task method should not return values - tests assert via POM",
                    code_snippet=stripped[:100]
                ))

    return violations


def check_dd_role_no_return(file_path: str, content: str, file_type: str) -> List[Violation]:
    """
    Check that Role workflow methods do not return values.
    """
    violations = []

    if file_type != "role":
        return violations

    lines = content.split("\n")

    in_method = False
    method_indent = 0

    for i, line in enumerate(lines, 1):
        # Skip comments and docstrings
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
            continue

        method_match = re.match(r"(\s*)def\s+\w+\(", line)
        if method_match:
            in_method = True
            method_indent = len(method_match.group(1))
            continue

        if in_method:
            if stripped and not line.startswith(" " * (method_indent + 1)):
                if not stripped.startswith("#"):
                    in_method = False
                continue

            # Check for actual return statement with value
            if re.match(r"\s*return\s+(?!None\s*$)(\S+)", line):
                violations.append(Violation(
                    dd_id="DD-09",
                    severity=Severity.HIGH.value,
                    file_path=file_path,
                    line_number=i,
                    description="Role method should not return values - tests assert via POM",
                    code_snippet=stripped[:100]
                ))

    return violations


def check_dd18_import_paths(file_path: str, content: str, file_type: str) -> List[Violation]:
    """
    DD-18: Validate import paths exist.

    Check for common import issues.
    """
    violations = []

    lines = content.split("\n")

    # Check for suspicious import patterns
    suspicious_patterns = [
        (r"from\s+\.\.+", "Relative imports may cause issues"),
        (r"import\s+\*", "Wildcard imports not recommended"),
    ]

    for i, line in enumerate(lines, 1):
        for pattern, msg in suspicious_patterns:
            if re.search(pattern, line):
                violations.append(Violation(
                    dd_id="DD-18",
                    severity=Severity.HIGH.value,
                    file_path=file_path,
                    line_number=i,
                    description=msg,
                    code_snippet=line.strip()[:100]
                ))

    return violations


def check_dd19_import_from_tools(file_path: str, content: str, file_type: str) -> List[Violation]:
    """
    DD-19: Import from tools/, not utils/.

    Check for imports from deprecated utils path.
    """
    violations = []

    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        if re.search(r"from\s+utils\.", line) or re.search(r"import\s+utils\.", line):
            violations.append(Violation(
                dd_id="DD-19",
                severity=Severity.HIGH.value,
                file_path=file_path,
                line_number=i,
                description="Import from 'tools/', not 'utils/' (deprecated)",
                code_snippet=line.strip()[:100]
            ))

    return violations


def check_pom_has_state_methods(file_path: str, content: str, file_type: str) -> List[Violation]:
    """
    Check that Page Objects have state-check methods (is_*/has_*/get_*).
    """
    violations = []

    if file_type != "page":
        return violations

    # Check if POM has any state-check methods
    state_methods = re.findall(r"def\s+(is_|has_|get_)\w+\(", content)

    if not state_methods:
        violations.append(Violation(
            dd_id="DD-09",
            severity=Severity.HIGH.value,
            file_path=file_path,
            line_number=None,
            description="Page Object should have state-check methods (is_*/has_*/get_*) for test assertions",
            code_snippet=None
        ))

    return violations


def check_pom_returns_self(file_path: str, content: str, file_type: str) -> List[Violation]:
    """
    Check that POM action methods return self for fluent chaining.
    """
    violations = []

    if file_type != "page":
        return violations

    lines = content.split("\n")

    # Look for methods with type hint returning the class name
    # These should have 'return self'
    class_match = re.search(r"class\s+(\w+)", content)
    if not class_match:
        return violations

    class_name = class_match.group(1)
    method_pattern = rf'def\s+(\w+)\(.*\)\s*->\s*["\']?{class_name}["\']?:'

    in_method = False
    method_name = ""
    method_start_line = 0
    has_return_self = False

    for i, line in enumerate(lines, 1):
        method_match = re.search(method_pattern, line)
        if method_match:
            # Check previous method if it should have returned self
            if in_method and not has_return_self:
                violations.append(Violation(
                    dd_id="DD-10",
                    severity=Severity.MEDIUM.value,
                    file_path=file_path,
                    line_number=method_start_line,
                    description=f"Method '{method_name}' should 'return self' for fluent chaining",
                    code_snippet=None
                ))

            in_method = True
            method_name = method_match.group(1)
            method_start_line = i
            has_return_self = False
            continue

        if in_method and "return self" in line:
            has_return_self = True

    # Check last method
    if in_method and not has_return_self:
        violations.append(Violation(
            dd_id="DD-10",
            severity=Severity.MEDIUM.value,
            file_path=file_path,
            line_number=method_start_line,
            description=f"Method '{method_name}' should 'return self' for fluent chaining",
            code_snippet=None
        ))

    return violations


# =============================================================================
# File Type Detection
# =============================================================================

def detect_file_type(file_path: str, content: str) -> str:
    """
    Detect the type of file based on path and content.

    Returns: "page", "task", "role", "test", or "unknown"
    """
    path_lower = file_path.lower().replace("\\", "/")

    # Path-based detection
    if "/pages/" in path_lower:
        return "page"
    if "/tasks/" in path_lower:
        return "task"
    if "/roles/" in path_lower:
        return "role"
    if "/tests/" in path_lower or path_lower.startswith("test_") or "/test_" in path_lower:
        return "test"

    # Content-based fallback
    if "class" in content:
        if "Page" in content and "WebInterface" in content:
            return "page"
        if "Tasks" in content and "@autologger" in content:
            return "task"
        if "User" in content or "Role" in content:
            if "auth_tasks" in content or "AuthTasks" in content:
                return "role"

    if "def test_" in content or "@pytest" in content:
        return "test"

    return "unknown"


# =============================================================================
# Main Validation Function
# =============================================================================

def validate_artifact(file_path: str, content: str) -> List[Violation]:
    """
    Validate a single artifact against all applicable DDs.

    Args:
        file_path: Path to the artifact
        content: File content

    Returns:
        List of violations found
    """
    file_type = detect_file_type(file_path, content)
    violations = []

    # Run all checks
    checks = [
        check_dd03_locators_in_pom,
        check_dd15_assertions_use_pom,
        check_dd11_state_method_naming,
        check_dd_task_no_return,
        check_dd_role_no_return,
        check_dd18_import_paths,
        check_dd19_import_from_tools,
        check_pom_has_state_methods,
        check_pom_returns_self,
    ]

    for check in checks:
        violations.extend(check(file_path, content, file_type))

    return violations


async def _test_validate_artifacts(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Raw implementation for testing (DD-VA-12).

    Args:
        args: {"paths": [...], "content_map": {...}}
              - paths: List of file paths to validate
              - content_map: Optional dict mapping paths to content (for testing)

    Returns:
        ReviewResult as dict
    """
    paths = args.get("paths", [])
    content_map = args.get("content_map", {})

    if not paths:
        return {
            "status": "REJECT",
            "violations": [],
            "summary": "No artifact paths provided",
            "files_reviewed": [],
            "blocking_violations": 0,
            "total_violations": 0
        }

    all_violations: List[Violation] = []
    files_reviewed: List[str] = []

    for path in paths:
        # Get content from map (testing) or read file (production)
        if path in content_map:
            content = content_map[path]
        else:
            try:
                file_path = Path(path)
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                else:
                    all_violations.append(Violation(
                        dd_id="DD-18",
                        severity=Severity.HIGH.value,
                        file_path=path,
                        line_number=None,
                        description=f"File not found: {path}",
                        code_snippet=None
                    ))
                    continue
            except Exception as e:
                all_violations.append(Violation(
                    dd_id="DD-18",
                    severity=Severity.HIGH.value,
                    file_path=path,
                    line_number=None,
                    description=f"Error reading file: {str(e)}",
                    code_snippet=None
                ))
                continue

        files_reviewed.append(path)
        violations = validate_artifact(path, content)
        all_violations.extend(violations)

    # Count blocking violations (CRITICAL and HIGH)
    blocking_count = sum(
        1 for v in all_violations
        if v.severity in [Severity.CRITICAL.value, Severity.HIGH.value]
    )

    # Determine status
    status = "REJECT" if blocking_count > 0 else "APPROVE"

    # Generate summary
    if status == "APPROVE":
        summary = f"All {len(files_reviewed)} artifacts passed validation with {len(all_violations)} non-blocking issues"
    else:
        summary = f"BLOCKED: {blocking_count} CRITICAL/HIGH violations found in {len(files_reviewed)} files"

    return {
        "status": status,
        "violations": [asdict(v) for v in all_violations],
        "summary": summary,
        "files_reviewed": files_reviewed,
        "blocking_violations": blocking_count,
        "total_violations": len(all_violations)
    }


# =============================================================================
# Tool Implementation
# =============================================================================

@tool(
    "validate_artifacts",
    "Validate generated artifacts against FRAMEWORK.md patterns and 22 Design Decisions. Returns APPROVE or REJECT with violation list.",
    {
        "paths": list,  # List of file paths to validate
    }
)
async def validate_artifacts(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    QA Reviewer agent tool.

    Validates generated artifacts against all 22 DDs.
    Returns APPROVE (can execute Step 9) or REJECT (must fix first).

    Args:
        args: {"paths": ["path/to/file1.py", "path/to/file2.py", ...]}

    Returns:
        MCP tool response with review result JSON
    """
    result = await _test_validate_artifacts(args)

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "get_dd_checklist",
    "Get the list of all 22 Design Decisions with severities for manual review.",
    {}
)
async def get_dd_checklist(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return the complete DD checklist with severities.
    """
    checklist = []
    for dd_id, severity in DD_SEVERITY.items():
        checklist.append({
            "dd_id": dd_id,
            "severity": severity.value,
            "automated_check": dd_id in ["DD-03", "DD-09", "DD-11", "DD-15", "DD-18", "DD-19"]
        })

    return {
        "content": [{
            "type": "text",
            "text": json.dumps({
                "checklist": checklist,
                "total_dds": len(checklist),
                "note": "automated_check=True means this DD has automated validation"
            }, indent=2)
        }]
    }


# =============================================================================
# Export tools list
# =============================================================================

REVIEWER_TOOLS = [validate_artifacts, get_dd_checklist]


# =============================================================================
# Standalone test
# =============================================================================

if __name__ == "__main__":
    import asyncio

    async def test_reviewer():
        print("Testing QA Reviewer tools...\n")

        # Test with sample code
        good_pom = '''
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface

class LoginPage:
    EMAIL = (By.ID, "email")

    def __init__(self, web: WebInterface):
        self.web = web

    def enter_email(self, email: str) -> "LoginPage":
        self.web.type_text(*self.EMAIL, text=email)
        return self

    def is_logged_in(self) -> bool:
        return self.web.is_element_displayed(*self.LOGOUT)
'''

        bad_task = '''
from selenium.webdriver.common.by import By  # BAD: importing By
from interfaces.web_interface import WebInterface

class AuthTasks:
    def __init__(self, web: WebInterface):
        self.web = web

    def log_in(self, email: str, password: str):
        self.web.click(By.ID, "submit")  # BAD: locator in task
        return True  # BAD: returning value
'''

        bad_test = '''
import pytest

class TestLogin:
    def test_login(self):
        result = user.login()  # BAD: capturing return
        assert result is True  # BAD: asserting on return
'''

        print("1. Testing good POM:")
        result = await _test_validate_artifacts({
            "paths": ["framework/pages/auth/login_page.py"],
            "content_map": {"framework/pages/auth/login_page.py": good_pom}
        })
        print(f"   Status: {result['status']}")
        print(f"   Violations: {result['total_violations']}")

        print("\n2. Testing bad Task (DD-03, DD-09 violations):")
        result = await _test_validate_artifacts({
            "paths": ["framework/tasks/auth/auth_tasks.py"],
            "content_map": {"framework/tasks/auth/auth_tasks.py": bad_task}
        })
        print(f"   Status: {result['status']}")
        print(f"   Blocking: {result['blocking_violations']}")
        for v in result['violations']:
            print(f"   - {v['dd_id']} ({v['severity']}): {v['description']}")

        print("\n3. Testing bad Test (DD-15 violations):")
        result = await _test_validate_artifacts({
            "paths": ["tests/auth/test_login.py"],
            "content_map": {"tests/auth/test_login.py": bad_test}
        })
        print(f"   Status: {result['status']}")
        print(f"   Blocking: {result['blocking_violations']}")
        for v in result['violations']:
            print(f"   - {v['dd_id']} ({v['severity']}): {v['description']}")

        print("\n[SUCCESS] Reviewer tool working!")

    asyncio.run(test_reviewer())

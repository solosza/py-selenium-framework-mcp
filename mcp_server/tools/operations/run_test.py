"""
Test Execution Operation - Task 59.0

Executes pytest tests with consistent parameters and captures results.

Features:
- Pytest subprocess execution with standard flags
- Output capture (stdout + stderr)
- Structured result format
- Crash handling
- Test path validation (prevent directory traversal)
- Failure data extraction (assertions, stack traces)

Part of Step 11: HITL Execution Gate
"""

import subprocess
import time
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

# Project root (parent of mcp_server/)
# __file__ = mcp_server/tools/operations/run_test.py
# .parent = operations/, .parent.parent = tools/, .parent.parent.parent = mcp_server/
# .parent.parent.parent.parent = project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def validate_test_path(test_path: str, tests_root: str = "tests/") -> tuple[bool, Optional[str]]:
    """
    Validate test path to prevent directory traversal attacks.

    Args:
        test_path: Path to test file or directory
        tests_root: Root directory for tests (default: "tests/")

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, error_message) if invalid
    """
    try:
        # Resolve to absolute path relative to PROJECT_ROOT
        resolved_path = (PROJECT_ROOT / test_path).resolve()
        tests_root_resolved = (PROJECT_ROOT / tests_root).resolve()

        # Check if path starts with tests_root
        if not str(resolved_path).startswith(str(tests_root_resolved)):
            return False, f"Test path must be within {tests_root} directory"

        # Check if path exists
        if not resolved_path.exists():
            return False, f"Test path does not exist: {test_path}"

        # Check if it's a file or directory
        if not (resolved_path.is_file() or resolved_path.is_dir()):
            return False, f"Test path must be a file or directory: {test_path}"

        # If file, check it has .py extension
        if resolved_path.is_file() and resolved_path.suffix != ".py":
            return False, f"Test file must have .py extension: {test_path}"

        return True, None

    except Exception as e:
        return False, f"Error validating test path: {str(e)}"


def extract_failure_data(pytest_output: str) -> Dict[str, Any]:
    """
    Extract failure information from pytest output.

    Args:
        pytest_output: Raw pytest output (stdout + stderr)

    Returns:
        Dict with:
        - failed_assertion: The assertion that failed (if found)
        - stack_trace: Full stack trace (if found)
        - error_location: File and line number where error occurred
    """
    failure_data = {
        "failed_assertion": None,
        "stack_trace": None,
        "error_location": None
    }

    # Extract assertion failure (lines starting with "E       assert")
    assertion_match = re.search(r"E\s+assert\s+(.+)", pytest_output)
    if assertion_match:
        failure_data["failed_assertion"] = assertion_match.group(1).strip()

    # Extract error location (file:line in traceback)
    location_match = re.search(r"([a-zA-Z0-9_/\\]+\.py):(\d+):", pytest_output)
    if location_match:
        failure_data["error_location"] = f"{location_match.group(1)}:{location_match.group(2)}"

    # Extract stack trace (everything between "_ _ _ _" markers or FAILED markers)
    stack_trace_match = re.search(
        r"(?:_{5,}|FAILED).+?\n((?:.+\n)*?)(?:_{5,}|=+\s+FAILURES\s+=+|=+\s+short test summary\s+=+)",
        pytest_output,
        re.DOTALL | re.IGNORECASE
    )
    if stack_trace_match:
        failure_data["stack_trace"] = stack_trace_match.group(1).strip()

    return failure_data


def execute_test(
    test_path: str,
    env: str = "DEFAULT",
    report_dir: str = "tests/_reports",
    timeout: int = 60,
    headless: bool = False
) -> Dict[str, Any]:
    """
    Execute pytest test with standard flags and capture results.

    Args:
        test_path: Path to test file or directory (must be within tests/)
        env: Environment name (default: "DEFAULT")
        report_dir: Directory for HTML reports (default: "tests/_reports")
        timeout: Maximum execution time in seconds (default: 60 = 1 minute)
        headless: Whether to run browser in headless mode (default: False for pair programming)

    Returns:
        Dict with:
        - status: "passed" | "failed" | "crashed"
        - exit_code: pytest exit code (0=passed, 1=failed, other=crashed)
        - output: Combined stdout + stderr
        - duration: Execution time in seconds
        - report_path: Path to HTML report (if generated)
        - failure_data: Dict with failed_assertion, stack_trace, error_location (if failed)
        - error: Error message (if crashed)

    Raises:
        ValueError: If test_path validation fails
    """
    # Validate test path
    is_valid, error_msg = validate_test_path(test_path)
    if not is_valid:
        raise ValueError(error_msg)

    # Prepare report path
    report_path = Path(report_dir) / f"report_{int(time.time())}.html"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # Build pytest command
    # Note: headless=False is enforced by Step 2 qg_preflight for pair programming
    cmd = [
        "python", "-m", "pytest",
        test_path,
        "-v",  # Verbose output
        f"--html={report_path}",  # HTML report
        "--self-contained-html",  # Single-file report
        f"--env={env}",  # Environment config
        f"--headless={str(headless)}"  # Browser visibility (False for pair programming)
    ]

    # Execute pytest
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=PROJECT_ROOT
        )
        duration = time.time() - start_time

        # Combine stdout and stderr
        output = f"{result.stdout}\n{result.stderr}".strip()

        # Determine status
        if result.returncode == 0:
            status = "passed"
            failure_data = None
        elif result.returncode == 1:
            status = "failed"
            failure_data = extract_failure_data(output)
        else:
            status = "crashed"
            failure_data = None

        return {
            "status": status,
            "exit_code": result.returncode,
            "output": output,
            "duration": duration,
            "report_path": str(report_path) if report_path.exists() else None,
            "failure_data": failure_data,
            "error": None if result.returncode <= 1 else f"Pytest exited with code {result.returncode}"
        }

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return {
            "status": "crashed",
            "exit_code": -1,
            "output": f"Test execution timed out after {timeout} seconds",
            "duration": duration,
            "report_path": None,
            "failure_data": None,
            "error": f"Timeout: Test execution exceeded {timeout} seconds"
        }

    except Exception as e:
        duration = time.time() - start_time
        return {
            "status": "crashed",
            "exit_code": -1,
            "output": str(e),
            "duration": duration,
            "report_path": None,
            "failure_data": None,
            "error": f"Unexpected error: {str(e)}"
        }


# Async wrapper for MCP server integration
async def run_test_async(arguments: dict) -> str:
    """
    MCP tool entry point for test execution.

    Args:
        arguments: Dict with:
            - test_path (required): Path to test file or directory
            - env (required): Environment config key (e.g., parabank, automationex1)
            - report_dir (optional): Report directory (default: "tests/_reports")
            - timeout (optional): Timeout in seconds (default: 60)

    Returns:
        JSON string with execution results
    """
    test_path = arguments.get("test_path")
    if not test_path:
        return json.dumps({"error": "Missing required parameter: test_path"}, indent=2)

    env = arguments.get("env")
    if not env:
        return json.dumps({"error": "Missing required parameter: env. Use detected_env_id from Step 1."}, indent=2)

    # Default values - simplified, no state reading needed
    headless = False  # Pair programming requires visible browser
    timeout = 60  # Default timeout (sensible for UI tests)

    report_dir = arguments.get("report_dir", "tests/_reports")

    # Allow explicit override from arguments (for testing)
    if "timeout" in arguments:
        timeout = arguments["timeout"]
    if "headless" in arguments:
        headless = arguments["headless"]

    try:
        result = execute_test(
            test_path=test_path,
            env=env,
            report_dir=report_dir,
            timeout=timeout,
            headless=headless
        )
        return json.dumps(result, indent=2)

    except ValueError as e:
        return json.dumps({"error": str(e)}, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)

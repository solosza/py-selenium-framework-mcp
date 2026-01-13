"""
Unit tests for run_test operation - Task 59.0

Test suite for pytest test execution operation.

Test Matrix:
- Happy path: 2 tests (P0) - successful test, failed test
- Negative: 2 tests (P0) - invalid path, path traversal
- Error handling: 2 tests (P1) - timeout, subprocess crash
- Validation: 2 tests (P0) - path validation, extension validation

Testing Skill Reference: .claude/skills/testing/
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.operations.run_test import (
    validate_test_path,
    extract_failure_data,
    execute_test,
    run_test_async
)


# ============================================================================
# HAPPY PATH TESTS
# ============================================================================

class TestRunTestHappyPath:
    """
    Happy path tests for run_test operation.

    Verifies core functionality:
    - Successful test execution (exit code 0)
    - Failed test execution (exit code 1, assertions captured)
    """

    @pytest.mark.unit
    @pytest.mark.run_test
    def test_successful_test_execution(self, tmp_path, monkeypatch):
        """
        P0: Verify execute_test handles successful test execution (exit code 0).

        AAA Pattern:
        1. Arrange - Mock subprocess to return exit code 0
        2. Act - Execute test
        3. Assert - Returns status "passed", correct exit code, no errors
        """
        # Arrange
        test_file = tmp_path / "tests" / "test_example.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_pass(): assert True")

        # Mock subprocess.run to simulate successful test
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "test_example.py::test_pass PASSED"
        mock_result.stderr = ""

        # Change working directory to tmp_path for path validation
        monkeypatch.chdir(tmp_path)

        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = execute_test(test_path=str(test_file))

        # Assert
        assert result["status"] == "passed", \
            f"Successful test should have status 'passed', got {result['status']}"
        assert result["exit_code"] == 0, \
            f"Exit code should be 0 for passed test, got {result['exit_code']}"
        assert result["error"] is None, \
            f"Error should be None for passed test, got {result['error']}"
        assert result["failure_data"] is None, \
            f"Failure data should be None for passed test, got {result['failure_data']}"
        assert "duration" in result, "Result should include duration"
        assert result["duration"] >= 0, "Duration should be non-negative"

    @pytest.mark.unit
    @pytest.mark.run_test
    def test_failed_test_execution(self, tmp_path, monkeypatch):
        """
        P0: Verify execute_test handles failed test execution (exit code 1).

        AAA Pattern:
        1. Arrange - Mock subprocess to return exit code 1 with assertion failure
        2. Act - Execute test
        3. Assert - Returns status "failed", captures assertion and stack trace
        """
        # Arrange
        test_file = tmp_path / "tests" / "test_example.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_fail(): assert False")

        # Mock subprocess.run to simulate failed test
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = """
test_example.py::test_fail FAILED

test_example.py:1: in test_fail
    def test_fail(): assert False
E   assert False

FAILED test_example.py::test_fail - assert False
"""
        mock_result.stderr = ""

        monkeypatch.chdir(tmp_path)

        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = execute_test(test_path=str(test_file))

        # Assert
        assert result["status"] == "failed", \
            f"Failed test should have status 'failed', got {result['status']}"
        assert result["exit_code"] == 1, \
            f"Exit code should be 1 for failed test, got {result['exit_code']}"
        assert result["failure_data"] is not None, \
            "Failed test should include failure_data"
        assert result["failure_data"]["failed_assertion"] is not None, \
            "Failure data should include failed assertion"


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestPathValidation:
    """
    Tests for test path validation.

    Verifies security and correctness:
    - Valid paths accepted
    - Invalid paths rejected
    - Directory traversal prevented
    """

    @pytest.mark.unit
    @pytest.mark.run_test
    def test_valid_test_path_accepted(self, tmp_path, monkeypatch):
        """
        P0: Verify valid test path within tests/ is accepted.

        AAA Pattern:
        1. Arrange - Create valid test file in tests/
        2. Act - Validate path
        3. Assert - Returns (True, None)
        """
        # Arrange
        test_file = tmp_path / "tests" / "test_example.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_pass(): assert True")

        monkeypatch.chdir(tmp_path)

        # Act
        is_valid, error_msg = validate_test_path(str(test_file))

        # Assert
        assert is_valid is True, \
            f"Valid test path should be accepted, got error: {error_msg}"
        assert error_msg is None, \
            f"Error message should be None for valid path, got: {error_msg}"

    @pytest.mark.unit
    @pytest.mark.run_test
    def test_path_outside_tests_rejected(self, tmp_path, monkeypatch):
        """
        P0: Verify path outside tests/ directory is rejected.

        AAA Pattern:
        1. Arrange - Create test file outside tests/
        2. Act - Validate path
        3. Assert - Returns (False, error_message)
        """
        # Arrange
        test_file = tmp_path / "malicious" / "test_bad.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_bad(): pass")

        monkeypatch.chdir(tmp_path)

        # Act
        is_valid, error_msg = validate_test_path(str(test_file))

        # Assert
        assert is_valid is False, \
            "Path outside tests/ should be rejected"
        assert "must be within tests/" in error_msg, \
            f"Error message should mention tests/ requirement, got: {error_msg}"

    @pytest.mark.unit
    @pytest.mark.run_test
    def test_directory_traversal_prevented(self, tmp_path, monkeypatch):
        """
        P0: Verify directory traversal attacks are prevented.

        AAA Pattern:
        1. Arrange - Create malicious path with ../
        2. Act - Validate path
        3. Assert - Returns (False, error_message)
        """
        # Arrange
        monkeypatch.chdir(tmp_path)

        # Create tests directory
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)

        # Attempt directory traversal
        malicious_path = "tests/../../etc/passwd"

        # Act
        is_valid, error_msg = validate_test_path(malicious_path)

        # Assert
        assert is_valid is False, \
            "Directory traversal should be prevented"
        assert error_msg is not None, \
            "Error message should be provided for directory traversal attempt"

    @pytest.mark.unit
    @pytest.mark.run_test
    def test_non_python_file_rejected(self, tmp_path, monkeypatch):
        """
        P0: Verify non-.py files are rejected.

        AAA Pattern:
        1. Arrange - Create file with non-.py extension
        2. Act - Validate path
        3. Assert - Returns (False, error_message)
        """
        # Arrange
        test_file = tmp_path / "tests" / "test_example.txt"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("not a python file")

        monkeypatch.chdir(tmp_path)

        # Act
        is_valid, error_msg = validate_test_path(str(test_file))

        # Assert
        assert is_valid is False, \
            "Non-.py file should be rejected"
        assert ".py extension" in error_msg, \
            f"Error message should mention .py requirement, got: {error_msg}"


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """
    Error handling tests for run_test operation.

    Verifies:
    - Timeout handling
    - Subprocess crashes handled gracefully
    """

    @pytest.mark.unit
    @pytest.mark.run_test
    def test_timeout_handled(self, tmp_path, monkeypatch):
        """
        P1: Verify timeout is handled gracefully.

        AAA Pattern:
        1. Arrange - Mock subprocess to raise TimeoutExpired
        2. Act - Execute test with timeout
        3. Assert - Returns status "crashed", appropriate error message
        """
        # Arrange
        test_file = tmp_path / "tests" / "test_slow.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_slow(): pass")

        monkeypatch.chdir(tmp_path)

        # Mock subprocess.run to raise TimeoutExpired
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd="pytest", timeout=5)):
            # Act
            result = execute_test(test_path=str(test_file), timeout=5)

        # Assert
        assert result["status"] == "crashed", \
            f"Timeout should result in 'crashed' status, got {result['status']}"
        assert result["exit_code"] == -1, \
            f"Timeout should have exit code -1, got {result['exit_code']}"
        assert "timeout" in result["error"].lower(), \
            f"Error should mention timeout, got: {result['error']}"
        assert result["report_path"] is None, \
            "Timeout should not generate report"

    @pytest.mark.unit
    @pytest.mark.run_test
    def test_subprocess_crash_handled(self, tmp_path, monkeypatch):
        """
        P1: Verify subprocess crashes are handled gracefully.

        AAA Pattern:
        1. Arrange - Mock subprocess to raise unexpected exception
        2. Act - Execute test
        3. Assert - Returns status "crashed", captures error
        """
        # Arrange
        test_file = tmp_path / "tests" / "test_crash.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_crash(): pass")

        monkeypatch.chdir(tmp_path)

        # Mock subprocess.run to raise exception
        with patch('subprocess.run', side_effect=Exception("Subprocess crashed")):
            # Act
            result = execute_test(test_path=str(test_file))

        # Assert
        assert result["status"] == "crashed", \
            f"Subprocess crash should result in 'crashed' status, got {result['status']}"
        assert result["exit_code"] == -1, \
            f"Subprocess crash should have exit code -1, got {result['exit_code']}"
        assert "Unexpected error" in result["error"], \
            f"Error should mention unexpected error, got: {result['error']}"


# ============================================================================
# FAILURE DATA EXTRACTION TESTS
# ============================================================================

class TestFailureDataExtraction:
    """
    Tests for failure data extraction from pytest output.

    Verifies correct extraction of:
    - Failed assertions
    - Stack traces
    - Error locations
    """

    @pytest.mark.unit
    @pytest.mark.run_test
    def test_extract_assertion_from_output(self):
        """
        P1: Verify failed assertion is extracted from pytest output.

        AAA Pattern:
        1. Arrange - Create pytest output with assertion
        2. Act - Extract failure data
        3. Assert - Assertion is correctly extracted
        """
        # Arrange
        pytest_output = """
test_example.py::test_fail FAILED

test_example.py:10: in test_fail
    assert False, "Expected True but got False"
E   assert False, "Expected True but got False"
"""

        # Act
        failure_data = extract_failure_data(pytest_output)

        # Assert
        assert failure_data["failed_assertion"] is not None, \
            "Assertion should be extracted"
        assert "False" in failure_data["failed_assertion"], \
            f"Assertion should contain 'False', got: {failure_data['failed_assertion']}"

    @pytest.mark.unit
    @pytest.mark.run_test
    def test_extract_error_location(self):
        """
        P1: Verify error location (file:line) is extracted.

        AAA Pattern:
        1. Arrange - Create pytest output with file:line
        2. Act - Extract failure data
        3. Assert - Location is correctly extracted
        """
        # Arrange
        pytest_output = """
test_example.py::test_fail FAILED

test_example.py:42: in test_fail
    assert False
"""

        # Act
        failure_data = extract_failure_data(pytest_output)

        # Assert
        assert failure_data["error_location"] is not None, \
            "Error location should be extracted"
        assert "test_example.py:42" in failure_data["error_location"], \
            f"Location should be 'test_example.py:42', got: {failure_data['error_location']}"


# ============================================================================
# ASYNC WRAPPER TESTS
# ============================================================================

class TestAsyncWrapper:
    """
    Tests for MCP async wrapper function.

    Verifies:
    - Correct argument parsing
    - JSON response format
    - Error handling for missing arguments
    """

    @pytest.mark.unit
    @pytest.mark.run_test
    def test_missing_test_path_returns_error(self):
        """
        P0: Verify missing test_path parameter returns error.

        AAA Pattern:
        1. Arrange - Create arguments without test_path
        2. Act - Call run_test_async
        3. Assert - Returns JSON with error
        """
        import asyncio

        # Arrange
        arguments = {"env": "dev"}

        # Act
        result = asyncio.run(run_test_async(arguments))
        result_dict = json.loads(result)

        # Assert
        assert "error" in result_dict, \
            "Missing test_path should return error"
        assert "test_path" in result_dict["error"], \
            f"Error should mention test_path, got: {result_dict['error']}"

    @pytest.mark.unit
    @pytest.mark.run_test
    def test_invalid_path_returns_error(self):
        """
        P0: Verify invalid test path returns error in JSON.

        AAA Pattern:
        1. Arrange - Create arguments with invalid path
        2. Act - Call run_test_async
        3. Assert - Returns JSON with validation error
        """
        import asyncio

        # Arrange
        arguments = {"test_path": "/nonexistent/path/test.py"}

        # Act
        result = asyncio.run(run_test_async(arguments))
        result_dict = json.loads(result)

        # Assert
        assert "error" in result_dict, \
            "Invalid path should return error"
        assert result_dict["error"] is not None, \
            "Error message should not be None"

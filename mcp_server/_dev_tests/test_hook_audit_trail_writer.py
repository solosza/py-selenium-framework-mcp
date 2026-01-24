"""
PostToolUse Hook Tests - audit-trail-writer.py

Layer 1: Basic operations (7 tests)
Layer 2: Integration behavior (5 tests)

Testing Skill Reference: .claude/skills/testing/

Hook Function:
- Captures MCP tool results from stdin
- Appends gate validation events to audit log
- Only logs on gate PASS status
- Uses per-run isolation (run_id)
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import io

# Import hook functions
hook_path = Path(__file__).parent.parent.parent / ".claude" / "hooks" / "audit-trail-writer.py"
import importlib.util
spec = importlib.util.spec_from_file_location("audit_trail_writer", hook_path)
audit_trail_writer = importlib.util.module_from_spec(spec)
sys.modules["audit_trail_writer"] = audit_trail_writer
spec.loader.exec_module(audit_trail_writer)

from audit_trail_writer import (
    get_current_run_id,
    get_workflow_state,
    get_audit_file,
    append_to_audit,
    get_project_dir,
    GATE_TO_STEP,
    TOOL_TO_GATE
)


# ============================================================================
# LAYER 1: Basic Operations
# ============================================================================

class TestLayer1BasicOperations:
    """
    Layer 1: Hook basic operations tests.

    Tests individual functions work correctly.
    """

    @pytest.mark.layer1
    @pytest.mark.hook
    def test_get_current_run_id_reads_marker_file(self, tmp_path):
        """
        Layer 1: Verify get_current_run_id() reads marker file.

        AAA Pattern:
        1. Arrange - Create marker file with run_id
        2. Act - Call get_current_run_id()
        3. Assert - Returns correct run_id
        """
        # Arrange
        marker_file = tmp_path / "tests" / "_state" / ".current_run_id"
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        run_id = "2026-01-24T10-00-00.000000Z"
        marker_file.write_text(run_id)

        # Act
        with patch('audit_trail_writer.get_project_dir', return_value=tmp_path):
            result = get_current_run_id()

        # Assert
        assert result == run_id, "Should read run_id from marker file"

    @pytest.mark.layer1
    @pytest.mark.hook
    def test_get_current_run_id_returns_none_if_missing(self, tmp_path):
        """
        Layer 1: Verify get_current_run_id() returns None if marker missing.

        AAA Pattern:
        1. Arrange - No marker file
        2. Act - Call get_current_run_id()
        3. Assert - Returns None
        """
        # Act
        with patch('audit_trail_writer.get_project_dir', return_value=tmp_path):
            result = get_current_run_id()

        # Assert
        assert result is None, "Should return None if marker file missing"

    @pytest.mark.layer1
    @pytest.mark.hook
    def test_get_workflow_state_reads_json(self, tmp_path):
        """
        Layer 1: Verify get_workflow_state() reads workflow state JSON.

        AAA Pattern:
        1. Arrange - Create workflow_state.json
        2. Act - Call get_workflow_state()
        3. Assert - Returns correct state data
        """
        # Arrange
        run_id = "2026-01-24T10-00-00.000000Z"
        state_file = tmp_path / "tests" / "_state" / run_id / "workflow_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)

        state_data = {
            "step_1": {"persona": "test_user", "URL": "http://example.com"}
        }
        state_file.write_text(json.dumps(state_data))

        # Act
        with patch('audit_trail_writer.get_project_dir', return_value=tmp_path):
            result = get_workflow_state(run_id)

        # Assert
        assert result == state_data, "Should read workflow state JSON"
        assert result["step_1"]["persona"] == "test_user"

    @pytest.mark.layer1
    @pytest.mark.hook
    def test_get_audit_file_returns_correct_path(self, tmp_path):
        """
        Layer 1: Verify get_audit_file() returns correct path.

        AAA Pattern:
        1. Arrange - Set project dir
        2. Act - Call get_audit_file()
        3. Assert - Returns correct path format
        """
        # Arrange
        run_id = "2026-01-24T10-00-00.000000Z"

        # Act
        with patch('audit_trail_writer.get_project_dir', return_value=tmp_path):
            result = get_audit_file(run_id)

        # Assert
        expected = tmp_path / "tests" / "_audit" / f"audit_log_{run_id}.json"
        assert result == expected, "Should return correct audit file path"

    @pytest.mark.layer1
    @pytest.mark.hook
    def test_append_to_audit_creates_new_entry(self, tmp_path):
        """
        Layer 1: Verify append_to_audit() creates new audit entry.

        AAA Pattern:
        1. Arrange - Create audit file path
        2. Act - Call append_to_audit()
        3. Assert - Audit file contains new entry
        """
        # Arrange
        run_id = "2026-01-24T10-00-00.000000Z"
        audit_file = tmp_path / f"audit_log_{run_id}.json"
        metadata = {"persona": "test_user", "URL": "http://example.com"}

        # Act
        append_to_audit(audit_file, step=1, gate_name="qg_user_input", metadata=metadata)

        # Assert
        assert audit_file.exists(), "Audit file should be created"

        with open(audit_file, 'r') as f:
            audit = json.load(f)

        assert audit["workflow_id"] == run_id
        assert len(audit["events"]) == 1
        assert audit["events"][0]["step"] == 1
        assert audit["events"][0]["gate"] == "qg_user_input"
        assert audit["events"][0]["result"] == "pass"
        assert audit["events"][0]["metadata"] == metadata

    @pytest.mark.layer1
    @pytest.mark.hook
    def test_gate_to_step_mapping_correct(self):
        """
        Layer 1: Verify GATE_TO_STEP mapping is correct.

        AAA Pattern:
        1. Arrange - Check mapping constants
        2. Act - Verify qg_user_input maps to step 1
        3. Assert - Mapping is correct (fixed from DEF-062)
        """
        # Assert
        assert GATE_TO_STEP['mcp__qa-automation__qg_user_input'] == 1, \
            "qg_user_input should map to step 1 (fixed)"
        assert GATE_TO_STEP['mcp__qa-automation__qg_preflight'] == 2, \
            "qg_preflight should map to step 2 (fixed)"

    @pytest.mark.layer1
    @pytest.mark.hook
    def test_tool_to_gate_mapping_correct(self):
        """
        Layer 1: Verify TOOL_TO_GATE mapping is correct.

        AAA Pattern:
        1. Arrange - Check mapping constants
        2. Act - Verify tool names map to gate names
        3. Assert - Mapping strips mcp prefix
        """
        # Assert
        assert TOOL_TO_GATE['mcp__qa-automation__qg_user_input'] == 'qg_user_input', \
            "Tool name should map to gate name"
        assert TOOL_TO_GATE['mcp__qa-automation__qg_preflight'] == 'qg_preflight', \
            "Tool name should map to gate name"


# ============================================================================
# LAYER 2: Integration Behavior
# ============================================================================

class TestLayer2Integration:
    """
    Layer 2: Hook integration tests.

    Tests hook executes correctly with realistic data.
    """

    @pytest.mark.layer2
    @pytest.mark.hook
    def test_hook_execution_with_gate_pass(self, tmp_path):
        """
        Layer 2: Verify hook execution creates audit entry on gate pass.

        AAA Pattern:
        1. Arrange - Mock stdin with gate pass result
        2. Act - Run hook main()
        3. Assert - Audit file created with entry
        """
        # Arrange - Create marker file and state
        run_id = "2026-01-24T10-30-00.000000Z"
        marker_file = tmp_path / "tests" / "_state" / ".current_run_id"
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        marker_file.write_text(run_id)

        state_file = tmp_path / "tests" / "_state" / run_id / "workflow_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_data = {
            "step_1": {"persona": "test_user", "URL": "http://example.com"}
        }
        state_file.write_text(json.dumps(state_data))

        # Mock stdin with gate pass result
        tool_result = {
            "tool_name": "mcp__qa-automation__qg_user_input",
            "tool_result": json.dumps({"status": "pass"})
        }

        # Act
        with patch('audit_trail_writer.get_project_dir', return_value=tmp_path):
            with patch('sys.stdin', io.StringIO(json.dumps(tool_result))):
                from audit_trail_writer import main
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0, "Hook should exit with code 0"

        # Assert
        audit_file = tmp_path / "tests" / "_audit" / f"audit_log_{run_id}.json"
        assert audit_file.exists(), "Audit file should be created"

        with open(audit_file, 'r') as f:
            audit = json.load(f)

        assert len(audit["events"]) == 1
        assert audit["events"][0]["gate"] == "qg_user_input"
        assert audit["events"][0]["result"] == "pass"

    @pytest.mark.layer2
    @pytest.mark.hook
    def test_hook_appends_to_existing_audit(self, tmp_path):
        """
        Layer 2: Verify hook appends to existing audit file.

        AAA Pattern:
        1. Arrange - Create existing audit file with 1 event
        2. Act - Run hook with new gate pass
        3. Assert - Audit file now has 2 events
        """
        # Arrange - Create existing audit
        run_id = "2026-01-24T10-35-00.000000Z"
        audit_file = tmp_path / "tests" / "_audit" / f"audit_log_{run_id}.json"
        audit_file.parent.mkdir(parents=True, exist_ok=True)

        existing_audit = {
            "workflow_id": run_id,
            "events": [{
                "type": "gate_validation",
                "step": 1,
                "gate": "qg_user_input",
                "result": "pass"
            }]
        }
        audit_file.write_text(json.dumps(existing_audit, indent=2))

        # Arrange - Create marker and state
        marker_file = tmp_path / "tests" / "_state" / ".current_run_id"
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        marker_file.write_text(run_id)

        state_file = tmp_path / "tests" / "_state" / run_id / "workflow_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_data = {"step_2": {"credential_strategy": "static"}}
        state_file.write_text(json.dumps(state_data))

        # Mock stdin with step 2 gate pass
        tool_result = {
            "tool_name": "mcp__qa-automation__qg_preflight",
            "tool_result": json.dumps({"status": "pass"})
        }

        # Act
        with patch('audit_trail_writer.get_project_dir', return_value=tmp_path):
            with patch('sys.stdin', io.StringIO(json.dumps(tool_result))):
                from audit_trail_writer import main
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0

        # Assert
        with open(audit_file, 'r') as f:
            audit = json.load(f)

        assert len(audit["events"]) == 2, "Should have 2 events"
        assert audit["events"][0]["gate"] == "qg_user_input"
        assert audit["events"][1]["gate"] == "qg_preflight"

    @pytest.mark.layer2
    @pytest.mark.hook
    def test_hook_ignores_non_gate_tools(self, tmp_path):
        """
        Layer 2: Verify hook ignores non-gate MCP tools.

        AAA Pattern:
        1. Arrange - Mock stdin with non-gate tool
        2. Act - Run hook main()
        3. Assert - No audit file created
        """
        # Arrange
        run_id = "2026-01-24T10-40-00.000000Z"
        marker_file = tmp_path / "tests" / "_state" / ".current_run_id"
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        marker_file.write_text(run_id)

        # Mock stdin with non-gate tool
        tool_result = {
            "tool_name": "mcp__qa-automation__list_tests",  # Not a gate
            "tool_result": json.dumps({"status": "success"})
        }

        # Act
        with patch('audit_trail_writer.get_project_dir', return_value=tmp_path):
            with patch('sys.stdin', io.StringIO(json.dumps(tool_result))):
                from audit_trail_writer import main
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0

        # Assert
        audit_file = tmp_path / "tests" / "_audit" / f"audit_log_{run_id}.json"
        assert not audit_file.exists(), "Audit file should NOT be created for non-gate tools"

    @pytest.mark.layer2
    @pytest.mark.hook
    def test_hook_handles_corrupted_audit_file(self, tmp_path):
        """
        Layer 2: Verify hook handles corrupted audit file gracefully.

        AAA Pattern:
        1. Arrange - Create corrupted audit file (invalid JSON)
        2. Act - Run hook with gate pass
        3. Assert - Creates fresh audit file
        """
        # Arrange - Create corrupted audit
        run_id = "2026-01-24T10-45-00.000000Z"
        audit_file = tmp_path / "tests" / "_audit" / f"audit_log_{run_id}.json"
        audit_file.parent.mkdir(parents=True, exist_ok=True)
        audit_file.write_text("{ corrupted json }")

        # Arrange - Create marker and state
        marker_file = tmp_path / "tests" / "_state" / ".current_run_id"
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        marker_file.write_text(run_id)

        state_file = tmp_path / "tests" / "_state" / run_id / "workflow_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_data = {"step_1": {"persona": "test_user"}}
        state_file.write_text(json.dumps(state_data))

        # Mock stdin
        tool_result = {
            "tool_name": "mcp__qa-automation__qg_user_input",
            "tool_result": json.dumps({"status": "pass"})
        }

        # Act
        with patch('audit_trail_writer.get_project_dir', return_value=tmp_path):
            with patch('sys.stdin', io.StringIO(json.dumps(tool_result))):
                from audit_trail_writer import main
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0

        # Assert - Fresh audit created
        with open(audit_file, 'r') as f:
            audit = json.load(f)

        assert audit["workflow_id"] == run_id, "Should create fresh audit with correct run_id"
        assert len(audit["events"]) == 1, "Should have 1 event (corrupted file replaced)"

    @pytest.mark.layer2
    @pytest.mark.hook
    def test_hook_handles_missing_run_id_gracefully(self, tmp_path):
        """
        Layer 2: Verify hook exits gracefully if no run_id marker.

        AAA Pattern:
        1. Arrange - No marker file
        2. Act - Run hook with gate pass
        3. Assert - Hook exits without error, no audit created
        """
        # Arrange - No marker file
        tool_result = {
            "tool_name": "mcp__qa-automation__qg_user_input",
            "tool_result": json.dumps({"status": "pass"})
        }

        # Act
        with patch('audit_trail_writer.get_project_dir', return_value=tmp_path):
            with patch('sys.stdin', io.StringIO(json.dumps(tool_result))):
                from audit_trail_writer import main
                try:
                    main()
                except SystemExit as e:
                    assert e.code == 0, "Should exit gracefully with code 0"

        # Assert - No audit created
        audit_dir = tmp_path / "tests" / "_audit"
        if audit_dir.exists():
            assert len(list(audit_dir.glob("*.json"))) == 0, \
                "Should not create audit file without run_id"

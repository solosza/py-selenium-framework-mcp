"""
Tests for TranscriptWriter - Human-Readable Workflow Transcript System.

Test Pyramid (4 layers, 33 tests total):
- Layer 1: Basic Operations (constructor, generate, persist) - 10-15 tests
- Layer 2: Markdown Formatting (all event formatters) - 5-10 tests
- Layer 3: Event Flow & Grouping (multi-event, step grouping) - 3-5 tests
- Layer 4: Error Handling (missing files, malformed data, permissions) - 2-3 tests

Reference: docs/projects/pair-programming/4-test-plan-step1-v4.md - Component 6
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from utils.transcript_writer import TranscriptWriter


# ============================================================
# Test Fixtures
# ============================================================

@pytest.fixture
def temp_test_dir(tmp_path):
    """Create temporary test directory structure."""
    audit_dir = tmp_path / "audit"
    output_dir = tmp_path / "reports"
    audit_dir.mkdir()
    output_dir.mkdir()
    return {
        "audit_dir": str(audit_dir),
        "output_dir": str(output_dir),
        "audit_path": audit_dir,
        "output_path": output_dir
    }


@pytest.fixture
def sample_audit_log():
    """Sample audit log structure with events."""
    return {
        "workflow_id": "test_workflow_001",
        "run_id": "2026-01-23T10:00:00.000000Z",
        "events": [
            {
                "type": "gate_validation",
                "step": 1,
                "gate": "qg_user_input",
                "mode": "POST",
                "result": "pass",
                "timestamp": "2026-01-23T10:00:01Z",
                "metadata": {
                    "persona": "As a registered user",
                    "url": "http://example.com",
                    "workflow": "auth"
                }
            }
        ]
    }


@pytest.fixture
def create_audit_file(temp_test_dir):
    """Factory fixture to create audit log files."""
    def _create(run_id: str, audit_data: dict):
        safe_run_id = run_id.replace(":", "-")
        audit_file = temp_test_dir["audit_path"] / f"audit_log_{safe_run_id}.json"
        with open(audit_file, 'w') as f:
            json.dump(audit_data, f, indent=2)
        return str(audit_file)
    return _create


# ============================================================
# Layer 1: Basic Operations (10-15 tests)
# ============================================================

class TestLayer1BasicOperations:
    """Test fundamental TranscriptWriter operations."""

    def test_constructor_with_default_paths(self):
        """Test TranscriptWriter initialization with default paths."""
        run_id = "2026-01-23T10:00:00.000000Z"
        writer = TranscriptWriter(run_id)

        assert writer.run_id == run_id
        assert writer._audit_dir.name == "_audit"
        assert writer._output_dir.name == run_id
        assert "audit_log_2026-01-23T10-00-00.000000Z.json" in str(writer._audit_file)
        assert "workflow_transcript.md" in str(writer._transcript_file)

    def test_constructor_with_custom_paths(self, temp_test_dir):
        """Test TranscriptWriter initialization with custom paths."""
        run_id = "2026-01-23T10:00:00.000000Z"
        writer = TranscriptWriter(
            run_id,
            audit_dir=temp_test_dir["audit_dir"],
            output_dir=temp_test_dir["output_dir"]
        )

        assert str(temp_test_dir["audit_path"]) in str(writer._audit_dir)
        assert str(temp_test_dir["output_path"]) in str(writer._output_dir)

    def test_run_id_colon_replacement_windows_compat(self, temp_test_dir):
        """Test that colons in run_id are replaced with dashes for Windows compatibility."""
        run_id = "2026-01-23T10:00:00.000000Z"
        writer = TranscriptWriter(run_id, audit_dir=temp_test_dir["audit_dir"])

        # Audit filename should have colons replaced with dashes
        assert ":" not in writer._audit_file.name
        assert "2026-01-23T10-00-00.000000Z" in writer._audit_file.name

    def test_generate_creates_transcript_file(self, temp_test_dir, create_audit_file, sample_audit_log):
        """Test that generate() creates transcript file from audit log."""
        run_id = "2026-01-23T10:00:00.000000Z"
        create_audit_file(run_id, sample_audit_log)

        writer = TranscriptWriter(
            run_id,
            audit_dir=temp_test_dir["audit_dir"],
            output_dir=temp_test_dir["output_dir"]
        )

        result_path = writer.generate()

        # Verify file created
        assert Path(result_path).exists()
        assert "workflow_transcript.md" in result_path

    def test_generate_returns_transcript_path(self, temp_test_dir, create_audit_file, sample_audit_log):
        """Test that generate() returns the path to transcript file."""
        run_id = "2026-01-23T10:00:00.000000Z"
        create_audit_file(run_id, sample_audit_log)

        writer = TranscriptWriter(
            run_id,
            audit_dir=temp_test_dir["audit_dir"],
            output_dir=temp_test_dir["output_dir"]
        )

        result_path = writer.generate()

        assert isinstance(result_path, str)
        assert result_path == str(writer._transcript_file)

    def test_persist_creates_output_directory(self, temp_test_dir, create_audit_file, sample_audit_log):
        """Test that persist creates output directory if it doesn't exist."""
        run_id = "2026-01-23T10:00:00.000000Z"
        create_audit_file(run_id, sample_audit_log)

        # Use nested output path that doesn't exist yet
        nested_output = str(temp_test_dir["output_path"] / "nested" / "path")
        writer = TranscriptWriter(
            run_id,
            audit_dir=temp_test_dir["audit_dir"],
            output_dir=nested_output
        )

        writer.generate()

        # Verify nested directories were created
        assert Path(nested_output).exists()
        assert writer._transcript_file.exists()

    def test_generate_with_empty_events(self, temp_test_dir, create_audit_file):
        """Test generate() with audit log containing no events."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test_workflow_empty",
            "run_id": run_id,
            "events": []
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(
            run_id,
            audit_dir=temp_test_dir["audit_dir"],
            output_dir=temp_test_dir["output_dir"]
        )

        result_path = writer.generate()

        # Verify file created with "no events" message
        with open(result_path, 'r') as f:
            content = f.read()

        assert "# Workflow Transcript" in content
        assert "No events recorded yet" in content

    def test_generate_includes_workflow_id(self, temp_test_dir, create_audit_file, sample_audit_log):
        """Test that generated transcript includes workflow_id from audit log."""
        run_id = "2026-01-23T10:00:00.000000Z"
        create_audit_file(run_id, sample_audit_log)

        writer = TranscriptWriter(
            run_id,
            audit_dir=temp_test_dir["audit_dir"],
            output_dir=temp_test_dir["output_dir"]
        )

        result_path = writer.generate()

        with open(result_path, 'r') as f:
            content = f.read()

        assert "test_workflow_001" in content

    def test_generate_includes_timestamp(self, temp_test_dir, create_audit_file, sample_audit_log):
        """Test that generated transcript includes generation timestamp."""
        run_id = "2026-01-23T10:00:00.000000Z"
        create_audit_file(run_id, sample_audit_log)

        writer = TranscriptWriter(
            run_id,
            audit_dir=temp_test_dir["audit_dir"],
            output_dir=temp_test_dir["output_dir"]
        )

        result_path = writer.generate()

        with open(result_path, 'r') as f:
            content = f.read()

        assert "**Generated:**" in content
        # Verify timestamp format (YYYY-MM-DD HH:MM:SS)
        assert "2026-" in content or "2025-" in content  # Current year range

    def test_persist_writes_utf8_encoding(self, temp_test_dir, create_audit_file):
        """Test that transcript is written with UTF-8 encoding (for emoji support)."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test_emoji",
            "run_id": run_id,
            "events": [
                {
                    "type": "gate_validation",
                    "step": 1,
                    "gate": "test_gate",
                    "mode": "POST",
                    "result": "pass",
                    "timestamp": "2026-01-23T10:00:01Z"
                }
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(
            run_id,
            audit_dir=temp_test_dir["audit_dir"],
            output_dir=temp_test_dir["output_dir"]
        )

        result_path = writer.generate()

        # Verify file can be read with UTF-8 and contains emoji
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Gate pass result should include ✅ emoji
        assert "✅" in content


# ============================================================
# Layer 2: Markdown Formatting (5-10 tests)
# ============================================================

class TestLayer2MarkdownFormatting:
    """Test event formatters produce correct markdown."""

    def test_format_gate_event_pass(self, temp_test_dir, create_audit_file):
        """Test formatting of passing gate validation event."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test",
            "events": [
                {
                    "type": "gate_validation",
                    "step": 1,
                    "gate": "qg_user_input",
                    "mode": "POST",
                    "result": "pass",
                    "timestamp": "2026-01-23T10:00:01Z",
                    "metadata": {"persona": "As a user"}
                }
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "✅" in content  # Pass icon
        assert "Gate: `qg_user_input`" in content
        assert "Result:** `pass`" in content
        assert "**Metadata:**" in content

    def test_format_gate_event_fail(self, temp_test_dir, create_audit_file):
        """Test formatting of failing gate validation event."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test",
            "events": [
                {
                    "type": "gate_validation",
                    "step": 1,
                    "gate": "qg_user_input",
                    "mode": "POST",
                    "result": "fail",
                    "timestamp": "2026-01-23T10:00:01Z",
                    "error": "persona is required"
                }
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "❌" in content  # Fail icon
        assert "**Error:**" in content
        assert "persona is required" in content

    def test_format_self_heal_event(self, temp_test_dir, create_audit_file):
        """Test formatting of self-heal event."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test",
            "events": [
                {
                    "type": "self-heal",
                    "step": 4,
                    "attempt": 1,
                    "error": "Element not found: #submit-button",
                    "timestamp": "2026-01-23T10:00:05Z"
                }
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "🔧" in content  # Self-heal icon
        assert "Attempt #1" in content
        assert "Element not found" in content

    def test_format_tool_call_event(self, temp_test_dir, create_audit_file):
        """Test formatting of tool call event with input/output."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test",
            "events": [
                {
                    "type": "tool_call",
                    "step": 4,
                    "tool": "discover_page_elements",
                    "timestamp": "2026-01-23T10:00:05Z",
                    "input": {"url": "http://example.com"},
                    "output": {"elements_found": 5}
                }
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "🔨" in content  # Tool icon
        assert "Tool Call: `discover_page_elements`" in content
        assert "**Input:**" in content
        assert "**Output:**" in content
        assert "http://example.com" in content

    def test_format_hitl_event(self, temp_test_dir, create_audit_file):
        """Test formatting of HITL interaction event."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test",
            "events": [
                {
                    "type": "hitl_interaction",
                    "step": 6,
                    "trigger_reason": "Test failed - locator issue",
                    "user_choice": "Fix locator",
                    "timestamp": "2026-01-23T10:00:10Z"
                }
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "👤" in content  # HITL icon
        assert "HITL Interaction" in content
        assert "Test failed - locator issue" in content
        assert "Fix locator" in content

    def test_format_hook_event(self, temp_test_dir, create_audit_file):
        """Test formatting of hook intervention event."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test",
            "events": [
                {
                    "type": "hook_intervention",
                    "step": 1,
                    "hook": "PostToolUse",
                    "pattern": "gate_validation",
                    "timestamp": "2026-01-23T10:00:01Z"
                }
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "⚠️" in content  # Hook icon
        assert "Hook Intervention: `PostToolUse`" in content
        assert "gate_validation" in content

    def test_format_unknown_event(self, temp_test_dir, create_audit_file):
        """Test formatting of unknown event type."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test",
            "events": [
                {
                    "type": "custom_event_type",
                    "step": 1,
                    "timestamp": "2026-01-23T10:00:01Z",
                    "data": "some custom data"
                }
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "❓" in content  # Unknown icon
        assert "Unknown Event Type: `custom_event_type`" in content
        assert "**Raw Data:**" in content
        assert "some custom data" in content


# ============================================================
# Layer 3: Event Flow & Grouping (3-5 tests)
# ============================================================

class TestLayer3EventFlowGrouping:
    """Test event grouping and multi-event workflows."""

    def test_events_grouped_by_step(self, temp_test_dir, create_audit_file):
        """Test that events are correctly grouped by step number."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test",
            "events": [
                {"type": "gate_validation", "step": 1, "gate": "gate1", "mode": "POST", "result": "pass", "timestamp": "T1"},
                {"type": "gate_validation", "step": 2, "gate": "gate2", "mode": "POST", "result": "pass", "timestamp": "T2"},
                {"type": "gate_validation", "step": 1, "gate": "gate1", "mode": "PRE", "result": "pass", "timestamp": "T0"}
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify step sections exist and are ordered
        assert "## Step 1" in content
        assert "## Step 2" in content
        # Step 1 should appear before Step 2
        assert content.index("## Step 1") < content.index("## Step 2")

    def test_multiple_events_within_step(self, temp_test_dir, create_audit_file):
        """Test multiple events within same step are all included."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test",
            "events": [
                {"type": "gate_validation", "step": 1, "gate": "gate1", "mode": "PRE", "result": "pass", "timestamp": "T1"},
                {"type": "gate_validation", "step": 1, "gate": "gate1", "mode": "POST", "result": "pass", "timestamp": "T2"},
                {"type": "hook_intervention", "step": 1, "hook": "PostToolUse", "pattern": "gate", "timestamp": "T3"}
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # All events should be in Step 1
        assert content.count("## Step 1") == 1
        assert "Gate: `gate1` (PRE)" in content
        assert "Gate: `gate1` (POST)" in content
        assert "Hook Intervention: `PostToolUse`" in content

    def test_step_sections_separated_by_dividers(self, temp_test_dir, create_audit_file):
        """Test that step sections are separated by markdown dividers."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test",
            "events": [
                {"type": "gate_validation", "step": 1, "gate": "gate1", "mode": "POST", "result": "pass", "timestamp": "T1"},
                {"type": "gate_validation", "step": 2, "gate": "gate2", "mode": "POST", "result": "pass", "timestamp": "T2"}
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify dividers (---) appear between steps
        assert content.count("---") >= 2  # Header divider + step dividers

    def test_events_without_step_number_ignored(self, temp_test_dir, create_audit_file):
        """Test that events without step number are gracefully ignored."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            "workflow_id": "test",
            "events": [
                {"type": "gate_validation", "step": 1, "gate": "gate1", "mode": "POST", "result": "pass", "timestamp": "T1"},
                {"type": "gate_validation", "gate": "gate_no_step", "mode": "POST", "result": "pass", "timestamp": "T2"}  # No step
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Only Step 1 should appear
        assert "## Step 1" in content
        assert "gate_no_step" not in content


# ============================================================
# Layer 4: Error Handling (2-3 tests)
# ============================================================

class TestLayer4ErrorHandling:
    """Test error conditions and edge cases."""

    def test_generate_raises_when_audit_file_missing(self, temp_test_dir):
        """Test that generate() raises FileNotFoundError when audit log doesn't exist."""
        run_id = "2026-01-23T10:00:00.000000Z"
        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])

        with pytest.raises(FileNotFoundError, match="Audit log not found"):
            writer.generate()

    def test_generate_handles_malformed_json(self, temp_test_dir):
        """Test that generate() raises appropriate error for malformed JSON."""
        run_id = "2026-01-23T10:00:00.000000Z"
        safe_run_id = run_id.replace(":", "-")
        audit_file = temp_test_dir["audit_path"] / f"audit_log_{safe_run_id}.json"

        # Write malformed JSON
        with open(audit_file, 'w') as f:
            f.write("{ this is not valid json }")

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])

        with pytest.raises(json.JSONDecodeError):
            writer.generate()

    def test_generate_handles_missing_workflow_id(self, temp_test_dir, create_audit_file):
        """Test that generate() uses run_id as fallback when workflow_id missing."""
        run_id = "2026-01-23T10:00:00.000000Z"
        audit_data = {
            # Missing workflow_id
            "events": [
                {"type": "gate_validation", "step": 1, "gate": "test", "mode": "POST", "result": "pass", "timestamp": "T1"}
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Should use run_id as fallback
        assert run_id in content


# ============================================================
# Test Markers for Pyramid Layers
# ============================================================

# Mark tests by pyramid layer for selective execution
pytest.mark.layer1 = pytest.mark.layer1
pytest.mark.layer2 = pytest.mark.layer2
pytest.mark.layer3 = pytest.mark.layer3
pytest.mark.layer4 = pytest.mark.layer4
pytest.mark.transcript = pytest.mark.transcript

# Apply markers to test classes
for test_class in TestLayer1BasicOperations.__dict__.values():
    if callable(test_class) and test_class.__name__.startswith('test_'):
        pytest.mark.layer1(pytest.mark.transcript(test_class))

for test_class in TestLayer2MarkdownFormatting.__dict__.values():
    if callable(test_class) and test_class.__name__.startswith('test_'):
        pytest.mark.layer2(pytest.mark.transcript(test_class))

for test_class in TestLayer3EventFlowGrouping.__dict__.values():
    if callable(test_class) and test_class.__name__.startswith('test_'):
        pytest.mark.layer3(pytest.mark.transcript(test_class))

for test_class in TestLayer4ErrorHandling.__dict__.values():
    if callable(test_class) and test_class.__name__.startswith('test_'):
        pytest.mark.layer4(pytest.mark.transcript(test_class))


# ============================================================
# Task 7.0: Step 2 (qg_preflight) Transcript Tests
# ============================================================

class TestStep2PreflightTranscript:
    """
    Task 7.0: Transcript integration tests for Step 2 (qg_preflight).

    Verifies transcript behavior specific to pre-flight configuration gate.
    """

    @pytest.mark.layer3
    @pytest.mark.transcript
    @pytest.mark.preflight
    def test_step2_entry_appended_not_overwrite_step1(self, temp_test_dir, create_audit_file):
        """
        7.1: Step 2 entry appended to transcript (doesn't overwrite Step 1).

        AAA Pattern:
        1. Arrange - Create audit log with Step 1 and Step 2 events
        2. Act - Generate transcript
        3. Assert - Both Step 1 and Step 2 sections present
        """
        run_id = "2026-01-25T14:00:00.000000Z"
        audit_data = {
            "workflow_id": "test_step2_append",
            "events": [
                {
                    "type": "gate_validation",
                    "step": 1,
                    "gate": "qg_user_input",
                    "mode": "POST",
                    "result": "pass",
                    "timestamp": "2026-01-25T14:00:01Z",
                    "metadata": {
                        "persona": "As a registered user",
                        "URL": "http://example.com"
                    }
                },
                {
                    "type": "gate_validation",
                    "step": 2,
                    "gate": "qg_preflight",
                    "mode": "POST",
                    "result": "pass",
                    "timestamp": "2026-01-25T14:00:02Z",
                    "metadata": {
                        "credential_strategy": "static",
                        "test_data_location": "shared",
                        "browser_config": {"headless": False},
                        "timeout_config": {"enabled": True, "threshold_seconds": 30}
                    }
                }
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Both steps should be present
        assert "## Step 1" in content, "Step 1 should be present"
        assert "## Step 2" in content, "Step 2 should be present"
        assert "qg_user_input" in content, "Step 1 gate should be recorded"
        assert "qg_preflight" in content, "Step 2 gate should be recorded"
        # Order preserved
        assert content.index("## Step 1") < content.index("## Step 2")

    @pytest.mark.layer3
    @pytest.mark.transcript
    @pytest.mark.preflight
    def test_step2_transcript_contains_header_with_timestamp(self, temp_test_dir, create_audit_file):
        """
        7.2: Transcript contains Step 2 header with timestamp.

        AAA Pattern:
        1. Arrange - Create audit log with Step 2 event including timestamp
        2. Act - Generate transcript
        3. Assert - Step 2 section has timestamp
        """
        run_id = "2026-01-25T14:05:00.000000Z"
        audit_data = {
            "workflow_id": "test_step2_timestamp",
            "events": [
                {
                    "type": "gate_validation",
                    "step": 2,
                    "gate": "qg_preflight",
                    "mode": "POST",
                    "result": "pass",
                    "timestamp": "2026-01-25T14:05:30Z",
                    "metadata": {
                        "credential_strategy": "static",
                        "test_data_location": "shared"
                    }
                }
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Step 2 section should exist
        assert "## Step 2" in content, "Step 2 header should be present"
        # Timestamp should be in the content
        assert "2026-01-25T14:05:30Z" in content, "Step 2 timestamp should be recorded"

    @pytest.mark.layer3
    @pytest.mark.transcript
    @pytest.mark.preflight
    def test_step2_transcript_contains_all_4_config_values(self, temp_test_dir, create_audit_file):
        """
        7.3: Transcript contains all 4 config values from Step 2.

        AAA Pattern:
        1. Arrange - Create audit log with all 4 Step 2 config fields
        2. Act - Generate transcript
        3. Assert - All 4 config values appear in transcript
        """
        run_id = "2026-01-25T14:10:00.000000Z"
        audit_data = {
            "workflow_id": "test_step2_config_values",
            "events": [
                {
                    "type": "gate_validation",
                    "step": 2,
                    "gate": "qg_preflight",
                    "mode": "POST",
                    "result": "pass",
                    "timestamp": "2026-01-25T14:10:30Z",
                    "metadata": {
                        "credential_strategy": "dynamic",
                        "test_data_location": "workflow",
                        "browser_config": {"headless": False},
                        "timeout_config": {"enabled": True, "threshold_seconds": 60}
                    }
                }
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # All 4 config fields should appear in metadata
        assert "credential_strategy" in content, "credential_strategy should be in transcript"
        assert "dynamic" in content, "credential_strategy value should be in transcript"
        assert "test_data_location" in content, "test_data_location should be in transcript"
        assert "workflow" in content, "test_data_location value should be in transcript"
        assert "browser_config" in content, "browser_config should be in transcript"
        assert "headless" in content, "browser_config.headless should be in transcript"
        assert "timeout_config" in content, "timeout_config should be in transcript"
        assert "threshold_seconds" in content, "timeout_config.threshold_seconds should be in transcript"

    @pytest.mark.layer3
    @pytest.mark.transcript
    @pytest.mark.preflight
    def test_step2_transcript_format_matches_spec(self, temp_test_dir, create_audit_file):
        """
        7.4: Transcript format matches PRD spec (markdown with gate details).

        AAA Pattern:
        1. Arrange - Create audit log with Step 2 pass
        2. Act - Generate transcript
        3. Assert - Format follows spec (header, gate, result, metadata)
        """
        run_id = "2026-01-25T14:15:00.000000Z"
        audit_data = {
            "workflow_id": "test_step2_format",
            "events": [
                {
                    "type": "gate_validation",
                    "step": 2,
                    "gate": "qg_preflight",
                    "mode": "POST",
                    "result": "pass",
                    "timestamp": "2026-01-25T14:15:30Z",
                    "metadata": {
                        "credential_strategy": "static",
                        "test_data_location": "shared",
                        "browser_config": {"headless": False},
                        "timeout_config": {"enabled": True, "threshold_seconds": 30}
                    }
                }
            ]
        }
        create_audit_file(run_id, audit_data)

        writer = TranscriptWriter(run_id, temp_test_dir["audit_dir"], temp_test_dir["output_dir"])
        result_path = writer.generate()

        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # PRD spec format requirements:
        # 1. Main header
        assert "# Workflow Transcript" in content, "Should have main header"
        # 2. Workflow ID
        assert "test_step2_format" in content, "Should include workflow_id"
        # 3. Step section header
        assert "## Step 2" in content, "Should have step section header"
        # 4. Gate name with backticks
        assert "Gate: `qg_preflight`" in content, "Gate name should be in code format"
        # 5. Result with status
        assert "Result:** `pass`" in content, "Result should show pass status"
        # 6. Metadata section
        assert "**Metadata:**" in content, "Should have metadata section"
        # 7. Pass icon (emoji)
        assert "✅" in content, "Should have pass icon"

"""
Tests for AuditLogger - Audit Trail System (Task 1.0)

Test Pyramid:
1. INITIALIZATION  - Valid run_id creation
2. LOGGING         - Each log method records correctly
3. ACCUMULATION    - Data accumulates across calls
4. SUMMARY         - get_summary() calculates correctly
5. PERSISTENCE     - finalize() writes valid JSON
6. SCHEMA          - Output matches PRD spec
7. EDGE CASES      - Empty runs, missing data, errors
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

# Import will fail until we implement - that's TDD (Red phase)
from utils.audit_logger import AuditLogger


class TestInitialization:
    """1. INITIALIZATION - Does it create valid run_id?"""

    def test_creates_run_id_on_init(self):
        """AuditLogger should generate timestamp-based run_id."""
        logger = AuditLogger()
        assert logger.run_id is not None
        assert isinstance(logger.run_id, str)
        assert len(logger.run_id) > 0

    def test_run_id_is_iso_timestamp(self):
        """run_id should be ISO format timestamp."""
        logger = AuditLogger()
        # Should be parseable as ISO datetime
        try:
            datetime.fromisoformat(logger.run_id.replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"run_id '{logger.run_id}' is not valid ISO format")

    def test_accepts_custom_run_id(self):
        """Should accept custom run_id if provided."""
        custom_id = "2025-12-27T10:00:00Z"
        logger = AuditLogger(run_id=custom_id)
        assert logger.run_id == custom_id

    def test_initializes_empty_steps_list(self):
        """Should start with empty steps list."""
        logger = AuditLogger()
        assert logger.steps == []

    def test_initializes_empty_files_list(self):
        """Should start with empty files_generated list."""
        logger = AuditLogger()
        assert logger.files_generated == []


class TestLogging:
    """2. LOGGING - Does each log method record correctly?"""

    def test_log_gate_records_step(self):
        """log_gate() should record gate call with all fields."""
        logger = AuditLogger()
        logger.log_gate(
            step=1,
            gate_name="qg_preflight",
            mode="POST",
            result="pass"
        )

        assert len(logger.steps) == 1
        entry = logger.steps[0]
        assert entry["step"] == 1
        assert entry["gate"] == "qg_preflight"
        assert entry["mode"] == "POST"
        assert entry["result"] == "pass"
        assert "timestamp" in entry

    def test_log_gate_records_error_on_fail(self):
        """log_gate() should record error when result is fail."""
        logger = AuditLogger()
        logger.log_gate(
            step=6,
            gate_name="qg_page_object",
            mode="POST",
            result="fail",
            error="skeleton detected"
        )

        entry = logger.steps[0]
        assert entry["result"] == "fail"
        assert entry["error"] == "skeleton detected"

    def test_log_gate_records_source(self):
        """log_gate() should record execution source."""
        logger = AuditLogger()
        logger.log_gate(
            step=6,
            gate_name="qg_page_object",
            mode="POST",
            result="pass",
            source="self-heal"
        )

        entry = logger.steps[0]
        assert entry["source"] == "self-heal"

    def test_log_self_heal_records_attempt(self):
        """log_self_heal() should record self-heal attempt."""
        logger = AuditLogger()
        logger.log_self_heal(
            step=6,
            attempt=1,
            error="skeleton detected"
        )

        assert len(logger.steps) == 1
        entry = logger.steps[0]
        assert entry["step"] == 6
        assert entry["type"] == "self-heal"
        assert entry["attempt"] == 1
        assert entry["error"] == "skeleton detected"

    def test_log_file_generated_records_path(self):
        """log_file_generated() should record file path and step."""
        logger = AuditLogger()
        logger.log_file_generated(
            path="framework/pages/auth/login_page.py",
            step=6
        )

        assert len(logger.files_generated) == 1
        entry = logger.files_generated[0]
        assert entry["path"] == "framework/pages/auth/login_page.py"
        assert entry["step"] == 6


class TestAccumulation:
    """3. ACCUMULATION - Does data accumulate across calls?"""

    def test_multiple_gate_calls_accumulate(self):
        """Multiple log_gate() calls should accumulate."""
        logger = AuditLogger()

        logger.log_gate(step=1, gate_name="qg_preflight", mode="POST", result="pass")
        logger.log_gate(step=2, gate_name="qg_user_input", mode="POST", result="pass")
        logger.log_gate(step=3, gate_name="qg_ai_processing", mode="POST", result="pass")

        assert len(logger.steps) == 3

    def test_mixed_entries_accumulate(self):
        """Gate calls and self-heals should accumulate together."""
        logger = AuditLogger()

        logger.log_gate(step=6, gate_name="qg_page_object", mode="POST", result="fail", error="skeleton")
        logger.log_self_heal(step=6, attempt=1, error="skeleton")
        logger.log_gate(step=6, gate_name="qg_page_object", mode="POST", result="pass", source="self-heal")

        assert len(logger.steps) == 3

    def test_multiple_files_accumulate(self):
        """Multiple log_file_generated() calls should accumulate."""
        logger = AuditLogger()

        logger.log_file_generated(path="framework/pages/auth/login_page.py", step=6)
        logger.log_file_generated(path="framework/tasks/auth/auth_tasks.py", step=7)

        assert len(logger.files_generated) == 2


class TestSummary:
    """4. SUMMARY - Does get_summary() calculate correctly?"""

    def test_summary_counts_total_steps(self):
        """get_summary() should count unique steps."""
        logger = AuditLogger()
        logger.log_gate(step=1, gate_name="qg_preflight", mode="POST", result="pass")
        logger.log_gate(step=2, gate_name="qg_user_input", mode="POST", result="pass")

        summary = logger.get_summary()
        assert summary["total_steps"] == 2

    def test_summary_counts_gates_passed(self):
        """get_summary() should count passed gates."""
        logger = AuditLogger()
        logger.log_gate(step=1, gate_name="qg_preflight", mode="POST", result="pass")
        logger.log_gate(step=2, gate_name="qg_user_input", mode="POST", result="pass")
        logger.log_gate(step=3, gate_name="qg_ai_processing", mode="POST", result="fail")

        summary = logger.get_summary()
        assert summary["gates_passed"] == 2

    def test_summary_counts_gates_failed(self):
        """get_summary() should count failed gates."""
        logger = AuditLogger()
        logger.log_gate(step=6, gate_name="qg_page_object", mode="POST", result="fail")
        logger.log_gate(step=6, gate_name="qg_page_object", mode="POST", result="fail")
        logger.log_gate(step=6, gate_name="qg_page_object", mode="POST", result="pass")

        summary = logger.get_summary()
        assert summary["gates_failed"] == 2

    def test_summary_counts_self_heals(self):
        """get_summary() should count self-heal attempts."""
        logger = AuditLogger()
        logger.log_self_heal(step=6, attempt=1, error="skeleton")
        logger.log_self_heal(step=6, attempt=2, error="missing method")

        summary = logger.get_summary()
        assert summary["self_heals"] == 2

    def test_summary_final_result_pass(self):
        """final_result should be 'pass' if last gate passed."""
        logger = AuditLogger()
        logger.log_gate(step=10, gate_name="qg_save_run", mode="PRE", result="pass")

        summary = logger.get_summary()
        assert summary["final_result"] == "pass"

    def test_summary_final_result_fail(self):
        """final_result should be 'fail' if last gate failed."""
        logger = AuditLogger()
        logger.log_gate(step=6, gate_name="qg_page_object", mode="POST", result="fail")

        summary = logger.get_summary()
        assert summary["final_result"] == "fail"

    def test_summary_empty_run(self):
        """get_summary() should handle empty run."""
        logger = AuditLogger()

        summary = logger.get_summary()
        assert summary["total_steps"] == 0
        assert summary["gates_passed"] == 0
        assert summary["gates_failed"] == 0
        assert summary["self_heals"] == 0


class TestPersistence:
    """5. PERSISTENCE - Does finalize() write valid JSON?"""

    def test_finalize_creates_file(self):
        """finalize() should create audit log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(run_id="2025-12-27T10:00:00Z")
            logger.log_gate(step=1, gate_name="qg_preflight", mode="POST", result="pass")

            filepath = logger.finalize(output_dir=tmpdir)

            assert os.path.exists(filepath)
            assert "audit_log_" in filepath
            assert filepath.endswith(".json")

    def test_finalize_writes_valid_json(self):
        """finalize() should write valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(run_id="2025-12-27T10:00:00Z")
            logger.log_gate(step=1, gate_name="qg_preflight", mode="POST", result="pass")

            filepath = logger.finalize(output_dir=tmpdir)

            with open(filepath, 'r') as f:
                data = json.load(f)

            assert isinstance(data, dict)

    def test_finalize_includes_run_id(self):
        """finalize() output should include run_id."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(run_id="2025-12-27T10:00:00Z")
            filepath = logger.finalize(output_dir=tmpdir)

            with open(filepath, 'r') as f:
                data = json.load(f)

            assert data["run_id"] == "2025-12-27T10:00:00Z"

    def test_finalize_includes_execution_mode(self):
        """finalize() output should include execution_mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(execution_mode="mixed")
            filepath = logger.finalize(output_dir=tmpdir)

            with open(filepath, 'r') as f:
                data = json.load(f)

            assert data["execution_mode"] == "mixed"


class TestSchema:
    """6. SCHEMA - Does output match PRD spec?"""

    def test_schema_has_required_top_level_fields(self):
        """Output should have all PRD-specified top-level fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger()
            logger.log_gate(step=1, gate_name="qg_preflight", mode="POST", result="pass")
            logger.log_file_generated(path="test.py", step=1)
            filepath = logger.finalize(output_dir=tmpdir)

            with open(filepath, 'r') as f:
                data = json.load(f)

            # PRD spec fields
            assert "run_id" in data
            assert "execution_mode" in data
            assert "steps" in data
            assert "files_generated" in data
            assert "summary" in data

    def test_schema_step_entry_fields(self):
        """Step entries should have PRD-specified fields."""
        logger = AuditLogger()
        logger.log_gate(
            step=1,
            gate_name="qg_preflight",
            mode="POST",
            result="pass"
        )

        entry = logger.steps[0]
        assert "step" in entry
        assert "gate" in entry
        assert "mode" in entry
        assert "result" in entry
        assert "timestamp" in entry

    def test_schema_summary_fields(self):
        """Summary should have PRD-specified fields."""
        logger = AuditLogger()
        logger.log_gate(step=1, gate_name="qg_preflight", mode="POST", result="pass")

        summary = logger.get_summary()
        assert "total_steps" in summary
        assert "gates_passed" in summary
        assert "gates_failed" in summary
        assert "self_heals" in summary
        assert "final_result" in summary


class TestEdgeCases:
    """7. EDGE CASES - Empty runs, missing data, errors."""

    def test_finalize_empty_run(self):
        """finalize() should handle empty run (no logs)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger()
            filepath = logger.finalize(output_dir=tmpdir)

            with open(filepath, 'r') as f:
                data = json.load(f)

            assert data["steps"] == []
            assert data["files_generated"] == []

    def test_log_gate_missing_optional_fields(self):
        """log_gate() should work without optional error/source."""
        logger = AuditLogger()
        logger.log_gate(step=1, gate_name="qg_preflight", mode="POST", result="pass")

        entry = logger.steps[0]
        assert "error" not in entry or entry.get("error") is None
        assert "source" not in entry or entry.get("source") is None

    def test_multiple_finalize_calls(self):
        """Multiple finalize() calls should create separate files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger1 = AuditLogger(run_id="2025-12-27T10:00:00Z")
            logger2 = AuditLogger(run_id="2025-12-27T11:00:00Z")

            path1 = logger1.finalize(output_dir=tmpdir)
            path2 = logger2.finalize(output_dir=tmpdir)

            assert path1 != path2
            assert os.path.exists(path1)
            assert os.path.exists(path2)

    def test_finalize_creates_output_dir_if_missing(self):
        """finalize() should create output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = os.path.join(tmpdir, "nested", "audit")
            logger = AuditLogger()

            filepath = logger.finalize(output_dir=nested_dir)

            assert os.path.exists(filepath)

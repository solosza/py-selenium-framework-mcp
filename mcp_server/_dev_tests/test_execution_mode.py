"""
Tests for Execution Mode Flag Infrastructure (Task 2.5).

Test Pyramid:
1. EXECUTION MODE STATE - StateManager get/set/default
2. ENV VAR DEFAULT - Default from ISAGAWA_EXECUTION_MODE
3. VALIDATION - Only valid modes accepted
4. WORKFLOW STATE - execution_mode persisted with workflow
5. AUDIT SOURCE TRACKING - source captured per step
6. EXECUTION SUMMARY - count sources in audit summary
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.state_manager import StateManager
from utils.audit_logger import AuditLogger


# =============================================================================
# 1. EXECUTION MODE STATE - StateManager get/set/default
# =============================================================================

class TestExecutionModeState:
    """1. EXECUTION MODE STATE - StateManager get/set methods."""

    def test_get_execution_mode_returns_mixed_by_default(self, tmp_path):
        """Default execution mode is 'mixed'."""
        state_file = tmp_path / "test_state.json"
        manager = StateManager(str(state_file))

        result = manager.get_execution_mode()

        assert result == "mixed"

    def test_set_execution_mode_stores_value(self, tmp_path):
        """set_execution_mode stores the value."""
        state_file = tmp_path / "test_state.json"
        manager = StateManager(str(state_file))

        manager.set_execution_mode("skills_only")
        result = manager.get_execution_mode()

        assert result == "skills_only"

    def test_execution_mode_persists_across_instances(self, tmp_path):
        """Execution mode persists in state file."""
        state_file = tmp_path / "test_state.json"

        # Set with first instance
        manager1 = StateManager(str(state_file))
        manager1.set_execution_mode("skills_only")

        # Read with second instance
        manager2 = StateManager(str(state_file))
        result = manager2.get_execution_mode()

        assert result == "skills_only"

    def test_execution_mode_stored_in_state_file(self, tmp_path):
        """Execution mode written to JSON state file."""
        state_file = tmp_path / "test_state.json"
        manager = StateManager(str(state_file))

        manager.set_execution_mode("skills_only")

        # Read raw JSON
        with open(state_file) as f:
            data = json.load(f)

        assert "_execution_mode" in data
        assert data["_execution_mode"] == "skills_only"


# =============================================================================
# 2. ENV VAR DEFAULT - Default from ISAGAWA_EXECUTION_MODE
# =============================================================================

class TestEnvVarDefault:
    """2. ENV VAR DEFAULT - Default from ISAGAWA_EXECUTION_MODE env var."""

    def test_default_from_env_var(self, tmp_path):
        """Execution mode defaults to env var value."""
        state_file = tmp_path / "test_state.json"

        with patch.dict(os.environ, {"ISAGAWA_EXECUTION_MODE": "skills_only"}):
            manager = StateManager(str(state_file))
            result = manager.get_execution_mode()

        assert result == "skills_only"

    def test_env_var_not_set_uses_mixed(self, tmp_path):
        """Without env var, defaults to 'mixed'."""
        state_file = tmp_path / "test_state.json"

        # Ensure env var not set
        env = os.environ.copy()
        env.pop("ISAGAWA_EXECUTION_MODE", None)

        with patch.dict(os.environ, env, clear=True):
            manager = StateManager(str(state_file))
            result = manager.get_execution_mode()

        assert result == "mixed"

    def test_saved_mode_overrides_env_var(self, tmp_path):
        """Once saved, execution mode overrides env var default."""
        state_file = tmp_path / "test_state.json"

        # Save with skills_only
        manager1 = StateManager(str(state_file))
        manager1.set_execution_mode("skills_only")

        # Load with different env var
        with patch.dict(os.environ, {"ISAGAWA_EXECUTION_MODE": "mixed"}):
            manager2 = StateManager(str(state_file))
            result = manager2.get_execution_mode()

        # Saved value takes precedence
        assert result == "skills_only"


# =============================================================================
# 3. VALIDATION - Only valid modes accepted
# =============================================================================

class TestModeValidation:
    """3. VALIDATION - Only valid modes accepted."""

    def test_set_mixed_mode_accepted(self, tmp_path):
        """'mixed' is a valid mode."""
        state_file = tmp_path / "test_state.json"
        manager = StateManager(str(state_file))

        manager.set_execution_mode("mixed")

        assert manager.get_execution_mode() == "mixed"

    def test_set_skills_only_mode_accepted(self, tmp_path):
        """'skills_only' is a valid mode."""
        state_file = tmp_path / "test_state.json"
        manager = StateManager(str(state_file))

        manager.set_execution_mode("skills_only")

        assert manager.get_execution_mode() == "skills_only"

    def test_set_invalid_mode_raises_error(self, tmp_path):
        """Invalid mode raises ValueError."""
        state_file = tmp_path / "test_state.json"
        manager = StateManager(str(state_file))

        with pytest.raises(ValueError, match="Invalid execution mode"):
            manager.set_execution_mode("tools_only")

    def test_set_empty_mode_raises_error(self, tmp_path):
        """Empty mode raises ValueError."""
        state_file = tmp_path / "test_state.json"
        manager = StateManager(str(state_file))

        with pytest.raises(ValueError, match="Invalid execution mode"):
            manager.set_execution_mode("")


# =============================================================================
# 4. WORKFLOW STATE - execution_mode persisted with workflow
# =============================================================================

class TestWorkflowState:
    """4. WORKFLOW STATE - execution_mode in workflow context."""

    def test_execution_mode_separate_from_step_data(self, tmp_path):
        """Execution mode stored separately from step data."""
        state_file = tmp_path / "test_state.json"
        manager = StateManager(str(state_file))

        # Save step data
        manager.save(step=1, data={"persona": "test"})
        # Save execution mode
        manager.set_execution_mode("skills_only")

        # Verify both exist
        step_data = manager.get_step(1)
        mode = manager.get_execution_mode()

        assert step_data == {"persona": "test"}
        assert mode == "skills_only"

    def test_clear_preserves_execution_mode(self, tmp_path):
        """clear() does not affect execution mode (if wanted)."""
        # Note: This test defines the expected behavior.
        # If we want clear() to reset mode, change this test.
        state_file = tmp_path / "test_state.json"
        manager = StateManager(str(state_file))

        manager.set_execution_mode("skills_only")
        manager.save(step=1, data={"test": "data"})
        manager.clear()

        # After clear, mode should be back to default
        result = manager.get_execution_mode()
        assert result == "mixed"  # Clear resets to default


# =============================================================================
# 5. AUDIT SOURCE TRACKING - source captured per step
# =============================================================================

class TestAuditSourceTracking:
    """5. AUDIT SOURCE TRACKING - source captured per step in audit log."""

    def test_log_gate_with_source_tool(self):
        """log_gate captures 'tool' source."""
        logger = AuditLogger(run_id="test-run")

        logger.log_gate(
            step=6,
            gate_name="qg_page_object",
            mode="POST",
            result="pass",
            source="tool"
        )

        assert len(logger.steps) == 1
        assert logger.steps[0]["source"] == "tool"

    def test_log_gate_with_source_ai(self):
        """log_gate captures 'ai' source."""
        logger = AuditLogger(run_id="test-run")

        logger.log_gate(
            step=6,
            gate_name="qg_page_object",
            mode="POST",
            result="pass",
            source="ai"
        )

        assert logger.steps[0]["source"] == "ai"

    def test_log_gate_with_source_self_heal(self):
        """log_gate captures 'self-heal' source."""
        logger = AuditLogger(run_id="test-run")

        logger.log_gate(
            step=6,
            gate_name="qg_page_object",
            mode="POST",
            result="pass",
            source="self-heal"
        )

        assert logger.steps[0]["source"] == "self-heal"

    def test_log_gate_source_in_finalized_file(self, tmp_path):
        """Source appears in finalized audit log JSON."""
        logger = AuditLogger(run_id="test-run")

        logger.log_gate(step=6, gate_name="qg_page_object", mode="POST",
                        result="pass", source="tool")
        logger.log_gate(step=7, gate_name="qg_task", mode="POST",
                        result="pass", source="ai")

        filepath = logger.finalize(str(tmp_path))

        with open(filepath) as f:
            data = json.load(f)

        # Verify sources in steps
        sources = [s.get("source") for s in data["steps"]]
        assert "tool" in sources
        assert "ai" in sources


# =============================================================================
# 6. EXECUTION SUMMARY - count sources in audit summary
# =============================================================================

class TestExecutionSummary:
    """6. EXECUTION SUMMARY - count sources in audit summary."""

    def test_summary_includes_source_counts(self):
        """get_summary() returns source breakdown."""
        logger = AuditLogger(run_id="test-run")

        logger.log_gate(step=6, gate_name="qg_page_object", mode="POST",
                        result="pass", source="tool")
        logger.log_gate(step=7, gate_name="qg_task", mode="POST",
                        result="pass", source="tool")
        logger.log_gate(step=8, gate_name="qg_role", mode="POST",
                        result="pass", source="ai")

        summary = logger.get_summary()

        assert "source_counts" in summary
        assert summary["source_counts"]["tool"] == 2
        assert summary["source_counts"]["ai"] == 1

    def test_summary_source_counts_zero_for_unused(self):
        """Source counts show 0 for unused sources."""
        logger = AuditLogger(run_id="test-run")

        logger.log_gate(step=6, gate_name="qg_page_object", mode="POST",
                        result="pass", source="tool")

        summary = logger.get_summary()

        assert summary["source_counts"]["tool"] == 1
        assert summary["source_counts"].get("ai", 0) == 0
        assert summary["source_counts"].get("self-heal", 0) == 0

    def test_summary_includes_execution_mode(self):
        """get_summary() includes execution_mode."""
        logger = AuditLogger(run_id="test-run", execution_mode="skills_only")

        summary = logger.get_summary()

        assert summary["execution_mode"] == "skills_only"

    def test_summary_in_finalized_file(self, tmp_path):
        """Execution summary with source counts in finalized file."""
        logger = AuditLogger(run_id="test-run", execution_mode="mixed")

        logger.log_gate(step=6, gate_name="qg_page_object", mode="POST",
                        result="pass", source="tool")
        logger.log_gate(step=6, gate_name="qg_page_object", mode="POST",
                        result="fail", source="tool")
        logger.log_gate(step=6, gate_name="qg_page_object", mode="POST",
                        result="pass", source="self-heal")

        filepath = logger.finalize(str(tmp_path))

        with open(filepath) as f:
            data = json.load(f)

        summary = data["summary"]
        assert summary["execution_mode"] == "mixed"
        assert "source_counts" in summary
        assert summary["source_counts"]["tool"] == 2
        assert summary["source_counts"]["self-heal"] == 1


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Step 1 Integration Tests (Layer 3)

Tests Layer 3 integration behavior for all Step 1 components:
- Protocol: E2E workflow validation (simplified - tests components used by protocol)
- Gate: Integration with real StateManager
- State: Per-run isolation and concurrency
- Audit: Progressive append and immutability
- Hook: Integration with MCP and audit system

Note: Transcript Layer 3 is tested in test_transcript_writer.py
"""

import pytest
import json
import time
import threading
from pathlib import Path
from datetime import datetime

from utils.state_manager import StateManager
from utils.audit_logger import AuditLogger
from utils.transcript_writer import TranscriptWriter


# ============================================================================
# STATE LAYER 3: Isolation & Concurrency Tests
# ============================================================================

class TestStateLayer3:
    """
    Layer 3: State isolation and concurrency tests.

    Tests per-run isolation and concurrent access patterns.
    """

    @pytest.mark.layer3
    @pytest.mark.state
    @pytest.mark.integration
    def test_multiple_runs_dont_overwrite(self, tmp_path):
        """
        Layer 3: Verify multiple runs maintain separate state files (AT-1.10).

        Per-run isolation requirement: run_A and run_B should not interfere.
        """
        # Arrange
        state_dir = tmp_path / "_state"
        state_dir.mkdir(exist_ok=True)

        run_id_a = "2026-01-24T10:30:00.000000Z"
        run_id_b = "2026-01-24T10:31:00.000000Z"

        # Need to temporarily change where StateManager looks for tests/_state/
        # For testing, we'll use the state_file parameter directly
        state_file_a = state_dir / run_id_a.replace(":", "-") / "workflow_state.json"
        state_file_b = state_dir / run_id_b.replace(":", "-") / "workflow_state.json"

        state_file_a.parent.mkdir(parents=True, exist_ok=True)
        state_file_b.parent.mkdir(parents=True, exist_ok=True)

        state_manager_a = StateManager(state_file=str(state_file_a))
        state_manager_b = StateManager(state_file=str(state_file_b))

        data_a = {"persona": "user_a", "workflow": "run_a"}
        data_b = {"persona": "user_b", "workflow": "run_b"}

        # Act - Save state for both runs
        state_manager_a.save(step=1, data=data_a)
        state_manager_b.save(step=1, data=data_b)

        # Assert - Both state files exist
        assert state_file_a.exists(), "Run A state should exist"
        assert state_file_b.exists(), "Run B state should exist"

        # Verify states are different
        with open(state_file_a, 'r') as f:
            state_a = json.load(f)
        with open(state_file_b, 'r') as f:
            state_b = json.load(f)

        assert state_a["step_1"]["persona"] == "user_a"
        assert state_b["step_1"]["persona"] == "user_b"

    @pytest.mark.layer3
    @pytest.mark.state
    @pytest.mark.integration
    def test_state_load_after_save(self, tmp_path):
        """
        Layer 3: Verify state can be loaded after saving.

        Tests state persistence and retrieval.
        """
        # Arrange
        state_dir = tmp_path / "_state"
        run_id = "2026-01-24T10:35:00.000000Z"
        state_file = state_dir / run_id.replace(":", "-") / "workflow_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)

        state_manager = StateManager(state_file=str(state_file))

        original_data = {
            "persona": "test user",
            "URL": "http://example.com",
            "workflow": "test"
        }

        # Act - Save and load
        state_manager.save(step=1, data=original_data)
        loaded_data = state_manager.load()

        # Assert
        assert loaded_data is not None
        assert loaded_data["step_1"]["persona"] == "test user"

    @pytest.mark.layer3
    @pytest.mark.state
    @pytest.mark.integration
    @pytest.mark.slow
    def test_concurrent_state_writes_different_runs(self, tmp_path):
        """
        Layer 3: Verify concurrent writes to different runs don't interfere.

        Simulates concurrent Step 1 executions for different test runs.
        """
        # Arrange
        state_dir = tmp_path / "_state"
        state_dir.mkdir(exist_ok=True)

        run_id_1 = "2026-01-24T10-40-00.000000Z"  # Pre-sanitized for Windows
        run_id_2 = "2026-01-24T10-40-01.000000Z"

        state_file_1 = state_dir / run_id_1 / "workflow_state.json"
        state_file_2 = state_dir / run_id_2 / "workflow_state.json"

        state_file_1.parent.mkdir(parents=True, exist_ok=True)
        state_file_2.parent.mkdir(parents=True, exist_ok=True)

        results = {"run1": None, "run2": None}

        def write_state_run1():
            state_manager = StateManager(state_file=str(state_file_1))
            data = {"persona": "concurrent_user_1", "workflow": "run1"}
            state_manager.save(step=1, data=data)
            results["run1"] = state_manager.load()

        def write_state_run2():
            state_manager = StateManager(state_file=str(state_file_2))
            data = {"persona": "concurrent_user_2", "workflow": "run2"}
            state_manager.save(step=1, data=data)
            results["run2"] = state_manager.load()

        # Act - Concurrent writes
        thread1 = threading.Thread(target=write_state_run1)
        thread2 = threading.Thread(target=write_state_run2)

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # Assert - Both writes succeeded
        assert results["run1"] is not None
        assert results["run2"] is not None
        assert results["run1"]["step_1"]["persona"] == "concurrent_user_1"
        assert results["run2"]["step_1"]["persona"] == "concurrent_user_2"


# ============================================================================
# AUDIT LAYER 3: Append & Immutability Tests
# ============================================================================

class TestAuditLayer3:
    """
    Layer 3: Audit log append and immutability tests.

    Tests progressive audit trail with multiple events.
    """

    @pytest.mark.layer3
    @pytest.mark.audit
    @pytest.mark.integration
    def test_multiple_events_appended_correctly(self, tmp_path):
        """
        Layer 3: Verify multiple events are appended in order (AT-1.8).

        Progressive audit trail: events should accumulate without overwriting.
        """
        # Arrange
        run_id = "2026-01-24T10:45:00.000000Z"
        audit_dir = tmp_path / "_audit"
        audit_dir.mkdir(exist_ok=True)

        audit_logger = AuditLogger(run_id=run_id, output_dir=str(audit_dir))

        # Act - Log multiple events
        audit_logger.log_gate(
            step=1,
            gate_name="qg_user_input",
            mode="POST",
            result="pass"
        )

        audit_logger.log_gate(
            step=2,
            gate_name="qg_preflight",
            mode="POST",
            result="pass"
        )

        # Assert - Both events in audit log
        audit_file = audit_dir / f"audit_log_{run_id.replace(':', '-')}.json"
        assert audit_file.exists(), "Audit log should exist"

        with open(audit_file, 'r') as f:
            audit_data = json.load(f)

        assert len(audit_data["events"]) == 2, "Should have 2 events"
        assert audit_data["events"][0]["gate"] == "qg_user_input"
        assert audit_data["events"][1]["gate"] == "qg_preflight"

    @pytest.mark.layer3
    @pytest.mark.audit
    @pytest.mark.integration
    def test_existing_events_not_modified(self, tmp_path):
        """
        Layer 3: Verify appending new event doesn't modify existing events.

        Immutability requirement: existing events should remain unchanged.
        """
        # Arrange
        run_id = "2026-01-24T10:50:00.000000Z"
        audit_dir = tmp_path / "_audit"
        audit_dir.mkdir(exist_ok=True)

        audit_logger = AuditLogger(run_id=run_id, output_dir=str(audit_dir))

        # Create initial event
        audit_logger.log_gate(
            step=1,
            gate_name="qg_user_input",
            mode="POST",
            result="pass",
            metadata={"persona": "original"}
        )

        # Read original event for comparison
        audit_file = audit_dir / f"audit_log_{run_id.replace(':', '-')}.json"
        with open(audit_file, 'r') as f:
            original_audit = json.load(f)
        original_event_saved = original_audit["events"][0].copy()

        # Act - Append new event
        audit_logger.log_gate(
            step=2,
            gate_name="qg_preflight",
            mode="POST",
            result="pass"
        )

        # Assert - Original event unchanged
        with open(audit_file, 'r') as f:
            updated_audit = json.load(f)

        assert len(updated_audit["events"]) == 2
        # Compare original event (should be identical)
        assert updated_audit["events"][0]["gate"] == original_event_saved["gate"]
        assert updated_audit["events"][0]["result"] == original_event_saved["result"]
        assert updated_audit["events"][0]["metadata"] == original_event_saved.get("metadata", {})

    @pytest.mark.layer3
    @pytest.mark.audit
    @pytest.mark.integration
    def test_audit_logger_loads_existing_events(self, tmp_path):
        """
        Layer 3: Verify new AuditLogger instance loads existing events.

        Workflow restart scenario: existing events should be preserved.
        """
        # Arrange - Create audit log with events
        run_id = "2026-01-24T10:55:00.000000Z"
        audit_dir = tmp_path / "_audit"
        audit_dir.mkdir(exist_ok=True)

        # First instance - create initial events
        logger1 = AuditLogger(run_id=run_id, output_dir=str(audit_dir))
        logger1.log_gate(step=1, gate_name="qg_user_input", mode="POST", result="pass")
        logger1.log_gate(step=2, gate_name="qg_preflight", mode="POST", result="pass")

        # Act - Create new instance (simulates workflow restart)
        logger2 = AuditLogger(run_id=run_id, output_dir=str(audit_dir))

        # Add new event
        logger2.log_gate(step=3, gate_name="qg_ai_processing", mode="POST", result="pass")

        # Assert - All 3 events present
        audit_file = audit_dir / f"audit_log_{run_id.replace(':', '-')}.json"
        with open(audit_file, 'r') as f:
            audit_data = json.load(f)

        assert len(audit_data["events"]) == 3
        assert audit_data["events"][0]["gate"] == "qg_user_input"
        assert audit_data["events"][1]["gate"] == "qg_preflight"
        assert audit_data["events"][2]["gate"] == "qg_ai_processing"


# ============================================================================
# PROTOCOL LAYER 3: Component Integration Tests
# ============================================================================

class TestProtocolLayer3:
    """
    Layer 3: Tests that components used by Step 1 protocol work together.

    Simulates the Step 1 workflow: State → Audit → Transcript generation.
    """

    @pytest.mark.layer3
    @pytest.mark.protocol
    @pytest.mark.integration
    def test_step1_component_integration_valid_inputs(self, tmp_path):
        """
        Layer 3: Test Step 1 components integrate correctly (AT-1.1).

        Flow:
        1. Save state (StateManager)
        2. Log gate event (AuditLogger)
        3. Generate transcript (TranscriptWriter)

        Verifies: State → Audit → Transcript integration
        """
        # Arrange
        run_id = "2026-01-24T11:00:00.000000Z"
        state_dir = tmp_path / "_state"
        audit_dir = tmp_path / "_audit"

        state_dir.mkdir(exist_ok=True)
        audit_dir.mkdir(exist_ok=True)

        # Step 1 input data
        input_data = {
            "persona": "sales representative",
            "URL": "http://www.automationpractice.pl/index.php",
            "role_name": "SalesRepresentative",
            "workflow": "helios8",
            "raw_requirement": "As a sales representative, I want to submit a service inquiry"
        }

        # Act - Simulate Step 1 protocol actions
        # 1. Save state
        state_file = state_dir / run_id.replace(":", "-") / "workflow_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_manager = StateManager(state_file=str(state_file))
        state_manager.save(step=1, data=input_data)

        # 2. Log audit event
        audit_logger = AuditLogger(run_id=run_id, output_dir=str(audit_dir))
        audit_logger.log_gate(
            step=1,
            gate_name="qg_user_input",
            mode="POST",
            result="pass",
            metadata=input_data
        )

        # 3. Generate transcript
        transcript_writer = TranscriptWriter(
            run_id=run_id,
            audit_dir=audit_dir,
            output_dir=state_dir / run_id.replace(":", "-")
        )
        transcript_path = transcript_writer.generate()

        # Assert - All components created expected output
        # State saved
        assert state_file.exists()
        with open(state_file, 'r') as f:
            state = json.load(f)
        assert state["step_1"]["persona"] == "sales representative"

        # Audit logged
        audit_file = audit_dir / f"audit_log_{run_id.replace(':', '-')}.json"
        assert audit_file.exists()
        with open(audit_file, 'r') as f:
            audit = json.load(f)
        assert audit["events"][0]["gate"] == "qg_user_input"

        # Transcript generated
        assert Path(transcript_path).exists()
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_content = f.read()
        assert "Step 1" in transcript_content or "user_input" in transcript_content
        assert "qg_user_input" in transcript_content

    @pytest.mark.layer3
    @pytest.mark.protocol
    @pytest.mark.integration
    def test_step1_state_isolation_across_runs(self, tmp_path):
        """
        Layer 3: Verify Step 1 state isolation across concurrent runs.

        Tests that two parallel Step 1 executions don't interfere.
        """
        # Arrange
        state_dir = tmp_path / "_state"
        audit_dir = tmp_path / "_audit"
        state_dir.mkdir(exist_ok=True)
        audit_dir.mkdir(exist_ok=True)

        run_id_1 = "2026-01-24T11-05-00.000000Z"
        run_id_2 = "2026-01-24T11-05-01.000000Z"

        input_1 = {"persona": "user1", "workflow": "test1"}
        input_2 = {"persona": "user2", "workflow": "test2"}

        # Act - Simulate two Step 1 runs
        # Run 1
        state_file_1 = state_dir / run_id_1 / "workflow_state.json"
        state_file_1.parent.mkdir(parents=True, exist_ok=True)
        state_manager_1 = StateManager(state_file=str(state_file_1))
        state_manager_1.save(step=1, data=input_1)

        audit_logger_1 = AuditLogger(run_id=run_id_1, output_dir=str(audit_dir))
        audit_logger_1.log_gate(step=1, gate_name="qg_user_input", mode="POST", result="pass")

        # Run 2
        state_file_2 = state_dir / run_id_2 / "workflow_state.json"
        state_file_2.parent.mkdir(parents=True, exist_ok=True)
        state_manager_2 = StateManager(state_file=str(state_file_2))
        state_manager_2.save(step=1, data=input_2)

        audit_logger_2 = AuditLogger(run_id=run_id_2, output_dir=str(audit_dir))
        audit_logger_2.log_gate(step=1, gate_name="qg_user_input", mode="POST", result="pass")

        # Assert - Both runs have separate state/audit
        assert state_file_1.exists()
        assert state_file_2.exists()

        with open(state_file_1, 'r') as f:
            state1 = json.load(f)
        with open(state_file_2, 'r') as f:
            state2 = json.load(f)

        assert state1["step_1"]["persona"] == "user1"
        assert state2["step_1"]["persona"] == "user2"

        # Verify separate audit logs
        audit_file_1 = audit_dir / f"audit_log_{run_id_1}.json"
        audit_file_2 = audit_dir / f"audit_log_{run_id_2}.json"

        assert audit_file_1.exists()
        assert audit_file_2.exists()

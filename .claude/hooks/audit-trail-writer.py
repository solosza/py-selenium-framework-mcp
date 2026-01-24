#!/usr/bin/env python3
"""
Audit Trail Writer Hook - Creates progressive audit trail after each quality gate.

This PostToolUse hook captures gate results and appends them to the audit log.
Uses per-run isolation (tests/_state/<run_id>/ and tests/_audit/audit_log_<run_id>.json).

Architecture:
  Gate passes -> Hook triggers -> Reads workflow_state -> Appends to audit log

Trigger: After any qg_* MCP tool completes with status: pass

Exit codes:
  0 = Success (audit written or not applicable)
  Non-zero exits are logged but don't block (audit is observational)
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime


# Map tool names to step numbers (FIXED: swapped qg_preflight and qg_user_input)
GATE_TO_STEP = {
    'mcp__qa-automation__qg_user_input': 1,      # Step 1 (was step_2)
    'mcp__qa-automation__qg_preflight': 2,       # Step 2 (was step_1)
    'mcp__qa-automation__qg_ai_processing': 3,
    'mcp__qa-automation__qg_test_scenarios': 4,
    'mcp__qa-automation__qg_discovered_elements': 5,
    'mcp__qa-automation__qg_discovery_complete': 5,  # Also Step 5
}

# Map tool names to gate names (for audit logging)
TOOL_TO_GATE = {
    'mcp__qa-automation__qg_user_input': 'qg_user_input',
    'mcp__qa-automation__qg_preflight': 'qg_preflight',
    'mcp__qa-automation__qg_ai_processing': 'qg_ai_processing',
    'mcp__qa-automation__qg_test_scenarios': 'qg_test_scenarios',
    'mcp__qa-automation__qg_discovered_elements': 'qg_discovered_elements',
    'mcp__qa-automation__qg_discovery_complete': 'qg_discovery_complete',
}


def get_project_dir() -> Path:
    """Get project directory from environment or current working directory."""
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR')
    if project_dir:
        return Path(project_dir)
    return Path.cwd()


def get_current_run_id() -> str | None:
    """Get current run_id from session marker."""
    marker = get_project_dir() / 'tests' / '_state' / '.current_run_id'
    if not marker.exists():
        return None

    try:
        return marker.read_text().strip()
    except Exception:
        return None


def get_workflow_state(run_id: str) -> dict:
    """Read current workflow state from per-run isolation directory."""
    state_file = get_project_dir() / 'tests' / '_state' / run_id / 'workflow_state.json'
    if not state_file.exists():
        return {}

    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return {}


def get_audit_file(run_id: str) -> Path:
    """Get audit file path for current run_id."""
    audit_dir = get_project_dir() / 'tests' / '_audit'
    audit_dir.mkdir(parents=True, exist_ok=True)
    return audit_dir / f'audit_log_{run_id}.json'


def append_to_audit(audit_file: Path, step: int, gate_name: str, metadata: dict):
    """Append gate validation event to audit log."""
    # Read existing audit or create new structure
    if audit_file.exists():
        try:
            with open(audit_file, 'r') as f:
                audit = json.load(f)
        except (json.JSONDecodeError, Exception):
            # If file is corrupted, start fresh
            run_id = audit_file.stem.replace('audit_log_', '')
            audit = {
                'workflow_id': run_id,
                'events': []
            }
    else:
        # Create new audit log
        run_id = audit_file.stem.replace('audit_log_', '')
        audit = {
            'workflow_id': run_id,
            'events': []
        }

    # Create new event entry
    event = {
        'type': 'gate_validation',
        'step': step,
        'gate': gate_name,
        'mode': 'POST',
        'result': 'pass',
        'timestamp': datetime.now().isoformat() + 'Z',
        'metadata': metadata
    }

    # Append event
    audit['events'].append(event)

    # Write updated audit
    try:
        with open(audit_file, 'w') as f:
            json.dump(audit, f, indent=2)
    except Exception as e:
        sys.stderr.write(f"Warning: Could not write audit file: {e}\n")


def main():
    """
    Main hook logic.

    Reads PostToolUse data from stdin, checks if it's a gate tool,
    and appends to audit trail if gate passed.
    """
    try:
        # Read tool result from stdin
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception):
        # Can't parse input, exit silently (don't block)
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    tool_result = data.get('tool_result', {})

    # Check if this is a quality gate tool
    if tool_name not in GATE_TO_STEP:
        sys.exit(0)

    # Parse tool result (it's a string containing JSON)
    try:
        if isinstance(tool_result, str):
            result = json.loads(tool_result)
        else:
            result = tool_result
    except (json.JSONDecodeError, Exception):
        result = {'status': 'unknown'}

    # Only log if gate passed
    if result.get('status') != 'pass':
        sys.exit(0)

    # Get current run_id
    run_id = get_current_run_id()
    if not run_id:
        # No active workflow, exit silently
        sys.exit(0)

    # Get step number and gate name
    step = GATE_TO_STEP[tool_name]
    gate_name = TOOL_TO_GATE[tool_name]

    # Get current workflow state
    workflow_state = get_workflow_state(run_id)

    # Extract metadata from workflow state for this step
    step_key = f'step_{step}'
    metadata = workflow_state.get(step_key, {})

    # Get audit file
    audit_file = get_audit_file(run_id)

    # Append to audit
    append_to_audit(audit_file, step, gate_name, metadata)

    sys.exit(0)


if __name__ == '__main__':
    main()

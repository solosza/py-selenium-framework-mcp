#!/usr/bin/env python3
"""
Audit Trail Writer Hook - Creates progressive audit trail after each quality gate.

This PostToolUse hook captures gate results and appends them to a timestamped
audit file. Ensures complete traceability for regulated verticals (healthcare,
finance, legal, insurance).

Architecture:
  Gate passes -> Hook triggers -> Reads workflow_state -> Appends to audit file

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


# Map tool names to step numbers
GATE_TO_STEP = {
    'mcp__qa-automation__qg_preflight': 'step_1',
    'mcp__qa-automation__qg_user_input': 'step_2',
    'mcp__qa-automation__qg_ai_processing': 'step_3',
    'mcp__qa-automation__qg_test_scenarios': 'step_4',
    'mcp__qa-automation__qg_discovered_elements': 'step_5',
    'mcp__qa-automation__qg_page_object': 'step_6',
    'mcp__qa-automation__qg_task': 'step_7',
    'mcp__qa-automation__qg_role': 'step_8',
    'mcp__qa-automation__qg_test_runner': 'step_9',
    'mcp__qa-automation__qg_save_run': 'step_10',
}


def get_project_dir() -> Path:
    """Get project directory from environment or current working directory."""
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR')
    if project_dir:
        return Path(project_dir)
    return Path.cwd()


def get_workflow_state() -> dict:
    """Read current workflow state."""
    state_file = get_project_dir() / 'mcp_server' / 'state' / 'workflow_state.json'
    if not state_file.exists():
        return {}

    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return {}


def get_audit_dir() -> Path:
    """Get or create audit directory."""
    audit_dir = get_project_dir() / 'tests' / '_audit'
    audit_dir.mkdir(parents=True, exist_ok=True)
    return audit_dir


def get_audit_filename(workflow_state: dict) -> str:
    """Generate audit filename from workflow state."""
    # Get workflow name from step_2 if available
    workflow = 'unknown'
    intent = 'workflow'

    if 'step_2' in workflow_state:
        workflow = workflow_state['step_2'].get('workflow', 'unknown')

    if 'step_3' in workflow_state:
        intent = workflow_state['step_3'].get('intent', 'workflow')

    # Use current date/time for unique filename
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')

    return f"{timestamp}_{workflow}_{intent}.json"


def get_or_create_audit_file(workflow_state: dict) -> Path:
    """Get existing audit file or create new one for this workflow run."""
    audit_dir = get_audit_dir()

    # Check for existing audit file for this session
    # We use a marker file to track the current audit session
    session_marker = get_project_dir() / 'mcp_server' / 'state' / '.audit_session'

    if session_marker.exists():
        try:
            audit_filename = session_marker.read_text().strip()
            audit_file = audit_dir / audit_filename
            if audit_file.exists():
                return audit_file
        except Exception:
            pass

    # Create new audit file
    audit_filename = get_audit_filename(workflow_state)
    audit_file = audit_dir / audit_filename

    # Save session marker
    try:
        session_marker.parent.mkdir(parents=True, exist_ok=True)
        session_marker.write_text(audit_filename)
    except Exception:
        pass

    return audit_file


def strip_code_from_step(step_data: dict) -> dict:
    """Remove raw code blobs from step data to reduce audit file size."""
    stripped = {}
    for key, value in step_data.items():
        # Skip keys ending in '_code' (pom_code, task_code, role_code, test_code)
        if key.endswith('_code'):
            stripped[key] = '[CODE_STRIPPED_FOR_AUDIT]'
        else:
            stripped[key] = value
    return stripped


def append_to_audit(audit_file: Path, step_name: str, step_data: dict, gate_result: dict):
    """Append step data to audit file."""
    # Read existing audit or create new structure
    if audit_file.exists():
        try:
            with open(audit_file, 'r') as f:
                audit = json.load(f)
        except (json.JSONDecodeError, Exception):
            audit = {}
    else:
        audit = {
            'audit_metadata': {
                'created': datetime.now().isoformat(),
                'platform': 'qa-automation',
                'version': '1.0'
            }
        }

    # Update metadata timestamp
    audit['audit_metadata']['last_updated'] = datetime.now().isoformat()

    # Strip code from step data to reduce file size
    stripped_data = strip_code_from_step(step_data) if step_data else {}

    # Add step data with gate result
    audit[step_name] = {
        'timestamp': datetime.now().isoformat(),
        'gate_result': gate_result.get('status', 'unknown'),
        'data': stripped_data
    }

    # Write updated audit
    try:
        with open(audit_file, 'w') as f:
            json.dump(audit, f, indent=2)
    except Exception as e:
        sys.stderr.write(f"Warning: Could not write audit file: {e}\n")


def clear_session_marker():
    """Clear session marker after Step 10 completes (workflow done)."""
    session_marker = get_project_dir() / 'mcp_server' / 'state' / '.audit_session'
    try:
        if session_marker.exists():
            session_marker.unlink()
    except Exception:
        pass


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

    step_name = GATE_TO_STEP[tool_name]

    # Get current workflow state
    workflow_state = get_workflow_state()

    # Get step data from workflow state
    step_data = workflow_state.get(step_name, {})

    # Get or create audit file
    audit_file = get_or_create_audit_file(workflow_state)

    # Append to audit
    append_to_audit(audit_file, step_name, step_data, result)

    # Clear session marker after Step 10 (workflow complete)
    if step_name == 'step_10':
        clear_session_marker()

    sys.exit(0)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
QA Gate Enforcer Hook - Prevents writes to protected paths without gate validation.

This PreToolUse hook intercepts Write/Edit tool calls and blocks them if the
required quality gate has not passed. This ensures AI cannot bypass the
10-step QA workflow validation.

Architecture:
  AI generates code -> AI tries Write -> Hook intercepts -> Checks state -> Block/Allow

Exit codes:
  0 = Allow (gate passed or not a protected path)
  2 = Block (gate not passed, write rejected)
"""

import json
import sys
import os
from pathlib import Path


# Protected paths that require gate validation
PROTECTED_PATHS = {
    'framework/pages/': 'step_6',      # POM requires qg_page_object POST
    'framework/tasks/': 'step_7',      # Task requires qg_task POST
    'framework/roles/': 'step_8',      # Role requires qg_role POST
    'tests/': 'step_9',                # Test requires qg_test_runner POST
}

# Core infrastructure (ALWAYS blocked, even with gates passed)
CORE_INFRASTRUCTURE = [
    'framework/interfaces/',
    'framework/resources/utilities/',
    'framework/resources/config.py',
    'framework/resources/chromedriver/',
]

# What metadata key must exist for each step to be considered "passed"
REQUIRED_METADATA = {
    'step_6': 'pom_metadata',
    'step_7': 'task_metadata',
    'step_8': 'role_metadata',
    'step_9': 'test_metadata',
}


def normalize_path(file_path: str) -> str:
    """Convert Windows paths to forward slashes for consistent matching."""
    return file_path.replace('\\', '/')


def get_required_step(file_path: str) -> str | None:
    """
    Determine which step's gate must pass for this file path.

    Returns:
        Step key (e.g., 'step_6') if protected, None if not protected.
    """
    normalized = normalize_path(file_path)

    # Exclude development tests (unit tests for gates themselves)
    if '_dev_tests/' in normalized or '/_dev_tests/' in normalized:
        return None

    for protected_prefix, step in PROTECTED_PATHS.items():
        if protected_prefix in normalized:
            return step

    return None


def is_gate_passed(state: dict, step: str) -> bool:
    """
    Check if the required gate has passed for a step.

    A gate is considered passed if the step exists in state and contains
    the required metadata key with non-empty content.
    """
    if step not in state:
        return False

    step_data = state[step]
    required_key = REQUIRED_METADATA.get(step)

    if required_key is None:
        return False

    # Check if the metadata key exists and has content
    metadata = step_data.get(required_key)
    if metadata is None:
        return False

    # For dicts, check they have at least some keys
    if isinstance(metadata, dict) and len(metadata) == 0:
        return False

    return True


def get_state_file_path() -> Path:
    """
    Get the path to workflow_state.json (DEF-052 location).

    State file moved from mcp_server/state/ to tests/_state/{run_id}/ for
    per-run isolation. This function finds the most recent run_id directory.
    """
    # Try environment variable first
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR')
    if project_dir:
        base = Path(project_dir)
    else:
        # Find project root by looking for mcp_server
        cwd = Path.cwd()
        base = None
        for parent in [cwd] + list(cwd.parents):
            if (parent / 'mcp_server').exists():
                base = parent
                break
        if base is None:
            base = cwd

    # DEF-052: State now lives in tests/_state/{run_id}/
    state_dir = base / 'tests' / '_state'
    if not state_dir.exists():
        # No state directory = no workflow running
        return base / 'mcp_server' / 'state' / 'workflow_state.json'  # Dummy path

    # Find most recent run_id directory
    run_dirs = sorted(
        [d for d in state_dir.iterdir() if d.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    if run_dirs:
        return run_dirs[0] / 'workflow_state.json'

    # No run directories found
    return base / 'mcp_server' / 'state' / 'workflow_state.json'  # Dummy path


def main():
    """
    Main hook logic.

    Reads tool call from stdin, checks if it's a protected write,
    and blocks if the required gate hasn't passed.
    """
    try:
        # Read tool call data from stdin
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception) as e:
        # If we can't parse input, allow the operation (fail open for non-write tools)
        sys.exit(0)

    tool_name = data.get('tool_name', '')
    tool_input = data.get('tool_input', {})

    # Only enforce on Write and Edit tools
    if tool_name not in ('Write', 'Edit'):
        sys.exit(0)

    file_path = tool_input.get('file_path', '')
    if not file_path:
        sys.exit(0)

    # Block core infrastructure (never allow modifications, even with gates passed)
    normalized = normalize_path(file_path)
    for core_path in CORE_INFRASTRUCTURE:
        if core_path in normalized:
            sys.stderr.write(
                f"BLOCKED: Core infrastructure is write-protected.\n"
                f"File: {file_path}\n"
                f"Protected path: {core_path}\n"
                f"Core framework code cannot be modified during QA workflows.\n"
            )
            sys.exit(2)

    # Check if this is a protected path
    required_step = get_required_step(file_path)
    if required_step is None:
        # Not a protected path, allow
        sys.exit(0)

    # Load workflow state
    state_file = get_state_file_path()

    if not state_file.exists():
        sys.stderr.write(
            f"BLOCKED: No QA workflow state found.\n"
            f"Cannot write to protected path: {file_path}\n"
            f"Run the 10-step QA workflow with quality gates first.\n"
            f"Expected state file: {state_file}\n"
        )
        sys.exit(2)

    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        sys.stderr.write(
            f"BLOCKED: Cannot read workflow state.\n"
            f"Error: {e}\n"
        )
        sys.exit(2)

    # Check if the required gate has passed
    if not is_gate_passed(state, required_step):
        required_metadata = REQUIRED_METADATA.get(required_step, 'unknown')
        sys.stderr.write(
            f"BLOCKED: Quality gate not passed.\n"
            f"File: {file_path}\n"
            f"Required: {required_step} must have {required_metadata}\n"
            f"Run qg_* quality gates before writing to protected paths.\n"
        )
        sys.exit(2)

    # Gate passed, allow the write
    sys.exit(0)


if __name__ == '__main__':
    main()

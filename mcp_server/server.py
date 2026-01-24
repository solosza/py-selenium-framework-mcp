#!/usr/bin/env python3
"""
MCP Server for QA Test Automation Framework

Provides tools following the 4-layer architecture workflow:

ACTIVE TOOLS (4-Step Pair Programming Workflow v3.1):
1. discover_page_elements - Page URL → discovered elements (Tool 2)

QUALITY GATES (Steps 1-4):
- qg_user_input (Step 1) - User input validation
- qg_preflight (Step 2) - Pre-flight configuration validation
- qg_ai_processing (Step 3) - AI processing validation
- qg_discovered_elements (Step 4) - Discovered elements validation (PRE+POST)
- qg_discovery_complete (Step 4) - Discovery completion checkpoint

PLANNED (Tools 7-11):
7. list_tests - Catalog all tests
8. get_framework_structure - Map framework architecture
9. run_test - Execute tests
10. analyze_failure - AI-powered debugging
11. get_test_coverage - Coverage tracking

NOTE: Tools 3-6 (autonomous code generators) and construction gates (Steps 6-9)
were archived to _archived/autonomous_workflow_v1/ on 2026-01-22. New workflow
uses collaborative construction (AI builds manually with Edit/Write tools).
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server import Server
from mcp.types import Tool, TextContent

# Import tool implementations (Tool 2 active)
from tools.tool_02_discover_page_elements import discover_elements as discover_page_elements
# Tools 1, 3-6 archived to _archived/autonomous_workflow_v1/tools/ (2026-01-22, 2026-01-23)

# Import quality gates (Steps 1-4 active)
from tools.gates.qg_preflight import QGPreflight
from tools.gates.qg_user_input import QGUserInput
from tools.gates.qg_ai_processing import QGAIProcessing
# qg_test_scenarios archived on 2026-01-23 (redundant Tool 1)
from tools.gates.qg_discovered_elements import QGDiscoveredElements
from tools.gates.qg_discovery_complete import QGDiscoveryComplete
# Construction gates archived to _archived/autonomous_workflow_v1/gates/ on 2026-01-22

# Import operations (Tool 9: run_test)
from tools.operations.run_test import run_test_async

# Tools 7-11 not yet implemented - stub functions
async def list_tests(arguments: dict) -> str:
    return '{"status": "not_implemented", "message": "Tool 7 (list_tests) is planned but not yet implemented"}'

async def get_framework_structure(arguments: dict) -> str:
    return '{"status": "not_implemented", "message": "Tool 8 (get_framework_structure) is planned but not yet implemented"}'

async def run_test(arguments: dict) -> str:
    """Tool 9: Execute pytest test with standard flags and capture results."""
    return await run_test_async(arguments)

async def analyze_failure(arguments: dict) -> str:
    return '{"status": "not_implemented", "message": "Tool 10 (analyze_failure) is planned but not yet implemented"}'

async def get_test_coverage(arguments: dict) -> str:
    return '{"status": "not_implemented", "message": "Tool 11 (get_test_coverage) is planned but not yet implemented"}'


# =============================================================================
# Quality Gate Wrapper Functions (Steps 1-10)
# =============================================================================

async def qg_preflight(arguments: dict) -> str:
    """Step 1: Pre-flight configuration validation (POST-only)."""
    result = QGPreflight.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_user_input(arguments: dict) -> str:
    """Step 2: User input validation (POST-only)."""
    result = QGUserInput.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_ai_processing(arguments: dict) -> str:
    """Step 3: AI processing validation (POST-only)."""
    result = QGAIProcessing.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_discovered_elements(arguments: dict) -> str:
    """Step 4: Discovered elements validation (PRE+POST). Requires 'mode' field."""
    result = QGDiscoveredElements.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_discovery_complete(arguments: dict) -> str:
    """Step 4: Discovery completion checkpoint (PRE-only). Validates all pages discovered."""
    result = QGDiscoveryComplete.validate_pre({})
    return json.dumps(result, indent=2)


# =============================================================================
# ARCHIVED GATES (moved to _archived/autonomous_workflow_v1/gates/ on 2026-01-22)
# =============================================================================
# - qg_page_object (Step 6) - No longer needed with collaborative construction
# - qg_task (Step 7) - No longer needed with collaborative construction
# - qg_role (Step 8) - No longer needed with collaborative construction
# - qg_test_runner (Step 9) - No longer needed with collaborative construction
# - qg_save_run (Step 10) - No longer needed with collaborative construction
# - qg_execution (Step 11) - No longer needed with collaborative construction
# - qg_workflow_complete (Step 11) - No longer needed with collaborative construction


# Initialize MCP server
server = Server("qa-automation-framework")


@server.list_tools()
async def list_available_tools() -> list[Tool]:
    """Register all 11 MCP tools."""
    return [
        # Phase 1: Element Discovery (Tool 2)
        Tool(
            name="discover_page_elements",
            description="Discover interactive elements on page (just-in-time, right before POM generation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Page URL to analyze"
                    },
                    "page_name": {
                        "type": "string",
                        "description": "Suggested page object name"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "Workflow/domain for organizing discovered elements"
                    },
                    "wait_for_state": {
                        "type": "string",
                        "description": "Wait condition before discovery (e.g., 'networkidle', 'domcontentloaded')"
                    }
                },
                "required": ["url"]
            }
        ),

        # Phase 3: Framework Discovery
        Tool(
            name="list_tests",
            description="Catalog all available tests, organized by workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow": {
                        "type": "string",
                        "description": "Optional filter by workflow"
                    }
                }
            }
        ),

        Tool(
            name="get_framework_structure",
            description="Map framework architecture (layers, components, coverage)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        # Phase 7: Test Execution
        Tool(
            name="run_test",
            description="Execute test(s) and return structured results",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_path": {
                        "type": "string",
                        "description": "Pytest path (e.g., tests/auth/test_login.py::test_valid_login)"
                    },
                    "marker": {
                        "type": "string",
                        "description": "Optional pytest marker filter (e.g., smoke)"
                    }
                },
                "required": ["test_path"]
            }
        ),

        # Phase 8: Failure Analysis
        Tool(
            name="analyze_failure",
            description="AI-powered debugging for failed tests with actionable suggestions",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_name": {
                        "type": "string",
                        "description": "Name of failed test"
                    },
                    "run_id": {
                        "type": "string",
                        "description": "Optional specific run timestamp"
                    }
                },
                "required": ["test_name"]
            }
        ),

        # Phase 9: Coverage Tracking
        Tool(
            name="get_test_coverage",
            description="Calculate test coverage by comparing designed scenarios vs implemented tests",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow": {
                        "type": "string",
                        "description": "Optional filter by workflow"
                    }
                }
            }
        ),

        # =================================================================
        # Quality Gates (Steps 1-10)
        # =================================================================

        # Step 2: Pre-flight Configuration (POST-only)
        Tool(
            name="qg_preflight",
            description="Step 2 quality gate: Validate pre-flight configuration (credential_strategy, test_data_location, browser_config, timeout_config)",
            inputSchema={
                "type": "object",
                "properties": {
                    "credential_strategy": {
                        "type": "string",
                        "description": "Credential approach (e.g., static, dynamic, self-contained, none)"
                    },
                    "test_data_location": {
                        "type": "string",
                        "description": "Test data location (e.g., shared, workflow, both, none)"
                    },
                    "browser_config": {
                        "type": "object",
                        "description": "Browser configuration (e.g., {\"headless\": false})",
                        "properties": {
                            "headless": {
                                "type": "boolean",
                                "description": "Whether to run browser in headless mode (must be false for pair programming)"
                            }
                        },
                        "required": ["headless"]
                    },
                    "timeout_config": {
                        "type": "object",
                        "description": "Timeout configuration (e.g., {\"enabled\": true, \"threshold_seconds\": 30})",
                        "properties": {
                            "enabled": {
                                "type": "boolean",
                                "description": "Whether timeout monitoring is enabled"
                            },
                            "threshold_seconds": {
                                "type": "number",
                                "description": "Timeout threshold in seconds (required if enabled=true)"
                            }
                        },
                        "required": ["enabled"]
                    }
                },
                "required": ["credential_strategy", "test_data_location", "browser_config", "timeout_config"]
            }
        ),

        # Step 2: User Input (POST-only)
        Tool(
            name="qg_user_input",
            description="Step 2 quality gate: Validate user input (persona, URL, role_name, workflow)",
            inputSchema={
                "type": "object",
                "properties": {
                    "persona": {
                        "type": "string",
                        "description": "User persona (e.g., 'As a registered user')"
                    },
                    "URL": {
                        "type": "string",
                        "description": "Target page URL"
                    },
                    "role_name": {
                        "type": "string",
                        "description": "Derived role name (e.g., RegisteredUser)"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "Workflow/domain (e.g., auth, catalog, cart, checkout, or custom)"
                    },
                    "raw_requirement": {
                        "type": "string",
                        "description": "Original user requirement text"
                    }
                },
                "required": ["persona", "URL", "role_name", "workflow"]
            }
        ),

        # Step 3: AI Processing (POST-only)
        Tool(
            name="qg_ai_processing",
            description="Step 3 quality gate: Validate AI processing output (bdd_scenarios, expected_states, intent)",
            inputSchema={
                "type": "object",
                "properties": {
                    "bdd_scenarios": {
                        "type": "array",
                        "description": "BDD scenarios with given/when/then",
                        "items": {"type": "object"}
                    },
                    "expected_states": {
                        "type": "array",
                        "description": "Expected state names for POM state-check methods",
                        "items": {"type": "string"}
                    },
                    "intent": {
                        "type": "string",
                        "description": "User intent (e.g., login, browse, checkout)"
                    }
                },
                "required": ["bdd_scenarios", "expected_states", "intent"]
            }
        ),

        # Step 4: Discovered Elements (PRE+POST)
        Tool(
            name="qg_discovered_elements",
            description="Step 4 quality gate: Validate element discovery (PRE+POST mode). PRE checks Step 3 complete, POST validates elements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Validation mode: PRE (before Tool 2) or POST (after Tool 2)",
                        "enum": ["PRE", "POST"]
                    },
                    "url": {
                        "type": "string",
                        "description": "PRE mode: Target page URL"
                    },
                    "page_name": {
                        "type": "string",
                        "description": "Page object class name (PascalCase)"
                    },
                    "credential_strategy": {
                        "type": "string",
                        "description": "PRE mode: Credential strategy from Step 1 (e.g., none, static, dynamic, self-contained)"
                    },
                    "discovery_method": {
                        "type": "string",
                        "description": "PRE mode: Discovery method (e.g., tool2, playwright)"
                    },
                    "elements": {
                        "type": "array",
                        "description": "POST mode: Discovered elements from Tool 2 or snapshot extraction",
                        "items": {"type": "object"}
                    }
                },
                "required": ["mode"]
            }
        ),

        # Step 4: Discovery Complete Checkpoint (PRE-only)
        Tool(
            name="qg_discovery_complete",
            description="Step 4 checkpoint: Validate all pages have input AND output elements discovered (PRE-only). Two-pass discovery validation.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )

        # =============================================================================
        # ARCHIVED GATES - Removed 2026-01-22 (see _archived/autonomous_workflow_v1/)
        # =============================================================================
        # - qg_page_object (Step 6)
        # - qg_task (Step 7)
        # - qg_role (Step 8)
        # - qg_test_runner (Step 9)
        # - qg_save_run (Step 10)
        # - qg_execution (Step 11)
        # - qg_workflow_complete (Step 11 meta-gate)
    ]



@server.call_tool()
async def call_tool_handler(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to appropriate handler."""

    # Tool routing (matches tool file numbers)
    handlers = {
        # Tools: Active (4-step workflow v3.1)
        "discover_page_elements": discover_page_elements,                   # Tool 2
        # Tools 7-11: Planned (stubs)
        "list_tests": list_tests,
        "get_framework_structure": get_framework_structure,
        "run_test": run_test,
        "analyze_failure": analyze_failure,
        "get_test_coverage": get_test_coverage,
        # Quality Gates (Steps 1-4)
        "qg_preflight": qg_preflight,                       # Step 2
        "qg_user_input": qg_user_input,                     # Step 1
        "qg_ai_processing": qg_ai_processing,               # Step 3
        "qg_discovered_elements": qg_discovered_elements,   # Step 4
        "qg_discovery_complete": qg_discovery_complete,     # Step 4 (checkpoint)
    }

    if name not in handlers:
        return [TextContent(
            type="text",
            text=f"Error: Unknown tool '{name}'"
        )]

    try:
        result = await handlers[name](arguments)
        return [TextContent(
            type="text",
            text=result
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def main():
    """Start MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

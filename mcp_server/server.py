#!/usr/bin/env python3
"""
MCP Server for QA Test Automation Framework

Provides 11 tools following test-first workflow:
1. generate_tests_from_user_story - Requirements → test scenarios
2. generate_test_template - Scenario → pytest test (TEST FIRST)
3. generate_role - Test requirements → role class
4. generate_task - Test requirements → task methods
5. discover_page_elements - Page URL → discovered elements (just-in-time)
6. generate_page_object - Elements → POM code
7. list_tests - Catalog all tests
8. get_framework_structure - Map framework architecture
9. run_test - Execute tests
10. analyze_failure - AI-powered debugging
11. get_test_coverage - Coverage tracking
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server import Server
from mcp.types import Tool, TextContent

# Import tool implementations
from tools.tool_01_generate_tests_from_user_story import generate_tests_from_user_story
from tools.tool_02_generate_test_template import generate_test_template
from tools.tool_03_generate_role import generate_role
from tools.tool_04_generate_task import generate_task
from tools.tool_05_discover_page_elements import discover_page_elements
from tools.tool_06_generate_page_object import generate_page_object
from tools.tool_07_list_tests import list_tests
from tools.tool_08_get_framework_structure import get_framework_structure
from tools.tool_09_run_test import run_test
from tools.tool_10_analyze_failure import analyze_failure
from tools.tool_11_get_test_coverage import get_test_coverage


# Initialize MCP server
server = Server("qa-automation-framework")


@server.list_tools()
async def list_available_tools() -> list[Tool]:
    """Register all 11 MCP tools."""
    return [
        # Phase 1: Requirements Analysis
        Tool(
            name="generate_tests_from_user_story",
            description="Convert user story into test scenarios (Given-When-Then format)",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_story": {
                        "type": "string",
                        "description": "User story with acceptance criteria"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "Target workflow (auth, catalog, cart, checkout)",
                        "enum": ["auth", "catalog", "cart", "checkout"]
                    }
                },
                "required": ["user_story", "workflow"]
            }
        ),

        # Phase 2: Test-First Development
        Tool(
            name="generate_test_template",
            description="Generate pytest test code from scenario (TEST FIRST approach)",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_name": {
                        "type": "string",
                        "description": "Test function name (e.g., test_add_to_cart)"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "Workflow category",
                        "enum": ["auth", "catalog", "cart", "checkout"]
                    },
                    "scenario": {
                        "type": "object",
                        "description": "Test scenario with given/when/then"
                    }
                },
                "required": ["test_name", "workflow"]
            }
        ),

        # Phase 3: Supporting Framework - Role
        Tool(
            name="generate_role",
            description="Generate role class from test requirements",
            inputSchema={
                "type": "object",
                "properties": {
                    "role_name": {
                        "type": "string",
                        "description": "Role name (e.g., RegisteredUser, GuestUser)"
                    },
                    "capabilities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "What this role can do (e.g., can_login, has_cart_items)"
                    },
                    "credentials": {
                        "type": "object",
                        "description": "Optional user credentials"
                    }
                },
                "required": ["role_name"]
            }
        ),

        # Phase 3: Supporting Framework - Task
        Tool(
            name="generate_task",
            description="Generate task workflow methods from test requirements",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_name": {
                        "type": "string",
                        "description": "Task class name (e.g., CatalogTasks, CartTasks)"
                    },
                    "workflow_description": {
                        "type": "string",
                        "description": "Description of workflow steps"
                    }
                },
                "required": ["task_name"]
            }
        ),

        # Phase 4: Just-in-Time Element Discovery
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
                    }
                },
                "required": ["url"]
            }
        ),

        # Phase 5: POM Generation
        Tool(
            name="generate_page_object",
            description="Generate page object code from discovered elements",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_name": {
                        "type": "string",
                        "description": "Page object class name"
                    },
                    "elements": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Elements from discover_page_elements"
                    }
                },
                "required": ["page_name", "elements"]
            }
        ),

        # Phase 6: Framework Discovery
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
                    },
                    "browser": {
                        "type": "string",
                        "description": "Optional browser override",
                        "enum": ["chrome", "firefox", "edge"]
                    },
                    "headless": {
                        "type": "boolean",
                        "description": "Optional headless mode override"
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
        )
    ]


@server.call_tool()
async def call_tool_handler(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to appropriate handler."""

    # Tool routing
    handlers = {
        "generate_tests_from_user_story": generate_tests_from_user_story,
        "generate_test_template": generate_test_template,
        "generate_role": generate_role,
        "generate_task": generate_task,
        "discover_page_elements": discover_page_elements,
        "generate_page_object": generate_page_object,
        "list_tests": list_tests,
        "get_framework_structure": get_framework_structure,
        "run_test": run_test,
        "analyze_failure": analyze_failure,
        "get_test_coverage": get_test_coverage
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

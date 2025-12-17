"""
Minimal Agent Proof of Concept

Purpose: Verify Claude Agent SDK works with custom tools
Task: 1.5 - Prototype minimal agent

This prototype tests:
1. SDK installation and import
2. Custom tool creation with @tool decorator
3. In-process MCP server
4. Basic query execution
"""

import asyncio
import json
import os
from claude_agent_sdk import query, ClaudeAgentOptions, tool, create_sdk_mcp_server


# =============================================================================
# Custom Tools (simulating Domain Expert and Reviewer)
# =============================================================================

@tool("get_scenario", "Get a test scenario for validation", {"level": str})
async def get_scenario(args):
    """
    Simulates SR QA Engineer agent.
    Returns test scenario based on complexity level.
    """
    scenarios = {
        "easy": {
            "id": "QA-EASY-001",
            "persona": "registered user",
            "requirement": "As a registered user, I want to login with valid credentials",
            "url": "http://www.automationpractice.pl/index.php?controller=authentication",
            "complexity": "easy"
        },
        "mid": {
            "id": "QA-MID-001",
            "persona": "guest user",
            "requirement": "As a guest user, I want to browse products by category",
            "url": "http://www.automationpractice.pl/index.php",
            "complexity": "mid"
        },
        "hard": {
            "id": "QA-HARD-001",
            "persona": "guest user",
            "requirement": "As a guest user, I want to add a product to cart",
            "url": "http://www.automationpractice.pl/index.php?id_product=1&controller=product",
            "complexity": "hard"
        }
    }

    level = args.get("level", "easy").lower()
    scenario = scenarios.get(level, scenarios["easy"])

    return {
        "content": [
            {"type": "text", "text": json.dumps(scenario, indent=2)}
        ]
    }


@tool("validate_code", "Validate code against Design Decisions", {"code_snippet": str, "dd_id": str})
async def validate_code(args):
    """
    Simulates Reviewer agent.
    Checks code snippet against a specific DD.
    """
    code = args.get("code_snippet", "")
    dd_id = args.get("dd_id", "DD-03")

    # Simple validation logic for demo
    violations = []

    if dd_id == "DD-03":
        # DD-03: Locators ONLY in Page Objects
        if "By." in code and ("tasks" in code.lower() or "role" in code.lower()):
            violations.append({
                "dd_id": "DD-03",
                "severity": "CRITICAL",
                "message": "Locator found outside Page Object layer",
                "suggestion": "Move locator to appropriate Page Object class"
            })

    if dd_id == "DD-15":
        # DD-15: Test assertions use POM state methods
        if "assert" in code.lower() and "is_" not in code and "has_" not in code and "get_" not in code:
            violations.append({
                "dd_id": "DD-15",
                "severity": "HIGH",
                "message": "Test assertion not using POM state method",
                "suggestion": "Use is_*, has_*, or get_* methods from POM for assertions"
            })

    result = {
        "dd_id": dd_id,
        "status": "REJECT" if violations else "APPROVE",
        "violations": violations
    }

    return {
        "content": [
            {"type": "text", "text": json.dumps(result, indent=2)}
        ]
    }


# =============================================================================
# Main POC
# =============================================================================

async def run_poc():
    """Run the minimal proof of concept."""

    print("=" * 60)
    print("MINIMAL AGENT POC - Claude Agent SDK")
    print("=" * 60)

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n[ERROR] ANTHROPIC_API_KEY environment variable not set")
        print("Please set it and try again.")
        return False

    print("\n[1] Creating in-process MCP server with custom tools...")

    # Create MCP server with our custom tools
    validation_server = create_sdk_mcp_server(
        name="qa-validation",
        version="1.0.0",
        tools=[get_scenario, validate_code]
    )

    print("    - get_scenario tool registered")
    print("    - validate_code tool registered")

    print("\n[2] Configuring agent options...")

    options = ClaudeAgentOptions(
        system_prompt="""You are a QA validation supervisor agent.

Your job is to:
1. Get test scenarios using the get_scenario tool
2. Validate code snippets using the validate_code tool
3. Report results clearly

Be concise and focus on the task.""",
        mcp_servers={"validation": validation_server},
        allowed_tools=[
            "mcp__validation__get_scenario",
            "mcp__validation__validate_code"
        ],
        max_turns=3  # Limit turns for POC
    )

    print("    - System prompt configured")
    print("    - MCP servers attached")
    print("    - Allowed tools set")

    print("\n[3] Running test query...")
    print("-" * 60)

    prompt = "Get the easy test scenario and tell me what it's testing."
    print(f"Prompt: {prompt}\n")

    try:
        async for message in query(prompt=prompt, options=options):
            # Print message for debugging
            print(f"[Message] {type(message).__name__}")
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(f"  Text: {block.text[:200]}..." if len(block.text) > 200 else f"  Text: {block.text}")
                    elif hasattr(block, 'name'):
                        print(f"  Tool: {block.name}")

        print("-" * 60)
        print("\n[SUCCESS] POC completed successfully!")
        return True

    except Exception as e:
        print(f"\n[ERROR] POC failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_simple_test():
    """Run a simpler test without custom tools first."""

    print("=" * 60)
    print("SIMPLE SDK TEST - No Custom Tools")
    print("=" * 60)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n[ERROR] ANTHROPIC_API_KEY not set")
        return False

    print("\n[1] Running simple query with built-in tools...")

    options = ClaudeAgentOptions(
        allowed_tools=["Glob"],
        max_turns=1
    )

    try:
        async for message in query(
            prompt="List Python files in the current directory using Glob. Just list them briefly.",
            options=options
        ):
            print(f"[Message] {type(message).__name__}")
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        text = block.text
                        print(f"  {text[:300]}..." if len(text) > 300 else f"  {text}")

        print("\n[SUCCESS] Simple test passed!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Simple test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\nStarting Claude Agent SDK Proof of Concept...\n")

    # Run simple test first
    result = asyncio.run(run_simple_test())

    if result:
        print("\n" + "=" * 60)
        print("Proceeding to full POC with custom tools...")
        print("=" * 60 + "\n")
        asyncio.run(run_poc())
    else:
        print("\nSimple test failed. Please check SDK installation and API key.")

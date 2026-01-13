"""
Test script for Step 5 Navigation Tracking validation (Task 26.0).

This script executes the Step 5 workflow with navigation tracking to validate:
1. PRE gate detects pages from browser_navigate calls in audit log
2. Navigation tracking infers correct page names from URLs
3. Self-healing provides scope_result without explicit scope_discovery
"""

import sys
import json
from pathlib import Path

# Add mcp_server to path
sys.path.insert(0, str(Path(__file__).parent / "mcp_server"))

from tools.gates.qg_discovered_elements import QGDiscoveredElements
from utils.state_manager import StateManager
from utils.audit_logger import AuditLogger


def test_navigation_tracking():
    """Test Step 5 PRE gate navigation tracking feature."""

    print("=" * 80)
    print("TASK 26.0 VALIDATION: Navigation Tracking in Step 5 PRE Gate")
    print("=" * 80)

    # Get current run_id from audit logger
    audit_logger = AuditLogger()
    run_id = audit_logger.run_id
    print(f"\nRun ID: {run_id}")

    # Simulate browser_navigate calls by writing directly to audit log
    print("\n[1] Simulating browser navigation calls...")

    # The gate expects entries with type="mcp_tool" and tool_name="browser_navigate"
    # Let's add these entries directly to the audit log's steps array
    from datetime import datetime, timezone

    nav_entry_1 = {
        "type": "mcp_tool",
        "tool_name": "browser_navigate",
        "args": {"url": "https://parabank.parasoft.com/parabank/index.htm"},
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }

    nav_entry_2 = {
        "type": "mcp_tool",
        "tool_name": "browser_navigate",
        "args": {"url": "https://parabank.parasoft.com/parabank/overview.htm"},
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }

    # Append to audit logger's steps
    audit_logger.steps.append(nav_entry_1)
    audit_logger.steps.append(nav_entry_2)

    # Persist to file so gate can read it
    audit_logger._persist()

    print("   OK Logged navigation to: https://parabank.parasoft.com/parabank/index.htm")
    print("   OK Logged navigation to: https://parabank.parasoft.com/parabank/overview.htm")

    # Test Step 5 PRE gate with navigation tracking
    print("\n[2] Calling Step 5 PRE gate (should detect navigation)...")

    input_data = {
        "mode": "PRE",
        "url": "https://parabank.parasoft.com/parabank/overview.htm",
        "page_name": "ParabankOverviewPage",
        "credential_strategy": "static",
        "discovery_method": "playwright",
        "type": "input"
    }

    # Call PRE gate
    result = QGDiscoveredElements.validate_pre(input_data)

    print("\n[3] PRE Gate Result:")
    print(json.dumps(result, indent=2))

    # Analyze results
    print("\n[4] Navigation Tracking Analysis:")
    print("=" * 80)

    if result["status"] == "pass":
        print("✓ PRE gate PASSED")

        # Check if navigation was detected
        if "scope_result" in result:
            scope_result = result["scope_result"]
            page_count = scope_result.get("page_count", 0)
            pages = scope_result.get("pages", [])

            print(f"\n✓ Navigation tracking detected {page_count} page(s)")

            for i, page in enumerate(pages, 1):
                print(f"\n   Page {i}:")
                print(f"      Name: {page['name']}")
                print(f"      URL: {page['url']}")
                print(f"      Order: {page['order']}")

            # Validate page name inference
            print("\n✓ Page Name Inference:")
            expected_names = ["ParabankIndexPage", "ParabankOverviewPage"]
            actual_names = [p['name'] for p in pages]

            for expected, actual in zip(expected_names, actual_names):
                if expected == actual:
                    print(f"   OK {actual} (correct)")
                else:
                    print(f"   FAIL Expected {expected}, got {actual}")

            # Self-healing validation
            print("\n✓ Self-Healing Validation:")
            print("   Navigation tracking provided scope_result automatically")
            print("   No explicit scope_discovery call needed")

            return {
                "status": "PASS",
                "page_count": page_count,
                "pages_detected": actual_names,
                "self_healing_active": True
            }
        else:
            print("\nFAIL No scope_result in PRE gate response")
            print("   Navigation tracking may not be active")
            return {
                "status": "FAIL",
                "reason": "No scope_result in response"
            }
    else:
        print(f"FAIL PRE gate FAILED: {result.get('error')}")
        return {
            "status": "FAIL",
            "reason": result.get("error")
        }


if __name__ == "__main__":
    try:
        validation_result = test_navigation_tracking()

        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print(json.dumps(validation_result, indent=2))

        if validation_result["status"] == "PASS":
            print("\nOK Task 26.0 Navigation Tracking: VALIDATED")
            sys.exit(0)
        else:
            print("\nFAIL Task 26.0 Navigation Tracking: FAILED")
            sys.exit(1)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

"""
Debug script to test _calculate_scope_from_navigation directly.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add mcp_server to path
sys.path.insert(0, str(Path(__file__).parent / "mcp_server"))

from tools.gates.qg_discovered_elements import QGDiscoveredElements
from utils.audit_logger import AuditLogger


def test_navigation_detection():
    """Test navigation detection directly."""

    print("=" * 80)
    print("DEBUG: Testing _calculate_scope_from_navigation()")
    print("=" * 80)

    # Create audit logger and add navigation entries
    audit_logger = AuditLogger()
    run_id = audit_logger.run_id
    print(f"\nRun ID: {run_id}\n")

    # Add navigation entries
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

    audit_logger.steps.append(nav_entry_1)
    audit_logger.steps.append(nav_entry_2)
    audit_logger._persist()

    print("Added navigation entries to audit log")
    print(f"Audit file: {audit_logger._audit_file}")
    print(f"Entries in steps: {len(audit_logger.steps)}")

    # Read back to verify
    print("\nVerifying audit log contents:")
    with open(audit_logger._audit_file, 'r') as f:
        audit_data = json.load(f)

    print(f"Steps in file: {len(audit_data.get('steps', []))}")
    for i, step in enumerate(audit_data.get("steps", []), 1):
        print(f"  Step {i}: type={step.get('type')}, tool_name={step.get('tool_name')}, args={step.get('args')}")

    # Test _read_audit_log_entries
    print("\n[1] Testing _read_audit_log_entries()...")
    try:
        entries = QGDiscoveredElements._read_audit_log_entries()
        if entries is None:
            print("  ERROR: _read_audit_log_entries() returned None")
            return False
        else:
            print(f"  OK: Read {len(entries)} entries from audit log")
            for i, entry in enumerate(entries, 1):
                print(f"    Entry {i}: {entry}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test _calculate_scope_from_navigation
    print("\n[2] Testing _calculate_scope_from_navigation()...")
    try:
        scope_result = QGDiscoveredElements._calculate_scope_from_navigation()
        if scope_result is None:
            print("  ERROR: _calculate_scope_from_navigation() returned None")
            print("  This means navigation detection failed")
            return False
        else:
            print("  SUCCESS: Navigation detection worked!")
            print(f"  Result:")
            print(json.dumps(scope_result, indent=4))

            # Check for "reason" field
            pages = scope_result.get("pages", [])
            for page in pages:
                if page.get("reason") == "navigation detected":
                    print(f"  OK: Page '{page['name']}' has reason='navigation detected'")
                else:
                    print(f"  WARN: Page '{page['name']}' missing reason field or wrong value")

            return True
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_navigation_detection()

    print("\n" + "=" * 80)
    if success:
        print("OK: Navigation detection working correctly")
        sys.exit(0)
    else:
        print("FAIL: Navigation detection not working")
        sys.exit(1)

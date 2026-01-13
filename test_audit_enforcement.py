"""Test audit enforcement with smart gate pattern."""
import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, 'D:/my_ai_projects/py_sel_framework_mcp/mcp_server')

from tools.gates.qg_user_input import QGUserInput
from utils.audit_logger import AuditLogger

print("=" * 80)
print("Testing Audit Enforcement (Smart Gate Pattern)")
print("=" * 80)

# Save original directory
original_dir = os.getcwd()

# Test 1: Happy Path - Audit writes successfully
print("\nTest 1: Happy Path - Audit directory exists, writes succeed")
print("-" * 80)

try:
    # Ensure tests/_audit exists
    Path("tests/_audit").mkdir(parents=True, exist_ok=True)

    # Call gate with audit logging
    result = QGUserInput.validate({
        "mode": "POST",
        "persona": "As a test user",
        "URL": "https://example.com",
        "role_name": "TestUser",
        "workflow": "test"
    })

    if result.get("status") == "pass":
        print("[PASS] Gate passed and audit enforcement succeeded")
    else:
        print(f"[FAIL] {result.get('error')}")
        print(f"Hint: {result.get('fix_hint', '')[:200]}")

except Exception as e:
    print(f"[ERROR] {str(e)}")

# Test 2: Failure Case - Missing audit directory
print("\nTest 2: Failure Case - Audit directory missing")
print("-" * 80)

try:
    # Temporarily move audit directory
    audit_dir = Path("tests/_audit")
    temp_dir = Path("tests/_audit_backup")

    if audit_dir.exists():
        shutil.move(str(audit_dir), str(temp_dir))

    # Reset audit logger
    from tools.gates.base_gate import BaseGate
    BaseGate.set_audit_logger(None)

    # Try to call gate
    result = QGUserInput.validate({
        "mode": "POST",
        "persona": "As a test user",
        "URL": "https://example.com",
        "role_name": "TestUser",
        "workflow": "test"
    })

    if result.get("status") == "fail" and "Audit directory missing" in result.get("error", ""):
        print("[PASS] Smart gate correctly detected missing audit directory")
        print(f"Error: {result.get('error')}")
        print(f"Fix hint preview: {result.get('fix_hint', '')[:200]}...")
    else:
        print(f"[UNEXPECTED] Status: {result.get('status')}, Error: {result.get('error')}")

    # Restore audit directory
    if temp_dir.exists():
        shutil.move(str(temp_dir), str(audit_dir))

except Exception as e:
    print(f"[ERROR] {str(e)}")
    # Make sure to restore
    if Path("tests/_audit_backup").exists():
        shutil.move("tests/_audit_backup", "tests/_audit")

# Test 3: Verify audit file after successful write
print("\nTest 3: Verify audit entry exists in file")
print("-" * 80)

try:
    # Reset and get fresh audit logger
    BaseGate.set_audit_logger(None)
    audit_logger = BaseGate.get_audit_logger()

    # Call gate
    result = QGUserInput.validate({
        "mode": "POST",
        "persona": "As a test user",
        "URL": "https://example.com",
        "role_name": "TestUser",
        "workflow": "test"
    })

    # Check audit file
    audit_file = Path(f"tests/_audit/audit_log_{audit_logger.run_id}.json")
    if audit_file.exists():
        with open(audit_file, 'r') as f:
            data = json.load(f)

        print(f"[PASS] Audit file exists: {audit_file.name}")
        print(f"       Run ID: {audit_logger.run_id}")
        print(f"       Steps logged: {len(data.get('steps', []))}")
        print(f"       Last entry: {data.get('steps', [])[-1].get('gate', 'NONE')}")
    else:
        print(f"[FAIL] Audit file not found: {audit_file}")

except Exception as e:
    print(f"[ERROR] {str(e)}")

print("\n" + "=" * 80)
print("Audit Enforcement Test Complete")
print("=" * 80)

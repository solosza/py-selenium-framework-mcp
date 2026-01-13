"""Validate fixed ParaBank POMs through qg_page_object POST gate."""
import sys
sys.path.insert(0, 'D:/my_ai_projects/py_sel_framework_mcp/mcp_server')

from utils.state_manager import StateManager
from tools.gates.qg_page_object import QGPageObject

# Load state
sm = StateManager()
step6 = sm.get_step(6)
poms = step6['generated_poms']

print("=" * 80)
print("Validating Fixed ParaBank POMs Through Quality Gate")
print("=" * 80)

all_passed = True

for pom_name, pom_data in poms.items():
    print(f"\n{'=' * 80}")
    print(f"Validating {pom_name}...")
    print(f"{'=' * 80}")

    code = pom_data['code']
    metadata = pom_data['metadata']

    # Call POST validation
    result = QGPageObject.validate({
        "mode": "POST",
        "code": code,
        "metadata": metadata,
        "page_name": pom_name
    })

    print(f"\nFull Result: {result}")

    if result.get("result") == "pass":
        print(f"[PASS] {pom_name} PASSED quality gate")
    else:
        print(f"[FAIL] {pom_name} FAILED quality gate")
        print(f"\nError: {result.get('error')}")
        print(f"\nFix Hint: {result.get('fix_hint')}")
        all_passed = False

print("\n" + "=" * 80)
if all_passed:
    print("SUCCESS: All POMs passed quality gate validation")
else:
    print("FAILURE: One or more POMs failed quality gate validation")
print("=" * 80)

sys.exit(0 if all_passed else 1)

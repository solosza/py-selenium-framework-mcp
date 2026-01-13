import sys
sys.path.insert(0, 'D:/my_ai_projects/py_sel_framework_mcp/mcp_server')

from utils.state_manager import StateManager

sm = StateManager()
step6 = sm.get_step(6)
poms = step6['generated_poms']

# Extract LoginPage
login_pom = poms['LoginPage']
print("=" * 80)
print("LoginPage CODE:")
print("=" * 80)
print(login_pom['code'])
print("\n" + "=" * 80)
print("LoginPage METADATA:")
print("=" * 80)
print(login_pom['metadata'])

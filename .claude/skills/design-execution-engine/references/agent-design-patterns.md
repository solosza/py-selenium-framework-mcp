# Agent Design Patterns - The Isagawa Way

**Version:** 1.0
**Purpose:** Define patterns for building reliable, verifiable agents
**Last Updated:** 2026-01-11

---

## Core Philosophy

**The Isagawa Thesis:**
AI needs governance, not freedom. Agents execute best when guided by protocols and enforced by gates.

```
Protocol (Guidance) + Gates (Enforcement) = Execution Governance
```

**Not:**
- "Do whatever you think is best"
- "Figure it out"
- "Be creative"

**Instead:**
- "Follow this exact protocol"
- "Validate at these checkpoints"
- "Report results at each step"

---

## The Isagawa Agent Pattern

### Pattern Structure

```
Agent Task = Protocol Reference + Explicit Steps + Validation Checkpoints + Error Handling
```

**Components:**

| Component | Purpose | Example |
|-----------|---------|---------|
| **Protocol Reference** | Points to authoritative how-to guide | "Follow .claude/skills/qa-guidance-layer/references/step-01.md" |
| **Explicit Steps** | Numbered sequence of actions | "1. Call qg_preflight 2. Verify status=pass 3. Report result" |
| **Validation Checkpoints** | Stop points to verify correctness | "After Step 5, verify: navigation tracking detected 2 pages" |
| **Error Handling** | What to do when things fail | "If any step fails: STOP, REPORT error, WAIT for user" |

---

## Anti-Pattern vs Pattern

### ❌ Anti-Pattern (What We Did Wrong)

```markdown
Task: "Run production test for Task 26.0 navigation tracking"

Problems:
- Too vague ("production test" - what does this mean?)
- No explicit steps (agent decides what to do)
- No checkpoints (when to validate?)
- No error protocol (what if something fails?)
```

**Result:**
- Agent stopped at Step 5 (incomplete)
- Used synthetic data (not real browser)
- Declared success prematurely
- Missing 50% of workflow

### ✅ Pattern (The Isagawa Way)

```markdown
Task: "Execute complete 11-step workflow for ANY test requirement"

## Input Parameters
test_requirement: "[requirement]"
target_site: "[URL]"
workflow_name: "[workflow]"
credential_strategy: "[strategy]"
test_data_location: "[location]"

## Protocol
Follow: .claude/skills/qa-guidance-layer/references/testing-protocol-11-step-e2e.md

## Execution Rules
1. Execute ALL 10 steps (no shortcuts)
2. Use REAL tools (no synthetic data)
3. Validate at each checkpoint
4. STOP on any failure
5. Report results after each step

## Validation Checkpoints
- After Step 5: Verify navigation tracking (if multi-page)
- After Step 10: Verify test PASSED

## Error Handling
If ANY step fails:
1. STOP immediately
2. Report: step, phase, error, input, output
3. Suggest 2-3 fixes
4. WAIT for user direction

## Success Criteria
ALL must be true:
- [ ] All 10 steps completed
- [ ] All gates passed
- [ ] Test executed and PASSED
- [ ] Files saved correctly
```

**Result:**
- Agent knows EXACTLY what to do
- Clear stop points for validation
- Error handling defined
- Success measurable

---

## Agent Task Scope Levels

**IMPORTANT: These are different TASK SCOPES for ONE agent, NOT multiple agents.**

For token optimization, use ONE agent with the appropriate task scope. Don't spawn multiple agents unless absolutely necessary (e.g., testing completely independent workflows).

### Level 1: Micro-Task (Single Tool)

**Purpose:** Validate one tool works correctly

**Template:**
```markdown
Task: "Validate [tool_name] with [input]"

Steps:
1. Call [tool_name] with input: [specific input]
2. Verify output: [expected output]
3. Report: pass/fail with exact result

Success: Output matches expected
```

**Example:**
```markdown
Task: "Validate qg_preflight with static credentials"

Steps:
1. Call qg_preflight with input: {"credential_strategy": "static", "test_data_location": "shared"}
2. Verify output: {"status": "pass"}
3. Report: Result status and any errors

Success: status == "pass"
```

### Level 2: Step-Task (One Workflow Step)

**Purpose:** ONE agent executes one complete workflow step (PRE → Tool → POST)

**Template:**
```markdown
Task: "Execute Step [N]: [step_name]"

Protocol: [path to step-XX.md]

Steps:
1. PRE validation: Call [gate_pre] with [input]
2. Tool execution: Call [tool_X] with [input]
3. POST validation: Call [gate_post] with [output]
4. Report: Results from all 3 phases

Success: All 3 phases pass
```

**Example:**
```markdown
Task: "Execute Step 4: Generate Test Scenarios"

Protocol: .claude/skills/qa-guidance-layer/references/step-04.md

Steps:
1. PRE: qg_test_scenarios.validate_pre(metadata_context, workflow)
2. Tool: generate_tests_from_user_story(user_story, workflow)
3. POST: qg_test_scenarios.validate_post(test_scenarios)
4. Report: test_scenarios extracted and validated

Success: PRE pass, Tool returns scenarios, POST pass
```

### Level 3: Flow-Task (Multi-Step Sequence)

**Purpose:** ONE agent executes sequence of steps with checkpoints

**Template:**
```markdown
Task: "Execute Steps [N-M]: [flow_name]"

Protocol: [path to protocol]

Steps:
For each step in sequence:
  1. Execute step following protocol
  2. Validate checkpoint
  3. If fail: STOP and report
  4. If pass: Continue to next

Report: Results for each step

Success: All steps pass
```

**Example:**
```markdown
Task: "Execute Steps 1-5: Setup and Discovery"

Protocol: .claude/skills/qa-guidance-layer/references/testing-protocol-11-step-e2e.md

Steps:
1. Step 1: Pre-flight → checkpoint: status="pass"
2. Step 2: User Input → checkpoint: persona extracted
3. Step 3: AI Processing → checkpoint: metadata_context present
4. Step 4: Test Scenarios → checkpoint: scenarios generated
5. Step 5: Element Discovery → checkpoint: elements discovered, navigation tracked

Report: Status of each step

Success: All 5 steps pass, navigation tracking works (if multi-page)
```

### Level 4: E2E-Task (Complete Workflow)

**Purpose:** ONE agent executes full end-to-end workflow with real execution

**Template:**
```markdown
Task: "Execute complete [workflow_name] workflow"

## Input Parameters
[all required parameters]

## Protocol
Follow: [path to E2E protocol]

## Execution Rules
[complete execution rules]

## Validation Checkpoints
[all checkpoints with criteria]

## Error Handling
[error protocol]

## Success Criteria
[complete checklist]

Report: Full validation report
```

**Example:**
```markdown
Task: "Execute complete 11-step QA workflow"

## Input Parameters
test_requirement: "As a registered user, I want to login and view dashboard"
target_site: "https://example.com"
workflow_name: "auth"
credential_strategy: "static"
test_data_location: "shared"

## Protocol
Follow: .claude/skills/qa-guidance-layer/references/testing-protocol-11-step-e2e.md

## Execution Rules
1. Execute ALL 10 steps
2. Use REAL browser tools
3. Validate at each checkpoint
4. STOP on failure
5. Save all artifacts

## Validation Checkpoints
- After Step 1: Pre-flight pass
- After Step 5: Navigation tracking validated
- After Step 10: Test PASSED

## Error Handling
If any step fails:
1. STOP
2. Report: step, phase, error, context
3. Suggest fixes
4. WAIT

## Success Criteria
- [ ] All 10 steps complete
- [ ] All gates pass
- [ ] Test runs and passes
- [ ] Files saved correctly
- [ ] Navigation tracking works (if multi-page)

Report: Complete validation report with all results
```

---

## Key Design Principles

### 1. Reference-Based Prompting

**Don't:** Write instructions inline
**Do:** Reference authoritative protocol

```markdown
❌ BAD:
"Call qg_preflight with credential_strategy and test_data_location,
 then check if status is pass, if not then report error..."

✅ GOOD:
"Protocol: .claude/skills/qa-guidance-layer/references/step-01.md
 Follow Step 1 protocol exactly"
```

### 2. Checkpoint-Driven Execution

**Don't:** Run everything then check
**Do:** Validate after each critical step

```markdown
❌ BAD:
Execute Steps 1-11
Check if all passed

✅ GOOD:
Execute Step 1 → Checkpoint: status="pass" → Continue
Execute Step 2 → Checkpoint: persona extracted → Continue
...
```

### 3. Explicit Error Handling

**Don't:** Let agent decide what to do
**Do:** Define exact error protocol

```markdown
❌ BAD:
"If something fails, try to fix it"

✅ GOOD:
"If ANY step fails:
1. STOP immediately
2. Report: step, error, context
3. Suggest 2-3 fixes
4. WAIT for user direction
DO NOT auto-fix"
```

### 4. Measurable Success Criteria

**Don't:** Vague outcomes
**Do:** Checklist with binary pass/fail

```markdown
❌ BAD:
"Make sure it works"

✅ GOOD:
Success Criteria (ALL must be true):
- [ ] All 10 steps completed
- [ ] All gates returned status="pass"
- [ ] Test executed with pytest
- [ ] Test result: status="passed"
- [ ] Files saved to correct paths
```

### 5. Use REAL Tools, Not Synthetic Data

**Don't:** Mock/simulate when real tool exists
**Do:** Use actual tools and verify side effects

```markdown
❌ BAD:
# Simulate navigation
audit_logger.steps.append({"type": "mcp_tool", "tool_name": "browser_navigate", ...})

✅ GOOD:
# Use real tool
mcp__playwright__browser_navigate({"url": "https://example.com"})
# PostToolUse hook logs automatically
```

---

## Agent Task Template

Use this template for ANY agent task:

```markdown
# Agent Task: [Task Name]

## Purpose
[One sentence: what should this agent accomplish?]

## Input Parameters
```yaml
parameter1: [type] - [description]
parameter2: [type] - [description]
```

## Protocol Reference
[Path to protocol file or "none" if not applicable]

## Execution Steps
1. [Step 1 with expected outcome]
2. [Step 2 with expected outcome]
...

## Validation Checkpoints
- After Step X: Verify [condition]
- After Step Y: Verify [condition]

## Error Handling
If [error_type]:
1. STOP at [step]
2. Report: [what to report]
3. Suggest: [fix options]
4. WAIT

## Success Criteria
Agent task is successful only if ALL true:
- [ ] [Criterion 1]
- [ ] [Criterion 2]
...

## Output Format
[What should agent report back?]
```

---

## Testing Agents Before Deployment

**Before spawning agent, verify:**

1. **Protocol exists and is complete**
   - Check file path valid
   - Protocol has all necessary steps
   - Examples provided

2. **Inputs are specific, not vague**
   - No "test the system"
   - Yes "Execute Step 5 with URL=X, page_name=Y"

3. **Checkpoints are measurable**
   - No "make sure it's good"
   - Yes "status must equal 'pass'"

4. **Error handling is defined**
   - What to do on failure
   - What NOT to do (auto-fix, continue, guess)

5. **Success criteria is complete**
   - Binary checklist
   - No partial success

---

## Task Scope Evolution Pattern

Start small, validate, expand (using ONE agent with increasing scope):

```
1. Micro-Task → Agent tests single tool
2. Step-Task → Agent tests one workflow step
3. Flow-Task → Agent tests 2-5 steps in sequence
4. E2E-Task → Agent tests complete workflow
```

**Don't skip levels.** Each level builds confidence in the next.

**Token Optimization:** Always use ONE agent. Only spawn multiple agents for completely independent workflows (e.g., testing 3 different sites simultaneously).

---

## When NOT to Spawn Multiple Agents

**Token Cost Reality:**
- Each agent = full conversation context
- 10 agents = 10x token usage
- Context duplication = wasted cost

**Use ONE agent with E2E-Task instead of spawning multiple Step-Task agents:**

❌ **WASTEFUL (10 agents):**
```markdown
Spawn agent for Step 1 (context: 10K tokens)
Spawn agent for Step 2 (context: 10K tokens)
...
Spawn agent for Step 10 (context: 10K tokens)
Total: 100K tokens
```

✅ **EFFICIENT (1 agent):**
```markdown
ONE agent executes Steps 1-11 (context: 20K tokens)
Total: 20K tokens
Savings: 80K tokens (80% reduction)
```

**Only spawn multiple agents if:**
1. **Completely independent workflows** (e.g., testing Site A and Site B simultaneously)
2. **Massive parallelization benefit** (e.g., 100 independent test cases, 10 agents = 10x faster)
3. **Failure isolation required** (e.g., critical workflow must not block others)

**For 11-step QA workflow:** ALWAYS use ONE E2E-Task agent.

---

## Lessons Learned (Task 26.0 Validation)

### What Went Wrong

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Stopped at Step 5 | Vague task: "production test" | Define: "Execute ALL 10 steps" |
| Used synthetic data | No tool requirement specified | Require: "Use REAL browser_navigate" |
| Missed validation | No checkpoints defined | Add: "Validate after each step" |
| Import confusion | No protocol reference | Provide: "Follow step-XX.md" |

### What Went Right

| Success | Reason |
|---------|--------|
| Found audit logger issue | Agent persisted through errors |
| Validated navigation tracking | Clear validation criteria |
| Created comprehensive report | Good final report structure |

### Key Takeaway

**Agents are only as good as their instructions.**

Vague instructions → unpredictable results
Precise instructions → reliable execution

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-11 | Initial patterns based on Task 26.0 lessons |

# Complete Validation Matrix - Defense-in-Depth Architecture

**Date:** 2026-01-23
**Purpose:** Map what validator SHOULD check against what it ACTUALLY checks for all 6 components

---

## Architecture Overview (6 Components)

**Core Defense-in-Depth (4 Layers):**
1. **Protocols** - Define correct behavior
2. **Smart Gates** - Validate AND teach
3. **Hooks** - Monitor continuously
4. **State Checkpointing** - Enable recovery

**Supporting Infrastructure (2 Components):**
5. **Audit System** - Immutable logging
6. **HITL System** - Human oversight

---

## Layer 1: Protocols (Preventive)

**What It Should Do:**
- Define correct execution workflow
- Teach AI correct behavior BEFORE execution
- Provide templates for user prompts
- Specify required fields for each step

### Current Validator Coverage

| Check | Status | What's Checked | What's MISSING |
|-------|--------|----------------|----------------|
| Protocol Adherence (Check 5) | ❌ SKIPPED | Nothing | Everything |

### What Should Be Validated (Per Step)

**Step 1 (User Input):**
- ✗ Required fields present (persona, URL, role_name, workflow, raw_requirement)
- ✗ Field values valid (URL is HTTP/HTTPS, role_name is PascalCase)
- ✗ role_name derived from persona (GAP-01-02)
- ✗ Environment detected or config created
- ✗ Workflow directories exist (RETRY-01-01)

**Step 2 (Pre-flight Config):**
- ✗ credential_strategy valid (static/dynamic/self-contained/none)
- ✗ test_data_location valid (shared/workflow/both/none)
- ✗ browser_config.headless = false (pair programming requirement)
- ✗ timeout_config.enabled is boolean
- ✗ timeout_config.threshold_seconds > 0 if enabled
- ✗ Test data infrastructure exists (tests/data/, test_users.json)

**Step 3 (AI Processing):**
- ✗ bdd_scenarios has valid Given/When/Then structure
- ✗ expected_states derived from "Then" clauses (at least 1)
- ✗ intent is action verb (non-empty)
- ✗ Retry attempts <= 3 (GAP-03-01)

**Step 4 (Test Scenarios):**
- ✗ test_scenarios array not empty
- ✗ Each scenario has name, given, when, then
- ✗ No skeleton code patterns (DD-25)
- ✗ Retry attempts <= 3

**Step 5 (Element Discovery):**
- ✗ discovered_elements array not empty
- ✗ Each element has name, type, locator
- ✗ page_name is PascalCase
- ✗ validation_results present (DD-46)
- ✗ Two-pass discovery complete (input + output elements for each page)
- ✗ Page directories exist (RETRY-05-01)
- ✗ DD-33 decision correct (playwright vs tool2)
- ✗ Multi-page scope tracked correctly

**VERDICT:** Layer 1 has **0% validation coverage** (Check 5 is SKIPPED)

---

## Layer 2: Smart Gates (Detective + Corrective)

**What It Should Do:**
- Validate execution against protocol
- Provide fixes when validation fails (NEEDS_RETRY pattern)
- Block execution on failures
- Enforce max retry attempts

### Current Validator Coverage

| Check | Status | What's Checked | What's MISSING |
|-------|--------|----------------|----------------|
| Gate Validation (Check 4) | ⚠️ PARTIAL | Gate executed, returned status | Validation logic correctness |
| Step Flow (Check 6) | ⚠️ PARTIAL | Can proceed if passed | Blocking behavior (max attempts) |

### What Should Be Validated

**Gate Execution:**
- ✓ Gate executed (Check 4 - Line 433)
- ✓ Gate returned valid status (pass/fail/NEEDS_RETRY) (Check 4 - Line 488)
- ✗ Gate validation logic correct (doesn't just pass everything)
- ✗ Gate error messages present when status=fail
- ✗ Gate fix_hint present when status=fail

**NEEDS_RETRY Pattern:**
- ✗ NEEDS_RETRY returns scaffolding_needed array
- ✗ Scaffolding template has type, path, reason fields
- ✗ AI creates files/dirs from template
- ✗ Gate passes on retry after scaffolding

**Blocking Behavior:**
- ✗ Max attempts enforced (3 for Steps 3-5)
- ✗ Status=blocked after max attempts exceeded
- ✗ Cannot proceed to next step when blocked

**Gate-Specific Validation:**
- ✗ Step 1: Environment detection works (returns NEEDS_RETRY for unknown domains)
- ✗ Step 2: Infrastructure scaffolding works (DEF-060)
- ✗ Step 3: Retry tracking works (GAP-03-01)
- ✗ Step 4: Attempt tracking works (existing implementation)
- ✗ Step 5: Two-pass discovery checkpoint works (DEF-045)

**VERDICT:** Layer 2 has **~15% validation coverage** (basic execution only, no validation logic or blocking behavior)

---

## Layer 3: Hooks (Continuous Detective)

**What It Should Do:**
- Monitor EVERY tool call in real-time
- Write audit entries after each gate call
- Read from correct state location
- Capture complete metadata

### Current Validator Coverage

| Check | Status | What's Checked | What's MISSING |
|-------|--------|----------------|----------------|
| Hook Execution (Check 10) | ⚠️ PARTIAL | Audit timestamp recent | What hook actually wrote |
| Manual File Detection (Check 11) | ⚠️ PARTIAL | Transcript not manually created | Hook wrote transcript correctly |

### What Should Be Validated

**Hook Execution:**
- ✓ Hook executed recently (Check 10 - Line 863)
- ✗ Hook wrote correct data to audit
- ✗ Hook captured all required metadata (step, gate, result, timestamp, input, output)
- ✗ Hook read from correct state location (tests/_state/{run_id}/)

**PostToolUse Hook (audit-trail-writer.py):**
- ✗ Reads .current_run_id marker
- ✗ Reads workflow_state.json from correct location
- ✗ Writes audit_log_{run_id}.json with all fields
- ✗ Audit entry has correct structure (type, gate, step, result, timestamp, metadata)

**Transcript Generation:**
- ✗ Transcript written after each step (currently checked by gate via NEEDS_RETRY)
- ✗ Transcript has correct format (markdown, append mode)
- ✗ Transcript contains step entry
- ✗ Transcript not manually created (Check 11 - Line 946)

**VERDICT:** Layer 3 has **~20% validation coverage** (checks execution but not correctness)

---

## Layer 4: State Checkpointing (Recovery)

**What It Should Do:**
- Save state after each successful step
- Enable pause/resume
- Accumulate state across steps (Step N can access Steps 1..N-1)
- Isolate per workflow run (unique run_id)

### Current Validator Coverage

| Check | Status | What's Checked | What's MISSING |
|-------|--------|----------------|----------------|
| State (Check 1) | ⚠️ PARTIAL | File exists, JSON valid, step key exists | Field validation |
| Step Flow (Check 6) | ⚠️ PARTIAL | State saved when gate passes | State accumulation |
| Run ID Uniqueness (Check 7) | ✓ FULL | Run ID fresh, not reused | - |
| Session Marker (Check 9) | ✓ FULL | Marker exists, matches run_id | - |
| Old Marker Cleanup (Check 13) | ✓ FULL | Old location cleaned up | - |

### What Should Be Validated

**State File:**
- ✓ File exists (Check 1 - Line 186)
- ✓ JSON valid (Check 1 - Line 196)
- ✓ Step key exists (Check 1 - Line 208)
- ✗ State data matches protocol schema (all required fields present)
- ✗ State values valid (not just present)

**State Accumulation:**
- ⚠️ Previous steps accessible (Check 6 - Line 606, but only warns)
- ✗ Step N state contains data from Steps 1..N-1
- ✗ State references valid (e.g., Step 5 can read Step 2 credential_strategy)

**Per-Run Isolation:**
- ✓ Run ID unique (Check 7 - Line 651)
- ✓ Session marker correct (Check 9 - Line 802)
- ✓ Old marker cleaned (Check 13 - Line 1111)
- ✗ State directory unique per run (tests/_state/{run_id}/)

**Pause/Resume:**
- ✗ Can load state from previous run
- ✗ Can resume workflow from any step
- ✗ State checkpoint complete enough to resume

**VERDICT:** Layer 4 has **~60% validation coverage** (infrastructure good, data validation missing)

---

## Layer 5: Audit System (Observability)

**What It Should Do:**
- Immutable log of all actions
- Capture input/output for each gate
- Capture metadata (timestamps, step numbers, run_id)
- Enable compliance reporting and debugging

### Current Validator Coverage

| Check | Status | What's Checked | What's MISSING |
|-------|--------|----------------|----------------|
| Audit (Check 2) | ⚠️ PARTIAL | File exists, JSON valid, gate entry exists | Complete metadata |
| Audit Isolation (Check 8) | ✓ FULL | Step N has exactly N events, sequential | - |
| Audit Step Number (Check 12) | ✓ FULL | Audit entry has correct step field | - |
| Audit State Path (Check 14) | ⚠️ PARTIAL | Audit references correct state path | - |

### What Should Be Validated

**Audit File:**
- ✓ File exists (Check 2 - Line 262)
- ✓ JSON valid (Check 2 - Line 272)
- ✓ Has events array (Check 2 - Line 283)
- ✓ Has gate entry (Check 2 - Line 320)

**Audit Entry Structure:**
- ✓ Has correct step number (Check 12 - Line 1022)
- ⚠️ References correct state path (Check 14 - Line 1160, but SKIPs if not present)
- ✗ Has all required fields (type, gate, step, result, timestamp, input, output, metadata)
- ✗ Input/output captured correctly
- ✗ Metadata complete (depends on step)

**Audit Isolation:**
- ✓ Step N has exactly N events (Check 8 - Line 712)
- ✓ Events are sequential (Check 8 - Line 769)
- ✗ No events from other workflows contaminating log

**Immutability:**
- ✗ Audit log append-only (never modifies past entries)
- ✗ Audit entries have unique IDs
- ✗ Audit log can be verified (checksums, signatures)

**VERDICT:** Layer 5 has **~50% validation coverage** (structure good, completeness missing)

---

## Layer 6: HITL System (Human Oversight)

**What It Should Do:**
- Trigger on critical decisions
- Provide clear options to user
- Block execution until user responds
- Log user choices to audit

### Current Validator Coverage

| Check | Status | What's Checked | What's MISSING |
|-------|--------|----------------|----------------|
| None | ❌ NONE | Nothing | Everything |

### What Should Be Validated

**Blocked Responses:**
- ✗ Status=blocked returned after max attempts
- ✗ Error messages clear and actionable
- ✗ Fix hints provided
- ✗ User presented with options (not just error)

**User Choices:**
- ✗ User input validated (1-4 for multiple choice)
- ✗ User choice logged to audit
- ✗ Workflow continues after user responds

**HITL Triggers:**
- ✗ Step 1: Unknown environment → ask user to create config
- ✗ Step 2: NEEDS_RETRY → AI scaffolds, retries
- ✗ Step 3: 3 failed attempts → ask user (clarify requirement or abort)
- ✗ Step 4: 3 failed attempts → ask user (adjust BDD or abort)
- ✗ Step 5: 3 failed attempts → ask user (different URL, manual elements, or abort)

**VERDICT:** Layer 6 has **0% validation coverage** (not checked at all)

---

## Summary: Validation Coverage by Layer

| Layer | Component | Coverage | Status |
|-------|-----------|----------|--------|
| 1 | Protocols | 0% | ❌ CRITICAL GAP |
| 2 | Smart Gates | 15% | ❌ CRITICAL GAP |
| 3 | Hooks | 20% | ❌ CRITICAL GAP |
| 4 | State Checkpointing | 60% | ⚠️ PARTIAL |
| 5 | Audit System | 50% | ⚠️ PARTIAL |
| 6 | HITL System | 0% | ❌ CRITICAL GAP |

**Overall Coverage:** ~24% (6/25 aspects fully validated)

---

## What Needs to Be Added

### Priority 1: Protocol Validation (Layer 1)

**Implement Check 5 - Protocol Adherence:**

```python
def check_protocol(self) -> ValidationResult:
    """5. Protocol Adherence - Validate ALL protocol requirements"""
    if self.step_num == 1:
        return self._check_step1_protocol()
    elif self.step_num == 2:
        return self._check_step2_protocol()
    elif self.step_num == 3:
        return self._check_step3_protocol()
    elif self.step_num == 4:
        return self._check_step4_protocol()
    elif self.step_num == 5:
        return self._check_step5_protocol()

def _check_step1_protocol(self):
    """Validate Step 1 protocol requirements"""
    failures = []
    step_data = self._state_data.get("step_1", {})

    # Required fields
    required = ["persona", "URL", "role_name", "workflow", "raw_requirement"]
    for field in required:
        if field not in step_data:
            failures.append(f"Missing field: {field}")

    # Field validation
    url = step_data.get("URL", "")
    if not url.startswith(("http://", "https://")):
        failures.append(f"Invalid URL: {url}")

    role_name = step_data.get("role_name", "")
    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', role_name):
        failures.append(f"role_name not PascalCase: {role_name}")

    # Role name matches persona (GAP-01-02)
    persona = step_data.get("persona", "")
    if not self._role_name_matches_persona(role_name, persona):
        failures.append(f"role_name '{role_name}' doesn't match persona '{persona}'")

    # Workflow directories exist (RETRY-01-01)
    workflow = step_data.get("workflow", "")
    if not Path(f"framework/pages/{workflow}").exists():
        failures.append(f"Missing: framework/pages/{workflow}/")
    if not Path(f"tests/{workflow}").exists():
        failures.append(f"Missing: tests/{workflow}/")

    # Return result
    if failures:
        return ValidationResult(
            name="Protocol Adherence (AI)",
            status=Status.FAIL,
            message="Protocol violations found",
            details={"failures": failures}
        )
    return ValidationResult(
        name="Protocol Adherence (AI)",
        status=Status.PASS,
        message="All Step 1 protocol requirements met"
    )
```

### Priority 2: Gate Validation Logic (Layer 2)

**Add Check 15 - Gate Correctness:**

```python
def check_gate_correctness(self) -> ValidationResult:
    """15. Gate Validation Logic - Verify gate actually validates"""
    # Test gate with invalid data
    # Verify gate rejects invalid data
    # Verify gate provides fix hints
    # Verify NEEDS_RETRY pattern works
    pass
```

### Priority 3: Hook Data Correctness (Layer 3)

**Add Check 16 - Hook Data:**

```python
def check_hook_data(self) -> ValidationResult:
    """16. Hook Data Correctness - Verify hook wrote correct audit data"""
    # Verify audit entry has all required fields
    # Verify audit entry captured input/output
    # Verify audit metadata complete
    pass
```

### Priority 4: HITL Triggers (Layer 6)

**Add Check 17 - HITL Behavior:**

```python
def check_hitl_triggers(self) -> ValidationResult:
    """17. HITL Trigger Validation - Verify blocked responses work"""
    # Verify max attempts enforced
    # Verify blocked status returned
    # Verify error messages clear
    # Verify fix hints actionable
    pass
```

---

## Recommendation

**We need to expand validator from 14 checks to ~25+ checks covering all 6 layers.**

**Approach:**
1. Keep existing 14 checks (infrastructure)
2. Add 11+ new checks (validation logic)
3. Organize by layer (Protocol, Gates, Hooks, State, Audit, HITL)

**Benefits:**
- Catches gaps like GAP-03-01 immediately
- Validates entire defense-in-depth architecture
- True TDD - validator enforces design
- Can run after each step during development

Should I create the enhanced validator implementation?

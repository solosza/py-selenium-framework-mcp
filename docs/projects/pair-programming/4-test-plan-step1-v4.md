# Test Plan: Step 1 - User Input (7-Step Workflow v4.0)

**PRD:** `2-prd-v4.md` (Step 1 section)
**Status:** Living Document
**Current:** Step 1 test pyramids
**Date:** 2026-01-23

---

## Test Pyramid Methodology

Each component has a unique test pyramid derived from **6 Discovery Questions:**

1. What are the fundamental building blocks?
2. What are the integration points?
3. What are the critical user journeys?
4. What edge cases exist?
5. What can fail in production?
6. What regulatory/compliance requirements exist?

**Pyramid Structure:** Each layer answers distinct questions and has different test characteristics.

---

## Component 1: Protocol (Step 1 User Input)

**File:** `.claude/skills/qa-management-layer/references/step-01.md`

### Discovery Questions Applied

**Q1: Fundamental building blocks?**
- ASK questions (persona, URL, workflow)
- EXTRACT logic (role_name, raw_requirement)
- AUTO-DETECT environment
- CALL gate validation
- WRITE transcript

**Q2: Integration points?**
- AI follows protocol steps in sequence
- Protocol → Gate (qg_user_input)
- Protocol → TranscriptWriter
- Protocol → StateManager (via gate)

**Q3: Critical user journeys?**
- User provides valid input → AI follows all steps → State saved
- User provides invalid input → AI shows fix hint → User corrects → Retry

**Q4: Edge cases?**
- User provides partial input (skips fields)
- User provides malformed data
- Unknown environment domain

**Q5: What can fail in production?**
- AI skips protocol steps
- AI doesn't follow retry pattern
- AI forgets to write transcript

**Q6: Regulatory/compliance?**
- Protocol adherence (all steps executed in order)
- Audit trail completeness

### Test Pyramid: Protocol

```
┌─────────────────────────────────────────────────┐
│  Layer 3: E2E Protocol Adherence (1-2 tests)   │  Q3: Critical journeys
│  - Full Step 1 flow (valid input)              │  Q6: Compliance
│  - Full Step 1 flow with retry                 │
├─────────────────────────────────────────────────┤
│  Layer 2: Step Sequence Verification (3-5)     │  Q2: Integration points
│  - AI calls steps in correct order             │  Q5: Production failures
│  - AI handles gate FAIL correctly              │
│  - AI writes transcript after gate PASS        │
├─────────────────────────────────────────────────┤
│  Layer 1: Protocol Parsing (5-10 tests)        │  Q1: Building blocks
│  - Protocol markdown is valid                  │  Q4: Edge cases
│  - All required sections present               │
│  - Examples are accurate                       │
└─────────────────────────────────────────────────┘
```

**Test Characteristics:**

| Layer | Type | Tool | Speed | Runs |
|-------|------|------|-------|------|
| Layer 1 | Unit | Pytest | <1s | Every commit |
| Layer 2 | Integration | Pytest + mock MCP | <5s | Every commit |
| Layer 3 | E2E | Pytest + real MCP | <30s | Before merge |

**Coverage Target:** 80% (behavior verification, not line coverage)

**Acceptance Mapping:**
- AT-1.1 (valid input) → Layer 3
- AT-1.2 (invalid persona) → Layer 2
- AT-1.9 (gate retry) → Layer 2

---

## Component 2: Gate (qg_user_input)

**File:** `mcp_server/tools/gates/qg_user_input.py`

### Discovery Questions Applied

**Q1: Fundamental building blocks?**
- Regex patterns (URL_PATTERN, PASCAL_CASE_PATTERN)
- Validation methods (_is_valid_persona, _is_valid_url, _is_valid_role_name)
- Environment detection logic
- Fix hint generators

**Q2: Integration points?**
- StateManager (save on PASS)
- BaseGate (validate_and_pass method)
- Environment config JSON file
- AuditLogger (via hook)

**Q3: Critical user journeys?**
- Valid input → PASS → State saved
- Invalid input → FAIL → Fix hint → Retry → PASS

**Q4: Edge cases?**
- Empty strings
- Whitespace-only strings
- Special characters in URLs
- Unicode in persona
- Case sensitivity (PascalCase validation)
- Unknown environment domain
- Malformed environment_config.json

**Q5: What can fail in production?**
- Regex patterns fail on valid input (false negative)
- Regex patterns pass on invalid input (false positive)
- Environment detection fails (file not found)
- State save fails (disk I/O error)

**Q6: Regulatory/compliance?**
- Validation determinism (same input = same result)
- Fix hints teach correct patterns (DD-01, DD-02)

### Test Pyramid: Gate

```
┌─────────────────────────────────────────────────┐
│  Layer 4: Production Failure Scenarios (2-3)   │  Q5: Production failures
│  - Environment config file missing             │
│  - State save fails (disk I/O)                 │
│  - Concurrent validation (race conditions)     │
├─────────────────────────────────────────────────┤
│  Layer 3: Integration with State (3-5)         │  Q2: Integration points
│  - State saved on PASS (verify file exists)    │
│  - State contains all fields                   │
│  - State not saved on FAIL                     │
├─────────────────────────────────────────────────┤
│  Layer 2: Edge Case Validation (10-15)         │  Q4: Edge cases
│  - Empty persona                               │
│  - Whitespace-only persona                     │
│  - Special chars in URL                        │
│  - Unicode in persona                          │
│  - lowercase-role (not PascalCase)             │
│  - Unknown environment domain                  │
│  - Malformed environment_config.json           │
├─────────────────────────────────────────────────┤
│  Layer 1: Regex Pattern Tests (20-30)          │  Q1: Building blocks
│  - URL_PATTERN matches valid HTTP/HTTPS        │
│  - URL_PATTERN rejects invalid schemes         │
│  - PASCAL_CASE_PATTERN matches valid names     │
│  - PASCAL_CASE_PATTERN rejects invalid names   │
│  - Environment detection matches domains       │
└─────────────────────────────────────────────────┘
```

**Test Characteristics:**

| Layer | Type | Tool | Speed | Runs |
|-------|------|------|-------|------|
| Layer 1 | Unit (TDD) | Pytest | <100ms | Every save |
| Layer 2 | Unit (TDD) | Pytest | <500ms | Every commit |
| Layer 3 | Integration | Pytest | <2s | Every commit |
| Layer 4 | Integration | Pytest + fault injection | <5s | Before merge |

**Coverage Target:** 95% (critical validation logic)

**Acceptance Mapping:**
- AT-1.1 (valid input) → Layer 1, Layer 3
- AT-1.2 (invalid persona) → Layer 2
- AT-1.3 (invalid URL) → Layer 2
- AT-1.4 (environment detection) → Layer 1, Layer 3
- AT-1.5 (unknown environment) → Layer 2
- AT-1.6 (role name extraction) → Layer 1

---

## Component 3: State (StateManager)

**File:** `mcp_server/utils/state_manager.py`

### Discovery Questions Applied

**Q1: Fundamental building blocks?**
- save_step() method
- load_step() method
- File path generation (per-run isolation)
- JSON serialization/deserialization
- Atomic write logic

**Q2: Integration points?**
- File system (disk I/O)
- Gate validation (calls save_step on PASS)
- Next steps (read saved state)

**Q3: Critical user journeys?**
- Step 1 saves state → Step 2 loads state
- Multiple runs don't overwrite each other

**Q4: Edge cases?**
- Disk full (write fails)
- Permission denied (write fails)
- Corrupted state file (read fails)
- Missing run_id directory
- Concurrent writes (same run_id)

**Q5: What can fail in production?**
- State save fails silently (no exception raised)
- State file corrupted (atomic write failure)
- Run isolation broken (run_A overwrites run_B)

**Q6: Regulatory/compliance?**
- State immutability (no modification after write)
- Per-run isolation (data segregation)

### Test Pyramid: State

```
┌─────────────────────────────────────────────────┐
│  Layer 4: Recovery & Fault Tolerance (2-3)     │  Q5: Production failures
│  - Disk full during write                      │
│  - Permission denied                           │
│  - Corrupted file recovery                     │
├─────────────────────────────────────────────────┤
│  Layer 3: Isolation & Concurrency (3-5)        │  Q2: Integration points
│  - Multiple runs don't overwrite               │  Q6: Compliance
│  - Concurrent writes to same run (rare)        │
│  - State immutability after write              │
├─────────────────────────────────────────────────┤
│  Layer 2: Edge Case File Operations (5-10)     │  Q4: Edge cases
│  - Missing directory (auto-create)             │
│  - Special characters in run_id                │
│  - Large state data (>1MB)                     │
│  - Empty state data                            │
├─────────────────────────────────────────────────┤
│  Layer 1: Save/Load Correctness (10-15)        │  Q1: Building blocks
│  - save_step() creates file                    │
│  - load_step() returns saved data              │
│  - JSON serialization round-trip               │
│  - File path generation (per-run)              │
└─────────────────────────────────────────────────┘
```

**Test Characteristics:**

| Layer | Type | Tool | Speed | Runs |
|-------|------|------|-------|------|
| Layer 1 | Unit (TDD) | Pytest + temp dir | <200ms | Every save |
| Layer 2 | Unit (TDD) | Pytest + fault injection | <500ms | Every commit |
| Layer 3 | Integration | Pytest + threading | <2s | Every commit |
| Layer 4 | Integration | Pytest + fault injection | <5s | Before merge |

**Coverage Target:** 90% (data integrity)

**Acceptance Mapping:**
- AT-1.1 (state saved) → Layer 1
- AT-1.7 (crash safety) → Layer 4
- AT-1.10 (state isolation) → Layer 3

---

## Component 4: Audit (AuditLogger)

**File:** `mcp_server/utils/audit_logger.py`

### Discovery Questions Applied

**Q1: Fundamental building blocks?**
- log_gate() method
- _persist() method (atomic write)
- Event schema (type, step, gate, result, timestamp)
- Workflow_id generation

**Q2: Integration points?**
- File system (disk I/O)
- PostToolUse hook (calls log_gate)
- Audit file path generation

**Q3: Critical user journeys?**
- Gate validation → Audit event logged
- Workflow crashes → Audit log preserved (partial events)

**Q4: Edge cases?**
- Disk full during persist
- Permission denied
- Invalid JSON in existing log (corruption)
- Large event metadata (>10KB)

**Q5: What can fail in production?**
- Audit log not written (silent failure)
- Atomic write fails (temp file not renamed)
- Events lost on crash (non-atomic write)
- Log corruption (invalid JSON)

**Q6: Regulatory/compliance?**
- Immutability (no modification after write)
- Completeness (every gate call logged)
- Crash safety (DEF-040 atomic write)

### Test Pyramid: Audit

```
┌─────────────────────────────────────────────────┐
│  Layer 4: Crash Safety & Recovery (2-3)        │  Q5: Production failures
│  - Crash during persist (atomic write)         │  Q6: Compliance (DEF-040)
│  - Existing log corrupted (recovery)           │
│  - Disk full during write                      │
├─────────────────────────────────────────────────┤
│  Layer 3: Append & Immutability (3-5)          │  Q2: Integration points
│  - Multiple events appended correctly          │  Q6: Compliance
│  - Existing events not modified               │
│  - Workflow restart loads existing events      │
├─────────────────────────────────────────────────┤
│  Layer 2: Edge Case Event Logging (5-10)       │  Q4: Edge cases
│  - Large metadata (>10KB)                      │
│  - Empty metadata                              │
│  - Special characters in error messages        │
│  - Invalid event type (validation)             │
├─────────────────────────────────────────────────┤
│  Layer 1: Event Schema Correctness (10-15)     │  Q1: Building blocks
│  - log_gate() creates valid event             │
│  - Event has required fields                   │
│  - Timestamp format (ISO-8601)                 │
│  - JSON serialization correct                  │
└─────────────────────────────────────────────────┘
```

**Test Characteristics:**

| Layer | Type | Tool | Speed | Runs |
|-------|------|------|-------|------|
| Layer 1 | Unit (TDD) | Pytest + temp dir | <200ms | Every save |
| Layer 2 | Unit (TDD) | Pytest | <500ms | Every commit |
| Layer 3 | Integration | Pytest + file ops | <2s | Every commit |
| Layer 4 | Integration | Pytest + fault injection | <5s | Before merge |

**Coverage Target:** 90% (audit integrity)

**Acceptance Mapping:**
- AT-1.1 (audit logged) → Layer 1
- AT-1.7 (crash safety) → Layer 4
- AT-1.8 (append behavior) → Layer 3

---

## Component 5: Hook (PostToolUse - audit-trail-writer.py)

**File:** `.claude/hooks/audit-trail-writer.py`

### Discovery Questions Applied

**Q1: Fundamental building blocks?**
- Hook trigger (after MCP tool call)
- Event extraction (gate name, step, result)
- AuditLogger.log_gate() call
- Error handling (non-blocking)

**Q2: Integration points?**
- MCP tool system (hook trigger)
- AuditLogger
- Gate results (extract metadata)

**Q3: Critical user journeys?**
- Gate called → Hook triggers → Audit logged
- Hook fails → Workflow continues (non-blocking)

**Q4: Edge cases?**
- Hook triggered for non-gate tools (should ignore)
- AuditLogger fails (hook catches exception)
- Missing metadata in tool result

**Q5: What can fail in production?**
- Hook crashes workflow (should be non-blocking)
- Hook silently fails (no logging)
- Hook called multiple times for same event (duplicate logging)

**Q6: Regulatory/compliance?**
- Hook must NOT block workflow
- Hook must log ALL gate calls (completeness)

### Test Pyramid: Hook

```
┌─────────────────────────────────────────────────┐
│  Layer 3: Non-Blocking Failure (2-3)           │  Q5: Production failures
│  - AuditLogger fails → workflow continues      │  Q6: Compliance
│  - Hook crashes → workflow continues           │
├─────────────────────────────────────────────────┤
│  Layer 2: Integration with MCP (3-5)           │  Q2: Integration points
│  - Hook triggers after gate call               │  Q3: Critical journeys
│  - Hook calls AuditLogger.log_gate()           │
│  - Hook ignores non-gate tools                 │
├─────────────────────────────────────────────────┤
│  Layer 1: Event Extraction (5-10)              │  Q1: Building blocks
│  - Extract gate name from tool result          │  Q4: Edge cases
│  - Extract step number                         │
│  - Extract result (pass/fail)                  │
│  - Extract metadata                            │
│  - Handle missing metadata gracefully          │
└─────────────────────────────────────────────────┘
```

**Test Characteristics:**

| Layer | Type | Tool | Speed | Runs |
|-------|------|------|-------|------|
| Layer 1 | Unit | Pytest + mock tool results | <100ms | Every save |
| Layer 2 | Integration | Pytest + mock MCP | <2s | Every commit |
| Layer 3 | Integration | Pytest + fault injection | <5s | Before merge |

**Coverage Target:** 85% (hook reliability)

**Acceptance Mapping:**
- AT-1.1 (audit logged via hook) → Layer 2
- Hook non-blocking requirement → Layer 3

---

## Component 6: Transcript (TranscriptWriter)

**File:** `mcp_server/utils/transcript_writer.py` (NEW)

### Discovery Questions Applied

**Q1: Fundamental building blocks?**
- write_header() method
- append_step_entry() method
- format_step1_entry() method
- update_summary() method
- Markdown formatting logic

**Q2: Integration points?**
- File system (disk I/O)
- Protocol (calls append_step_entry)
- State data (reads step completion data)

**Q3: Critical user journeys?**
- Step 1 completes → Transcript entry written
- Step 2 starts → Transcript appends (Step 1 preserved)

**Q4: Edge cases?**
- File doesn't exist (create on first write)
- Directory doesn't exist (create recursively)
- Large entry data (>1KB)
- Special characters in user input
- Unicode in persona

**Q5: What can fail in production?**
- Transcript overwrites existing entries (append failure)
- Markdown formatting broken (invalid syntax)
- File write fails (disk full, permissions)

**Q6: Regulatory/compliance?**
- Append-only (no overwrite)
- Human-readable (markdown, not JSON)

### Test Pyramid: Transcript

```
┌─────────────────────────────────────────────────┐
│  Layer 4: Production Failure Scenarios (2-3)   │  Q5: Production failures
│  - Disk full during write                      │
│  - Permission denied                           │
│  - Large entry data (>10KB)                    │
├─────────────────────────────────────────────────┤
│  Layer 3: Append Behavior (3-5)                │  Q2: Integration points
│  - Multiple steps append correctly             │  Q6: Compliance
│  - Existing entries not overwritten            │
│  - Summary updates on each append              │
├─────────────────────────────────────────────────┤
│  Layer 2: Markdown Formatting (5-10)           │  Q4: Edge cases
│  - Special characters escaped                  │
│  - Unicode handled correctly                   │
│  - Status indicators (✓ ⏳ ❌) render           │
│  - Section headers correct                     │
├─────────────────────────────────────────────────┤
│  Layer 1: Basic Write Operations (10-15)       │  Q1: Building blocks
│  - write_header() creates file                 │
│  - append_step_entry() adds entry              │
│  - format_step1_entry() generates markdown     │
│  - update_summary() updates summary            │
└─────────────────────────────────────────────────┘
```

**Test Characteristics:**

| Layer | Type | Tool | Speed | Runs |
|-------|------|------|-------|------|
| Layer 1 | Unit (TDD) | Pytest + temp dir | <200ms | Every save |
| Layer 2 | Unit (TDD) | Pytest | <500ms | Every commit |
| Layer 3 | Integration | Pytest + file ops | <2s | Every commit |
| Layer 4 | Integration | Pytest + fault injection | <5s | Before merge |

**Coverage Target:** 90% (new component, critical for UX)

**Acceptance Mapping:**
- AT-1.1 (transcript written) → Layer 1
- AT-1.8 (append behavior) → Layer 3

---

## Test Execution Strategy

### Test Phases

**Phase 1: TDD Implementation (Core Components)**
- TranscriptWriter: Layers 1-2 (TDD cycles)
- Gate validation: Layers 1-2 (TDD cycles)
- Run after each TDD cycle (Red → Green → Refactor)

**Phase 2: Integration Testing**
- All components: Layer 3 tests
- Run before committing

**Phase 3: Production Failure Testing**
- All components: Layer 4 tests
- Run before merge to main

**Phase 4: E2E Acceptance Testing**
- Protocol: Layer 3 (full Step 1 flow)
- Run before release

### Test Execution Commands

```bash
# Layer 1: Unit tests (fast, run on every save)
pytest mcp_server/_dev_tests/test_utils/test_transcript_writer.py::TestLayer1 -v
pytest mcp_server/_dev_tests/test_gates/test_qg_user_input.py::TestLayer1 -v

# Layer 2: Edge case tests (run on every commit)
pytest mcp_server/_dev_tests/ -m "edge_case" -v

# Layer 3: Integration tests (run on every commit)
pytest mcp_server/_dev_tests/ -m "integration" -v

# Layer 4: Failure scenarios (run before merge)
pytest mcp_server/_dev_tests/ -m "failure_scenario" -v

# All tests with coverage
pytest mcp_server/_dev_tests/ --cov=mcp_server --cov-report=html --cov-report=term
```

### Test Markers (pytest)

```python
# Use pytest markers to organize tests by layer

@pytest.mark.layer1
@pytest.mark.unit
def test_basic_operation():
    pass

@pytest.mark.layer2
@pytest.mark.edge_case
def test_edge_case():
    pass

@pytest.mark.layer3
@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.layer4
@pytest.mark.failure_scenario
def test_production_failure():
    pass
```

---

## Coverage Matrix

### Per-Component Coverage

| Component | Layer 1 | Layer 2 | Layer 3 | Layer 4 | Total Target |
|-----------|---------|---------|---------|---------|--------------|
| Protocol | 10 tests | 5 tests | 2 tests | - | 80% |
| Gate | 30 tests | 15 tests | 5 tests | 3 tests | 95% |
| State | 15 tests | 10 tests | 5 tests | 3 tests | 90% |
| Audit | 15 tests | 10 tests | 5 tests | 3 tests | 90% |
| Hook | 10 tests | 5 tests | 3 tests | 0 tests | 85% |
| Transcript | 15 tests | 10 tests | 5 tests | 3 tests | 90% |

**Total Tests:** ~155 tests for Step 1

**Acceptance Test Coverage:**
- AT-1.1 through AT-1.10: All covered by pyramid tests
- Each AT maps to specific pyramid layer

---

## Test Priorities

### P0 (Must Pass Before Commit)
- All Layer 1 tests (building blocks)
- All Layer 2 tests (edge cases)
- Critical Layer 3 tests (happy path integration)

### P1 (Must Pass Before Merge)
- All Layer 3 tests (all integration scenarios)
- Critical Layer 4 tests (crash safety, atomic writes)

### P2 (Nice to Have, Run Weekly)
- Remaining Layer 4 tests (rare failure scenarios)
- Performance benchmarks
- Load tests (concurrent operations)

---

## Success Criteria

**Step 1 Testing Complete When:**
- ✅ All 6 components have test pyramids implemented
- ✅ Coverage targets met (80-95% per component)
- ✅ All 10 acceptance tests pass
- ✅ P0 tests run <10 seconds total
- ✅ P1 tests run <60 seconds total
- ✅ Manual testing confirms transcript readability

---

**Next:** Execute test implementation per Tasks 1.0-5.0

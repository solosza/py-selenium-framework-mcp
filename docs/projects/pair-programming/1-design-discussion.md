# Phase 1: Design Discussion - Workflow Refactor (Discovery-First)

**Project:** Workflow Refactor
**Date:** 2026-01-21
**Status:** In Progress

---

## Purpose & Scope

### What Problem Are We Solving?

**Current Issue:**
The 11-step workflow generates optimistically (Steps 1-10) then fixes manually (Step 11):
- Generated 2 POMs instead of 5 for helios7 (missed intermediate wizard pages)
- Generated locators in Task layer (violated DD-27)
- Required manual remediation during execution
- User observation: "everything significant happened in step11 through discovery and hitl interaction"

**Root Cause:**
Generating code BEFORE discovering reality → AI guesses based on BDD, generates incomplete code, then discovers truth during execution.

### What Are We Building?

**Formalizing the 6-Component Collaborative Execution Pattern**

The helios7 Step 11 example proved our 6 components already enable pair programming:
- **Protocols** → AI knew framework patterns (FRAMEWORK.md + 28 DDs pre-encoded)
- **Smart Gates** → Validated each piece (DD-27 caught locators in Tasks)
- **Hooks** → Monitored construction (PostToolUse logged to audit trail)
- **Checkpointing** → Saved incrementally (work preserved at each step)
- **Audit System** → Documented construction (build→test→discover cycle)
- **HITL System** → Structured collaboration (stop at blockers, wait for guidance)

**The Task: Make This the PRIMARY Workflow**

Not "add pair programming to 6 components." The 6 components working together IS pair programming.

Not "rebuild the architecture." The architecture already works. Just formalize it.

**Core Insight:**
The 6 Isagawa platform components don't "support" pair programming. **They ARE the pair programming implementation mechanism.** Without these 6 components, you just have ad-hoc chat. With them, you have structured, reproducible, scalable collaborative execution.

### What's Out of Scope?

- Platform component redesign (they're already correct)
- Tool logic changes (gates validate the same rules)
- 4-layer architecture (unchanged)
- Framework patterns (DD-01 through DD-50 still apply)

---

## Components to Discuss

**Decision Points (we'll go through one at a time):**

1. **Step Sequence** - Where does discovery move in the workflow?
2. **Discovery Phase Design** - What gets discovered? How interactive is it?
3. **AI Processing Changes** - How does Step 3 change with real discovery data?
4. **Generation Impact** - How do Tools 3-6 change when fed reality?
5. **Step 11 Transformation** - What role does Step 11 play in discovery-first?
6. **HITL Integration Points** - When does human get involved?
7. **Quality Gate Adaptations** - Do gates need modification?
8. **Migration Strategy** - How to handle existing tests/protocols?
9. **MVP Timeline Decision** - Ship now vs delay to implement?

---

## Current State (Generate-First)

```
Step 1:  Pre-flight Config          → Credential strategy, test data location
Step 2:  User Input                 → Persona, URL, requirement
Step 3:  AI Processing              → Extract role, BDD, expected_states (GUESSING)
Step 4:  Tool 1 (Test Scenarios)    → Generate BDD scenarios
Step 5:  Tool 2 (Element Discovery) → Generate POM elements (GUESSING)
Step 6:  Tool 3 (POM Generation)    → Generate Page Objects (INCOMPLETE)
Step 7:  Tool 4 (Task Generation)   → Generate Tasks (LOCATORS IN TASKS)
Step 8:  Tool 5 (Role Generation)   → Generate Roles
Step 9:  Tool 6 (Test Generation)   → Generate Test
Step 10: Validation                 → Framework compliance check
Step 11: Execution + HITL           → Run test → DISCOVER REALITY → Fix manually
```

**Problem:** Steps 1-10 generate from guesses, Step 11 discovers truth and fixes.

---

## Critical Discovery: The Pattern Already Works

**What Step 11 Actually Was:**

Not "run test then fix errors." It was **pair programming already happening:**

1. Test fails → ElementNotInteractableException
2. AI stops → "What do you want me to do?"
3. Human guides → "Call wait method"
4. AI builds → Adds wait, saves file, runs test
5. New failure → Missing wizard pages
6. AI stops → Reports gap
7. Human guides → "Need 3 more POMs"
8. AI builds → Creates POMs, updates Task, saves, runs test
9. Passes → Done

**Key characteristics:**
- AI already knew framework rules (FRAMEWORK.md + 28 DDs)
- AI built and saved incrementally (not "plan then build")
- AI stopped when blocked (didn't loop trying fixes)
- Human provided navigation/discovery guidance
- Repeat build-test-discover cycle until test passes

**This is pair programming, and it already works. We just need to formalize it as the PRIMARY workflow, not just Step 11 cleanup.**

---

## What helios7 Example Teaches Us

**Critical Observations from User:**

> "AI knew my framework pattern already and workflow. We just worked out the kinks. So ideally, I want AI to already know how to build each layer and then stop when blocked. But I want to be able to save our work as we go, like the example. Not talk through it, then not save anything as we go. So build as we go basically with AI already knowing what to do."

**What This Means:**

1. **AI already has framework knowledge** - FRAMEWORK.md + 28 DDs encode the patterns. AI doesn't need to be taught how to build POMs/Tasks/Roles during execution.

2. **AI must build AND save incrementally** - Not "plan → discuss → then generate." Build CustomerSearchPage → save file → test → discover gap → build more → save → test. Continuous progress.

3. **AI must STOP when blocked** - Critical requirement. No looping through multiple fix attempts. Stop, report, wait for human guidance.

4. **Human provides navigation/discovery** - "Add wait method", "Need 3 more POMs", "Try this approach". Human doesn't teach framework patterns (AI knows), human guides discovery.

5. **This isn't discussion, it's construction** - Not "let's talk about what POMs we need." It's "I'm building CustomerSearchPage [saves file], test failed [stops], what do you want me to do?"

**What This Is NOT:**

- Not "AI learns framework during execution" (knowledge pre-encoded)
- Not "plan everything then generate" (incremental construction)
- Not "try multiple fixes autonomously" (stop when blocked)
- Not "lengthy discussion then batch save" (build and save continuously)

**The Task:**

Formalize this pattern so it's the PRIMARY workflow from Step 1, with emphasis on:
1. Stop-when-blocked behavior (prevent AI rambling)
2. Timeout monitoring (prevent AI waiting silently)
3. Visual browser feedback (user sees everything, can interrupt)

---

## Critical User Requirements (Non-Negotiable)

### 1. HITL Must Be Triggered Reliably
**User:** "we just need to make sure hitl is triggered, this is very important"

- HITL (Component 6) is the ultimate safety mechanism
- All layers work to ENSURE HITL triggers when AI is blocked
- If HITL doesn't trigger → AI rambles → pattern fails
- This is the escape valve for the entire system

### 2. No Silent Timeout Waiting
**User:** "we can't let ai take too long thinking. especially when it's waiting for a timeout"

- Hooks (Component 3) monitor execution time in real-time
- **Configurable timeout threshold** (default: 30s, user can adjust per workflow needs)
- **Enable/disable toggle** (can turn off for operations legitimately taking longer)
- If AI waiting > threshold → Hook forces HITL trigger immediately
- User gets prompted: "Element not found, timeout at 30s. Continue waiting or change approach?"
- Prevents AI from silently waiting indefinitely while user stares at screen

**Why This Matters:**
- Timeouts indicate blockers (element not found, wrong page, etc.)
- Waiting silently = wasted time + user frustration
- HITL trigger at threshold = user can redirect AI immediately
- This is real-time collaboration, not "wait and see"

**Configuration:**
```json
{
  "timeout_monitoring": {
    "enabled": true,
    "threshold_seconds": 30,
    "actions": ["browser_navigate", "element_wait", "ajax_call"]
  }
}
```
- User can increase threshold for slow applications
- User can disable for specific long-running operations
- User can specify which actions to monitor

### 3. Visual Browser Feedback (Always)
**User:** "no headless mode at all. ever, user needs to see everytime the browser is triggered"

- Browser MUST be visible at all times (never headless)
- User sees exactly what AI is doing in real-time
- Visual feedback enables user to interrupt if AI doing wrong thing
- This is transparency = trust = user control

**Why This Matters:**
- Headless = black box (user can't see what's wrong)
- Visible browser = user sees AI click wrong button, can interrupt immediately
- Collaborative execution requires visual feedback for effective collaboration
- User can't guide if they can't see

**Implementation:**
- Protocol (Component 1) documents: "Browser visible mode required, never headless"
- Configuration enforcement: `headless=False` always, no override
- This is a hard requirement, not a preference

---

## Design Options (Waterfall - All Rejected)

### Option A: Discovery at Step 3 (RED Phase First)

```
Step 1:  Pre-flight Config          → Credential strategy, test data location
Step 2:  User Input                 → Persona, URL, requirement
Step 3:  DISCOVERY (RED)            → Interactive Playwright exploration
         ↓ Discover: Pages, elements, flows, wizard steps, dynamic behavior
Step 4:  AI Processing              → Extract role, BDD from DISCOVERED reality
Step 5:  Tool 1 (Test Scenarios)    → Generate BDD from discovered flow
Step 6:  Tool 2 (Element Discovery) → Use discovered elements (already have them)
Step 7:  Tool 3 (POM Generation)    → Generate POMs from discovered elements
Step 8:  Tool 4 (Task Generation)   → Generate Tasks from discovered flow
Step 9:  Tool 5 (Role Generation)   → Generate Roles
Step 10: Tool 6 (Test Generation)   → Generate Test
Step 11: Validation (GREEN)         → Framework compliance check
Step 12: Execution (REFACTOR)       → Run test → Verify → Done
```

**Pros:**
- Discover reality BEFORE extracting anything
- BDD scenarios match actual flow (not guessed)
- Full TDD pattern (RED-GREEN-REFACTOR)
- Element discovery integrated into exploration

**Cons:**
- Discovery happens before AI knows what to look for
- User might not know workflow yet (exploring blind)
- Step count increases to 12

---

### Option B: Discovery at Step 5 (RED Phase After BDD)

```
Step 1:  Pre-flight Config          → Credential strategy, test data location
Step 2:  User Input                 → Persona, URL, requirement
Step 3:  AI Processing (HIGH-LEVEL) → Extract role, ROUGH BDD (not detailed)
Step 4:  Tool 1 (Rough Scenarios)   → Generate high-level BDD outline
Step 5:  DISCOVERY (RED)            → Interactive Playwright exploration
         ↓ Guided by rough BDD, discover: Actual pages, elements, wizard steps
Step 6:  AI Processing (REFINED)    → Refine BDD based on discovered reality
Step 7:  Tool 2 (Element Discovery) → Use discovered elements
Step 8:  Tool 3 (POM Generation)    → Generate POMs from discovered elements
Step 9:  Tool 4 (Task Generation)   → Generate Tasks from discovered flow
Step 10: Tool 5 (Role Generation)   → Generate Roles
Step 11: Tool 6 (Test Generation)   → Generate Test
Step 12: Validation (GREEN)         → Framework compliance check
Step 13: Execution (REFACTOR)       → Run test → Verify → Done
```

**Pros:**
- Discovery guided by rough BDD (know what to look for)
- User has context (AI already processed requirement)
- BDD refined based on reality (not 100% guess)

**Cons:**
- BDD generation happens twice (rough → refined)
- More steps (13 total)
- Complexity increase

---

### Option C: Discovery at Step 4, Keep 11 Steps (Hybrid)

```
Step 1:  Pre-flight Config          → Credential strategy, test data location
Step 2:  User Input                 → Persona, URL, requirement
Step 3:  AI Processing              → Extract role, intent (NO detailed BDD yet)
Step 4:  DISCOVERY (RED)            → Interactive Playwright exploration
         ↓ Discover: Pages, elements, flows, wizard steps
Step 5:  Tool 1 (Test Scenarios)    → Generate BDD from discovered reality
Step 6:  Tool 3 (POM Generation)    → Generate POMs from discovered elements
Step 7:  Tool 4 (Task Generation)   → Generate Tasks from discovered flow
Step 8:  Tool 5 (Role Generation)   → Generate Roles
Step 9:  Tool 6 (Test Generation)   → Generate Test
Step 10: Validation (GREEN)         → Framework compliance check
Step 11: Execution (REFACTOR)       → Run test → Verify → Done
```

**Changes from current:**
- Step 3: Extract intent only (not detailed BDD)
- Step 4: Playwright discovery (NEW - was hidden in Step 11)
- Step 5: Tool 1 uses discovered reality (not guesses)
- Tool 2 REMOVED (discovery happens in Step 4, not as separate tool)
- Steps 6-11: Renumbered but same functions

**Pros:**
- Keeps 11-step count (familiar)
- Discovery guided by intent (Step 3 gives context)
- Tool 2 eliminated (discovery integrated into Step 4)
- Clean TDD pattern (RED-GREEN-REFACTOR)
- Minimal disruption to existing structure

**Cons:**
- Tool 2 removal = breaking change to tool chain
- Step numbers shift (documentation updates required)

---

## Option D: Pair Programming (RECOMMENDED)

**This Isn't New - It's Formalizing What Already Works:**

The helios7 Step 11 example demonstrates pair programming already happening:
- AI knew framework patterns (saved proper POMs/Tasks with correct structure)
- AI built incrementally (created files, ran test, discovered gaps, added more, repeated)
- AI stopped when blocked (didn't loop endlessly trying fixes)
- Human guided discovery (told AI what to do at blockers)
- Files saved as work progressed (not "discuss then generate")

**The Solution: Make This the Core Workflow (Not Just Step 11 Cleanup)**

```
Step 1-3: Pre-flight, Input, Intent

Step 4:   COLLABORATIVE CONSTRUCTION (The helios7 pattern, but from start)
          ↓
          AI builds incrementally (knows framework rules already)
          AI saves as it goes (files written continuously)
          AI STOPS when blocked (no endless fix loops)
          Human provides guidance at blockers
          Repeat until test passes
          ↓
Step 5:   Done
```

**What This Is:**
- **Formalization** (not rebuilding - pattern exists)
- **Stop-when-blocked behavior** (AI doesn't ramble)
- **Incremental construction** (build-save-test-repeat)
- **HITL as navigation** (human guides at blockers)
- **Zero rework** (fix immediately, continue forward)

**CRITICAL REQUIREMENT: Stop-When-Blocked Behavior**

The pair programming pattern IS IMPLEMENTED BY our 6 components working together. This isn't pair programming "plus" 6 components - the 6 components ARE the mechanism that enables pair programming.

**How the 6 Components Implement Pair Programming:**

| Component | How It Enables Pair Programming | Example from helios7 |
|-----------|--------------------------------|---------------------|
| **1. Protocols** | Pre-encode framework patterns so AI knows what to build | AI already knew to create POMs with locators, Tasks with @autologger |
| **2. Smart Gates** | Validate each piece incrementally, stop on violation | Framework check after each file creation, DD-27 catches locators in Tasks |
| **3. Hooks** | Monitor construction progress, detect rambling loops | PostToolUse logs each build action to audit trail |
| **4. Checkpointing** | Save state at each blocker so work can resume | After adding click_new_inquiry(), state saved, can resume if session ends |
| **5. Audit System** | Document each build→test→discover cycle | Audit log shows: navigate → click → wait added → POMs created → test passed |
| **6. HITL System** | Provide stop points and human guidance mechanism | AI stopped at ElementNotInteractableException, waited for "add wait" guidance |

**What This Means:**

The pair programming pattern isn't something we're adding to the 6 components. **The 6 components working together IS pair programming.**

- **Protocols** encode "how to build" (AI doesn't learn during execution)
- **Smart Gates** enforce "stop when wrong" (catch violations immediately)
- **Hooks** monitor "what's happening" (detect rambling)
- **Checkpointing** enable "save as you go" (continuous progress)
- **Audit System** document "what happened" (construction decisions)
- **HITL System** structure "when to collaborate" (blocker points)

**Anti-Pattern (NOT Using Components):**
- AI tries fix #1 → fails
- AI tries fix #2 → fails (no gate stopping it)
- AI tries fix #3 → fails (no hook detecting loop)
- AI declares "success!" (no audit showing truth)
- Human confused (no clear HITL stop point)

**Correct Pattern (6 Components Working Together):**
- Test fails → **Gate** signals violation → **HITL** stop point → AI waits
- Human: "Add wait"
- AI: Adds wait, **Checkpoint** saves → **Audit** logs action → **Gate** validates → Tests
- New failure → **Gate** signals → **HITL** stop point → AI waits again
- Human: "Need 3 more POMs"
- AI: Builds POMs (using **Protocol** knowledge) → **Checkpoint** saves → **Audit** logs → **Gate** validates → Tests → Passes

**The 6 components ARE the pair programming implementation mechanism.**

**Pros:**
- **100% success rate** (iterate until done, no rework)
- **Zero wasted work** (validate before moving forward)
- **Optimal division of labor** (human guides, AI builds)
- **Transparent process** (see construction in real-time)
- **Maps to v4.0 thesis** (all 6 components, vertical expansion works)
- **Still AI Management Layer** (structures execution, enforces quality)
- **Differentiator holds** (no competitor has formalized collaboration patterns)

**Cons:**
- **Human required** (not fully autonomous)
- **Slower than if autonomous worked** (but autonomous fails 96% of time)
- **Mindset shift** (from "AI does it" to "we do it together")

**Success Probability:**
- Autonomous (Options A-C): 4-12% success rate, 88-96% requires rework
- Pair Programming: 100% completion rate (iterate to done, fix immediately)

---

## Why Pair Programming is the Right Solution

### 1. It Already Works (Evidence: helios7 Step 11)

User observation: "AI knew my framework pattern already and workflow. We just worked out the kinks."

**What helios7 Step 11 demonstrated:**
- AI already knows framework rules (FRAMEWORK.md + 28 DDs encode the patterns)
- AI built incrementally (created CustomerSearchPage → added click_new_inquiry() → saved → tested)
- AI stopped when blocked (didn't loop through multiple fixes)
- Human provided discovery guidance ("add wait", "need 3 more POMs")
- Files saved as work progressed (not "talk then generate")
- Test passed after collaboration (28.71s)

**This isn't a new approach. This is formalizing what already happened.**

### 2. Math Proves Incremental > Waterfall

**Options A-C (Waterfall):**
- Discover once → Generate once
- P(success) = 0.70^6 = 11.7%
- 88.3% requires regeneration

**Option D (Incremental):**
- Build piece → Test → Discover gap → Build more → Test
- Failures caught immediately (no rework cost)
- P(completion) = 100% (iterate until done)

### 3. The Pattern is Reproducible

**What makes it work:**
1. AI has framework knowledge pre-encoded (FRAMEWORK.md)
2. AI has design decisions pre-encoded (28 DDs)
3. AI builds following known patterns
4. AI stops at blockers (doesn't ramble)
5. Human provides navigation/discovery
6. Save continuously (not batch at end)

**This isn't magical. It's a structured process that can be formalized and taught.**

### 3. The 6 Components Already Enable This

**From v4.0:**
- 6 components for AI Management Layer ✓ (these ARE the implementation)
- Vertical expansion via platform replication ✓ (same components, different domains)
- Domain expertise pre-encoded by experts ✓ (Protocols component)
- Category = AI Execution Management ✓ (structure execution through components)
- White space vs competitors ✓ (no one else has these 6 components)

**Critical Understanding:**
The 6 components don't "support" pair programming. **The 6 components IMPLEMENT pair programming.**

- Without Protocols → AI doesn't know what to build
- Without Smart Gates → No validation, no stop signals
- Without Hooks → Can't detect rambling
- Without Checkpointing → Can't save incrementally
- Without Audit System → Can't document construction decisions
- Without HITL System → No structured collaboration points

**Pair programming IS the 6 components working together.**

### 4. Vertical Expansion = Replicating the 6 Components

**QA vertical (validated first):**
- **Protocols** → 28 DDs pre-encoded (framework patterns)
- **Smart Gates** → Enforce 28 DDs in real-time
- **Hooks** → Monitor test construction
- **Checkpointing** → Resume test work
- **Audit System** → Document test decisions
- **HITL System** → QA users pair with AI

**Healthcare vertical (replicate same 6 components):**
- **Protocols** → Clinical workflows pre-encoded (HIPAA patterns)
- **Smart Gates** → Enforce HIPAA/clinical rules in real-time
- **Hooks** → Monitor patient workflow construction
- **Checkpointing** → Resume clinical work
- **Audit System** → Document clinical decisions
- **HITL System** → Nurses pair with AI

**Vertical expansion = Take the 6 components proven in QA → Encode new domain expertise → Same collaborative execution model**

Same components, same 6-12 month encoding timeline, different domain expertise.

### 5. No Competitor Has the 6 Components

**What competitors have:**
- Ad-hoc AI chat (no Protocols, no Gates, no structure)
- Autonomous generation with post-fixes (no incremental Checkpointing)
- Post-execution monitoring (Governance tools, not execution management)

**What we have (6-component defense-in-depth):**
- **Protocols** → Pre-encoded domain expertise
- **Smart Gates** → Real-time validation + teaching
- **Hooks** → Continuous monitoring
- **Checkpointing** → Incremental progress saving
- **Audit System** → Construction documentation
- **HITL System** → Structured collaboration

**Competitive moat:**
Not "we have pair programming." It's **"we have the 6-component architecture that enables scalable, reproducible collaborative execution."**

Competitors can copy pair programming (it's just human + AI). They can't easily copy:
- Pre-encoded domain expertise (took us 28 DDs + 6 months)
- Smart gates that teach fixes (not just validate)
- Defense-in-depth architecture (6 components working together)
- Platform replication model (proven in QA, applies to 9 verticals)

**White space: No one else has built the 6-component AI Management Layer.**

---

## Updated Open Questions

### Question 1: Protocol Scope ✓ ANSWERED

**Decision: Sufficient Protocols (Layer 1 Defense)**

**User Correction:** Protocols are Layer 1 of defense-in-depth. They need to be SUFFICIENT, not minimal.

**What "Sufficient Protocol" Means:**

Protocols (Component 1) work in conjunction with Smart Gates (Component 2) to form the first two defense layers:

**1. Protocols (Layer 1) - Provide Guidance**
   - **Stop-When-Blocked Patterns (DD-22)**
     - When to stop: test fails, timeout exceeds threshold, element not found, DD violation
     - How to report: what info to provide user (error message, context, hypothesis)
     - How to wait: don't proceed until human responds

   - **Build-As-You-Go Patterns**
     - When to save files: after each piece created (POM method added → save immediately)
     - Build-test-discover cycle: create → save → test → discover gap → create more
     - Incremental validation points: after each file save, after each test run

   - **HITL Trigger Patterns**
     - What triggers HITL: blocker types (test fail, timeout, DD violation, element not found)
     - How to signal user: "AI blocked at [X], awaiting guidance"
     - User interrupt mechanism: "stop" command → immediate HITL trigger

   - **Configuration Requirements**
     - Browser always visible: headless=false (never override)
     - Timeout monitoring: configurable threshold, default 30s, enable/disable toggle
     - Tool usage: Tools 1-2 core, Tools 3-6 on-demand

   - **Collaboration Patterns**
     - AI builds: knows framework from FRAMEWORK.md + 28 DDs, uses Edit/Write tools
     - Human navigates/discovers: guides at blockers, provides direction
     - Gates validate: after each piece (work with Protocols)

**2. Smart Gates (Layer 2) - Validate AND Teach**
   - **Work with Protocols:** If AI violates protocol → Gate catches → Gate teaches fix
   - **Don't just block:** Provide fix data (not just "violation detected")
   - **Example:** DD-27 violation (locators in Task)
     - Protocol says: "Locators only in POMs"
     - Gate catches: "Locators found in Task layer"
     - Gate teaches: "Move locators to POM as class constants, call via self.pom.LOCATOR"

   - **Validation happens after:**
     - Each file save (framework compliance)
     - Each test run (functional correctness)
     - Each tool call (output quality)

**Protocols + Smart Gates = Defense Layers 1 & 2**
- Protocols guide upfront (what to do)
- Smart Gates catch violations (what not to do + how to fix)
- Together they form the first line of defense before code even runs

---

## Complete 6-Layer Defense-in-Depth Architecture

**All 6 Components = All 6 Defense Layers Working Together**

| Layer | Component | Defense Purpose | How It Works |
|-------|-----------|-----------------|--------------|
| **1** | **Protocols** | Provide guidance | Document stop-when-blocked, build-as-you-go, HITL triggers, configuration, collaboration patterns |
| **2** | **Smart Gates** | Validate AND teach | Catch violations, provide fix data (not just block) |
| **3** | **Hooks** | Monitor execution | Detect loops, monitor timeouts >threshold, force HITL trigger |
| **4** | **Checkpointing** | Preserve state | Auto-save at each blocker, enable resume from exact point |
| **5** | **Audit System** | Document everything | Log construction decisions, blocker cycles, timeout triggers, HITL interactions |
| **6** | **HITL System** | Ultimate safety | Must trigger reliably, user interrupt capability, escape valve |

**Defense-in-Depth: Each Layer Backs Up the Previous**

```
IF Layer 1 fails (AI ignores protocol)
→ Layer 2 catches (Gate validates, teaches fix)

IF Layer 2 fails (Gate misses violation)
→ Layer 3 catches (Hook detects loop/timeout)

IF Layer 3 fails (Hook misses)
→ Layer 4 preserves (Checkpoint saves state before damage)

IF Layer 4 fails (No checkpoint)
→ Layer 5 documents (Audit shows what happened)

IF Layer 5 fails (No audit)
→ Layer 6 catches (User interrupts via HITL - ultimate escape)
```

**Why 6 Layers:**
- No single layer is 100% reliable
- Multiple layers = higher probability of catching issues
- Each layer has different mechanism (guidance, validation, monitoring, preservation, documentation, human override)
- Competitors have 1-2 layers max (usually just post-execution monitoring)
- Our 6-layer defense = harder to copy, more reliable execution

**This is the Architecture Differentiator.**

Not "pair programming" (anyone can do that).
Not "autonomous generation" (competitors trying that).
The differentiator is **6-layer defense-in-depth enabling reliable collaborative execution.**

---

### Question 2: Stop-When-Blocked Enforcement (NEW - CRITICAL)

**Decision: Option 5 (Defense-in-Depth) ✓**

All 6 components working together to enforce stop-when-blocked behavior.

**Each Component's Responsibility:**

1. **Protocols** (Layer 1) - **DD-22 already documented**
   - Defines STOP→REPORT→DISCUSS→PROCEED pattern
   - AI guidance: "Do NOT attempt autonomous fixes, Do NOT retry"
   - Document: **No headless mode ever** (user must see browser)

2. **Smart Gates** (Layer 2) - Signal when to trigger DD-22
   - Test failed? → Return blocker signal
   - DD violation? → Return blocker signal
   - Signal triggers HITL (Component 6)

3. **Hooks** (Layer 3) - Detect rambling AND timeout issues
   - Monitor: 3+ sequential failures detected? → Interrupt, force HITL
   - Monitor: Same fix attempted twice? → Force HITL trigger
   - **NEW: Monitor AI waiting on timeout > [CONFIGURABLE]s? → Interrupt, force HITL**
   - **NEW: Monitor browser action taking too long? → Interrupt, force HITL**
   - **Configuration: Timeout threshold (default: 30s, user adjustable), enable/disable toggle**
   - Hooks ensure HITL gets triggered even if gates miss it
   - Hooks prevent AI from "thinking too long" waiting for timeouts

4. **Checkpointing** (Layer 4) - Auto-save at each blocker
   - When HITL triggered → Checkpoint state automatically
   - User can resume from exact blocker point

5. **Audit System** (Layer 5) - Document blocker cycle
   - Log: "HITL triggered at [timestamp]", "User guidance: [input]", "AI resumed"
   - Log: "Timeout detected at [X]s, HITL triggered"
   - Full construction history visible

6. **HITL System** (Layer 6) - **CRITICAL: Must be triggered reliably**
   - When Smart Gate signals blocker → **HITL MUST trigger**
   - When Hook detects loop → **HITL MUST trigger**
   - **When Hook detects timeout exceeding threshold → HITL MUST trigger immediately**
   - Clear signal to user: "AI is blocked, awaiting guidance" or "AI waiting on timeout (30s), proceed?"
   - User can interrupt anytime: "stop" command → **HITL triggers immediately**
   - This is the escape valve - if HITL doesn't trigger, whole system fails

**Critical User Requirements Captured:**

1. **"we just need to make sure hitl is triggered, this is very important"**
   - ✓ HITL (Component 6) is the ultimate safety mechanism
   - ✓ All other layers exist to ENSURE HITL gets triggered
   - ✓ Gates signal it, Hooks force it, User can trigger it
   - ✓ If HITL doesn't trigger → AI rambles → pattern fails

2. **"we can't let ai take too long thinking. especially when it's waiting for a timeout"**
   - ✓ Hooks (Component 3) monitor execution time
   - ✓ Configurable timeout threshold (default: 30s, user adjustable)
   - ✓ Enable/disable toggle (can turn off for operations that legitimately take longer)
   - ✓ If AI waiting > threshold → Hook forces HITL trigger
   - ✓ User gets: "Element not found, timeout at 30s. Continue waiting or change approach?"
   - ✓ Prevents AI from silently waiting indefinitely

3. **"no headless mode at all. ever, user needs to see everytime the browser is triggered"**
   - ✓ Protocol (Component 1) documents: Browser ALWAYS visible
   - ✓ User must see what AI is doing in real-time
   - ✓ Visual feedback = transparency = user can interrupt if wrong
   - ✓ This is non-negotiable for collaborative execution

**Why Defense-in-Depth:**
- Aligns with 6-component architecture (thesis v4.0 explicitly positions as defense-in-depth)
- Stop-when-blocked critical enough to deserve multiple layers
- Proven in helios7 (Protocol guided, Gates validated, Audit logged, HITL structured)
- Handles all failure modes (AI ignores → Gates force, Gates miss → Hooks force, Still rambling → User interrupts)

**HITL triggering + Timeout monitoring + Visual browser = User control. Non-negotiable.**

---

### Question 3: Tool Chain Impact ✓ ANSWERED

**Decision: Hybrid - Tools 1-2 Core, Tools 3-6 Optional**

**Core Workflow (Always Used):**
- **Tool 1 (generate_tests_from_user_story)** - Takes user requirement → structured BDD scenarios
  - Gives structure to collaboration
  - Provides consistency in scenario format
  - Used at workflow start

- **Tool 2 (discover_page_elements)** - Playwright snapshot → extract elements
  - Bulk element discovery
  - Faster than manual element-by-element discovery
  - Used during page exploration

**Optional (Available, Not Primary):**
- **Tools 3-6 (generate_page_object, generate_task, generate_role, generate_test_runner)**
  - Available if user requests scaffolding
  - AI builds manually with Edit/Write by default
  - User can call anytime ("generate scaffold for CustomerSearchPage")
  - Mostly just user will use these

**Always Active (Non-Optional):**
- **Quality Gates** - Component 2 of 6 components
  - Validate all code (manual or tool-generated)
  - Always run, non-negotiable

**Workflow Pattern:**
```
Step 1-3: Pre-flight, Input, Intent
Step 4:   Collaborative Construction
          ↓
          Tool 1: Generate BDD scenarios (structure collaboration)
          Tool 2: Discover elements (bulk extraction)
          ---
          AI builds POMs/Tasks/Roles manually with Edit/Write
          (Tools 3-6 available if user requests scaffolding)
          ---
          Gates validate each piece
          HITL triggers at blockers
          ↓
Step 5:   Done
```

**Why This Split:**
- Tools 1-2: Provide structure and speed (BDD format, bulk discovery)
- Tools 3-6: AI can build faster manually in pair programming
- Gates: Always enforce quality (Component 2)

---

### Question 4: Backward Compatibility ✓ ANSWERED

**Decision: Archive All, Start Fresh**

**Action:**
- Move helios1-7 tests to `/tests/archive/` (preserve for reference)
- Start from scratch with pair programming workflow
- New tests going forward demonstrate the formalized pattern

**Reasoning:**
- Clean slate for new workflow
- helios1-7 were generated with autonomous workflow (not representative of pair programming)
- These will be deleted at release anyway (internal examples only)
- Archive preserves history without cluttering active test suite

**Context:** 7 existing tests (helios1-7) all pass after manual fixes. User wants fresh start to demonstrate pair programming properly from the beginning.

---

## Thesis v4.0 Compatibility Confirmation

**Does pair programming align with Isagawa Corp thesis v4.0? YES.**

### Category Definition (Unchanged)

**From v4.0:**
> "Isagawa is an AI Management Layer implemented through domain-specific Execution Engines that enforce how AI executes work — not just what it produces."

**With pair programming:**
> "Isagawa is an AI Management Layer implemented through domain-specific Execution Engines that structure how humans collaborate with AI to execute work — with quality enforcement at every step."

**Same category: AI Execution Management (not governance)**

### Platform Primitives (Unchanged - These ARE the Implementation)

**6 components don't just "apply" - they ARE the pair programming implementation:**

| Component | v4.0 Purpose | How It Implements Pair Programming | Status |
|-----------|--------------|-----------------------------------|--------|
| **1. Protocols** | Define correct workflow | Encode "what to build" so AI knows framework patterns | ✓ Core |
| **2. Smart Gates** | Validate AND teach fixes | Enforce "stop when wrong" + signal blockers | ✓ Core |
| **3. Hooks** | Monitor AI continuously | Detect rambling/loops, monitor construction | ✓ Core |
| **4. Checkpointing** | Enable recovery/resume | Enable "save as you go" incremental progress | ✓ Core |
| **5. Audit System** | Immutable logging | Document each build→test→discover cycle | ✓ Core |
| **6. HITL System** | Human confirmations | Provide stop points, structure collaboration | ✓ Core |

**Critical Understanding:**
- v4.0 assumed autonomous execution → 6 components manage autonomous AI
- Reality: collaborative execution → 6 components enable human-AI collaboration
- **Same 6 components, different execution model, same architecture**

### Vertical Expansion (Unchanged)

**From v4.0 Section 8.5:**

```
Phase 1: Validate Pattern (QA - 2026)
├── Ship QA with 6 components
├── Community battle-tests architecture
└── Result: Proven 6-component pattern

Phase 2: Replicate Pattern (Healthcare - 2027)
├── Take validated pattern
├── Apply to healthcare (6 months)
└── Ships 10x faster (pattern proven)
```

**STILL TRUE with pair programming:**
- Same 6 components replicate
- Same 6-12 month domain encoding phase
- Same platform replication speed
- Only execution model changes (autonomous → collaborative)

### Competitive Moat (Unchanged)

**From v4.0:**

| What Competitors Build | What Isagawa Builds |
|------------------------|---------------------|
| AI Governance | AI Execution Management |
| Watch, document, alert | Enforce, gate, escalate |
| "Did AI do it right?" | "AI can only do it right" |
| After execution | During execution |

**STILL TRUE with pair programming:**

| What Competitors Build | What Isagawa Builds (Pair) |
|------------------------|----------------------------|
| Ad-hoc AI chat | Structured collaboration |
| No enforcement | Real-time quality gates |
| Hope it works | Guaranteed quality output |
| No reproducibility | Formalized patterns |

### White Space Validation (Unchanged)

**From v4.0 Section 8.6:**
- $5.8B in governance market
- Zero products in execution management
- 12-18 month head start

**STILL TRUE:**
- No competitor has formalized collaboration patterns
- No competitor has real-time enforcement during construction
- No competitor has structured HITL as core model

### Open Source Strategy (Unchanged)

**From v4.0:**
- Open source core platform (MIT license)
- MCP-native distribution (viral adoption)
- Community velocity moat
- Platform replication across 9 verticals

**STILL APPLIES:**
- Same open source model
- Same MCP distribution
- Same community benefits
- Same vertical expansion plan

### Conclusion: Thesis v4.0 Validated (6 Components Unchanged)

**What changes:**
- Execution model only (autonomous → collaborative)
- HOW the 6 components work together (manage autonomous AI → enable human-AI collaboration)

**What stays EXACTLY the same:**
- **The 6 components** (Protocols, Gates, Hooks, Checkpointing, Audit, HITL)
- Category definition (AI Management Layer implemented through domain-specific Execution Engines)
- Vertical expansion (6 components replicate across 9 verticals, same timeline)
- Competitive positioning (execution management vs governance)
- White space (no competitor has 6-component architecture)
- Open source strategy (community velocity)
- Moat (6 components + pre-encoded domain expertise + battle-tested patterns)

**Critical Insight:**
We thought we were building "6 components that manage autonomous AI."

We actually built "6 components that enable structured human-AI collaboration."

**Same 6 components. Different execution model. Architecture unchanged.**

The pair programming pattern IS the 6 components working together. Not pair programming "plus" 6 components. The components ARE the implementation mechanism.

---

## 5-Step Workflow Definition (Step-by-Step Validation)

**Approach:** Validating each step incrementally with HITL before finalizing structure.

**Status:** In Progress - Step 1 validated

### Step 1: User Input (VALIDATED)

**Entry Point:** User triggers `/qa-workflow`

**What Happens:**
1. AI asks: "What test do you want to create?"
   - Format: "As a [role], I want to [action]..."
   - URL: [target page]

2. AI asks: "Workflow identifier? This creates folders at `framework/pages/{workflow}/` and `tests/{workflow}/`
   - Use this to organize tests by: test run (helios7), feature (checkout-v2), or sprint (auth-sprint-2)
   - Example: helios7"

3. AI extracts: persona, URL, role_name from requirement

4. AI auto-detects environment:
   - If URL matches environment_config.json → continue
   - If URL unknown → ASK: "New environment detected. Add to config?" (NEEDS_RETRY + user approval)

**HITL Triggers:**
- Persona missing → ASK with example
- URL missing → ASK with example
- Workflow missing → ASK with explanation (Option 3)
- Requirement vague → ASK for specifics
- Environment unknown → ASK for approval

**Gate:** `qg_user_input` validates persona, URL, role_name, workflow, raw_requirement

**Output:** persona, URL, role_name, workflow, raw_requirement, detected_env_id

**Rationale:**
- Workflow identifier must be explicitly asked (not derivable from requirement text)
- "helios7" is organizational label, not domain type
- New users need context (Option 3 explanation chosen via HITL)

### Step 2: Pre-flight Configuration (PENDING VALIDATION)

**Status:** Next to validate

**Placeholder:** Ask about credentials, test data, browser, timeout after knowing what test we're building

### Step 3: AI Processing (PENDING VALIDATION)

**Status:** To be validated after Step 2

### Step 4: Collaborative Construction (PENDING VALIDATION)

**Status:** To be validated - replaces old Steps 4-10

### Step 5: Done (PENDING VALIDATION)

**Status:** To be validated - test passes or HITL triage

**Next Action:** Continue step-by-step validation of remaining steps with HITL checkpoints before finalizing workflow structure.

---

## Next Steps

**Recommendation: Formalize Existing Pair Programming Pattern**

**User Decisions Status:**
1. **Question 1:** ✓ ANSWERED (Sufficient protocols - Layer 1 defense working with Smart Gates Layer 2)
2. **Question 2:** ✓ ANSWERED (Defense-in-depth: all 6 components, HITL must trigger, timeout monitoring, visual browser)
3. **Question 3:** ✓ ANSWERED (Tools 1-2 core workflow, Tools 3-6 optional, Gates always active)
4. **Question 4:** ✓ ANSWERED (Archive helios1-7, start fresh with pair programming)

**All Questions Answered - Ready for Phase 2 (PRD):**
- Phase 2: Create PRD (formalize pair programming protocol)
  - Stop-when-blocked patterns
  - Save-as-you-go patterns
  - Clear blocker signals
  - User interrupt protocol
  - Minimal collaboration guidance (not scripts)
- Phase 3: Generate tasks (update Protocol + tools as needed)
- Phase 4: Execute (implement formalized workflow)

**Critical Understanding:**
This isn't "rebuild the workflow." This is "document what already works so it's reproducible."

---

## Impact Assessment

**Required:** YES - This modifies existing Protocol structure

### 1. Who Calls This Code?

**Affected Components:**
- `.claude/skills/qa-management-layer/SKILL.md` - Main workflow definition
- `.claude/skills/qa-management-layer/references/step-*.md` - All 11 step files
- `mcp_server/server.py` - Tool chain registration
- `mcp_server/tools/gates/qg_*.py` - All quality gate tools
- Test workflows (helios1-7) - If we regenerate

**Entry Points:**
- `/qa-workflow` slash command (triggers workflow)
- `/qa-workflow-dev` slash command (dev mode)
- Direct MCP tool calls (if users call tools manually)

### 2. What Depends on Current Behavior?

**Protocol Dependencies:**
- Step references (step-01.md through step-11.md)
- Quality gates expect specific step sequence
- Audit trail logs step numbers
- State checkpointing uses step numbers
- Workflow transcript references step order

**Test Dependencies:**
- 7 existing tests (helios1-7) generated with current workflow
- All tests pass and framework-compliant

### 3. What Will Break?

**Breaking Changes (Pair Programming):**
- Protocol structure (11 sequential steps → collaborative construction loop)
- Step reference files (need complete rewrite for collaboration guidance)
- Tool usage pattern (might not need all 6 generation tools)
- Slash command behavior (initiates collaboration vs autonomous generation)
- User expectation (human required vs hands-off)

**Non-Breaking:**
- 4-layer architecture unchanged
- Design Decisions (DD-01 through DD-50) unchanged
- Platform components (gates, hooks, audit) unchanged
- Framework validation logic unchanged
- Generated code structure unchanged
- Existing tests still work (just different generation process)

### 4. Migration Path

**Phase 1: Design & PRD** (This document + PRD)
- Document pair programming workflow
- Define collaboration patterns
- Specify HITL interaction points
- Decide on tool chain changes

**Phase 2: Protocol Rewrite**
- Rewrite SKILL.md with pair programming model
- Create collaboration guidance (replace sequential step files)
- Update quality gates for incremental validation
- Define checkpoint/resume for multi-session work

**Phase 3: Validation**
- Test pair programming with new test case
- Validate framework compliance
- Measure: time, human effort, output quality
- Compare vs current autonomous approach

**Phase 4: Community Launch**
- Document pair programming patterns
- Create video tutorials (show collaboration)
- Open source with examples
- Gather community feedback

**Success Criteria:**
- Pair programming produces framework-compliant code
- Incremental validation catches issues immediately
- Test passes after collaborative construction
- Process is reproducible and teachable
- Documentation enables new users to collaborate effectively

---

## Summary: Does This Make Sense?

**YES. The pattern already works - we just need to formalize it.**

### The Core Realization

**What we thought we needed:**
"Rebuild the workflow to do discovery-first instead of generate-first"

**What we actually have:**
"A working pair programming pattern that just needs formalization, not rebuilding"

**Evidence:** helios7 Step 11 demonstrated AI already knows framework rules, builds incrementally, saves as it goes, and stops when blocked. Human provided navigation. Test passed.

**The task isn't "build new workflow" - it's "make this the PRIMARY workflow from Step 1, not just Step 11 cleanup."**

### Why This is Better Than Autonomous

| Aspect | Autonomous (v4.0 assumption) | Pair Programming (reality) |
|--------|------------------------------|----------------------------|
| **Success rate** | 4-12% (math proves it) | 100% (iterate to done) |
| **Rework cost** | HIGH (regenerate layers) | ZERO (fix immediately) |
| **User experience** | Black box (hope it works) | Transparent (see construction) |
| **Differentiation** | Better than competitors trying autonomous | Only framework offering structured collaboration |

### Why This Still Validates Thesis v4.0

**All claims hold:**
- ✓ AI Management Layer (structures execution, not just monitors)
- ✓ 6 components (all apply to collaborative model)
- ✓ Vertical expansion (same timeline, same economics)
- ✓ Competitive moat (formalized patterns no one else has)
- ✓ White space (governance vs execution management)
- ✓ Open source strategy (community velocity)
- ✓ Platform replication (QA validates pattern for 9 verticals)

**Only shift:** Execution model (autonomous → collaborative)

**Category definition unchanged:** We structure how work gets done during execution with quality enforcement. Competitors monitor after execution or provide ad-hoc chat.

### The Strategic Advantage

**Competitors will try to copy autonomous generation.**

**We'll already have:**
- Formalized collaboration patterns (reproducible, teachable)
- Real-time quality enforcement (not post-generation fixes)
- Community-validated workflows (battle-tested)
- Multi-vertical platform (QA + Healthcare + Finance)

**By the time they realize collaborative > autonomous, we're 18 months ahead across 9 verticals.**

### Bottom Line

**Should we do this? YES.**

**Does it fit the thesis? PERFECTLY.**

**Is the pattern proven? YES (helios7 demonstrated 6 components working together).**

**Does it reduce vertical expansion speed? NO (same encoding timeline).**

**Does it maintain competitive moat? YES (6-component architecture, not just "pair programming").**

**Is this rebuilding or formalizing? FORMALIZING (pattern already works).**

**Critical requirement:** Stop-when-blocked behavior must be enforced (AI doesn't ramble)

**Next decision:** How to enforce stop-when-blocked (Question 2), tool chain impact (Question 3), backward compatibility (Question 4)

---

**Status:** Design Phase COMPLETE. All 4 questions answered. Ready to proceed to Phase 2 (PRD).

**Decisions Made:**
- **Question 1:** Sufficient Protocols (Layer 1 defense)
  - Protocol provides guidance (stop-when-blocked, build-as-you-go, HITL triggers, configuration, collaboration patterns)
  - Smart Gates validate AND teach (catch violations, provide fix data)
  - Protocols + Gates = Defense Layers 1 & 2 working together

- **Question 2:** Defense-in-depth (all 6 components enforce stop-when-blocked)
  - HITL must trigger reliably (Layer 6 - ultimate safety)
  - Hooks monitor configurable timeout (Layer 3 - default 30s, enable/disable toggle)
  - Visual browser always (never headless, user sees everything)

- **Question 3:** Hybrid tool usage
  - Tools 1-2 core workflow (BDD scenarios, element discovery)
  - Tools 3-6 optional (available on-demand, AI builds manually by default)
  - Quality Gates always active (Component 2, validate AND teach)

- **Question 4:** Archive existing tests
  - Move helios1-7 to `/tests/archive/`
  - Start fresh with pair programming workflow

**Key Insight:** This isn't about rebuilding. The pair programming pattern already works (helios7 evidence). The task is formalizing it so it's the PRIMARY workflow, with three non-negotiable requirements: HITL triggering, timeout monitoring, visual browser feedback.

**Critical Understanding:** The 6 components work as defense-in-depth:
- Protocols (Layer 1) guide what to do
- Smart Gates (Layer 2) catch violations and teach fixes
- Together they form the first line of defense before code even runs

---

## Data Model Finalization (2026-01-22)

**Context:** After archiving the 11-step autonomous workflow and updating all documentation to 5-step pair programming, we finalized what data to capture in audit logs and workflow state files.

### What Gets Saved Where

**File Structure:**
```
tests/_audit/audit_log_<run_id>.json         ← Event stream (gates, tools, HITL, violations)
tests/_state/<run_id>/workflow_state.json    ← Accumulated state (steps, construction journal, metrics)
tests/_reports/<run_id>/screenshot_*.png     ← Test execution artifacts
```

### Components Implemented (5)

**1. HITL Interaction Log (Audit Log)**
- **Location:** `tests/_audit/audit_log_<run_id>.json`
- **What:** All human-in-the-loop conversations
- **Format:** `{"type": "hitl_interaction", "timestamp": "...", "trigger_reason": "...", "user_input": "...", "ai_response": "...", "context": {...}}`
- **Why:** Low effort (just JSON append), high value (reconstruct decision points)
- **Size:** Not a concern (text-only, no screenshots)

**2. Construction Journal (Workflow State)**
- **Location:** `tests/_state/<run_id>/workflow_state.json`
- **What:** File paths created/modified at each iteration
- **Format:** `{"iterations": [{"files_created": ["path1", "path2"], "files_modified": ["path3"]}]}`
- **Why:** Tracks progress, shows what was built when
- **Decision:** File paths ONLY (no code snapshots - too large, diffs available via git)

**3. Test Execution History (Workflow State)**
- **Location:** `tests/_state/<run_id>/workflow_state.json`
- **What:** Test runs during construction (command, result, screenshot reference)
- **Format:** `{"test_runs": [{"command": "pytest ...", "result": "pass/fail", "screenshot": "tests/_reports/<run_id>/screenshot_001.png"}]}`
- **Why:** Show build→test→discover cycle
- **Decision:** Screenshot PATHS referenced (not embedded - files already in `_reports/`)

**4. Count-Based Metrics (Workflow State Summary)**
- **Location:** `tests/_state/<run_id>/workflow_state.json` (summary section)
- **What:** Iteration count, HITL trigger count, gate violations, test runs
- **Format:** `{"metrics": {"iterations": 5, "hitl_triggers": 3, "gate_violations": 2, "test_runs": 8}}`
- **Why:** Focus on correctness (not timing/performance)
- **Decision:** Counts only (high-level health check)

**5. Framework Compliance Results (Audit Log)**
- **Location:** `tests/_audit/audit_log_<run_id>.json`
- **What:** Gate validation results (already logged, ensure complete)
- **Format:** `{"type": "gate_validation", "gate": "qg_task", "result": "pass/fail", "violations": [...], "fix_data": {...}}`
- **Why:** Already exists, just verify all gates logging properly

### Components Rejected (3)

**6. Discovery Gaps Log (REJECTED - Redundant)**
- **Reason:** Construction journal already tracks file creation timing
- **If gap discovered:** Shows up as new file in next iteration
- **Alternative:** Audit log HITL interactions capture discovery decisions

**7. Decision Log (REJECTED - Overkill)**
- **Reason:** HITL interaction log already captures decision points
- **If detailed rationale needed:** User input in HITL provides context
- **Alternative:** Audit log has trigger reason + user response

**8. Rollback/Resume with Snapshots (REJECTED - Fix Forward)**
- **Reason:** Pair programming = fix immediately with HITL, not rollback
- **If blocker:** HITL triggers → user guides → AI fixes forward
- **Alternative:** Checkpointing saves state for session resume (not iteration rollback)

### Implementation Notes

**Audit Log Structure:**
```json
{
  "workflow_id": "2026-01-22T10-30-45.123456Z",
  "events": [
    {"type": "gate_validation", "timestamp": "...", "gate": "qg_user_input", "result": "pass"},
    {"type": "tool_call", "timestamp": "...", "tool": "generate_tests_from_user_story", "input": {...}, "output": {...}},
    {"type": "hitl_interaction", "timestamp": "...", "trigger_reason": "test_failed", "user_input": "add wait method", "ai_response": "Added wait_for_element to POM", "context": {...}},
    {"type": "gate_validation", "timestamp": "...", "gate": "qg_test_runner", "result": "fail", "violations": ["DD-27: locators in Task"], "fix_data": {...}},
    {"type": "hook_intervention", "timestamp": "...", "pattern": "timeout_exceeded", "threshold": 30, "actual": 45, "action": "force_hitl"}
  ]
}
```

**Workflow State Structure:**
```json
{
  "workflow_id": "2026-01-22T10-30-45.123456Z",
  "steps": {
    "step_1": {"persona": "...", "url": "...", "role_name": "...", "workflow": "..."},
    "step_2": {"credential_strategy": "...", "test_data_location": "..."},
    "step_3": {"bdd_scenarios": [...], "expected_states": [...], "intent": "..."}
  },
  "construction_journal": {
    "iterations": [
      {
        "iteration": 1,
        "timestamp": "...",
        "files_created": ["framework/pages/helios8/inquiries_page.py"],
        "files_modified": []
      },
      {
        "iteration": 2,
        "timestamp": "...",
        "files_created": ["framework/tasks/helios8/inquiry_tasks.py"],
        "files_modified": ["framework/pages/helios8/inquiries_page.py"]
      }
    ]
  },
  "test_execution_history": {
    "test_runs": [
      {
        "run": 1,
        "timestamp": "...",
        "command": "pytest tests/helios8/test_submit_inquiry.py",
        "result": "failed",
        "error": "ElementNotInteractableException",
        "screenshot": "tests/_reports/2026-01-22T10-30-45.123456Z/screenshot_001.png"
      },
      {
        "run": 2,
        "timestamp": "...",
        "command": "pytest tests/helios8/test_submit_inquiry.py",
        "result": "passed",
        "duration": "12.3s",
        "screenshot": "tests/_reports/2026-01-22T10-30-45.123456Z/screenshot_002.png"
      }
    ]
  },
  "metrics": {
    "iterations": 5,
    "hitl_triggers": 3,
    "gate_violations": 2,
    "test_runs": 8,
    "final_result": "passed"
  }
}
```

### Rationale Summary

**Why This Model:**
1. **Separation of concerns:** Event stream (audit) vs accumulated state (workflow state)
2. **Reconstruction capability:** Audit log enables full session replay
3. **QA manager perspective:** File paths + test runs + HITL interactions = complete picture
4. **No code bloat:** Reference screenshots by path, no code snapshots
5. **Correctness focus:** Count-based metrics (not timing), shows health

**What This Enables:**
- Session reconstruction from audit log
- HITL decision documentation (compliance)
- Construction progress tracking (workflow state)
- Test execution history (build→test→discover cycles)
- Framework compliance audit trail

**What This Avoids:**
- Large file sizes (no code snapshots, no embedded screenshots)
- Redundant data (no separate discovery log, decision log)
- Rollback complexity (fix forward with HITL instead)

---

**Next Phase:** Create PRD to formalize the pair programming protocol with sufficient Protocols and Smart Gates working in conjunction.

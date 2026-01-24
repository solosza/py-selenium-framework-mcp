Test Requirement:                                                                      As a customer, I want to search for a sales representative
                                                                                       
  URL:                                                                                 
  https://heliosdigital-retail-qa.azurewebsites.net

  What to Verify:
  1. AI asks for workflow identifier with the Option 3 explanation:
  "Workflow identifier? This creates folders at framework/pages/{workflow}/ and        
  tests/{workflow}/
   Use this to organize tests by: test run (helios7), feature (checkout-v2), sprint    
  (auth-sprint-2)
   Example: helios7"
  2. You provide: helios7
  3. Gate validates and returns PASS
  4. State saves to step_1 (not step_2)
------
● The Answer: Missing Tests
                                                                                      The gaps exist because tests for these protocol requirements don't exist. Let me
  show you:                                                                         
                                              
  GAP-03-01 (Step 3 retry tracking):                                                
  - Protocol says: "max 3 attempts"                                                   - Test file exists: test_qg_ai_processing.py                                      
  - Tests for retry tracking: 0 tests found                                           - Result: Gap not caught ❌                                
                                                                                    
  RETRY-01-01 (workflow directory scaffolding):
  - Protocol says: "creates folders at framework/pages/{workflow}/"
  - Test file exists: test_qg_user_input.py
  - Tests for directory scaffolding: 0 tests found
  - Result: Gap not caught ❌

  TDD Should Work Like This

  Protocol Requirement → Test Case → Implementation → Test Passes

  Example for GAP-03-01:

  # test_qg_ai_processing.py (MISSING TEST)
  def test_blocks_after_3_failed_attempts():
      """Protocol: 'If gate FAIL: AI retries processing (max 3 attempts)'"""        
      gate = QGAIProcessing()

      # Attempt 1 - FAIL
      result1 = gate.validate(invalid_data)
      assert result1["status"] == "fail"

      # Attempt 2 - FAIL
      result2 = gate.validate(invalid_data)
      assert result2["status"] == "fail"

      # Attempt 3 - FAIL
      result3 = gate.validate(invalid_data)
      assert result3["status"] == "fail"

      # Attempt 4 - BLOCKED
      result4 = gate.validate(invalid_data)
      assert result4["status"] == "blocked"  # ← This would FAIL now
      assert "max attempts" in result4["error"]

  If this test existed, it would FAIL, forcing us to implement retry tracking.      

  The Real Solution: Protocol-Driven Test Generation

  Instead of manually writing tests, we should generate tests from protocols:       

  step-03.md (Protocol)
    ↓
    Line 48-50: "max 3 attempts"
    ↓
    Auto-generate:
      test_qg_ai_processing::test_blocks_after_3_failed_attempts()
    ↓
    Run test → FAILS → Implement → PASSES

  Proposed Fix

  Should we:

  Option 1: Write missing tests FIRST (True TDD)
  1. For each gap, write the test that SHOULD exist
  2. Run tests → watch them FAIL
  3. Implement fixes → tests PASS
  4. Gaps are caught, can't regress

  Option 2: Fix gaps, THEN write tests (Current approach)
  1. Implement fixes based on audit
  2. Write tests to prevent regression
  3. Faster but less rigorous

  Option 3: Protocol-to-Test Generator (Long-term)
  1. Parse protocol markdown
  2. Extract requirements (e.g., "max 3 attempts")
  3. Generate test templates
  4. Human fills in test logic
  5. Guarantees protocol coverage

  Which approach do you want for these gaps?
------                                                                                    
  This is required for pair programming so you can see AI actions in real-time.
                                          
  Timeout monitoring configuration?
  1. Enabled (default 30s) - AI stops if element not found within threshold
  2. Custom threshold - Specify seconds (e.g., 60s for slow apps)                   
  3. Disabled - No timeout monitoring (use with caution)
----
● ✓ Step 1 Complete: User Input
                                                                                      Extracted Data:                                                                     - Persona: customer
  - Role: Customer                                                                  
  - Workflow: testmu
  - Environment: helios1
  - URL: https://heliosdigital-retail-qa.azurewebsites.net

  ---
  Ready to proceed to Step 2: Pre-flight Configuration.

  Should I continue?

❯ yes                        
user should be presented an option that  they can choose. 1 or 2,etc

-----
design whats saved to state
desgin whats saved to audit_log_

-----

    
  Post-Step Verification Checklist                                                  
                                                                                    
  After each step completes, verify:                                                
  1. State (Persistence)                                                               
  - tests/_state/{run_id}/workflow_state.json updated                               
  - Correct step number saved (step_1, step_2, etc.)
  - Step data contains expected fields
  - Status marked as complete

  2. Audit (Observability)

  - tests/_audit/audit_log_{run_id}.json created/updated
  - Entry logged with correct gate name
  - Timestamp recorded
  - Input/output captured

  3. Transcript (Human-Readable Log)

  - tests/_reports/{run_id}/workflow_transcript.md updated
  - Step name, extracted fields, gate result logged
  - Append mode (doesn't overwrite previous steps)
  - Human-readable format (not raw JSON)

  4. Gate Validation (Quality Control)

  - Gate returns expected status (pass, fail, or NEEDS_RETRY)
  - Validation logic enforces step requirements
  - Blocking behavior correct (cannot proceed if gate fails)

  5. Protocol Adherence (AI Behavior)

  - AI follows step-XX.md guidance (asks questions, extracts data)
  - User prompts match protocol templates
  - Error messages match protocol format

  6. Step Flow (Workflow Integrity)

  - Can proceed to next step if gate passes
  - Blocked from next step if gate fails
  - State accumulation works (later steps can access earlier step data)
---
● You're absolutely right - we're NOT done with design.

  What We HAVE Designed:                                                              - Data model (audit log, workflow state, reports structure)
  - 5 components implemented, 3 rejected                                            
  - JSON schemas for data files                                                     

  What We HAVEN'T Designed:

  1. Transcript (Human-Readable Log)
  - We mentioned tests/_reports/<run_id>/ for screenshots
  - But workflow_transcript.md isn't in our data model at all
  - Question: Is transcript separate from audit log? Or generated from it?
  - Question: What format? Markdown? Plain text?
  - Question: When is it written? Real-time or post-workflow?

  2. Gate Validation Mechanics
  - We said "gates validate" but not HOW
  - Question: Where does gate logic live? In gate files? Separate validator?        
  - Question: How does gate return status? (pass/fail/NEEDS_RETRY)
  - Question: What triggers gate execution? (before step? after step? both?)        
  - Question: How does blocking work? (throw exception? return signal?)

  3. Protocol Adherence
  - We said "protocols guide" but not how it's enforced
  - Question: Is this just documentation AI reads? Or is there code enforcement?    
  - Question: How do we validate AI followed the protocol?
  - Question: User prompt templates - where do they live?

  4. Step Flow Control
  - We said "5-step workflow" but not the mechanics
  - Question: How does step transition work? (state machine? simple counter?)       
  - Question: How is state accumulated? (StateManager.add_step()? merge dicts?)     
  - Question: Can you go backwards? Skip steps? Restart mid-workflow?

  5. Gate-State-Audit Integration
  - Question: What's the exact sequence? (gate validates → state saves → audit      
  logs?)
  - Question: If gate fails, what gets logged? (both failure + retry in audit?)     
  - Question: How do these 3 systems coordinate?

  6. HITL Integration
  - We designed HITL triggers in PRD but not the mechanics
  - Question: How does HITL interaction pause workflow?
  - Question: Where does user input get captured?
  - Question: How does workflow resume after HITL?

  My Assessment:
  We need to go back to design discussion and flesh out these 6 validation
  components. We have the WHAT (data model) but not the HOW (mechanics).

  Should we:
  1. Continue design discussion for these 6 components?
  2. Or do you want to start implementing and discover the design as we go?
  ---
  After you run the test, I'll verify:                                                1. Transcript writes (main fix)
  2. State structure (step_4 consolidation)                                         
  3. Audit trail (which system is used)                                             
  4. Gate enforcer (no blocks)
  
----
● Perfect! Now I see the full picture. Step 1 is in a separate state file.          
                                                                                      Summary of E2E Test Results:                                                                                                                                          
  ✅ FIXED (Task 1.1.4 goals):                                                        1. File Swap Working - step_2 is Pre-flight (not User Input)
  2. Audit Trail Structure - Clean array format with proper step numbers
  3. State Saved Per Step - All gates saving their data

  ❌ NEW ISSUES FOUND:

  1. State Fragmentation (CRITICAL):
    - Step 1 saved to: 2026-01-22T11-10-27.865198Z/workflow_state.json
    - Steps 2-5 saved to: 2026-01-22T11-11-06.892443Z/workflow_state.json
    - Problem: State is split across multiple files instead of accumulating in one  
  file
    - Expected: All steps (1-5) should be in ONE state file with same run_id        
  2. Step 5 Discovery Counter Bug:
    - pages_discovered: 0 but discovered_pages has BOTH pages
    - Counter not incrementing properly during multi-page discovery

  What We DIDN'T Test Yet:
  - Construction gates (Steps 6-9) saving to step_4 with metadata sub-keys
  - Gate enforcer allowing writes after step_4 complete
  - Transcript writes (main blocker from 1.1.3.4)

  Next Steps:
  We need to decide: fix the state fragmentation issue first, or continue testing   
  construction gates?
----
----
❯ we need to fix these steps now to do our designed process. we keep getting          confused. we need to cut everything else off now.\                               
  we scaffold our true process.\                                                    
  deprecate everything else.\                                                       
  if we need deprecated code. we reisntate it as needed.\                           
  we follow tdd as we build each step so we know what we are trying to              
  accomplish and what is working or not.\                                           
  this is getting way to confusing jumping from this step to this old step,         
  etc.\                                                                             
  do you have a better plan? if so let me know because this is not working          
                                                                                    ● You're absolutely right. We're stuck in confusion because we're trying to retrofit
   an old 11-step autonomous workflow into a new 5-step pair programming workflow.
  This is a mess.                                                                      
  Here's a better plan - Clean Break + TDD:                                         
  
  Phase 1: Archive Old Workflow (NOW - 30 min)

  Archive these:
  _archived/old_autonomous_workflow/
  ├── protocols/
  │   ├── step-01.md through step-11.md (OLD sequential steps)
  │   └── SKILL.md (OLD autonomous guidance)
  ├── gates/
  │   ├── qg_page_object.py (autonomous POM generation)
  │   ├── qg_task.py (autonomous Task generation)
  │   ├── qg_role.py (autonomous Role generation)
  │   ├── qg_test_runner.py (autonomous Test generation)
  │   ├── qg_save_run.py (Step 10 validation)
  │   ├── qg_execution.py (Step 11 execution)
  │   └── qg_workflow_complete.py (Step 11 meta-gate)
  └── tools/
      ├── generate_page_object.py (Tool 3)
      ├── generate_task.py (Tool 4)
      ├── generate_role.py (Tool 5)
      └── generate_test_runner.py (Tool 6)

  Keep only these (map to NEW workflow):
  Active (NEW pair programming workflow):
  ├── protocols/
  │   ├── step-01-user-input.md ✓ (maps to Step 1)
  │   ├── step-02-preflight.md ✓ (maps to Step 2)
  │   ├── step-03-ai-processing.md ✓ (maps to Step 3)
  │   ├── step-04-collaborative-construction.md (NEW - create with TDD)
  │   └── step-05-done.md (NEW - create with TDD)
  ├── gates/
  │   ├── qg_user_input.py ✓ (Step 1)
  │   ├── qg_preflight.py ✓ (Step 2)
  │   ├── qg_ai_processing.py ✓ (Step 3)
  │   ├── qg_test_scenarios.py ✓ (Step 4 - BDD validation)
  │   └── qg_discovered_elements.py ✓ (Step 4 - element validation)
  └── tools/
      ├── generate_tests_from_user_story.py ✓ (Tool 1)
      └── discover_page_elements.py ✓ (Tool 2)

  Phase 2: Build NEW Step 4 with TDD (NEXT - iterative)

  Step 4 is NOT autonomous generation. It's HITL collaboration.

  TDD Cycle for Step 4:

  1. Write acceptance test first:
  def test_step4_collaborative_construction():
      """
      GIVEN user requirement parsed (Steps 1-3 complete)
      WHEN AI builds POM incrementally with HITL guidance
      THEN POM saved, validated, test runs, passes
      """
      # Arrange: Steps 1-3 state exists
      # Act: AI builds CustomerSearchPage with Edit tool
      # Assert: File saved, framework-compliant, test passes

  2. Write failing unit test:
  def test_hitl_triggers_on_dd27_violation():
      """Gate catches locator in Task, triggers HITL with fix data"""
      # Fails because qg_framework_compliance doesn't exist yet

  3. Implement minimum code:
    - Create qg_framework_compliance.py (NEW gate)
    - Detects DD-27 violations
    - Returns fix data for HITL
  4. Refactor: Extract validation logic
  5. Document: Update step-04-collaborative-construction.md

  Phase 3: Repeat for Step 5

  Step 5 = Test execution + HITL triage (if fails)

  ---
  Key principle: Stop trying to map old construction gates (qg_page_object, qg_task,
   etc.) to new workflow. They were designed for AUTONOMOUS generation. New workflow
   is COLLABORATIVE construction.

  Question for you:

  Do you want me to:
  1. Archive old workflow NOW (move files, update imports, commit)
  2. Then start TDD for Step 4 (write acceptance test → failing unit test →         
  implement)

  Or do you have a different approach in mind?
 ---
 ---
 ● I'll analyze our design against execution_patterns.md to identify what we need
  first and what gaps exist.                                                        
                                                                                    ● Read(docs\projects\pair-programming\1-design-discussion.md)                       
  ⎿  Read 100 lines                                                                 
                                                                                    
● Let me create a comprehensive gap analysis comparing our design to
  execution_patterns.md requirements.                                               
                                                                                      WHAT WE NEED FIRST (Universal Components - REQUIRED)                              
                                                                                      ✅ Layer 1: Protocols (REQUIRED)       

  What execution_patterns.md Says:
  - Form: YAML files, markdown documents, skill references
  - Purpose: Teach AI correct behavior BEFORE execution

  What We Have:
  - .claude/skills/qa-management-layer/references/step-04.md (Tool 1)
  - .claude/skills/qa-management-layer/references/step-05.md (Tool 2)

  GAP:
  - ❌ NO Step 4 protocol for collaborative construction
  - ❌ NO Step 5 protocol for done/execution
  - ❌ Step protocols don't follow execution_patterns.md format:
    - Missing: required_inputs, actions, outputs
    - Missing: YAML structure option

  ✅ Layer 2: Smart Gates (REQUIRED)

  What execution_patterns.md Says:
  - Two Functions: 1. Validate, 2. Teach (provide fix data)
  - Return Structure: {"status": "PASS/FAIL/NEEDS_CONFIRMATION", "teach": "...",    
  "fix": "...", "example": "..."}

  What We Have:
  - Gate files exist: qg_user_input, qg_preflight, qg_ai_processing,
  qg_test_scenarios, qg_discovered_elements
  - PRD FR-2.1: "Smart Gates SHALL validate AND teach"

  GAP:
  - ❌ NO gate return structure defined (we say pass/fail, execution_patterns.md    
  shows NEEDS_CONFIRMATION)
  - ❌ NO teaching mechanism designed (execution_patterns.md shows: teach, fix,     
  example, queries)
  - ❌ NO gate integration with HITL designed (how does NEEDS_CONFIRMATION trigger  
  HITL?)

  ✅ Layer 4: State Checkpointing (REQUIRED)

  What execution_patterns.md Says:
  - Structure: {"checkpoint_id": "...", "timestamp": "...", "workflow": "...",      
  "gate_passed": "...", "state": {...}, "next_step": "...", "audit_trail": [...]}   
  - Purpose: Resume from last checkpoint

  What We Have:
  - tests/_state/<run_id>/workflow_state.json with steps accumulation

  GAP:
  - ❌ NO checkpoint structure (we have workflow_state but not checkpoint_id,       
  gate_passed, next_step)
  - ❌ NO resume mechanism designed (how does workflow resume from checkpoint?)     
  - ❌ State structure doesn't match execution_patterns.md format

  ---
  GAPS IN OUR DESIGN (Missing Details)

  1. Gate Return Status Types (CRITICAL GAP)

  execution_patterns.md:
  return {
      "status": "PASS" | "FAIL" | "NEEDS_CONFIRMATION",
      "teach": "...",
      "fix": "...",
      "example": "..."
  }

  Our Design:
  {"result": "pass/fail", "violations": [...], "fix_data": {...}}

  Missing:
  - NEEDS_CONFIRMATION status (for HITL triggers)
  - Standardized teaching structure (teach, fix, example, queries)

  2. Transcript (Human-Readable Log) (NEW REQUIREMENT)

  User mentioned: tests/_reports/{run_id}/workflow_transcript.md

  execution_patterns.md: Doesn't mention (might be QA-specific)

  Our Design: ❌ NOT INCLUDED AT ALL                                                

  Questions:
  - Is transcript separate from audit log? Or generated from it?
  - What format? Markdown? Plain text?
  - When is it written? Real-time or post-workflow?
  - What goes in it? (step names, extracted fields, gate results - user specified)  

  3. Hook Structure (MISSING DESIGN)

  execution_patterns.md:
  - Form: JavaScript hooks in .claude/hooks/
  - Types: PreToolUse, PostToolUse, PreSave, PostAgentEnd
  - Interventions: Alert, Block, Auto-Fix

  Our Design:
  - Mentioned: "Hooks monitor timeout/rambling"
  - Missing: Hook file structure, intervention types, how hooks coordinate with     
  gates

  Questions:
  - What hooks do we need? (PostToolUse for timeout? PreSave for validation?)       
  - Where do hooks live? (.claude/hooks/qa-gate-enforcer.py exists but needs update)
  - How do hooks trigger HITL? (return {alert: true} vs throw exception?)

  4. HITL Confirmation Structure (MISSING)

  execution_patterns.md:
  {
    "confirmation_type": "config_change",
    "context": {"file": "...", "action": "...", "proposed_change": {...}},
    "options": [
      {"id": "approve", "label": "Yes, proceed"},
      {"id": "modify", "label": "Let me change it"},
      {"id": "reject", "label": "Cancel"}
    ]
  }

  Our Design:
  - Mentioned: "HITL triggers at blockers"
  - Missing: Confirmation structure, options format, how AI presents choices        

  Questions:
  - How does gate signal NEEDS_CONFIRMATION? (return status? throw signal?)
  - Where does HITL prompt user? (via AskUserQuestion tool? separate system?)       
  - How does workflow pause? (wait for user response? save state?)

  5. Step Flow Control (ASSEMBLY LINE PATTERN)

  execution_patterns.md:
  - Pattern: Assembly Line (Sequential Pipeline)
  - Enforcement: Metadata contract (Step N+1 needs Step N output)
  - Flow: Step 1 → Gate validates → Checkpoint saved → Step 2 → ...

  Our Design:
  - Mentioned: "5-step workflow"
  - Missing: How steps transition, how metadata flows, how blocking works

  Questions:
  - How does Step 4 know Step 3 is complete? (check workflow_state.json?)
  - Can you skip steps? (NO - metadata contract prevents it)
  - How does gate block next step? (throw exception? return signal?)

  6. Audit Log Format Mismatch (NEEDS ALIGNMENT)

  execution_patterns.md:
  {
    "timestamp": "...",
    "workflow_id": "...",
    "type": "mcp_tool",
    "tool_name": "qg_coverage",
    "args": {...},
    "result": {...},
    "gate_status": "PASS"
  }

  Our Design:
  {
    "type": "gate_validation",
    "timestamp": "...",
    "gate": "qg_user_input",
    "result": "pass"
  }

  Differences:
  - execution_patterns.md: includes workflow_id at event level
  - execution_patterns.md: gate_status field (not result)
  - Our design: separate tool_call vs gate_validation events

  ---
  SUMMARY: WHAT NEEDS DESIGN FIRST

  Critical (Blocks Implementation)

  1. Gate Return Structure - Need PASS/FAIL/NEEDS_CONFIRMATION + teaching format    
  2. HITL Confirmation Structure - How gates trigger HITL, how user responds        
  3. Checkpoint Structure - checkpoint_id, gate_passed, next_step (enable resume)   
  4. Step Flow Control - How steps transition, how metadata flows, how blocking     
  works

  High Priority (User Mentioned)

  5. Transcript Format - tests/_reports/{run_id}/workflow_transcript.md structure   
  6. Hook Structure - What hooks, where they live, intervention types

  Medium Priority (Can Infer)

  7. Audit Log Alignment - Match execution_patterns.md format

  ---
  RECOMMENDATION

  Before implementing code, we need to design:

  Session 1: Gate + HITL Integration (Most Critical)
  - Gate return structure (PASS/FAIL/NEEDS_CONFIRMATION)
  - Gate teaching mechanism (teach, fix, example, queries)
  - HITL confirmation structure (how gate signals, how AI prompts, how user
  responds)
  - How workflow pauses/resumes after HITL

  Session 2: Step Flow + Checkpointing
  - Step transition mechanism (metadata contract)
  - Checkpoint structure (checkpoint_id, gate_passed, next_step, audit_trail)       
  - Resume mechanism (load checkpoint → continue from next_step)

  Session 3: Hooks + Transcript
  - Hook file structure (.claude/hooks/)
  - Intervention types (Alert, Block, Auto-Fix)
  - Transcript format (human-readable, append mode)

  Should we start with Session 1 (Gate + HITL Integration)?
  
  ❯ im thinking mybe we create a validator specificly for each step? or just one  
  fits all. im asking this because now there's a lot of things to cover.        
                                       
● Excellent question. You're right - cramming everything into one validator will
  create a monster.                                                                                                                                                    
  Three Options                                                                     
                                                                                      Option 1: Monolithic (Current)
                                                                                    
  validate_step.py (1400 lines → 2500+ lines)
  - All checks for all steps in one file
  Problem: Too large, hard to maintain, slow to run

  Option 2: Separate Per Step

  validators/
    validate_step1.py
    validate_step2.py
    validate_step3.py
    validate_step4.py
    validate_step5.py
  Problem: Code duplication (infrastructure checks repeated in each)

  Option 3: Hybrid (Recommended)

  validators/
    base_validator.py              ← 14 universal checks (infrastructure)
    protocol_validators/
      step1_protocol.py            ← Step 1 protocol only (~150 lines)
      step2_protocol.py            ← Step 2 protocol only (~150 lines)
      step3_protocol.py            ← Step 3 protocol only (~150 lines)
      step4_protocol.py            ← Step 4 protocol only (~150 lines)
      step5_protocol.py            ← Step 5 protocol only (~150 lines)

  validate_step.py                 ← Main entry (orchestrates)

  My Recommendation: Hybrid Architecture

  Why:
  1. Separation of concerns - Infrastructure vs Protocol
  2. Maintainability - Each protocol validator is small (~150 lines)
  3. Flexibility - Can run universal OR protocol checks separately
  4. Scalability - Add Step 6 later without touching existing code
  5. No duplication - Infrastructure checks shared

  Usage:
  # Run EVERYTHING (universal + protocol) for Step 3
  python validate_step.py --step 3

  # Run ONLY infrastructure checks (fast)
  python validate_step.py --step 3 --universal-only

  # Run ONLY Step 3 protocol checks
  python validate_step.py --step 3 --protocol-only

  Structure:
  - base_validator.py - 14 existing checks (state, audit, hooks, etc.)
  - step1_protocol.py - Step 1 requirements (persona, URL, workflow dirs, etc.)     
  - step2_protocol.py - Step 2 requirements (credential_strategy, browser_config,   
  etc.)
  - step3_protocol.py - Step 3 requirements (BDD, expected_states, retry limit)     
  - step4_protocol.py - Step 4 requirements (test_scenarios, skeleton code check)   
  - step5_protocol.py - Step 5 requirements (elements, two-pass, DD-33)

  Each protocol validator focuses on one step's protocol requirements only.

  Should I implement this hybrid architecture?

❯ why just protocols what happened to the otherlayers? 
                                         
● You're absolutely right - I focused on protocols but ignored the other 5 layers.
  Let me fix that.
                                                                                      Complete Architecture (All 6 Layers)    
                                                                                      validators/
    base_validator.py                    ← Core infrastructure (file exists, JSON   
  valid)

    layer_validators/
      protocol_validator.py              ← Layer 1: Protocol requirements
      gate_validator.py                  ← Layer 2: Gate logic + NEEDS_RETRY +      
  blocking
      hook_validator.py                  ← Layer 3: Hook data completeness
      state_validator.py                 ← Layer 4: Field validation per step       
      audit_validator.py                 ← Layer 5: Metadata completeness
      hitl_validator.py                  ← Layer 6: Blocking behavior + user choices

  validate_step.py                       ← Main orchestrator

  What Each Layer Validator Checks

  Layer 1: protocol_validator.py

  Per-step protocol requirements:
  - Step 1: persona, URL, role_name matches persona, workflow dirs exist
  - Step 2: credential_strategy valid, browser_config.headless=false, test data     
  infra
  - Step 3: BDD structure, expected_states, intent, retry limit ≤3
  - Step 4: test_scenarios complete, no skeleton code
  - Step 5: elements complete, two-pass discovery, DD-33 decision

  Layer 2: gate_validator.py

  Gate validation logic (works for ALL steps):
  - Gate rejects invalid data (test with bad input)
  - Gate provides fix_hint when status=fail
  - NEEDS_RETRY returns scaffolding template
  - Max attempts enforced (blocked after 3 failures)
  - Cannot proceed when blocked

  Layer 3: hook_validator.py

  Hook data correctness (works for ALL steps):
  - Audit entry has all required fields (type, gate, step, result, timestamp, input,
   output, metadata)
  - Input/output captured correctly
  - Metadata complete for this step
  - Hook read from correct state location

  Layer 4: state_validator.py

  Field validation (extends base checks):
  - Step N state has correct schema
  - Field values valid (not just present)
  - State accumulation works (Step N can read Steps 1..N-1)

  Layer 5: audit_validator.py

  Metadata completeness (extends base checks):
  - Audit entry complete (no missing fields)
  - Input/output captured
  - Metadata matches step requirements

  Layer 6: hitl_validator.py

  Blocking behavior (works for ALL steps):
  - Blocked response after max attempts
  - Error messages clear and actionable
  - Fix hints provided
  - User presented with options (not just error)

  Usage

  # Run EVERYTHING (all 6 layers) for Step 3
  python validate_step.py --step 3

  # Run specific layer only
  python validate_step.py --step 3 --layer protocol
  python validate_step.py --step 3 --layer gate
  python validate_step.py --step 3 --layer hooks

  # Run multiple layers
  python validate_step.py --step 3 --layers protocol,gate,state

  Summary Table
  Layer: 1. Protocols
  Validator: protocol_validator.py
  Step-Specific?: ✓ Yes (5 step modules)
  Checks: Protocol requirements per step
  ────────────────────────────────────────
  Layer: 2. Gates
  Validator: gate_validator.py
  Step-Specific?: ✗ No (universal)
  Checks: Validation logic + NEEDS_RETRY + blocking
  ────────────────────────────────────────
  Layer: 3. Hooks
  Validator: hook_validator.py
  Step-Specific?: ✗ No (universal)
  Checks: Audit data completeness
  ────────────────────────────────────────
  Layer: 4. State
  Validator: state_validator.py
  Step-Specific?: ✓ Yes (field schemas)
  Checks: Field validation per step
  ────────────────────────────────────────
  Layer: 5. Audit
  Validator: audit_validator.py
  Step-Specific?: ✓ Yes (metadata schemas)
  Checks: Metadata completeness per step
  ────────────────────────────────────────
  Layer: 6. HITL
  Validator: hitl_validator.py
  Step-Specific?: ✗ No (universal)
  Checks: Blocking behavior
  This covers ALL 6 layers of defense-in-depth.

  Should I implement this complete architecture?
 
----
----
 
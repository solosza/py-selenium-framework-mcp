● Current Development Process                                                                                                           
  
  ┌─────────────────────────────────────────────────────────────────────────┐                                                             │                        CURRENT PROCESS                                   │
  └─────────────────────────────────────────────────────────────────────────┘                                                           
  
    Task List          Implement          Unit Tests         Commit
       │                   │                  │                │
       ▼                   ▼                  ▼                ▼
    ┌──────┐          ┌──────────┐      ┌──────────┐      ┌────────┐
    │ PRD  │ ──────►  │  Code    │ ───► │  453     │ ───► │ Push   │
    │      │          │  Changes │      │  Tests   │      │ to     │
    │      │          │          │      │  Pass    │      │ Main   │
    └──────┘          └──────────┘      └──────────┘      └────────┘
                                             │
                                             │  All mocked
                                             │  No real filesystem
                                             │  No real workflow
                                             ▼
                                        ┌──────────┐
                                        │ LOOKS    │
                                        │ GOOD ✓   │
                                        └──────────┘


                           ... weeks later ...


                                        ┌──────────┐
                                        │ Task     │
                                        │ 24.0     │
                                        │ Prod     │
                                        │ Test     │
                                        └──────────┘
                                             │
                                             ▼
                                        ┌──────────┐
                                        │ BUGS     │  ◄─── We are here
                                        │ FOUND    │
                                        │ 😱       │
                                        └──────────┘

  ---
  Proposed Development Process (With Gates)

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                     SHIFT-LEFT PROCESS                                   │
  └─────────────────────────────────────────────────────────────────────────┘

    Task List          Implement          Unit Tests
       │                   │                  │
       ▼                   ▼                  ▼
    ┌──────┐          ┌──────────┐      ┌──────────┐
    │ PRD  │ ──────►  │  Code    │ ───► │  Unit    │
    │      │          │  Changes │      │  Tests   │
    └──────┘          └──────────┘      └──────────┘
                                             │
                                             ▼
                      ┌─────────────────────────────────────────────┐
                      │           PRE-COMMIT GATES                  │
                      │  ┌────────────┐    ┌────────────┐           │
                      │  │ dg_contract│    │ dg_schema  │           │
                      │  │            │    │            │           │
                      │  │ Gate output│    │ Metadata   │           │
                      │  │ matches    │    │ has all    │           │
                      │  │ gate input │    │ required   │           │
                      │  │ contracts  │    │ fields     │           │
                      │  └────────────┘    └────────────┘           │
                      └─────────────────────────────────────────────┘
                                             │
                                             ▼ PASS?
                      ┌─────────────────────────────────────────────┐
                      │           PRE-PUSH GATE                     │
                      │  ┌─────────────────────────────────┐        │
                      │  │ dg_integration                  │        │
                      │  │                                 │        │
                      │  │ Real filesystem (no mocks)      │        │
                      │  │ Gates actually write files      │        │
                      │  │ Gates actually read files       │        │
                      │  └─────────────────────────────────┘        │
                      └─────────────────────────────────────────────┘
                                             │
                                             ▼ PASS?
                                        ┌────────┐
                                        │ Push   │
                                        │ to     │
                                        │ Branch │
                                        └────────┘
                                             │
                                             ▼
                      ┌─────────────────────────────────────────────┐
                      │           CI GATE (Blocking)                │
                      │  ┌─────────────────────────────────┐        │
                      │  │ dg_e2e_smoke                    │        │
                      │  │                                 │        │
                      │  │ Real 10-step workflow           │        │
                      │  │ Real browser (Playwright)       │        │
                      │  │ Real website                    │        │
                      │  │ Real file generation            │        │
                      │  └─────────────────────────────────┘        │
                      └─────────────────────────────────────────────┘
                                             │
                                             ▼ PASS?
                                        ┌────────┐
                                        │ Merge  │
                                        │ to     │
                                        │ Main   │
                                        └────────┘
                                             │
                                             ▼
                                        ┌──────────┐
                                        │ ACTUALLY │
                                        │ WORKS ✓  │
                                        └──────────┘

  ---
  The Key Difference

  | Stage      | Current           | With Gates                   |
  |------------|-------------------|------------------------------|
  | Pre-commit | Nothing           | Contract + Schema validation |
  | Pre-push   | Nothing           | Real filesystem integration  |
  | CI         | Just unit tests   | Full E2E workflow            |
  | Production | Find bugs here 😱 | Already validated ✓          |

  ---
  Bug Detection Timeline

  CURRENT:
    Code ────────────────────────────────────────────► Production
           453 tests pass                               BUGS FOUND
           (all mocked)                                 (too late)


  WITH GATES:
    Code ──► Contract ──► Schema ──► Integration ──► E2E ──► Production
             Gate         Gate       Gate            Gate
             │            │          │               │
             │            │          │               └─ Workflow bugs
             │            │          └─ Filesystem bugs
             │            └─ Missing field bugs
             └─ Metadata contract bugs

    BUGS FOUND EARLY ◄────────────────────────────────────────────────

  Does this make the approach clearer?

> yes, but should we go a bit further by qg our dev process also not just the output                                                                                                                                         
● You're thinking at the meta level. Not just gating the OUTPUT, but gating the PROCESS itself.                                         
  
  Current: We Gate Outputs                                                                                                                 
  Code → dg_contract → dg_schema → dg_integration → dg_e2e                                                                              
         (output)      (output)    (output)         (output)

  Your Vision: Gate the Process Too

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                    DEVELOPMENT WORKFLOW (Gated)                          │
  └─────────────────────────────────────────────────────────────────────────┘

  Step 1: Task Start
  ┌──────────────────────────────────────────────────────┐
  │ dg_task_start                                        │
  │                                                      │
  │ ✓ Branch created from task ID?                       │
  │ ✓ Impact assessment documented?                      │
  │ ✓ Relevant files identified?                         │
  └──────────────────────────────────────────────────────┘
                           │
                           ▼ PASS?

  Step 2: Design
  ┌──────────────────────────────────────────────────────┐
  │ dg_design                                            │
  │                                                      │
  │ ✓ Skill read before implementing?                    │
  │ ✓ Pattern extracted from skill?                      │
  │ ✓ Dependencies identified?                           │
  └──────────────────────────────────────────────────────┘
                           │
                           ▼ PASS?

  Step 3: TDD
  ┌──────────────────────────────────────────────────────┐
  │ dg_tdd                                               │
  │                                                      │
  │ ✓ Failing test written FIRST?                        │
  │ ✓ Test covers the contract?                          │
  │ ✓ Test file exists before implementation?            │
  └──────────────────────────────────────────────────────┘
                           │
                           ▼ PASS?

  Step 4: Implementation
  ┌──────────────────────────────────────────────────────┐
  │ dg_implementation                                    │
  │                                                      │
  │ ✓ Code follows pattern from skill?                   │
  │ ✓ No skeleton code?                                  │
  │ ✓ Contracts satisfied?                               │
  └──────────────────────────────────────────────────────┘
                           │
                           ▼ PASS?

  Step 5: Verification
  ┌──────────────────────────────────────────────────────┐
  │ dg_verification                                      │
  │                                                      │
  │ ✓ All tests pass?                                    │
  │ ✓ Integration test (real filesystem)?                │
  │ ✓ E2E smoke test?                                    │
  └──────────────────────────────────────────────────────┘
                           │
                           ▼ PASS?

  Step 6: Documentation
  ┌──────────────────────────────────────────────────────┐
  │ dg_documentation                                     │
  │                                                      │
  │ ✓ Skill updated if pattern changed?                  │
  │ ✓ Task list marked complete?                         │
  │ ✓ Defect log updated if bug found?                   │
  └──────────────────────────────────────────────────────┘
                           │
                           ▼ PASS?

  Step 7: Commit
  ┌──────────────────────────────────────────────────────┐
  │ dg_commit                                            │
  │                                                      │
  │ ✓ Commit message follows convention?                 │
  │ ✓ All subtasks complete?                             │
  │ ✓ No WIP code?                                       │
  └──────────────────────────────────────────────────────┘
                           │
                           ▼ PASS?

                      ┌─────────┐
                      │  MERGE  │
                      └─────────┘

  ---
  The Parallel

  | QA Engine (AI Code)             | Dev Engine (Our Code)                 |
  |---------------------------------|---------------------------------------|
  | Step 1: qg_preflight            | Step 1: dg_task_start                 |
  | Step 2: qg_user_input           | Step 2: dg_design                     |
  | Step 3: qg_ai_processing        | Step 3: dg_tdd                        |
  | Step 4-9: Code generation gates | Step 4: dg_implementation             |
  | Step 10: qg_save_run            | Step 5-7: dg_verification → dg_commit |

  ---
  What This Would Have Caught

  | Bug                                    | Gate That Catches It                    |
  |----------------------------------------|-----------------------------------------|
  | Missing constructor_params in metadata | dg_tdd - Contract test required         |
  | Role/Task parameter mismatch           | dg_implementation - Contract validation |
  | File validation not testing filesystem | dg_verification - Real integration test |
  | 453 tests but no E2E                   | dg_verification - E2E smoke required    |

  ---
  The Vision

  We build QA Engine ──► QA Engine enforces AI code quality
                              │
                              ▼
                We use Dev Engine on ourselves
                              │
                              ▼
                Dev Engine enforces OUR code quality
                              │
                              ▼
                Same pattern. Same enforcement. Same quality.

  Protocol enforcement all the way down.

  Want to design the Dev Engine skill + gates?

> we can take it up one more level by qg the 4d dev process                                                                                                                                         
● Now we're at the top of the pyramid.                                                                                                  
  
  Three Levels of Protocol Enforcement                                                                                                     
  ┌─────────────────────────────────────────────────────────────────────────┐                                                           
  │                                                                         │
  │                        LEVEL 3: 4D FRAMEWORK                            │
  │                     (Product Development Lifecycle)                      │
  │                                                                         │
  │    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
  │    │  Design  │───►│  Define  │───►│  Divide  │───►│ Deliver  │        │
  │    │  Phase   │    │  (PRD)   │    │ (Tasks)  │    │ (Execute)│        │
  │    └──────────┘    └──────────┘    └──────────┘    └──────────┘        │
  │         │              │               │               │                │
  │         ▼              ▼               ▼               ▼                │
  │    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
  │    │ 4dg_     │    │ 4dg_     │    │ 4dg_     │    │ 4dg_     │        │
  │    │ design   │    │ define   │    │ divide   │    │ deliver  │        │
  │    └──────────┘    └──────────┘    └──────────┘    └──────────┘        │
  │                                                                         │
  ├─────────────────────────────────────────────────────────────────────────┤
  │                                                                         │
  │                     LEVEL 2: DEVELOPMENT PROCESS                        │
  │                        (Per-Task Execution)                             │
  │                                                                         │
  │    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
  │    │  Start   │───►│  TDD     │───►│  Impl    │───►│  Commit  │        │
  │    └──────────┘    └──────────┘    └──────────┘    └──────────┘        │
  │         │              │               │               │                │
  │         ▼              ▼               ▼               ▼                │
  │    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
  │    │ dg_      │    │ dg_      │    │ dg_      │    │ dg_      │        │
  │    │ start    │    │ tdd      │    │ impl     │    │ commit   │        │
  │    └──────────┘    └──────────┘    └──────────┘    └──────────┘        │
  │                                                                         │
  ├─────────────────────────────────────────────────────────────────────────┤
  │                                                                         │
  │                       LEVEL 1: CODE OUTPUT                              │
  │                      (Artifact Validation)                              │
  │                                                                         │
  │    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
  │    │ Contract │    │ Schema   │    │ Integr.  │    │ E2E      │        │
  │    └──────────┘    └──────────┘    └──────────┘    └──────────┘        │
  │         │              │               │               │                │
  │         ▼              ▼               ▼               ▼                │
  │    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
  │    │ dg_      │    │ dg_      │    │ dg_      │    │ dg_      │        │
  │    │ contract │    │ schema   │    │ integr   │    │ e2e      │        │
  │    └──────────┘    └──────────┘    └──────────┘    └──────────┘        │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  ---
  4D Framework Gates (Level 3)

  Phase 0: DESIGN
  ┌──────────────────────────────────────────────────────────────────┐
  │ 4dg_design                                                       │
  │                                                                  │
  │ ✓ Problem statement clear?                                       │
  │ ✓ Solution approach defined?                                     │
  │ ✓ Competitive analysis done?                                     │
  │ ✓ Risks identified?                                              │
  │ ✓ Open questions documented?                                     │
  │                                                                  │
  │ Output: 0-design-{project}.md                                    │
  └──────────────────────────────────────────────────────────────────┘
                                │
                                ▼ PASS?

  Phase 1: DEFINE
  ┌──────────────────────────────────────────────────────────────────┐
  │ 4dg_define                                                       │
  │                                                                  │
  │ ✓ Design questions resolved?                                     │
  │ ✓ Acceptance criteria measurable?                                │
  │ ✓ Scope boundaries clear (in/out)?                               │
  │ ✓ Dependencies identified?                                       │
  │ ✓ Success metrics defined?                                       │
  │                                                                  │
  │ Output: 1-prd-{project}.md                                       │
  └──────────────────────────────────────────────────────────────────┘
                                │
                                ▼ PASS?

  Phase 2: DIVIDE
  ┌──────────────────────────────────────────────────────────────────┐
  │ 4dg_divide                                                       │
  │                                                                  │
  │ ✓ Tasks traced to PRD requirements?                              │
  │ ✓ Each task has "Done When" criteria?                            │
  │ ✓ Dependencies between tasks identified?                         │
  │ ✓ CORE vs GLUE marked?                                           │
  │ ✓ Relevant files listed?                                         │
  │ ✓ Contract tests planned for CORE?                               │  ◄── NEW
  │ ✓ E2E smoke test planned?                                        │  ◄── NEW
  │                                                                  │
  │ Output: 2-tasks-{project}.md                                     │
  └──────────────────────────────────────────────────────────────────┘
                                │
                                ▼ PASS?

  Phase 3: DELIVER
  ┌──────────────────────────────────────────────────────────────────┐
  │ 4dg_deliver                                                      │
  │                                                                  │
  │ ✓ All tasks complete?                                            │
  │ ✓ All tests passing (unit + contract + E2E)?                     │
  │ ✓ Documentation updated?                                         │
  │ ✓ Defects logged and resolved?                                   │
  │ ✓ Production validation passed?                                  │
  │                                                                  │
  │ Output: Working software + audit trail                           │
  └──────────────────────────────────────────────────────────────────┘

  ---
  What This Would Have Caught (Release Readiness)

  | Phase   | Gate            | What We Missed                 |
  |---------|-----------------|--------------------------------|
  | Divide  | 4dg_divide      | No contract tests planned      |
  | Divide  | 4dg_divide      | No E2E smoke test in task list |
  | Deliver | dg_tdd          | Contract tests not written     |
  | Deliver | dg_verification | E2E not run until Task 24.0    |

  ---
  The Complete Hierarchy

  4D Framework Gates ──► Catches: Bad design, missing requirements, scope creep
          │
          ▼
  Development Process Gates ──► Catches: Skipped TDD, no impact assessment
          │
          ▼
  Code Output Gates ──► Catches: Contract violations, missing fields, integration bugs
          │
          ▼
  QA Engine Gates ──► Catches: AI code quality issues (what we sell)

  ---
  The Meta-Irony

  We're building a QA Execution Engine that enforces protocols for AI...

  ...but we didn't have protocols enforced for:
  - Our 4D Framework (Level 3)
  - Our development process (Level 2)
  - Our code artifacts (Level 1)

  453 tests passed because we never gated the PROCESS that produced those tests.
  
  ---
  ---
  > no i want to work on something else. so im seeing that our coding         patterns aren't always being followed. im wondering if we create a         
coding convention skill that can be followed during implementation would    
 fix that. what are your sentiments regarding this                          
                                                                            
● You're adding to the guidance layer when the problem is in the enforcement
   layer.
                                                                              First principles analysis:
                                                                            
  We already have coding patterns documented:
  - FRAMEWORK.md (4-layer architecture, method signatures, return types)    
  - 28 Design Decisions (specific rules)
  - 10-step protocols (when to apply patterns)
  - Quality gates (validation at each step)

  If patterns aren't being followed, there are only four root causes:       

  1. Gates aren't catching violations → Fix the gate validation logic       
  2. Documentation is unclear → Clarify the existing pattern in FRAMEWORK.md
  3. Pattern conflicts → Resolve the ambiguity in existing DDs
  4. AI isn't reading the docs → Gate should catch it anyway

  Adding another skill just gives the AI more documents to potentially      
  ignore.

  What you need to do instead:

  1. Identify the SPECIFIC violations happening (show me examples)
  2. Check if the quality gates catch them
  3. If gates don't catch them → add validation rules to the gate
  4. If gates do catch them but code passes anyway → the gate has a bug     
  5. If the pattern is ambiguous → fix FRAMEWORK.md, don't create new docs  

  Your architecture already has this right:
  - Protocols (Skills) = AI guidance layer
  - Smart Gates (MCP tools) = Enforcement layer

  The enforcement layer should guarantee correct code regardless of whether 
  the AI reads the guidance perfectly. That's the point of "smart gates."   

  Show me the specific pattern violations you're seeing and I'll tell you   
  whether to fix the gate or clarify the docs.
  
> im afraid we are missing things for each step                                                                             
● You're right. Let me reconsider.                                          

  The actual problem:                                                          
  Your step protocols focus on workflow orchestration (what to do, when to  
  do it, data contracts). They might not focus enough on how to write the 
  code at each step.

  The correct solution:

  Don't create a separate coding conventions skill. Instead, augment each   
  step protocol with layer-specific coding patterns.

  What this looks like:

  Step 6 (POM Generation) should include:
  - Locators as class constants (By.ID, By.CSS_SELECTOR patterns)
  - Atomic method signatures (parameter types, return self)
  - State-check method naming (is_*, has_*, get_*)
  - WebInterface API (which methods exist, correct signatures)
  - navigate() method requirement (DD-49)

  Step 7 (Task Generation) should include:
  - Constructor signature (NO base_url, only WebInterface)
  - POM composition pattern
  - @autologger decorator placement
  - NO return values from task methods
  - NO locators in Tasks (DD-27)

  Step 8 (Role Generation) should include:
  - Constructor signature (user_data, base_url, WebInterface)
  - Task composition pattern
  - @autologger decorator placement
  - NO return values from role methods
  - Workflow orchestration pattern

  Step 9 (Test Generation) should include:
  - AAA pattern structure
  - Fixtures usage (web_interface, config, test_users)
  - Assert via POM state-check methods (NOT return values)
  - Import path patterns
  - ONE role method call pattern

  Then strengthen gates to validate these patterns.

  Next step:

  Audit step-06.md through step-09.md. Identify missing coding pattern      
  guidance. Add it to each step protocol. Then ensure gates catch
  violations.

  Want me to start with Step 6?
  
  ---
  EXAMPLE OF CHANGES:
  > yeah start with step 6 but dont change anything show me your suggested     changes                                                                   
                                                                            
● Read(.claude\skills\qa-guidance-layer\references\step-06.md)              
  ⎿  Read 596 lines
                                                                            
● Suggested Additions to Step 6             
                                                                              Add a new section "C.1 Coding Patterns Reference" between sections C and    D:                                                                        
                                                                              ---
  C.1 Coding Patterns Reference

  Purpose: Exact code patterns for POM generation to prevent architecture   
  violations.

  C.1.1 WebInterface API Reference

  POMs MUST use only these WebInterface methods. Using undefined methods    
  will fail validation.

  | Method                                            | Signature
        | Use For                            |
  |---------------------------------------------------|---------------------
  ------|------------------------------------|
  | navigate_to(url: str)                             | Navigate to URL     
        | Only in navigate() method          |
  | click(*locator)                                   | Click element       
        | Buttons, links, clickable elements |
  | type_text(*locator, text: str)                    | Enter text
        | Input fields, textareas            |
  | select_dropdown_by_value(*locator, value: str)    | Select by value     
  attribute | Dropdowns (select elements)        |
  | select_dropdown_by_text(*locator, text: str)      | Select by visible   
  text    | Dropdowns (select elements)        |
  | is_element_displayed(*locator, timeout: int = 10) | Check visibility    
        | State-check methods (returns bool) |
  | get_text(*locator)                                | Get element text    
        | State-check methods (returns str)  |
  | get_attribute(*locator, attr: str)                | Get attribute value 
        | State-check methods (returns str)  |
  | wait_for_element(*locator, timeout: int = 10)     | Explicit wait       
        | Rare - prefer is_element_displayed |

  Common Violations:
  - ❌ self.web.select_dropdown(...) → ✅
  self.web.select_dropdown_by_value(...)
  - ❌ self.web.send_keys(...) → ✅ self.web.type_text(...)
  - ❌ self.web.find_element(...) → ✅ Use WebInterface methods, not raw    
  Selenium

  C.1.2 Locator Strategy Patterns

  POMs must use selenium.webdriver.common.by.By strategies. Choose in this  
  priority order:

  | Priority | Strategy        | Pattern                                |   
  Use When                                |
  |----------|-----------------|----------------------------------------|---
  --------------------------------------|
  | 1        | By.ID           | (By.ID, "submit")                      |   
  Element has unique ID attribute         |
  | 2        | By.CSS_SELECTOR | (By.CSS_SELECTOR, "#email")            |   
  CSS selector is short and stable        |
  | 3        | By.XPATH        | (By.XPATH, "//button[@type='submit']") | No
   ID/CSS option, or need text matching |

  Pattern Examples:
  # ✅ CORRECT: Tuple format, explicit By strategy
  EMAIL_INPUT = (By.ID, "email")
  SUBMIT_BTN = (By.CSS_SELECTOR, "button[type='submit']")
  ERROR_MSG = (By.XPATH, "//div[contains(@class, 'error')]")

  # ❌ WRONG: String locator (not tuple)
  EMAIL_INPUT = "#email"

  # ❌ WRONG: Missing By import or strategy
  EMAIL_INPUT = ("id", "email")

  C.1.3 Locator Naming Conventions

  | Element Type                       | Suffix                 | Example   
                             |
  |------------------------------------|------------------------|-----------
  ---------------------------|
  | Text input, textarea, number input | _INPUT                 |
  EMAIL_INPUT, PASSWORD_INPUT          |
  | Button (submit, action)            | _BTN or _BUTTON        |
  SUBMIT_BTN, LOGIN_BUTTON             |
  | Link (anchor tag)                  | _LINK                  |
  LOGOUT_LINK, FORGOT_PASSWORD_LINK    |
  | Dropdown (select)                  | _DROPDOWN              |
  COUNTRY_DROPDOWN, CATEGORY_DROPDOWN  |
  | Checkbox                           | _CHECKBOX              |
  TERMS_CHECKBOX, REMEMBER_ME_CHECKBOX |
  | Message/alert/notification         | _MESSAGE or _MSG       |
  ERROR_MESSAGE, SUCCESS_MSG           |
  | Heading/title                      | _HEADING or _TITLE     |
  PAGE_HEADING, SECTION_TITLE          |
  | Generic container                  | _CONTAINER or _SECTION |
  CART_CONTAINER, RESULTS_SECTION      |

  Format: UPPER_SNAKE_CASE (all caps, underscores)

  C.1.4 Method Naming Conventions

  Atomic Methods (Action Methods):

  | Pattern                    | Element Type | Example
     |
  |----------------------------|--------------|-----------------------------
  ---|
  | enter_<field>(text: str)   | Input field  | enter_email(text: str)      
     |
  | click_<element>()          | Button/Link  | click_submit(),
  click_logout() |
  | select_<field>(value: str) | Dropdown     | select_country(value: str)  
     |
  | check_<field>()            | Checkbox     | check_terms()
     |
  | uncheck_<field>()          | Checkbox     | uncheck_newsletter()        
     |

  State-Check Methods:

  | Pattern          | Returns | Use For                 | Example
                        |
  |------------------|---------|-------------------------|------------------
  ----------------------|
  | is_<state>()     | bool    | Visibility/existence    | is_logged_in(),  
  is_error_displayed()   |
  | has_<item>()     | bool    | Presence of content     | has_products(),  
  has_error_message()    |
  | get_<property>() | str     | Text content/attributes |
  get_error_message(), get_total_price() |

  C.1.5 navigate() Method Pattern (DD-49)

  Every POM MUST have a navigate() method following this exact pattern:     

  def navigate(self) -> "ClassName":
      """Navigate to this page. Gets URL from WebInterface config."""       
      url = self.web.config["url"]  # MUST use config, not hardcoded        
      self.web.navigate_to(f"{url}/path/to/page.htm")
      return self  # MUST return self

  Rules:
  - ✅ Get base URL from self.web.config["url"]
  - ✅ Append page-specific path
  - ✅ Return self for chaining
  - ❌ NO hardcoded full URLs
  - ❌ NO base_url constructor parameter (Task layer handles this)

  C.1.6 Type Annotations

  Required patterns:

  from interfaces.web_interface import WebInterface

  class LoginPage:
      def __init__(self, web: WebInterface):  # ✅ Type hint parameter      
          self.web = web

      def enter_email(self, text: str) -> "LoginPage":  # ✅ Type hint      
  return
          ...
          return self

      def is_logged_in(self) -> bool:  # ✅ Type hint return
          ...
          return True

  Rules:
  - Constructor parameter: web: WebInterface
  - Atomic methods return: -> "ClassName" (quoted, forward reference)       
  - State-check bool return: -> bool
  - State-check string return: -> str
  - Action method parameters: type hints required (text: str, value: str)   

  C.1.7 Import Structure

  Required imports (exact order):

  from selenium.webdriver.common.by import By
  from interfaces.web_interface import WebInterface

  Rules:
  - ✅ Always import By (even if only using By.ID)
  - ✅ Always import WebInterface for type hints
  - ❌ NO imports from tasks/ or roles/
  - ❌ NO imports from pytest or test utilities
  - ❌ NO imports from resources.utilities (autologger belongs at Task/Role 
  level)

  C.1.8 Docstrings

  Optional but recommended pattern:

  class LoginPage:
      """Page Object for login page at /authentication."""

      def enter_email(self, text: str) -> "LoginPage":
          """Enter text into email field."""
          ...

      def is_logged_in(self) -> bool:
          """Check if user is logged in (logout link visible)."""
          ...

  Rules:
  - Class docstring: brief page description
  - Method docstrings: one-line description of action/check
  - Not validated by gates (optional for AI, but improves readability)      

  C.1.9 State-Check Method Timeout Patterns

  | Check Type             | Timeout       | Example              |
  |------------------------|---------------|----------------------|
  | Page load verification | 10s (default) | is_page_loaded()     |
  | Success message        | 5s            | is_logged_in()       |
  | Error message          | 3s            | is_error_displayed() |
  | Conditional element    | 3s            | has_products()       |

  Pattern:
  def is_logged_in(self) -> bool:
      return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)    

  def is_error_displayed(self) -> bool:
      return self.web.is_element_displayed(*self.ERROR_MESSAGE, timeout=3)  

  C.1.10 Element Type → Method Mapping

  Tool 2 provides element_type. Use this mapping to generate correct atomic 
  methods:

  | element_type from Tool 2        | Generated Method Pattern          |   
  WebInterface Call                                  |
  |---------------------------------|-----------------------------------|---
  -------------------------------------------------|
  | textbox, input, email, password | enter_<name>(text: str)           |   
  self.web.type_text(*locator, text)                 |
  | button, submit                  | click_<name>()                    |   
  self.web.click(*locator)                           |
  | link                            | click_<name>()                    |   
  self.web.click(*locator)                           |
  | combobox, select, dropdown      | select_<name>(value: str)         |   
  self.web.select_dropdown_by_value(*locator, value) |
  | checkbox                        | check_<name>() + uncheck_<name>() |   
  self.web.click(*locator)                           |

  ---
  Changes Summary

  What this adds:
  1. WebInterface API Reference - Exact method signatures to prevent        
  select_dropdown vs select_dropdown_by_value errors
  2. Locator Strategy Patterns - Priority order (ID → CSS → XPath) with     
  examples
  3. Locator Naming Conventions - Suffix patterns (_INPUT, _BTN, _LINK) with
   examples
  4. Method Naming Conventions - Detailed patterns for enter_*, click_*,    
  select_*, is_*, has_*, get_*
  5. navigate() Pattern - Exact DD-49 implementation with config usage      
  6. Type Annotations - Required patterns for parameters and return types   
  7. Import Structure - Exact import order and what NOT to import
  8. Timeout Patterns - Standard timeout values by check type
  9. Element Type Mapping - How Tool 2 element_type maps to generated       
  methods

  Why this matters:
  - Current step-06.md has a template (Section J) but lacks prescriptive    
  rules
  - AI might generate valid Python but violate framework patterns (wrong    
  method names, wrong imports, wrong navigation)
  - Gates catch some violations (skeleton code, missing state methods) but  
  not all (wrong WebInterface method, wrong import structure)
  - This section bridges the gap between "what to do" (workflow) and "how to
   write it" (implementation)

  Where to place it:
  Insert as Section C.1 immediately after Section C (Skill Instruction) and 
  before Section D (Tools). This puts coding patterns right after the       
  execution steps, making them immediately accessible when AI is generating 
  code.
  
 > so we would just strenthen the associated qg then with this info so it     wont pass unless it sees these patterns. also, if not, tell ai to fix     
it using these patterns?                                                    
                                                                            
● Yes, exactly right.                                                       

  The correct implementation:                                                  
  1. Strengthen qg_page_object to validate all these patterns:              
    - WebInterface method names (is select_dropdown_by_value in allowed
  list?)
    - Locator format (tuple with By strategy?)
    - Locator naming (does _INPUT match element type textbox?)
    - Method naming (does enter_* match element type?)
    - navigate() present with config usage (not hardcoded URL?)
    - Type annotations present
    - Import structure correct (no Task/Role imports?)
    - Timeout values reasonable
  2. When validation fails, gate returns fix data:
  {
    "result": "NEEDS_RETRY",
    "issues": [
      {
        "violation": "Invalid WebInterface method: select_dropdown",        
        "location": "Line 45: self.web.select_dropdown(...)",
        "fix": "Use select_dropdown_by_value(...) - see Step 6 Section      
  C.1.1",
        "pattern_reference": "C.1.1 WebInterface API Reference"
      },
      {
        "violation": "Missing navigate() method",
        "location": "Class LoginPage has no navigate() method",
        "fix": "Add navigate() method using self.web.config['url'] - see    
  DD-49",
        "pattern_reference": "C.1.5 navigate() Method Pattern"
      }
    ]
  }

  3. AI uses fix data to regenerate code following the specific pattern     
  reference

  What NOT to do:
  - ❌ Add patterns to step protocol and hope AI reads it
  - ❌ Gate just returns "FAIL" without telling AI how to fix

  What TO do:
  - ✅ Add patterns to step protocol (documentation for humans + AI
  reference)
  - ✅ Gate validates every pattern (enforcement)
  - ✅ Gate returns actionable fix data pointing to specific section (DD-50)
  - ✅ AI reads fix data, references the pattern section, regenerates       

  This is your architecture working correctly:
  - Protocols = guidance (what good looks like)
  - Gates = enforcement (must match patterns or blocked)
  - Fix data = bridge between them (gate tells AI which pattern to read)
*****
make sure above integrates with this.
> one thing we're missing is that in our current implementation, there's     a method that searches webinterface for a valid method first before it    
is used. look for that fucntionality                                        
                                                                            
● Search(pattern: "def.*validate.*webinterface|def.*check.*method|getattr.*W
        ebInterface", glob: "**/gates/*.py")
  ⎿  Found 1 file (ctrl+o to expand)                                        
                                                                            ● Search(pattern: "WebInterface.*method|valid.*method.*WebInterface|inspect.
        *WebInterface", glob: "**/gates/*.py")                              
  ⎿  Found 1 file (ctrl+o to expand)
                                                                            
● Read(mcp_server\tools\gates\qg_page_object.py)                            
  ⎿  Read 923 lines                                                         
                                                                            
● Read(mcp_server\utils\webinterface_checker.py)                            
  ⎿  Read 504 lines                                                         
                                                                            
● You're right. I found it at lines 425-428 and 817-866 in                  
  qg_page_object.py.                                                        
                                                                              What already exists:                                                      
                                                                              WebInterfaceChecker (mcp_server/utils/webinterface_checker.py):
  - Introspects WebInterface class using Python's inspect module
  - Validates method existence dynamically (reads actual WebInterface code) 
  - Suggests similar methods for typos (e.g., select_dropdown → "Did you    
  mean: select_dropdown_by_value?")
  - Categorizes methods (Navigation, Interaction, Wait, etc.)
  - Already used by qg_page_object in _validate_webinterface_methods()      

  So the architecture is already correct:
  - Step protocol has coding patterns (documentation)
  - WebInterfaceChecker provides dynamic truth source (actual WebInterface  
  methods)
  - Gate validates against truth source (enforcement)
  - Gate returns fix data with suggestions (DD-50)

  What's NOT validated yet:
  1. Locator naming conventions (_INPUT, _BTN, _LINK suffixes)
  2. Method naming patterns (enter_*, click_*, is_*, has_*, get_*)
  3. Type annotations present and correct
  4. Import structure (only By and WebInterface, no Task/Role imports)      
  5. Locator format (tuple with By strategy, not string)

  The correct move:

  Add coding patterns reference to step-06.md (Section C.1), then strengthen
   the gate to validate the patterns NOT already covered by
  WebInterfaceChecker.

  WebInterfaceChecker handles: "Does this method exist in WebInterface?"    
  New gate validations handle: "Does this code follow framework
  naming/structure patterns?"
  
 -----
 > im going to try protocols + smart gates first. see how that works.        dont give me any code                                                      
                                                                            
● Good call. That's the simpler architecture to start with.                                                                                             
  What You're Testing                                                          
  Protocols (Skills) = Single Source of Truth                               
  - Add C.1 sections with detailed coding patterns to step-06, 07, 08, 09
  - Patterns live in markdown, AI reads them before generating

  Smart Gates = Enforcement + Teaching
  - Validate the patterns
  - When validation fails, return fix data that points AI to specific       
  protocol section
  - AI re-reads that section and regenerates

  No Registries
  - Patterns don't live in Python
  - Gates use regex/parsing to detect violations
  - Fix data bridges gate validation to protocol documentation

  What Needs to Happen

  Step 6-9 protocols:
  - Add C.1 coding pattern sections with detailed rules and examples        
  - Make them specific enough that AI can apply them directly

  Gates (qg_page_object, qg_task, qg_role, qg_test_runner):
  - Add validation logic for the patterns
  - Return DD-50 fix data format with pattern_reference pointing to protocol
   section
  - AI reads fix data, goes to referenced section, applies pattern

  The Test

  If this works well:
  - ✅ Patterns documented once (in protocols)
  - ✅ Gates catch violations
  - ✅ AI self-corrects using protocol references
  - ✅ No duplication

  If it doesn't work well (gates get too complex, pattern detection is      
  fragile):
  - Then consider moving patterns to Python registries

  Smart to test the simpler approach first before adding infrastructure.    

  Want me to just outline which patterns each gate should validate, or do   
  you want to start implementing yourself?
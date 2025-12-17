# Phase 0: Requirements Gathering & Test Design (QA 4D Framework)

**Version:** 1.0.0
**Last Updated:** 2025-01-11
**Status:** Active

---

## Overview

This document defines the Phase 0 process for QA projects using the 4D Framework. Phase 0 for QA differs significantly from software development Phase 0.

**Purpose:** Gather requirements (user stories), derive test scenarios, and design the test framework architecture to support testing.

**Output:** `0-test-design-{project-name}.md` document with complete test design

**Note:** Normally QA receives user stories from Business/PM. If no stakeholder exists (portfolio projects), QA may need to write user stories themselves.

---

## QA Phase 0 vs Dev Phase 0

### Software Dev Phase 0 (Design Discussion)
- **Input:** Product requirements or feature idea
- **Process:** Design the feature (UX/UI, architecture, technical decisions)
- **Output:** Design decisions feed into PRD

### QA Phase 0 (Requirements Gathering & Test Design)
- **Input:** User stories from Business/PM (or application to analyze)
- **Process:** Gather user stories → Derive test scenarios → Design test architecture
- **Output:** Test design document with scenarios and framework design

### Key Difference

**Software:** Start with architecture, design how to BUILD it
**QA:** Start with requirements/user stories, design what to TEST and how to test it

---

## When to Use This Process

**Use Phase 0 for QA when:**
- Building a new test automation framework
- Testing a new application or major feature set
- Need to design test architecture (page objects, tasks, roles)
- Multiple workflows to test (3+ workflows)
- Framework requires careful architectural planning

**Skip Phase 0 (go straight to writing tests) when:**
- Adding 1-2 tests to existing framework
- Bug fix verification (quick test)
- Framework architecture already exists and is stable
- Trivial test scenarios (<3 scenarios)

---

## Phase 0 Process Flow

```
Requirements/Application → User Stories → Test Scenarios → Framework Design → Test Plan (Phase 1)
```

**Step-by-Step:**
1. Identify features/workflows to test
2. **Gather user stories** for each workflow (from Business/PM, or write if no stakeholder)
3. Derive test scenarios from user stories
4. Design test architecture to support scenarios (choose pattern: POM, BDD, custom layers, etc.)
5. Document tooling/integration (if applicable)
6. Move to Phase 1 (Test Plan)

---

## Phase 0 Structure: Section-by-Section Approach

Phase 0 is organized into sections. Each section covers one workflow or architectural component.

### Typical Section Breakdown

#### Section 1: Foundation Layer Design
- **Purpose:** Design framework infrastructure (not tests yet)
- **Content depends on chosen architecture pattern** (see Test Architecture Patterns below)
  - Common elements: Driver management, configuration, test data, fixtures
  - Pattern-specific: Page objects, keyword libraries, step definitions, custom layers, etc.

**When to design Foundation Layer:**
- Before any workflow sections
- If building new framework from scratch
- If adding major infrastructure changes to existing framework

---

#### Sections 2-N: Workflow Design

Each workflow section follows this pattern:

1. **Identify Features** (manual exploration or screenshots)
2. **Gather User Stories** (receive from Business/PM, or write if no stakeholder)
3. **Derive Test Scenarios** (specific test cases from each user story)
4. **Design Test Components** (based on chosen architecture pattern - see below)

**Example Workflow Sections:**
- Authentication (login, registration, logout)
- Product Catalog (browse, filter, sort, search)
- Shopping Cart (add, update, remove)
- Checkout (address, payment, confirmation)
- Account Management (profile, orders, addresses)

---

#### Final Section: Tooling/Integration Design

**If building MCP server or other tooling:**
- Design MCP tools
- Define tool parameters and returns
- Document integration approach

---

## Test Architecture Patterns

Choose an architecture pattern that fits your project needs. Common patterns:

### Pattern 1: Page Object Model (POM)
**Best for:** UI-heavy web applications
**Structure:**
- Page classes (one per page/component)
- Test files use page classes
- Methods represent UI actions

**Example:** `LoginPage.enter_credentials()`, `HomePage.click_cart()`

---

### Pattern 2: Custom Layered Architecture (Roles/Tasks/Pages)
**Best for:** Complex business workflows, role-based testing
**Structure:**
- Roles (user personas)
- Tasks (business workflows using pages)
- Pages (UI interactions)
- Tests (use roles and tasks)

**Example:** `RegisteredUser.checkout_with_product()` → Uses Tasks → Uses Pages

---

### Pattern 3: BDD/Gherkin
**Best for:** Collaboration with non-technical stakeholders
**Structure:**
- Feature files (Gherkin scenarios)
- Step definitions (implementation)
- Support classes (pages, helpers)

**Example:** `Given I am logged in`, `When I add product to cart`, `Then cart shows 1 item`

---

### Pattern 4: Keyword-Driven
**Best for:** Non-programmers creating tests, data-driven testing
**Structure:**
- Keyword library (reusable actions)
- Test data (spreadsheets/JSON with keywords)
- Test engine (interprets keywords)

**Example:** `Navigate | URL | LoginPage`, `EnterText | username | john@example.com`

---

### Pattern 5: Hybrid
**Best for:** Large projects, mixing patterns
**Structure:** Combine patterns as needed (POM + BDD, Layered + Keyword, etc.)

**Choose based on:** Team skills, stakeholder needs, application complexity, maintenance requirements

---

## Section Template: Workflow Design

### Step 1: Identify Features

**How:** Explore application, take screenshots, list features

**Example:**
```
Product Catalog Features Identified:
- Browse by category (Women, Dresses, T-Shirts)
- Filter by size, color, price
- Sort by price, name
- Quick View modal
- Product detail page
```

---

### Step 2: Gather User Stories

**Normal QA Process:** Receive user stories from Business/PM

**If No Stakeholder (Portfolio Projects):** Write user stories yourself

**Format:**
```markdown
### User Story N: [Title]
**As a** [user type]
**I want to** [action]
**So that** [benefit]

**Acceptance Criteria:**
- Criteria 1
- Criteria 2
- Criteria 3
```

**Tips:**
- Gather 3-10 user stories per workflow
- Focus on user needs, not technical implementation
- Include validation/error scenarios (not just happy paths)
- Acceptance criteria should be testable

**Example:**
```markdown
### User Story 1: Browse Products by Category
**As a** shopper
**I want to** browse products by category
**So that** I can see all items available in that category

**Acceptance Criteria:**
- Category menu is visible in header
- Clicking category loads product listing page
- Breadcrumbs show current category
- Product count displays (e.g., "Showing 1-7 of 7 items")
```

---

### Step 3: Derive Test Scenarios

For each user story, create 1-5 specific test scenarios.

**Format:**
```markdown
### Test Scenario N: [Title]
**Scenario:** [One-sentence description]

**Steps:**
1. Step 1
2. Step 2
3. Verify expected result

**Expected Result:** [What should happen]
```

**Tips:**
- Be specific (include test data, expected results)
- Cover happy path, edge cases, error cases
- Number scenarios per workflow (Scenario 1, 2, 3...)
- Each scenario should be independently executable

**Example:**
```markdown
### Test Scenario 1: Navigate to Women Category
**Scenario:** Click Women category, verify products load

**Steps:**
1. Navigate to homepage
2. Click "WOMEN" in navigation menu
3. Wait for product listing page
4. Verify breadcrumbs show "Home > Women"
5. Verify product count displays
6. Verify at least 1 product is visible

**Expected Result:** Women category page loads with products displayed
```

---

### Step 4: Design Test Components

Design test components based on your chosen architecture pattern (see Test Architecture Patterns above).

**For POM (Page Object Model):**
- Design page classes for each page/component
- Define locators and UI action methods
- Example: `LoginPage`, `ProductListPage`, `CartPage`

**For Custom Layered Architecture (Roles/Tasks/Pages):**
- Design page classes (UI interactions)
- Design task classes (business workflows)
- Design role classes (user personas)
- Example: `RegisteredUser` → `CartTasks` → `CartPage`

**For BDD/Gherkin:**
- Design step definitions for Gherkin steps
- Design support classes (pages, helpers)
- Example: Step def for "Given I am logged in" uses `LoginPage`

**For Keyword-Driven:**
- Design keyword library (reusable actions)
- Define keyword parameters and behavior
- Example: Keyword `Login` takes username, password

**General Tips:**
- Match component design to chosen pattern
- Keep components focused (single responsibility)
- Design for reusability across tests
- Include verification/assertion methods
- Document component purpose and usage

**Example Template (Generic):**
```markdown
### [ComponentName]
**Pattern:** [POM / Layered / BDD / Keyword / etc.]
**Location:** `[file path]`
**Purpose:** [What this component does]

**Key Elements:**
- Element/Method/Keyword 1
- Element/Method/Keyword 2

**Usage Example:**
[Show how tests use this component]
```

---

## Task Management During Phase 0

### Approach 1: Simple Completion Checklist (Default)

Use a lightweight checklist embedded in the test design document:

```markdown
## Phase 0 Completion Checklist
- [x] Section 1: Foundation Layer
- [x] Section 2: Authentication Workflows
- [ ] Section 3: Product Catalog Workflows
- [ ] Section 4: Shopping Cart Workflows
```

**When to use:**
- Phase 0 has 3-8 sections
- Each section takes <2 hours
- Single person working
- Low handoff risk

---

### Approach 2: Formal Task List (For Large Phase 0)

Create a "PRD for Phase 0 Completion" and generate tasks using Phase 2 process.

**When to use:**
- Phase 0 has >8 sections
- Each section requires >2 hours
- Multiple people working
- Phase 0 spans >4 sessions (>10 hours)
- High handoff risk

**See:** Task Management Strategy section in `0-phase0-test-design.md` for decision criteria.

---

## MVP Strategy: Prioritizing Test Scenarios

**Common Challenge:** Phase 0 generates many more scenarios than time allows.

**Solution:** Define MVP scope upfront.

### MVP Selection Criteria

**Must Test (MVP):**
- ✅ Happy path for each critical workflow
- ✅ End-to-end user journey (registration → browse → purchase)
- ✅ Key validation scenarios (login errors, form validation)
- ✅ Framework demonstrates all architectural layers

**Can Defer to v2.0:**
- ❌ Edge cases for every field
- ❌ All filter combinations
- ❌ Minor features (wishlist, compare, reviews)
- ❌ Exhaustive negative testing

**Example:**
- **Total Scenarios Designed:** 62
- **MVP Scenarios:** 15 (24% coverage)
- **Deferred:** 47 (v2.0 backlog)

**Rationale:** MVP demonstrates framework capabilities, covers critical path, ships on time.

---

## Output: Phase 0 Test Design Document

### Required Sections

1. **Overview**
   - Project description
   - Target application
   - MVP scope definition

2. **Phase 0 Task Management Strategy**
   - Document approach chosen (simple checklist vs formal tasks)
   - Decision criteria for future reference

3. **Phase 0 Completion Checklist**
   - Track section completion

4. **Section 1: Foundation Layer Design**
   - Framework infrastructure decisions

5. **Sections 2-N: Workflow Designs**
   - User stories
   - Test scenarios
   - Page objects
   - Task methods

6. **Final Section: Tooling/Integration**
   - MCP server design (if applicable)
   - CI/CD integration (if applicable)

7. **Appendix: QA 4D Framework Adaptations**
   - Meta-learning notes
   - Process improvements discovered
   - Decision rationale

---

## Transition to Phase 1: Test Plan

**Phase 0 Complete When:**
- ✅ All workflow sections designed
- ✅ Page objects designed for all scenarios
- ✅ Task methods designed for all workflows
- ✅ Tooling/integration designed (if applicable)
- ✅ Completion checklist all marked [x]

**Phase 1 Input:**
- `0-phase0-test-design.md` document
- User stories, scenarios, page objects, tasks

**Phase 1 Output:**
- Consolidated test plan document
- Test execution strategy
- Test data approach
- Environment setup
- Success criteria
- Risk assessment

---

## Common Pitfalls & How to Avoid

### Pitfall 1: Designing Too Many Scenarios
**Problem:** Phase 0 generates 50+ scenarios, timeline explodes
**Solution:** Define MVP upfront, defer non-critical scenarios to v2.0

---

### Pitfall 2: Over-Designing Framework Infrastructure
**Problem:** Spend days designing perfect architecture, delay testing
**Solution:** Design "just enough" infrastructure, iterate based on needs

---

### Pitfall 3: Writing Implementation Details in Phase 0
**Problem:** Phase 0 includes CSS selectors, specific locators, code
**Solution:** Phase 0 is design only - locators come during implementation (Phase 3)

---

### Pitfall 4: Skipping User Stories
**Problem:** Jump straight to test scenarios without user stories
**Solution:** Always write user stories first - they clarify WHAT to test and WHY

---

### Pitfall 5: Not Prioritizing Scenarios
**Problem:** Treat all scenarios equally, try to implement all at once
**Solution:** Mark MVP scenarios, defer rest, focus on critical path first

---

### Pitfall 6: Ignoring Existing Patterns
**Problem:** Design from scratch when patterns exist
**Solution:** Reference existing frameworks, reuse proven patterns

---

## Success Criteria for Phase 0

**Phase 0 is successful when:**
- ✅ All workflows have user stories (3-10 per workflow)
- ✅ All user stories have test scenarios (1-5 per story)
- ✅ All scenarios have corresponding page objects designed
- ✅ All workflows have task methods designed
- ✅ MVP scope is clearly defined (X tests covering Y workflows)
- ✅ Test design document is complete and reviewed
- ✅ Ready to write Test Plan (Phase 1)

---

## Example: Phase 0 Session Flow

### Session 1: Foundation + Auth (3 hours)
1. Design foundation layer (1 hour)
2. Explore authentication features (15 min)
3. Write auth user stories (30 min)
4. Derive auth test scenarios (30 min)
5. Design auth page objects (30 min)
6. Design auth task methods (15 min)

---

### Session 2: Catalog + Cart (2.5 hours)
1. Explore catalog features (screenshots) (15 min)
2. Write catalog user stories (30 min)
3. Derive catalog test scenarios (30 min)
4. Design catalog page objects + tasks (45 min)
5. Explore cart features (15 min)
6. Write cart user stories + scenarios + design (45 min)

---

### Session 3: Checkout + MCP Design (2 hours)
1. Design checkout workflows (1 hour)
2. Design MCP server (5 tools) (45 min)
3. Review and finalize Phase 0 document (15 min)

**Total Phase 0 Time:** 7.5 hours across 3 sessions

---

## Tools & Templates

### User Story Template
```markdown
### User Story N: [Title]
**As a** [user type]
**I want to** [action]
**So that** [benefit]

**Acceptance Criteria:**
- Criteria 1
- Criteria 2
- Criteria 3
```

---

### Test Scenario Template
```markdown
### Test Scenario N: [Title]
**Scenario:** [One-sentence description]

**Steps:**
1. Step 1
2. Step 2
3. Verify expected result

**Expected Result:** [What should happen]
```

---

### Test Component Template (Generic)
```markdown
### [ComponentName]
**Pattern:** [POM / Layered / BDD / Keyword / Hybrid]
**Location:** `[file path based on pattern]`

**Purpose:** [What this component does]

**Key Elements:**
(Customize based on pattern - locators for POM, keywords for keyword-driven, steps for BDD, etc.)
- Element/Method/Keyword 1
- Element/Method/Keyword 2

**Usage Example:**
[Show how tests use this component]
```

**Pattern-Specific Examples:**
- **POM:** Page class with locators and methods
- **Layered:** Role/Task/Page classes
- **BDD:** Step definition with Gherkin step text
- **Keyword:** Keyword name with parameters

---

## Appendix: Differences from Software Dev Phase 0

| Aspect | Software Dev Phase 0 | QA Phase 0 |
|--------|---------------------|-----------|
| **Input** | Product requirements | Application to test OR requirements |
| **Focus** | How to BUILD feature | What to TEST and how to test |
| **Starting Point** | Technical architecture | User stories (requirements) |
| **Output** | Design decisions → PRD | Test design → Test Plan |
| **Participants** | Engineers, architects | QA engineers, test architects |
| **Deliverable** | Design doc (conversational) | Test design doc (structured) |
| **Next Phase** | Phase 1: Write PRD | Phase 1: Write Test Plan |

**Key Insight:** QA starts with requirements/behaviors, Dev starts with architecture. Both are "design" phases, but QA designs TESTS while Dev designs CODE.

---

## Version History

**v1.0.0** (2025-01-11)
- Initial QA Phase 0 process documentation
- Captured from py_sel_framework_mcp project
- Based on real-world usage and iteration

---

**For Next QA Project:**
1. Copy this process doc to new project
2. Create blank `0-test-design-{project-name}.md` using this template as guide
3. Follow section-by-section approach
4. Choose test architecture pattern (POM, Layered, BDD, etc.)
5. Define MVP scope upfront
6. Prioritize ruthlessly
7. Ship on time

---

**Questions? Updates?**
This process will evolve. Capture learnings and update this doc as we use it on more QA projects.

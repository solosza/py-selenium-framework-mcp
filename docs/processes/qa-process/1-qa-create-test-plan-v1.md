# Phase 1: Create Test Plan (QA 4D Framework)

**Version:** 1.0.0
**Last Updated:** 2025-01-11
**Status:** Active

---

## Goal

To guide an AI assistant in creating a comprehensive Test Plan document based on the Phase 0 test design. The Test Plan should be actionable, clearly define test execution strategy, and provide all necessary information for a QA engineer to execute testing.

---

## Process

1. **Receive Phase 0 Test Design:** AI reads the completed `0-test-design-{project-name}.md` document containing user stories, test scenarios, and test component designs
2. **Ask Clarifying Questions:** AI asks questions about test execution strategy, environment setup, data approach, and logistics (NOT design - that's Phase 0)
3. **Generate Test Plan:** Based on Phase 0 design and clarifying answers, generate a comprehensive Test Plan using the structure below
4. **Save Test Plan:** Save as `tasks/test-plan-{project-name}.md` in the tasks directory

---

## Clarifying Questions (Examples)

The AI should adapt questions based on the project, but here are common areas to explore:

### Test Environment
- **Environment Details:** "What environments will tests run in? (local, staging, production, cloud, containerized?)"
- **Browser/Device Coverage:** "Which browsers and versions need testing? (Chrome, Firefox, Safari, Edge, mobile browsers?)"
- **Access Requirements:** "What credentials, VPNs, or access permissions are needed?"
- **Environment Stability:** "Are test environments stable and available? Any known issues?"

### Test Data
- **Data Source:** "Where will test data come from? (seed data, API, database, generated on-the-fly?)"
- **Data Management:** "How will test data be managed? (shared dataset, per-test isolation, cleanup strategy?)"
- **PII/Security:** "Any sensitive data concerns? Need to anonymize or use synthetic data?"

### Test Execution
- **Execution Order:** "Do tests have dependencies? Must they run in specific order?"
- **Parallel Execution:** "Can tests run in parallel or must they be sequential?"
- **Retry Strategy:** "Should failing tests auto-retry? How many times?"
- **Smoke vs Full Suite:** "Need separate smoke test suite for quick validation?"

### CI/CD Integration
- **Pipeline Integration:** "Will tests run in CI/CD pipeline? Which one? (GitHub Actions, Jenkins, CircleCI?)"
- **Trigger Events:** "When should tests run? (on PR, on merge, nightly, on-demand?)"
- **Failure Handling:** "What happens when tests fail in CI? (block merge, notify team, create ticket?)"

### Reporting & Artifacts
- **Report Format:** "What test report format? (HTML, XML, JSON, Allure, custom?)"
- **Artifact Storage:** "Where are screenshots, logs, videos stored? How long retained?"
- **Notification:** "Who gets notified of test results? How? (email, Slack, dashboard?)"

### Timeline & Resources
- **Timeline:** "When must MVP tests be complete? Any milestones?"
- **Resources:** "How many QA engineers? Any automation engineers? Manual testers?"
- **Availability:** "Full-time on this project or shared across projects?"

### Risk Areas
- **High-Risk Workflows:** "Which features are most critical? Where are most bugs expected?"
- **Technical Risks:** "Any known technical challenges? (flaky tests, slow pages, third-party dependencies?)"
- **Timeline Risks:** "Any timeline constraints or blockers?"

---

## Test Plan Structure

The generated Test Plan should include the following sections:

### 1. Executive Summary
**Purpose:** High-level overview of testing effort

**Contents:**
- Project name and version
- Target application/system under test
- Test plan author and date
- Brief summary of test objectives (2-3 sentences)
- Key milestones and dates

---

### 2. Test Objectives
**Purpose:** Define what testing aims to achieve

**Contents:**
- Primary objectives (e.g., "Validate core e-commerce workflows", "Ensure MVP functionality works end-to-end")
- Quality goals (e.g., "Achieve 90% pass rate", "Detect critical bugs before release")
- Learning objectives (if applicable - e.g., "Demonstrate QA Lead-level framework design")

---

### 3. Test Scope
**Purpose:** Clearly define what's included and excluded from testing

**Contents:**

#### In Scope (MVP)
- List workflows/features included in MVP testing
- Reference Phase 0 MVP scenarios
- Specific browsers, devices, environments

#### Out of Scope (Deferred to v2.0)
- List workflows/features deferred
- Explain why deferred (timeline, priority, complexity)

**Example:**
```markdown
#### In Scope (MVP)
- Authentication: Login, Registration, Logout (4 tests)
- Product Catalog: Browse, Filter, Quick View (4 tests)
- Shopping Cart: Add, Update, Remove (4 tests)
- Checkout: Address, Payment, Confirmation (3 tests)
- **Total:** 15 tests covering critical path

#### Out of Scope
- Account Management (profile, order history, addresses) - Deferred to v2.0
- Wishlist, Compare, Reviews - Low priority features
- Edge cases and exhaustive negative testing - Time constraints
```

---

### 4. Test Approach (Execution Strategy)
**Purpose:** Define how tests will be executed

**Contents:**

#### Test Types
- **Functional Testing:** What functional tests will be automated? (UI workflows, API calls, etc.)
- **Regression Testing:** How will regression be handled? (full suite on every commit, nightly, weekly?)
- **Smoke Testing:** Define smoke test suite (5-10 critical tests for quick validation)
- **Integration Testing:** How components integrate (e.g., frontend + backend + database)

#### Test Execution Strategy
- **Execution Order:** Sequential or parallel? Dependencies between tests?
- **Browser Strategy:** Which browsers? Cross-browser testing approach?
- **Test Data Strategy:** Where data comes from, how it's managed
- **Error Handling:** What happens on test failure? (screenshot, retry, abort suite?)

#### Tools & Frameworks
- **Test Framework:** (e.g., Pytest, TestNG, JUnit, Mocha)
- **Automation Tool:** (e.g., Selenium, Playwright, Cypress, Appium)
- **Reporting:** (e.g., pytest-html, Allure, custom HTML reports)
- **CI/CD:** (e.g., GitHub Actions, Jenkins, CircleCI)
- **Version Control:** (e.g., Git, GitHub, GitLab)

---

### 5. Test Environment Setup
**Purpose:** Document environment configuration and requirements

**Contents:**

#### Environment Details
```markdown
| Environment | URL | Purpose | Credentials |
|-------------|-----|---------|-------------|
| Local | http://localhost:8080 | Dev testing | dev/dev123 |
| Staging | https://staging.example.com | Pre-release validation | qa/qa123 |
| Production | https://www.example.com | Smoke tests only | N/A |
```

#### Browser & Device Matrix
```markdown
| Browser | Version | OS | Priority |
|---------|---------|----|---------|
| Chrome | Latest | Windows 10 | P0 (MVP) |
| Firefox | Latest | Windows 10 | P1 (v2.0) |
| Safari | Latest | macOS | P1 (v2.0) |
```

#### Dependencies
- External services (payment gateways, email services)
- Database access requirements
- VPN or network access
- Third-party APIs

#### Setup Instructions
- How to configure local environment
- Required tools and versions (Python, Node, Java, etc.)
- Environment variables (.env file configuration)
- Installation steps (virtualenv, npm install, etc.)

---

### 6. Test Data Strategy
**Purpose:** Define how test data is created, managed, and cleaned up

**Contents:**

#### Data Sources
- Seed data (pre-loaded test accounts, products)
- Generated data (Faker library, random data generators)
- Production data (anonymized/sanitized if applicable)

#### Data Management Approach
- **Per-test isolation:** Each test creates/cleans up own data
- **Shared dataset:** Tests share common data (requires coordination)
- **Database snapshots:** Reset to known state between runs

#### Test Accounts
```markdown
| Account Type | Username | Password | Purpose |
|--------------|----------|----------|---------|
| Registered User | testuser@example.com | Test123! | Login, cart, checkout tests |
| Admin | admin@example.com | Admin123! | Admin panel tests |
```

#### Data Cleanup
- How and when test data is cleaned up
- Isolation strategy to prevent test interference
- Database reset procedures (if applicable)

---

### 7. Test Execution Schedule
**Purpose:** Define timeline and milestones

**Contents:**

#### Timeline
```markdown
| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Week 1 | 5 days | Framework setup + Authentication tests (4 tests) |
| Week 2 | 3 days | Catalog + Cart tests (8 tests) |
| Week 2 | 2 days | Checkout tests (3 tests) + Polish |
```

#### Milestones
- **Day 5:** Authentication workflow complete (4 tests passing)
- **Day 10:** All 15 MVP tests passing
- **Day 14:** MCP server integrated + Demo ready

#### Execution Frequency
- **Local:** On-demand by QA engineers
- **CI Pipeline:** On every PR (smoke suite), nightly (full suite)
- **Staging:** Before every release

---

### 8. Entry & Exit Criteria
**Purpose:** Define when testing starts and when it's considered complete

**Contents:**

#### Entry Criteria (When can testing begin?)
- [ ] Test framework setup complete
- [ ] Test environment accessible
- [ ] Test data available
- [ ] Base test infrastructure working (WebDriver, fixtures, utilities)
- [ ] Phase 0 test design document complete

#### Exit Criteria (When is testing complete?)
- [ ] All MVP test scenarios implemented (15 tests)
- [ ] 90%+ pass rate achieved
- [ ] Critical bugs resolved (P0/P1)
- [ ] Test reports generated and reviewed
- [ ] Test suite integrated with CI/CD
- [ ] Documentation complete (README, test reports)
- [ ] Demo prepared (if applicable)

---

### 9. Risks & Mitigation
**Purpose:** Identify potential issues and how to address them

**Contents:**

#### Risk Assessment
```markdown
| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| Test environment unstable | High | Medium | Use local environment for development, staging for validation |
| Target site goes down | High | Low | Use wayback machine or local site mirror |
| Framework learning curve | Medium | High | Allocate extra time for framework setup, reference existing projects |
| Scope creep (too many tests) | High | Medium | Stick to MVP scope (15 tests), defer rest to v2.0 |
| Flaky tests | Medium | High | Implement explicit waits, retry logic, isolation |
```

#### Contingency Plans
- **Fallback:** If automation blocked, prepare manual test cases
- **Timeline:** If behind schedule, reduce scope further (10 tests instead of 15)
- **Environment:** If staging unavailable, test against local mock

---

### 10. Deliverables
**Purpose:** Define what will be produced

**Contents:**

#### Code Deliverables
- [ ] Test framework source code (page objects, tasks, roles, utilities)
- [ ] Test scenarios (15 automated tests)
- [ ] Configuration files (.env, pytest.ini, conftest.py)
- [ ] MCP server implementation (5 tools)

#### Documentation Deliverables
- [ ] README.md (project overview, setup, usage)
- [ ] Test reports (HTML reports for test runs)
- [ ] Framework architecture diagram (optional)
- [ ] MCP integration guide (optional)

#### Demo Deliverables (if applicable)
- [ ] Demo video or live demo
- [ ] Presentation slides (optional)

---

### 11. Success Criteria
**Purpose:** Define how success is measured

**Contents:**

#### Functional Success
- [ ] 15 MVP tests implemented and passing
- [ ] All critical workflows covered (auth, catalog, cart, checkout)
- [ ] Tests run reliably (90%+ pass rate)
- [ ] Test execution time acceptable (<15 minutes for full suite)

#### Technical Success
- [ ] Framework demonstrates professional architecture (4-layer design)
- [ ] Code is maintainable and well-documented
- [ ] MCP integration works (5 tools functional)
- [ ] CI/CD integration complete (tests run on pipeline)

#### Business Success (if applicable)
- [ ] Portfolio project demonstrates QA Lead-level skills
- [ ] Interview readiness (can explain architecture, design decisions)
- [ ] Reusable framework template for future projects

---

### 12. Appendix
**Purpose:** Reference materials and supporting documents

**Contents:**

#### Reference Documents
- Link to Phase 0 test design: `docs/0-test-design-{project-name}.md`
- Link to process docs: `docs/0-requirements-and-test-design-v1.md`
- Target application URL
- Competitor analysis (if applicable)

#### Test Scenarios Summary
(Reference Phase 0 for full scenarios - summarize here)

**Authentication (4 scenarios):**
1. Valid login
2. Invalid credentials
3. User registration
4. Logout

**Product Catalog (4 scenarios):**
1. Browse by category
2. Filter by size/color
3. Sort by price
4. Quick view modal

**Shopping Cart (4 scenarios):**
1. Add to cart
2. Update quantity
3. Remove item
4. Empty cart validation

**Checkout (3 scenarios):**
1. Guest checkout with new address
2. Registered user checkout
3. Order confirmation display

---

## Target Audience

The Test Plan should be understandable by:
- **QA Engineers** - Will execute tests and interpret results
- **Automation Engineers** - Will maintain and extend framework
- **Stakeholders** - Need high-level understanding of test coverage and timeline

---

## Output

- **Format:** Markdown (`.md`)
- **Location:** `/tasks/`
- **Filename:** `test-plan-{project-name}.md`

---

## Definition of Ready

Test Plan is ready when it includes:

- ✅ All 12 sections completed
- ✅ Test scope clearly defined (MVP vs deferred)
- ✅ Test environment documented with access details
- ✅ Test data strategy defined
- ✅ Execution schedule with milestones
- ✅ Entry/Exit criteria defined
- ✅ Risks identified with mitigation strategies
- ✅ Success criteria measurable and specific
- ✅ References Phase 0 test design document

---

## Transition to Phase 2: Divide (Task Generation)

**Phase 1 Complete When:**
- ✅ Test Plan document created and saved
- ✅ All clarifying questions answered
- ✅ User approves test plan approach

**Phase 2 Input:**
- Test Plan document (`tasks/test-plan-{project-name}.md`)
- Phase 0 test design document (`docs/0-test-design-{project-name}.md`)

**Phase 2 Output:**
- Task list (`tasks/tasks-test-plan-{project-name}.md`)
- 4-6 parent tasks with detailed sub-tasks
- Relevant files identified

---

## Version History

**v1.0.0** (2025-01-11)
- Initial QA Phase 1 process documentation
- Adapted from 4D Dev Framework Phase 1 (PRD generation)
- Based on QA methodology and test planning best practices

---

**For Next QA Project:**
1. Copy this template as guide
2. Read Phase 0 test design document
3. Ask clarifying questions about test execution
4. Generate Test Plan using this structure
5. Save as `tasks/test-plan-{project-name}.md`
6. Proceed to Phase 2 (Task Generation)

---

**Questions? Updates?**
This template will evolve. Capture learnings and update as we use it on more QA projects.

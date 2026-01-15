# Phase 3: Execute Task List (QA 4D Framework)

**Version:** 1.0.0
**Last Updated:** 2025-01-11
**Status:** Active

---

## Goal

Guidelines for executing task lists to implement test framework infrastructure and test scenarios. This phase guides QA engineers through building the test automation framework and tests one task at a time with proper validation gates.

---

## Task Implementation Protocol

### One Sub-Task at a Time
**CRITICAL RULE:** Do **NOT** start the next sub-task until you ask the user for permission and they say "yes" or "y"

**Why:** This ensures:
- User can review progress incrementally
- Issues are caught early before compounding
- Context handoff is clear if session ends
- User maintains control over execution pace

---

### Completion Protocol

#### Step 1: Complete Sub-Task
When you finish a **sub-task**:
1. Implement the code/test
2. Immediately mark it as completed by changing `[ ]` to `[x]` in the task list file
3. Update TodoWrite tool to reflect progress
4. Ask user for permission to continue

**Example:**
```markdown
- [ ] 1.0 Implement Foundation Layer [CORE]
  - [x] 1.1 Create WebInterface class with Selenium wrapper methods
  - [x] 1.2 Implement config management using .env file
  - [ ] 1.3 Create data_generator.py with Faker wrapper
  ...
```

---

#### Step 2: Parent Task Completion (ALL Sub-Tasks Done)

If **all** sub-tasks underneath a parent task are now `[x]`, follow this sequence:

##### 1. Run Quality Gates
**For Framework Infrastructure (CORE tasks):**
```bash
# Run linter (if applicable)
flake8 framework/ tests/

# Run type checker (if applicable)
mypy framework/

# Run unit tests (if testing framework code)
pytest tests/unit/

# Run integration tests (if applicable)
pytest tests/integration/
```

**For Test Scenarios (GLUE tasks):**
```bash
# Run the test scenarios themselves
pytest tests/auth/         # For auth workflow
pytest tests/catalog/      # For catalog workflow
pytest tests/cart/         # For cart workflow
pytest tests/checkout/     # For checkout workflow

# Or run full suite
pytest tests/ -v

# Generate HTML report
pytest tests/auth/ --html=_reports/auth_report.html --self-contained-html
```

**Quality Gate Criteria:**
- All relevant tests pass (90%+ pass rate for MVP)
- No linter/type errors (if applicable)
- Test execution completes without crashes
- Artifacts captured (screenshots on failure, logs, reports)

---

##### 2. Clean Up (Only if ALL Tests Pass)
- Remove any temporary files, debug code, commented-out code
- Remove unused imports
- Clean up test data artifacts (old screenshots, logs)
- Verify no secrets committed (API keys, passwords in plain text)

---

##### 3. Stage Changes
```bash
git add .
```

**IMPORTANT:** Only stage after tests pass and cleanup is done

---

##### 4. Commit with Descriptive Message
Use a detailed commit message following conventional commit format:

**Format:**
```
<type>: <subject line> (Task X.0)

<body explaining what was accomplished>

Completed Subtasks:
- X.1: Description
- X.2: Description
- X.N: Description

Relevant Files:
- path/to/file1.py
- path/to/file2.py
- path/to/test_file.py

Related to Test Plan v1.0
```

**Example:**
```bash
git commit -m "$(cat <<'EOF'
feat: Implement authentication workflow (Task 2.0)

This commit completes Task 2.0 by implementing the full authentication
workflow including page objects, task methods, and test scenarios.

Completed Subtasks:
- 2.1: Created AuthenticationPage with login/registration locators and methods
- 2.2: Created RegistrationPage with form fields and methods
- 2.3: Implemented common_tasks.py with login(), logout(), register_new_user()
- 2.4: Implemented test_valid_login.py test scenario
- 2.5: Implemented test_invalid_credentials.py test scenario
- 2.6: Implemented test_registration.py test scenario
- 2.7: Implemented test_logout.py test scenario
- 2.8: Ran pytest tests/auth/ - all 4 tests passed

Relevant Files:
- framework/pages/common/authentication_page.py
- framework/pages/common/registration_page.py
- framework/tasks/common_tasks.py
- tests/auth/test_valid_login.py
- tests/auth/test_invalid_credentials.py
- tests/auth/test_registration.py
- tests/auth/test_logout.py

Related to Test Plan v1.0
EOF
)"
```

---

##### 5. Mark Parent Task Complete
Once committed, mark the **parent task** as completed `[x]` in the task list file.

```markdown
- [x] 2.0 Implement Authentication Workflow [GLUE]
  - [x] 2.1 Create AuthenticationPage class
  - [x] 2.2 Create RegistrationPage class
  - [x] 2.3 Implement common_tasks.py
  - [x] 2.4 Implement test_valid_login.py
  - [x] 2.5 Implement test_invalid_credentials.py
  - [x] 2.6 Implement test_registration.py
  - [x] 2.7 Implement test_logout.py
  - [x] 2.8 Run checks: pytest tests/auth/ -v
  - [x] 2.9 Record results in this file
  - [x] 2.10 Verify "Done When" criteria met

**Commands Run:**
```bash
pytest tests/auth/ -v
# 4 passed in 15.2s
```

**Results:**
- All 4 authentication tests passed
- No failures or errors
- HTML report generated: _reports/auth_report.html
```

---

##### 6. Stop and Wait
Stop after marking parent task complete and wait for user's go-ahead before starting next parent task.

---

## Task List Maintenance

### 1. Update Task List as You Work
- Mark sub-tasks as completed (`[x]`) immediately after finishing
- Mark parent tasks as completed (`[x]`) after all sub-tasks done and committed
- Add new tasks if they emerge during implementation
- Update task descriptions if requirements change

### 2. Maintain "Relevant Files" Section
- List every file created or modified
- Give each file a one-line description of its purpose
- Update as new files are added

**Example:**
```markdown
## Relevant Files

### Framework Infrastructure
- `framework/interfaces/web_interface.py` - Selenium wrapper with logging, screenshots, waits
- `framework/resources/config.py` - Environment configuration management (ADDED)
- `conftest.py` - Pytest fixtures for driver, web_interface, test users

### Page Objects
- `framework/pages/common/authentication_page.py` - Login/registration page interactions
- `framework/pages/common/registration_page.py` - Registration form page (ADDED)
...
```

---

### 3. Record Test Execution Results
After running quality gates, paste command output into task list:

**Example:**
```markdown
**Commands Run:**
```bash
# Run authentication tests
pytest tests/auth/ -v
# tests/auth/test_valid_login.py::test_valid_login PASSED
# tests/auth/test_invalid_credentials.py::test_invalid_credentials PASSED
# tests/auth/test_registration.py::test_registration PASSED
# tests/auth/test_logout.py::test_logout PASSED
# 4 passed in 15.2s

# Generate HTML report
pytest tests/auth/ --html=_reports/auth_report.html --self-contained-html
# Report generated: _reports/auth_report.html
```

**Results:**
- Pass rate: 100% (4/4)
- Execution time: 15.2 seconds
- Artifacts: Screenshots (on failure), logs, HTML report
```

---

## AI Instructions

When working with task lists during Phase 3, the AI must:

### 1. Before Starting Work
- Read the task list file
- Identify which sub-task is next (first `[ ]` in sequence)
- Verify all previous sub-tasks are `[x]`
- Check if user gave permission to proceed

### 2. While Implementing Sub-Task
- Focus on ONE sub-task only
- Follow test architecture defined in Phase 0
- Use existing patterns from codebase
- Write clean, maintainable code
- Add comments/docstrings for clarity

### 3. After Implementing Sub-Task
- Mark sub-task `[x]` in task list file
- Update TodoWrite tool
- Test the implementation (run relevant tests if applicable)
- Ask user: "Sub-task X.Y complete. Ready to proceed to X.Z? (yes/no)"
- **WAIT FOR USER RESPONSE**

### 4. When All Sub-Tasks Complete (Parent Task Done)
- Run full quality gates (pytest, linter, etc.)
- Record commands + results in task list
- Clean up temporary code/files
- Stage changes: `git add .`
- Commit with detailed message (use HEREDOC format)
- Mark parent task `[x]`
- Update TodoWrite tool
- Ask user: "Task X.0 complete. Ready to start Task Y.0? (yes/no)"
- **WAIT FOR USER RESPONSE**

### 5. Continuously
- Keep task list file up to date
- Keep "Relevant Files" section accurate
- Add newly discovered tasks
- Update SESSION.md if token usage >50% (handoff protocol)

---

## Quality Gates (Per Parent Task)

### For Framework Infrastructure Tasks (CORE)

**Before marking complete:**
1. **Linter:** `flake8 framework/ tests/` (or `pylint`)
   - No errors, warnings acceptable if justified
2. **Type checker:** `mypy framework/` (if using type hints)
   - No type errors
3. **Unit tests:** `pytest tests/unit/` (if testing framework code)
   - All tests pass
4. **Integration tests:** Run sample test using framework
   - Framework infrastructure works as expected

**Example:**
```markdown
**Commands Run:**
```bash
flake8 framework/interfaces/web_interface.py
# No errors found

pytest tests/unit/test_web_interface.py -v
# 8 passed in 2.1s
```

**Results:**
- Linter: Clean
- Unit tests: 8/8 passed
- WebInterface methods working as expected
```

---

### For Test Scenario Tasks (GLUE)

**Before marking complete:**
1. **Test execution:** Run workflow tests
   ```bash
   pytest tests/auth/ -v
   pytest tests/catalog/ -v
   pytest tests/cart/ -v
   pytest tests/checkout/ -v
   ```
2. **Pass rate:** 90%+ tests passing
3. **HTML report:** Generate report for review
   ```bash
   pytest tests/auth/ --html=_reports/auth_report.html --self-contained-html
   ```
4. **Artifacts:** Verify screenshots captured on failure, logs generated

**Example:**
```markdown
**Commands Run:**
```bash
pytest tests/auth/ -v
# tests/auth/test_valid_login.py::test_valid_login PASSED
# tests/auth/test_invalid_credentials.py::test_invalid_credentials PASSED
# tests/auth/test_registration.py::test_registration PASSED
# tests/auth/test_logout.py::test_logout PASSED
# 4 passed in 15.2s

pytest tests/auth/ --html=_reports/auth_report.html --self-contained-html
# Report: _reports/auth_report.html
```

**Results:**
- Pass rate: 100% (4/4)
- Execution time: 15.2s
- All assertions passed
- HTML report generated successfully
```

---

## Token Management & Handoff

### When Token Usage Reaches 50-60%

If a session is long and token usage approaches 50-60%, update `SESSION.md` with:

**Required Information:**
- Current phase (Phase 3 - Task Execution)
- Current parent task (X.0)
- Last completed sub-task (X.Y)
- Next sub-task to resume (X.Z)
- Files modified in this session
- Test execution status (which tests passing/failing)
- Any blockers or issues
- Commands run and results

**See:** Handoff Protocol in `CLAUDE.md` for full template

---

## Execution Flow Example

### Parent Task: Implement Authentication Workflow

```markdown
- [ ] 2.0 Implement Authentication Workflow [GLUE]
  - [ ] 2.1 Create AuthenticationPage class
  - [ ] 2.2 Create RegistrationPage class
  - [ ] 2.3 Implement common_tasks.py
  - [ ] 2.4 Implement test_valid_login.py
  - [ ] 2.5 Implement test_invalid_credentials.py
  - [ ] 2.6 Implement test_registration.py
  - [ ] 2.7 Implement test_logout.py
  - [ ] 2.8 Run checks: pytest tests/auth/
  - [ ] 2.9 Record results in this file
  - [ ] 2.10 Verify "Done When" criteria met
```

**Execution Steps:**

#### Sub-Task 2.1: Create AuthenticationPage
1. AI: Implement `framework/pages/common/authentication_page.py`
2. AI: Mark `[x]` in task list
3. AI: "Sub-task 2.1 complete. Ready to proceed to 2.2? (yes/no)"
4. USER: "yes"

#### Sub-Task 2.2: Create RegistrationPage
1. AI: Implement `framework/pages/common/registration_page.py`
2. AI: Mark `[x]` in task list
3. AI: "Sub-task 2.2 complete. Ready to proceed to 2.3? (yes/no)"
4. USER: "yes"

#### Sub-Task 2.3: Implement common_tasks.py
1. AI: Implement `framework/tasks/common_tasks.py`
2. AI: Mark `[x]` in task list
3. AI: "Sub-task 2.3 complete. Ready to proceed to 2.4? (yes/no)"
4. USER: "yes"

#### Sub-Tasks 2.4-2.7: Implement Tests
1. AI: Implement each test file
2. AI: Mark `[x]` after each
3. AI: Ask permission between each
4. USER: "yes" (repeat for 2.4, 2.5, 2.6, 2.7)

#### Sub-Task 2.8: Run Quality Gates
1. AI: Run `pytest tests/auth/ -v`
2. AI: Verify 4/4 tests pass
3. AI: Generate HTML report
4. AI: Mark `[x]`
5. AI: "All tests passed. Ready for 2.9? (yes/no)"
6. USER: "yes"

#### Sub-Task 2.9: Record Results
1. AI: Paste command output into task list
2. AI: Document pass rate, execution time, artifacts
3. AI: Mark `[x]`
4. AI: "Results recorded. Ready for 2.10? (yes/no)"
5. USER: "yes"

#### Sub-Task 2.10: Verify "Done When"
1. AI: Check all "Done When" criteria:
   - ✅ AuthenticationPage and RegistrationPage implemented
   - ✅ common_tasks.py has login, logout, register methods
   - ✅ 4 authentication tests passing
   - ✅ Tests run reliably (100% pass rate)
   - ✅ Commands + results documented
2. AI: Mark `[x]`
3. AI: All sub-tasks complete!

#### Parent Task 2.0 Completion
1. AI: Clean up temporary files
2. AI: Stage changes: `git add .`
3. AI: Commit with detailed message (HEREDOC format)
4. AI: Mark parent task `[x]`
5. AI: Update TodoWrite tool
6. AI: "Task 2.0 complete. Authentication workflow implemented and all tests passing. Ready to start Task 3.0 (Catalog Workflow)? (yes/no)"
7. USER: "yes"

#### Repeat for Task 3.0, 4.0, 5.0...

---

## Common Issues & Solutions

### Issue 1: Tests Failing
**Symptom:** Test execution shows failures
**Action:**
- Do NOT mark parent task complete
- Do NOT commit changes
- Debug and fix failing tests
- Re-run quality gates
- Only proceed when tests pass

---

### Issue 2: Flaky Tests
**Symptom:** Tests pass sometimes, fail other times
**Action:**
- Identify flaky test
- Add explicit waits (WebDriverWait)
- Improve locators (more stable selectors)
- Re-run 3-5 times to verify stability
- Document known flakiness in task list

---

### Issue 3: Test Environment Down
**Symptom:** automationpractice.pl is unreachable
**Action:**
- Verify site is accessible via browser
- Check internet connection
- Wait for site recovery
- Mark task as BLOCKED in task list
- Update SESSION.md with blocker
- Resume when site is back up

---

### Issue 4: Scope Creep (New Requirements Discovered)
**Symptom:** Realize additional sub-tasks needed
**Action:**
- Add new sub-tasks to parent task (2.8, 2.9, 2.10...)
- Update task list file
- Inform user: "Discovered additional work needed. Added sub-tasks 2.X, 2.Y. Proceed?"
- Continue with new sub-tasks

---

### Issue 5: Implementation Different from Design
**Symptom:** Phase 0 design doesn't match reality (site changed, assumptions wrong)
**Action:**
- Adapt implementation to reality
- Document deviation in task list or SESSION.md
- Inform user of change
- Update Phase 0 design doc if major deviation

---

## Differences from Dev Phase 3

| Aspect | Dev Phase 3 (Task Execution) | QA Phase 3 (Task Execution) |
|--------|------------------------------|------------------------------|
| **Input** | Implementation task list | Test framework task list |
| **Focus** | Build product features | Build test framework + tests |
| **Quality Gates** | Unit tests of product code | Run test scenarios themselves |
| **Success Criteria** | Product code works, tests pass | Tests pass, framework works |
| **Artifacts** | Product code, unit tests | Test code, test reports, screenshots |
| **Commit Message** | Describes feature implemented | Describes tests/framework implemented |

**Key Insight:**
- Dev Phase 3 builds the **product** and verifies with tests
- QA Phase 3 builds the **tests** and verifies by running them

---

## Success Criteria (Phase 3 Complete)

### Overall Project Success
- [ ] All parent tasks marked `[x]`
- [ ] All test scenarios implemented (15 MVP tests)
- [ ] Test pass rate ≥90% (13-15 of 15 tests passing)
- [ ] HTML reports generated
- [ ] All commits follow conventional commit format
- [ ] Git history is clean (no temporary commits)
- [ ] SESSION.md updated (if applicable)

### Framework Success
- [ ] Framework architecture matches Phase 0 design
- [ ] Page objects implemented for all workflows
- [ ] Task methods implemented for all workflows
- [ ] Roles implemented (if applicable)
- [ ] Configuration management working (.env)
- [ ] Test data generation working (Faker + JSON)
- [ ] Fixtures working (driver, web_interface, test_users)

### Test Success
- [ ] 15 tests implemented (4 auth, 4 catalog, 4 cart, 3 checkout)
- [ ] Smoke suite tagged (3 tests)
- [ ] Tests run reliably (90%+ pass rate)
- [ ] Execution time acceptable (<15 minutes full suite)
- [ ] Artifacts captured (screenshots, logs, reports)

### Documentation Success
- [ ] README.md complete (setup, usage)
- [ ] Task list complete with all results documented
- [ ] Relevant files section accurate
- [ ] SESSION.md updated (if handoff needed)

---

## Version History

**v1.0.0** (2025-01-11)
- Initial QA Phase 3 process documentation
- Adapted from 4D Dev Framework Phase 3 (task execution)
- Based on QA test execution and quality gate patterns

---

**For Next QA Project:**
1. Copy this template as guide
2. Read task list generated in Phase 2
3. Execute one sub-task at a time
4. Mark `[x]` after each sub-task
5. Run quality gates after parent task complete
6. Commit with detailed message
7. Mark parent task `[x]`
8. Repeat until all tasks complete
9. Demo prepared, project ready for interview

---

**Questions? Updates?**
This template will evolve. Capture learnings and update as we use it on more QA projects.

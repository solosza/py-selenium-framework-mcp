# Task List Management

Guidelines for managing task lists in markdown files to track progress on completing a PRD

## Task Implementation
- **One sub-task at a time:** Do **NOT** start the next sub‑task until you ask the user for permission and they say "yes" or "y"
- **Completion protocol:**  
  1. When you finish a **sub‑task**, immediately mark it as completed by changing `[ ]` to `[x]`.
  2. If **all** subtasks underneath a parent task are now `[x]`, follow this sequence:
    - **First**: Run the full test suite (`pytest`, `npm test`, `bin/rails test`, etc.)
    - **Only if all tests pass**: Stage changes (`git add .`)
    - **Clean up**: Remove any temporary files and temporary code before committing
    - **Commit**: Use a descriptive commit message that:
      - Uses conventional commit format (`feat:`, `fix:`, `refactor:`, etc.)
      - Summarizes what was accomplished in the parent task
      - Lists key changes and additions
      - References the task number and PRD context
      - Formats the message as a multi-line commit (using git commit to open an editor, or standard newlines), e.g.:

        ```
         Subject: feat: Implement payment validation module (Task 4.0)
   
         Body:
         This commit closes Task 4.0 by completing the core payment validation logic
         using a TDD-driven approach.

         Completed Subtasks:
         - T-4.1: Wrote failing unit tests for card number validation.
         - T-4.2: Implemented regex logic to handle card types (Visa, MC, Amex).
         - T-4.3: Implemented validation for future expiry date.
         - T-4.4: Refactored shared validation logic into a new helper file.
         - T-4.5: Asserted telemetry events are emitted on validation failure.
         
         Relevant Files:
         - src/services/PaymentService.ts
         - src/utils/ValidationHelper.ts
         - src/utils/ValidationHelper.test.ts 
         Related to PRD 0002
        ```
  3. Once all the subtasks are marked completed and changes have been committed, mark the **parent task** as completed.
- Stop after each sub‑task and wait for the user's go‑ahead.

## Task List Maintenance

1. **Update the task list as you work:**
   - Mark tasks and subtasks as completed (`[x]`) per the protocol above.
   - Add new tasks as they emerge.

2. **Maintain the "Relevant Files" section:**
   - List every file created or modified.
   - Give each file a one‑line description of its purpose.

## AI Instructions

When working with task lists, the AI must:

1. Regularly update the task list file after finishing any significant work.
2. Follow the completion protocol:
   - Mark each finished **sub‑task** `[x]`.
   - Mark the **parent task** `[x]` once **all** its subtasks are `[x]`.
3. Add newly discovered tasks.
4. Keep "Relevant Files" accurate and up to date.
5. Before starting work, check which sub‑task is next.
6. After implementing a sub‑task, update the file and then pause for user approval.

---
## Addendum: Execution Gates & PR Flow (supplemental; original process unchanged)

### During execution
- After any sub‑task that changes logic, **run unit tests immediately**.
- Keep the one‑at‑a‑time rule; stop and get confirmation before moving on (per your original file).

### Before marking a parent task complete
- Run formatter check, linter, type checker.
- Run full unit + integration test suite; target coverage on **changed lines** (e.g., ≥ 80%).
- If telemetry is defined in PRD, assert it in tests.
- Record the exact commands and a one‑line result summary in the task list.

### PR workflow (lightweight)
- Open a PR from the feature branch; CI must pass before merge.
- PR template sections to fill: What/Why, Acceptance tests covered, Commands + results, Risks/Rollback, Telemetry notes.
- Merge when CI is green and gates are satisfied.

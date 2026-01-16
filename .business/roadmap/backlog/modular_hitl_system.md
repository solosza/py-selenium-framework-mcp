# Modular HITL System

**Status:** Idea
**Created:** 2026-01-14
**Target Version:** v1.2 (Post-MVP)
**Effort:** 12-15 hours
**Impact:** High (enables all future HITL use cases)

---

## Context

Extracted from Parabank10 production test validation. Currently, HITL (Human-in-the-Loop) confirmation only exists at Step 11 (test execution failures). Other steps that need user confirmation must build their own ad-hoc confirmation logic.

---

## Problem

**Current State:**
- HITL confirmation only exists at Step 11 (test execution failures)
- Other steps that need user confirmation build ad-hoc confirmation logic
- No standardized HITL interface across the workflow
- Each step reinvents the wheel for user approvals

**Examples Where HITL Needed:**
- **Step 2:** Confirm new environment addition to `environment_config.json` (DEF-062)
- **Step 5:** Confirm multi-page scope detection results before POM generation
- **Step 6:** Confirm skeleton code fix before saving POM
- **Step 9:** Confirm test data file creation before test generation
- **Step 11:** Already has HITL for execution failures

**Impact:**
- Inconsistent user experience across steps
- Code duplication for confirmation logic
- No standardized confirmation patterns
- Harder to add HITL to new steps

---

## Proposed Solution

**Vision:** Standardized HITL module accessible by any step

**Proposed Architecture:**
```
mcp_server/
├── tools/
│   ├── hitl/                         ← New modular HITL system
│   │   ├── __init__.py
│   │   ├── hitl_core.py              ← Core confirmation engine
│   │   ├── confirmation_types.py     ← Standard confirmation patterns
│   │   └── templates/                ← Reusable templates
│   │       ├── config_change.py      ← For environment_config.json changes
│   │       ├── code_approval.py      ← For skeleton fixes
│   │       ├── data_creation.py      ← For test data file creation
│   │       └── execution_retry.py    ← Step 11 execution failures
│   ├── gates/
│   │   ├── qg_user_input.py          ← Can call HITL for confirmations
│   │   ├── qg_discovered_elements.py ← Can call HITL for scope confirmation
│   │   ├── qg_page_object.py         ← Can call HITL for skeleton fixes
│   │   ├── qg_test_runner.py         ← Can call HITL for data creation
│   │   └── qg_execution.py           ← Already uses HITL (refactor to use core)
```

**Standard Interface:**
```python
from tools.hitl import request_confirmation

# Any gate can use it
result = request_confirmation(
    confirmation_type="config_change",     # Template to use
    context={
        "file": "environment_config.json",
        "action": "add_environment",
        "proposed_change": {
            "env_id": "parabank",
            "url": "https://parabank.parasoft.com/parabank"
        }
    },
    options=[
        {"id": "approve", "label": "Yes, add it"},
        {"id": "modify", "label": "Let me change the name"},
        {"id": "reject", "label": "No, I'll add it manually"}
    ]
)

# Returns: {"action": "approve|modify|reject", "user_input": {...}}
```

---

## Value

**Benefits:**
- ✅ Single reusable HITL system across all steps
- ✅ Consistent confirmation UX
- ✅ Standard templates reduce boilerplate
- ✅ Easy to add HITL to new steps
- ✅ Centralized logging of user decisions
- ✅ Audit trail of all confirmations

**Platform Impact:**
- **QA Vertical:** Steps 2, 5, 6, 9, 11 use modular HITL
- **Consumer Vertical:** User approves rule interpretations
- **Agent Management:** Approve protocol deviations
- **Enterprise:** Compliance approvals for EU AI Act

---

## Implementation Plan

1. Extract Step 11 HITL logic into `hitl_core.py`
2. Define standard confirmation templates
3. Refactor Step 11 to use modular system
4. Add HITL to Step 2 (environment config - DEF-062)
5. Add HITL to Step 5 (scope confirmation)
6. Add HITL to Step 6/7/8 (skeleton fixes)
7. Add HITL to Step 9 (test data creation)

---

## Related Issues

- **DEF-062:** Environment flag auto-detection needs HITL for config changes

---

## Next Steps

1. Move to `.business/roadmap/backlog/` when ready to implement
2. Create PRD with detailed API design
3. Implement following 4D framework

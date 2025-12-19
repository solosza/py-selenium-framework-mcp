---
name: dialogue-engine
description: Global interaction protocol for all conversations. Controls response structure, question format, and topic management. READ THIS SKILL after every user interaction.
---

# Dialogue Engine

**Purpose:** Enforce consistent, user-controlled interaction patterns across all conversations.

**Applies to:** Every conversation, every response.

---

## Checkpoint (Run After Every User Message)

1. **STOP** - Do not respond immediately
2. **READ** - Check applicable references:
   - `references/response-protocol.md` - Response structure rules
   - `references/question-format.md` - If asking questions
   - `references/checkpoint-triggers.md` - What action to take
   - `references/topic-queue.md` - If multiple topics pending
3. **EVALUATE** - Does interaction fit existing categories?
   - No → Propose new reference (with rationale), await user approval
4. **RESPOND** - Following all applicable rules

---

## Quick Rules (Always Apply)

- One topic at a time
- Number all options (1, 2, 3... then a, b, c for sub-items)
- User can respond with just a number
- Never create new reference categories without user approval

---

## References

| File | Purpose |
|------|---------|
| `response-protocol.md` | How to structure every response |
| `question-format.md` | How to ask questions |
| `checkpoint-triggers.md` | When to stop and check |
| `topic-queue.md` | Managing multiple topics |
| `task-execution.md` | Stop after each task, await confirmation |
| `formatting-rules.md` | Tables over bullets, ASCII visuals |

---

*Living document - update as new patterns emerge with user approval.*

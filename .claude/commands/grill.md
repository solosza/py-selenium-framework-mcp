# Grill - Adversarial Review

Critical analysis of current work. Use after any implementation, spec, or decision.

## Instructions

Identify what's being grilled (implementation, spec, design, tasks) from recent context.

**Execute:**
```
GRILL MODE

Analyzing [what's being reviewed]...

CRITICAL ISSUES:
- [Issue 1]: [Why it's a problem]
- [Issue 2]: [Why it's a problem]

EDGE CASES UNHANDLED:
- [Case 1]: [What could happen]
- [Case 2]: [What could happen]

FAILURE MODES:
- [How this breaks under condition X]
- [How this breaks under condition Y]

SECURITY/RISK:
- [Any security concerns]
- [Any data/privacy risks]

WHAT YOU'RE IGNORING:
- [Assumption that might be wrong]
- [Constraint not addressed]

VERDICT: [Clean / Minor Issues / Needs Rework]
```

**HITL:**
```
GRILL COMPLETE

1. Address issues and continue
2. Issues are acceptable - proceed anyway
3. Need elegant solution (fundamental rethink)

Select (1-3):
```

If Option 3, invoke `/elegant` flow.

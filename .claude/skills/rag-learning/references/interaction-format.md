<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Interactive Lesson & Experiment Format

Detailed guide for running interactive, AI-guided lessons with hands-on experiments.

## Core Principles

| # | Principle | Description |
|---|-----------|-------------|
| 1 | Numbered options | User can respond with just a number |
| 2 | Last option = question | Always allow open-ended questions |
| 3 | Clarify before proceeding | Ask if concepts need explanation |
| 4 | Pause between steps | Don't rush through |
| 5 | Key terms first | Define vocabulary before using it |
| 6 | Summarize at end | Every lesson ends with key takeaways |

## Formatting Rules (MANDATORY)

### Always Use Tables

| Data Type | Format | Example |
|-----------|--------|---------|
| Key Terms | Markdown table | `\| Term \| Definition \|` |
| Options/Trade-offs | Markdown table | `\| Option A \| Option B \|` |
| Parameters | Markdown table | `\| Param \| Value \| Purpose \|` |
| Results | Markdown table | `\| Metric \| Predicted \| Actual \|` |
| Comparisons | Markdown table | `\| Ours \| Framework \|` |

**NEVER use bullet lists for structured data:**

```
BAD (bullet list):
- Boundary - Where a chunk cuts the text
- Hard boundary - Fixed position cut
- Soft boundary - Respects natural breaks

GOOD (table):
| Term | Definition |
|------|------------|
| Boundary | Where a chunk cuts the text |
| Hard boundary | Fixed position cut |
| Soft boundary | Respects natural breaks |
```

### Always Include ASCII Visuals

Every AI response should include ASCII art/diagrams when it helps explain the concept.

```
GOOD CUT (at sentence):         BAD CUT (mid-sentence):
┌─────────────────────┐         ┌─────────────────────┐
│ The fox jumps over  │         │ The fox jumps over  │
│ the lazy dog.       │         │ the laz             │
└─────────────────────┘         └─────────────────────┘
                                ┌─────────────────────┐
                                │ y dog.              │
                                └─────────────────────┘
```

**Visual types to use:**

| Concept | Visual Style |
|---------|--------------|
| Boundaries/cuts | Box diagrams with `┌─┐└─┘` |
| Flow/sequence | Arrow diagrams `→` |
| Comparison | Side-by-side boxes |
| Structure | Tree with `├──` and `└──` |
| Data chunks | `[████████]` blocks |

### Every Response Includes

```
┌─────────────────────────────────────┐
│  1. Tables for structured data      │
│  2. ASCII visuals for concepts      │
│  3. Both when helpful               │
└─────────────────────────────────────┘
```

## Lesson Structure

```
LESSON N: [Topic Name]
│
├── 1. Key Terms (table format)
├── 2. Concepts to Understand (visuals + tables)
├── 3. Experiment N.1 (hands-on test)
├── 4. Key Points to Remember (summary visual)
└── [Optional] Experiment N.2 (deeper dive)
```

## Section Templates

### Section 1: Lesson Opening (Key Terms + Concepts)

```markdown
---
# LESSON N: [Topic Name]

## 1. Key Terms

| Term | Definition |
|------|------------|
| Term 1 | Simple, clear definition |
| Term 2 | Simple, clear definition |
| Term 3 | Simple, clear definition |

## 2. Concepts to Understand

### [Concept Heading]

[Brief explanation]

```
ASCII VISUAL ILLUSTRATING THE CONCEPT
```

### [Second Concept Heading]

| Column A | Column B | Column C |
|----------|----------|----------|
| Data | Data | Data |

```
ANOTHER VISUAL IF HELPFUL
```

---

**Are any of these concepts unclear?**

1. "Explain [Term/Concept 1] more"
2. "Explain [Term/Concept 2] more"
3. "All clear, continue to experiment"
4. "I have a different question"
```

### Section 2: Experiment Introduction + Prediction

```markdown
---
## 3. Experiment N.1: [Experiment Name]

**What this tests:** [One sentence]

```
VISUAL SHOWING WHAT WE'RE TESTING
```

| Parameter | Value | Purpose |
|-----------|-------|---------|
| param1 | value | reason |
| param2 | value | reason |

**My predictions:**

| What I'm Measuring | Prediction | Reasoning |
|--------------------|------------|-----------|
| Metric A | X | Because... |
| Metric B | Y | Because... |

---

**What's YOUR prediction?**

1. "I agree with your predictions"
2. "I think [X] will be different because..."
3. "I have no idea what to expect"
4. "I have a different question"
```

### Section 3: Parameter Adjustment

```markdown
---
**Current experiment parameters:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| chunk_size | 60 | Force multiple cuts |
| overlap | 10 | See boundary recovery |

```
VISUAL OF PARAMETER EFFECT (if helpful)
```

---

**Want to modify the experiment?**

1. "Run as-is"
2. "Change [parameter] to [value]"
3. "Explain what each parameter does"
4. "I have a different question"
```

### Section 4: Run Experiment

```markdown
---
**Running experiment...**

```
[ACTUAL OUTPUT FROM CODE]
```

---

**Results ready. How to proceed?**

1. "Show me your analysis"
2. "Show raw output again"
3. "What do these numbers mean?"
4. "I have a different question"
```

### Section 5: Analysis

```markdown
---
## Analysis

**Prediction vs Reality:**

| Metric | Predicted | Actual | Result |
|--------|-----------|--------|--------|
| A | X | X' | Hit/Miss |
| B | Y | Y' | Hit/Miss |

```
VISUAL SHOWING WHAT HAPPENED

Example:
Chunk 1: [████████████]
Chunk 2:      [████████████]  ← overlap zone
Chunk 3:           [████████████]
```

**Key observations:**

| # | Observation |
|---|-------------|
| 1 | What we saw |
| 2 | Why it matters |
| 3 | Implication |

---

**What patterns do you notice?**

1. "I see [specific pattern]"
2. "Why did [X] happen?"
3. "I don't see any patterns"
4. "I have a different question"
```

### Section 6: Discussion

```markdown
---
**Discussion**

[Response to user's observation]

| Scenario | Recommendation | Why |
|----------|----------------|-----|
| Case A | Option 1 | Reason |
| Case B | Option 2 | Reason |

```
VISUAL IF IT HELPS EXPLAIN
```

---

**What would you like to explore?**

1. "Run another experiment with different parameters"
2. "How does this apply to [use case]?"
3. "I'm ready for the key takeaways"
4. "I have a different question"
```

### Section 7: Lesson Summary

```markdown
---
## 4. Key Points to Remember

```
LESSON N SUMMARY
================

[ASCII VISUAL summarizing the main concept]

┌─────────────────────────────────────────────┐
│  Key Takeaway 1: [Most important point]     │
│  Key Takeaway 2: [Practical application]    │
│  Key Takeaway 3: [Pitfall to avoid]         │
└─────────────────────────────────────────────┘
```

| Takeaway | Application |
|----------|-------------|
| Point 1 | When/how to use |
| Point 2 | When/how to use |
| Point 3 | What to avoid |

---

**Ready to continue?**

1. "Yes, continue to Lesson [N+1]"
2. "Run another experiment first"
3. "I have questions about this lesson"
4. "Save progress and take a break"
5. "I have a different question"
```

## Interaction Flow Summary

| Section | User Sees | Includes | Pause For |
|---------|-----------|----------|-----------|
| 1. Opening | Key Terms + Concepts | Tables + Visuals | Clarification |
| 2. Experiment Intro | Setup + AI Prediction | Tables + Visual | User prediction |
| 3. Parameters | Current values | Table | Adjustments |
| 4. Run | Raw output | Code output | Ready for analysis |
| 5. Analysis | Prediction vs Reality | Table + Visual | User observations |
| 6. Discussion | Response + context | Table + Visual | Exploration |
| 7. Summary | Key Points | Summary visual + Table | Next lesson |

## Handling User Responses

| User Does | AI Does |
|-----------|---------|
| Picks a number | Execute that option immediately |
| Picks "I have a different question" | Wait for question, answer, return to menu |
| Gives custom response | Address input, offer to continue |

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Use bullet lists for definitions | Use markdown tables |
| Skip visuals | Include ASCII art when helpful |
| Rush through steps | Pause for user input |
| Assume understanding | Offer clarification proactively |
| Use more than 5-6 options | Keep menus scannable |
| Forget question option | Last option always open-ended |

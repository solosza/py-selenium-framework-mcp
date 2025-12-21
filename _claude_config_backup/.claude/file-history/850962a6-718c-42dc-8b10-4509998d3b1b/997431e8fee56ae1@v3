# Interactive Lesson & Experiment Format

Detailed guide for running interactive, AI-guided lessons with hands-on experiments.

## Core Principles

1. **Numbered options** - User can respond with just a number
2. **Last option = question** - Always allow open-ended questions
3. **Clarify before proceeding** - Ask if concepts need explanation
4. **Pause between steps** - Don't rush through
5. **Key terms first** - Define vocabulary before using it
6. **Summarize at end** - Every lesson ends with key takeaways

## Lesson Structure

```
LESSON N: [Topic Name]
│
├── Key Terms (define vocabulary)
├── Concepts to Understand (learning objectives)
├── Experiment N.1 (hands-on test)
├── Experiment N.2 (optional deeper dive)
└── Key Points to Remember (takeaways)
```

## Full Lesson Template

### Opening: Key Terms & Concepts

```
# LESSON N: [Topic Name]

## Key Terms

- **[Term 1]** - [Simple, clear definition]
- **[Term 2]** - [Simple, clear definition]
- **[Term 3]** - [Simple, clear definition]

## Concepts to Understand

Before we experiment, you need to understand:

1. **[Concept 1]** - [Why it matters]
2. **[Concept 2]** - [Why it matters]
3. **[Concept 3]** - [Why it matters]

**Framework analogy:** [Relate to testing/QA if applicable]
- [Comparison point 1]
- [Comparison point 2]

---

**Are any of these concepts unclear?**

1. "Explain [Term/Concept 1] more"
2. "Explain [Term/Concept 2] more"
3. "What's the framework analogy about?"
4. "All clear, continue to experiment"
5. "I have a different question"
```

### Experiment Section

```
## Experiment N.1: [Name]

**What this tests:** [One sentence description]

**Trade-offs:**
| Option A | Option B |
|----------|----------|
| Pro | Pro |
| Con | Con |
```

### Step 2: AI PREDICTS

```
**My predictions for [experiment]:**

| Variable | Prediction | Reasoning |
|----------|------------|-----------|
| [A] | [value] | [why] |
| [B] | [value] | [why] |

---

**What's YOUR prediction?**

1. "I agree with your predictions"
2. "I think [X] will be different because..."
3. "I have no idea what to expect"
4. "I don't understand your reasoning"
5. "I have a different question"
```

### Step 3: AI ADJUSTS

```
**Current parameters:**
| Parameter | Value | Purpose |
|-----------|-------|---------|
| [param1] | [val] | [why] |
| [param2] | [val] | [why] |

---

**Want to modify the experiment?**

1. "Run as-is"
2. "Change [parameter] to [new value]"
3. "Add another test case"
4. "Explain what each parameter does"
5. "I have a different question"
```

### Step 4: AI RUNS

```
[Executes experiment, shows output]

---

**Results are ready. How would you like to proceed?**

1. "Show me the full raw output"
2. "Go straight to your analysis"
3. "What do these numbers mean?"
4. "I have a different question"
```

### Step 5: AI ANALYZES

```
**Prediction vs Reality:**

| Variable | Predicted | Actual | Assessment |
|----------|-----------|--------|------------|
| [A] | [pred] | [actual] | [hit/miss] |
| [B] | [pred] | [actual] | [hit/miss] |

**Key insights:**
1. [Observation 1]
2. [Observation 2]
3. [Observation 3]

---

**What patterns do you notice?**

1. "I see [specific pattern]"
2. "I'm curious about [specific data point]"
3. "Why did [X] happen?"
4. "I don't see any patterns"
5. "I have a different question"
```

### Step 6: USER OBSERVES (Discussion)

```
**Discussion time. What would you like to explore?**

1. "What would you recommend for [use case]?"
2. "Show me a concrete example of [X]"
3. "How does this compare to [industry/framework]?"
4. "I'm ready for the next experiment"
5. "I have a different question"
```

### Step 7: SUMMARIZE (End of Lesson)

```
## Key Points to Remember

1. **[Most important takeaway]** - [Why it matters]
2. **[Second takeaway]** - [Practical application]
3. **[Common pitfall]** - [How to avoid]

---

**Ready to continue?**

1. "Yes, continue to Lesson [N+1]"
2. "Run another experiment with different parameters"
3. "I have questions about this lesson"
4. "Take a break, save progress"
5. "I have a different question"
```

**Key Points must include:**
- At least one conceptual takeaway
- At least one practical application
- At least one pitfall to avoid

## Handling User Responses

### When user picks a number
- Execute that option immediately
- No need to confirm

### When user picks "I have a different question"
- Wait for their question
- Answer thoroughly
- Return to the menu with same options

### When user gives a custom response
- Address their input
- Then offer to continue or return to menu

## Common Clarification Patterns

### Concept clarification
```
**You asked about [concept]. Here's a deeper explanation:**

[Detailed explanation]

**Framework analogy:** [Relate to testing/QA if applicable]

---

**Does this clarify it?**

1. "Yes, continue where we left off"
2. "Still confused about [specific part]"
3. "I have a different question"
```

### "Why would anyone choose differently?"
```
**Great question. Here's why different choices make sense:**

| Use Case | Better Choice | Why |
|----------|---------------|-----|
| [Case 1] | [Option A] | [Reason] |
| [Case 2] | [Option B] | [Reason] |

**The real answer:** It depends on [key factor].

---

**Does this clarify the trade-off?**

1. "Yes, makes sense"
2. "Show me a concrete example"
3. "What would you recommend for our case?"
4. "I have a different question"
```

### Framework vs Custom
```
**Our implementation vs [Framework]:**

| Ours | Framework |
|------|-----------|
| `our_method()` | `framework.Method()` |

**Why we built it ourselves:**
- Learning: [benefit]
- Control: [benefit]
- Understanding: [benefit]

---

**Clear on build-to-learn vs use-framework?**

1. "Yes, continue"
2. "When would I use a framework instead?"
3. "Show me more framework examples"
4. "I have a different question"
```

## Anti-Patterns

- **Don't skip options** - Always provide numbered choices
- **Don't assume understanding** - Offer clarification proactively
- **Don't rush** - Wait for user response before proceeding
- **Don't forget the question option** - Last option is always open-ended
- **Don't use more than 5-6 options** - Keep menus scannable

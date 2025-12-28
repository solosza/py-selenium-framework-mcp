<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Formatting Rules (MANDATORY)

## Always Use Tables

| Data Type | Format | Example |
|-----------|--------|---------|
| Key Terms | Markdown table | `| Term | Definition |` |
| Options/Trade-offs | Markdown table | `| Option A | Option B |` |
| Parameters | Markdown table | `| Param | Value | Purpose |` |
| Results | Markdown table | `| Metric | Predicted | Actual |` |
| Comparisons | Markdown table | `| Ours | Framework |` |

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

## Always Include ASCII Visuals

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

## Every Response Includes

```
┌─────────────────────────────────────┐
│  1. Tables for structured data      │
│  2. ASCII visuals for concepts      │
│  3. Both when helpful               │
└─────────────────────────────────────┘
```

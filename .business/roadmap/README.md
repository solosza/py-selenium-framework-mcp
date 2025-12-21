# Roadmap

Product development pipeline.

## Workflow

```
ideas/      → Raw capture, "don't forget this"
    │
    ▼ (when picked up)
backlog/    → Committed, will implement
    │
    ▼ (create PRD, implement)
DONE
```

## Folders

| Folder | Purpose | Action |
|--------|---------|--------|
| `ideas/` | Parking lot for future features | Create MD when idea emerges |
| `backlog/` | Picked up, ready to work | Move from ideas/, create PRD |

## File Format

Each idea/backlog item is a markdown file with:
- Status (Idea / Backlog / In Progress)
- Created date
- Context (where the idea came from)
- Problem / Idea / Value
- Next steps

## Moving Items

When picking up an idea:
1. Move file from `ideas/` to `backlog/`
2. Update status to "Backlog"
3. Create PRD if complex
4. Implement following 4D framework

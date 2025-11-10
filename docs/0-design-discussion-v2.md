# Phase 0: Design Discussion

## Goal

To guide conversational design discussions between user and AI before creating PRDs for features or modules. This phase focuses on UX/UI workflows and user-facing decisions while trusting implementation details to the AI.

## When to Use This Phase

**Use Phase 0 for:**
- New features or modules that need architectural decisions
- Features with multiple design approaches to evaluate
- User-facing changes where UX/UI matters significantly
- Complex features where discussing options before writing PRD saves time
- Features that integrate with existing modules (discuss integration patterns first)

**Skip Phase 0 for:**
- Trivial features with obvious implementation (go straight to PRD)
- Bug fixes or minor enhancements (no design discussion needed)
- Features where requirements are crystal clear and unambiguous

**Advanced Use Case:**
For large features with multiple interdependent modules/components, consider designing them TOGETHER as a system (one Phase 0 discussion) before building individually. This prevents integration issues by ensuring data flow and interfaces align.

## Phase 0 Output

**Format:** Conversational discussion in Claude Code chat (NO separate markdown file created)

**Outcome:** Design decisions documented in chat, ready to feed into Phase 1 (PRD creation)

## Process

### Step 1: AI Presents Design Proposal

For each feature/module (or group of related components), AI presents:

1. **Purpose & Scope**
   - What does this module do?
   - What problems does it solve?
   - What is explicitly OUT of scope?

2. **User-Facing Elements (FOCUS HERE)**
   - What does the user see?
   - What can the user click/interact with?
   - What data is displayed and how?
   - What are the user workflows? (step-by-step)
   - What feedback does the user get?

3. **Design Options**
   - Option A: [Description, pros, cons]
   - Option B: [Description, pros, cons]
   - Recommendation: [Which option and why]

4. **Integration Points**
   - What other modules does this interact with?
   - What data flows in/out?
   - Any dependencies or constraints?

5. **Open Questions**
   - What decisions need user input?
   - What tradeoffs should user be aware of?

### Step 2: Discussion

User and AI discuss:
- Clarify user workflows and interactions
- Evaluate design options and tradeoffs
- Make decisions on UX/UI elements
- Adjust scope if needed
- Address open questions

**User focuses on:**
- UX/UI workflows (what user sees and does)
- User experience and interactions
- Data presentation and visualization
- Feature priorities and scope

**AI handles (user trusts Claude):**
- Implementation details
- Database schemas
- API structure
- Algorithms and logic
- Performance optimization

### Step 3: Finalize Design Decisions

Once discussion is complete, AI summarizes:
- Key design decisions made
- Chosen options and rationale
- Confirmed scope
- User workflows agreed upon
- Any constraints or risks

### Step 4: User Approval

User responds with "approved" or "go" → Proceed to Phase 1 (PRD creation)

## Integration with 3-Step Feature Development Process

```
Phase 0: Design Discussion (NEW - conversational, no file)
    ↓
    User says "approved"
    ↓
Phase 1: PRD Generation (docs/create-prd-v2.md)
    ↓
Phase 2: Task Generation (docs/generate-tasks-v2.md)
    ↓
Phase 3: Task Execution (docs/process-task-list-v2.md)
```

**How Phase 0 feeds into Phase 1:**
- PRD captures design decisions from Phase 0 conversation
- PRD clarifying questions focus on requirements (NOT architecture - already decided)
- No redundant documentation needed

## Advanced Use Case: System Design (Multiple Related Components)

When building a feature with multiple interdependent modules/components, design them as a complete system in ONE Phase 0 discussion before building individually.

**Example:** Building a data processing pipeline with 4 components:
1. Data Ingestion Module (foundation)
2. Data Validation Module (foundation)
3. Data Transformation Module (uses 1 & 2)
4. Data Storage Module (uses 2 & 3)

**Why design together:**
- Prevents integration issues between components
- Ensures clean data flow across entire system
- Aligns module interfaces and contracts early
- Validates dependencies make sense before coding

**Discussion focuses on:**
- How data flows between modules
- What APIs/interfaces each module exposes
- What data structures are shared
- How different parts of the system interact

**After system design is approved:**
Build each module individually using full 4-phase process (Phase 0 → Phase 1 → Phase 2 → Phase 3 per module)

## Example: Phase 0 for User Dashboard Feature

### AI Proposal:

**Purpose & Scope:**
Dashboard showing user's key metrics and activity. User views stats, filters data, and takes quick actions.

**User-Facing Elements:**

Option A: Card-based layout
- Metric cards in grid (2-3 columns)
- Click card → expanded view
- Filter toolbar at top
- Recent activity feed on right sidebar

Option B: Single-page scroll layout
- Metrics at top (horizontal cards)
- Charts/graphs in middle section
- Activity feed at bottom
- Sticky filters in header

**Recommendation:** Option A (card-based) - better information hierarchy, easier to scan

**Open Questions:**
1. Should filters apply globally or per-card?
2. Show real-time updates or refresh on demand?
3. Which metrics are most important to show first?

### User Response:
"Card layout works. Filters should apply globally to all cards. Real-time updates for critical metrics only (not all). Prioritize: total users, revenue, active sessions."

### AI Summary:
Design decisions:
- Card-based layout (grid)
- Global filters (apply to all cards)
- Real-time updates for: users, revenue, sessions only
- Other metrics: refresh on demand
- Priority order: users → revenue → sessions

User: "approved"

→ Proceed to Phase 1 (PRD creation for User Dashboard)

## AI Instructions

When conducting Phase 0 design discussions:

1. **Present designs visually** - Use text diagrams, bullet points, clear structure
2. **Focus 80% on UX/UI** - User cares about what they see and interact with
3. **Provide recommendations** - Don't just list options, suggest the best path
4. **Highlight tradeoffs** - Be honest about pros/cons (use Truth Filter if available)
5. **No separate files** - Keep discussion in chat, capture decisions in PRD later
6. **For system design** - Design related components as integrated system in one discussion
7. **For single features** - Design one at a time
8. **Wait for approval** - Don't proceed to PRD until user says "approved" or "go"

## Target Audience

Assume the user:
- Cares deeply about UX/UI and user workflows
- Trusts AI to handle implementation details
- Wants to make informed decisions with clear options
- Values efficiency (no redundant documentation)

---

**Status:** This process is project-agnostic and can be used for any feature or module in any project.

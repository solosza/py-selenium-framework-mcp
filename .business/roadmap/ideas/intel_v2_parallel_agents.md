---
description: Run daily competitive intelligence scan for AI execution governance space (v2.1)
---

# Competitive Intelligence Scan

Run the Isagawa Competitive Intelligence Monitoring Prompt (v2.1).

## Execution Pattern: Inspection Team (Parallel)

This scan uses the Isagawa Inspection Team pattern. See `.business/architecture/execution_patterns.md`.

**Non-bypassable enforcement:** All 8 category agents must complete before report generation.

---

## Phase 1: Dispatch Parallel Agents

Spawn 8 parallel agents using the Task tool. Each agent searches ONE category.

**CRITICAL INSTRUCTION FOR ALL AGENTS:**
- Search queries below are EXAMPLES, not limits
- Expand searches to ensure comprehensive coverage
- Use variations, synonyms, adjacent terms
- Do NOT limit to examples provided
- Goal: Cast wide net, miss nothing

---

### Agent 1: Direct Competitors
**Goal:** Find ANY company/product that could compete with Isagawa

Example searches (EXPAND THESE):
- "AI governance platform [year]"
- "AI agent management platform [year]"
- "AI execution control [year]"
- "AI workflow enforcement [year]"
- "AI oversight platform enterprise [year]"
- "agentic AI governance [year]"

Also search for:
- New product launches, announcements
- Startups in adjacent spaces
- Big tech entries into governance

---

### Agent 2: Feature Convergence
**Goal:** Find features being added to existing platforms that overlap with Isagawa

Example searches (EXPAND THESE):
- "AI agent orchestration features [year]"
- "AI governance new capabilities [year]"
- "multi-agent coordination platform [year]"
- "AI runtime control features [year]"
- "human-in-the-loop AI platform [year]"

Also search for:
- Product updates from major vendors
- New integrations announced
- Feature roadmaps published

---

### Agent 3: Enterprise Adoption
**Goal:** Find how enterprises are adopting AI governance across ALL verticals

Example searches (EXPAND THESE):
- "AI governance enterprise adoption [year]"
- "AI agent deployment case study [year]"
- "AI workflow automation enterprise [year]"
- "enterprise AI oversight implementation [year]"

Vertical-specific (examples, not limits):
- Healthcare, Finance, Construction Management
- Legal, Insurance, Government
- Any industry adopting AI governance

---

### Agent 4: Regulatory & Standards
**Goal:** Find ALL regulatory movements affecting AI governance globally

Example searches (EXPAND THESE):
- "AI regulation [year]"
- "AI compliance requirements [year]"
- "AI governance standards [year]"
- "AI agent regulation [year]"
- "AI oversight law [year]"

Also search for:
- New laws passed or proposed
- Industry standards emerging
- Compliance deadlines
- Global (EU, US, UK, APAC, etc.)

---

### Agent 5: Developer & Open Source
**Goal:** Find developer tools, frameworks, and open source projects in AI governance space

Example searches (EXPAND THESE):
- "GitHub AI governance [year]"
- "AI agent framework trending [year]"
- "open source AI orchestration [year]"
- "AI guardrails framework [year]"
- "LangChain LlamaIndex governance [year]"

Also search for:
- New repos gaining stars
- Framework updates
- Developer community trends
- Hugging Face models/spaces

---

### Agent 6: Marketplace & Ecosystem
**Goal:** Find marketplace activity, integrations, ecosystem developments

Example searches (EXPAND THESE):
- "AI governance marketplace [year]"
- "GPT Store governance [year]"
- "MCP server ecosystem [year]"
- "AI agent marketplace [year]"
- "cloud AI governance solutions [year]"

Also search for:
- AWS, Azure, GCP marketplace listings
- Integration partnerships announced
- Ecosystem plays by major vendors
- API/plugin ecosystems forming

---

### Agent 7: Community & Social
**Goal:** Find community sentiment, discussions, hiring signals

Example searches (EXPAND THESE):
- "AI governance" site:youtube.com
- "AI agent management" site:reddit.com
- "AI governance" site:news.ycombinator.com
- "AI governance jobs [year]"
- "AI oversight hiring [year]"

Also search for:
- YouTube tutorials, demos, reviews
- Reddit/HN discussions and sentiment
- LinkedIn job postings and trends
- Conference talks, podcasts
- Influencer opinions

---

### Agent 8: Funding & Market
**Goal:** Find funding activity, market sizing, M&A in AI governance space

Example searches (EXPAND THESE):
- "AI governance startup funding [year]"
- "AI governance market size [year]"
- "AI agent platform investment [year]"
- "AI governance acquisition [year]"
- "AI oversight venture capital [year]"

Also search for:
- Recent funding rounds (any stage)
- Market reports and forecasts
- Acquisitions and mergers
- Analyst predictions

---

## Phase 2: Aggregation Gate

**GATE REQUIREMENT:** Do NOT proceed until all 8 agents have returned results.

Verify coverage:
- [ ] Agent 1: Direct Competitors - COMPLETE
- [ ] Agent 2: Feature Convergence - COMPLETE
- [ ] Agent 3: Enterprise Adoption - COMPLETE
- [ ] Agent 4: Regulatory & Standards - COMPLETE
- [ ] Agent 5: Developer & Open Source - COMPLETE
- [ ] Agent 6: Marketplace & Ecosystem - COMPLETE
- [ ] Agent 7: Community & Social - COMPLETE
- [ ] Agent 8: Funding & Market - COMPLETE

**If any agent failed or returned empty:** Re-run that agent before proceeding.

---

## Phase 3: Generate Report

Only after Phase 2 gate passes, generate the full report using this EXACT format:

### Output Format Template:

# Isagawa Competitive Intelligence Report
## YYYY-MM-DD (Fresh Scan)

---

## Executive Summary

| Metric | Score |
|--------|-------|
| Overall Threat | **X/10** |
| Overall Validation | **X/10** |
| Net Market Signal | **Favorable/Neutral/Concerning** |

---

## Overlapping Tools (Not Direct Competitors)

| Tool | What They Do | Overlap | What They DONT Do |
|------|--------------|---------|-------------------|
| [Name] | [Function] | [Overlap area] | [Gap vs Isagawa] |

---

## Closest Rival: [Name]

**Threat Score: X/10**

Why closest:
- [Reason 1]
- [Reason 2]
- [Reason 3]

| Feature | [Rival] | Isagawa |
|---------|---------|---------|
| Step-by-step workflow | No/Yes | Yes |
| Non-bypassable gates | No/Yes | Yes (mandatory) |
| Human escalation triggers | Limited/None | Core feature |
| Non-tech verticals | No | Yes |
| Standalone product | No/Yes | Yes |

---

## Second Closest: [Name]

**Threat Score: X/10**

Why close:
- [Reason 1]
- [Reason 2]

Gap: [Brief gap description]

---

## Gap: What NO Competitor Offers

- Step-by-step execution enforcement
- Non-bypassable gates (mandatory)
- Human escalation triggers (built-in)
- Non-tech vertical specialization
- Management layer (not security)
- Vendor agnostic

---

## Key Regulatory Tailwinds

| Regulation | Effective | Validation |
|------------|-----------|------------|
| [Name] | [Date] | X/10 |

---

## GTM by Vertical

**Tech:** [One-liner positioning]
**Healthcare:** [One-liner positioning]
**Finance:** [One-liner positioning]
**Construction Management:** [One-liner positioning]

---

*Report: YYYY-MM-DD*

---

## Phase 4: Save Report

Save to: .business/intel_reports/competitive_intel_YYYY-MM-DD.md

---

## Phase 5: Terminal Summary

After saving, display ONLY this concise terminal summary (NOT the full report):

=== ISAGAWA INTEL SUMMARY (YYYY-MM-DD) ===

THREAT LEVEL: X/10
VALIDATION:   X/10
NET SIGNAL:   Favorable/Neutral/Concerning

TOP THREATS:
1. [Rival Name] (X/10) - [One line why]
2. [Rival Name] (X/10) - [One line why]

KEY VALIDATION:
- [Regulation/Trend] (X/10 validation)
- [Regulation/Trend] (X/10 validation)

GAPS NO ONE FILLS:
- [Gap 1]
- [Gap 2]

Report saved: .business/intel_reports/competitive_intel_YYYY-MM-DD.md

**Focus on:** Who is getting close + market validation signals

---

## Context

Isagawa is an AI Management Layer implemented through domain-specific Execution Engines. It enforces how AI executes work, not just what it produces.

**Key differentiators to monitor against:**
- Execution enforcement (not just observation)
- Step-by-step workflow control (not just input/output validation)
- Human escalation triggers (not just alerts)
- Non-bypassable gates (not just recommendations)
- Works across tech AND non-tech verticals

**Target verticals:**
- Tech (QA, DevOps, etc.)
- Healthcare
- Finance
- Construction Management

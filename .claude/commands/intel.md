---
description: Run daily competitive intelligence scan for AI execution governance space (v2.1)
---

# Competitive Intelligence Scan

Run the Isagawa Competitive Intelligence Monitoring Prompt (v2.1).

## Instructions

Execute comprehensive web searches across all 8 categories sequentially:

### 1. Direct Competitors
Find ANY company/product competing with Isagawa:
- AI governance platforms, AI agent management platforms
- AI execution control, workflow enforcement
- New product launches, startups in adjacent spaces

### 2. Feature Convergence
Find features being added to existing platforms that overlap:
- AI agent orchestration features
- Multi-agent coordination platforms
- Human-in-the-loop AI platforms
- Product updates from major vendors

### 3. Enterprise Adoption
Find how enterprises are adopting AI governance:
- Case studies across verticals (Healthcare, Finance, Legal, Insurance, Government, Construction)
- Enterprise AI oversight implementations

### 4. Regulatory & Standards
Find regulatory movements affecting AI governance globally:
- New laws passed or proposed (EU, US, UK, APAC)
- Industry standards emerging
- Compliance deadlines

### 5. Developer & Open Source
Find developer tools and frameworks:
- GitHub repos gaining traction
- LangChain, LlamaIndex governance features
- AI guardrails frameworks

### 6. Marketplace & Ecosystem
Find marketplace activity:
- AWS, Azure, GCP marketplace listings
- GPT Store, MCP server ecosystem
- Integration partnerships

### 7. Community & Social
Find community sentiment:
- YouTube, Reddit, HN discussions
- LinkedIn job postings
- Conference talks, podcasts

### 8. Funding & Market
Find funding activity and market sizing:
- Recent funding rounds
- Market reports and forecasts
- Acquisitions and mergers

---

## Report Format

Generate the report using this EXACT format:

```
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
```

---

## Save Report

Save to: `.business/intel_reports/competitive_intel_YYYY-MM-DD.md`

---

## Terminal Summary

After saving, display ONLY this concise terminal summary:

```
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
```

---

## Context

Isagawa is an AI Management Layer implemented through domain-specific Execution Engines. It enforces how AI executes work, not just what it produces.

**CRITICAL: Scan competitors for ALL 5 Isagawa products:**

1. **AI Management Layer** (Enterprise platform)
   - Competitors: AI governance platforms, agent orchestration platforms
   - Examples: Credo AI, Airia, ModelOp, IBM watsonx.governance

2. **QA Execution Engine** (Test automation vertical)
   - Competitors: TestMu AI, mabl, Virtuoso QA, Katalon, Selenium alternatives
   - Examples: Autonomous test generation, AI-augmented testing tools

3. **Consumer Execution Engine** (Personal productivity)
   - Competitors: Personal AI assistants, task automation tools
   - Examples: Notion AI, ClickUp AI, personal workflow automation

4. **AI Agent Management Layer** (Multi-agent orchestration)
   - Competitors: Agent orchestration platforms, multi-agent frameworks
   - Examples: PwC Agent OS, CrewAI, AutoGen, LangGraph

5. **HITL Infrastructure** (Cross-product platform)
   - Competitors: Approval workflow systems, human-in-the-loop platforms
   - Examples: Workato (sandbox testing), enterprise approval workflows

**Report Structure Reference:**

Follow the format from `.business/intel_reports/competitive_intel_consolidated_HITL_2026-01-14.md`:
- One consolidated report covering all 5 products
- Separate threat assessment per product
- Overall threat + validation scores at top
- Product-specific competitor sections in Category 1 (Direct Competitors)

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

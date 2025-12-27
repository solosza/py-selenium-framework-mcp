# Market Intelligence Agent Design Document
*Automated Competitive & Market Intelligence for Isagawa*

**Version:** 1.0 (Draft)
**Status:** Roadmap / Ideas
**Purpose:** Design specification for an AI agent that monitors market trends, competitors, and industry developments, delivering actionable intelligence briefings.

---

## Executive Summary

The Market Intelligence Agent automates the monitoring of sources defined in `market_intelligence_sources.md`, synthesizes findings, and delivers structured briefings to leadership and the CMO Agent. It transforms manual market watching into a continuous, systematic intelligence operation.

**Core Principle:** Every signal has a quality gate. Nothing enters intelligence without verification.

---

## Part 1: Quality Gate Framework

The Market Intelligence Agent enforces quality gates at every stage of the intelligence cycle. This is non-negotiable — it embodies Isagawa's execution engine philosophy.

### 1.1 Gate Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 MARKET INTELLIGENCE QUALITY GATES                        │
├─────────────────────────────────────────────────────────────────────────┤
│  STAGE              │  GATE NAME           │  GATE MUST PASS BEFORE     │
├─────────────────────────────────────────────────────────────────────────┤
│  1. Collection      │  GATE-COLLECT        │  Signal recorded           │
│  2. Verification    │  GATE-VERIFY         │  Signal classified         │
│  3. Classification  │  GATE-CLASSIFY       │  Signal enters analysis    │
│  4. Analysis        │  GATE-ANALYZE        │  Finding added to briefing │
│  5. Synthesis       │  GATE-SYNTHESIZE     │  Briefing finalized        │
│  6. Delivery        │  GATE-DELIVER        │  Briefing sent             │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Gate Definitions

#### GATE-COLLECT: Source Collection
**Must pass before:** Signal is recorded

```
□ Source is from approved source list (market_intelligence_sources.md)
□ Source URL/reference captured
□ Timestamp recorded
□ Raw content preserved
□ Source credibility noted (primary/secondary/community)
□ No duplicate of already-collected signal
```

**If gate fails:** Log source issue, skip signal, note gap

---

#### GATE-VERIFY: Signal Verification
**Must pass before:** Signal is classified

```
□ Content is accessible and readable
□ Content is relevant to Isagawa (not off-topic)
□ Content is current (not stale/outdated news)
□ Claims are verifiable (not speculation without label)
□ Source attribution complete
□ If uncertain: marked as [Unverified]
```

**If gate fails:** Discard signal or mark as unverified

---

#### GATE-CLASSIFY: Signal Classification
**Must pass before:** Signal enters analysis

```
□ Category assigned:
  □ Competitive (direct competitor activity)
  □ Technology (new capabilities, frameworks)
  □ Market (industry shifts, buyer behavior)
  □ Community (developer sentiment, pain points)
  □ Threat (risks to positioning)
  □ Opportunity (gaps, timing windows)
□ Priority assigned:
  □ ALERT (high impact + high certainty → immediate)
  □ BRIEF (include in scheduled briefing)
  □ WATCH (track for pattern emergence)
  □ LOG (record for reference)
□ Entities extracted (companies, products, people)
□ Relevance to Isagawa explained (1 sentence)
```

**If gate fails:** Return to verification or discard

---

#### GATE-ANALYZE: Analysis Quality
**Must pass before:** Finding added to briefing

```
□ Fact vs. interpretation clearly separated
□ Confidence level stated (high/medium/low)
□ Business relevance explained
□ "So what?" answered (why does this matter?)
□ If ALERT: impact and urgency justified
□ Related signals linked (if pattern)
□ No editorializing or advocacy
□ Actionability considered
```

**If gate fails:** Revise analysis or downgrade priority

---

#### GATE-SYNTHESIZE: Briefing Quality
**Must pass before:** Briefing is finalized

```
□ Executive summary present (3-5 bullets, most important)
□ Signals organized by category
□ Priority items highlighted
□ Sources cited for all claims
□ Confidence levels included
□ Actionable recommendations (if appropriate)
□ No duplicates or redundancy
□ Follows briefing template format
□ Appropriate length for cadence (daily = short, weekly = comprehensive)
```

**If gate fails:** Revise briefing structure

---

#### GATE-DELIVER: Delivery Check
**Must pass before:** Briefing is sent

```
□ Correct recipients identified (human, CMO Agent, etc.)
□ Delivery format correct for channel
□ Sensitive information flagged (if any)
□ ALERT items highlighted with urgency markers
□ Handoff context included (for CMO integration)
□ Briefing archived for reference
□ Delivery timestamp logged
```

**If gate fails:** Fix delivery issues before sending

---

### 1.3 Gate Enforcement Rules

**Hard Gates (Cannot Proceed):**
- GATE-VERIFY: Cannot classify unverified signals as fact
- GATE-CLASSIFY: Cannot include in briefing without classification
- GATE-SYNTHESIZE: Cannot send incomplete briefing

**Soft Gates (Can Proceed with Flag):**
- GATE-COLLECT: Can note source issues and continue
- GATE-ANALYZE: Can include with [Low Confidence] flag

**Escalation Triggers:**
- ALERT-level signal → immediate notification (bypass normal cadence)
- Source reliability concern → flag for human review
- Pattern of failed gates → review source list quality
- Critical intelligence gap → escalate to Chief of Staff

### 1.4 Gate Checklist Quick Reference

```
QUICK GATE CARD (for every signal)

□ COLLECT:   Approved source? URL captured? Timestamp? Not duplicate?
□ VERIFY:    Accessible? Relevant? Current? Verifiable? Attributed?
□ CLASSIFY:  Category? Priority? Entities? Relevance explained?
□ ANALYZE:   Fact/interpretation separated? Confidence? So what?
□ SYNTHESIZE: Summary? Organized? Sources cited? Template followed?
□ DELIVER:   Recipients? Format? Archived? Timestamp logged?
```

### 1.5 Signal Quality Standards

**Reliability Indicators:**
| Indicator | High Reliability | Low Reliability |
|-----------|------------------|-----------------|
| Source | Official announcement, GitHub release | Reddit rumor, anonymous post |
| Verification | Multiple sources confirm | Single source only |
| Recency | < 48 hours | > 1 week old |
| Specificity | Named companies, dates, figures | Vague claims, "some say" |

**Confidence Labeling:**
- **High:** Primary source, verified, specific details
- **Medium:** Secondary source, partially verified
- **Low:** Community source, unverified, speculation
- **Unverified:** Cannot confirm, treat as rumor

---

## Part 2: Agent Identity

### 2.1 Role Definition

**Title:** Market Intelligence Agent

**Mission:** Continuously monitor the competitive landscape, technology trends, and industry developments to ensure Isagawa leadership has timely, actionable intelligence for strategic decisions.

**Scope:**
- Source monitoring and data collection
- Signal detection and prioritization
- Intelligence synthesis and summarization
- Briefing generation and delivery
- Trend tracking over time

**Out of Scope:**
- Strategic decision-making (provides intelligence, not recommendations)
- Content creation for marketing (feeds CMO Agent, doesn't publish)
- Sales intelligence (separate function)
- Product roadmap decisions (informs, doesn't decide)

### 1.2 Agent Personality

```
┌─────────────────────────────────────────────────────────────┐
│              MARKET INTELLIGENCE AGENT PERSONA               │
├─────────────────────────────────────────────────────────────┤
│  Voice        │ Objective, analytical, concise              │
│  Tone         │ Neutral, fact-based                         │
│  Style        │ Signal over noise, prioritized findings     │
│  Perspective  │ Strategic analyst, not advocate             │
└─────────────────────────────────────────────────────────────┘
```

**Operating Principles:**
- Report facts, separate from interpretation
- Prioritize by business impact, not recency
- Distinguish signal from noise
- Surface unknowns and gaps
- Never editorialize or advocate

---

## Part 2: Intelligence Framework

### 2.1 Intelligence Categories

| Category | Definition | Priority Triggers |
|----------|------------|-------------------|
| **Competitive** | Direct competitor moves, funding, product launches | Any significant development |
| **Technology** | New capabilities, frameworks, standards | Potential product impact |
| **Market** | Industry shifts, buyer behavior, regulations | Strategic implications |
| **Community** | Developer sentiment, pain points, adoption trends | Pattern emergence |
| **Threat** | Risks to positioning, new entrants, disruption | Any credible threat |
| **Opportunity** | Gaps, unmet needs, timing windows | Actionable openings |

### 2.2 Signal Classification

```
┌─────────────────────────────────────────────────────────────┐
│                    SIGNAL PRIORITY MATRIX                    │
├─────────────────────────────────────────────────────────────┤
│                    │  Low Certainty  │  High Certainty      │
├─────────────────────────────────────────────────────────────┤
│  High Impact       │  WATCH          │  ALERT (immediate)   │
│  Low Impact        │  LOG            │  BRIEF (scheduled)   │
└─────────────────────────────────────────────────────────────┘
```

| Level | Response | Example |
|-------|----------|---------|
| **ALERT** | Immediate notification | Major competitor funding, direct product launch |
| **BRIEF** | Include in next scheduled briefing | Blog post on relevant topic, minor feature |
| **WATCH** | Track for pattern emergence | Rumor, speculation, early signal |
| **LOG** | Record for historical reference | Minor mention, routine update |

### 2.3 Source Hierarchy

```
Primary Sources (highest signal)
├── Official announcements (company blogs, press releases)
├── GitHub releases and changelogs
├── Research papers and documentation
│
Secondary Sources (context and sentiment)
├── Tech publications (TechCrunch, The Verge, etc.)
├── Industry newsletters
├── Conference presentations
│
Community Sources (emerging signals)
├── Hacker News discussions
├── Reddit threads
├── Twitter/X conversations
├── Discord/Slack communities
│
Aggregated Sources (efficiency)
├── Google Alerts
├── RSS feeds
└── Newsletter digests
```

---

## Part 3: Agent Capabilities

### 3.1 Core Functions

| Function | Description | Output |
|----------|-------------|--------|
| **Source Scanning** | Fetch and parse monitored sources | Raw content + metadata |
| **Signal Detection** | Identify relevant items from noise | Classified signals |
| **Entity Extraction** | Identify companies, products, people | Structured entities |
| **Trend Analysis** | Track patterns over time | Trend reports |
| **Synthesis** | Combine signals into intelligence | Briefings |
| **Alerting** | Notify on high-priority signals | Alerts |

### 3.2 Tools & Integrations

**Required Tools:**
```
┌─────────────────────────────────────────────────────────────┐
│              MARKET INTELLIGENCE AGENT TOOLS                 │
├─────────────────────────────────────────────────────────────┤
│  Web Fetch     │ Retrieve web pages, APIs, RSS feeds        │
│  Web Search    │ Query search engines for topics            │
│  Read/Write    │ Access knowledge base, save briefings      │
│  Scheduling    │ Trigger on schedule or event               │
│  Notification  │ Send alerts via configured channels        │
│  Memory        │ Track historical signals for trends        │
└─────────────────────────────────────────────────────────────┘
```

**MCP Tool Mapping:**
| Capability | MCP Tool |
|------------|----------|
| Fetch sources | WebFetch |
| Search queries | WebSearch |
| Read knowledge base | Read, Glob |
| Save briefings | Write |
| GitHub monitoring | WebFetch (GitHub API) |

**External Integrations (Future):**
| Integration | Purpose |
|-------------|---------|
| Slack/Discord | Alert delivery |
| Email | Briefing distribution |
| RSS aggregator | Efficient source monitoring |
| Database | Historical signal storage |

### 3.3 Scheduling

| Cadence | Task | Output |
|---------|------|--------|
| **Continuous** | Alert monitoring (high-priority sources) | Immediate alerts |
| **Daily** | Priority 1 source scan | Daily digest |
| **Weekly** | Full source scan + synthesis | Weekly briefing |
| **Monthly** | Trend analysis + deep dives | Monthly report |
| **On-demand** | Specific topic research | Research memo |

---

## Part 4: Operating Rules

### 4.1 Collection Standards

**Source Quality:**
- Prefer primary sources over aggregators
- Verify claims across multiple sources when possible
- Note source credibility in reporting
- Timestamp all collected information

**Coverage:**
- Check all Priority 1 sources daily
- Rotate through Priority 2/3 sources systematically
- Adjust frequency based on source activity levels
- Flag sources that become inactive or unreliable

### 4.2 Analysis Standards

**Signal Detection:**
- Match against keyword lists and entity lists
- Use semantic similarity for fuzzy matching
- Apply business relevance filter
- Classify by category and priority

**Synthesis:**
- Group related signals
- Identify contradictions or confirmations
- Note confidence levels
- Separate fact from interpretation

### 4.3 Reporting Standards

**Briefing Structure:**
```
1. Executive Summary (3-5 bullets, most important items)
2. Alerts (if any, with full context)
3. Competitive Intelligence (by company)
4. Technology Trends (by theme)
5. Community Signals (notable discussions)
6. Opportunities & Threats
7. Items to Watch
8. Appendix (full signal list)
```

**Quality Gates:**
```
Before delivering any briefing:
□ All claims sourced and linked?
□ Priority classification applied?
□ Fact vs. interpretation clearly marked?
□ Business relevance explained?
□ Actionability considered?
□ Duplicates removed?
```

---

## Part 5: Knowledge Management

### 5.1 Entity Tracking

Maintain structured profiles for key entities:

**Competitor Profile:**
```yaml
company: "Temporal.io"
category: "Execution/Orchestration"
threat_level: "Medium"
last_updated: "2024-01-15"
funding:
  - round: "Series B"
    amount: "$75M"
    date: "2023-02"
products:
  - name: "Temporal Cloud"
    relevance: "Direct competitor for durable execution"
recent_developments:
  - date: "2024-01-10"
    event: "Announced AI workflow features"
    source: "https://..."
    implication: "Moving into AI execution space"
positioning:
  claims: ["Durable execution", "Workflow as code"]
  overlap_with_isagawa: ["Reliable execution", "Developer-focused"]
  differentiation: ["We focus on enforcement, they focus on durability"]
```

### 5.2 Signal History

Store signals for trend analysis:

```yaml
signals:
  - id: "SIG-2024-001"
    date: "2024-01-15"
    category: "competitive"
    priority: "BRIEF"
    source: "https://temporal.io/blog/..."
    title: "Temporal announces AI workflow primitives"
    summary: "New features for AI agent orchestration"
    entities: ["Temporal.io", "AI agents"]
    relevance: "Adjacent to Isagawa positioning"
    related_signals: []
```

### 5.3 Trend Tracking

Aggregate signals into trends:

```yaml
trends:
  - id: "TREND-2024-001"
    name: "AI Agent Reliability"
    status: "Emerging"
    first_observed: "2023-11"
    signal_count: 15
    description: "Growing discussion of reliability challenges in AI agents"
    key_signals: ["SIG-2023-045", "SIG-2024-001"]
    isagawa_relevance: "Core to our thesis - validates market need"
    recommended_action: "Monitor for messaging opportunities"
```

---

## Part 6: Integration Points

### 6.1 CMO Agent Integration

```
┌─────────────────────────────────────────────────────────────┐
│         MARKET INTELLIGENCE → CMO INTEGRATION               │
├─────────────────────────────────────────────────────────────┤
│  Weekly Briefing  → CMO knowledge base update               │
│  Competitor Moves → Messaging adjustment triggers           │
│  Trend Shifts     → Positioning review triggers             │
│  Opportunities    → Campaign ideation input                 │
└─────────────────────────────────────────────────────────────┘
```

**Handoff Format:**
```markdown
## Intelligence Update for CMO Agent
**Date:** [Date]
**Type:** [Weekly/Alert/Special]

### Messaging Implications
- [Finding]: [Suggested messaging adjustment]

### Competitive Updates
| Competitor | Development | Recommended Response |
|------------|-------------|---------------------|

### Content Opportunities
- [Topic]: [Why relevant now]
```

### 6.2 Human Leadership Integration

**Alert Delivery:**
- High-priority alerts → Immediate notification (Slack/email)
- Weekly briefing → Scheduled delivery (Monday AM)
- Monthly report → End of month summary

**Interaction Patterns:**
- Human can request deep-dive on any topic
- Human can adjust priority thresholds
- Human can add/remove sources
- Human approves major entity profile updates

---

## Part 7: Implementation

### 7.1 System Prompt Template

```markdown
# Market Intelligence Agent System Prompt

You are the Market Intelligence Agent for Isagawa, an Execution Engine company.

## Your Mission
Continuously monitor the competitive landscape, technology trends, and industry
developments to provide timely, actionable intelligence for strategic decisions.

## What Isagawa Does
[Insert product summary from marketing brief]

## Your Sources
[Reference market_intelligence_sources.md]

## Intelligence Categories
- Competitive: Direct competitor moves
- Technology: New capabilities affecting our space
- Market: Industry shifts, buyer behavior
- Community: Developer sentiment, pain points
- Threats: Risks to our positioning
- Opportunities: Gaps we can capitalize on

## Signal Priority
- ALERT: High impact + high certainty → Immediate notification
- BRIEF: Include in scheduled briefing
- WATCH: Track for pattern emergence
- LOG: Record for reference

## Operating Rules
- Report facts, separate from interpretation
- Always cite sources
- Prioritize by business impact
- Surface unknowns and gaps
- Never advocate, only inform

## Output Format
[Insert briefing template]

## Current Priorities
[Insert current focus areas]
```

### 7.2 Workflow Automation

**Daily Scan Workflow:**
```
1. Trigger: Scheduled (6 AM)
2. Fetch Priority 1 sources
3. Parse and extract signals
4. Classify by category and priority
5. Check for ALERT-level items
   - If ALERT: Send immediate notification
6. Store signals in history
7. Generate daily digest (if significant items)
8. Update entity profiles as needed
```

**Weekly Briefing Workflow:**
```
1. Trigger: Scheduled (Sunday PM)
2. Aggregate week's signals
3. Group by category
4. Identify trends and patterns
5. Generate weekly briefing
6. Update CMO Agent knowledge base
7. Deliver to human stakeholders
8. Archive briefing
```

### 7.3 Bootstrapping Steps

**Phase 1: Manual Assisted**
1. Human runs source checks using `market_intelligence_sources.md`
2. Human uses briefing template to document findings
3. Learnings inform automation design

**Phase 2: Semi-Automated**
1. Agent fetches sources on command
2. Agent drafts briefings for human review
3. Human edits and approves
4. Agent learns from edits

**Phase 3: Fully Automated**
1. Agent runs on schedule
2. Agent delivers briefings automatically
3. Human reviews and provides feedback
4. Agent self-improves based on feedback

---

## Part 8: Evaluation Metrics

### 8.1 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Signal relevance | 80%+ relevant | Human review sampling |
| False positive rate | <20% | Irrelevant items in briefings |
| Source coverage | 100% Priority 1 | Sources checked vs. listed |
| Timeliness | <24hr for alerts | Time from event to notification |
| Accuracy | 95%+ | Fact-checking sampling |

### 8.2 Value Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Insights actioned | 2+/month | Decisions influenced by intel |
| Blind spots avoided | Qualitative | Threats caught early |
| Time saved | 4+ hrs/week | vs. manual monitoring |
| CMO Agent uplift | Qualitative | Marketing relevance improvement |

---

## Part 9: Example Outputs

### Example 1: Alert

```
🚨 MARKET INTELLIGENCE ALERT
Priority: HIGH
Category: Competitive
Time: 2024-01-15 14:32 UTC

SIGNAL: LangChain announces "LangGraph Orchestration" for enterprise

SOURCE: https://blog.langchain.dev/langgraph-orchestration/

SUMMARY:
LangChain launched LangGraph Orchestration, a managed service for
running multi-agent workflows with built-in reliability features.
Pricing targets enterprise ($500/mo+).

KEY CLAIMS:
- "Durable execution for AI agents"
- "Enterprise-grade reliability"
- "Built-in human-in-the-loop"

RELEVANCE TO ISAGAWA:
Direct overlap with "reliable AI execution" positioning.
They emphasize reliability; we emphasize enforcement/standards.
Differentiation remains intact but messaging clarity is critical.

RECOMMENDED ACTIONS:
1. Review positioning vs. LangGraph messaging
2. Prepare competitive differentiation talking points
3. Monitor enterprise adoption signals

---
Isagawa Market Intelligence Agent
```

### Example 2: Weekly Briefing

```markdown
# Weekly Market Intelligence Briefing
**Week of:** January 8-14, 2024
**Prepared by:** Market Intelligence Agent

---

## Executive Summary

1. **LangChain enterprise push accelerates** - New orchestration product
   positions them closer to our space. Differentiation remains but
   messaging needs sharpening.

2. **"AI reliability" becoming mainstream term** - 12 mentions across
   HN/Reddit this week vs. 3 last week. Validates our thesis.

3. **Temporal quiet** - No significant announcements. May be preparing
   larger release.

4. **QA community pain point: flaky AI tests** - Multiple threads
   discussing AI-generated test instability. Direct opportunity.

---

## Competitive Intelligence

| Competitor | Development | Impact | Our Response |
|------------|-------------|--------|--------------|
| LangChain | Enterprise orchestration launch | Medium | Sharpen differentiation |
| Guardrails AI | New validation rules | Low | Monitor adoption |
| Temporal | No news | — | Continue watching |

---

## Technology Trends

**Emerging: "Durable AI Execution"**
- Temporal, Inngest, and now LangChain using this term
- Focuses on reliability through persistence
- Our angle: Reliability through enforcement, not just durability

**Stable: Agent Frameworks Proliferating**
- CrewAI, AutoGen, custom builds all growing
- More agents = more need for execution governance
- Opportunity: Position as the governance layer

---

## Community Signals

**r/QualityAssurance thread (847 upvotes):**
"Anyone else drowning in AI-generated test maintenance?"
- Top comments cite inconsistency and standards drift
- Direct validation of our QA execution engine value prop

**HN discussion on Claude tool use:**
- Developers praising capabilities, questioning reliability
- Comments about "needing guardrails" common

---

## Opportunities Identified

1. **QA content opportunity** - Write piece addressing AI test maintenance
   pain point. Community clearly hungry for solutions.

2. **Positioning clarification** - "Enforcement" vs. "durability" distinction
   becoming critical. Recommend messaging workshop.

---

## Threats Identified

1. **LangChain ecosystem lock-in** - If developers standardize on LangGraph,
   they may default to LangChain orchestration. Need to ensure we integrate
   or differentiate clearly.

---

## Items to Watch

- LangGraph enterprise pricing finalized (expected this month)
- Temporal Q1 announcements
- Anthropic developer day (March) - potential tool use updates

---

## Appendix: Full Signal List

[Detailed list of all signals collected this week]
```

---

## Appendix: Source Reference

Primary source document: `market_intelligence_sources.md`

Maintain this document as the authoritative list of sources to monitor.
Updates to sources should be logged and reviewed monthly.

---

*End of Document*

---
description: Run daily competitive intelligence scan for AI execution governance space (v2.1)
---

# Competitive Intelligence Scan

Run the Isagawa Competitive Intelligence Monitoring Prompt (v2.1).

## Instructions

1. Read the prompt template from `.business/roadmap/ideas/competitive_intelligence_prompt_v2.md`

2. Execute comprehensive web searches across all 8 categories:
   - Direct Competitor Emergence
   - Feature Convergence
   - Enterprise Adoption Signals
   - Regulatory & Standards Movements
   - Developer & Open Source Signals (GitHub, Hugging Face, LangChain)
   - Marketplace & Ecosystem Activity (GPT Store, MCP, Cloud marketplaces)
   - Community & Social Signals (YouTube, Reddit, HN, LinkedIn jobs)
   - Funding & Market Signals

3. Search for these topics:
   - AI governance / AI management platforms
   - AI trust / trustworthy AI / AI accountability
   - AI oversight / AI compliance / responsible AI
   - Managing AI agents / AI agent management
   - Multi-agent orchestration / agent coordination
   - Execution control planes / runtime enforcement
   - Human-in-the-loop AI / AI checkpoints
   - AI governance in healthcare, finance, and non-tech verticals

4. Generate the full report following the v2.1 template format with:
   - Threat Scores (0-10) for each item
   - Validation Scores (0-10) for regulatory items
   - Net Signal calculations (Tailwind/Neutral/Headwind)
   - 8-category summary table
   - Strategic recommendation

5. Include all sources as markdown hyperlinks at the end.

## Output Format

Follow the exact structure in the prompt template file, including:
- Tables for each monitoring category
- Validation score breakdowns for regulations
- Community sentiment summary table
- Overall assessment matrix
- Priority action items

## Context

Isagawa is an AI Management Layer implemented through domain-specific Execution Engines. It enforces how AI executes work, not just what it produces. Key differentiators to monitor against:
- Execution enforcement (not just observation)
- Step-by-step workflow control (not just input/output validation)
- Human escalation triggers (not just alerts)
- Non-bypassable gates (not just recommendations)
- Works across tech AND non-tech verticals

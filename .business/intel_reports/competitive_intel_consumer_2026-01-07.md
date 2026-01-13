# Consumer Product (Protocol Enforcement) Competitive Intelligence Report
## 2026-01-07 (Fresh Scan)

---

## Executive Summary

| Metric | Score |
|--------|-------|
| Overall Threat | **2/10** |
| Problem Validation | **10/10** |
| Net Market Signal | **Highly Favorable** |

**Key Insight:** The problem is extremely well-documented and NOBODY is solving it. AI instruction-following failures are universal across ChatGPT, Claude, Cursor, and every AI tool. Users are left with workarounds and frustration. The market is wide open for a Protocol Enforcement product.

---

## Problem Validation: The Pain is Real

### ChatGPT Custom Instructions
- "Custom instructions no longer work" - [OpenAI Forum](https://community.openai.com/t/custom-instructions-no-longer-work/1116521)
- "ChatGPT Plus does not take instructions into account" - [OpenAI Forum](https://community.openai.com/t/chatgpt-plus-does-not-take-instructions-into-account/645586)
- "ChatGPT 4 ignoring my custom instructions" - [OpenAI Forum](https://community.openai.com/t/chatgpt-4-ignoring-my-custom-instructions-claims-it-has-no-access/397024)

**Root Cause:** OpenAI's RLHF training makes AI "agreeable" - when instructions conflict with being helpful, it ignores instructions.

### Claude Code / Claude Projects
- [BUG] Claude not following Claude.md / memory instructions - [GitHub #668](https://github.com/anthropics/claude-code/issues/668)
- [BUG] Claude Code ignores most instructions from CLAUDE.md - [GitHub #6120](https://github.com/anthropics/claude-code/issues/6120)
- [BUG] Claude ignores instruction in CLAUDE.MD and agents - [GitHub #7777](https://github.com/anthropics/claude-code/issues/7777)

**Root Cause:** Context window fills up - instructions at the beginning lose importance as conversation grows.

### Cursor IDE Rules
- "CursorRules not being followed or applied" - [Cursor Forum](https://forum.cursor.com/t/cursorrules-not-being-followed-or-applied/131781)
- "Cursor isn't strictly enforcing the rules" - [Cursor Forum](https://forum.cursor.com/t/cursor-isnt-strictly-enforcing-the-rules/108691)
- "AI agent seems to follow its heart instead of your instructions"

**Root Cause:** No enforcement mechanism - rules are suggestions, not requirements.

---

## The Universal Problem Statement

> **Every AI tool has a way to provide instructions. None of them enforce those instructions.**

| AI Tool | Instruction Method | Enforcement | Reality |
|---------|-------------------|-------------|---------|
| ChatGPT | Custom Instructions | None | Ignores after a few prompts |
| Claude.ai | Project Instructions | None | Forgets as context grows |
| Claude Code | CLAUDE.md | None | Bug reports still open |
| Cursor | .cursorrules | None | "Sees rules, ignores them" |
| Copilot | Instructions file | None | Inconsistent application |

---

## Competitor Analysis: Who's Trying to Solve This?

### Direct Competitors: **NONE**

No product specifically targets "Protocol Enforcement for everyday AI users."

### Adjacent Products (Enterprise-Focused)

| Product | What They Do | Why Not a Threat |
|---------|--------------|------------------|
| **Guardrails AI** | Input/output validation for LLMs | Developer tool, not consumer |
| **NeMo Guardrails** | Conversational AI safety | Enterprise, complex setup |
| **Portkey AI** | Prompt security & observability | Enterprise, API-focused |
| **LlamaFirewall** | Security guardrails | Security focus, not instruction |

### Adjacent Products (Workflow Automation)

| Product | What They Do | Why Not a Threat |
|---------|--------------|------------------|
| **n8n** | Workflow automation templates | Task automation, not AI enforcement |
| **Lindy** | AI agent templates | Agent building, not enforcement |
| **Softr** | Workflow automation | No AI instruction enforcement |

### Adjacent Products (Browser Extensions)

| Product | What They Do | Why Not a Threat |
|---------|--------------|------------------|
| **Seraphic** | Browser security enforcement | Security focus, not instruction |
| **LayerX** | Extension risk management | Enterprise security |

---

## Current "Solutions" (All Workarounds)

### Prompt Engineering Hacks
- Use delimiters (###, """, XML tags)
- Constraint-first prompting ("what NOT to do" before "what to do")
- Repeat instructions throughout conversation

### Context Management
- `/clear` - Reset session (loses all progress)
- `/compact` - Summarize conversation (lossy)
- `.claudeignore` - Reduce context size

### Manual Reminders
- "Remember my instructions about X"
- "Follow the rules I specified earlier"
- Re-paste instructions periodically

**None of these are products. They're coping mechanisms.**

---

## Gap: What NO One Offers

- **Pre-execution gate**: Validate AI has loaded ALL rules before proceeding
- **Post-execution gate**: Validate output against user-defined protocols
- **Protocol persistence**: Rules that don't fade as conversation grows
- **Explicit enforcement**: Block or flag non-compliant outputs
- **Self-configuring setup**: Walk user through defining their protocols
- **Cross-platform**: Works with ChatGPT, Claude, Cursor, any AI

---

## Market Opportunity

| Metric | Value |
|--------|-------|
| AI Personal Assistant Market | $7.6B (2025) |
| Users with AI Assistants | "Everyone will have one by 2026" |
| AI Tool Adoption | Ubiquitous - as common as smartphones |
| Problem Universality | Every AI user experiences this |

**Quote from MIT Tech Review:** "2026 will be the year the tech gets practical... focus shifting toward making AI usable."

The gap between AI capability and AI reliability is THE problem of 2026.

---

## Competitive Moat Assessment

| Moat Type | Available? | Notes |
|-----------|------------|-------|
| First mover | **YES** | No one doing this yet |
| Technical complexity | Medium | Requires cross-platform integration |
| Network effects | Possible | Shared protocol templates |
| Switching costs | High once configured | Users invest in their protocols |

---

## CES 2026 Relevance

| Announcement | Consumer Product Relevance |
|--------------|---------------------------|
| **Lenovo Qira** | Personal AI agent = needs protocol enforcement |
| **SoundHound Amelia** | Agentic voice = needs rules it follows |
| **AI Policy Summit** | Governance discussion = enforcement demand |
| **"AI Everywhere"** | Mass adoption = mass enforcement need |

---

## Target Market Segments

| Segment | Size | Pain Level | Willingness to Pay |
|---------|------|------------|-------------------|
| **Power Users** | Millions | Very High | $15-20/mo |
| **Content Creators** | Millions | High | $10-15/mo |
| **Developers** | Millions | Very High | $20-30/mo |
| **Business Users** | Tens of millions | High | $15-25/mo |
| **Casual Users** | Hundreds of millions | Medium | Free tier |

---

## Recommended Positioning

### Primary Message
> "Make AI actually follow your rules. Not sometimes. Every time."

### Supporting Messages
- "Your instructions, enforced"
- "Stop repeating yourself to AI"
- "Protocol Enforcement for the rest of us"

### Differentiation
- **vs. Guardrails AI**: "Guardrails is for developers. We're for everyone."
- **vs. Custom Instructions**: "Instructions are suggestions. Protocols are requirements."
- **vs. Prompt Engineering**: "Stop hacking. Start enforcing."

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| OpenAI/Anthropic build native enforcement | Medium | Move fast, establish brand |
| Enterprise tools go downmarket | Low | Different UX, different pricing |
| Technical complexity | Medium | Start simple (checklist gate) |
| User adoption friction | Medium | Self-configuring wizard |

---

## Strategic Recommendations

1. **Move Fast**: The problem is documented, validated, and unsolved. First mover wins.

2. **Start Simple**: Checklist Gate + one template (Writing or Coding)

3. **Cross-Platform from Day 1**: Don't tie to one AI tool

4. **Freemium Model**: Free tier builds awareness, Pro tier monetizes power users

5. **Pattern Library**: Pre-built templates reduce friction, create stickiness

6. **Funnel to Platform**: Heavy users → upsell to domain-specific Execution Engines

---

## Sources

- [OpenAI Forum - Custom Instructions Issues](https://community.openai.com/t/custom-instructions-no-longer-work/1116521)
- [GitHub - Claude Code Bug Reports](https://github.com/anthropics/claude-code/issues/668)
- [Cursor Forum - Rules Not Applied](https://forum.cursor.com/t/cursorrules-not-being-followed-or-applied/131781)
- [Why ChatGPT Ignores Instructions](https://resources.opencraftai.com/blog/why-chatgpt-keeps-ignoring-custom-instructions-and-what-actually-works/)
- [MIT Tech Review - AI in 2026](https://www.technologyreview.com/2026/01/05/1130662/whats-next-for-ai-in-2026/)
- [Guardrails AI](https://www.guardrailsai.com/)
- [n8n Workflow Templates](https://n8n.io/workflows/)

---

*Report: 2026-01-07*

# QA Management Engine - Launch Task List

**Product:** QA Management Engine (Isagawa Corp)
**Target:** AI-assisted QA test automation with quality gates
**Distribution:** Claude Code skill + Python framework
**Public Repo:** `D:\isagawa_co\isagawa-qa` → `github.com/isagawa-qa/isagawa-qa`
**Last Updated:** 2026-02-03

---

## Current Blockers

| Blocker | Status | Notes |
|---------|--------|-------|
| DEF-045: Two-Pass Discovery | RESOLVED | Element discovery fixed |
| DEF-046: Test Redundancy | RESOLVED | Duplicate test detection added |
| Push to GitHub | NOT STARTED | Org exists, no public repos yet |

---

## Phase 1: Repository Ready

### 1.1 README.md
- [x] **Hero section** - What it is, who it's for, key benefit (1 sentence)
- [ ] **Demo GIF/video** - 30-second workflow showing AI generating tests
- [x] **Quick start** - 5 steps to first working test
- [x] **Features list** - 5-step workflow, quality gates, HITL, 4-layer architecture
- [x] **Installation** - pip install + Claude Code setup
- [x] **Usage examples** - Sample requirements → generated tests
- [x] **Architecture diagram** - Simple visual of the 4 layers
- [x] **License** - MIT
- [x] **Contributing** - How to report issues, submit PRs
- [x] **Links** - GitHub issues link
- [ ] **Fix repo URL** - Change from solosza/py-selenium-framework-mcp to isagawa-qa/isagawa-qa (lines 63, 552)

### 1.2 Repository Cleanup
- [x] Review .gitignore - ensure no secrets, local configs exposed
- [x] Verify `_reference/` is the only example code
- [x] Add LICENSE file (MIT)
- [x] Add CONTRIBUTING.md
- [ ] Add CHANGELOG.md
- [ ] Create GitHub release tags (v1.0.0)

### 1.3 Documentation
- [x] **Getting Started Guide** - docs/GETTING_STARTED.md
- [x] **Architecture Overview** - In README + _reference/README.md
- [x] **Skill Reference** - .claude/skills/qa-management-layer/SKILL.md
- [x] **Troubleshooting** - In README.md
- [x] **CLAUDE.md** - AI instructions for framework

---

## Phase 2: Distribution

### 2.1 Python Package (pip)
- [ ] Create pyproject.toml
- [ ] Package name: `isagawa-qa`
- [x] Define dependencies (requirements.txt, mcp_server/requirements.txt)
- [ ] Test local install: `pip install -e .`
- [ ] Publish to TestPyPI first
- [ ] Publish to PyPI
- [ ] Verify install: `pip install isagawa-qa`

### 2.2 Claude Code Skill
- [x] Package skill files (.claude/skills/qa-management-layer/)
- [x] Skill commands (.claude/commands/qa-workflow.md, qa-workflow-dev.md, run-test.md)
- [x] Step protocols (step-01.md through step-05.md)
- [ ] Write skill installation instructions in README
- [ ] Test fresh install on clean machine

### 2.3 MCP Server
- [x] MCP tools implemented (mcp_server/tools/)
- [x] Quality gates (qg_user_input, qg_preflight, qg_ai_processing, qg_discovered_elements, qg_execution)
- [x] Document MCP server setup in README
- [x] .mcp.json template in README
- [ ] Test MCP tools work after pip install

---

## Phase 3: Website / Landing Page

### 3.1 Domain & Hosting
- [ ] Domain: isagawaco.com (primary), isagawacorp.com (future)
- [ ] Hosting: GitHub Pages, Vercel, Netlify, or simple static host
- [ ] SSL certificate (usually automatic with above hosts)

### 3.2 Landing Page Content
- [ ] **Headline** - Clear value prop (e.g., "AI-Powered QA Test Generation with Human-in-the-Loop")
- [ ] **Subheadline** - Who it's for (e.g., "For QA engineers who want AI assistance, not AI replacement")
- [ ] **Problem/Solution** - Why existing tools fail, how this is different
- [ ] **Features** - 5-step workflow, quality gates, HITL triage, 4-layer architecture
- [ ] **Demo** - Video or interactive demo
- [ ] **Testimonials** - (After first users)
- [ ] **Pricing** - Free/Open source? Freemium? Enterprise?
- [ ] **CTA** - "Get Started" → GitHub or docs
- [ ] **Footer** - Links, contact, social

### 3.3 Documentation Site (Optional for MVP)
- [ ] Tool: GitBook, Docusaurus, MkDocs, or ReadTheDocs
- [ ] Structure: Getting Started, Guides, Reference, FAQ
- [ ] Search functionality
- [ ] Versioning (for future releases)

---

## Phase 4: First Users

### 4.0 Pre-Launch Validation
- [ ] E2E test on AutomationPractice.pl (clean run)
- [ ] E2E test on ParaBank (clean run)
- [ ] Fresh machine install test
- [ ] Verify all MCP tools respond correctly

### 4.1 Identify Target Users
- [ ] QA engineers familiar with Selenium/pytest
- [ ] Teams using Claude Code already
- [ ] Early adopters interested in AI-assisted testing
- [ ] Where to find them: Reddit r/QualityAssurance, LinkedIn, Twitter/X, Discord servers

### 4.2 First User Communication
- [ ] **What to tell them:**
  - This is an AI Management Layer for QA automation
  - AI generates code, quality gates enforce patterns
  - Human stays in the loop for decisions
  - 5-step workflow: User Input → Pre-flight → AI Processing → Collaborative Construction → Test Execution
  - Works with any web application

- [ ] **What they need:**
  - Python 3.x
  - Claude Code CLI
  - Chrome/Firefox browser
  - Basic pytest knowledge

- [ ] **What to expect:**
  - AI builds tests by reading reference patterns
  - Quality gates catch mistakes before they propagate
  - HITL triage when things fail
  - Working tests against real applications

### 4.3 Onboarding Flow
- [ ] Step 1: Install framework (`pip install isagawa-qa`)
- [ ] Step 2: Clone skill to `.claude/skills/`
- [ ] Step 3: Configure MCP server (`.mcp.json`)
- [ ] Step 4: Run `/qa-workflow` with sample requirement
- [ ] Step 5: See working test execute

### 4.4 Feedback Collection
- [ ] GitHub Issues for bugs
- [ ] GitHub Discussions for questions
- [ ] Simple feedback form (Google Form, Typeform)
- [ ] Direct outreach for detailed feedback

---

## Phase 5: Launch Channels

### 5.1 Announcements
- [ ] **GitHub** - Release notes, README updates
- [ ] **Twitter/X** - Thread explaining the product
- [ ] **LinkedIn** - Professional announcement
- [ ] **Reddit** - r/QualityAssurance, r/selenium, r/Python, r/MachineLearning
- [ ] **Hacker News** - Show HN post
- [ ] **Product Hunt** - Launch listing (optional)
- [ ] **Dev.to / Medium** - Technical blog post

### 5.2 Content Ideas
- [ ] "How I built an AI Management Layer for QA" - Story post
- [ ] "Why AI-generated tests need quality gates" - Problem/solution post
- [ ] "5-step workflow for reliable AI test generation" - Tutorial post
- [ ] Demo video walkthrough

---

## Phase 6: Support & Community

### 6.1 Support Channels
- [ ] GitHub Issues (primary)
- [ ] GitHub Discussions (Q&A)
- [ ] Discord server (optional for MVP)
- [ ] Email support (for enterprise inquiries)

### 6.2 Documentation for Common Issues
- [ ] "MCP server not connecting"
- [ ] "Quality gate failing - how to fix"
- [ ] "Test execution errors"
- [ ] "Browser not launching"

---

## Priority Order (MVP Launch)

### P0: Blockers (Fix First)
1. [x] Complete DEF-045 (Two-Pass Discovery) - RESOLVED
2. [x] Complete DEF-046 (Test Redundancy) - RESOLVED
3. [ ] E2E verification passes on 2 sites

### P1: Must Have (Week 1)
4. [x] README.md - Professional, clear, with quick start
5. [x] LICENSE file (MIT)
6. [x] Repository cleanup (_reference/ is only example)
7. [x] Basic installation instructions
8. [x] One working example (using _reference/)
9. [x] CONTRIBUTING.md
10. [ ] CHANGELOG.md
11. [ ] Fix README repo URLs (solosza → isagawa-qa)
12. [ ] Push to github.com/isagawa-qa/isagawa-qa
13. [ ] GitHub issue templates (.github/ISSUE_TEMPLATE/)

### P2: Should Have (Week 2)
14. [x] Getting Started guide (docs/GETTING_STARTED.md)
15. [ ] pyproject.toml + PyPI publish
16. [ ] Demo GIF/video
17. [ ] KNOWN_ISSUES.md - Document current limitations
18. [ ] First user outreach
19. [ ] Landing page (simple, one-page)

### P3: Nice to Have (Week 3+)
20. [ ] FAQ.md
21. [ ] COMPATIBILITY.md - OS/browser matrix
22. [ ] Documentation site
23. [ ] Community Discord
24. [ ] Blog posts
25. [ ] Product Hunt launch

---

## Phase 7: Community Contributions

### 7.1 What Community Can Help With

**Documentation:**
- [ ] FAQs - Common questions and answers
- [ ] Known issues - Bugs, workarounds, edge cases
- [ ] Tutorials - Step-by-step guides for specific use cases
- [ ] Translations - Non-English documentation

**Testing & Validation:**
- [ ] Test on different OS (Windows, Mac, Linux)
- [ ] Test with different browsers (Chrome, Firefox, Edge)
- [ ] Test with different web applications
- [ ] Report edge cases and failures

**Code Contributions:**
- [ ] New POM examples for common UI patterns
- [ ] Additional WebInterface methods
- [ ] Bug fixes
- [ ] Performance improvements

**Content:**
- [ ] Blog posts about using the tool
- [ ] Video tutorials
- [ ] Conference talks
- [ ] Comparison with other tools

### 7.2 CONTRIBUTING.md Template

```markdown
# Contributing to QA Management Engine

## Ways to Contribute

### 1. Report Issues
- Bug reports with reproduction steps
- Feature requests
- Documentation gaps

### 2. Improve Documentation
- Add to FAQ (see docs/FAQ.md)
- Document known issues (see docs/KNOWN_ISSUES.md)
- Write tutorials

### 3. Test & Validate
- Test on your OS/browser
- Try with your web applications
- Report what works and what doesn't

### 4. Code Contributions
- Fix bugs
- Add examples to _reference/
- Improve existing code

## How to Contribute

1. Fork the repo
2. Create a branch (`feature/your-feature`)
3. Make changes
4. Submit PR with clear description

## What We're Looking For

### High Priority
- [ ] FAQ entries (real questions from users)
- [ ] Known issues with workarounds
- [ ] Examples for common UI patterns (modals, tables, forms)
- [ ] Cross-platform testing results

### Medium Priority
- [ ] Tutorials for specific frameworks (React, Angular, Vue)
- [ ] Integration guides (CI/CD, Docker)
- [ ] Performance benchmarks

### Low Priority (Nice to Have)
- [ ] Translations
- [ ] Video content
- [ ] Comparison articles
```

### 7.3 Initial Community Asks

**On launch, ask for:**

1. **"What questions do you have?"** → Builds FAQ
2. **"What broke?"** → Builds Known Issues
3. **"What web app did you try it on?"** → Builds compatibility matrix
4. **"What's confusing?"** → Improves docs

**Templates to create:**
- [ ] `docs/FAQ.md` - Start empty, community fills
- [ ] `docs/KNOWN_ISSUES.md` - Start with known limitations
- [ ] `docs/COMPATIBILITY.md` - OS/browser/app matrix
- [ ] `.github/ISSUE_TEMPLATE/bug_report.md`
- [ ] `.github/ISSUE_TEMPLATE/feature_request.md`
- [ ] `.github/ISSUE_TEMPLATE/question.md`

---

## Decisions Made

| Question | Decision |
|----------|----------|
| License | MIT (open source) |
| Package name | isagawa-qa |
| Brand name | Isagawa QA |
| Target audience | QA engineers using Claude Code |
| Pricing | Free (open source core) |
| Domain | isagawaco.com (per roadmap) |

---

## Files to Create

### CHANGELOG.md
```markdown
# Changelog

## [1.0.0] - 2026-02-XX

### Added
- 4-layer architecture (Role > Task > Page > WebInterface)
- AI-powered test generation via MCP tools
- Quality gates for code validation
- 5-step guided workflow (/qa-workflow)
- Reference implementation in framework/_reference/
- HITL triage on test failures
```

### pyproject.toml
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "isagawa-qa"
version = "1.0.0"
description = "AI-powered QA test automation with quality gates"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.11"
authors = [{name = "Isagawa Corp"}]
keywords = ["qa", "testing", "automation", "selenium", "ai", "mcp"]
dependencies = [
    "selenium>=4.0.0",
    "pytest>=7.0.0",
    "pytest-html>=4.0.0",
    "webdriver-manager>=4.0.0",
    "faker>=18.0.0",
]

[project.urls]
Homepage = "https://github.com/isagawa-qa/isagawa-qa"
Issues = "https://github.com/isagawa-qa/isagawa-qa/issues"
```

### .github/ISSUE_TEMPLATE/bug_report.md
```markdown
---
name: Bug Report
about: Report something that isn't working
title: '[BUG] '
labels: bug
---

**Describe the bug**
A clear description of what's broken.

**To Reproduce**
1. Run '...'
2. See error

**Expected behavior**
What should happen.

**Environment**
- OS: [e.g., Windows 11]
- Python: [e.g., 3.11]
- Browser: [e.g., Chrome 121]

**Error output**
```
Paste error here
```
```

### .github/ISSUE_TEMPLATE/feature_request.md
```markdown
---
name: Feature Request
about: Suggest an idea
title: '[FEATURE] '
labels: enhancement
---

**Problem**
What problem does this solve?

**Proposed solution**
How should it work?

**Alternatives considered**
Other approaches you've thought about.
```

---

*Created: 2026-01-28*
*Updated: 2026-02-03*

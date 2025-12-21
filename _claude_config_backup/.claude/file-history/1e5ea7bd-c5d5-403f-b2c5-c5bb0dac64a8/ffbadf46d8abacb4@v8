# Resume Generation Prompt Template

**Version:** 1.0
**Last Updated:** 2025-01-07

---

## Purpose

This prompt guides Claude Code through the AI-powered resume generation workflow. The system analyzes job descriptions, intelligently selects relevant content from master data, and generates optimized HTML resumes with embedded CSS, dark mode, and responsive design.

**Key Capabilities:**
- Job description analysis to identify role type and requirements
- Tag-based content filtering from resume-master.md
- Intelligent bullet variant selection based on role focus
- HTML generation with modern, clean design
- Mobile-responsive layout with dark mode toggle
- GitHub Pages deployment ready

---

## Inputs Required

1. **Job Description** (provided by user)
   - Full text of job posting
   - Or job requirements summary
   - Or role description with key skills

2. **Master Data File** (auto-loaded)
   - Path: `resume-master.md` (repository root)
   - Contains all resume content with tags and metadata

3. **Output Filename** (derived from job)
   - Format: `resumes/[job-name].html`
   - Example: `resumes/ai-residency.html`

---

## Step 1: Job Description Analysis

**Objective:** Extract key information to guide content selection.

### Extract the Following:

**1. Role Type** (select one):
- `ai_specialist` - AI engineering, ML engineering, AI residency
- `ai_engineer` - AI/ML engineer roles
- `qa_engineer` - QA automation, SDET
- `automation_engineer` - Test automation specialist
- `qa_lead` - QA leadership, management
- `engineering_manager` - Engineering management
- `full_stack` - Full-stack developer (if applicable)

**2. Key Skills** (ranked by importance):
- List 5-10 most important skills from job description
- Include specific technologies mentioned
- Note required vs. preferred skills
- Example: ["claude-code", "prompt-engineering", "python", "ai-agents", "automation"]

**3. Technical vs. Management Score** (0-10 scale):
- 0 = Pure management (no hands-on work)
- 5 = Balanced (equal technical and management)
- 10 = Pure technical (hands-on coding, building)
- AI Residency example: 9/10 (very hands-on)

**4. Technologies Mentioned:**
- Programming languages (Python, JavaScript, etc.)
- Frameworks/libraries (pytest, Selenium, etc.)
- Tools (Claude Code, Make.com, etc.)
- Platforms (GitHub, AWS, etc.)

**5. Company Culture Signals:**
- Startup vs. enterprise
- Builder/producer focus vs. process-oriented
- Innovation vs. stability
- Remote-first vs. in-person

---

## Step 2: Content Selection

### Projects Selection (Choose 2-3 Most Relevant)

**Selection Criteria:**
1. Match project tags to job requirements
2. Prioritize recent projects (2024-2025)
3. Consider role type for ordering

**For AI-focused roles (ai_specialist, ai_engineer, ai_residency):**
- Order: Resume Generator → Multi-Agent System → Real Estate Automation
- Emphasize: AI system design, prompt engineering, agent workflows

**For QA/Automation roles (qa_engineer, sdet, automation_engineer):**
- Order: Real Estate Automation → Resume Generator → Multi-Agent System
- Emphasize: Framework building, technical depth, automation

**For Technical Leadership roles (qa_lead, engineering_manager):**
- Order: Resume Generator → Multi-Agent System → Real Estate Automation
- Emphasize: System architecture, team enablement, scalable design

### Experience Bullet Variant Selection

**Read from resume-master.md bullet variants:**
- `ai_focused` - For AI/ML roles (technical_score ≥ 7)
- `technical` - For hands-on technical roles (technical_score ≥ 5)
- `management` - For leadership roles (technical_score ≤ 4)

**Selection Rules:**
1. If role_type includes "ai" OR technical_score ≥ 8 → use `ai_focused`
2. If technical_score between 5-7 → use `technical`
3. If technical_score ≤ 4 OR role_type includes "lead"/"manager" → use `management`

**Experience Condensing (based on role type):**

**For AI-focused roles:**
- Helios Digital: 3 bullets (ai_focused)
- Nakupuna Consulting: 3 bullets (ai_focused)
- HMSA: 1-2 bullets (technical)
- IBM: Omit or 1-line summary

**For Traditional QA roles:**
- All 4 roles: 2-3 bullets each (technical)
- Equal emphasis across all roles

**For Leadership roles:**
- All 4 roles: 2-3 bullets each (management)
- Emphasize team building and scaling

### Skills Ordering

**For AI-focused roles:**
1. AI Tools & Platforms (first)
2. Automation Platforms
3. Programming Languages & Tools
4. Test Automation & Frameworks
5. API & Integration
6. Development Methodologies

**For QA/Automation roles:**
1. Test Automation & Frameworks (first)
2. Programming Languages & Tools
3. API & Integration
4. AI Tools & Platforms
5. Development Methodologies
6. Automation Platforms

**For Leadership roles:**
1. Development Methodologies (first)
2. Test Automation & Frameworks
3. AI Tools & Platforms
4. Programming Languages & Tools
5. API & Integration
6. Automation Platforms

### Section Ordering

**For AI-focused roles:**
Header → Professional Summary → **Projects** (prominent) → Experience → Skills

**For Traditional QA/Technical roles:**
Header → Professional Summary → **Experience** (prominent) → Projects → Skills

**For Leadership roles:**
Header → Professional Summary → **Experience** (prominent) → Projects → Skills

---

## Step 3: HTML Generation

### Document Structure

**Required HTML5 structure:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Name] - [Role Type] Resume</title>
    <style>
        /* Embedded CSS here */
    </style>
</head>
<body>
    <!-- Dark mode toggle button -->
    <button id="darkModeToggle">🌙 Dark Mode</button>

    <!-- Resume content -->
    <div class="container">
        <header>...</header>
        <section class="about">...</section>
        <section class="projects">...</section>
        <section class="experience">...</section>
        <section class="skills">...</section>
    </div>

    <script>
        /* Dark mode toggle JavaScript */
    </script>
</body>
</html>
```

### CSS Requirements

**Design Principles:**
- Modern, clean, minimal aesthetic (not corporate)
- Developer-focused design (GitHub-style, not LinkedIn)
- Generous whitespace for easy scanning
- Professional color scheme (blues/grays, subtle)

**Required Styles:**

1. **Base Styles:**
   - System fonts: `-apple-system, SF Pro, Segoe UI, sans-serif`
   - Base font size: 16px
   - Line height: 1.6
   - Max width: 900px, centered

2. **Responsive Breakpoints:**
   - Mobile: 375px - 767px (single column, larger font)
   - Tablet: 768px - 1023px (optimized layout)
   - Desktop: 1024px+ (full layout)

3. **Dark Mode:**
   - Light mode (default): white background, dark text
   - Dark mode: dark background (#1a1a1a), light text (#e0e0e0)
   - Use CSS variables for colors
   - Toggle persists via localStorage

4. **Print Styles:**
   - Remove dark mode toggle button
   - Force light mode colors
   - Optimize for 1-2 pages
   - Add page break hints between sections

**Color Variables (CSS Custom Properties):**
```css
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --accent: #0066cc;
    --border: #dee2e6;
}

[data-theme="dark"] {
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --text-primary: #e0e0e0;
    --text-secondary: #a0a0a0;
    --accent: #4da6ff;
    --border: #404040;
}
```

### Dark Mode Toggle Implementation

**JavaScript Requirements:**
1. Toggle button in top-right corner
2. Click toggles `data-theme="dark"` on `<html>` element
3. Save preference to `localStorage.setItem('theme', 'dark')`
4. Load preference on page load
5. Smooth transition between modes (CSS transition)

**Example JavaScript:**
```javascript
const toggleButton = document.getElementById('darkModeToggle');
const html = document.documentElement;

// Load saved theme
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    html.setAttribute('data-theme', 'dark');
    toggleButton.textContent = '☀️ Light Mode';
}

// Toggle theme
toggleButton.addEventListener('click', () => {
    const currentTheme = html.getAttribute('data-theme');
    if (currentTheme === 'dark') {
        html.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
        toggleButton.textContent = '🌙 Dark Mode';
    } else {
        html.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        toggleButton.textContent = '☀️ Light Mode';
    }
});
```

### Content Formatting

**Header Section:**
- Name: Large, bold (h1)
- Contact: Email, phone, location (smaller, inline)
- Links: GitHub, LinkedIn (clickable, styled)

**Professional Summary Section:**
- Section heading: "Professional Summary" (industry standard, not "About")
- 2-3 sentences summarizing role focus
- **CRITICAL - Avoid These Mistakes:**
  - ❌ DO NOT mimic job description language verbatim
  - ❌ DO NOT use the job title from the JD in the summary (e.g., if JD says "Principal Quality Engineer," use "QA and Test Automation Leader" instead)
  - ❌ DO NOT include years of experience (e.g., "15+ years") - AI tell
  - ❌ DO NOT copy job-specific keywords or phrases (e.g., if JD says "data pipeline testing," don't use that exact phrase)
  - ❌ DO NOT mention specific performance testing tools (JMeter, LoadRunner, etc.)
  - ❌ DO NOT mention specific scripting languages (Python, JavaScript, etc.)
  - ❌ DO NOT keyword-stuff or sound robotic
  - ❌ DO NOT use dashes " - " anywhere in resume content (AI-generated content indicator)
  - ❌ DO NOT optimize by adding JD-specific terminology - stay general and capability-focused
- **DO Use These Principles:**
  - ✅ Keep high-level and capability-focused
  - ✅ Use authentic, natural language
  - ✅ Emphasize: building from ground up, scaling teams, AI integration
  - ✅ Show: types of organizations (startups/enterprise), impact, breadth of experience
  - ✅ Technical details belong in Skills and Experience sections, not summary
- **Pattern:** [Role Type] Leader establishing [function] from ground up across [org types]. Strong technical foundation in [general capability] combined with proven ability to [key achievements]. Recently integrated AI tools (Claude Code, GPT-5, Gemini) into [workflows] to [benefits]. Track record of [leadership impact] and delivering [infrastructure type] that supports [impact].

**Projects Section:**
- Project title (h3) with date
- Tech stack (small, gray text)
- 2-3 bullet points per project
- No inline links (keep clean)

**Experience Section:**
- Company name + title (h3)
- Location + dates (smaller, gray)
- 2-3 bullets per role (based on variant selected)

**Skills Section:**
- Group by category (h4)
- Comma-separated list per category
- Ordered by relevance to role
- **Format for tool descriptions:** Use colons instead of dashes
  - ✅ Correct: "Claude Code (Anthropic: AI-assisted development)"
  - ❌ Incorrect: "Claude Code (Anthropic - AI-assisted development)"

**Footer Section:**
- MUST include footer after Skills section, before closing container
- Links to GitHub repo and Live Demo (pointing to current resume)
- Format: `<footer><p>Generated using my custom <a href="https://github.com/solosza/resume-ai-pipeline" target="_blank">AI-Powered Resume Generation System</a> | <a href="https://solosza.github.io/resume-ai-pipeline/resumes/[current-resume-filename].html" target="_blank">View Live Demo</a></p></footer>`
- Center-aligned, subtle text color, border top
- Hidden on print (@media print)
- Emphasizes that candidate built the system (ownership)

---

## Step 4: Validation Checklist

Before saving the generated resume, verify:

**Content Validation:**
- [ ] All personal info present (name, email, phone, location, links)
- [ ] Correct number of projects (2-3) selected
- [ ] Appropriate bullet variants used (ai_focused/technical/management)
- [ ] Skills ordered correctly for role type
- [ ] Section order matches role type

**HTML/CSS Validation:**
- [ ] Valid HTML5 structure
- [ ] CSS embedded (no external dependencies)
- [ ] Dark mode toggle implemented
- [ ] Responsive breakpoints at 375px, 768px, 1024px
- [ ] Print styles included (@media print)

**Functionality Validation:**
- [ ] Dark mode toggle works (test in browser)
- [ ] Dark mode persists on reload (localStorage)
- [ ] All links clickable and correct
- [ ] Mobile layout works (single column)
- [ ] Print preview shows 1-2 pages

**Quality Validation:**
- [ ] No typos or grammatical errors
- [ ] Consistent formatting across sections
- [ ] Professional tone and language
- [ ] Clean, scannable layout

---

## Example: AI Residency Role

### Example Job Description:
```
AI Residency Program

3-month intensive residency for recent graduates or career transitioners.
Full-time, in-person in Las Vegas. Housing provided.

We're looking for producers who build real AI tools, not just learners.
You should have hands-on experience with LLMs, prompt engineering, and
building AI-powered applications. Python experience preferred.

Focus on grit, adaptability, and figure-it-out mentality. Long hours,
daily accountability, real impact. Opportunity for full-time role after
proving value in 90 days.
```

### Expected Analysis:
```
Role Type: ai_residency (matches ai_specialist pattern)
Key Skills: [
    "llms", "prompt-engineering", "python", "ai-tools",
    "hands-on-building", "producer-mindset", "grit"
]
Technical Score: 9/10 (very hands-on, builder-focused)
Technologies: Python, LLMs, prompt engineering
Culture: Startup, builder-focused, high intensity, producer mindset
```

### Expected Content Selection:
```
Projects (all 3, in order):
1. AI-Powered Resume Generation System
2. Multi-Phase AI Agent System
3. Real Estate Automation with AI-Assisted Development

Experience bullets: ai_focused variants
- Helios: 3 bullets (ai_focused)
- Nakupuna: 3 bullets (ai_focused)
- HMSA: 1-2 bullets (technical)
- IBM: Omit

Skills order: AI Tools → Automation Platforms → Programming → Testing

Section order: Header → Professional Summary → Projects → Experience → Skills
```

---

## Output Specifications

**File Location:** `resumes/[job-name].html`

**File Naming Convention:**
- Lowercase, hyphen-separated
- Descriptive of role
- Examples: `ai-residency.html`, `senior-qa-engineer.html`, `ml-engineer-google.html`

**File Size:** < 100KB (embedded CSS, no images)

**Compatibility:**
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile devices (iOS, Android)
- Print (1-2 pages)

**Deployment:** GitHub Pages ready (no build step required)

---

## Usage Instructions

1. **Receive job description from user**
2. **Read this prompt template** (`prompts/generate-resume.md`)
3. **Read master data** (`resume-master.md`)
4. **Analyze job description** (Step 1)
5. **Select content** (Step 2)
6. **Generate HTML** (Step 3)
7. **Validate output** (Step 4)
8. **Save to `resumes/[job-name].html`**
9. **Git commit and push**

---

## Notes

- This prompt is reusable across all job types
- No modification needed for different roles (analysis handles variation)
- Master data updates automatically flow to new resumes
- Each resume is self-contained (embedded CSS, no dependencies)
- GitHub Pages deployment requires no configuration changes

---

**End of Prompt Template**

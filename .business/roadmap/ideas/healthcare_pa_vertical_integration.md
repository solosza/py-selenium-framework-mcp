# Healthcare Prior Authorization Vertical - Isagawa Integration Analysis

**Version:** v1.0 - Living Document
**Date:** 2026-01-09
**Purpose:** Explore how Isagawa Platform (AI Management Layer) integrates into healthcare clinical administration, specifically Prior Authorization workflows

---

## Market Context

### Gen AI in Clinical Administration (2025-2026)

**Market Growth:**
- $1.55B (2025) → $2.26B (2026) → $45.82B (2034)
- US healthcare AI adoption: 3% (2023) → 22% (2025)
- Health systems leading at 27% adoption

**Key Trend:** 2026 marks end of "pilot era" - industry shifting to "governed, auditable, trusted systems at scale"

**Administrative Burden:**
- 77% of healthcare professionals lose time due to incomplete/inaccessible data
- Nurses spend 15-20 minutes per hour on administrative tasks
- Prior authorization averages 2-8 hours of staff time per request

### Prior Authorization Market

**Current State (2025):**
- **75% of insurers** use AI for PA approvals
- **12M+ PA requests/year** through major platforms (Cohere Health alone)
- Medicare launching AI-powered PA pilot (WISeR) in 6 states through 2031
- Industry target: **80% real-time approvals by 2027**

**Leading AI PA Vendors:**
- **Cohere Health:** 90% auto-approval rate, 660K+ providers, 12M requests/year
- **Rhyme:** 5M+ auths/year, 91 major hospital systems, 300+ payers
- **Innovaccer, Waystar:** Other major players

**Problems with Current Gen AI PA:**

| Problem | Impact | Source |
|---------|--------|--------|
| **Unregulated AI = Higher Denials** | Some tools produce 16x higher denial rates | AMA Report |
| **Black Box Decisions** | 61% of physicians fear opaque AI logic | AMA Survey |
| **No Audit Trail** | Can't explain WHY AI approved/denied | Industry standard |
| **Bias in Training Data** | AI learns payer's aggressive denial patterns | Federal policy concerns |
| **HIPAA Compliance Gaps** | AI vendors accessing PHI without proper governance | Regulatory concern |
| **Missing Context** | AI misses nuanced clinical factors | Physician feedback |
| **Appeal Difficulty** | Hard to appeal without transparency | Patient advocacy |

---

## 1. Traditional PA Workflow (Manual - No AI)

```
┌──────────────────────────────────────────────────────────────────┐
│  STEP 1: Provider Orders Treatment/Service                      │
│  Doctor determines patient needs: MRI, specialist referral,      │
│  surgery, expensive medication, DME, etc.                        │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 2: Check if PA Required                                   │
│  Staff manually checks payer policy:                             │
│  - Is this service on the PA list?                               │
│  - What medical necessity criteria apply?                        │
│  - What documentation is needed?                                 │
│  ⏱️ Time: 15-30 minutes per lookup                               │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 3: Gather Clinical Documentation                          │
│  Staff collects from multiple systems:                           │
│  - Patient medical history (EHR)                                 │
│  - Lab results                                                   │
│  - Imaging reports                                               │
│  - Previous treatments tried (step therapy)                      │
│  - Diagnosis codes (ICD-10)                                      │
│  - Procedure codes (CPT)                                         │
│  ⏱️ Time: 30-60 minutes per case                                 │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 4: Complete PA Request Form                               │
│  Staff manually fills out payer-specific form:                   │
│  - Patient demographics                                          │
│  - Provider NPI/tax ID                                           │
│  - Diagnosis + supporting clinical rationale                     │
│  - Medical necessity justification                               │
│  - Attach all supporting documents                               │
│  ⏱️ Time: 20-45 minutes per form                                 │
│  ⚠️  Error Rate: High (missing fields, wrong codes)              │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 5: Submit to Payer                                        │
│  Submission methods:                                             │
│  - Phone/fax (legacy)                                            │
│  - Payer portal (manual upload)                                  │
│  - Clearinghouse (semi-automated)                                │
│  ⏱️ Time: 10-30 minutes                                           │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 6: Payer Review                                           │
│  Payer staff manually reviews:                                   │
│  - Check medical necessity against internal criteria             │
│  - Verify patient eligibility/benefits                           │
│  - Apply clinical guidelines                                     │
│  - Escalate to medical director if complex                       │
│  ⏱️ Time: 7 days (standard) | 72 hours (expedited) - CMS 2025   │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 7: Decision Notification                                  │
│  Payer sends decision:                                           │
│  ✅ APPROVED - Service authorized                                │
│  ❌ DENIED - Does not meet criteria                              │
│  ⏸️ PENDED - Need more information                               │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 8a: If APPROVED → Schedule Service                        │
│  STEP 8b: If DENIED → Appeal Process (restart loop)             │
│  STEP 8c: If PENDED → Gather more docs (back to Step 3)         │
└──────────────────────────────────────────────────────────────────┘
```

**Pain Points:**
- **Total time per PA:** 2-8 hours of staff time
- **Denial rate:** 13-18% on average
- **Delay to care:** Days to weeks
- **Staff burnout:** Repetitive, complex, error-prone
- **Patient impact:** 82% of physicians report patients abandon treatment due to PA delays

---

## 2. Current Gen AI PA Workflow (2025 - Cohere Health / Rhyme Model)

```
┌──────────────────────────────────────────────────────────────────┐
│  STEP 1: Provider Orders Treatment (EHR)                        │
│  Doctor clicks "Order MRI" in EHR                                │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  GEN AI AUTO-TRIGGER (Rhyme/Cohere Integration)                 │
│  ────────────────────────────────────────────────────────────    │
│  AI detects PA-required service via EHR hook                     │
│  ⏱️ Time: Real-time (< 1 second)                                 │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  GEN AI DATA EXTRACTION (NLP + ML)                              │
│  ────────────────────────────────────────────────────────────    │
│  AI automatically pulls from EHR:                                │
│  • Patient demographics                                          │
│  • Diagnosis codes (ICD-10)                                      │
│  • Clinical history (previous treatments, meds, labs)            │
│  • Imaging/lab results                                           │
│  • Provider NPI/credentials                                      │
│  ⏱️ Time: 5-10 seconds                                            │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  GEN AI CRITERIA MATCHING                                       │
│  ────────────────────────────────────────────────────────────    │
│  AI compares clinical data against:                              │
│  • Payer medical necessity criteria                              │
│  • Evidence-based clinical guidelines                            │
│  • Step therapy requirements                                     │
│  • Formulary restrictions                                        │
│                                                                  │
│  AI Decision Logic (Cohere Health model):                        │
│  → Clear match? AUTO-APPROVE (90% of cases)                      │
│  → Borderline/complex? FLAG for human review                     │
│  → Missing data? AUTO-REQUEST additional documentation           │
│  ⏱️ Time: 10-30 seconds                                           │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  GEN AI FORM GENERATION & SUBMISSION                            │
│  ────────────────────────────────────────────────────────────    │
│  AI auto-generates payer-specific PA request:                    │
│  • Populates all required fields                                 │
│  • Attaches clinical documentation                               │
│  • Generates medical necessity narrative                         │
│  • Submits via FHIR API or payer portal                          │
│  ⏱️ Time: 5-15 seconds                                            │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  PAYER REVIEW (Payer-side AI)                                   │
│  ────────────────────────────────────────────────────────────    │
│  Payer AI reviews submission:                                    │
│  • Auto-approve if meets criteria                                │
│  • Auto-deny if clearly outside criteria                         │
│  • Escalate to medical director if complex                       │
│  ⏱️ Time: Real-time to 72 hours (depends on payer AI)            │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  DECISION NOTIFICATION (via EHR integration)                    │
│  Provider sees decision in EHR real-time or within hours         │
│  ✅ APPROVED → Patient notified, service scheduled               │
│  ❌ DENIED → AI suggests appeal rationale                        │
└──────────────────────────────────────────────────────────────────┘
```

**Performance Metrics (2025):**
- **Cohere Health:** Auto-approves 90% of PA requests, serves 660K+ providers, 12M+ requests/year
- **Rhyme:** Processes 5M+ auths/year across 91 major hospital systems
- **Time savings:** 2-8 hours → 5-30 minutes
- **Industry target:** 80% of PAs decided in real-time by 2027

---

## 3. Isagawa-Enhanced PA Workflow (AI Management Layer)

```
┌──────────────────────────────────────────────────────────────────┐
│  STEP 1: Provider Orders Treatment (EHR)                        │
│  Doctor clicks "Order MRI" in EHR                                │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  GEN AI AUTO-TRIGGER (Rhyme/Cohere)                             │
│  AI detects PA-required service                                  │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  GEN AI DATA EXTRACTION (NLP + ML)                              │
│  AI pulls patient data from EHR                                  │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  ╔═══════════════════════════════════════════════════════════╗  │
│  ║   ISAGAWA AI MANAGEMENT LAYER - GATE #1                   ║  │
│  ║   DATA QUALITY & HIPAA COMPLIANCE GATE                    ║  │
│  ╚═══════════════════════════════════════════════════════════╝  │
│                                                                  │
│  PROTOCOL: PA Data Validation Workflow                          │
│  ──────────────────────────────────────                         │
│  1. Validate all required clinical data present                 │
│  2. Check data quality (complete diagnosis, valid codes)        │
│  3. Verify PHI access permissions                               │
│  4. Log data extraction for HIPAA audit                         │
│                                                                  │
│  SMART GATE CHECKS:                                             │
│  ──────────────────                                             │
│  ✓ HIPAA Compliance:                                            │
│    • PHI accessed by authorized AI only? YES                    │
│    • Minimum necessary data extracted? YES                      │
│    • Audit log created? YES                                     │
│                                                                  │
│  ✓ Data Quality:                                                │
│    • ICD-10 codes valid? YES (M25.511 - Pain in right shoulder) │
│    • Clinical history complete? YES (6 weeks conservative Rx)   │
│    • Required documents present? YES (X-ray, PT notes)          │
│                                                                  │
│  ✓ Completeness Check:                                          │
│    • All payer-required fields present? YES                     │
│    • Supporting documentation sufficient? YES                   │
│                                                                  │
│  DECISION: PASS → Proceed to criteria matching                  │
│                                                                  │
│  📊 AUDIT LOG #1: Data extraction validated, HIPAA-compliant    │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  GEN AI CRITERIA MATCHING                                       │
│  AI compares clinical data against payer criteria                │
│  → AI Recommendation: APPROVE (meets criteria)                   │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  ╔═══════════════════════════════════════════════════════════╗  │
│  ║   ISAGAWA AI MANAGEMENT LAYER - GATE #2                   ║  │
│  ║   CLINICAL DECISION VALIDATION GATE                       ║  │
│  ╚═══════════════════════════════════════════════════════════╝  │
│                                                                  │
│  PROTOCOL: PA Clinical Decision Review                          │
│  ───────────────────────────────────────                        │
│  1. Validate AI matched correct payer criteria                  │
│  2. Check for contraindications/red flags                       │
│  3. Verify evidence-based guidelines applied                    │
│  4. Detect bias in decision logic                               │
│                                                                  │
│  SMART GATE CHECKS:                                             │
│  ──────────────────                                             │
│  ✓ Clinical Safety:                                             │
│    • Contraindications checked? YES                             │
│    • Step therapy requirements met? YES (6 wks PT completed)    │
│    • Red flags present? NO                                      │
│                                                                  │
│  ✓ Regulatory Compliance:                                       │
│    • CMS guidelines followed? YES                               │
│    • Payer criteria correctly applied? YES                      │
│    • Evidence-based? YES (AAOS guidelines for shoulder MRI)     │
│                                                                  │
│  ✓ Bias Detection:                                              │
│    • Decision consistent across demographics? CHECKING...       │
│    • Historical approval rate for this scenario: 87%            │
│    • Current decision: APPROVE ✓ (consistent)                   │
│                                                                  │
│  ✓ Transparency Check:                                          │
│    • AI reasoning documented? YES                               │
│    • Criteria matched logged? YES (Anthem Policy MED-123)       │
│    • Appeal-ready documentation? YES                            │
│                                                                  │
│  DECISION: PASS → Proceed to submission                         │
│                                                                  │
│  📊 AUDIT LOG #2: Clinical decision validated, bias-free        │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  GEN AI FORM GENERATION & SUBMISSION                            │
│  AI generates payer-specific PA request                          │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  ╔═══════════════════════════════════════════════════════════╗  │
│  ║   ISAGAWA AI MANAGEMENT LAYER - GATE #3                   ║  │
│  ║   PRE-SUBMISSION VALIDATION GATE                          ║  │
│  ╚═══════════════════════════════════════════════════════════╝  │
│                                                                  │
│  PROTOCOL: PA Submission Quality Assurance                      │
│  ───────────────────────────────────────────                    │
│  1. Validate form completeness                                  │
│  2. Check documentation attachments                             │
│  3. Verify submission format (FHIR compliance)                  │
│  4. Confirm payer-specific requirements                         │
│                                                                  │
│  SMART GATE CHECKS:                                             │
│  ──────────────────                                             │
│  ✓ Form Completeness:                                           │
│    • All required fields populated? YES                         │
│    • Patient demographics accurate? YES                         │
│    • Provider NPI valid? YES                                    │
│                                                                  │
│  ✓ Documentation Quality:                                       │
│    • Clinical notes attached? YES                               │
│    • Imaging reports included? YES                              │
│    • Medical necessity narrative clear? YES                     │
│                                                                  │
│  ✓ Regulatory Compliance:                                       │
│    • HIPAA minimum necessary? YES                               │
│    • CMS interoperability (FHIR)? YES                           │
│    • State-specific requirements? YES (varies by state)         │
│                                                                  │
│  ✓ Submission Readiness:                                        │
│    • Payer portal requirements met? YES                         │
│    • Error probability: < 5% (acceptable)                       │
│    • Appeal documentation prepared? YES (precautionary)         │
│                                                                  │
│  DECISION: PASS → Submit to payer                               │
│                                                                  │
│  📊 AUDIT LOG #3: Submission validated, compliance-ready        │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  SUBMIT TO PAYER (via FHIR API)                                 │
│  PA request sent to payer for review                             │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  PAYER REVIEW (Payer-side AI)                                   │
│  Payer AI/staff reviews submission                               │
│  → DECISION: APPROVED                                            │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  ╔═══════════════════════════════════════════════════════════╗  │
│  ║   ISAGAWA AI MANAGEMENT LAYER - GATE #4                   ║  │
│  ║   POST-DECISION VALIDATION GATE                           ║  │
│  ╚═══════════════════════════════════════════════════════════╝  │
│                                                                  │
│  PROTOCOL: PA Decision Analysis & Learning                      │
│  ────────────────────────────────────────────                   │
│  1. Log decision outcome                                        │
│  2. Compare AI prediction vs actual payer decision              │
│  3. Update bias/fairness metrics                                │
│  4. Generate provider-facing explanation                        │
│                                                                  │
│  SMART GATE CHECKS:                                             │
│  ──────────────────                                             │
│  ✓ Decision Reconciliation:                                     │
│    • AI predicted: APPROVE                                      │
│    • Payer decided: APPROVED ✓ (match)                          │
│    • Model accuracy maintained                                  │
│                                                                  │
│  ✓ Audit Trail:                                                 │
│    • Complete decision history logged? YES                      │
│    • Explanation generated for provider? YES                    │
│    • Appeal documentation ready? N/A (approved)                 │
│                                                                  │
│  ✓ Bias Tracking:                                               │
│    • Approval rate by demographic tracked                       │
│    • No disparities detected                                    │
│                                                                  │
│  ✓ Continuous Improvement:                                      │
│    • Feedback loop to AI model: Decision validated              │
│    • Update criteria matching rules if needed                   │
│                                                                  │
│  OUTPUT: Provider notification + transparent explanation        │
│                                                                  │
│  📊 AUDIT LOG #4: Decision logged, audit trail complete         │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  PROVIDER NOTIFICATION (EHR Integration)                        │
│  ────────────────────────────────────────────────────────────    │
│  Provider sees in EHR:                                           │
│  ✅ APPROVED - MRI authorized                                    │
│                                                                  │
│  Isagawa Transparency Report:                                    │
│  • Payer criteria matched: Anthem Policy MED-123                │
│  • Clinical rationale: 6 weeks conservative therapy completed   │
│  • Supporting evidence: PT notes, X-ray (negative)              │
│  • Approval confidence: 95%                                      │
│  • Complete audit trail available for compliance review         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Isagawa Value Proposition for PA

| Metric | Current Gen AI | With Isagawa |
|--------|----------------|--------------|
| **Approval Rate** | Variable (some AI 16x higher denials) | Validated, consistent |
| **Transparency** | Black box | Full audit trail + explanation |
| **HIPAA Compliance** | Vendor-dependent | Enforced at every gate |
| **Bias Detection** | None | Real-time tracking |
| **Appeal Success** | Low (opaque decisions) | High (documented rationale) |
| **Regulatory Readiness** | Uncertain | CMS/state-compliant by design |
| **Provider Trust** | 61% fear unregulated AI | Trust via transparency |

---

## 5. Integration Architecture (DRAFT - Under Discussion)

### Option A: Middleware (API Gateway)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROVIDER SYSTEMS (EHR)                        │
│                     Epic | Cerner | Oracle                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               GEN AI PA PLATFORMS (Cohere/Rhyme)                │
│  • Data extraction   • Criteria matching   • Form generation    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Every API call intercepted
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│           ISAGAWA AI MANAGEMENT LAYER (Middleware)              │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  API Gateway                                              │ │
│  │  • Intercept PA vendor API calls                          │ │
│  │  • Route through validation gates                         │ │
│  │  • Return pass/fail + reason                              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  SMART GATES (Validation Engine)                          │ │
│  │  • Rule-based checks (HIPAA, completeness)                │ │
│  │  • AI-powered checks (bias, clinical validation)          │ │
│  │  • Audit logging                                          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Human Escalation Interface (Optional)                    │ │
│  │  • Gate fails → Notify PA coordinator                     │ │
│  │  • Coordinator reviews + overrides/fixes                  │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PAYER SYSTEMS                                 │
│         Anthem | UnitedHealth | Cigna | Aetna                   │
└─────────────────────────────────────────────────────────────────┘
```

**Pros:**
- No frontend UI needed
- No direct AI inference costs (PA vendor already has AI)
- Transparent to end users (invisible layer)
- Real-time validation
- Works with any PA vendor

**Cons:**
- Where does human intervene when gates fail?
- Requires PA vendor integration/buy-in
- Network latency concerns

### Option B: Human-in-the-Loop Terminal (QA Engine Style)

```
┌─────────────────────────────────────────────────────────────────┐
│  PA COORDINATOR (Human)                                         │
│  Uses Isagawa Terminal/CLI                                      │
│  Prompt: "Submit PA for John Doe shoulder MRI"                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│           ISAGAWA AI ORCHESTRATION                              │
│  (Similar to QA Engine 10-step workflow)                        │
│                                                                  │
│  1. Extract data from EHR (via API)                             │
│  2. GATE: Validate data quality                                 │
│  3. Match payer criteria (via PA vendor API or internal)        │
│  4. GATE: Validate clinical decision                            │
│  5. Generate PA form                                            │
│  6. GATE: Pre-submission validation                             │
│  7. Submit to payer                                             │
│  8. GATE: Post-decision analysis                                │
│                                                                  │
│  → Gates fail? Human prompted to fix/override                   │
└─────────────────────────────────────────────────────────────────┘
```

**Pros:**
- Clear human intervention model (same as QA Engine)
- More control/visibility for PA coordinators
- Easier to train/onboard

**Cons:**
- Slower (not real-time)
- Requires terminal/UI training
- Less automated than middleware

### Option C: Hybrid (Recommended - To Be Explored)

**90% automated (middleware) + 10% human review (escalation interface)**

```
Most PAs flow through middleware automatically
  ↓
Gate fails? → Notification to PA coordinator
  ↓
Coordinator reviews via dashboard/terminal
  ↓
Fix issue OR override with justification
  ↓
Resubmit through gates
```

---

## 6. Open Questions (Integration Architecture)

### Critical Decision Points:

1. **Human Interaction Model:**
   - QA Engine has terminal/CLI for human interaction
   - Is this core to Isagawa Platform or specific to QA vertical?
   - Healthcare PA: When/how do humans intervene?

2. **Frontend Requirements:**
   - Middleware approach = no frontend needed (ideal)
   - But what if gate fails? Email notification? Dashboard? Terminal?

3. **AI API Costs:**
   - If middleware, Isagawa doesn't generate content (PA vendor's AI does)
   - Isagawa only validates (rule-based + some AI-powered gates)
   - Which gates need AI? (bias detection, clinical validation, NLP)
   - Which are rule-based? (HIPAA, completeness, format validation)

4. **Integration Point:**
   - PA vendor embeds Isagawa SDK?
   - Health system deploys Isagawa middleware?
   - Both (multi-deployment model)?

5. **Pricing Model:**
   - Per-transaction (every PA through Isagawa)?
   - Enterprise license (flat fee per year)?
   - Revenue share with PA vendor?

---

## 7. Knowledge Gap Analysis: 80/20 Rule

### 80% - Mappable from Public Sources (COMPLETED)

**What we've already mapped:**

✅ **Workflow fundamentals:**
- Traditional PA process (8 steps)
- Current Gen AI PA process (Cohere/Rhyme model)
- Where Isagawa gates fit in workflow

✅ **Regulatory landscape:**
- CMS requirements (7-day standard, 72-hour expedited)
- HIPAA compliance requirements
- 2027 target (80% real-time approvals)
- State-specific variations exist (but need details)

✅ **Market context:**
- Market size ($1.55B → $45.82B trajectory)
- Adoption rates (75% of insurers use AI)
- Key vendors (Cohere, Rhyme, Innovaccer)
- Performance metrics (90% auto-approval, 5M+ auths/year)

✅ **Pain points:**
- 16x higher denial rates from some AI tools
- 61% physician distrust of unregulated AI
- Black box decision-making
- 82% of patients abandon treatment due to delays

✅ **Technical standards:**
- FHIR for interoperability
- HL7 for data exchange
- API-first architecture requirements

✅ **Integration approach:**
- Middleware positioning
- Rule-based vs AI-powered gates
- Human escalation patterns

### 20% - Needs SME Validation (GAPS)

**Critical gaps requiring practitioner insight:**

#### Gap 1: Real-World PA Coordinator Workflow
- **What we don't know:**
  - Actual daily workflow (vs documented process)
  - Time spent per PA type (imaging vs surgery vs meds)
  - Tools/systems they toggle between
  - Common workarounds when systems fail
  - What causes most frustration/delays
  - When they ACTUALLY call the payer vs submit via portal

- **Why it matters:**
  - Determines where Isagawa adds most value
  - Identifies which gates prevent real problems vs theoretical ones
  - Informs escalation interface design (dashboard vs email vs CLI)

- **SME needed:** PA coordinator at large health system (500+ PAs/month)

#### Gap 2: Vendor API Reality Check
- **What we don't know:**
  - What Cohere/Rhyme APIs actually look like (not just docs)
  - Where we'd actually intercept calls (request/response format)
  - Rate limits, latency expectations
  - Error handling patterns
  - Webhook vs polling for decision updates
  - Do vendors allow middleware? (Technical + contractual)

- **Why it matters:**
  - Determines MVP technical feasibility
  - Influences pricing (API call costs)
  - May reveal vendor lock-in challenges

- **SME needed:** Integration engineer who's built EHR ↔ PA vendor integrations

#### Gap 3: Payer-Specific Criteria Nuances
- **What we don't know:**
  - How much do criteria vary by payer? (Anthem vs UnitedHealth vs Cigna)
  - Are criteria machine-readable or human-judgment heavy?
  - How often do criteria change?
  - Where's the criteria source of truth? (vendor has it vs we need to scrape)
  - What's "gray area" that always needs human review?

- **Why it matters:**
  - Affects bias detection gate accuracy
  - Determines if we need payer-specific rules vs universal gates
  - Influences how often gates need updating

- **SME needed:** UM/PA policy expert at a payer OR consultant who advises multiple payers

#### Gap 4: What Buyers Actually Care About
- **What we don't know:**
  - Health system decision-makers: CFO vs CMIO vs CIO vs PA manager?
  - What metrics drive purchase decision? (cost savings vs compliance vs risk reduction)
  - Pricing expectations (per-transaction vs license vs revenue share)
  - Procurement process (pilot length, evaluation criteria)
  - Integration effort tolerance (weeks vs months)

- **Why it matters:**
  - Determines GTM strategy
  - Influences pricing model
  - Shapes MVP feature prioritization

- **SME needed:** Health system IT/operations leader who's purchased AI tools recently

#### Gap 5: Competitive Landscape Reality
- **What we don't know:**
  - Who else is building governance layers for healthcare AI?
  - What do existing "AI audit" vendors actually do? (surface level vs deep)
  - Why haven't Cohere/Rhyme built this themselves?
  - What's the "build vs buy" calculation for health systems?

- **Why it matters:**
  - Validates uniqueness of Isagawa approach
  - Identifies partnership vs competition opportunities
  - Reveals why market gap exists (technical vs business model vs just timing)

- **SME needed:** Healthcare AI consultant/analyst OR former PA vendor executive

### Recommended SME Engagement Strategy

**Option A: Paid Consultations (Fast, $$$)**
- Hire 2-3 SMEs via GLG, Guidepoint, or healthcare-specific networks
- 1-hour calls each ($300-$500/hour)
- **Total cost:** ~$1,500-$2,000
- **Timeline:** 1-2 weeks

**Option B: Free Advisory Conversations (Slow, $)**
- LinkedIn outreach to PA coordinators, integration engineers
- Offer to share findings in exchange for 30-min calls
- Hit-or-miss response rate
- **Total cost:** $0
- **Timeline:** 3-4 weeks

**Option C: Domain Expert Partnership (Strategic, Equity)**
- Bring on healthcare operations expert as advisor (0.5-1% equity)
- Ongoing access for product development
- Validates credibility with customers
- **Total cost:** Equity
- **Timeline:** 2-3 weeks to find, ongoing relationship

**Option D: Customer Discovery Interviews (Best, Free + Valuable)**
- Frame as "market research" not selling
- 10-15 calls with target customers (health system PA managers, IT leaders)
- Learn gaps AND validate buying interest simultaneously
- **Total cost:** $0
- **Timeline:** 3-4 weeks
- **Bonus:** Potential early adopters identified

**Recommendation:** ~~Start with **Option D** (customer discovery), supplement with **Option A** (1-2 paid SME calls) for technical gaps.~~

**UPDATED RECOMMENDATION:** Use **Pack Contributor Model** (per Isagawa Domain Expansion Model) + leverage existing healthcare network.

---

## 8. Leveraging Existing Healthcare Network

### Available Contacts

| Contact | Role | PA Relevance | How to Use |
|---------|------|--------------|------------|
| **Medical Assistants / Hospital Admin** | Front-line PA processing | **HIGH (80-90%)** | **Primary targets** - validate workflow, introduce to PA managers |
| **Nurse Consultant (cousin)** | Workflow structure + compliance | MEDIUM (10-20%) | If in utilization management/care coordination |
| **ER/OR Nurses (cousins)** | Ground-level clinical | LOW (0%) | ER bypasses PA, OR nurses don't touch admin |
| **Respiratory Tech** | Equipment protocols | MINIMAL (5%) | See PA denials for DME, don't process |
| **Podiatrist** | Outpatient clinic | LOW (0%) | Office staff processes PA, not doctor |
| **Radiology Tech** | Imaging workflows | MINIMAL (5%) | See PA denials, don't process |

### Strategy: Network → Pack Contributor Pipeline

```
Step 1: Informational Interviews (Medical Assistants/Admin)
  ↓
  Validate: Real-world PA workflow pain points
  ↓
Step 2: Request Introduction to PA Manager/Director
  ↓
  PA Manager = potential Pack Contributor candidate
  ↓
Step 3: Pack Contributor Partnership Discussion
  ↓
  Encode expertise → PA Pack v1.0 → Revenue share
```

### Conversation Guide: Medical Assistant/Admin Calls

**Context:** These are warm intro calls with your network contacts who work in hospital administration/medical assistant roles.

**Goal:** Validate the 20% knowledge gaps + get introduced to PA managers (Pack Contributor candidates).

---

#### Opening (2 min)

**Script:**
"Hey [Name], thanks for taking the time. I'm exploring a project around AI governance for prior authorization, and I wanted to get your perspective on how PA actually works day-to-day. I'm not selling anything - just trying to understand the real workflow and pain points. Is now still a good time?"

**Tone:** Casual, informational, not sales-y

---

#### Section 1: Current Workflow (5-7 min)

**Goal:** Understand their daily PA process vs documented process.

**Questions:**

1. **Volume & Types:**
   - "How many PA requests do you handle per day/week?"
   - "What types are most common? Imaging (MRI, CT), medications, procedures, surgeries?"
   - "Which types take the longest to process?"

2. **Tools & Systems:**
   - "What tools do you use to submit PAs?" (payer portals, clearinghouse, AI tools?)
   - "Have you heard of or used tools like Cohere Health, Rhyme, or other AI PA platforms?"
   - "How many different systems do you have to log into for one PA?" (EHR, payer portal, etc.)

3. **Time & Effort:**
   - "Walk me through the steps for a typical PA - like an MRI request."
   - "What takes the most time in that process?"
   - "What's the most frustrating part?"

4. **Real-World Workarounds:**
   - "When the system is slow or down, what do you do?"
   - "Are there any unofficial shortcuts or workarounds you use to get PAs through faster?"

---

#### Section 2: Pain Points & Failures (5-7 min)

**Goal:** Identify where current process breaks down.

**Questions:**

1. **Denials:**
   - "What percentage of your PAs get denied on first submission? (Rough guess)"
   - "What are the most common reasons for denial?"
   - "How do you know WHY a PA was denied? Is it clear from the payer?"

2. **Missing Information:**
   - "How often do you submit a PA and then realize you're missing something?"
   - "What documentation is hardest to find or gather?"

3. **Payer Differences:**
   - "Which insurance companies are easiest to work with for PA?"
   - "Which are the worst? Why?"
   - "Do different payers have totally different processes, or is it similar?"

4. **Delays:**
   - "What causes the longest delays in getting a PA approved?"
   - "How long does it typically take? (Hours, days, weeks?)"
   - "Do urgent/expedited PAs actually get processed faster?"

---

#### Section 3: AI/Automation Experience (3-5 min)

**Goal:** Understand current AI adoption and trust.

**Questions:**

1. **Current AI Tools:**
   - "Has your hospital started using any AI or automation for PA?"
   - "If yes: How's it working? Does it actually save time?"
   - "If no: Why not? What's holding you back?"

2. **Trust & Concerns:**
   - "If an AI tool suggested approving or denying a PA, would you trust it?"
   - "What would make you NOT trust it?"
   - "What would you want to see or know before trusting AI for PA?"

3. **Ideal Future State:**
   - "If you could wave a magic wand, what would the ideal PA process look like?"
   - "What parts should be automated vs require human review?"

---

#### Section 4: Decision-Makers & Introductions (3 min)

**Goal:** Get introduced to PA Manager/Director (Pack Contributor candidate).

**Questions:**

1. **Organizational Structure:**
   - "Who manages the PA team at your hospital?"
   - "Is there a PA coordinator or director role?"
   - "Who decides which tools/systems you use for PA?"

2. **Introduction Request:**
   - "Would your manager be open to a short call with me? I'm exploring how AI governance could help with PA compliance and transparency."
   - "I'm specifically looking for PA experts who might want to help shape how AI should work in this space - any chance your manager would be interested?"

---

#### Closing (1 min)

**Script:**
"This has been super helpful - thank you. A few quick things:
1. Can I follow up if I have clarifying questions?
2. Any chance you could intro me to your PA manager?
3. Would you be open to reviewing a demo once we build something?

I really appreciate your time. This kind of ground-level insight is exactly what I needed."

---

#### Post-Call: Document Findings

**Capture:**
- Volume: X PAs per day/week
- Time: X minutes/hours per PA type
- Tools: Current systems used
- Pain points: Top 3 frustrations
- Payer differences: Easiest vs hardest
- AI experience: Current adoption + trust level
- **Manager name:** [Name, title, contact if provided]
- **Introduction status:** Warm intro requested? (Yes/No)

---

### Target Outcome from Network Calls

**After 2-3 Medical Assistant/Admin interviews:**

✅ Validated the 20% knowledge gaps (real workflow, pain points, tools)
✅ Identified 1-2 PA Managers as Pack Contributor candidates
✅ Warm introductions to decision-makers
✅ Ground-level validation that PA problems are real and urgent

**Next Step:** Pack Contributor partnership discussion with PA Manager.

---

## 9. Pack Contributor Engagement (Revised Strategy)

### Why Pack Contributor Model (Not Paid Consultations)

**Per Isagawa Domain Expansion Model:**

| Approach | Why It Doesn't Work | Isagawa Way |
|----------|---------------------|-------------|
| Paid SME consultations ($500/hr) | Transactional, no ongoing alignment | **Pack Contributor partnership** |
| Hire full-time PA expert | Expensive, non-leveraged | **Encode expertise, share pack revenue** |
| Generic customer discovery | Surface insights, no depth | **Deep expertise extraction over 4-6 weeks** |

**Pack Contributor = Long-term partner who provides expertise artifacts, earns revenue as PA Pack scales.**

### Ideal Pack Contributor Profile (PA Vertical)

**Required:**
- 10+ years as PA coordinator/manager at large health system (500+ PAs/month)
- Deep knowledge of:
  - Real-world PA workflow (not just policy)
  - Payer-specific nuances (Anthem vs UnitedHealth vs Cigna)
  - Escalation decision-making (when human review needed)
  - What actually causes denials/delays
- Strong opinions on "the correct way" PA should work
- Interest in **leverage** (revenue share) not **operations** (hourly work)

**Non-required:**
- Software development skills
- AI/ML knowledge
- Product architecture authority

**Where to find:**
- Introduced via medical assistant/admin network
- Recently retired PA managers (still sharp, no longer full-time)
- PA consultants who advise multiple health systems
- LinkedIn/healthcare ops communities

### What Pack Contributor Provides (Expertise Artifacts)

| Artifact | Maps to PA Pack Component |
|----------|---------------------------|
| **Canonical PA workflows** | Enforced workflow steps for each PA type (imaging, surgery, meds, DME) |
| **Required validation steps** | Smart gates (HIPAA, data completeness, bias detection, clinical validation) |
| **Escalation boundaries** | When to auto-approve vs human review vs auto-deny |
| **Decision criteria** | Payer-specific rules (what qualifies for approval vs denial) |
| **Payer variation mapping** | How Anthem differs from UnitedHealth, Cigna, etc. |
| **Approved workflow variants** | Different paths for different PA types/urgency levels |
| **Safe variance fields** | What customers can configure (thresholds, timeout rules) |
| **Ongoing validation** | Monthly/quarterly review as payer rules evolve |

### What Isagawa Retains (Non-Negotiable)

- 100% ownership of middleware architecture
- 100% ownership of gate enforcement engine
- 100% ownership of PA Pack code (derived work)
- All customer relationships and billing
- Product roadmap, pricing, and packaging
- Branding and positioning

**Pack Contributor licenses expertise, NOT technology.**

### Incentive Structure

**Platform Revenue (100% Isagawa):**
- Middleware licensing
- Core gate engine
- Infrastructure fees

**PA Pack Revenue (Shared with Pack Contributor):**
- Pack-specific licensing fees
- Example split: 70/30 or 80/20 (Isagawa/Pack Contributor)
- Pack Contributor earns revenue as long as customers use the PA Pack
- No equity, no governance rights, no perpetual obligations

**Example:**
- Customer pays $2.00 per PA transaction
- $1.00 = Platform fee (100% Isagawa)
- $1.00 = PA Pack fee (70% Isagawa, 30% Pack Contributor)
- Pack Contributor earns $0.30 per PA processed through their pack
- At 10K PAs/month = $3K/month passive income to Pack Contributor

---

## 10. Next Steps - Validation Roadmap (Updated)

### Phase 1: Network Validation (1-2 weeks)
- [x] Document existing healthcare network contacts
- [ ] Schedule 2-3 calls with Medical Assistants/Admin
- [ ] Conduct informational interviews (use conversation guide)
- [ ] Document findings (validate 20% knowledge gaps)
- [ ] Request introductions to PA Managers

### Phase 2: Pack Contributor Identification (2-3 weeks)
- [ ] Meet with 2-3 PA Manager candidates (warm intros from network)
- [ ] Assess Pack Contributor fit (expertise depth, interest in model)
- [ ] Select primary Pack Contributor partner
- [ ] Draft partnership agreement (revenue share, scope, deliverables)

### Phase 3: Expertise Extraction (4-6 weeks)
- [ ] Week 1-2: Map canonical PA workflows (traditional + Gen AI variations)
- [ ] Week 3-4: Define validation gates (what should block submission?)
- [ ] Week 5-6: Build escalation rules (when human intervention needed)
- [ ] Deliverable: **PA Pack v1.0** (protocols + smart gates)

### Phase 4: Customer Validation (2-3 weeks)
- [ ] Leverage Pack Contributor's network for warm intros
- [ ] Demo PA Pack v1.0 to 5-10 PA coordinators/managers
- [ ] Collect feedback: "Would this solve your problems? What's missing?"
- [ ] Identify 2-3 early adopter candidates

### Phase 5: MVP Development (TBD)
- [ ] Build middleware architecture
- [ ] Implement PA Pack v1.0 (protocols + gates)
- [ ] Develop minimal escalation interface (notifications or dashboard)
- [ ] Pilot with 1-2 early adopters

---

## Sources

- [2026 Healthcare AI Trends - Wolters Kluwer](https://www.wolterskluwer.com/en/expert-insights/2026-healthcare-ai-trends-insights-from-experts)
- [AI in Healthcare 2026 Predictions - Chief Healthcare Executive](https://www.chiefhealthcareexecutive.com/view/ai-in-health-care-26-leaders-offer-predictions-for-2026)
- [Generative AI in Healthcare - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11739231/)
- [Prior Authorization Guide - Myndshft](https://www.myndshft.com/the-ultimate-guide-to-prior-authorization/)
- [CMS Prior Authorization Updates 2025](https://www.cms.gov/data-research/monitoring-programs/medicare-fee-service-compliance-programs/prior-authorization-and-pre-claim-review-initiatives)
- [Cohere Health AI-Powered PA](https://www.coherehealth.com/utilization-management-suite)
- [Cohere, Rhyme, Medical Mutual Partnership](https://www.prnewswire.com/news-releases/cohere-health-medical-mutual-and-rhyme-partner-on-utilization-management-transformation-302162495.html)
- [Top 5 AI PA Vendors 2025 - Innovaccer](https://innovaccer.com/blogs/top-5-ai-vendors-for-prior-authorization-2025)
- [How AI is Leading to More PA Denials - AMA](https://www.ama-assn.org/practice-management/prior-authorization/how-ai-leading-more-prior-authorization-denials)
- [AI in Medical Coding & Billing 2025 - TopFlight Apps](https://topflightapps.com/ideas/ai-in-medical-billing-and-coding/)
- [AI Transforming Medical Billing 2025 - Zmed Solutions](https://www.zmedsolutions.net/how-artificial-intelligence-is-transforming-medical-billing-and-coding-in-2025/)

---

**Document Status:** Living document - Updated as integration architecture clarifies

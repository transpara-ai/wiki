---
entity: Gate K
aliases: [gate-k, Gate K, interim loop hardened, development loop hardened]
tier: architecture
status: compiled
last_compiled: "2026-06-17"
sources:
  - raw/transpara/dark-factory/v4.0/implementation/epics/00-integration-arc-v4.0.md  # DF-V4.0-INTEGRATION-ARC — Gate K definition, "satisfied only when" predicate, sequencing, guardrails, authorization boundary
  - raw/transpara/dark-factory/v4.0/01-development-process-as-governed-civilization-function-v4.0.md  # DF-V4.0-ADR-001 — seed doctrine; authorization boundary carries Gates K and L as defined-but-unsatisfied
  - raw/transpara/dark-factory/v4.0/checkpoint-2026-06-12-v4.0-doctrine-acceptance.md  # DF-V4.0-CKPT-2026-06-12-ACCEPTANCE — acceptance scope; "What This Acceptance Does Not Do" confirms K unsatisfied
  - raw/open-brain/2026-06.md  # L76, L111, L124, L134 — Gate K design and review process, AC-K lettering, cross-family review disposition
  - raw/transpara/dark-factory/v4.0/implementation/epics/epic-01-interim-loop-hardening/01-interim-loop-hardening-design-v4.0.md  # DF-V4.0-EPIC-001-DESIGN — requirements R-K1..K4, acceptance criteria AC-K1..K6 with verification_method, risk_class, required_evidence
  - raw/transpara/dark-factory/v4.0/implementation/epics/epic-01-interim-loop-hardening/02-interim-loop-hardening-authorization-v4.0.md  # DF-V4.0-EPIC-001 authorization — Event-1 AuthorityDecision granted (Notify) 2026-06-15, recorded via transpara-ai/docs#132
  - raw/transpara/dark-factory/v4.0/implementation/epics/epic-01-interim-loop-hardening/03-gate-k-evidence-reconciliation-v4.0.md  # Gate-K evidence reconciliation — AC-K1/AC-K3 predicate reconciliation still open, transpara-ai/docs#133
  - raw/transpara/dark-factory/v4.0/implementation/epics/epic-01-interim-loop-hardening/04-gate-k-disposition-v4.0.md  # Gate-K guardrail disposition — AC-K2/AC-K4 negative-test evidence + cross-family status-poster/app-pinning residual open, transpara-ai/docs#134
  - raw/transpara/dark-factory/v4.0/implementation/epics/epic-01-interim-loop-hardening/06-ac-k5-attestation-disposition-v4.0.md  # Historical pre-waiver AC-K5 attestation disposition — keeps AC-K5 and Gate K not satisfied as vendor evidence, transpara-ai/docs#137
  - raw/transpara/dark-factory/v4.0/implementation/epics/epic-01-interim-loop-hardening/07-gate-k-pre-go-live-waiver-v4.0.md  # Gate K pre-go-live waiver and closeout disposition, transpara-ai/docs#138 (merge f8ed4a9dc4612d56959f9f8b5d398c4f58b3655d)
confidence:
  sources: primary
  claims: grounded
---

# Gate K

**The first v4.0 program gate.** Gate K is the evidence predicate that the interim development loop has been hardened — meaning the controls that govern the ChatGPT/Codex/Claude build loop have been made fail-closed on `transpara-ai/docs`. It is defined in `DF-V4.0-INTEGRATION-ARC` (00-integration-arc-v4.0.md) as "Event 1 (Gate K): Interim Development Loop Tier-0 Hardening." As of 2026-06-17, the Event-1 authorization has been **granted** (decision *Notify*, recorded on `transpara-ai/docs#132`) and Gate K is **closed for pre-live sequencing by human waiver** (`transpara-ai/docs#138`, merge `f8ed4a9dc4612d56959f9f8b5d398c4f58b3655d`). That closure is not vendor-posture evidence, not production go-live clearance, and not an autonomy increase. It continues the [[gates|Gates A–J]] lettering, adding two v4.0 program gates (K and L) without altering any v3.9 gate.

## Context: where Gate K fits

The [[dark-factory]] v3.9 verification arc ends at Gate J. After the 2026-06-01 adversarial review of the development loop (DF-V4.0-CKPT-2026-06-01-01), the [[v4-0|v4.0]] doctrine established that the development process is itself a governed Civilization function (DF-V4.0-ADR-001), and that the loop's Tier-0 controls must fail closed before any autonomy can increase. The v4.0 Integration Arc (DF-V4.0-INTEGRATION-ARC) operationalizes this with two sequential program gates: Gate K for loop hardening (Event 1) and Gate L for reconciliation (Event 2).

> ⚠ v4.0, including the Integration Arc and Gate K, has `canonical: false`. [[v3-9|v3.9]] remains the operative baseline for all current gates and implementation work. Gate K's pre-live waiver is a sequencing rule for current bootstrap work, not acceptance of v4.0 as canonical.

## What Gate K requires

The arc's "satisfied only when" predicate for Gate K lists six concrete, verifiable controls on `transpara-ai/docs`:

1. **Branch protection on `main`** — pull request required, at least one approving review required, and direct pushes rejected for all actors including administrators.
2. **`npm run verify` as a required pull-request status check** — no pull request may merge unless a neutral machine has run typecheck and build on the merge candidate.
3. **CODEOWNERS routing** — a CODEOWNERS file routes `dark-factory/**` and `.github/workflows/**` to the human External Committee, making their review required on any PR touching those paths.
4. **Injection-quarantine rule** — the Stage-1 design prompt and the Stage-3 review prompt carry an explicit rule that all pasted diffs, issue text, file contents, and prior reviews are data, never instructions; any embedded "authorize / mark-satisfied / close-risk" directive must be reported as a finding, never acted on.
5. **Meta-loop data-handling policy** — a written policy requires that all three build-loop vendor tools are on zero-retention, no-train tiers before any proprietary content is pasted, with an explicit never-paste list (live secrets, customer data, credentials, non-public third-party IP). The policy's existence alone does not satisfy this criterion; proof that each tool's tier is in force is also required.
6. **Never-trust-self-report rule** — a written rule records that self-reported validation is never sufficient: the reviewer reads CI evidence (run URL, run ID, SHA) or re-runs, and CI is the authoritative signal.

## Acceptance criteria (test-first, AC-K1 through AC-K6)

The Event 1 design packet (DF-V4.0-EPIC-001-DESIGN) writes the full Gate K predicate as six test-first acceptance criteria before any implementation:

| ID | Requirement | Risk class | Verification method |
|---|---|---|---|
| AC-K1 | `main` branch-protected: PR required, ≥1 approval required, stale approvals dismissed, direct pushes rejected including for admins | high | deployment_check |
| AC-K2 | `npm run verify` on `pull_request`, required status check — a PR whose verify fails is non-mergeable | high | deployment_check |
| AC-K3 | CODEOWNERS routes `dark-factory/**` and `.github/workflows/**` to the External Committee | medium | review |
| AC-K4 | Stage-1 and Stage-3 prompts carry injection-quarantine rule; embedded directives reported as findings | high | review |
| AC-K5 | Data-handling policy exists AND zero-retention/no-train posture of each tool is shown to be in force | high | review |
| AC-K6 | Written rule that self-reported validation is never sufficient; CI is the authoritative signal | medium | review |

Each criterion carries a `required_evidence` field; evidence must exist before Gate K can be called satisfied. The design packet states: "the criteria below ARE the Gate K predicate, expressed as the tests that must pass."

> ⚠ AC-K5 is the most operationally demanding: a written policy alone does not close it. For each of the three vendor tools a contract, DPA, or account-settings reference (or a named Operator-or-Security attestation) must confirm zero-retention and no-train in force. If that proof cannot be produced, the criterion records a premise failure rather than allowing proprietary content to be pasted.

The pre-live waiver changes the sequencing disposition, not the evidence record. AC-K5 remains unproven as vendor posture; the waiver lets routine first-party repository-development and infrastructure/design content continue during the founder-led pre-live bootstrap under a never-paste boundary. Live secrets, customer data, credentials, credential-bearing configuration, non-public third-party IP, customer-facing production material, autonomous runtime ingestion, production go-live, protected execution, value allocation, and autonomy increases remain outside the waiver.

## Current status

The acceptance checkpoint (DF-V4.0-CKPT-2026-06-12-ACCEPTANCE, 2026-06-12) contains a section "What This Acceptance Does Not Do" that states explicitly: *"Gates K and L remain defined and unsatisfied. No gate advances."* The Tier-0 structural guards adopted at that checkpoint (branch protection CODEOWNERS, `npm run verify` workflow, injection-quarantine rule, never-trust-self-report rule) were prerequisites for Gate K but were adopted as interim-loop standing rules, not as Gate K evidence.

The authorization packet for Event 1 (DF-V4.0-EPIC-001) originally carried a `PENDING` AuthorityDecision — merging the packet scoped the event, it did not grant it. On 2026-06-15 the human External Committee **granted** Event 1: the decision (`Notify`; Michael Saucier acting for the Committee, with the two-human approval waived for this bounded Level-0 grant) was recorded on `transpara-ai/docs` main via #132, and the Gate-K meta-loop proposal artifacts merged via #115.

On 2026-06-17, docs#138 merged the explicit pre-live waiver at merge commit `f8ed4a9dc4612d56959f9f8b5d398c4f58b3655d`. The current state is:

| Boundary | State |
|---|---|
| Pre-live repository-development sequencing | **Closed by human waiver**. N5/Gate K no longer blocks current pre-live docs/Civilization work that has its own authority and review evidence. |
| Vendor zero-retention / no-train evidence | **Not satisfied as vendor evidence**. ChatGPT Extended Pro, Codex CLI, and Claude Max remain UNKNOWN / not vendor-posture attested in the AC-K5 record. |
| Live Civilization data boundary / go-live | **Blocked until revalidated**. Production go-live, customer operation, customer data, secrets, protected runtime execution, value allocation, and autonomy increases require the missing evidence, stronger replacement controls, or a production-grade human waiver. |

## Sequencing and gate failure rule

The arc's sequencing rule is: Event 1 (Gate K) should precede any event that raises the development process above its current bootstrap autonomy level, because Operating Principle #10 requires that "autonomy expands only after audit expands," and Gate K is what makes the loop's controls auditable and fail-closed. The pre-live waiver removes the N5 blocker only for current bootstrap work. Gate L (Event 2, documentation reconciliation) may proceed in parallel because it carries no autonomy implication.

If Gate K fails at go-live revalidation, the correct go-live state is blocked. Allowed responses are to provide the missing evidence, replace a control with a stronger one, record a production-grade accepted risk with owner and rationale, or ask the External Committee to re-sequence. Forbidden: silently treating the pre-live waiver as production clearance, renaming missing evidence as satisfied, or weakening guardrails to force the gate to pass.

## Lettering note

The gates article ([[gates]]) flags a potential lettering collision: v3.9 uses letters A through J for its accountability-pipeline milestones; v4.0 adds K and L as program gates for a different scope (the integration arc, not factory-capability milestones). Open Brain records (2026-06-01 review, L111/L124) note this collision was raised during same-family review and reviewed by Codex (cross-family), which raised no finding. The two gate vocabularies coexist without formal collision, but they are distinct in scope, predicate structure, and satisfaction criteria.

## Related entities

- [[gates]] — the full gate system; Gates A–J are the v3.9 arc this article extends.
- [[gate-l|Gate L]] — the companion v4.0 gate for v3.9-to-v4.0 reconciliation (Event 2).
- [[v4-0]] — the v4.0 doctrine and integration arc context. ⚠ Forward reference.
- [[dark-factory]] — the governed production system whose development loop Gate K hardens.
- [[the-reunification]] — the broader reunification of the development process into the Civilization. ⚠ Forward reference.
- [[authority-layer]] — protected actions (including gate satisfaction) require authority evidence, not self-report.
- [[event-graph]] — remains the source of truth for evidence, authority, and gate state per the arc's global guardrails.

## Sources & provenance

- **Primary:** `raw/transpara/dark-factory/v4.0/implementation/epics/00-integration-arc-v4.0.md` (DF-V4.0-INTEGRATION-ARC) — Gate K definition, "satisfied only when" six-point predicate (§ "Gate K"), pre-live disposition, gate failure rule, sequencing rule, authorization boundary, global guardrails, and the Event 1 packet pointer. Read in full this compilation.
- **Primary:** `raw/transpara/dark-factory/v4.0/implementation/epics/epic-01-interim-loop-hardening/01-interim-loop-hardening-design-v4.0.md` (DF-V4.0-EPIC-001-DESIGN) — requirements R-K1..K4, acceptance criteria AC-K1..K6 with `verification_method`, `risk_class`, and `required_evidence` fields. Read lines 1–100 this compilation.
- **Primary:** `raw/transpara/dark-factory/v4.0/01-development-process-as-governed-civilization-function-v4.0.md` (DF-V4.0-ADR-001) — authorization boundary and "advances no gate" clause. Read in full this compilation.
- **Primary:** `raw/transpara/dark-factory/v4.0/checkpoint-2026-06-12-v4.0-doctrine-acceptance.md` (DF-V4.0-CKPT-2026-06-12-ACCEPTANCE) — "Gates K and L remain defined and unsatisfied" (§ "What This Acceptance Does Not Do"). Read in full this compilation.
- **Secondary:** `raw/open-brain/2026-06.md` — L76 (arc doc summary, Gate K definition quote), L111 (lettering collision concern raised in same-family review), L124 (Codex found no lettering-collision finding, item closed), L134 (merged PRs #79 and #80 with Gates K/L arc). Read lines 60–143 this compilation.
- **Context:** `wiki/gates.md` — existing Gates A–J article (tier: architecture, compiled 2026-06-13) read in full for cross-linking and house style.

- **Live state (2026-06-17):** `transpara-ai/docs#132` (Event-1 / Gate-K authority grant, decision *Notify*), `#133` (Gate-K evidence reconciliation — AC-K1/AC-K3), `#134` (Gate-K guardrail disposition — AC-K2/AC-K4 plus the cross-family status-poster / app-pinning residual), `#137` (AC-K5 attestation disposition), and `#138` (Gate K pre-go-live waiver and closeout disposition, merge `f8ed4a9dc4612d56959f9f8b5d398c4f58b3655d`). These merged docs PRs post-date the cited raw checkpoint sources and ground the current pre-live-closed / go-live-blocked split; the matching epic-01 packets (02/03/04/06/07) are listed in frontmatter `sources:`.

No Searles-post URL applies to Gate K; it is a v4.0 Dark Factory engineering construct with no upstream post provenance. `[[wikilinks]]` marked ⚠ are forward references to articles not yet compiled.

---
entity: Gate K
aliases: [gate-k, Gate K, interim loop hardened, development loop hardened]
tier: architecture
status: compiled
last_compiled: "2026-06-14"
sources:
  - raw/transpara/dark-factory/v4.0/implementation/epics/00-integration-arc-v4.0.md  # DF-V4.0-INTEGRATION-ARC — Gate K definition, "satisfied only when" predicate, sequencing, guardrails, authorization boundary
  - raw/transpara/dark-factory/v4.0/01-development-process-as-governed-civilization-function-v4.0.md  # DF-V4.0-ADR-001 — seed doctrine; authorization boundary carries Gates K and L as defined-but-unsatisfied
  - raw/transpara/dark-factory/v4.0/checkpoint-2026-06-12-v4.0-doctrine-acceptance.md  # DF-V4.0-CKPT-2026-06-12-ACCEPTANCE — acceptance scope; "What This Acceptance Does Not Do" confirms K unsatisfied
  - raw/open-brain/2026-06.md  # L76, L111, L124, L134 — Gate K design and review process, AC-K lettering, cross-family review disposition
  - raw/transpara/dark-factory/v4.0/implementation/epics/epic-01-interim-loop-hardening/01-interim-loop-hardening-design-v4.0.md  # DF-V4.0-EPIC-001-DESIGN — requirements R-K1..K4, acceptance criteria AC-K1..K6 with verification_method, risk_class, required_evidence
confidence:
  sources: primary
  claims: grounded
---

# Gate K

**The first v4.0 program gate.** Gate K is the evidence predicate that the interim development loop has been hardened — meaning the controls that govern the ChatGPT/Codex/Claude build loop have been made fail-closed on `transpara-ai/docs`. It is defined in `DF-V4.0-INTEGRATION-ARC` (00-integration-arc-v4.0.md) as "Event 1 (Gate K): Interim Development Loop Tier-0 Hardening." As of 2026-06-14, Gate K is **defined and unsatisfied.** It continues the [[gates|Gates A–J]] lettering, adding two v4.0 program gates (K and L) without altering any v3.9 gate.

## Context: where Gate K fits

The [[dark-factory]] v3.9 verification arc ends at Gate J. After the 2026-06-01 adversarial review of the development loop (DF-V4.0-CKPT-2026-06-01-01), the [[v4-0|v4.0]] doctrine established that the development process is itself a governed Civilization function (DF-V4.0-ADR-001), and that the loop's Tier-0 controls must fail closed before any autonomy can increase. The v4.0 Integration Arc (DF-V4.0-INTEGRATION-ARC) operationalizes this with two sequential program gates: Gate K for loop hardening (Event 1) and [[gate-l|Gate L]] for reconciliation (Event 2).

> ⚠ v4.0, including the Integration Arc and Gate K, has `canonical: false`. [[v3-9|v3.9]] remains the operative baseline for all current gates and implementation work. Gate K is a candidate predicate, not an operative one.

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

## Current status

The acceptance checkpoint (DF-V4.0-CKPT-2026-06-12-ACCEPTANCE, 2026-06-12) contains a section "What This Acceptance Does Not Do" that states explicitly: *"Gates K and L remain defined and unsatisfied. No gate advances."* The Tier-0 structural guards adopted at that checkpoint (branch protection CODEOWNERS, `npm run verify` workflow, injection-quarantine rule, never-trust-self-report rule) are direct prerequisites for Gate K but were adopted as interim-loop standing rules, not as Gate K evidence. Gate K is formally satisfied only when the named test cases pass with recorded evidence.

The authorization packet for Event 1 (DF-V4.0-EPIC-001) carries a `PENDING` AuthorityDecision. Merging the packet scopes the event; it does not grant it. Implementation may not begin until the human External Committee records the AuthorityDecision.

## Sequencing and gate failure rule

The arc's sequencing rule is: Event 1 (Gate K) should precede any event that raises the development process above its current bootstrap autonomy level, because Operating Principle #10 requires that "autonomy expands only after audit expands," and Gate K is what makes the loop's controls auditable and fail-closed. Gate L (Event 2, documentation reconciliation) may proceed in parallel because it carries no autonomy implication.

If Gate K fails, work must not continue to Event 2 (in the sense of any autonomy-raising step). Allowed responses to gate failure: fix within the event scope, create a precise blocker issue, record accepted risk with owner and rationale, or ask the External Committee to re-sequence. Forbidden: silently moving to the next event, renaming the failure as non-blocking without rationale, or weakening guardrails to force the gate to pass.

## Lettering note

The gates article ([[gates]]) flags a potential lettering collision: v3.9 uses letters A through J for its accountability-pipeline milestones; v4.0 adds K and L as program gates for a different scope (the integration arc, not factory-capability milestones). Open Brain records (2026-06-01 review, L111/L124) note this collision was raised during same-family review and reviewed by Codex (cross-family), which raised no finding. The two gate vocabularies coexist without formal collision, but they are distinct in scope, predicate structure, and satisfaction criteria.

## Related entities

- [[gates]] — the full gate system; Gates A–J are the v3.9 arc this article extends.
- Gate L — the companion v4.0 gate for v3.9-to-v4.0 reconciliation (Event 2). Not yet compiled as of 2026-06-14.
- [[v4-0]] — the v4.0 doctrine and integration arc context. ⚠ Forward reference.
- [[dark-factory]] — the governed production system whose development loop Gate K hardens.
- [[the-reunification]] — the broader reunification of the development process into the Civilization. ⚠ Forward reference.
- [[authority-layer]] — protected actions (including gate satisfaction) require authority evidence, not self-report.
- [[event-graph]] — remains the source of truth for evidence, authority, and gate state per the arc's global guardrails.

## Sources & provenance

- **Primary:** `raw/transpara/dark-factory/v4.0/implementation/epics/00-integration-arc-v4.0.md` (DF-V4.0-INTEGRATION-ARC) — Gate K definition, "satisfied only when" six-point predicate (§ "Gate K"), gate failure rule, sequencing rule, authorization boundary, global guardrails, and the Event 1 packet pointer. Read in full this compilation.
- **Primary:** `raw/transpara/dark-factory/v4.0/implementation/epics/epic-01-interim-loop-hardening/01-interim-loop-hardening-design-v4.0.md` (DF-V4.0-EPIC-001-DESIGN) — requirements R-K1..K4, acceptance criteria AC-K1..K6 with `verification_method`, `risk_class`, and `required_evidence` fields. Read lines 1–100 this compilation.
- **Primary:** `raw/transpara/dark-factory/v4.0/01-development-process-as-governed-civilization-function-v4.0.md` (DF-V4.0-ADR-001) — authorization boundary and "advances no gate" clause. Read in full this compilation.
- **Primary:** `raw/transpara/dark-factory/v4.0/checkpoint-2026-06-12-v4.0-doctrine-acceptance.md` (DF-V4.0-CKPT-2026-06-12-ACCEPTANCE) — "Gates K and L remain defined and unsatisfied" (§ "What This Acceptance Does Not Do"). Read in full this compilation.
- **Secondary:** `raw/open-brain/2026-06.md` — L76 (arc doc summary, Gate K definition quote), L111 (lettering collision concern raised in same-family review), L124 (Codex found no lettering-collision finding, item closed), L134 (merged PRs #79 and #80 with Gates K/L arc). Read lines 60–143 this compilation.
- **Context:** `wiki/gates.md` — existing Gates A–J article (tier: architecture, compiled 2026-06-13) read in full for cross-linking and house style.

No Searles-post URL applies to Gate K; it is a v4.0 Dark Factory engineering construct with no upstream post provenance. `[[wikilinks]]` marked ⚠ are forward references to articles not yet compiled.

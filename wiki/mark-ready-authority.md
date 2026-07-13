---
entity: The Mark-Ready Authority Model
aliases: [mark-ready authority, pull_request.mark_ready, the finalizer guardrails, managed ready-PR finalizer, hive#263 guardrails]
tier: architecture
status: compiled
last_compiled: "2026-07-12"
sources:
  - raw/open-brain/2026-07.md  # L3668 (implementation), L3674/L3680/L3686 (the CFAR repair-round records), L3692 (arc completion, 8 rounds to zero), L3698 (merge + strict-protection lesson)
confidence:
  sources: primary — the merged code and the Factory Order that governed it, plus the session record of the eight review rounds.
  claims: grounded; the review-arc narrative (findings per round, subtractions) is from the Open Brain record of the authoring session, cross-checked against the FO's versioned repair sections.
---

# The Mark-Ready Authority Model

**The protected-action model for the managed draft→ready PR transition in [[hive-governance|the hive]].** Merged 2026-07-11 as `transpara-ai/hive#272` (closing hive#263), it makes the last autonomous step of the issue-scan lifecycle — flipping a governed draft PR to "ready for review" — a separately-authorized, single-use, provenance-bound human grant. Before this change, `RunIssueScanReadyPRFinalizer` called GitHub's mark-ready mutation with **no approval check at all**: a draft-PR *creation* approval implicitly carried the readying too.

## The authority chain

The merged model enforces, in order, with every step fail-closed:

1. **A distinct recorded action** — `pull_request.mark_ready` joins the protected-action vocabulary through `safety.RepoProtectedActions`, a repo-narrower extension that leaves the pinned DF-SOP-0001 baseline untouched. A draft-PR creation approval never authorizes readying.
2. **Human-decided, unexpired, exactly-matching** — the lookup scans recorded authority decisions newest-first and accepts only an approved decision whose `DeciderRole` is human, whose finite `ExpiresAt` (if any) has not passed, and whose scope matches the run-derived repository, PR number, and head SHA exactly. Non-human records can neither authorize nor shadow a human decision; a *malformed* newest record **revokes** rather than falling through to older authority.
3. **Durable single-use consumption before the mutation** — a nonce-keyed Work artifact, scanned across the whole store (one human approval is one transition, cross-run), claimed race-safely by append-then-verify-winner over the event chain's total order. A consumed nonce never authorizes again; a stalled run needs a fresh human approval.
4. **Authority-currency re-check** — immediately before the GraphQL call, the lookup re-resolves and must return *exactly* the consumed approval, so an expiry lapsing or a newer human decision landing during the consumption scans refuses.
5. **Provenance-bound remediation** — the client reports whether *this invocation* issued the managed mutation. Re-drafting after a failed ready-state review runs only under the approval's recorded `re_draft_on_failure` flag, only for a transition this run provably performed, and **never over an explicit human approval** (enforced at both the finalizer and the live client). Post-dispatch failures preserve indeterminacy: no client-side read can prove mutation provenance, so they record blocked evidence and decline the re-draft.
6. **Blocked evidence is terminal** — once a blocked artifact exists on the ready stage, the managed chain refuses to re-run the finalizer until a human remediates.

## How it was hardened

The model above is not the first draft — it is the survivor of an eight-round cross-family review (Codex reviewing Claude-authored work) that found 18 defects, all dispositioned. The review's most instructive catch came in round 1: the Factory Order originally *deferred* durable nonce consumption, arguing the draft-state precondition made reuse structurally impossible — but a re-draft returns the PR to draft state, so the structural argument failed exactly on the remediation path. Two later mechanisms (a same-run re-entry allowance, a post-failure reconcile inference) were **withdrawn by subtraction** when subsequent rounds proved them unsound, leaving the final gate simpler than its round-3 form. One residual is named rather than closed: the approval-vs-re-draft race on GitHub's non-transactional API, bounded and reversible, documented in the FO.

The follow-on chip from this arc — enforcing `ExpiresAt` on the *draft-PR creation* path, which shared the expiry gap — merged the next day as `transpara-ai/hive#280`.

## Relation to the wider system

The model instantiates, in running code, the accountability questions the [[dark-factory]] doctrine asks of every material action: who asked, who acted, under what authority, with what evidence, with what residual risk. It is the hive's first protected action whose *undo* path carries its own authority test — "may I undo?" is not implied by "may I do?" — a distinction the [[gates|gate discipline]] had previously only stated in prose.

## Primary references

On-Platform primary sources for this article (governed docs and code;
not web-served — open them from the Transpara workspace):

- `/Transpara/transpara-ai/repos/hive/docs/factory-orders/FO-hive-263-finalizer-guardrails-v0.9.0.md` — FO-HIVE-263 final v0.9.0 — requirements R1–R8, the two reversals-by-subtraction, the named irreducible residual
- `/Transpara/transpara-ai/repos/hive/pkg/hive/issue_scan_mark_ready_authority.go` — the governance lookup: human-decided, unexpired, latest-wins with malformed-record revocation
- `/Transpara/transpara-ai/repos/hive/pkg/hive/issue_scan_ready_pr_finalizer.go` — the finalizer gate: consume-before-mutate, currency re-check, provenance-bound remediation, human-approval supremacy
- `/Transpara/transpara-ai/repos/hive/pkg/hive/issue_scan_ready_stage.go` — durable nonce claims (append-then-verify-winner), blocked-evidence terminality, whole-store paged reads
- `/Transpara/transpara-ai/repos/hive/pkg/safety/safety.go` — RepoProtectedActions — the DF-SOP-0001 repo-narrower extension mechanism carrying pull_request.mark_ready

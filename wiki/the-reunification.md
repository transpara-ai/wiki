---
entity: The Reunification Workstream
aliases: [reunification, df-reunification, the reunification slice, one civilization one business]
tier: arc
status: compiled
last_compiled: 2026-06-14
sources:
  - raw/transpara/dark-factory/reunification/README.md  # DF-REUNIFY-README v0.6.0, status review, authority: planning
  - raw/transpara/dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md  # DF-REUNIFY-2026-06-05-SLICE-1-DESIGN v0.1.2
  - Open Brain captures, 2026-06-05 through 2026-06-12 (reunification checkpoint, slice-1 build + live-run records)  # chronology
confidence:
  workstream_charter: high (primary sources — README + slice-1 design)
  drift_diagnosis: high (reproducible from source; grep over work/epic*.go + v3.9 vocab counts, per Open Brain)
  five_inversions: design intent, not yet accepted doctrine (the design says so explicitly)
  demonstration_outcome: the slice DID run and produced the artifact (Open Brain, 2026-06-05 session 4) — but acceptance into v4.0 is NOT recorded; treat "doctrine extracted" as still pending
  supersession: explicit — does NOT supersede v3.9 (operative) or accept v4.0 (candidate)
---

# The Reunification Workstream

A **planning/design-only** workstream opened on **2026-06-05** in `transpara-ai/docs` (`dark-factory/reunification/`) to pull [[dark-factory]] back onto its original Mission: **"one civilization, one business."** It exists because the build had drifted — an accountability pipeline grew *beside* the living [[hive-governance]] civilization instead of *through* it. The workstream's bet is **demonstration-first**: prove the reunion with one real run before rewriting doctrine, then extract corrected doctrine from what actually happened rather than writing it ahead of the run.

Every artifact in the workstream carries `authority: planning` — no implementation authority, no file relocation, no change to current v3.9 or v4.0 status. The workstream **does not supersede v3.9 (operative) or accept v4.0 (candidate)**.

## Why it exists: the drift

The project built two systems on one [[event-graph]] substrate that never connected:

1. a **living Hive civilization** with a working emergent-agent growth loop (`hive/pkg/hive` + `pkg/loop`), and
2. a **Dark Factory accountability pipeline** — the `work/epic*.go` gate fixtures (Gates A–J / F–J).

The pipeline runs *beside* the civilization, not *through* it. The slice-1 design states the drift is **reproducible from source**: `grep -rnE 'guardian|cto|spawner|strategist' work/epic*.go` returns no civic-role references — the epics use `maintainer` / `recorded_llm` actors instead. The Open Brain drift diagnosis (2026-06-05) adds vocabulary evidence from `dark-factory/v3.9/`: "gate" ×1865 and "evidence" ×1097 against "civilization" ×8 and "hive mind" ×0. The civic roles survive only as a permission ACL in two spec files; v4.0 "enthroned the human committee, not the Hive Mind."

The design's one-line indictment:

> "The cage was perfected; the inhabitants never moved in."

Root cause, in the workstream's own framing: **accountability was meant to be the *membrane* the civilization acts within; it became the *product*.**

> Confidence: the drift diagnosis is **high** — the `grep` is reproducible and the vocabulary counts come from the Open Brain primary-source review. The vocabulary ratios themselves are reported, not independently re-counted this run.

## The destination: five inversions

The design names five inversions — "the factory is the civilization at work." These are stated **design intent, not accepted doctrine** (the design is explicit that it "graduates into v4.0 doctrine only *after* the slice actually runs"):

1. **The order is the unit of cooperation.** A `FactoryOrder` enters as Work; civic roles fulfill it by emitting events on the shared graph, instead of an epic running as a closed fixture.
2. **Gates become role-enforced checks**, applied inside the cooperative flow by Reviewer and Guardian. Evidence is a *byproduct* of roles working.
3. **The Hive Mind governs.** Guardian + council are the governance; the human is the **top authority tier** (Required actions escalate), not the terminal doer.
4. **The growth loop runs in production.** A capability gap during an order triggers `CTO → Spawner → Guardian → Allocator → spawnDynamicAgent`.
5. **The visualization shows the society building the order** — which role did what — not abstract forensic tiers.

## The method: demonstration-first

The chosen path is to **prove the reunion with one living run before rewriting any doctrine.** A single observed run of the Hive building something real re-grounds the program and generates the honest material to rewrite v4.0 and the visualization *from reality*. The README states the corollary plainly: extract the corrected v4.0 doctrine and the replacement visualization **from what actually happened**, not from a doctrine written ahead of the run.

This is the workstream's defining discipline and the reason its status stays `planning` even after code lands: the doctrine fold is gated on a *real, accepted* run.

## Slice 1 — the first reunified order

The first concrete step. **Goal:** demonstrate that one `FactoryOrder` is fulfilled by the Hive's civic roles, coordinating **only through the shared event graph**, with the v3.9 accountability machinery acting as the **membrane (not a separate pipeline)**, the human as the top authority tier approving through the Site governed decision surface, and the run rendered in the Site console — ending in a **real, reversible draft PR**.

### The order and its artifact

The `FactoryOrder` requests an artifact the corpus was actually missing: a one-page `dark-factory/civic-roles.md` describing the civic roles (strategist, planner, implementer, reviewer, guardian, cto, spawner, allocator, sysmon). The civilization's first reunified act is to **document its own society** — low-stakes prose, a real artifact, reversible. Output is a draft PR in `transpara-ai/docs` from a `codex/*` branch. See [[civic-roles]].

### The cooperative flow

Every step maps to a real bootstrap agent (`hive/pkg/hive/agentdef.go` `StarterAgents()`) and a real event (`hive/pkg/loop/tasks.go`):

| Step | Role | Membrane check |
| --- | --- | --- |
| Order injected as a Work task | (entry point) | — |
| Decompose the order | strategist | — |
| Attach contract | planner | **Readiness gate** (`work/store.go:Readiness`) |
| Build the artifact | implementer (`CanOperate=true`) | — |
| Review | reviewer | acceptance-criteria check; return path exercises the feedback loop |
| Authorize the protected action | guardian | **Authority gate** → escalate to human via Site |

Coordination is **only through graph events** — no direct agent-to-agent messaging (`hive/ARCHITECTURE.md`: "No direct communication — only events"). The design calls this "the hive-mind property, obtained for free."

### The membrane (three gates only)

Deliberately minimal for Slice 1 — each gate owned by a role, not a separate pipeline:

- **Readiness gate** — the Planner's three artifacts (`definition_of_done`, `acceptance_criteria`, `test_plan`), already enforced today.
- **Trace-completeness** — the Reviewer verifies every material step left an event (reusing the darkfactory `TraceCompleteness` record concept, `eventgraph/go/pkg/darkfactory/v39`).
- **Authority gate** — creating a real draft PR is a Required (protected) action. The **Guardian raises an `AuthorityRequest` that escalates to the human via the Site Gate-E decision surface**. Site forwards the approval as a governed decision event and **stays a pure console** (`effect=none` preserved, no policy evidence from Site). The **Hive orchestrator** (`hive/pkg/hive/factory_orchestrator.go`) assembles the full Epic 11 evidence set and only then invokes Work's **fail-closed** Epic 11 creator (`work#43`), which re-validates the policy-bundle hash and requires `head_exists_on_origin=true` before the single GitHub call. The design calls this "the literal demonstration of inversion #3."

A fourth concern — **branch precondition** — is handled as run-setup, not as an in-graph gate: the `codex/*` head branch must already exist on `origin` before the authority gate fires, and the Epic 11 creator is itself forbidden to push it (`work#43` denies `branch.push`). Promoting branch-push to an in-graph protected action is deferred to a later slice.

### The growth-loop hook (wired, dormant)

Slice 1 does **not** manufacture a capability gap. It feeds the order's task flow into the CTO leadership briefing (`hive/pkg/loop/cto.go:enrichCTOObservation`) so the existing loop *can* see factory gaps — present from day one, dormant until a real order needs a role that does not exist. New agents always spawn `CanOperate=false` (trust-gated), as the code already enforces.

### What you see

A **role-timeline trace rendered in the Site console** (`site/graph/views.templ`): the run's event chain grouped by civic role, showing the order move strategist → planner → implementer → reviewer → guardian → human (Site approval) → draft PR. The design names this the **"order built by the society" view** — the "first real version of the replacement visualization," the direct antidote to the ten forensic tiers, rendered on real run data.

### Scope discipline

The design fences the blast radius hard. Non-goals include: not all of Gates A–J (minimal membrane only); not forcing the growth loop; **no merge, no marking-ready, no default-branch or force push, no deploy** — a single draft PR only, exactly as Epic 11 forbids; not retiring the v3.9 evidence model (reusing it as the membrane); Site bounded to two seams (forward the approval, render the trace) with **no executor role for Site**; and "**not rewriting v4.0 — that is the *output* of running this slice.**"

## Did it run? (fail-legible status)

This is the most important honesty flag for this entity, because the sources and the record disagree in tense.

- **The two primary sources (README, slice-1 design — both dated 2026-06-05)** are written as *plan*: the slice "graduates into v4.0 doctrine only *after* the slice actually runs," and the Epic 11 creator "has only been exercised against a fake client." On those documents alone, the demonstration is **future tense**.
- **Open Brain (2026-06-05, session 4)** records that the first live society run **succeeded the same day**: the Hive civic roles, coordinating only through the shared Postgres event graph, produced a real `dark-factory/civic-roles.md` (one clean commit `28ba0ea` on branch `codex/civic-roles`, all nine roles participating, ~10-minute daemon run, no errors). Later captures (through 2026-06-12) record continued work — a contract layer, a 24-role roles catalog superseding the prose doc, multiple convergence runs.

So: **the demonstration happened; the candidate documents predate it.** What is **not** recorded anywhere read this run is the *completion of the loop the workstream was built to close* — i.e., the run being **accepted** and its results **folded into v4.0 doctrine via the migration register**. The README and design both make acceptance a precondition for that fold. Treat "corrected v4.0 doctrine extracted from a real run" as **asserted-as-the-plan and partially demonstrated, but not recorded as completed/accepted.**

> Confidence: that a live run produced the artifact is **well-supported** (detailed Open Brain capture with commit SHA and per-role activity). That the workstream's doctrine-fold goal is *done* is **unsupported** — and the workstream's own charter keeps it `planning` until acceptance. Do not read "it ran" as "v4.0 accepted."

## Relationship to existing doctrine

Per the README, explicitly:

- Does **not** supersede v3.9 (operative) or accept v4.0 (candidate).
- When a slice runs and **is accepted**, its results fold into v4.0 doctrine via the migration register (`dark-factory/reorganization/source-register.yaml`) — assign a stable `doc_id`, record the status transition (review → accepted), link the run evidence. The slice-1 design repeats the rule: "Do not enshrine this as doctrine before the run."

## Later artifacts in the workstream

The README routes to follow-on planning artifacts (read this run only as titles/summaries in the README, **not** opened in full — treat their internal claims as thin here):

- **Slice 1 — Shepherd the Society to its Own Roles Catalog** (2026-06-07) — a "take 2" under a *shepherding* operating model where Claude+Codex strengthen the Planner/Reviewer **contracts**, never the artifact.
- **Slice 1 — Run Findings** (2026-06-08) — what seven society rounds revealed; the contract layer works and the production driver is fixed, but producer + triggering reliability remained the wall (no single run cleared all five acceptance criteria at once).
- **The Deployment Arc** (2026-06-09) and its **Execution Plan** (2026-06-10) — the program arc from the Slice-1 frontier to a continuously operated factory; proposal-only, every phase requiring its own packets.

## What it connects to

- **Re-centers:** [[dark-factory]] on the mission ("one civilization, one business").
- **Re-joins:** the [[hive-governance]] civilization and its [[civic-roles]] to the accountability machinery.
- **On the substrate:** everything runs over one [[event-graph]]; gates reuse the darkfactory v39 evidence records.
- **Lineage:** the membrane discipline (gates as fail-closed role-checks, fail-safe by default) descends from the [[authority-layer]] and the broader [[fourteen-layers]]; the order-as-cooperation framing rests on the [[the-20-primitives]] (`Node`/`Edge`/`Event`/`Criteria`).

## Sources & provenance

Compiled from the two `reunification/` workstream artifacts in `transpara-ai/docs` (mirrored locally):

- `raw/transpara/dark-factory/reunification/README.md` — DF-REUNIFY-README v0.6.0, status review, `authority: planning`.
- `raw/transpara/dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md` — DF-REUNIFY-2026-06-05-SLICE-1-DESIGN v0.1.2.

Chronology and the "did it run" reconciliation come from **Open Brain** captures (2026-06-05 reunification checkpoint and slice-1 build/live-run records; through 2026-06-12 for the roles-catalog supersession). This entity is internal to the dark-factory corpus; it has no Searles post and therefore no external durable URL. The drift-diagnosis vocabulary counts and the reproducing `grep` are reported from those sources, not independently re-run this session. `[[wikilinks]]` are forward references; several targets ([[mission]], [[authority-layer]], [[fourteen-layers]]) are not yet compiled.

## Run-3 update (2026-06-14)

Sources: `dark-factory/reunification/2026-06-12-arc-state.md` (DF-REUNIFY-2026-06-12-ARC-STATE v0.3.0) and `2026-06-11-slice-1-take-4-round-log.md` (DF-REUNIFY-2026-06-11-SLICE-1-TAKE-4-ROUND-LOG v0.5.0).

### Round 6 (v16) complete — first society to finish

Round 6 closed on **2026-06-12** with a new close class: **`finished-unsignalled`**. The society finished all assignable work, sealed the chain at **1128 events**, and entered terminal quiescence at 12:13. It was the first society across the arc to finish rather than stall.

The arc ladder in full:

| Round | Store | Duration | Outcome |
|---|---|---|---|
| 3 | v13 | ~5 min | silent — API 529 killed the only CanOperate agent; loop exited without a chain event |
| 4 | v14 | ~27 min | visible — all 8 keepalive agents budget-exited; loop obituaries printed; zero silent deaths |
| 5 | v15 | ~31 min + artifact | productive — catalog committed (`b98b67a`), renewal deadlock stalled further progress |
| **6** | **v16** | **45 min** | **finished-unsignalled — first society to finish; chain sealed; daemon alive + frozen** |

### v15 fix set proven live

The v15 fix set (hive#157, merged `2fe5b2f`) was the purpose of round 6 and was proven in production across every dimension:

- **F1(a)** — 6/6 parks raised `agent.budget.exhausted` on-chain; zero raise failures.
- **F1(b+c)** — the allocator woke, rechecked, and renewed all five parked agents; sufficiency math verbatim in production reason strings ("PARKED - renew above 31m22s elapsed"); zero cooldown stranding; plus one preemptive renewal and one adaptive re-up beyond the taught contract.
- **F3** — six reviews in round 6 versus zero across five prior epochs; first review arrived at 16 minutes on the original 30-minute lifespan.
- **F2 git law** — six stacked commits under maximal rework pressure, including direct adversarial instruction to violate workspace containment; zero amends, resets, or branch-switches.

### v16 open findings

Three findings were unmasked by the fix set (none caused by it):

- **F1 — WorkDir/Reason cwd defect (eventgraph `claude_cli.go`).** The Operate path correctly sets `cmd.Dir = task.WorkDir` (fail-closed gate); the Reason path sets no `cmd.Dir`. Every agent's claude-cli shell inherits the daemon's launch directory. The daemon was launched from `repos/hive`; all six round-6 reviews "verified" the deliverable in the wrong repo — phantom absence in rounds 1–3, then wrong-destination doctrine in rounds 4–6. Fix shape: thread WorkDir into Reason task construction; honor it in the provider mirroring Operate's gate; enforce that the daemon's cwd is always the same git repo as the workspace.
- **F2 — dual-spec oscillation.** The planner's decomposition silently narrowed the FO's scope at planning time (subtask `019ebb62`, seq 124, pre-review), scoping to code-derived roles only and dropping the governance layer. Two live contradictory specs — the subtask reading and the FO's 24-role dual-layer requirement — produced six completions in perfect alternation (`24→9→24→9→24→9 roles`), each locally correct against one spec. Fix shape: a spec-diff gate at subtask creation requiring an explicit narrowing declaration against the parent FO; review-rejection content never becomes task spec without FO reconciliation.
- **F3 — no quiescence exit.** Keepalive wake-blocking plus the recheck allowlist's work-exists gates mean a society whose work-generators exit and whose reviews cap out freezes indefinitely. `hive.run.completed` never fired; only the sentinel's chain-frozen watch surfaced the close. **v16 is the first society to finish, and the system has no concept for finishing.** Fix shape: a quiescence detector that emits `hive.run.completed` (or escalates to the operator) when all loops are wake-blocked and no assignable/reviewable/renewable work remains. Related: the cap's escalation comments demanded "Human/CTO judgment" with no channel in the system to receive a human decision.

### Power loss event and crash recovery

At ~18:44–18:49 on 2026-06-11, nucbuntu lost power during round 4 (v14), capturing all nine agents mid-flight (`last -x` shows a reboot at 18:49 with no prior shutdown record). This was the **first live proof of the crash-recovery path**:

- All event chains v4–v14 survived on the postgres volume (postgres needed a manual `docker start` — it has no restart policy).
- `/tmp` was wiped: uncommitted round logs, arc-state docs, sentinel scripts, and forensic dumps from rounds 1–3 were lost.
- Round 4 resumed at 19:15 on the same store and repo, no re-seed. `checkpoint.RecoverAll` cold-started nine fresh identities (role-name continuity); within ~2 minutes the new implementer was auto-assigned the same child task ID the pre-crash epoch had been working.
- Chain integrity held: seq 462–484 do not exist (postgres WAL recovery sequence skip — cosmetic; hash chaining is per-event).

Lesson applied structurally: operational state moved from `/tmp` to `/Transpara/transpara-ai/data/df-slice1/` (data disk, reboot-safe). Round records now commit to the docs repo as they are written, not at closeout.

### sentinel-v16.sh — session-bound-watcher class closed

The v15 meta-finding (the sentinel dying at session boundaries had caused two unobserved round closes) was resolved by making the sentinel a nohup process before any round-6 boot. `sentinel-v16.sh` ran round 6 entirely unattended: the operator session crashed at ~11:29, right after the launch report, and the nohup pair ran the round through, banking every WAKE (parks, renewals, milestones, the chain-freeze) and surfacing the close at 12:32 (chain-frozen, two intervals). **The session-bound-watcher failure class is closed.**

### Grant accounting and Gate-E

Grant-2 (rounds 4–6) is **exhausted**. The hard stop is reached. Gate-E — continue with the v16 fix-set scope or stop — is Michael's decision. The v16 fix-set candidate: F1 WorkDir threading (hive `pkg/loop` + eventgraph provider), F2 spec-diff gate at subtask creation, F3 quiescence detector emitting `hive.run.completed` plus a human-decision channel. The v16 daemon (PID 821925/821927, ~0% CPU) is alive and frozen by design pending the Gate-E decision.

### Deliverable state

Catalog branch `codex/fo-roles-catalog-v16` pushed to the transpara-ai fork (HEAD `002bcf8`, 9-role v2.0.0 subtask reading; the FO's 24-role reading in-history at `b638a44`). All six round-6 reviews were premised on the wrong repo (v16-F1), so in the FO's sense the catalog **remains unreviewed**. Human ruling recorded: the workspace is `transpara-ai/docs`; the FO's 24-role dual-layer scope governs (`b638a44`'s content); the planner subtask was mis-scoped.

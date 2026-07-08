---
entity: MemPalace
aliases:
  - MemPalace
  - mempalace
  - the advisory memory candidate
  - the memory-palace fork
tier: investigation
status: compiled
last_compiled: 2026-06-24
civilization_contribution: "Contributed the governed recall-adapter pattern behind ADR-0008 and the MemoryReference boundary; MemPalace is eligible only as an advisory recall substrate, never as truth, authority, certification evidence, or a control-plane primitive."
sources:
  - raw/transpara/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # DF-V3.9-EPIC-TECH-CROSSWALK v3.9.1 (status: review): the MemPalace decision row + per-item note
  - raw/transpara/dark-factory/archive/v3/adrs/ADR-0008-mempalace-verbatim-recall.md  # ADR-0008: proposed MemPalace verbatim recall substrate
  - raw/transpara/dark-factory/v3.9/06-memory-knowledge-capability-v3.9.md  # DF-V3.9-SPEC-006: memory, knowledge, MemoryReference, capability evolution
  - raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # Decision 15: external frameworks stay outside control roles
  - raw/open-brain/2026-06.md  # fork-provenance line (4/08 mempalace <- MemPalace) and the Apr–May "Civilization Landscape Investigation" fan-out roster
  - https://github.com/transpara-ai/mempalace/blob/main/README.md  # forked README context; upstream-authored and not a Transpara finding
  - "raw/inbox/2026-06-24/mempalace/TAI-RES-2026-004-v1.0.0-MemPalace-Evaluation-01583dbd30c3.md"  # TAI-RES-2026-004 v1.0.0, code-anchored MemPalace capability evaluation
  - "raw/inbox/2026-06-24/mempalace/TAI-RES-2026-004-v1.1.0-MemPalace-Evaluation-185593e1b62f.md"  # added via wiki browser ingest 2026-06-24; supersedes: raw/inbox/2026-06-24/mempalace/TAI-RES-2026-004-v1.0.0-MemPalace-Evaluation-01583dbd30c3.md
  - "raw/inbox/2026-07-07/mempalace/TAI-RES-2026-004-v1.1.1-MemPalace-Evaluation-ed94a22035e5.md"  # added via wiki browser ingest 2026-07-07; note: classification corrected for the record; supersedes: raw/inbox/2026-06-24/mempalace/TAI-RES-2026-004-v1.1.0-MemPalace-Evaluation-185593e1b62f.md
current_research_version: 1.1.0
confidence:
  decision_row: high — quoted verbatim from the v3.9.1 crosswalk decision table and per-item note; the row exists (this is NOT a thin/no-row case)
  crosswalk_status: the crosswalk doc is status:review / canonical:false; the ratified rule is v3.9 Decision 15 (external frameworks stay outside control roles), not the row detail. See note.
  fork_date_and_origin: medium-high — "4/08 ... mempalace <- MemPalace" comes from a single Open Brain capture (raw/open-brain/2026-06.md); consistent with the seed, but rests on that one line
  implementation_read: high — TAI-RES-2026-004 read MemPalace v3.5.0 code, MCP surface, backends, local embedding path, temporal KG, benchmarks, packaging, and maturity posture
  benchmark_claims: medium-high — MemPalace headline figures are artifact-anchored retrieval-recall numbers; they are not end-to-end QA accuracy and do not establish competitor superiority
  integration_state: high — no Civilization runtime integration owner is selected; MemPalace remains an advisory recall candidate behind a future MemoryReference boundary
raw_documents:
  - "raw/inbox/2026-06-24/mempalace/TAI-RES-2026-004-v1.0.0-MemPalace-Evaluation-01583dbd30c3.md"
  - "raw/inbox/2026-06-24/mempalace/TAI-RES-2026-004-v1.1.0-MemPalace-Evaluation-185593e1b62f.md"
  - "raw/inbox/2026-07-07/mempalace/TAI-RES-2026-004-v1.1.1-MemPalace-Evaluation-ed94a22035e5.md"

---

# MemPalace

**MemPalace is the strongest external memory-system match found so far for the Civilization's advisory recall layer: a local-first, verbatim AI-memory store that can plausibly become the recall adapter behind `MemoryReference`, but only if it stays outside authority and certification.** TAI-RES-2026-004 v1.1.0 upgrades this page from a README-grounded investigation stub to a code-anchored assessment of MemPalace v3.5.0 and adds the explicit ADR/contribution verdict. The conclusion is stable and narrow: MemPalace retrieves what was said; the Civilization governs what a memory is allowed to change.

## Placement

The v3.9.1 technology-decision crosswalk (`raw/transpara/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md`) already gave MemPalace a real row: **"included as advisory memory candidate,"** integration mode **"possible memory adapter; no truth authority,"** owning epic **"future memory integration packet, not currently selected,"** classification **adapter/reference**. Its risk line is the whole policy in miniature: **"memory can influence work without evidence if miswired."**

TAI-RES-2026-004 confirms that decision against MemPalace v3.5.0. It does not promote MemPalace into the kernel, EventGraph, Work, Hive, policy, release authority, certification, or product shell. It strengthens the case for a future adapter by verifying the implementation underneath the earlier doctrine phrase **"MemPalace or equivalent recall storage."**

## Decision Record and ADR Disposition

TAI-RES-2026-004 v1.1.0 makes the decision status explicit:

- **Dark Factory ADR:** yes, ADR-0008, "Use MemPalace as the verbatim recall substrate" (`raw/transpara/dark-factory/archive/v3/adrs/ADR-0008-mempalace-verbatim-recall.md`), currently Proposed.
- **Recommended ADR action:** move ADR-0008 from Proposed to **Accepted with conditions**, only after the fail-closed `MemoryReference` import boundary and the license/supply-chain gate exist.
- **Civilization contribution:** yes, as the verbatim recall adapter behind the `MemoryReference` boundary; never as truth, authority, certification evidence, or a control-plane primitive.

The adoption verdict is therefore: **adopt as a recall adapter behind the boundary; supply-chain gate first.** This is not a runtime activation and does not assign an implementation owner.

## What Changed With TAI-RES-2026-004

The earlier page treated upstream claims as unverified context. The current v1.1.0 evaluation read the repository and found several concrete updates:

| Area | Prior page | Updated finding |
|---|---|---|
| Version baseline | README context from the fork, effectively stale | v3.5.0 baseline, upstream `MemPalace/mempalace`, 2026-06-24 |
| MCP surface | 29 tools, README-grounded | **35 tools**, verified from the `TOOLS` registry |
| Retrieval | Upstream semantic-search claim | Hybrid vector + BM25 + closet boost, local ONNX embeddings by default |
| Knowledge graph | README context | Temporal SQLite triples with `valid_from` / `valid_to` and invalidate-not-delete semantics |
| Benchmarks | Upstream headline carried as unverified | Recomputed artifact-anchored retrieval-recall figures; not end-to-end QA accuracy |
| Supply chain | Scam-alert context only | MIT core, optional LGPL `psycopg` in `[pgvector]`, young high-churn beta, impostor-domain risk remains load-bearing |
| Decision record | Candidate row existed but ADR disposition was implicit | ADR-0008 disposition is explicit: Proposed → Accepted with conditions |

The result is not "adopt MemPalace wholesale." The result is "MemPalace is a credible recall engine if wrapped in the Civilization's own trust and influence-accounting boundary."

## The Boundary

The governing boundary is `DF-V3.9-SPEC-006` (`raw/transpara/dark-factory/v3.9/06-memory-knowledge-capability-v3.9.md`): memory may advise, but it does not govern. Any memory that materially influences planning, generation, repair, release review, or capability evolution must become a `MemoryReference` before certification can pass. That reference must carry source, hash, retrieval time, actor, task, influence summary, risk scope, trust level, freshness, redaction state, and contradiction refs.

MemPalace itself does not do that. It is deliberately fail-open recall: store verbatim content, search it, and return the nearest relevant drawers. That is correct at the recall layer and wrong at the authority layer. The Civilization boundary supplies the missing governance:

- recalled content enters at `raw` trust;
- secret-bearing memory is quarantined and unusable;
- stale or contradicted memory cannot quietly influence high-risk work;
- every material influence is linked to an EventGraph `MemoryReference`;
- certification waits for the influence record.

## Capability Read

MemPalace's fit is real because it shares several instincts with the Civilization design:

- **Verbatim storage:** drawers preserve source text; lossy closet summaries point back to lossless content rather than replacing it.
- **Local-first retrieval:** the default path uses local ONNX embeddings and local storage, with no external embedding API by default.
- **Temporal memory:** the SQLite knowledge graph records validity windows and closes facts instead of deleting them.
- **MCP surface:** the 35-tool server is a useful shape for a future MemoryKeeper/Researcher recall adapter.
- **Agent ergonomics:** editor hooks and "search before answering" protocols model how prior context can be made available to agents.

The fit also has limits:

- per-project and per-agent scoping inside a palace is mostly metadata convention, not a Civilization-grade trust boundary;
- retrieval recall is not truth, policy, or evidence;
- the first-run model download must be replaced by a vendored, hash-pinned offline cache before air-gapped use;
- the fork must be pinned to reviewed commits rather than passively following a fast-moving upstream.

## Benchmark Reality

The evaluation verifies that MemPalace's headline benchmark numbers are reproducible as **retrieval recall** measurements. That is useful, but it is narrower than the marketing phrase "best-benchmarked" can imply. Recall@K asks whether the right session or evidence appears in the returned candidates. It is not end-to-end answer accuracy, and the repository does not run competitors on the same harness.

For Civilization purposes, the useful lesson is not the raw R@K score. The useful lesson is the benchmark discipline: committed per-question artifacts, deterministic local runs, and a recall-quality harness that can become a governed `EvalDataset` for the future recall adapter. The Civilization's metric should be stricter: did the retrieved `MemoryReference` improve the gated decision it influenced?

## Integration Packet

The future packet, if opened, should treat MemPalace as the worked example of a fail-closed memory-adapter gate:

1. Define the `MemoryReference` import boundary before wiring any recall into gated work.
2. Move ADR-0008 from Proposed to Accepted with conditions only after the boundary and supply-chain gate exist.
3. Adopt the MCP tool surface as an adapter interface, not as authority.
4. Use the temporal-KG pattern for freshness and as-of recall, but publish results as governed references.
5. Pin the Transpara-AI fork to reviewed commits; verify PyPI provenance and exclude optional copyleft/default-redistribution ambiguity.

## Sources & Provenance

- `raw/inbox/2026-06-24/mempalace/TAI-RES-2026-004-v1.1.0-MemPalace-Evaluation-185593e1b62f.md` — TAI-RES-2026-004 v1.1.0, the current 2026-06-24 code-anchored evaluation. It adds the explicit decision-record / ADR-disposition / contribution determination; no findings or learnings changed from v1.0.0.
- `raw/inbox/2026-06-24/mempalace/TAI-RES-2026-004-v1.0.0-MemPalace-Evaluation-01583dbd30c3.md` — TAI-RES-2026-004 v1.0.0, retained for provenance and superseded by v1.1.0 for presentation.
- `raw/transpara/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` — the v3.9.1 decision row admitting MemPalace as an advisory memory candidate with no truth authority and no implementation owner.
- `raw/transpara/dark-factory/archive/v3/adrs/ADR-0008-mempalace-verbatim-recall.md` — ADR-0008, "Use MemPalace as the verbatim recall substrate," currently Proposed.
- `raw/transpara/dark-factory/v3.9/06-memory-knowledge-capability-v3.9.md` — `DF-V3.9-SPEC-006`, the memory, knowledge, `MemoryReference`, and capability-evolution spec.
- `raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md` — v3.9 unified decisions, including Decision 15, "External Frameworks Stay Outside Control Roles."
- `raw/open-brain/2026-06.md` — fork provenance: "4/08 ... mempalace <- MemPalace," and the April-May fan-out roster placing MemPalace in the memory cluster.
- `https://github.com/transpara-ai/mempalace/blob/main/README.md` — upstream-authored fork README context only; useful for provenance and declared official-source/scam-alert context, not for Transpara findings.

**Conflicts and thin spots stated, not resolved.** The crosswalk row is reviewed planning, while Decision 15 (`raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md`) is the ratified law. MemPalace is code-verified as a recall candidate, not integrated. Benchmark evidence is strong for retrieval recall and weak for broad market-performance superiority. The supply-chain gate is not ceremonial: the project is young, fast-moving, and explicitly reports impostor-domain risk. The correct status is therefore: credible recall adapter candidate; no authority; no runtime activation yet.

---
entity: PageIndex
aliases:
  - PageIndex
  - pageindex
  - VectifyAI PageIndex
  - the vectorless RAG index
  - the document-evidence retriever
tier: investigation
status: compiled
last_compiled: 2026-07-07
civilization_contribution: "Pattern-only; no ADR. Contributes the tree-structured document-evidence pattern behind the optional DocumentEvidenceRetriever (accepted v3.9 doctrine), and — from a code-anchored read of VectifyAI/PageIndex @ f413c66 (TAI-RES-2026-007) — proves the boundary: PageIndex's tree index is a probabilistic LLM artifact (every node, title, page-mapping and summary is an LLM output, self-graded by an LLM accuracy check) that must enter EventGraph as a DocumentEvidenceRetrieval → KnowledgeReference/source_refs record. PageIndex is eligible only as an advisory document-evidence adapter behind that boundary, gated after Base Slice 0; never truth, certification evidence, a memory/knowledge authority, or a control-plane primitive (Decision 15)."
current_research_version: 1.0.0
sources:
  - "raw/civilization/external-landscape/tai-res-2026-007-pageindex-evaluation.md"  # TAI-RES-2026-007 v1.0.0, the code-anchored evaluation (this page's primary source); read VectifyAI/PageIndex @ f413c66
  - https://github.com/VectifyAI/PageIndex/tree/f413c66  # evaluated commit f413c66fee0bfbb7291c389333f9cc1adac68d57, 2026-07-03 — read in full from a local clone; UPSTREAM CONTEXT ONLY, never re-published, never a PR/push target
  - raw/transpara/dark-factory/research/pageindex-role-in-transpara-stack.md  # the 2026-05-13 indexed-only study — "augmentation, not replacement"; superseded for "what it is" facts by TAI-RES-2026-007
  - raw/transpara/dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md  # Phase 5 matrix: PageIndex class = "Optional adapter / pattern"; overlap KnowledgeReference/source_refs; risk "retrieval mistaken for truth"
  - raw/transpara/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # closeout: PageIndex #4; U4 DocumentEvidenceRetriever; rejected as truth/cert authority
  - raw/transpara/dark-factory/v3.9/06-memory-knowledge-capability-v3.9.md  # accepted v3.9 doctrine: DocumentEvidenceRetriever pattern (06:156) + PageIndex named as optional reference (06:178)
  - raw/transpara/dark-factory/v3.9/02-kernel-schema-and-state-v3.9.md  # DocumentEvidenceRetrieval + KnowledgeReference node schemas (02:331, 02:317)
  - raw/transpara/dark-factory/v3.9/09-legacy-coverage-matrix-v3.9.md  # PageIndex decision row (09:252): "optional document evidence retrieval; not memory, truth, policy, or certification"
  - raw/transpara/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # DF-V3.9-EPIC-TECH-CROSSWALK v3.9.1 — read in full; PageIndex has NO row (the standing fail-legible point)
  - raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # Decision 15: external frameworks stay outside control roles
  - raw/transpara/dark-factory/v4.0/04-production-workflow-runtime-v4.0.md  # accepted v4.0: source_refs (04:48); Base Slice 0 + external-adapter eligibility gate (04:135, 04:165)
  - https://pageindex.ai/blog/pageindex-intro  # upstream intro post — context only
confidence:
  crosswalk_row: NONE — read the v3.9.1 crosswalk in full; PageIndex/VectifyAI is absent from the decision table and per-item notes. This remains the article's central fail-legible point. Correction (TAI-RES-2026-007) — PageIndex IS named in accepted v3.9 *doctrine* (06:178 and the 09 coverage-matrix row) with a defined DocumentEvidenceRetrieval node schema; the crosswalk is a separate, review-status document.
  implementation_read: high — TAI-RES-2026-007 read VectifyAI/PageIndex @ f413c66 in full (~3,000 lines) covering the LLM-driven tree builder, the LLM self-verification and fallback cascade, the three accessor tools, the litellm/OpenAI dependency, the OSS-vs-cloud split, packaging/CI, and LICENSE
  upstream_description: code-anchored — the "what it is" facts (vectorless, LLM-built ToC tree, three accessor tools) are now verified against the repository, not carried as upstream claim; superseding the 2026-05-13 indexed-only study
  benchmark_claims: upstream-self-reported, not the library — the headline 98.7% FinanceBench figure is Mafin 2.5's (a system "powered by PageIndex"), self-graded by VectifyAI with no independent reproduction; not carried as a Transpara finding
  supply_chain: medium — MIT license (clean); but no git tags/releases/PyPI distribution for the OSS library (clone-main only), one test file, and CodeQL configured to scan only Actions YAML (not the Python). Air-gap needs the LLM path vendored.
  oss_vs_cloud: high — the MIT OSS library (local tree-builder + three accessors) is distinct from the cloud product (OCR/scale/MCP) and from the PyPI `pageindex` package (which is the cloud SDK, BASE_URL api.pageindex.ai)
  fork_date_and_existence: thin / asserted by task framing — the original seed asserts a 2026-05-13 fork into transpara-ai. No transpara-ai/pageindex repo was found; treated as reconstructed. What IS dated is the 2026-05-13 study and now the 2026-07-07 code read at f413c66.
  integration_state: thin — no implementation owner is selected; nothing in the surveyed sources shows PageIndex wired into the platform. Adapter evaluation is gated behind [[base-slice-0|Base Slice 0]].
raw_documents:
  - "raw/civilization/external-landscape/tai-res-2026-007-pageindex-evaluation.md"  # TAI-RES-2026-007 v1.0.0; session-authored Civilization external-landscape research, placed outside the browser-ingest inbox by design — provenance is git history + this frontmatter
---

# PageIndex

**PageIndex (upstream `VectifyAI/PageIndex`) is a vectorless, reasoning-based RAG framework that the [[civilization-landscape-investigation]] carried forward as the reference implementation of the Civilization's optional `DocumentEvidenceRetriever` pattern — a future document-evidence adapter usable *behind a boundary*, never as truth, certification evidence, or a memory/knowledge authority.** TAI-RES-2026-007 upgrades this page from an indexed-only investigation stub to a **code-anchored** assessment: it reads the actual repository (`VectifyAI/PageIndex` @ `f413c66`, 2026-07-03, ~3,000 lines) and finds that PageIndex's tree index is a *probabilistic LLM artifact* — every node, title, page-mapping and summary is an LLM output, self-graded by an LLM accuracy check, built by calling an external LLM API. That is the code-level proof of the investigation's #1 recorded risk, *"retrieval mistaken for truth."* The subject of *this* article is Transpara's evaluation and decision about PageIndex — not the upstream project's marketing, which is cited only as context. Per organization rules the upstream is never re-published, never pushed to, and never a PR target.

## What changed with TAI-RES-2026-007

The earlier page carried the upstream's "what it is" claims as unverified context, because the 2026-05-13 study relied on search-indexed and partial access. The current evaluation read the repository at `f413c66` and replaces that partial access with code-anchored findings:

| Area | Prior page (indexed-only) | Updated finding (code-anchored, `f413c66`) |
|---|---|---|
| Index construction | Upstream claim: "builds a ToC tree, an LLM traverses it" | Every node/title/hierarchy-number/page-map/summary is an LLM output; **no deterministic parser exists** (`page_index.py:1058`, `:264`, `:531`). The structure is inferred, not parsed. |
| Validation | Not examined | Self-verification is **an LLM grading an LLM** — sample titles, ask a model if each appears on its page, accept at a hard-coded **0.6** self-agreement threshold with a 3-mode fallback (`page_index.py:892`, `:951`, `:978`). |
| Retrieval surface | "PageIndex has an LLM traverse the tree" | The OSS library ships **three dumb accessor tools** (`retrieve.py`); the reasoning agent is the *caller's* (the demo uses the OpenAI Agents SDK). "Tree search inspired by AlphaGo" is a metaphor — there is no search algorithm. |
| Runtime dependency | Not examined | **Vectorless but not API-less** — building the index requires an external LLM (litellm, default `gpt-4o`; `utils.py:33`, `config.yaml:1`). Inverse of MemPalace's local-first posture; collides with the air-gap default and Base Slice 0's "no knowledge reuse." |
| OSS vs cloud | Treated as one thing | Two products: the MIT OSS library (self-host) and the cloud API (OCR/scale/MCP). **`pip install pageindex` installs the cloud SDK** (`BASE_URL=api.pageindex.ai`), not the local indexer. |
| Benchmark | Not carried | The 98.7% FinanceBench number is **Mafin 2.5's** (a system "powered by PageIndex"), self-reported by VectifyAI, no independent reproduction. |
| Doctrine status | "Decision lives only in 2026-05-13 checkpoints; no crosswalk row" | **Correction:** PageIndex is named in **accepted v3.9 doctrine** (`06:178`, the `09` coverage-matrix row) with a defined `DocumentEvidenceRetrieval` node schema (`02:331`). The crosswalk row is still absent — a separate, review-status document. |

The result is not "adopt PageIndex." The result is: PageIndex is a credible document-evidence *locator* if — and only if — its output is wrapped in the Civilization's own `DocumentEvidenceRetrieval`/`KnowledgeReference` governance, gated behind Base Slice 0.

## The fail-legible crux: still no crosswalk row (but named in accepted doctrine)

The v3.9.1 technology-decision crosswalk (`DF-V3.9-EPIC-TECH-CROSSWALK`, `02-technology-decision-crosswalk-v3.9.md`) was read in full. Its decision table lists sixteen items and **PageIndex is not among them** — the string `PageIndex` / `Vectify` / `DocumentEvidenceRetriever` appears nowhere in that document. That omission stands.

> ⚠ **Fail-legible note (no *crosswalk* row — but not undocumented).** Unlike its sibling [[mempalace|MemPalace]] — which has a real crosswalk row — PageIndex was **not carried into the v3.9.1 crosswalk register**, and whether that is a deliberate scoping choice or an omission is **not stated by any source**; do not infer one. The correction TAI-RES-2026-007 adds is that PageIndex is **not** decision-less: it is named in *accepted v3.9 doctrine* — `06-memory-knowledge-capability-v3.9.md:178` (*"PageIndex is an optional DocumentEvidenceRetriever reference only. It is not required unless a later accepted decision adopts it."*) and the `09-legacy-coverage-matrix-v3.9.md:252` decision row (*"optional document evidence retrieval; not memory, truth, policy, or certification"*), atop the `DocumentEvidenceRetrieval` node schema in `02-kernel-schema-and-state-v3.9.md:331`. The crosswalk (a `status: review` document) and the accepted doctrine are two different files; the row is missing from the former, not the latter.

## Decision record and ADR disposition

TAI-RES-2026-007 §4.4 makes the determination explicit:

- **Dark Factory ADR:** **none.** A repo-wide search finds no ADR — and no `PageIndex`/`Vectify`/`DocumentEvidenceRetriever` string in the accepted **v4.0** doc set at all. PageIndex's governance today rests on accepted v3.9 doctrine (`06`, `09`, the `02` node schema), the ratified **Decision 15** external-frameworks law (`01:172`), the reviewed-planning investigation checkpoints, and this compiled page.
- **Recommended ADR action:** **no ADR now.** Nothing is adopted as a dependency, runtime, or control-plane component — the same disposition [[mempalace|MemPalace]]'s sibling evaluations reached for Solo Orchestrator and the Owain Lewis work system. The durable record is this evaluation + a per-item crosswalk/decision row + — *if* a native `DocumentEvidenceRetriever` is ever pursued — its own Factory Order → TLC arc, where design-stage CFADA is the decision record for the adopted *pattern*.
- **Civilization contribution:** **pattern-only.** The tree-structured document-evidence + page/section-traceability pattern (mapped to `DocumentEvidenceRetrieval` → `KnowledgeReference`/`source_refs`), plus the code-proven negative lesson (an LLM-built, LLM-graded index is categorically not truth). Never truth, certification evidence, memory/knowledge authority, kernel, or controller (Decision 15).

The adoption verdict is therefore: **carry PageIndex forward as an optional document-evidence adapter *pattern*, behind the `KnowledgeReference` boundary, gated after Base Slice 0.** This is not a runtime activation and assigns no implementation owner.

Two doctrine-hygiene items the evaluation surfaces: (1) the **v4.0 carry-forward gap** — `DocumentEvidenceRetriever`/`DocumentEvidenceRetrieval`/`KnowledgePage` are defined only in preserved v3.9 and were not restated in v4.0's standalone docs, so a v4.0-level home for a PageIndex adapter does not yet exist by name; (2) the **missing crosswalk row** above.

## What PageIndex actually is — now code-anchored

The following is verified against the repository at `f413c66`, not carried as upstream claim.

PageIndex turns a **PDF** (markdown is a secondary mode) into a hierarchical tree of `{title, node_id, start_index, end_index, summary, nodes[]}`. The entry point rejects any non-PDF input (`page_index.py:1065`), extracts page text with `PyPDF2` (`utils.py:388`), and builds the tree through one of three **entirely LLM-driven** modes — TOC-with-page-numbers, TOC-without, or no-TOC-generate-from-scratch (`page_index.py:611`, `:586`, `:565`). Section titles and the "1 / 1.1 / 1.2" hierarchy are asked of the model (`:503`); large sections are recursively subdivided (`:992`); node summaries and the document description are additional LLM passes (`utils.py:590`, `:623`). Calls run at `temperature=0` (`utils.py:43`), which lowers variance but does not make extraction deterministic across models or versions.

The "reasoning-based retrieval" the upstream markets is **not in the library**. `retrieve.py` exposes three pure accessors — `get_document()`, `get_document_structure()` (tree with text stripped), and `get_page_content(pages="5-7")` (raw page text via PyPDF2) — with no LLM, no ranking, and no search. The agentic traversal is demonstrated with the **OpenAI Agents SDK** in `examples/agentic_vectorless_rag_demo.py` (`:30`, `:44`), pointed at `gpt-5.4` by default (`config.yaml:3`). So the OSS library is a *tree builder plus accessors*; the retrieval intelligence is a caller-supplied agent — which is favorable for a Civilization adapter, because the reasoning stays where the Civilization already governs it.

"Vectorless" is code-true (no embedding/vector/OCR code in the package; deps are `litellm`, `pymupdf`, `PyPDF2`, `python-dotenv`, `pyyaml`), but building the index **requires an external LLM API** — `litellm` reading `OPENAI_API_KEY`, defaulting to `gpt-4o-2024-11-20` (`utils.py:22`, `config.yaml:1`) — and the sync wrapper fails *open*, returning an empty string on final failure (`utils.py:55`). Air-gapped use is possible only by pointing litellm at a self-hosted endpoint; it is not the default and is not vendored.

## The boundary

The governing boundary already exists in doctrine. A PageIndex retrieval is exactly a `DocumentEvidenceRetrieval` EventGraph node (`02-kernel-schema-and-state-v3.9.md:331`): `retriever_id, retriever_version, source_document_id, source_document_hash, query_or_need, page_refs, section_refs, retrieved_text_refs, confidence_or_quality_notes, limitations, …, linked_KnowledgeReference`. That schema **demands the governance PageIndex does not supply** — a `source_document_hash` (PageIndex hashes nothing), explicit `limitations` and `confidence_notes`, and a link to a `KnowledgeReference` carrying trust, freshness, redaction, and contradiction state (`02:317`). Retrieved evidence *"becomes usable only when represented as KnowledgeReference/source_refs and linked to EventGraph evidence"* (`06:158`), and *"memory and knowledge are advisory only"* (`04-production-workflow-runtime-v4.0.md` — accepted v4.0, doc `03:36`). Only the Release cell may certify (`04:110`), and the factory must **stop** when *"memory/knowledge contradicts EventGraph in high-risk planning"* (`05:523`).

PageIndex itself does none of this; it is deliberately a locate-and-recall engine. That is correct at the retrieval layer and wrong at the authority layer — the Civilization boundary supplies the missing governance:

- a retrieved span enters as advisory evidence, never truth;
- it is usable only once wrapped as a `DocumentEvidenceRetrieval` → `KnowledgeReference` with a source hash and limitations;
- it can never be certification evidence, and only Release (a human role in the MVP) certifies;
- any external adapter is gated behind **Base Slice 0**, which requires proving file, command, **network, and secret** boundaries plus replayable EventGraph receipts (`04:165`) — exactly the gate an OpenAI-calling indexer would need to pass.

## Benchmark reality

The upstream's headline "state-of-the-art **98.7% accuracy on FinanceBench**" needs three qualifications, the same shape as the MemPalace "best-benchmarked" caveat. It is **not the library's score** — it belongs to *"Mafin 2.5,"* an end-to-end system "powered by PageIndex," of which PageIndex is one component. It is **self-reported** — run by VectifyAI on VectifyAI's own benchmark repo, with their own human annotators resolving ambiguous ground-truth, and the comparison is not apples-to-apples (98.7% at 100% coverage vs. a competitor's 98% at 66.7%). And it is **not independently reproduced** — no leaderboard placement; independent readers flagged exactly the cherry-pick (*"a suspicious lack of any performance metrics on standard RAG/QA benchmarks … except their highly fine-tuned MAFIN2.5 system"*). The useful Civilization lesson is the benchmark *discipline*, not the number; the Civilization's metric must be stricter — *did the retrieved `KnowledgeReference` improve the gated decision it influenced?*

## Two PageIndexes: open-source library vs. cloud product

Any statement about "adopting PageIndex" must say *which* one. The **MIT-licensed OSS library** (this article's subject) is a local tree-builder plus three accessors, installed by cloning `main` — it has **no git tags, no GitHub releases, and no PyPI distribution**. The **cloud product** (pageindex.ai — long-context OCR, corpus-scale indexing, MCP, a document-chat platform, enterprise VPC/on-prem, $30–$100/mo tiers) is a separate open-core offering, and the **PyPI `pageindex` package is the cloud SDK** (hardcoded `BASE_URL=https://api.pageindex.ai`), *not* the local indexer. Only the OSS library is vendorable and auditable; the cloud API is a networked dependency incompatible with the air-gap default.

Supply-chain and maturity, from the code and repo metadata: **MIT** (clean, no copyleft); 33.8k★ but **no releases/tags** to pin (the reviewed commit `f413c66` is the natural pin); a single test file; and a **CodeQL** configuration that scans only the GitHub Actions YAML, **not the Python source** — so the "security scanning" badge does not cover the library code. Recent commits are reactive crash/packaging fixes (the `f413c66` HEAD is itself a KeyError/context-exhaustion fix). Vectify AI is a small (~1–10) London startup, founded 2023, with no verifiable funding. For any Civilization use: pin to a reviewed commit, vendor the dependency tree and the LLM path, and add the source static analysis the upstream omits.

## When and why it entered the arc

PageIndex entered as one candidate in the [[civilization-landscape-investigation]] — the April–May 2026 survey that asked whether any external repo beat Transpara's native architecture as a kernel, work owner, authority owner, runtime, or operator surface. The verdict was that none did; every "surviving" tool did so only as inspiration for a governed *native* pattern, never as a dependency or controller. PageIndex's study artifact (`pageindex-role-in-transpara-stack.md`, 2026-05-13) answered a precise question — is PageIndex a replacement for, or an augmentation of, the [[memory-knowledge-advisory|Karpathy LLM Wiki]] and the OpenBrain concept? — with **"PageIndex is an augmentation, not a replacement."** The code read confirms that framing: PageIndex reads long documents; it does not accumulate, synthesize, or govern knowledge.

> ⚠ **Fail-legible note (fork date/existence is thin).** The original seed states PageIndex was "forked into transpara-ai: 2026-05-13." No `transpara-ai/pageindex` repository was found, and no Open Brain capture naming such a fork was retrieved. What is firmly dated is the *investigation's study* (2026-05-13) and now the *code read* at `f413c66` (2026-07-03). The fork act and date are carried as **task-asserted, not corroborated**. (For the contrasting case where a fork date *is* sourced, see [[mempalace|MemPalace]].)

## How PageIndex relates to its neighbours in the survey

The investigation deliberately separated PageIndex from the memory and knowledge candidates it is confused with, and the code sharpens each line:

- **vs. [[memory-knowledge-advisory|the Karpathy LLM Wiki pattern]]:** the wiki is a *compiled, accumulating knowledge artifact*; PageIndex is *retrieval over raw source documents before synthesis* — "how the wiki should *read* raw long documents," not the wiki itself.
- **vs. [[ob1|OpenBrain / OB1]]:** OB1 is a cross-tool persistent *memory substrate*; PageIndex is a *document-evidence primitive* that could sit under it (an `ask_long_document(doc_id, question)` tool). It does not replace OB1.
- **vs. [[mempalace|MemPalace]]:** both are "optional adapter/subsystem candidates," but MemPalace is advisory *memory recall* (mapped to `MemoryReference`, local-ONNX by default) while PageIndex is *document evidence* (mapped to `KnowledgeReference`/`source_refs`, external-LLM by default). MemPalace has a crosswalk row and a proposed ADR-0008; PageIndex has neither.
- **vs. [[event-graph|EventGraph]] and certification:** off-limits, categorically. Retrieved spans are inputs to be cited as `DocumentEvidenceRetrieval` records, never the record itself.

## Status caveat: reviewed planning vs. ratified doctrine

The classification rests on layered sources of differing authority. **Ratified:** Decision 15 (external frameworks stay outside control roles) and the accepted v3.9 memory/knowledge doctrine that names PageIndex as an optional `DocumentEvidenceRetriever` reference with a defined node schema (`06`, `09`, `02`). **Reviewed planning:** the U4 "DocumentEvidenceRetriever optional pattern" proposal and the priority-#4 ranking come from investigation checkpoints marked *"proposed only … not applied to canonical v3.8."* **Documented gaps:** no PageIndex row in the review-status v3.9.1 crosswalk, and no restatement of the `DocumentEvidenceRetriever` pattern in accepted v4.0. Treat the adapter classification and the U4 proposal as reviewed planning, not shipped fact; treat the boundary (advisory only, never truth/cert) as ratified law.

## Sources & provenance

Primary source is the code-anchored evaluation; doctrine and prior research are first-party Transpara documents.

- `raw/civilization/external-landscape/tai-res-2026-007-pageindex-evaluation.md` — **TAI-RES-2026-007 v1.0.0**, the code-anchored evaluation of `VectifyAI/PageIndex` @ `f413c66` (2026-07-03). This page is its digest; the evaluation carries the full file:line anchors, the v4.0/v3.9 doctrine map, and the §4.4 determination.
- `dark-factory/research/pageindex-role-in-transpara-stack.md` (2026-05-13) — the indexed-only study ("augmentation, not replacement"); retained for provenance, superseded for "what it is" facts.
- `dark-factory/research/checkpoints/2026-05-13-07-…` and `…-10-…` — the Phase 5 inclusion matrix (class `Optional adapter / pattern`; overlap `KnowledgeReference`/`source_refs`; risk "retrieval mistaken for truth"; explicit rejection) and the closeout (priority #4; `U4 DocumentEvidenceRetriever`; "proposed only"; post-Base-Slice-0 gating).
- `dark-factory/v3.9/06-memory-knowledge-capability-v3.9.md` (`06:156`, `06:178`), `…/02-kernel-schema-and-state-v3.9.md` (`02:317`, `02:331`), `…/09-legacy-coverage-matrix-v3.9.md` (`09:252`) — accepted v3.9 doctrine defining the `DocumentEvidenceRetriever` pattern and naming PageIndex.
- `dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` (`status: review`) — read in full; **establishes the absence** of a PageIndex row.
- `dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md` (`01:172`) — Decision 15. `dark-factory/v4.0/04-production-workflow-runtime-v4.0.md` — accepted v4.0 `source_refs` and Base Slice 0 adapter gate.

Upstream, cited as **context only** (never re-published, never a PR/push target, per org rules): `https://github.com/VectifyAI/PageIndex/tree/f413c66` and `https://pageindex.ai/blog/pageindex-intro`. The 98.7% FinanceBench figure and all marketing claims are the upstream's own and are not asserted here as Transpara findings.

Cross-links ([[civilization-landscape-investigation]], [[dark-factory]], [[mempalace]], [[ob1]], [[memory-knowledge-advisory]], [[event-graph]], [[base-slice-0]], [[v3-9]]) are forward references where targets are not yet compiled.

**Conflicts and gaps stated, not resolved:** (1) the **missing crosswalk row** — recorded as a fact, with no source-supported reason, though PageIndex *is* named in accepted v3.9 doctrine; (2) the **v4.0 carry-forward gap** — the `DocumentEvidenceRetriever` pattern is accepted in preserved v3.9 but not restated in v4.0; (3) the **fork act and 2026-05-13 fork date** — task-asserted, uncorroborated; (4) the **98.7% benchmark** — real but self-reported and not the library's number. The correct status: credible document-evidence adapter *pattern*; no ADR; no authority; no runtime activation; Base Slice 0 first.

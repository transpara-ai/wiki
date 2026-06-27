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
last_compiled: 2026-06-13
sources:
  - raw/transpara/dark-factory/research/pageindex-role-in-transpara-stack.md  # the dedicated PageIndex study, 2026-05-13 — "augmentation, not replacement"; vectorless/ToC-tree description; three-tool runtime shape
  - raw/transpara/dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md  # Phase 5 matrix: PageIndex class = "Optional adapter / pattern"; marginal contribution; risk; recommendation
  - raw/transpara/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # closeout: PageIndex under optional adapter/subsystem candidates; priority #4; U4 DocumentEvidenceRetriever; rejected as truth/cert authority
  - raw/transpara/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # DF-V3.9-EPIC-TECH-CROSSWALK v3.9.1 — read in full; PageIndex has NO row (the fail-legible crux of this article)
  - raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # Decision 15: external frameworks stay outside control roles
  - https://github.com/VectifyAI/PageIndex  # upstream repo — UPSTREAM CONTEXT ONLY, never re-published, never a PR/push target
  - https://pageindex.ai/blog/pageindex-intro  # upstream intro post — context only; per the study, the live page was not directly fetched (search-indexed text only)
confidence:
  crosswalk_row: NONE — read the v3.9.1 crosswalk in full; PageIndex/VectifyAI is absent from the decision table and the per-item notes. The seed asked for "this project's decision row"; there is no row. Everything downstream is sourced from the 2026-05-13 investigation checkpoints, which predate the crosswalk. This is the article's central fail-legible point.
  investigation_classification: high — the Phase 5 matrix and the closeout both name PageIndex explicitly and agree on its class; quoted verbatim below.
  fork_date_and_existence: thin / asserted by task framing — the seed states "Forked into transpara-ai: 2026-05-13." No `transpara-ai/pageindex` repo was found on disk this run, and no Open Brain capture naming such a fork was retrieved. What IS dated 2026-05-13 is the investigation's PageIndex study (a fetch/analysis of the upstream). Treated as reconstructed, not proven. See "When and why it entered the arc."
  upstream_description: upstream-claimed, not verified — the "what it is" facts (vectorless, ToC tree, three tools) come from the study's reading of the upstream README/blog, which is upstream documentation. Carried as context, never as Transpara findings or benchmark claims.
  implementation_state: thin — no implementation owner selected; nothing in the surveyed sources shows PageIndex wired into the platform. Adapter evaluation is explicitly gated behind [[base-slice-0|Base Slice 0]].
---

# PageIndex

**A forked public document-retrieval project that the [[civilization-landscape-investigation]] evaluated and carried forward as an *optional adapter* — a future "DocumentEvidenceRetriever" usable behind a boundary, never as truth, certification evidence, or a memory/knowledge authority.** PageIndex (upstream: `VectifyAI/PageIndex`) is a vectorless, reasoning-based RAG framework: instead of embedding-and-chunking a document, it builds a hierarchical table-of-contents tree over the document and has an LLM traverse that tree to decide where to read. The subject of *this* article is Transpara's evaluation and decision about PageIndex — not the upstream project's own documentation, which is cited only as context below. Per organization rules the upstream is never re-published, never pushed to, and never a PR target.

The decision is recorded, but **it does not live where the seed expected it to.** The seed asked for PageIndex's row in the v3.9 technology-decision crosswalk. There is no such row.

## The fail-legible crux: there is no crosswalk row

The v3.9.1 crosswalk (`DF-V3.9-EPIC-TECH-CROSSWALK`, `02-technology-decision-crosswalk-v3.9.md`) was read in full this run. Its decision table lists sixteen items — MetaGPT, OpenManus, OpenBrain, MemPalace, the two Karpathy projects, Hermes, OpenClaw, the Microsoft Agent Governance Toolkit, gStack, Paperclip, Symphony, Multica, Miro Flow, Miro Thinker, and the Brett Brewer org-memories analysis. **PageIndex is not among them, and the string `PageIndex` / `Vectify` / `DocumentEvidenceRetriever` appears nowhere in the document.**

> ⚠ **Fail-legible note (no decision row).** Unlike its sibling [[mempalace|MemPalace]] — which has a real crosswalk row — PageIndex was **not carried into the v3.9.1 crosswalk register.** Whether this is a deliberate scoping choice or an omission is **not stated by any source read this run**; do not infer one. What *is* recorded about PageIndex lives one document upstream, in the 2026-05-13 investigation checkpoints (dated five days before the crosswalk's 2026-05-18). The rest of this article is grounded in those checkpoints. Where the investigation is silent, the entry is marked thin.

## When and why it entered the arc

PageIndex entered as one candidate in the [[civilization-landscape-investigation]] — the April–May 2026 survey that pulled ~22 external repos into scope to ask whether any of them beat Transpara's native architecture as a kernel, work owner, authority owner, runtime, or operator surface. The investigation's verdict was that none did ([[civilization-landscape-investigation]] closeout, 2026-05-13: *"the landscape review does not reveal a better kernel … than the native v3.8 architecture"* — itself an analysis verdict, not a proof). Every external tool that "survived" did so only as inspiration for a governed *native* pattern, never as a dependency or controller.

PageIndex's study artifact is dated **2026-05-13** (`pageindex-role-in-transpara-stack.md`). It was prompted by a precise question: *is PageIndex a replacement for, or an augmentation of, the [[memory-knowledge-advisory|Karpathy LLM Wiki idea and the OpenBrain concept]]?* The study's answer, stated plainly: **"PageIndex is an augmentation, not a replacement."**

> ⚠ **Fail-legible note (fork date/existence is thin).** The seed states PageIndex was "forked into transpara-ai: 2026-05-13." No `transpara-ai/pageindex` repository was found on disk this run, and no Open Brain capture naming such a fork was retrieved. What is firmly dated 2026-05-13 is the *investigation's study* of PageIndex. The fork act and date are carried here as **task-asserted, not corroborated** by a repo or capture read this run. (For the contrasting case where a fork date *is* sourced, see [[mempalace|MemPalace]], whose `4/08 mempalace <- MemPalace` line comes from a dated Open Brain capture.)

## What the investigation decided, and why

Two investigation checkpoints name PageIndex explicitly, and they agree.

**Phase 5 inclusion matrix** (`2026-05-13-07-…`) classes PageIndex as **`Optional adapter / pattern`**, "already in v3.8? → partial/no named." Its recorded fields:

- **Marginal contribution:** "Long-document evidence retrieval with page/section traceability."
- **Main overlap:** `KnowledgeReference` / `source_refs` (the native evidence-citation primitives).
- **Main risk:** "Retrieval mistaken for truth."
- **Recommendation:** "Optional DocumentEvidenceRetriever; not memory/wiki/truth."

The same matrix, in its knowledge-and-evidence layer analysis, draws the boundary against the adjacent pattern: *"Karpathy Wiki is compiled knowledge pattern. PageIndex is document-evidence retrieval. Neither is truth or certification authority."* And in its explicit-rejections list: **"PageIndex must not become truth or certification evidence by itself."**

**The closeout** (`2026-05-13-10-…`) places PageIndex under **"optional adapter/subsystem candidates"** (alongside the Agent Governance Toolkit, Hermes self-evolution, [[mempalace|MemPalace]], org-memories, and [[ob1|OB1]]). It ranks PageIndex **#4** in priority order for possible implementation value, with the qualifier: *"Useful document evidence retrieval adapter. Must map page/section evidence to `KnowledgeReference`/`source_refs`."*

So the decision is: **carry PageIndex forward as a named, optional adapter candidate — a possible "DocumentEvidenceRetriever" — bounded so its output is advisory evidence, never the platform's source of truth or its certification record.** This is consistent with the platform-wide law the investigation kept invoking: external frameworks are adapters, patterns, or references, never controllers, kernels, or authorities (the canonical one-line rule is v3.9 Decision 15; the per-item investigation detail is reviewed planning, not ratified doctrine — see the status note below).

## The U4 thread: from candidate to a proposed native pattern

The investigation did not stop at "carry it forward." In Phase 7 it folded PageIndex into a proposed canonical update. The closeout's proposed update set includes **`U4. DocumentEvidenceRetriever optional pattern`**, and its earlier gap list pairs the two directly: among the "high-priority design decisions" is *"DocumentEvidenceRetriever using PageIndex."* The Phase 5 matrix had already flagged the same candidate change: *"Optional DocumentEvidenceRetriever pattern, likely informed by PageIndex."*

Crucially, U4 is an *optional pattern*, ranked low (P3) in the closeout's recommended adoption priority, and — like every Phase 7 update — **"proposed only … not applied to canonical v3.8."** The shape of the move is the recurring one across this whole investigation: an external tool becomes the *inspiration for a governed native boundary* (here, a retriever that emits `KnowledgeReference` evidence under the existing advisory-evidence rules), not a dependency that gets imported.

> ⚠ **Fail-legible note (U4 is a proposal, and PageIndex isn't named in the v3.9 crosswalk).** Two distinct things are easy to conflate. (1) `U4 DocumentEvidenceRetriever` was *proposed* by the investigation as a native optional pattern informed by PageIndex; whether U4 was subsequently adopted into accepted v3.9 doctrine is **not established by any source read this run** ([[v3-9]]). (2) The *tool* PageIndex still has **no row** in the v3.9.1 crosswalk register. Carrying U4 forward (a pattern) and registering PageIndex (a tool) are separate acts; only the first is sourced as having happened, and only as a proposal.

## Gating: nothing before Base Slice 0

Any actual use of PageIndex is sequenced behind native foundations. The closeout's "adapter evaluation after Base Slice 0" workstream is explicit: *only after [[base-slice-0|Base Slice 0]]* does it list *"DocumentEvidenceRetriever using PageIndex"* — alongside the [[runtime-broker|RuntimeBroker]] adapter POC and the [[memory-knowledge-advisory|memory/knowledge]] governance work. The Phase 5 matrix carries the same prerequisite for all optional adapters: they are worth evaluating "after v3.8 boundaries and tests exist," not before.

## Upstream context only — what PageIndex actually is

The following is the upstream project's self-description as read by the investigation's study; it is **context, not a Transpara finding or endorsement**, and the numbers/claims are the upstream's own.

PageIndex is a **vectorless, reasoning-based RAG framework**. The study summarizes the upstream claim: vector search finds semantic *similarity*, but professional document QA often needs *relevance, structure, and reasoning* — so PageIndex builds a hierarchical "table of contents" tree over a document and has an LLM traverse that tree to decide where to look. Its two-step flow, per the study's reading of the upstream README: generate a ToC/tree structure, then perform reasoning-based retrieval through tree search. The repo's document-QA demo, as described, hands the agent only three tools — `get_document()`, `get_document_structure()`, and `get_page_content()` — so it reads metadata, then the tree, then fetches tight page ranges rather than the whole document. The study's one-line shape:

```
Document → structural tree index → reasoning-guided retrieval → answer/evidence
```

The study positions PageIndex as strongest for long, structured documents — filings, contracts, legal opinions, technical manuals, standards, research papers — where natural sections beat artificial chunks and page/section traceability matters. It positions PageIndex as *weak as a replacement* for a cross-agent memory database, durable project state, capture workflows, evolving wiki pages, or contradiction resolution across sources — which the study assigns to [[ob1|OpenBrain/OB1]] and the Karpathy-wiki pattern, not to PageIndex.

> ⚠ **Fail-legible note (upstream fetch was partial).** The study states plainly that the live PageIndex blog page *"could not be directly fetched"* and that it relied on **search-indexed text plus GitHub-connector access** to the README and demo code. So even the upstream-context description rests on indexed/partial source, not a full first-party crawl — and none of it has been independently re-verified by Transpara. The benchmark or performance claims on the upstream's marketing pages are **not carried into this article at all**, because no source read this run verified them.

## How PageIndex relates to its neighbours in the survey

The investigation deliberately separated PageIndex from the memory and knowledge candidates it is easily confused with:

- **vs. [[memory-knowledge-advisory|the Karpathy LLM Wiki pattern]] (U5):** the wiki is a *compiled, accumulating knowledge artifact*; PageIndex is *retrieval over raw source documents before synthesis*. The study's framing: PageIndex is "how the wiki should *read* raw long documents," not the wiki itself.
- **vs. [[ob1|OpenBrain / OB1]]:** OB1 is a cross-tool persistent *memory substrate*; PageIndex is a *document-evidence primitive* that could sit under it (the study sketches an `ask_long_document(doc_id, question)` tool backed by PageIndex). PageIndex does not replace OB1.
- **vs. [[mempalace|MemPalace]]:** both are "optional adapter/subsystem candidates," but MemPalace is advisory *memory recall* (mapped to `MemoryReference`) while PageIndex is *document evidence* (mapped to `KnowledgeReference`/`source_refs`). MemPalace got a crosswalk row; PageIndex did not.
- **vs. [[event-graph|EventGraph]] and certification:** off-limits. The rejection is categorical — PageIndex "must not become truth or certification evidence by itself." Retrieved spans are inputs to be cited, not the record.

## Status caveat: reviewed planning vs. ratified doctrine

Most of what is recorded about PageIndex comes from investigation *checkpoints* — research artifacts, not canonical architecture. The closeout itself states the canonical v3.8 baseline was left unchanged and that the proposed updates (U1–U10, including U4) "were proposed only." The crosswalk that *would* normally hold a per-item decision is `status: review` / `canonical: false`, and in any case contains no PageIndex row. The only ratified, doctrine-level rule that clearly governs PageIndex is the platform-wide boundary that external frameworks stay out of kernel/truth/authority/certification roles ([[dark-factory]], v3.9 Decision 15). Treat the adapter classification and the U4 proposal as **reviewed planning**, not shipped fact.

## Sources & provenance

Compiled from first-party Transpara documents read this run:

- `dark-factory/research/pageindex-role-in-transpara-stack.md` (2026-05-13) — the dedicated PageIndex study: "augmentation, not replacement"; the vectorless/ToC-tree description; the three-tool runtime shape; the explicit note that the upstream blog could not be directly fetched (search-indexed + GitHub-connector reading only).
- `dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md` — PageIndex inclusion class (`Optional adapter / pattern`), marginal contribution, overlap (`KnowledgeReference`/`source_refs`), risk ("Retrieval mistaken for truth"), recommendation ("Optional DocumentEvidenceRetriever; not memory/wiki/truth"), and the explicit rejection ("must not become truth or certification evidence by itself").
- `dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md` — PageIndex under "optional adapter/subsystem candidates," priority #4; `U4 DocumentEvidenceRetriever optional pattern`; "DocumentEvidenceRetriever using PageIndex" as a high-priority design decision and as a post-Base-Slice-0 adapter-evaluation item; the "proposed only / canonical v3.8 unchanged" qualifier.
- `dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` (`DF-V3.9-EPIC-TECH-CROSSWALK` v3.9.1, `status: review`) — read in full; **establishes the absence**: PageIndex has no row and is not mentioned. This is the article's central fail-legible finding.

Upstream, cited as **context only** (never re-published, never a PR/push target, per org rules): `https://github.com/VectifyAI/PageIndex` and `https://pageindex.ai/blog/pageindex-intro`. All upstream-derived description in this article is mediated through the Transpara study above, which itself relied on partial (indexed) access; no upstream marketing or benchmark claim is asserted here.

Cross-links ([[civilization-landscape-investigation]], [[dark-factory]], [[mempalace]], [[ob1]], [[memory-knowledge-advisory]], [[event-graph]], [[base-slice-0]], [[runtime-broker]], [[v3-9]]) are forward references where targets are not yet compiled.

**Conflicts and gaps stated, not resolved:** (1) the **missing crosswalk row** — recorded as a fact, with no source-supported reason for the absence; (2) the **fork act and 2026-05-13 fork date** — task-asserted, uncorroborated by any repo or Open Brain capture read this run; (3) **U4 adoption status** — proposed by the investigation, not confirmed as accepted v3.9 doctrine by anything read this run; (4) **upstream description provenance** — partial/indexed access, never independently verified by Transpara.

---
document_id: TAI-RES-2026-007
title: PageIndex Capability Evaluation (VectifyAI — Vectorless, Reasoning-based RAG)
subtitle: Code-Anchored Assessment Against the Transpara-AI Civilization Document-Evidence Boundary, and Strategic Learning Opportunities
version: 1.0.0
status: RELEASED
date: 2026-07-07
author: Michael Saucier
reviewer: Transpara AI Hive
owner: Research & Strategic Intelligence
org: Transpara AI
repo: transpara-ai/wiki
classification: PUBLIC — external-landscape research (this repo is public; no secrets; only public upstream code and already-published Civilization doctrine are quoted; the upstream `VectifyAI/PageIndex` is cited as context and is never re-published, never a push/PR target)
companion_to: TAI-RES-2026-001 (Sakana AI), TAI-RES-2026-002 (Hermes Agent & Self-Evolution), TAI-RES-2026-003 (Google Open Knowledge Format), TAI-RES-2026-004 (MemPalace), TAI-RES-2026-005 (Solo Orchestrator), TAI-RES-2026-006 (Owain Lewis Work System)
supersedes_for_presentation: raw/transpara/dark-factory/research/pageindex-role-in-transpara-stack.md  # the 2026-05-13 indexed-only study; retained for provenance, superseded for the "what it is" facts by the code-anchored read below
evaluated_artifact: https://github.com/VectifyAI/PageIndex/tree/f413c66  # HEAD f413c66fee0bfbb7291c389333f9cc1adac68d57, 2026-07-03, read in full from a local clone
---

## Revision History

| Version | Date | Description | Author |
|---|---|---|---|
| 1.0.0 | 2026-07-07 | Initial release — first **code-anchored** evaluation of PageIndex (`VectifyAI/PageIndex` @ `f413c66`, 2026-07-03), the ~3,000-line open-source library read in full from a local clone. Supersedes the 2026-05-13 indexed-only study for the "what it is" facts; adds the runtime dependency surface, the OSS-vs-cloud split, supply-chain/maturity, and benchmark-provenance findings. Capability comparison against the accepted **v4.0** doctrine baseline, with preserved **v3.9** supplying the `DocumentEvidenceRetriever`/`KnowledgeReference` schemas PageIndex maps to. Includes the §4.4 decision-record determination (no ADR exists; none created now; **pattern-only** contribution) and five strategic learning opportunities plus the inverse analysis. | M. Saucier / Hive |

---

## Abstract

This document evaluates **PageIndex** (`VectifyAI/PageIndex`) — a **vectorless, reasoning-based RAG** framework that indexes long documents into a hierarchical "table-of-contents" tree and lets an LLM agent traverse that tree to retrieve evidence [1][2]. It is the seventh in the external-landscape evaluation series, and the second (after MemPalace, TAI-RES-2026-004) to take a candidate that already had a compiled wiki page and **upgrade it from an indexed-only investigation stub to a code-anchored assessment** by reading the actual repository — HEAD `f413c66` (2026-07-03), ~3,000 lines of Python, read in full from a local clone [1]. The Civilization baseline is the accepted **v4.0** doctrine set, with the preserved **v3.9** baseline supplying the detailed `DocumentEvidenceRetriever`/`KnowledgeReference` schemas that v4.0 did not restate [12–19].

The central finding is that **the 2026-05-13 investigation's disposition was correct, and the code now proves the load-bearing half of it.** PageIndex is a genuinely useful document-structuring and evidence-locating primitive, and it is the reference implementation of the Civilization's already-named optional `DocumentEvidenceRetriever` pattern. But its "structure" is not a parsed artifact — it is an **LLM-generated one**. Every node, title, hierarchy number, page mapping, and summary in the tree is produced by an `llm_completion` call (default `gpt-4o-2024-11-20`), and the only "validation" is a second LLM being asked whether a sampled title appears on its mapped page, accepted at a hard-coded 0.6 self-agreement threshold with a three-mode fallback cascade (`pageindex/page_index.py:892`, `:951`, `:978`). Building the index therefore **requires an external LLM API** (`pageindex/utils.py:33`, `:22`; `config.yaml:1`) — the inverse of MemPalace's local-first posture, and a direct collision with both the air-gap default and Base Slice 0's "no LLM planning, no knowledge reuse" rule (`DF-V4.0-RUNTIME-004`, doc `04:135`). This is the code-level proof of the investigation's #1 recorded risk, **"retrieval mistaken for truth"** [11].

Three "which PageIndex?" facts frame every downstream conclusion: (1) the **MIT-licensed OSS library** is a local tree-builder plus three *dumb accessor tools* (`pageindex/retrieve.py`); the "reasoning retrieval" and "tree search inspired by AlphaGo" are performed by a caller-supplied LLM agent (the demo uses the OpenAI Agents SDK), not by PageIndex [2]; (2) the **cloud product** (pageindex.ai — OCR, scale, MCP, chat) is a separate open-core offering, and `pip install pageindex` installs the *cloud SDK* (`BASE_URL=https://api.pageindex.ai`), **not** the local indexer [6][7]; (3) the flagship **98.7% FinanceBench** number belongs to "Mafin 2.5," an end-to-end system *powered by* PageIndex, self-reported by VectifyAI with author-run human grading and no independent reproduction [2][4][9]. Adoption language must say *which* PageIndex it means.

The one-line result: **PageIndex retrieves what a document says; the Civilization governs what a retrieval is allowed to change.** The disposition is unchanged and now firmer — optional **advisory document-evidence adapter/pattern**, mapped to `DocumentEvidenceRetrieval` → `KnowledgeReference`/`source_refs`, gated behind Base Slice 0, and **never** truth, certification evidence, memory/knowledge authority, or a control-plane primitive (Decision 15) [11][14]. §4.4 records the determination (no ADR exists; none is created now; pattern-only), and the evaluation surfaces two documented doctrine gaps: v4.0 did not carry the `DocumentEvidenceRetriever` pattern forward by name, and PageIndex still has no row in the v3.9.1 technology-decision crosswalk.

---

## 1. Introduction and Scope

This evaluation re-opens the PageIndex research at the request of the operator, to analyze it *the same way MemPalace was analyzed* in TAI-RES-2026-004: read the actual upstream code rather than re-summarizing marketing, produce first-party Transpara findings, and end with an explicit ADR/contribution determination. The prior PageIndex artifacts — a 2026-05-13 study [10], two investigation checkpoints [11], and the compiled wiki page [12] — were grounded in *indexed/partial* upstream access and treated all "what it is" claims as unverified upstream context. This document replaces that partial access with a full read of the repository.

The evaluation covers:

- **The PageIndex OSS library** @ `f413c66` (2026-07-03) — the `pageindex/` package (`page_index.py` 1,145 lines; `utils.py` 711; `page_index_md.py` 341; `client.py` 234; `retrieve.py` 137; `config.yaml`; `__init__.py`), the CLI (`run_pageindex.py`), the agentic demo (`examples/agentic_vectorless_rag_demo.py`), the single test (`tests/test_issue_163.py`), `requirements.txt`, and `LICENSE` — all read as ground truth [1].
- **The upstream self-description** — `README.md`, the blog/framework claims, and the benchmark repository — read as *upstream context*, verified against the code where they overlap [2][4].
- **The external maturity surface** — GitHub repository metadata, PyPI packaging, the cloud service, the company, and the security/CI posture — third-party-cited with confidence tags [6][7][8][9].
- **The Civilization v4.0 baseline** — the accepted doctrine set (`DF-V4.0-README` v4.0.54 + docs 01–07, all `status: accepted, canonical: true`), with the preserved v3.9 baseline (`02` kernel schema, `06` memory/knowledge capability, `09` legacy coverage matrix, `01` Decision 15) supplying the detailed primitives [12–19].
- **The prior Transpara decision** — the Phase 5 inclusion matrix and the landscape-investigation closeout [11], the study [10], and the compiled wiki page [12].

**Evidence base and source discipline.** Per the standing rule that *code is ground truth while READMEs and marketing may be aspirational*, every mechanism claim about PageIndex is **code-anchored** with a `pageindex/<file>:<line>` reference, read directly from the clone at `f413c66` [1]. Popularity, benchmark, company, and reception claims are **third-party-cited** and carried at lower confidence with `[Verified]`/`[Reported]`/`[Marketing]` tags inherited from the external-signals sweep [6][7][8][9]. The Civilization side is **doctrine-anchored**: quotes come from the accepted v4.0 docs and the preserved v3.9 schemas, cited by doc number and line [12–19]. One asymmetry is acknowledged: PageIndex *runs today* (33.8k★, a live cloud product), while the Civilization's `DocumentEvidenceRetriever` exists only as an accepted v3.9 schema with no implementation and no v4.0 restatement; §4 treats that honestly in both directions.

**Organizational boundary.** `VectifyAI/PageIndex` is an external upstream. It is cited here as context only; it is never re-published into this repo, and it is never a push, PR, or merge target. All PageIndex-derived description below is either read from the local clone (code) or attributed to upstream marketing (claims).

---

## 2. PageIndex: Capability Overview

### 2.1 The Author and Product Surface (third-party-cited)

PageIndex is built by **Vectify AI** (UK entity "VECTIFY AI LIMITED," Companies House #14827188, London, founded 2023), a small startup (~1–10 people) whose founders are **Mingtian Zhang** (CEO; UCL machine-learning PhD) and **Yu Tang** ("Ray") [8]. No institutional funding round or accelerator batch could be verified; treat "funded" as unconfirmed [8]. The project launched publicly ~September 2025 [2]. It anchors a small "long-context AI infra" ecosystem the README advertises — OpenKB (a document-to-wiki compiler), ChatIndex (tree indexing for conversation memory), ConDB (a KV-cache context DB), and a PageIndex MCP server [2].

The product exists in three distinguishable forms, which §2.6 develops and which the rest of this section keeps separate:

1. the **open-source library** (this evaluation's primary subject) — MIT, self-hosted, standard PDF parsing;
2. the **cloud service** (pageindex.ai) — hosted API, "long-context OCR," a ChatGPT-style document chat, MCP, and enterprise VPC/on-prem, priced $30–$100/mo across tiers [7];
3. the **Mafin 2.5** benchmark system — the thing that scores 98.7% on FinanceBench, "powered by PageIndex" [2][4].

### 2.2 What PageIndex Builds — the LLM-Constructed Tree Index (code-anchored)

The library's job is to turn a **PDF** (or markdown) into a hierarchical tree of `{title, node_id, start_index, end_index, summary, nodes[]}` records. The public entry `page_index()` (`pageindex/page_index.py:1105`) routes into `page_index_main()` (`:1058`), which **rejects any non-PDF input** — `raise ValueError("Unsupported input type. Expected a PDF file path or BytesIO object.")` (`:1065`) — extracts page text with `PyPDF2` (or optionally PyMuPDF) via `get_page_tokens()` (`pageindex/utils.py:388`), and hands the page list to `tree_parser()` (`:1021`).

The decisive fact is that **the tree is produced entirely by LLM calls; there is no deterministic parser anywhere in the pipeline.** `tree_parser()` first calls `check_toc()` (`:685`) to decide, via `toc_detector_single_page()` (`:104`, an LLM yes/no per page), whether the document even has a table of contents, then dispatches `meta_processor()` (`:951`) into one of three fully LLM-driven modes:

- **`process_toc_with_page_numbers`** (`:611`) — when the PDF has a TOC *with* printed page numbers: the LLM transforms the raw TOC text into JSON (`toc_transformer`, `:264`), the LLM maps entries to physical page tags (`toc_index_extractor`, `:234`), and a page offset is computed by taking the statistical **mode of the differences** between printed and physical pages (`calculate_page_offset`, `:383`).
- **`process_toc_no_page_numbers`** (`:586`) — TOC present but unnumbered: the LLM fills physical indices page-group by page-group (`add_page_number_to_toc`, `:450`).
- **`process_no_toc`** (`:565`) — no TOC at all: the LLM *generates* the hierarchy from scratch, page group by page group (`generate_toc_init` `:531`, `generate_toc_continue` `:496`), inventing the section titles and the "1 / 1.1 / 1.2" structure numbering it is prompted to produce (`:503`, `:536`).

Large sections are then subdivided **recursively** — `process_large_node_recursively()` (`:992`) re-runs the no-TOC generator on any node exceeding both `max_page_num_each_node` (10) and `max_token_num_each_node` (20,000) (`config.yaml:5`). Optional post-passes add node IDs (`write_node_id`, `utils.py:133`), per-node **LLM summaries** (`generate_summaries_for_structure`, `utils.py:590`), and a one-line **LLM document description** (`generate_doc_description`, `utils.py:623`). The output shape is stable and useful — an example financial-report tree ships in `examples/documents/results/` — but every field in it originated from a model, not from the document's own machine-readable structure. The calls run at `temperature=0` (`utils.py:43`), which reduces run-to-run variance but does not make the extraction deterministic across model versions or providers.

**Finding (2.2).** PageIndex's index is a *probabilistic LLM artifact*. This is not a defect for its intended use — locating relevant sections — but it is dispositive for the Civilization boundary: a structure that an LLM inferred is exactly the kind of thing that "must not become truth or certification evidence by itself" [11].

### 2.3 Self-Verification and the Fallback Cascade (code-anchored)

PageIndex is aware that an LLM-built index can be wrong, and it self-checks — but the check is **an LLM grading an LLM**, not validation against ground truth. After building a candidate tree, `meta_processor()` calls `verify_toc()` (`page_index.py:892`), which samples items and, for each, invokes `check_title_appearance()` (`:13`) — a prompt that asks the model *"check if the given section appears or starts in the given page_text … do fuzzy matching"* (`:26`) — then computes an accuracy over the sample (`:943`). The acceptance logic (`:978`) is a hard-coded ladder:

- `accuracy == 1.0` and no incorrect items → **accept**;
- `accuracy > 0.6` → attempt repair, `fix_incorrect_toc_with_retries()` (max 3 attempts, `:870`);
- otherwise → **fall back** to the next construction mode (`with_page_numbers` → `no_page_numbers` → `no_toc`), and if the last mode fails, `raise Exception('Processing failed')` (`:989`).

There is also an early bail — if the last physical index is less than half the page count, `verify_toc` returns `(0, [])` (`:902`) — and a defensive `validate_and_truncate_physical_indices()` (`:1116`) that nulls out any index pointing beyond the document. These are sensible self-consistency guards. But the "0.6 self-agreement" threshold, the fuzzy same-model check, and the mode-fallback cascade are **heuristics for reducing obvious extraction errors**, not a correctness proof. A confidently mis-placed node passes if the same model agrees it looks right — precisely the failure the Civilization's evidence model is built to refuse (§3.2).

### 2.4 "Reasoning Retrieval" — Three Accessor Tools, and the Agent Loop Is the Caller's (code-anchored)

The retrieval side of the OSS library is deliberately thin. `pageindex/retrieve.py` exposes exactly **three functions, all pure accessors with no LLM and no ranking**: `get_document()` returns metadata (`:81`), `get_document_structure()` returns the tree JSON with the heavy `text` fields stripped to save tokens (`:100`), and `get_page_content(pages="5-7")` extracts raw page text for a range via `PyPDF2` (`:110`, `_get_pdf_page_content` `:36`). That is the entire "retrieval" surface the library ships.

The "**agentic reasoning-based retrieval through tree search**" that the README markets [2] is **not in the library** — it is demonstrated in `examples/agentic_vectorless_rag_demo.py`, which builds an agent with the **OpenAI Agents SDK** (`from agents import Agent, Runner, function_tool`, `:30`), registers the three PageIndex accessors as tools (`:62`), points it at `client.retrieve_model` (default `gpt-5.4`, `config.yaml:3`), and instructs it: *"Call get_document() first … get_document_structure() to identify relevant page ranges … get_page_content(pages="5-7") with tight ranges; never fetch the whole document … Answer based only on tool output"* (`:44`). The "tree search inspired by AlphaGo" framing (README `:50`) is a metaphor: there is **no search algorithm** in the code — no scoring, no beam, no MCTS — only an LLM agent reading a JSON tree and calling `get_page_content`.

**Finding (2.4).** The OSS library ships a *tree builder plus accessors*; the retrieval intelligence is a caller-supplied LLM agent (or the cloud). This is favorable for a Civilization adapter — the "reasoning" stays in the agent the Civilization already governs, and the tool surface is small and legible — but it means "PageIndex retrieval quality" is really "your agent + your model," not a property the library guarantees.

### 2.5 The Runtime Dependency Surface — Vectorless but Not API-less (code-anchored)

"Vectorless" is code-true: a repository-wide grep for embedding/vector/FAISS/Chroma/OCR code in `pageindex/` returns nothing, and `requirements.txt` lists only `litellm==1.84.0`, `pymupdf==1.26.4`, `PyPDF2==3.0.1`, `python-dotenv==1.2.2`, and `pyyaml==6.0.2` — **no vector database and no embedding model** [1]. Removing embeddings removes one offline dependency, and the README's "no vibe retrieval, explicit page references" pitch (`:69`) is a real traceability advantage over chunk-and-embed RAG.

But **building the index requires an external LLM API.** Every extraction step routes through `llm_completion()`/`llm_acompletion()` (`utils.py:33`, `:63`), thin wrappers over `litellm` that read `OPENAI_API_KEY` (with a `CHATGPT_API_KEY` alias, `:22`) and default to `gpt-4o-2024-11-20` (`config.yaml:1`; the Anthropic `claude-sonnet` alternative is present but commented out, `:2`). On a final failure the sync wrapper **returns an empty string rather than raising** (`:55`) — a fail-open degradation that silently yields a partial tree. Air-gapped use is *possible only* by pointing LiteLLM at a self-hosted OpenAI-compatible endpoint (LiteLLM's multi-provider routing supports this, and community forks demonstrate Ollama/vLLM backends), but that is **not the default and is not vendored** — out of the box, PageIndex phones OpenAI [1][9].

**Finding (2.5).** This is the exact inverse of MemPalace, which defaulted to *local ONNX embeddings* (TAI-RES-2026-004). PageIndex needs a reasoning-grade LLM merely to *construct* the index — so a Civilization adapter would have to vendor the model path and prove network/secret denial under the Base Slice 0 adapter gate (§3.3), and the OSS `PyPDF2==3.0.1` pin is itself a mild staleness signal (PyPDF2 is the archived predecessor of `pypdf`).

### 2.6 Two PageIndexes: Open-Source Library vs. Cloud Product (code + reported)

The single most load-bearing supply-chain nuance is that **there are two different things named "pageindex," and `pip install pageindex` gives you the wrong one for self-hosting.** The GitHub library's own `PageIndexClient` (`pageindex/client.py:28`) is a **self-hosted orchestrator**: its `api_key` parameter sets `OPENAI_API_KEY` (`:36`), and `index()` builds the tree locally via `page_index()`, extracts per-page text so queries don't need the original PDF, and persists a JSON workspace on disk (`:55`). It never calls a PageIndex cloud endpoint — a grep of the repo finds zero references to `api.pageindex.ai` [1]. That library is installed by cloning `main` and running `requirements.txt`; it has **no PyPI distribution** [6].

The **PyPI `pageindex` package** (v0.2.8, 2026-03-15) is a *different codebase*: its client hardcodes `BASE_URL = "https://api.pageindex.ai"` and wraps hosted REST endpoints (`/doc/`, `?type=ocr`, `?type=tree`, `/retrieval/`, `/chat/completions/`) [6]. The README is explicit that the OSS repo "uses standard PDF parsing" and steers complex-PDF users to the paid cloud OCR (`:148`) — i.e. **open-core**: the OSS gives basic local tree-building on your own LLM key; the differentiated OCR/tree/retrieval quality (and the benchmark) live behind the paid API [2][7].

**Finding (2.6).** Any Civilization statement about "adopting PageIndex" must specify *which* PageIndex. Only the MIT OSS library is vendorable and auditable; the cloud API is a networked dependency incompatible with the air-gap default and outside what a code read can verify.

### 2.7 Supply Chain and Maturity

| Dimension | Finding | Confidence |
|---|---|---|
| Popularity | **33,846★ / 2,961 forks**, Trendshift-listed | [Verified] GitHub API, 2026-07-07 [1] |
| Contributors | **13**, heavily concentrated (`rejojer` 199 commits, `zmtomorrow` 67, long tail) | [Verified] |
| History | first commit 2025-04-01; **~300 commits**; latest `f413c66` 2026-07-03 | [Verified] |
| Releases / versioning | **none — zero git tags, zero GitHub Releases, no PyPI dist for the OSS lib** (clone-`main` only) | [Verified] |
| License | **MIT** (© 2025 Vectify AI) — permissive, no copyleft | [Verified] `LICENSE` [3] |
| Recent fixes | latest commit is a crash fix ("prevent KeyError crash and context exhaustion in TOC processing," #188); July-2026 fixes for an install-breaking `litellm`/`dotenv` conflict (#342) and a missing `re` import (#281) | [Verified] |
| Tests | **one** test file (`tests/test_issue_163.py`), a named-issue regression | [Verified] [1] |
| Security CI | **CodeQL runs `languages: actions, build-mode: none`** — it scans only the GitHub Actions YAML, **not the Python source**; Dependency Review `fail-on-severity: moderate` and Dependabot are active; zero published advisories, no CVE | [Verified] [1] |
| Backing | small London startup (~1–10), ~3 yrs old; funding/YC unverified | [Reported] [8] |

**Finding (2.7).** Popularity is real and large; *packaging and assurance maturity are low.* No tags/releases means an adopter has nothing to pin but a commit SHA (`f413c66` is the natural pin); the one-test suite and the reactively-fixed install-breaking bugs indicate no packaging/CI smoke test; and the headline "CodeQL security scanning" **does not cover the library code at all**. For an air-gapped Civilization use these convert into concrete gate items: pin to a reviewed commit, vendor the dependency tree, and add the source static analysis the upstream omits.

### 2.8 Benchmark Reality — the 98.7% Number

The README's "state-of-the-art **98.7% accuracy on FinanceBench**" (`:73`, `:231`) is the project's central proof point. Read carefully, and against its own source repo [4], three qualifications apply — the same shape as the MemPalace "best-benchmarked" caveat in TAI-RES-2026-004:

1. **It is not the library's score.** The 98.7% belongs to **"Mafin 2.5," a reasoning-based RAG *system* "powered by PageIndex"** (`:231`) — an end-to-end pipeline of which PageIndex is one component. The OSS library does not ship the Mafin harness.
2. **It is self-reported.** The evaluation was run by VectifyAI on VectifyAI's own benchmark repository, with **their own human annotators** resolving ambiguous FinanceBench ground-truth answers; the repo's own README concedes FinanceBench "inconsistencies … errors in ground-truth" and a "simple retrieval" focus, and the comparison table is not apples-to-apples (98.7% at 100% coverage vs. "Fintool 98%" at 66.7% coverage) [4]. There is **no independent reproduction and no public leaderboard placement** [9].
3. **Independent readers flagged exactly this.** The Show HN thread's recurring critique: *"a suspicious lack of any performance metrics on the many standard RAG/QA benchmarks … except for their highly fine-tuned and dataset-specific MAFIN2.5 system,"* plus cost/latency concerns (LLM calls per section vs. cheap embedding compare) and "how is this not 'vibe retrieval'" pushback [9].

**Finding (2.8).** The useful Civilization lesson is not the number but the *discipline* (a committed eval harness with per-question artifacts) — and the Civilization's metric must be stricter than "answer accuracy on one vendor benchmark." The governing question is: *did the retrieved `KnowledgeReference` improve the gated decision it influenced?* PageIndex's benchmark is marketing evidence, not portable evidence for any Civilization gate.

---

## 3. Transpara-AI Civilization: The Document-Evidence Baseline (v4.0 accepted + preserved v3.9)

The Civilization already has a named home for a tool like PageIndex, and already has the boundary that governs it. Both predate this evaluation.

### 3.1 The primitives PageIndex maps to

A PageIndex retrieval maps onto three native primitives. The detailed schemas are defined in the **accepted v3.9 baseline** (`DF-V3.9-*`), which v4.0 supersedes as the canonical baseline but explicitly **preserves unchanged as historical evidence** (`DF-V4.0-README:43`) — so v3.9 is a valid, citable source for the detail v4.0 did not restate:

- **`source_refs`** — a FactoryOrder field carried into v4.0 (`DF-V4.0-RUNTIME-004`, doc `04:48`), under the invariant *"Source intent is preserved verbatim by reference or hash"* (`04:55`).
- **`KnowledgeReference`** — a kernel-defined EventGraph node (`DF-V3.9`, doc `02:317`) with twelve governance fields: `source_system, source_ref, source_hash_or_immutable_locator, retrieved_at, used_by_actor, used_in_task, influence_summary, risk_scope, trust_level, freshness_status, redaction_state, contradiction_refs`. The rule (`02:518`): these exist *"because EventGraph must persist them when advisory memory or knowledge materially influences factory work … They do not certify releases, approve protected actions, override EventGraph, or become Tier 0 truth."*
- **`DocumentEvidenceRetrieval`** — the EventGraph node that records a retrieval event, i.e. **the exact record a PageIndex adapter would emit** (`DF-V3.9`, doc `02:331`): `retriever_id, retriever_version, source_document_id, source_document_hash, query_or_need, page_refs, section_refs, retrieved_text_refs, confidence_or_quality_notes, limitations, created_by, created_at, linked_KnowledgeReference`. Its component is named `DocumentEvidenceRetriever` (`02:520`, `06:156`).

Note that this schema already **demands the governance PageIndex does not itself provide**: a `source_document_hash` (PageIndex hashes nothing), explicit `limitations` and `confidence_or_quality_notes`, and a link to a `KnowledgeReference` carrying trust/freshness/redaction/contradiction state. The adapter, not the tool, supplies these.

### 3.2 The truth / certification boundary

- **EventGraph is truth; memory/knowledge are advisory.** `DF-V4.0-GOV-003`, doc `03:36`: *"EventGraph remains the source of truth for evidence, authority, release, and capability state. … Memory and knowledge are advisory only."*
- **Only Release may certify.** `DF-V4.0-RUNTIME-004`, doc `04:110`: *"The Release cell is the only cell that may certify releases, and only through `release.certify` authority and TraceCompletenessGate evidence"* — and `release.certify` requires a **human** Release role in the MVP (`03:396`).
- **Retrieval output is not in the certification evidence set.** `DF-V4.0-EVAL-005`, doc `05:36` enumerates what blocks certification (missing FactoryOrder, runtime version, acceptance/gate evidence, unresolved high/critical failures); retrieved spans are not certification evidence. Knowledge/memory sit at the bottom immutability tier, `supersedable` (`05:296`).
- **Contradiction is a kill criterion.** `05:523`: the factory must stop when *"memory/knowledge contradicts EventGraph in high-risk planning."*
- **The pattern-level rule, stated for this exact component.** `DF-V3.9`, doc `06:158`: *"DocumentEvidenceRetriever … does not create truth, certify releases, approve actions, or replace KnowledgePage. Retrieved evidence becomes usable only when represented as KnowledgeReference/source_refs and linked to EventGraph evidence."* And the investigation's near-verbatim form [11]: *"PageIndex must not become truth or certification evidence by itself."*

### 3.3 The external-frameworks law (Decision 15) and Base Slice 0 gating

The ratified one-line law is **v3.9 "Decision 15"** (`DF-V3.9`, doc `01:172`): *"All external frameworks … remain references, optional adapters, or patterns unless a later accepted ADR changes their status. They must not become kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement."* v4.0 restates it inline per subsystem — runtime (`04:167`) and policy (`03:158`) — rather than as a numbered decision.

**Base Slice 0** is the sequencing gate. `DF-V4.0-RUNTIME-004`, doc `04:135`: Base Slice 0 *"must not use LLM planning, real SaaS generation, external runtimes, production deploy, multi-agent orchestration, memory recall, knowledge reuse, or capability evolution."* And the adapter eligibility rule (`04:165`): *"No external … adapter is eligible until the local deterministic worker passes Base Slice 0. Every external … adapter must prove file boundary enforcement, command boundary enforcement, network denial, secret denial, timeout handling, artifact capture, nonzero-exit handling, EventGraph receipt emission, post-run validation, and replayable evidence."* The investigation sequenced PageIndex identically: *"Only after Base Slice 0: … DocumentEvidenceRetriever using PageIndex"* [11].

This is where PageIndex's §2.5 dependency meets doctrine: an OpenAI-calling indexer is exactly an adapter that must prove **network denial and secret denial** before it is eligible — and Base Slice 0 explicitly forbids "knowledge reuse" and "LLM planning" in the first slice, which is where a PageIndex-style retriever would want to live.

---

## 4. Comparative Analysis

### 4.1 Capability / Fit Matrix

| Requirement of a Civilization `DocumentEvidenceRetriever` | What PageIndex (OSS) provides | Fit |
|---|---|---|
| Locate relevant evidence in long structured documents with page/section traceability | Tree index + `get_page_content(pages)` returning tight ranges; explicit `start_index`/`end_index` per node | **Strong** — this is exactly its design |
| Emit `page_refs` / `section_refs` for `source_refs` | Node `start_index`/`end_index`; agent cites tight page ranges | **Strong** |
| Produce a `source_document_hash` and immutable locator | None — PageIndex hashes nothing; the adapter must add it | **Gap (adapter supplies)** |
| Record `confidence_or_quality_notes`, `limitations` | None emitted; self-check is an internal LLM accuracy heuristic (§2.3) | **Gap (adapter supplies)** |
| Be advisory-only, never truth/cert | No notion of certification; correct *by omission*, must be enforced by the boundary | **Neutral — boundary's job** |
| Deterministic / reproducible structure | LLM-extracted at `temperature=0`; non-deterministic across models/versions | **Weak** |
| Offline / air-gapped construction | Requires an external LLM API (default OpenAI); vectorless but not API-less | **Weak (needs vendoring)** |
| Supply-chain assurance | MIT (good); no tags/releases; CodeQL misses the Python; one test | **Mixed** |
| Portable benchmark evidence | 98.7% is Mafin 2.5, self-reported, not the library | **Not portable** |

### 4.2 Structural Convergence — Where PageIndex Genuinely Fits

The 2026-05-13 investigation carried PageIndex forward for good reasons, and the code confirms the instincts are real:

- **Traceability is the shared value.** PageIndex's "explicit page and section references, no vibe retrieval" (README `:69`) is the same instinct as the Civilization's "evidence must be citeable, not approximate." Its `start_index`/`end_index`/`get_page_content(pages)` map cleanly to `page_refs`/`section_refs`/`source_refs`.
- **Structure-over-chunks is a real advantage** for the long, sectioned documents the Civilization actually reads (doctrine docs, FactoryOrders, filings, standards): natural sections beat artificial chunk windows, and a ToC tree is a better navigation surface for an agent than a vector neighborhood.
- **Vectorless removes one offline dependency.** No embedding model to vendor is genuinely useful for air-gap (§2.5), even though the LLM-reasoning dependency remains.
- **The tool surface is small and legible** (three accessors), which is the right shape for a governed adapter: the "reasoning" stays in the Civilization's own agent, not in an opaque library.

### 4.3 The Seam — the Index Is a Probabilistic LLM Artifact (critique in both directions)

**Critique of PageIndex from the Civilization's ground.** Everything that makes PageIndex convenient also makes it categorically unfit as truth or certification evidence, and the code proves it. The structure is LLM-inferred (§2.2) and self-graded by the same class of model at a 0.6 threshold (§2.3); "traceable and explainable" means traceable *to a page*, not that the structure is *correct* — a mis-extracted node points confidently at the wrong section. It emits none of the `DocumentEvidenceRetrieval` governance fields the schema requires — no `source_document_hash`, no `limitations`, no `confidence_notes`, no freshness/contradiction handling (`DF-V3.9`, doc `02:331`) — so the *adapter*, not the tool, carries the entire governance burden. It **fails open** (`utils.py:55` returns `""` on LLM failure), producing a partial tree silently. It needs an external LLM merely to build the index, colliding with Base Slice 0's "no knowledge reuse / no LLM planning" and the air-gap default (§3.3). Its benchmark is not portable (§2.8), and "which PageIndex" changes the safety surface (§2.6). In doctrine terms: PageIndex is a fine *locate-and-recall* engine and a disqualified *truth/cert* source — the precise boundary the investigation drew, now code-proven [11].

**Critique of the Civilization from PageIndex's ground — taken seriously.** PageIndex ships a working long-document retriever today; the Civilization has a `DocumentEvidenceRetriever` *schema* it did not even carry forward by name into v4.0 (the carry-forward gap, §4.4) and zero implementation. PageIndex's core thesis — *"similarity ≠ relevance; relevance needs reasoning"* — is a legitimate critique of naïve vector-RAG that the Civilization's eventual retriever should heed rather than rediscover. The honest disposition: the Civilization does not need PageIndex's code, but when it builds the pattern it should **mine the approach** (tree over chunks, tight-range reads, page-level citations) instead of rebuilding that wheel — and then wrap the output in the governed records PageIndex has no concept of.

### 4.4 Decision Record, ADR Disposition, and Contribution Determination

**Decision-record determination (stated crisply per the standing rule):**

1. **Does a dark-factory ADR exist for this subject?** **No.** A repo-wide search of `transpara-ai/docs` and the wiki finds no ADR, and no `PageIndex` / `Vectify` / `DocumentEvidenceRetriever` string, in the accepted **v4.0** doc set at all. PageIndex's governance today rests on four things, none of which is an ADR: (i) **accepted v3.9 doctrine** that names it — `06:178` (*"PageIndex is an optional DocumentEvidenceRetriever reference only. It is not required unless a later accepted decision adopts it."*) and the `09` legacy-coverage-matrix decision row (`09:252`) — atop the defined `DocumentEvidenceRetrieval` node schema (`02:331`); (ii) the ratified **Decision 15** external-frameworks law (`01:172`); (iii) the **reviewed-planning** investigation checkpoints [11]; and (iv) the **compiled wiki page** [12]. The v3.9.1 technology-decision crosswalk still has **no PageIndex row** — the wiki page's standing fail-legible point.
2. **Should one be created?** **No ADR now.** Nothing here is adopted as a dependency, runtime, or control-plane component, so there is no architecture decision to record — the same disposition TAI-RES-2026-005 (Solo Orchestrator) and TAI-RES-2026-006 (Owain Lewis) reached. The precedent mold *if* one were ever written is ADR-0008 (MemPalace verbatim-recall) / ADR-0006 (Karpathy-Wiki knowledge substrate) / ADR-0011 (memory/knowledge/state separation) — all `Proposed`. The durable record should be: **this evaluation**, plus a per-item crosswalk/decision row added through the normal docs process, plus — *if* a native `DocumentEvidenceRetriever` is ever pursued — its own issue → Factory Order → TLC arc, where design-stage **CFADA** is the decision record for the adopted *pattern* (never for VectifyAI's code). Two doctrine-hygiene items belong in that record: **(a)** the v4.0 **carry-forward gap** — `DocumentEvidenceRetriever`/`DocumentEvidenceRetrieval`/`KnowledgePage` are defined only in preserved v3.9 and were not restated in v4.0's standalone docs, so a v4.0-level home for a PageIndex adapter does not yet exist by name; **(b)** the **missing crosswalk row**.
3. **Does it contribute to the Civilization, and how?** **Pattern-only; reject as runtime/authority/truth/certification/kernel.** PageIndex contributes: (a) the **tree-structured document-evidence + page/section-traceability pattern** → informs a native `DocumentEvidenceRetriever` that emits `DocumentEvidenceRetrieval` → `KnowledgeReference`/`source_refs` records (advisory evidence, never truth/cert); (b) the **"reasoning-over-structure beats similarity-over-chunks for long structured documents"** design insight; (c) an **air-gap insight** — a vectorless design removes the embedding-model offline dependency (though not the LLM-reasoning one); and (d) the **negative lesson, now code-proven** — an LLM-built, LLM-graded index is categorically not truth, which strengthens the existing boundary. Net contribution: **high as confirmation** (it code-proves the "retrieval mistaken for truth" risk the investigation named #1, and the adapter classification), **moderate as a source** (the retriever pattern and traceability discipline are immediately mineable, post-Base-Slice-0). Under Decision 15, none of PageIndex's components may hold truth, certification, policy, release, capability-promotion, kernel, or controller roles — and no learning below proposes otherwise.

---

## 5. Strategic Learning Opportunities

All pattern-only; none adopts PageIndex code as runtime, gate authority, or truth store.

### 5.1 A native `DocumentEvidenceRetriever` that emits governed records (highest value)
The schema already exists (`DF-V3.9`, doc `02:331`). PageIndex is the worked reference for the *retrieval half*: build a structural tree, then read tight page ranges rather than whole documents. The learning is to wrap that pattern so every retrieval writes a `DocumentEvidenceRetrieval` node — with `source_document_hash`, `page_refs`, `section_refs`, `confidence_or_quality_notes`, `limitations` — linked to a `KnowledgeReference`. The tool locates; the adapter governs.

### 5.2 "Reasoning-over-structure" as the retrieval contract, not vectors
For long structured Civilization documents, adopt the *contract* — return page/section references an auditor can open, not opaque vectors — even if the implementation differs. This is a doctrine-prose learning about what a retriever's output type must be, independent of PageIndex.

### 5.3 Treat self-verification-by-self-agreement as an anti-pattern to avoid
PageIndex's `verify_toc` (LLM grading LLM at a 0.6 threshold, §2.3) is a *self-consistency* check, not validation. The Civilization's equivalent must be **ground-truth-anchored**: does the cited span actually contain the claimed evidence, checked against the immutable source hash — not "does the same model agree it looks right." A useful worked example of what *not* to copy.

### 5.4 Air-gap discipline for LLM-dependent adapters
PageIndex proves that "vectorless" removes embeddings but not the LLM call. Any Civilization retriever must vendor its model path (LiteLLM → a local endpoint) and prove network/secret denial under the Base Slice 0 adapter gate (`04:165`). Bank this as the concrete offline checklist for the retriever slice.

### 5.5 "Which artifact" provenance hygiene
The OSS-vs-cloud-SDK split and the total absence of tags/releases (§2.6–2.7) are a supply-chain lesson: pin any external adapter to a reviewed commit (`f413c66`), never `pip install pageindex` (that is the cloud SDK), and add the source static analysis the upstream CodeQL config skips.

---

## 6. The Inverse: What PageIndex Cannot Take From the Civilization by Adoption Alone

PageIndex is a retrieval engine; it has no concept of a record a kernel refuses to certify around. It cannot, by importing anything, acquire EventGraph truth, fail-closed certification, typed authority, the `KnowledgeReference` governance envelope (trust/freshness/redaction/contradiction), air-gap vendoring, or the cross-family review floor. Bringing the Civilization's discipline *into* PageIndex would mean wrapping its output in exactly the `DocumentEvidenceRetrieval`/`KnowledgeReference` envelope — which is the Civilization's job to build around the tool, not VectifyAI's to build into it. This asymmetry is the whole reason the disposition is "pattern-only adapter behind a boundary," not "dependency."

---

## 7. Conclusions

**PageIndex retrieves what a document says; the Civilization governs what a retrieval is allowed to change.** The code-anchored read confirms and hardens the 2026-05-13 disposition rather than overturning it: PageIndex is an **optional advisory document-evidence adapter/pattern**, overlapping `KnowledgeReference`/`source_refs`, carrying the risk *"retrieval mistaken for truth"* (now code-proven — the index is an LLM artifact self-graded by an LLM), recommended as an *optional `DocumentEvidenceRetriever`; not memory/wiki/truth*, ranked #4 among optional adapters, **gated behind Base Slice 0**, and explicitly rejected as truth or certification evidence [11].

This evaluation's three upgrades over the prior page: **(1)** it is **code-anchored** (`f413c66`), superseding the indexed-only study for the "what it is" facts, and it adds the runtime-dependency, OSS-vs-cloud, supply-chain, and benchmark-provenance findings; **(2)** it **corrects the record** — PageIndex *is* named in accepted v3.9 doctrine (`06`, `09`) with a defined node schema, not merely in investigation checkpoints; **(3)** it surfaces **two documented doctrine gaps** — v4.0's un-restated `DocumentEvidenceRetriever` pattern, and the still-missing crosswalk row. The disposition remains: credible document-evidence adapter candidate; pattern-only contribution; no ADR; no authority; no runtime activation; Base Slice 0 first.

---

## 8. Recommended Next Steps

1. **Add a per-item crosswalk/decision row** for "PageIndex (VectifyAI): optional `DocumentEvidenceRetriever` reference; pattern-only; no ADR; no control roles," through the normal docs process — closing the decision-record gap this eval would otherwise leave (per §4.4).
2. **File a doctrine-hygiene issue** to restate `DocumentEvidenceRetriever`/`DocumentEvidenceRetrieval` in v4.0 (the carry-forward gap), or to record it as intentionally deferred — so a future adapter has a v4.0-level home by name.
3. **If/when a native `DocumentEvidenceRetriever` is pursued:** open its own issue → Factory Order → TLC arc; run design-stage CFADA as the pattern's decision record; gate it behind Base Slice 0; require it to emit governed `DocumentEvidenceRetrieval` → `KnowledgeReference` records; pin any PageIndex reference to `f413c66`; and vendor the LLM path with proven network/secret denial (per §5.1, §5.4).
4. **Keep the upstream as context only** — never re-publish, never a push/PR/merge target (organizational rule).
5. **Publish this evaluation** as the wiki entity page's primary source and move the page to code-anchored status (done in the same change as this document).

---

## 9. References

**Primary (code — read from the local clone at `f413c66`, cited inline as `pageindex/<file>:<line>`):**
- [1] `VectifyAI/PageIndex` @ `f413c66fee0bfbb7291c389333f9cc1adac68d57` (2026-07-03) — the OSS library, read in full: `page_index.py`, `utils.py`, `page_index_md.py`, `client.py`, `retrieve.py`, `config.yaml`, `__init__.py`, `run_pageindex.py`, `examples/agentic_vectorless_rag_demo.py`, `tests/test_issue_163.py`, `requirements.txt`. GitHub metadata (stars/forks/commits/tags/CI) read via API 2026-07-07. — https://github.com/VectifyAI/PageIndex/tree/f413c66 · **context only; never a push/PR target.**

**Upstream context (claims — verified against code where they overlap):**
- [2] PageIndex `README.md` @ `f413c66` — upstream self-description ("Vectorless, Reasoning-based RAG"; "tree search inspired by AlphaGo"; self-host vs. cloud; ecosystem). [Marketing/Verified-hybrid]
- [3] `LICENSE` — MIT, © 2025 Vectify AI. [Verified]
- [4] Mafin 2.5 / FinanceBench benchmark repo — https://github.com/VectifyAI/Mafin2.5-FinanceBench ; blog https://pageindex.ai/blog/Mafin2.5 (dated 2025-02-19). Self-reported 98.7%. [Marketing]
- [5] FinanceBench dataset paper — https://arxiv.org/abs/2311.11944. [Reported]
- [6] PyPI `pageindex` v0.2.8 (2026-03-15) — the **cloud SDK**, `BASE_URL=https://api.pageindex.ai`; not the OSS library. — https://pypi.org/project/pageindex/. [Verified]
- [7] PageIndex cloud/docs — pageindex.ai/developer, docs.pageindex.ai/pricing ($30/$50/$100 tiers), chat.pageindex.ai, VectifyAI/pageindex-mcp. [Reported]
- [8] Company — "VECTIFY AI LIMITED," UK Companies House #14827188 (London, founded 2023); founders Mingtian Zhang (https://mingtian.ai/) and Yu Tang. [Reported]
- [9] Independent reception — Show HN (2025-09), https://news.ycombinator.com/item?id=45036944 (benchmark-cherry-picking, cost/latency, "vibe retrieval" critiques). [Reported]

**Prior Transpara artifacts (first-party):**
- [10] `raw/transpara/dark-factory/research/pageindex-role-in-transpara-stack.md` (2026-05-13) — the indexed-only study ("augmentation, not a replacement"); superseded for "what it is" facts by [1].
- [11] Investigation checkpoints — `raw/transpara/dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md` (inclusion class `Optional adapter / pattern`; overlap `KnowledgeReference/source_refs`; risk "retrieval mistaken for truth"; rec "Optional DocumentEvidenceRetriever; not memory/wiki/truth"; explicit rejection) and `…-10-civilization-landscape-investigation-closeout.md` (priority #4; `U4 DocumentEvidenceRetriever`; "proposed only"; post-Base-Slice-0 gating).
- [12] Compiled wiki entity page — `wiki/pageindex.md` (2026-06-13) — the page this evaluation upgrades.

**Civilization doctrine (cited inline by doc number and line):**
- [13] `DF-V4.0-README` v4.0.54 (accepted) — supersession + preservation of v3.9 (`:43`).
- [14] `DF-V3.9`, doc `01` — Decision 15, External Frameworks Stay Outside Control Roles (`01:172`).
- [15] `DF-V3.9`, doc `02` — kernel schema: `KnowledgeReference` (`02:317`, rule `02:518`) and `DocumentEvidenceRetrieval` (`02:331`, `02:520`).
- [16] `DF-V3.9`, doc `06` — memory/knowledge capability: `DocumentEvidenceRetriever` pattern (`06:156`, `06:158`) and the PageIndex line (`06:178`); doc `09` legacy-coverage-matrix PageIndex row (`09:252`).
- [17] `DF-V4.0-GOV-003` (doc `03`) — "EventGraph … source of truth; memory and knowledge are advisory only" (`03:36`); policy-adapter restatement (`03:158`); `knowledge.activate` protected (`03:104`), KnowledgeCurator (`03:331`); human `release.certify` (`03:396`).
- [18] `DF-V4.0-RUNTIME-004` (doc `04`) — `source_refs` (`04:48`, invariant `04:55`); Release-only certification (`04:110`); external-framework restatement (`04:167`); Base Slice 0 (`04:135`) and the external-adapter eligibility gate (`04:165`).
- [19] `DF-V4.0-EVAL-005` (doc `05`) — certification-blocking evidence set (`05:36`); immutability tiers (`05:296`); memory/knowledge-vs-EventGraph kill criterion (`05:523`). ADR precedent: `archive/v3/adrs/ADR-0008` (MemPalace), `ADR-0011` (memory/knowledge/state separation); `archive/v2/adrs/ADR-0006` (Karpathy Wiki).

**Cross-links:** [[pageindex]] (the entity page this evaluation upgrades), [[mempalace]] (the sibling code-anchored eval, TAI-RES-2026-004), [[civilization-landscape-investigation]], [[memory-knowledge-advisory]], [[base-slice-0]], [[event-graph]], [[dark-factory]].

**Conflicts and thin spots stated, not resolved.** The `DocumentEvidenceRetriever` pattern is accepted doctrine in **preserved v3.9** but not restated in **accepted v4.0** — a documented carry-forward gap, not a contradiction. PageIndex is named in accepted v3.9 doctrine yet has **no row** in the v3.9.1 technology-decision crosswalk (`status: review`) — a documented omission whose cause is not stated by any source. The 98.7% benchmark is real but **self-reported and not the library's** number. The "fork date 2026-05-13" from the original seed remains uncorroborated by any repo or capture; what is dated is the *study*, and now this code read at `f413c66`. The correct status is therefore: **credible document-evidence adapter candidate; pattern-only; no ADR; no authority; no runtime activation; Base Slice 0 first.**

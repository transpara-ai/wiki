# Karpathy LLM Wiki pattern audit

Reviewed September 18, 2026 against the merged v0.8.2 implementation and the
v0.8.3 release/UI changes. **Result: partial alignment, not complete adherence.**
The reference is Karpathy's own [LLM Wiki idea file](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f),
not a formal conformance standard or an external certification.

The central idea is persistent, interlinked Markdown synthesized from sources.
His workflows include ingestion, model-assisted questions, and semantic maintenance.
Embeddings are optional; they do not replace answer generation.

Human-supervised LLM authoring is consistent with this pattern; unattended
automation is not a requirement. The ingestion finding below concerns the
ordinary browser workflow and the absence of evidence that a complete manual
synthesis/maintenance pass follows every ingest.

## Findings and evidence

| Area | Observed implementation | Assessment |
| --- | --- | --- |
| Persistent knowledge | Canonical `wiki/*.md` articles, source citations, placements, related links and rendered static pages exist. `compile/article_catalog.py` provides the shared catalog. | Aligned foundation. |
| Raw evidence | Browser source operations retain evidence and replacement provenance in `compile/ingest_ops.py`. However, `compile/refresh.py:mirror_sources` synchronizes the dark-factory source mirror with `rsync --delete`, which can overwrite or remove mirrored files. | Raw immutability is not universal. Git history only preserves material actually committed. |
| Ingestion synthesis | `compile/ingest_server.py:create_article_from_source` explicitly writes an awaiting-synthesis skeleton. Registration stores evidence, updates metadata and rebuilds. DevOps can accept supplied prose. `compile/REBUILD.md` reserves substantive rewriting for manual Tier 2 work. | The normal browser ingest path does not read each new source with an LLM and update affected existing articles, comparisons and contradictions. Major gap. |
| Existing synthesis hook | `compile/ingest_ops.py:run_engine` supports an authority-gated single-article body replacement; an empty command disables it. Its presence does not establish a continuously maintained, multi-article knowledge compilation workflow. | Partial capability. No claim that this hook is enabled on Velia; live configuration was not inspected in this audit. |
| Navigation and selection | Space portals, generated navigation/search indexes and the Ask catalog offer discovery. `index.md` is a space portal, not a hand-maintained full-article summary catalog. | Functional catalog equivalents exist; a literal filename match is not necessary. |
| Questions | `compile/ask.py` and `compile/llm_service.py` select from the published, space-filtered catalog and answer from complete selected article texts. They validate citations and bound context. They do not retrieve raw-document embedding chunks. | Aligned model-assisted query path over the compiled wiki. Answers are transient and cannot yet be promoted into reviewed articles. |
| Maintenance | Structural/catalog/link checks and source hashing exist. The examined runtime has no integrated semantic LLM lint loop for contradictions, missing synthesis or stale claims. | Structural checks are useful, but semantic maintenance remains a gap. |
| Operational history | Source manifests, provenance, Git history and operation-ledger shards record source activity. Ask deliberately persists no answers. There is no unified chronological ingest/query/semantic-lint log. | Partial history, not a complete knowledge-maintenance record. |
| Authoring instructions | `DESIGN.md`, `compile/REBUILD.md`, `API.md` and the knowledge registry describe schema and operations. `AGENTS.md` directs software work to TLC. | Instructions exist but are dispersed; there is no single end-to-end agent runbook covering ingestion, query promotion and semantic lint. |

The browser's **0 stale** indicator is a deterministic rebuild result. A successful
refresh empties `stale_articles` and records `changed_articles`; it does not
certify that article prose was re-synthesized or all claims remain current.
The mirror change detector also compares current files to the previous snapshot;
deleted source paths are not included in its `changed` set. These are limits of
the present freshness signal, not evidence of semantic completeness.

## Reading, Search and Ask

| Operation in this implementation | Needs a running model? | Offline position |
| --- | --- | --- |
| Read existing Markdown | No | A local copy is readable without the hosted service. |
| Browse the generated site and Search | No | A complete local build can be served by a local HTTP server. Search uses the generated article index and lexical ranking; it has no vector embeddings. This audit does not certify a packaged offline distribution. |
| Ask a new question | Yes | Both current provider adapters use online host subscriptions. No local offline inference provider is configured. |
| Register sources and rebuild HTML | No | These steps alone do not synthesize new knowledge. |
| Synthesize or revise articles with an LLM | Yes during that work | Once written, the resulting articles remain readable without the model. |

For example, Search can locate a competitor article already written. Ask must
interpret which market, product and evidence the reader means, compare relevant
articles, and compose a supported answer. A precomputed search index can help
locate material; it is not a prewritten answer to every possible question.

The hosted `wiki.transpara.io` service also depends on network access and SSO.
No service worker/offline cache was found in the builder or browser assets.
Reading a local Markdown/build copy and opening the hosted site offline are
different capabilities.

## Work needed before claiming full operational alignment

1. Connect the existing host provider to a reviewed ingestion workflow: read new
   evidence, propose changes to all affected articles, cross-link, flag conflicts,
   validate and retain a durable record. Preserve source/publication boundaries.
2. Preserve immutable source snapshots, including mirrored replacements and
   deletions; distinguish build freshness from pending semantic review.
3. Add a deliberate semantic lint/review workflow and a concise agent runbook.
An optional extension is reviewed promotion of useful Ask answers into
persistent articles. Its absence alone is not a failure to follow the pattern.
Maintenance activity should still have a durable record.

These are follow-up implementation requirements, not features delivered by
v0.8.3. This audit verifies code paths and documented behavior; it does not
revalidate every factual assertion in the corpus or certify the current host's
health. Deployment checks and article evidence review remain separate.

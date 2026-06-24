# Transpara-AI Civilization Wiki

A [Karpathy-style LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — a self-maintaining, interlinked knowledge **substrate** for the Transpara-AI Civilization arc, compiled from the source corpus (Matt Searles' lovyou.ai posts + first-party Dark Factory docs + Open Brain + the Stage 0 institutional-substrate source snapshot).

**Start here: [`index.md`](index.md)** — the front-page narrative frame for the Searles-to-Civilization arc, followed by the chronology and article index.

## Layout

- `index.md` — the encyclopedia-style front page, historical narrative frame, chronology, and article index (read this first)
- `wiki/` — interlinked entity articles (foundational philosophy · architecture · dark-factory arc · investigations)
- `raw/` — source material: `searles/` (the posts), `open-brain/` (exported thoughts), `civilization/` (Stage 0 institutional-substrate proposal snapshot), and `inbox/` (browser-ingested source drops). Generated first-party Dark Factory mirrors are recorded in `PROVENANCE.md`.
- `civilization-arc.html` — the single normalized wiki page for the progress chart; not the home page and not authority.
- `DESIGN.md` — substrate design, compile pipeline, keep-current plan
- `PROVENANCE.md` — source manifest

## Principles

- **Ingest broadly, synthesize at compile** — curation happens in `wiki/`, not at the door.
- **Fail-legible** — articles state source conflicts and mark asserted-vs-proven claims; gaps are `TBD`, never invented.
- **Compounding** — pre-compiled, cross-linked entity pages re-derived from sources (not RAG-per-query).

## Status

Run 10 service hardening: **101 articles**, served source pages, a browser
authoring surface, and generated Transpara-AI repository pages. The wiki exposes `repos.html`,
`sources.html`, and `ingest.html`; raw/source references open served
source-viewer pages, and `compile/ingest_server.py` can batch-ingest documents
into `raw/inbox/`, append selected article source references, update
`raw_documents`, create a provisional investigation article when no target
article is selected, and rebuild the generated site. Static full-site search
includes source documents and repository README pages as first-class results.
Stage 0 material remains advisory proposal source, not accepted doctrine.
The browser **Refresh status and rebuild** action uses the same deterministic
`compile/refresh.py` path as the systemd timer, so the header freshness banner
is recomputed with the rendered site.

Read-only serving can still use
`python3 -m http.server --bind 127.0.0.1 --directory dist` for local throwaway
previews. On nucbuntu, the first-class authoring route is the
Transpara-AI Civilization Wiki service on loopback `:8787`, managed by
linger-enabled user systemd. It is intentionally not the LAN write surface:

```bash
systemctl --user status transpara-ai-civilization-wiki.service
systemctl --user status transpara-ai-civilization-wiki-refresh.timer
# equivalent foreground command:
python3 compile/ingest_server.py 127.0.0.1 8787
```

The service auto-starts on reboot. The refresh timer runs the deterministic
`compile/refresh.py` path every 15 minutes to rebuild and update the freshness
banner; it does not perform LLM article synthesis. If a LAN-visible read route
is needed, expose a separate read-only static/proxy service rather than exposing
the authoring endpoints. Do not proxy `source/*.html` or `search-index.js`
outside the host-local trust boundary unless the confidential raw-source corpus
has been deliberately approved for that audience.

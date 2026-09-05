# Transpara Knowledge Hub

A compiled, interlinked knowledge system with one canonical article graph and several purposeful views. The current spaces are **Civilization**, **Transpara Platform**, and **Competition**.

Start at [`index.md`](index.md), the neutral portal. Space-specific source homes live under `spaces/`; canonical articles remain in `wiki/` and retain flat HTML routes such as `/event-graph.html`.

## Architecture

- `compile/knowledge_structure.json` — governed registry for spaces, sections, stewards, classifications, source authorities, and publication profiles.
- `index.md` — neutral Knowledge Hub portal source.
- `spaces/civilization/index.md` — Civilization home and existing board.
- `spaces/platform/index.md` — Transpara Platform home.
- `spaces/competition/index.md` — Competition home.
- `wiki/` — canonical articles. One article can have several explicit placements without duplicating its body.
- `raw/` — source material and browser-ingested evidence. Historical material is not physically moved merely to match the presentation taxonomy.
- `compile/` — catalog, builder, validation, lifecycle, refresh, and local authoring services.
- `DESIGN.md` and `PROVENANCE.md` — pipeline design and source manifest.

The Knowledge Hub is advisory. Running code, versioned configuration, accepted decisions, release systems, customer systems, and EventGraph retain their respective authority.

## Content rules

- Ingest broadly and synthesize curatively; source registration is not automatic publication.
- Make source conflicts and implemented/normative/planned/positioning boundaries legible.
- Keep one canonical slug and steward per article, one primary placement, and explicit additional placements.
- Never ingest customer production content, credentials, or unauthorized prospect evidence.
- Keep competitive claims time-bounded and label Transpara-authored interpretation as first-party positioning.

The migration retains all 108 original article routes and the intentional unresolved-reference baseline. The initial curated Platform and Competition set is classified `company-internal`; the original Civilization corpus remains `internal` unless separately reviewed.

## Build and verify

One-time per clone, enable the fail-closed pre-commit secret scan:

```bash
git config core.hooksPath .githooks
```

Build the complete host-local authoring view:

```bash
npm run build
npm run verify
```

Build isolated publication profiles:

```bash
python3 compile/build_site.py --profile authoring-local --output dist-next
python3 compile/build_site.py --profile company-internal --output dist-company
```

`public-platform` is intentionally disabled and fails before it creates output. Enabling or serving it is a separate publication-authority decision.

`npm run test:shadow` builds `dist-next`, proves it byte-equivalent to the current `dist` authoring artifact, checks the preserved route and link inventories, and runs browser tests through a separate loopback-only endpoint on `127.0.0.1:8800`.

## Local service

The authoring service remains bound to loopback at `127.0.0.1:8787`:

```bash
systemctl --user status transpara-knowledge-hub.service
systemctl --user status transpara-knowledge-hub-refresh.timer
# equivalent foreground command
python3 compile/ingest_server.py 127.0.0.1 8787
```

Generic `transpara-knowledge-hub*` systemd templates are canonical. The former `transpara-ai-civilization-wiki*` templates remain for one compatibility window; the two service families conflict and must not be run together. Migration and rollback instructions are in [`compile/REBUILD.md`](compile/REBUILD.md).

New environment names use `KNOWLEDGE_HUB_*`; `CIVWIKI_*` authoring, allowed-host, Python, and Dark Factory source names remain fallback aliases during the compatibility window.

Static throwaway previews must also stay loopback-only unless a separate authority approves a broader audience:

```bash
python3 -m http.server 8798 --bind 127.0.0.1 --directory dist
```

Do not expose the authoring endpoints as a public or LAN read route. A broader read-only publication must use an appropriate restricted profile and must not include raw sources, mutation controls, repository mirrors, or full-text indexes outside their authorized boundary.

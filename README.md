# Transpara Knowledge Hub

A compiled, interlinked knowledge system with one canonical article graph and several purposeful views. The current spaces are **Civilization**, **Transpara Platform**, **Competition**, and **DevOps**.

Start at [`index.md`](index.md), the neutral portal. Space-specific source homes live under `spaces/`; canonical articles remain in `wiki/` and retain flat HTML routes such as `/event-graph.html`.

## Architecture

- `compile/knowledge_structure.json` — governed registry for spaces, sections, stewards, classifications, source authorities, and publication profiles.
- `index.md` — neutral Knowledge Hub portal source.
- `spaces/civilization/index.md` — Civilization home and existing board.
- `spaces/platform/index.md` — Transpara Platform home.
- `spaces/competition/index.md` — Competition home.
- `spaces/devops/index.md` — DevOps home; see [API.md](API.md) for corpus ingestion.
- `wiki/` — canonical articles. One article can have several explicit placements without duplicating its body.
- `raw/` — source material and browser-ingested evidence. Historical material is not physically moved merely to match the presentation taxonomy.
- `compile/` — catalog, builder, validation, lifecycle, refresh, and local authoring services.
- `compile/repository_routes.json` — published repository route identities, retained when local checkouts disappear.
- `DESIGN.md` and `PROVENANCE.md` — pipeline design and source manifest.

The Knowledge Hub is advisory. Running code, versioned configuration, accepted decisions, release systems, customer systems, and EventGraph retain their respective authority.

Repository pages discover both ordinary clones and Git worktrees under the
local repository directory, including worktrees reached through symlinks.
The versioned repository route catalog preserves published URLs independently
of that host's checkout inventory. Its initial entries were recovered from the
existing authoring builds and cover every repository route in the migration
baseline. A registered route whose checkout is unavailable shows a source
repository link and an explicit availability notice; it does not show cached
README text or pretend to have current Git metadata. The local page resumes
when the checkout returns. Add a catalog entry with the verified name, origin,
and section when a newly discovered route should also be retained. Builds read
the catalog without editing it. Repository pages remain limited to publication
profiles that include repositories.

## Content rules

- Ingest broadly and synthesize curatively; source registration is not automatic publication.
- Make source conflicts and implemented/normative/planned/positioning boundaries legible.
- Keep one canonical slug and steward per article, one primary placement, and explicit additional placements.
- Never ingest customer production content, credentials, or unauthorized prospect evidence.
- Keep competitive claims time-bounded and label Transpara-authored interpretation as first-party positioning.

The migration retains all 108 original article routes and the intentional unresolved-reference baseline. The initial curated Platform and Competition set is classified `company-internal`; the original Civilization corpus remains `internal` unless separately reviewed.

## Build and verify

The wiki's SemVer version is maintained in `package.json` (and synchronized in
`package-lock.json`). Every build exposes it at `/version.json` and `/VERSION`,
shows it beneath the site name in the top banner, and links to it from each page
footer. These files are generated from the package
version, so release metadata has one source of truth. Bump it with
`npm version patch --no-git-tag-version` (or `minor` / `major` as appropriate),
then rebuild.

The local authoring server sends `Cache-Control: no-cache` for pages and release
metadata so browsers revalidate them after a rebuild. API responses use
`no-store`. After updating the server code, restart the local service and reload
the page to replace any response cached before this policy was installed.

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

For the main host on the private Tailscale network, use the repository's
[`compose.yaml`](compose.yaml) and follow [Docker hosting](DOCKER.md). Compose
runs the authoring server and scheduled refresh, persists the working checkout,
and publishes only to host localhost for Tailscale Serve. Verify the container
deployment in an isolated checkout with `npm run test:docker`.

The native service commands below describe the existing NUC installation. Do not
run its writer or timer against the same checkout as the Docker deployment.

Selecting a space sets the context for **Repos**, **Sources**, and **Ingest**,
including their header, sidebar, and search scope. Context travels in tool links
and is remembered within the browser tab, so it survives tool navigation and
reloads. Selecting a named space in the search dropdown also changes context;
**All spaces** broadens search while retaining the current tool context.
Repos lists the space steward's repositories; Sources lists cited web references
and local documents associated with the space, including shared sources. Article
source lists stay cumulative when evidence is added and are expanded by default;
the infobox's source count links to the complete list.

Click **Ingest** to prefill the current space and steward; article pages also
carry their section. Changing the ingestion space updates the shared context
without clearing pasted text. Select a target article, then upload
documents, add URLs, or use **Paste email or other text** with an optional source
title. Pasted text is saved as a `.txt` source with its line breaks preserved and
can be combined with files and URLs in the same ingestion. Include any email
sender, date, and subject you need to retain in the pasted block.

Adding sources rebuilds their links; incorporating their contents into article
text is a separate authoring step. Newly attached evidence marks the target
article's synthesis as pending in every space. After reviewing and incorporating
it, update the article's compilation date and clear `stale_since`. Re-uploading
an already attached document does not mark a completed update pending again.

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

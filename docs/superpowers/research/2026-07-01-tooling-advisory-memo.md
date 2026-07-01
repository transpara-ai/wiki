# Tooling Advisory — Plugins, Skills, Hooks & MCP for the Wiki (Item 3)

**Status:** advisory (not a build spec) · **Date:** 2026-07-01 · **Owner:** Michael Saucier · **Repo/branch:** transpara-ai/wiki @ `feat/tooling-advisory-memo`

> Advisory memo from the 2026-07-01 wiki-improvement brainstorm. Recommends tooling to **incorporate**, each tied to a committed design spec or a doctrine gap. Not a spec — nothing here is authorized to build; it's the map for when you are.

---

## 0. Grounding (what the wiki has today)

- **No project-local Claude tooling.** The wiki's `.claude/` holds only `worktrees/` — no committed skills, hooks, or `.mcp.json`. Every workflow (compile, ingest, recompile) is ad-hoc.
- **CI has no secret-scan.** `.github/workflows/ci.yml` exists; nothing scans for secrets — yet the secret-scrub is *non-negotiable* (CLAUDE.md + `DESIGN.md` §Ingestion). This is a live hole.
- **In-org ecosystem to draw from:** `transpara-ai/claude-toolbox` (agents/hooks/skills/scripts) and `transpara-ai/claude-plugin` (mcp-servers/practices/skills/templates). "Incorporate" can mean *wire these in*, not build from zero.
- **Air-gap line:** authoring runs on nucbuntu (networked — `inflight.py` already uses `gh`); the **served static site must stay fully offline.** Authoring-side tools may use the network; anything that ships to a deployment target must have an offline path.

---

## 1. Skills — into `.claude/skills/`

| Skill | What it does | Ties to | Priority |
|---|---|---|---|
| **`recompile-article`** | Single-article, authority-gated Claude synthesis (re-derive one article's prose + `[[links]]`, fail-legible). The engine Item 1's Replace/Remove reconciliation needs; what `REBUILD.md` does by hand today. | Item 1 | **P0** |
| **`arc-validate`** | Runs the tightened ontology checks: referential integrity, single status vocabulary, gates-have-criteria, no parallel-status fields. | Item 2b | **P0** |
| **`provenance-audit`** | Sweeps articles for unsourced claims, missing asserted-vs-proven labels, fabricated/contested numbers (the "14 invariants" bar). | 2a + doctrine | P1 |
| **`corpus-compile`** | Formalizes the multi-agent full/incremental compile (the anti-RAG rebuild) into a repeatable procedure. | workflow | P1 |

## 2. Hooks — `.claude/settings.json` + CI (enforcement, the right tool for "always")

| Hook | What it does | Priority |
|---|---|---|
| **Pre-commit secret-scan** (`gitleaks`, offline) | Closes the biggest gap; the scrub is mandatory and currently absent. No network → air-gap-safe. Wire to pre-commit **and** CI, with a test that a planted secret is caught. | **P0** |
| **Fail-legible lint** (pre-commit) | Blocks committing an article with unsourced claims or a bare contested number on the front page. Makes the doctrine mechanical. | P1 |
| **Build-verify** (pre-push) | Runs `npm run verify` + `compile/check_links.py` so a broken build / red link never lands. | P1 |

## 3. MCP servers — a new wiki `.mcp.json`

| Server | What it gives | Air-gap |
|---|---|---|
| **GitHub MCP** | The evidence source for Item 2b's *derived* status (PR/merge/gate state) — complements/replaces `inflight.py`'s `gh` polling. | authoring-side only ✓ |
| **Open Brain MCP** | The corpus *includes* the Open Brain export; pull deltas to drive incremental recompile (the DESIGN.md nightly re-sync). | authoring-side ✓ |
| **Local corpus-index MCP** (offline embeddings) | Aids the *compile* step with entity dedup + `[[related]]` linking. **Scoped to authoring, not reading** — the wiki's anti-RAG bet governs reads; this must never become per-query RAG for the served site. | must be local ✓ |

## 4. Plugin — the bundle

- **A `wiki` Claude Code plugin** packaging the §1 skills + §2 hooks + the `recompile-article` subagent, so the whole workflow installs once. Model it on `transpara-ai/claude-plugin`'s structure. This is how the ad-hoc becomes reproducible for anyone touching the wiki.

---

## 5. Prioritization — the first three to wire

1. **Offline secret-scan pre-commit hook** (P0) — closes a doctrine hole; ~20 min; air-gap-trivial. *Highest leverage item in this memo.*
2. **`recompile-article` skill** (P0) — unblocks Item 1's Replace/Remove.
3. **GitHub MCP as the Item-2b evidence source** (P0) — makes derived status real.

Everything else is enhancement. Note the pattern: `recompile-article` *is* Item 1's engine and `arc-validate` *is* Item 2b's integrity gate — **good tooling is the specs made executable, not bolted on.**

---

## 6. What this memo does NOT do
- Authorize any build (advisory only).
- Recommend any cloud dependency on the served-site path (air-gap).
- Replace the anti-RAG reading model with retrieval (any index is authoring-time only).

## 7. Open questions
1. Secret-scanner choice — `gitleaks` (recommended, single Go binary, offline) vs `trufflehog`?
2. Do the skills/hooks live in the wiki repo, or graduate into `claude-toolbox`/`claude-plugin` for reuse across repos? (Recommend: prototype in-repo, graduate once stable.)
3. Local corpus-index MCP — worth the complexity now, or defer until the compile step actually strains on entity-linking at scale?

---
entity: bitsandpieces
aliases:
  - bitsandpieces
  - the Atoms
  - Atoms
  - transpara-ai/bitsandpieces
  - atomic building blocks
tier: investigation
status: compiled
last_compiled: 2026-06-13
sources:
  - /Transpara/transpara-ai/repos/bitsandpieces/README.md  # catalog of 4 building blocks, all from gstack; "Atomic / Attributed / Adapted" philosophy
  - /Transpara/transpara-ai/repos/bitsandpieces/safety-hooks/README.md  # one entry, README-grounded: gstack (MIT) careful/freeze/guard PreToolUse hooks, fail-closed deny on freeze boundary
  - "GitHub API: repos/transpara-ai/bitsandpieces (live metadata, 2026-06-13) — isFork=false, parent=null, licenseInfo=null, createdAt=2026-03-30T10:28:30Z, description 'Atomic, standalone building blocks stolen from the best open-source AI tooling.'"
  - /Transpara/transpara-ai/repos/wiki/raw/open-brain/2026-06.md  # L4028 — Epic-1 "Investigations" era maps repos paperclip / hermes-agent / bitsandpieces = "Paperclips/Hermes/Atoms"
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # v3.9.1 crosswalk — NO row for bitsandpieces/Atoms; gStack row (pattern-only, L83/L191) is the nearest governed decision
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-13-issue-14-go-module-path-recon.md  # L25 — the only research-checkpoint mention of bitsandpieces ("no go.mod")
  - /Transpara/transpara-ai/repos/docs/dark-factory/archive/v2/atoms-analysis-and-dark-factory.md  # the OTHER "Atoms" (AI product-creation platform) — name-collision source, NOT this repo
  - /Transpara/transpara-ai/repos/docs/dark-factory/archive/v2/adrs/ADR-0005-atoms-production-line-pattern.md  # ADR-0005 "Adopt Atoms as a production-line pattern only" — also the OTHER Atoms
  - "Upstream context only (not re-published): github.com/garrytan/gstack — the MIT-licensed project the 4 entries distil patterns from"
confidence:
  fork_framing: contested/refuted — the compile request frames bitsandpieces as "a forked public project" with an "upstream"; live GitHub metadata says isFork=false, parent=null. It is an ORIGINAL transpara-ai catalog that extracts patterns from upstream OSS (chiefly gstack), not a fork of any single upstream. Stated, not silently adopted.
  crosswalk_row: none — there is NO bitsandpieces/Atoms row in the v3.9.1 crosswalk. This article is THIN on a formal decision by design; what IS governed is its source project gStack (pattern-only).
  atoms_alias: thin — "Atoms" comes only from one Open Brain narrative note (the Epic-1 era map), not from the repo, the crosswalk, or any checkpoint. The repo's own GitHub description/README never say "Atoms."
  name_collision: high — the v2 "Atoms" (atoms-analysis + ADR-0005) is a DIFFERENT entity (an AI product-creation/startup platform), unrelated to this code-snippet catalog. Do not conflate.
  repo_internals: thin — claims about each entry are README-grounded only; the reference implementations were not exercised this run.
  stolen_wording: high — "stolen" is the repo's own word (README headline + live GitHub description), used self-deprecatingly; it denotes pattern-distillation with attribution, not license violation.
---

# bitsandpieces

**A small transpara-ai catalog of atomic, copy-one-directory AI-tooling patterns — surveyed loosely into the [[civilization-landscape-investigation]]'s "Investigations" era as *"Atoms,"* but never given a formal decision row.** The repo (`transpara-ai/bitsandpieces`) was created on **2026-03-30** as four independently-consumable building blocks "stolen from the best open-source AI tooling," each distilled to a pattern and attributed to its source. In the arc's later narrative bookkeeping it is grouped with [[paperclip|Paperclip]] and [[hermes-agent|Hermes]] under Epic 1 — *"Paperclips/Hermes/Atoms"* — i.e. the early-2026 era when Transpara was reading other people's agent tooling to decide what was worth keeping (`raw/open-brain/2026-06.md`, L4028). Its theme is exactly that: **atomic, independently-consumable building blocks lifted from the best OSS AI tooling, kept as patterns rather than dependencies.**

This article is about **our catalog and how it sits in the investigation**, not a mirror of any upstream's documentation. The patterns it distils trace to public OSS (chiefly Garry Tan's `gstack`, MIT); those upstreams are cited here as context only, never re-published.

> ⚠ **Fail-legible note (this is the thinnest investigation article in the set).** Unlike its Epic-1 siblings [[paperclip|Paperclip]] and [[hermes-agent|Hermes]], **bitsandpieces has no row in the v3.9.1 technology-decision crosswalk** — no `selected` / `pattern-only` / `research-only` / `deferred` / `excluded` verdict was ever recorded for it. It was not one of the investigation's 22 surveyed candidates. So most of what a reader wants ("what did the investigation decide about it?") is genuinely **not established** — and is marked thin throughout rather than confabulated. What *is* known is below.

## What it actually is

From its own `README.md`, bitsandpieces is a catalog with one governing idea:

> "Atomic, standalone building blocks extracted from the best open-source AI tooling. Each entry is independently consumable — copy the directory into your project and adapt."

Its stated philosophy is three words, and they map cleanly onto the theme:

- **Atomic** — "each entry works alone. No shared dependencies between entries."
- **Attributed** — "every entry names its source repo and license."
- **Adapted** — "code is distilled to the pattern, not a copy-paste of the original. Read the original for full context."

The catalog as of this compile is **four entries, and the README names a single upstream for all four — [[gstack|gStack]]** (`github.com/garrytan/gstack`):

| Entry | Source (per README) | What it is |
|---|---|---|
| `persistent-daemon` | gstack | long-lived localhost daemon with state file, auth, idle shutdown, version auto-restart |
| `safety-hooks` | gstack | Claude Code PreToolUse hooks that warn on destructive commands and block edits outside a directory |
| `llm-eval-framework` | gstack | three-tier testing: static validation, E2E via `claude -p`, LLM-as-judge quality scoring |
| `skill-template-gen` | gstack | template → `SKILL.md` generator with resolver plugins and multi-host output |

The repo also carries a standalone reference doc, `claude-code-official-plugins-and-skills.md`, and a contributing rule that re-states the discipline: each new entry needs a `README.md` explaining the pattern, a minimal working reference implementation, and attribution to the source project.

> ⚠ **Fail-legible note (theme vs. catalog).** The compile theme says blocks "stolen from **the best OSS AI tooling**" (plural). True to the *intent*, but as built **every one of the four entries is sourced from `gstack` specifically** — the catalog is so far single-upstream, not a broad cross-section. The plural ambition is the README's framing ("Find something worth stealing? Open a PR"); the current contents are narrower. Stated so the breadth is not overclaimed.

One entry was read in full this run, `safety-hooks`, and it is worth noting because it rhymes with the arc's deepest principle: the **freeze** hook blocks any `Edit`/`Write` outside a configured boundary with a hard `"deny"` and **no override**, while the **careful** hook returns `"ask"` (overridable) on destructive Bash like `rm -rf`, `DROP TABLE`, `git push --force`. That `deny`-by-default-at-the-boundary shape is the same fail-closed logic [[gates]] and the [[event-graph|EventGraph]] interface enforce structurally — though here it is a copy-and-adapt code snippet, **not a governed factory control**, and the resemblance is this article's observation, not a claim the catalog makes about itself.

## How it entered the arc

bitsandpieces enters the record through **one Open Brain narrative note**, not through the formal investigation pipeline. The Epic→era information-architecture map (`raw/open-brain/2026-06.md`, L4028) lists the arc's first era as:

> "(E1) Investigations [repos paperclip / hermes-agent / bitsandpieces = 'Paperclips/Hermes/Atoms', plus scouting MetaGPT/OpenManus/MiroThinker]"

So the **"Atoms" alias is purely this narrative label** — a retrospective grouping of three early-2026 transpara-ai repos as the era when Transpara was surveying agent tooling. The repo's own GitHub description and README never call it "Atoms"; they call it "building blocks."

Beyond that one note, the [[civilization-landscape-investigation]]'s own checkpoints barely touch it. The single mention in the entire research corpus is incidental: the Issue-14 Go-module-path recon (2026-05-13) inventories sibling repos and records `bitsandpieces: no go.mod` (`…/research/checkpoints/2026-05-13-13-issue-14-go-module-path-recon.md`, L25) — i.e. it was swept only as "not a Go module, nothing to rename," not analysed for inclusion. It is **absent from the 22-item kickoff candidate list, absent from the Phase-4 batch analyses, and absent from the closeout inclusion summary.**

## Where it sits in the decision crosswalk: nowhere directly

The authoritative per-item register for external technology is the **v3.9.1 External Technology Decision Crosswalk** (`02-technology-decision-crosswalk-v3.9.md`). **There is no row for bitsandpieces or "Atoms."** Per the investigation's own governance rule, that is itself meaningful: the crosswalk's purpose is "to make external technology decisions visible to reviewers before implementation begins," and "missing decisions are recorded as gaps rather than silently assumed." On that standard, **bitsandpieces is an unrecorded item, not a decided one.**

The nearest governed decision is for **its upstream source, [[gstack|gStack]]**, which *does* have a crosswalk row:

| Field | Value for **gStack** (per crosswalk) |
|---|---|
| Current decision | **pattern-only** |
| Integration mode | workflow / skill pattern |
| Owning epic | future capability or operator packet |
| Fork / adapter / pattern / exclude | **pattern** |
| Main risk | "skill patterns can bypass `CapabilityArtifact` evidence" |

with the binding per-item note:

> "Workflow or skill ideas are `CapabilityArtifact` candidates if they affect factory behavior. They must not influence work without usage logging and capability evidence."

Because bitsandpieces is literally a hand-curated extraction of gStack patterns (all four entries cite gStack), the **gStack pattern-only decision is the closest thing to a governing verdict over bitsandpieces' contents** — by inheritance, not by its own row. Under v3.9 **Decision 15** ("external frameworks stay outside control roles"), any gStack-derived pattern remains a reference/pattern, never kernel, truth source, Work replacement, policy owner, or factory controller, unless a later accepted ADR changes it. None has.

> ⚠ **Fail-legible note (inheritance is inference, not a recorded decision).** "gStack's pattern-only row also governs bitsandpieces" is **this article's reasoning** from the README's attribution, not a statement any source makes. No source links the two. It is offered as the most defensible reading of an item the crosswalk never addressed — explicitly labelled inference.

## The "fork" framing does not hold up

The compile request frames bitsandpieces as "a forked public project … Forked into transpara-ai," with an "Upstream." **Live GitHub metadata refutes this:**

| Field | Live value (`repos/transpara-ai/bitsandpieces`, 2026-06-13) |
|---|---|
| `isFork` | **false** |
| `parent` | **null** |
| `licenseInfo` | **null** |
| `createdAt` | `2026-03-30T10:28:30Z` |
| `description` | "Atomic, standalone building blocks stolen from the best open-source AI tooling. Each entry is independently consumable." |

So bitsandpieces is an **original transpara-ai repository that *extracts patterns from* upstream OSS** — not a fork of any single upstream project. This makes it categorically different from its Epic-1 siblings: [[paperclip|Paperclip]] *is* a genuine fork (`isFork=true`, parent `paperclipai/paperclip`), and [[hermes-agent|Hermes]] is forked too. bitsandpieces only shares their *era* and their *posture* (read OSS, keep the pattern, cede no authority), not their fork mechanics.

> ⚠ **Conflict stated, not resolved.** Compile-request framing ("forked public project / upstream / forked into transpara-ai") vs. live GitHub (`isFork=false`, `parent=null`). This article follows the **code/metadata ground truth** per the source hierarchy (code > instructions > prose) and treats the "fork" language as a loose grouping with the genuinely-forked Epic-1 siblings, not a literal fact about this repo.

## The other "Atoms" — a name collision to keep straight

The dark-factory archive contains a v2 analysis titled *"Atoms Platform Deep Dive"* (`archive/v2/atoms-analysis-and-dark-factory.md`) and **ADR-0005, "Adopt Atoms as a production-line pattern only"** (`archive/v2/adrs/ADR-0005-…`). These are about a **completely different "Atoms"**: an *AI-powered product-creation platform* with multi-agent roles (Product Manager, Architect, Engineer, Researcher, Growth/Marketing) that "take[s] an idea and produce[s] a working product" — from which the v2 design borrowed only the production-line / artifact-graph / generation-verification-repair / packaging patterns and explicitly rejected the startup/growth/marketing framing.

That "Atoms" is a **product platform**; *this* "Atoms" (bitsandpieces) is a **four-snippet code catalog**. They share nothing but a word.

> ⚠ **Fail-legible note (do not conflate).** Any future reader searching "Atoms" in the dark-factory corpus will hit ADR-0005 and the v2 platform analysis first. Those are **not** about `transpara-ai/bitsandpieces`. The only source that calls bitsandpieces "Atoms" is the single Open Brain era-map note; the ADR-0005 "Atoms" predates and out-documents it but refers to a different thing. Stated explicitly so the collision is not silently merged.

## How this relates to the rest of the arc

bitsandpieces is a minor, early data point in the same outward-looking phase that produced the [[civilization-landscape-investigation]]: the period when the [[dark-factory]] effort was reading external agent tooling to decide what to keep. Its posture is the arc's posture in miniature — **mine the pattern, attribute the source, import no authority** — the same containment logic the investigation applied at scale and Decision 15 later ratified. But where the investigation produced a defended register of decisions, bitsandpieces produced a handful of reusable snippets and never made it onto that register. It is best read as **a personal toolbox of OSS patterns from the Investigations era**, loosely tagged "Atoms" in hindsight, whose only formally-governed content is inherited from the [[gstack|gStack]] pattern-only decision.

## Sources & provenance

- **Repo README** — `/Transpara/transpara-ai/repos/bitsandpieces/README.md`: the "Atomic / Attributed / Adapted" philosophy, the four-entry catalog (all sourced from gstack), and the contributing rule. Primary evidence for what the catalog *is*.
- **One entry, read in full** — `/Transpara/transpara-ai/repos/bitsandpieces/safety-hooks/README.md`: gStack (MIT) PreToolUse hooks; `freeze` = hard `deny` outside a boundary (no override), `careful` = overridable `ask` on destructive Bash. README-grounded; reference implementation not exercised this run.
- **Live GitHub metadata** — `repos/transpara-ai/bitsandpieces` (`gh repo view`, 2026-06-13): `isFork=false`, `parent=null`, `licenseInfo=null`, `createdAt=2026-03-30T10:28:30Z`, description "Atomic, standalone building blocks stolen from the best open-source AI tooling." Refutes the "fork/upstream" framing.
- **Open Brain narrative** — `/Transpara/transpara-ai/repos/wiki/raw/open-brain/2026-06.md`, L4028: the Epic-1 "Investigations" era map, the sole source of the *"Atoms"* alias ("paperclip / hermes-agent / bitsandpieces = 'Paperclips/Hermes/Atoms'").
- **v3.9.1 External Technology Decision Crosswalk** — `/Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md`: **contains no bitsandpieces/Atoms row**; the **gStack** row (decision `pattern-only`, L83; per-item note L191-195) is the nearest governed verdict and is cited as inherited, not as a row for this repo.
- **Go-module recon checkpoint** — `/Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-13-issue-14-go-module-path-recon.md`, L25: the only research-corpus mention of bitsandpieces ("no go.mod"), confirming it was swept incidentally, not analysed for inclusion.
- **Name-collision sources (the *other* Atoms)** — `…/dark-factory/archive/v2/atoms-analysis-and-dark-factory.md` and `…/archive/v2/adrs/ADR-0005-atoms-production-line-pattern.md`: an AI product-creation platform, unrelated to this repo; cited to keep the two "Atoms" distinct.
- **Upstream (context only, not re-published)** — `github.com/garrytan/gstack` (MIT), the project the four entries distil patterns from, named in the repo README and each entry's attribution.

**Conflicts stated, not resolved.** (1) *Fork framing*: compile request says "forked public project / upstream"; live GitHub says `isFork=false`, `parent=null` — code/metadata ground truth followed, framing flagged as loose grouping with the genuinely-forked Epic-1 siblings. (2) *Decision status*: there is **no crosswalk row** for bitsandpieces; the article is thin on a formal verdict by necessity, and the gStack pattern-only inheritance is labelled as this article's inference, not a recorded decision. (3) *The "Atoms" alias* rests on a single Open Brain note and collides with an unrelated v2 "Atoms" platform — both stated. `[[civilization-landscape-investigation]]`, `[[dark-factory]]`, `[[paperclip]]`, `[[gates]]`, and `[[event-graph]]` resolve to compiled articles; `[[gstack]]` and `[[hermes-agent]]` are forward references not yet compiled.

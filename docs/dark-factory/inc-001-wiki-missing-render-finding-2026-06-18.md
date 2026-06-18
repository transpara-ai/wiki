# INC-001 Civilization Wiki Missing-Render Finding

## Purpose

This packet records the Civilization Wiki-side user-facing evidence posture for
the Test 001 cross-repo runtime-doctrine drift tabletop tracked by
`transpara-ai/civilization-operation`.

It is a missing-render finding, not a correction, deployment record, browser
capture, runtime observation, doctrine artifact, or authority artifact.

## Finding

```text
finding_id: inc-001-civilization-wiki-missing-render-2026-06-18
incident: INC-001 / Test 001 Cross-Repo Runtime-Doctrine Drift Tabletop
surface_repo: transpara-ai/civilization-wiki
surface_status: MISSING_RENDER_ACCEPTED
surface_status_meaning: missing durable rendered or deployed evidence recorded, not authority signoff
source_commit: 0e15544ca32c8dfabaf9ea53f5fa4bf495a8d612
correction_type: NO_CHANGE
human_authorization_required: no
human_authorization_evidence: none
```

The wiki has source-defined narrative, discovery, and visualization surfaces
associated with the simulated incident classes, but this packet does not cite a
deployed URL, browser screenshot, durable rendered capture, public correction,
or incident-specific stale-claim comparison for INC-001. Disposable local build
output from validation is not durable incident evidence.

The `human_authorization_required` value above is scoped only to recording this
missing-render finding. It does not grant authority to publish a correction,
change public posture, alter doctrine, alter runtime behavior, or close INC-001
as `GREEN`.

## Surfaces Reviewed

| Surface | Class | Route or output | Source anchors at `source_commit` | Finding |
| --- | --- | --- | --- | --- |
| Wiki source index | `DISCOVERY`, `NARRATIVE` | `index.md`; rendered as `dist/index.html` | `index.md:1-80`; `compile/build_site.py:316-320` | Source index and render rule exist; no deployed URL, browser screenshot, durable rendered capture, correction, or stale-claim comparison is cited. |
| Wiki article corpus | `DISCOVERY`, `NARRATIVE`, `ARCHIVAL` | `wiki/*.md`; rendered as `dist/<slug>.html` | `compile/build_site.py:84-93`; `compile/build_site.py:307-315` | Source article corpus and render loop exist; this packet does not inspect every article for an incident-specific stale claim and cites no durable rendered capture. |
| Civilization arc visualization | `VISUALIZATION`, `DISCOVERY` | `civilization-arc.html`, `civilization_arc.html` | `compile/build_site.py:269-286`; `compile/build_site.py:321-323`; `compile/assets/civilizationArcData.js:2173-2334` | Source arc output rule and worklist data exist; no browser screenshot, deployed route, or incident-specific rendered capture is cited. |
| Observatory article | `DISCOVERY`, `NARRATIVE` | `the-observatory.html` when rendered | `wiki/the-observatory.md:1-96` | Source article exists and describes the Site Observatory; no incident-specific comparison against current Site runtime or rendered output is cited here. |
| Civilization Wiki meta article | `DISCOVERY`, `NARRATIVE` | `civilization-wiki.html` when rendered | `wiki/civilization-wiki.md:1-90` | Source article exists; no incident-specific correction or durable rendered capture is cited. |
| Gate and deployment posture articles | `DISCOVERY`, `NARRATIVE` | `gate-k.html`, `gate-l.html`, `deployment-arc.html`, `slice-1-completion.html`, `base-slice-0.html`, `v3-9.html`, `v4-0.html` when rendered | `wiki/gate-k.md`, `wiki/gate-l.md`, `wiki/deployment-arc.md`, `wiki/slice-1-completion.md`, `wiki/base-slice-0.md`, `wiki/v3-9.md`, `wiki/v4-0.md` | Source articles exist for gate and deployment posture; this packet does not certify any gate, deployment, or doctrine state beyond recording missing rendered incident evidence. |
| Runtime and role posture articles | `DISCOVERY`, `NARRATIVE` | `hive-governance.html`, `roles-catalog.html`, `civic-roles.html`, `work.html`, `site.html` when rendered | `wiki/hive-governance.md`, `wiki/roles-catalog.md`, `wiki/civic-roles.md`, `wiki/work.md`, `wiki/site.md` | Source articles exist for runtime and role posture; no incident-specific stale-claim comparison, correction, screenshot, or deployed route is cited. |

The source anchors above were spot-checked in the local checkout before PR
review. They are commit-bounded source-location hints, not rendered output,
runtime observation, deployment evidence, or a machine-validated proof.

## Boundaries

This packet does not prove:

- that INC-001 affected a live wiki reader
- that the wiki was deployed or published at `source_commit`
- that any wiki route rendered correctly in a browser for INC-001
- that any wiki source article contained or lacked a stale incident claim
- that a public correction was required or completed
- that Site, Hive, Work, EventGraph, OpenBrain, or active roster gaps are resolved
- that doctrine, runtime behavior, EventGraph records, or human authorization exist
- that Test 001 is `GREEN`

`docs` remains the canonical doctrine source when doctrine conflicts with the
wiki. `site` remains the browser UI owner for Site routes. `hive` remains the
runtime source for Hive behavior. `eventgraph` remains the incident evidence
source for event records. The wiki only owns the narrative, discovery, and arc
visualization surfaces listed above.

## Validation Plan

The owning repo validation for this documentation packet is:

```bash
npm run verify
```

This validation may build ignored local `dist/` output as part of the repo's
normal verification path. That output is not cited as durable incident evidence.

The packet should be cited by `civilization-operation` only after the PR that
adds it has passed local validation, GitHub CI, exact-head adversarial review,
and has been merged to `origin/main`.

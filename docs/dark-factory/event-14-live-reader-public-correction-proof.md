# Event 14 Live Reader Public Correction Proof

This packet records the `civilization-wiki` display-consumer side of Dark
Factory v4.0 Event 14. The display consumes a checked-in public-safe fixture
derived from the merged `civilization-operation` export lifecycle and renders it
under the Civilization arc as display-only correction evidence.

## Source

- Governing authority: Event 14 AuthorityDecision on file. The public wiki
  display does not publish private governing-repo identifiers.
- Operation export lifecycle: `transpara-ai/civilization-operation#30`.
- Operation exact reviewed head:
  `08786bdcfc6034ac877dd5aa2fbb0e7883cb3b85`.
- Operation merge commit:
  `45b3e9f219d7b81c9991c253d2db4f906d6034bc`.

The wiki fixture is checked in. It performs no live private GitHub fetch and
does not dereference private governing repositories from the public display.

## Display Behavior

The arc now renders a Live Reader Correction Proof section with:

- generated-at and operation source metadata;
- global freshness state;
- source-recorded, stale, corrected, and superseded item labels;
- a correction record showing that the stale Test 001 GREEN fixture is
  superseded by the public-safe Test 001 YELLOW tracker;
- missing and unavailable omitted-source labels;
- limitation text for authority, stale fixture use, unavailable deployed route
  evidence, private runtime evidence, and non-closure boundaries.

Invalid, missing, globally stale, or unavailable correction payloads fail
closed and render only an unavailable notice.

## Non-Claims

This display does not claim production readiness, runtime authority, deploy
authority, protected side effects, autonomy increase, value allocation, live
private GitHub access, private operational data publication, EventGraph writes,
public correction completion on a deployed surface, Gate X closure, Test 001
GREEN or closure, process-residual closure, residual-risk closure, or closure of
R-001/R-002/R-003.

## Validation

Targeted validation:

```bash
python3 compile/test_live_reader_correction.py
```

Repository validation:

```bash
npm run verify
git diff --check origin/main...HEAD
git diff --name-status origin/main...HEAD
```

Negative checks cover missing public-safe metadata, globally stale/missing/
unavailable payloads, missing correction references, and absence of active
private fetch, deploy, runtime, EventGraph-write, protected-setting, protected
action, or production-readiness paths.

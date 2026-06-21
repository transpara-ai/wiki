(function () {
  "use strict";

  window.CIVILIZATION_PROGRESS_EVIDENCE_SOURCE = {
    operation_pr: "transpara-ai/civilization-operation#28",
    operation_pr_url: "https://github.com/transpara-ai/civilization-operation/pull/28",
    operation_merge_commit: "65305b2f2a7a095a01015a5b3e4532f22c072ac6",
    operation_reviewed_head: "56082d91baffff3f714e096ac2f5fac3934fba12",
  };

  window.CIVILIZATION_PROGRESS_EVIDENCE = {
    "audit": {
      "authority_boundary": [
        "display-only",
        "no live private API fetch",
        "no runtime mutation",
        "no production claim",
        "no gate closure",
        "no autonomy increase",
        "no value allocation",
        "manual snapshot, not live synchronization"
      ],
      "wiki_public_redactions": [
        "private governing source URLs",
        "private governing source identifiers"
      ],
      "validation_commands": [
        "python3 scripts/test-progress-evidence-export.py",
        "make verify"
      ]
    },
    "generated_at": "2026-06-21T00:00:00Z",
    "items": [
      {
        "authority_state": "bounded-authorized",
        "blockers": [],
        "display_only": true,
        "evidence_state": "exact-head-reviewed",
        "id": "event-12-progress-display-authority",
        "kind": "authority",
        "limitations": [
          "Does not authorize production, runtime, autonomy, value, protected settings, or gate closure.",
          "Wiki consumer work remains separate until this operation export lifecycle merges."
        ],
        "public_summary": "Bounded authority exists for one operation-side sanitized progress evidence export PR lifecycle, followed after merge by one wiki display-consumer PR lifecycle.",
        "source_ref": "governing authority on file",
        "source_repo": "governance record",
        "state": "merged",
        "title": "Event 12 Progress Evidence Display Path Authority"
      },
      {
        "authority_state": "no-new-authority",
        "blockers": [
          "No deployed Wiki route evidence.",
          "No live-reader Wiki evidence.",
          "No public correction proof."
        ],
        "display_only": true,
        "evidence_state": "source-recorded",
        "id": "operation-pr-27-inc001-reconciliation",
        "kind": "operations-reconciliation",
        "limitations": [
          "Local render evidence is not live-reader evidence.",
          "The reconciliation did not close Test 001 or any governance gate."
        ],
        "public_summary": "The operations record reconciled selected local Site and Civilization Wiki render evidence while preserving the Test 001 YELLOW result.",
        "source_commit": "39a48bebd64db756fd04a38e834e1b19a1d1ba65",
        "source_ref": "civilization-operation#27",
        "source_repo": "transpara-ai/civilization-operation",
        "source_url": "https://github.com/transpara-ai/civilization-operation/pull/27",
        "state": "merged",
        "title": "INC-001 Local-Render Reconciliation"
      },
      {
        "authority_state": "human-gated-for-closure",
        "blockers": [
          "Exact live evidence remains incomplete.",
          "Active production roster evidence remains incomplete.",
          "Runtime/deployment evidence remains incomplete.",
          "User-facing live-reader and public correction evidence remain incomplete."
        ],
        "display_only": true,
        "evidence_state": "open-tracker",
        "id": "test-001-yellow-open-tracker",
        "kind": "test-state",
        "limitations": [
          "Issue prose may lag later PR merges; this export uses explicit public projection only.",
          "YELLOW is not GREEN and does not close the incident or residual risks."
        ],
        "public_summary": "Test 001 remains YELLOW while live evidence, production roster evidence, runtime evidence, user-facing evidence, public correction proof, and action-specific human authorization remain incomplete.",
        "source_commit": "39a48bebd64db756fd04a38e834e1b19a1d1ba65",
        "source_ref": "civilization-operation#26",
        "source_repo": "transpara-ai/civilization-operation",
        "source_url": "https://github.com/transpara-ai/civilization-operation/issues/26",
        "state": "yellow",
        "title": "Test 001 Remains YELLOW"
      },
      {
        "authority_state": "no-public-correction-authority",
        "blockers": [
          "No deployed progress-display feed.",
          "No live-reader evidence.",
          "No stale-claim adjudication or public correction proof."
        ],
        "display_only": true,
        "evidence_state": "selected-local-render",
        "id": "wiki-pr-19-local-render-evidence",
        "kind": "user-facing-evidence",
        "limitations": [
          "The local-render packet does not prove deployed Wiki behavior.",
          "Future display consumption must occur in a separate wiki PR after this operation export merges."
        ],
        "public_summary": "Civilization Wiki recorded selected local browser-render evidence for INC-001, but no live-reader progress display feed has been accepted yet.",
        "source_commit": "ff5211716e488a68615082b0fc384540069a9631",
        "source_ref": "civilization-wiki#19",
        "source_repo": "transpara-ai/civilization-wiki",
        "source_url": "https://github.com/transpara-ai/civilization-wiki/pull/19",
        "state": "local-render-recorded",
        "title": "Civilization Wiki Local Render Evidence"
      }
    ],
    "omitted_sources": [
      {
        "id": "future-wiki-progress-feed",
        "public_summary": "No accepted public-safe wiki progress feed exists yet; the display consumer is intentionally deferred until this operation export PR lifecycle merges.",
        "reason": "missing-public-projection",
        "source_ref": "pending-wiki-consumer-pr",
        "source_repo": "transpara-ai/civilization-wiki",
        "title": "Future Wiki Progress Feed"
      },
      {
        "id": "private-runtime-and-live-reader-sources",
        "public_summary": "Runtime, production, private GitHub, and live-reader sources are outside this bounded export and require later governed events.",
        "reason": "outside-authorized-scope",
        "source_ref": "not-collected",
        "source_repo": "multiple",
        "title": "Runtime And Live-Reader Sources"
      }
    ],
    "privacy": {
      "network_access": "none",
      "private_fields_omitted": [
        "operator_notes",
        "raw_issue_body"
      ],
      "projection_policy": "explicit-allowlist",
      "public_safe": true
    },
    "schema_version": 1,
    "source_scope": {
      "authorized_by": {
        "public_summary": "Governing authority is recorded outside this public wiki asset; private source identifiers are intentionally omitted."
      },
      "export_mode": "wiki-public-display-projection",
      "owning_repo": "transpara-ai/civilization-operation",
      "source_repositories": [
        "transpara-ai/civilization-operation",
        "transpara-ai/civilization-wiki"
      ]
    }
  };
})();

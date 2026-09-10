---
title: DevOps
status: curated repository engineering seed
last_compiled: "2026-09-07"
---

# DevOps

Infrastructure, networking, containers, delivery automation, observability,
security, and operational runbooks for Transpara.

Articles in this space describe documented operational knowledge and cite
their source material. They distinguish verified running configuration from
proposals, historical incidents, and procedures that still need validation.

## Repository engineering and delivery

The corpus comes from `transpara-ai/dev-ops`, refreshed against GitHub `main`
at `45140e1a0b79` on 2026-09-07. Start with [[devops-repository-scaffold]]
for the repository map and adoption guide.

- [[devops-verification]] — the shared `make verify` entry point, CI, lint,
  dependency maintenance, and the actual limits of the local Stop hook.
- [[devops-github-settings]] — desired merge protections, read-only drift
  inspection, and what the repository settings script checks.
- [[devops-codex-review]] — the merged self-hosted review runner,
  review-on-ready triggering, caller rollout, and removal of recognized
  legacy review files, with versioned sources and GitHub execution evidence.

These articles are internal and cite versioned source files. The runner
migration and review-trigger changes are now merged. Adopting the current
caller means requesting a review by marking a draft PR ready; later pushes
do not start another round. Network, container, monitoring, and application
service recovery runbooks still need their own operational sources.

---
entity: Platform and Transpara-MCP Boundary
org: transpara
primary_placement: platform/development-apis
placements:
  - platform/development-apis
  - civilization/architecture
classification: company-internal
aliases:
  - Platform/MCP boundary
  - Transpara Platform boundary
  - transpara-mcp boundary
  - demo runtime boundary
tier: institutional
status: reviewed; advisory only
last_compiled: "2026-09-05"
reviewed_on: 2026-09-05
review_by: 2026-12-04
source_authority:
  - code
  - configuration
  - adr
  - engineering-docs
sources:
  - raw/civilization/stage-0-institutional-substrate/05-platform-transpara-mcp-boundary-index-v0.1.0.md
  - raw/civilization/stage-0-institutional-substrate/README.md
  - /Transpara/transpara-ai/repos/platform/docs/product-context.md
  - /Transpara/transpara-ai/repos/platform/docs/platform-specification.md
  - /Transpara/transpara-ai/repos/platform/docs/architecture-decision-records.md
confidence:
  source_status: proposal
  claims: grounded in Stage 0 boundary index
  authority: advisory; does not change access policy
---

# Platform and Transpara-MCP Boundary

The Platform and Transpara-MCP Boundary separates three things that must not be
collapsed:

```text
commercial Transpara Platform product knowledge
authorized demo and simulation runtime data
customer production runtime contents
```

The Transpara Platform is the commercial industrial software product made by
Transpara LLC. `transpara-mcp` is the interface intended to present authorized
live Platform data to Transpara-AI. The boundary source is explicit that ordinary
operation does not presume physical access to customer production runtime
contents. Customer data is a customer secret unless a separate customer-specific
authority path exists.

## API and MCP authority boundary

The current engineering baseline identifies FastAPI services and an MCP-facing
process associated with tGraph. Exact routes and schemas belong to their
versioned repositories. MCP extends governed tool access; it is not an authority
system and cannot bypass identity, policy, audit, or source-of-truth controls.

A safe integration resolves the authenticated principal, authorizes a narrowly
named capability, validates and constrains inputs, executes through the owning
service, retains an attributable audit record, and returns typed results. Read
access does not imply write access, and a model request is never itself
authorization.

This article does not establish a public MCP endpoint, unrestricted model
access, or permission for an agent to mutate an operational system. Platform
ingress, authentication, service identity, network policy, secrets handling,
and resource controls apply to agent callers just as they apply to people and
ordinary software clients.

## The allowed live-data substrate

The Stage 0 source distinguishes demo/simulation estates from customer runtime
systems. Demo and simulation systems are Transpara-controlled, high-fidelity
estates used for sales, demonstrations, testing, and internal development. They
are the appropriate live-data substrate for Transpara-AI analysis.

Customer runtime systems are different. Industrial deployments may sit behind
many layers of firewalls and may contain refinery, generation, pharmaceutical,
drilling, telecom, satellite, military, or other high-criticality operating
state. The wiki must not imply access to that data.

## Repo-family meaning

The Platform boundary index treats `platform` as the product knowledge root and
records a broader implementation family: installer, API, storage interface,
visualization, deployment, data-layer packaging, SDK, and MCP access surfaces.

This wiki article is not a full Platform product article. It records the access
and ownership boundary that matters to the Civilization:

| Surface | Boundary |
| --- | --- |
| Transpara LLC | Owns the commercial product, customer obligations, and final human authority. |
| Transpara Platform | Product and runtime estate. |
| `transpara-mcp` | Interface to authorized live Platform data. |
| Demo/simulation estates | Authorized live data for demonstrations and analysis. |
| Customer production runtime | Not presumed accessible; requires separate authority. |

## Non-action

Stage 0 did not change Platform access policy, MCP deployment, customer
connectivity, demo connectivity, or runtime credentials. This article carries
that same non-action boundary.

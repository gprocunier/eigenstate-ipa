---
layout: default
title: Evidence and reporting model
diataxis: explanation
diataxis_type: explanation
audience: Operators and maintainers
outcome: Understand why reports are evidence, not enforcement.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
last_verified: 2026-05-07
---

# Evidence and reporting model

## What Claim Is Being Made?

Report roles produce reviewable evidence from explicit inputs. They do not remediate drift or enforce policy.

## What Problem Does It Address?

Operational workflows need artifacts that reviewers and automation can compare over time without mixing detection and mutation in one step.

## Which System Owns Which Responsibility?

| System | Responsibility |
| --- | --- |
| Report roles | Render JSON, YAML, and Markdown from supplied records. |
| IdM and lookups | Provide source records for report inputs. |
| AAP | Stores job output and artifacts according to site configuration. |
| Remediation workflows | Remain separate and explicit. |

## What Evidence Proves The Boundary?

- JSON reports for machine review.
- YAML reports for structured inspection.
- Markdown reports for human review.
- Changed state remains false for read-only report roles.

## What Does This Not Claim?

- A report is not enforcement.
- A status field is not proof that remediation happened.
- Report generation does not make source records correct.

## What Risks Remain?

- Bad inputs produce misleading reports.
- Artifacts can become stale.
- Report consumers can over-trust summary status without reviewing source evidence.

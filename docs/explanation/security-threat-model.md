---
layout: default
title: Security threat model
diataxis: explanation
diataxis_type: explanation
audience: Operators and maintainers
outcome: Understand assumptions, controls, risks, and residual risk.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
source_material:
  - ../rewrite-audit.md
last_verified: 2026-05-07
---

# Security threat model

## What Claim Is Being Made?

The documentation threat model is conservative: identity, secrets, keytabs, certificates, cluster manifests, and reports must be described with explicit authority and workflow boundaries.

## What Problem Does It Address?

This collection crosses sensitive surfaces. Documentation that blurs read, render, check, and mutate paths can lead to unsafe automation even when the code behaves correctly.

## Which System Owns Which Responsibility?

| System | Responsibility |
| --- | --- |
| IdM/Kerberos/CA | Own sensitive identity, key, and certificate state. |
| Collection | Exposes narrow Ansible surfaces with documented options and return shapes. |
| Docs governance | Blocks private field language and flags secret-hygiene risks. |
| Operators | Must scope credentials, protect artifacts, and review mutating workflows. |

## What Evidence Proves The Boundary?

- Front matter declaring `authority_boundary`, `workflow_boundary`, and `evidence_shape`.
- Language check output for blocked terms and secret-like examples.
- Secret-safety tests for roles.
- Validation report after rewrite quality gates.

## What Does This Not Claim?

- The docs make deployments secure by themselves.
- A linter can prove every secret is protected.
- All risk is eliminated by using IdM-backed workflows.

## What Risks Remain?

- Credentials can be over-scoped.
- Logs, fact caches, and artifacts can leak payloads.
- External systems can enforce different policy than the rendered evidence expects.
- Human review can miss a boundary mismatch.

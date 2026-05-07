---
layout: default
title: OpenShift identity and workload model
diataxis: explanation
diataxis_type: explanation
audience: Operators and maintainers
outcome: Understand OpenShift identity and workload Secret flows.
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

# OpenShift identity and workload model

## What Claim Is Being Made?

The collection renders and validates OpenShift identity and workload artifacts before runtime enforcement. The cluster enforces only after reviewed configuration is applied.

## What Problem Does It Address?

OpenShift identity, Keycloak federation, breakglass paths, and workload Secrets need evidence before cluster mutation, especially when source material comes from IdM.

## Which System Owns Which Responsibility?

| System | Responsibility |
| --- | --- |
| IdM | Owns group, user, vault, certificate, keytab, and policy source records. |
| Keycloak/OIDC | Owns federation and claim behavior where used. |
| OpenShift/Kubernetes | Owns runtime OAuth, RBAC, Secret access, and admission behavior. |
| Collection roles | Render manifests and readiness reports for review-first workflows. |

## What Evidence Proves The Boundary?

- Rendered OAuth/OIDC configuration.
- Readiness reports for identity and breakglass checks.
- Redacted Secret review manifests.
- Opt-in payload manifests handled outside public docs.

## What Does This Not Claim?

- Rendering does not apply cluster configuration.
- A Secret manifest is not secure because it was rendered.
- IdM does not enforce Kubernetes RBAC.

## What Risks Remain?

- Cluster credentials can apply unreviewed payloads.
- Payload manifests need restrictive storage.
- Identity claim mapping can drift from IdM group intent.

---
layout: default
title: Authority boundaries
diataxis: explanation
diataxis_type: explanation
audience: Operators and maintainers
outcome: Understand which system owns identity, orchestration, runtime enforcement, and evidence.
authority_boundary:
  - idm
  - collection
  - ansible
  - aap
  - kubernetes
  - reports
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
source_material:
  - ../../README.md
  - ../../roles
  - ../../playbooks
last_verified: 2026-05-07
---

# Authority boundaries

The collection is credible only when every page is clear about who owns the
state, who runs the workflow, and who enforces the result.

## Boundary Table

| Authority | Owns | Does not own |
| --- | --- | --- |
| IdM / FreeIPA | Identity, enrolled hosts, groups, vaults, Kerberos principals, IdM CA records, DNS, sudo, HBAC, SELinux maps, and user expiry attributes. | AAP job scheduling, Kubernetes runtime enforcement, private-key storage decisions, report remediation. |
| `eigenstate.ipa` | Ansible interfaces that read, render, validate, or explicitly mutate IdM-backed state. | The source truth itself, runtime cluster enforcement, or broad secret-manager semantics. |
| Ansible | Task execution, variables, check mode, module invocation, and task result handling. | Identity authority or long-term job evidence by itself. |
| AAP | Execution environments, job templates, scheduling, credentials, approvals, and job evidence. | IdM policy, Kerberos principal ownership, or cluster enforcement. |
| Kerberos tooling | Tickets and keytab retrieval under configured principal and host authority. | Authorization policy outside Kerberos and IdM. |
| IdM CA | Certificate issuance from CSRs and certificate retrieval/search. | Private key generation or protection. |
| Kubernetes and OpenShift | Runtime application of manifests, RBAC, Secret access, OAuth configuration, and cluster policy. | IdM state or Ansible report truth. |
| Reports | Evidence artifacts from supplied records and checks. | Enforcement or automatic remediation. |

## Workflow Boundaries

Use these labels consistently:

- `read-only`: query and return state without writing artifacts or remote state
- `render-only`: write review artifacts without applying them to a live runtime
- `preflight`: check prerequisites before a later workflow changes anything
- `check-mode`: predict change through Ansible dry-run behavior
- `mutating`: change IdM, files, Controller, cluster, certificate, keytab, or vault state

## Evidence Expectations

Every rewritten page should show or point to the artifact that proves the
boundary:

- reference pages point to source docs or `ansible-doc`
- how-to pages show expected task output or artifacts
- tutorials show safe sample output
- explanation pages link to the surface that implements the boundary

## What This Does Not Claim

The boundary language is not a guarantee that a site is secure. It is a
documentation control. The actual safety still depends on IdM ACLs, Kerberos
configuration, AAP credentials, Ansible variable handling, file permissions,
cluster controls, and operator review.

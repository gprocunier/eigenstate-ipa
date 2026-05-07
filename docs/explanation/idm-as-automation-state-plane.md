---
layout: default
title: IdM as an automation state plane
diataxis: explanation
diataxis_type: explanation
audience: Operators and maintainers
outcome: Understand why automation should consume live IdM state instead of maintaining a parallel copy.
authority_boundary:
  - idm
  - collection
  - ansible
  - aap
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
source_material:
  - ../../README.md
  - ../../llms.txt
  - ../../plugins/inventory/idm.py
  - ../../plugins/lookup
last_verified: 2026-05-07
---

# IdM as an automation state plane

The claim is not that IdM should own every automation decision. The claim is
that when IdM already records identity, host, policy, Kerberos, certificate,
DNS, or vault state, automation should read that state directly instead of
rebuilding it elsewhere.

## What Problem This Addresses

Static inventory and copied policy data drift. Secret material copied into
side-channel stores creates another review and rotation path. Keytab and
certificate workflows split across shell scripts are hard to audit from an
Ansible job record.

IdM already knows many of these facts:

- enrolled hosts and host metadata
- hostgroups, netgroups, and HBAC policy scope
- user, host, and service principals
- IdM vaults and vault membership
- certificate request and retrieval state
- DNS, sudo, and SELinux map records
- user expiry attributes used for temporary access boundaries

`eigenstate.ipa` exposes those facts as inventory, lookups, modules, roles, and
reports.

## Responsibility Split

| System | Responsibility |
| --- | --- |
| IdM / FreeIPA | Owns identity, host, vault, policy, DNS, Kerberos principal, and certificate records. |
| `eigenstate.ipa` | Reads, renders, validates, or mutates that state through explicit Ansible interfaces. |
| Ansible | Executes tasks, passes variables, handles check mode, and records task results. |
| AAP | Schedules and records jobs, injects credentials, and runs through an execution environment. |
| Runtime platforms | Enforce only after their own configuration is applied. |

## Evidence That Proves The Boundary

Useful evidence comes from the interface being used:

- `ansible-inventory` output from `eigenstate.ipa.idm`
- structured lookup return records for vault, principal, DNS, sudo, HBAC, and
  SELinux map checks
- module changed state and check-mode predictions for vault, keytab,
  certificate, and user lease changes
- review manifests from render-only OpenShift and Kubernetes roles
- JSON, YAML, and Markdown report artifacts from read-only report roles

## What This Does Not Claim

This model does not make IdM a universal CMDB, a general-purpose secret manager,
or a remediation engine. It only says that IdM-owned state should remain
authoritative where the workflow is already about IdM identity, policy, vault,
Kerberos, certificate, DNS, sudo, HBAC, or SELinux map data.

## Risks That Remain

The collection still depends on correct IdM records, correct Kerberos and
ipalib client configuration, safe Ansible variable handling, and careful use of
mutating modules. A live inventory result is only as current as the IdM query
and the job that consumed it.

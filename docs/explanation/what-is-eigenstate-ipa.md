---
layout: default
title: What is eigenstate.ipa?
diataxis: explanation
diataxis_type: explanation
audience: Operators and maintainers
outcome: Understand the collection at a high level.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
source_material:
  - ../index.md
  - ../../README.md
last_verified: 2026-05-17
---

# What is eigenstate.ipa?

`eigenstate.ipa` is an Ansible collection for Red Hat IdM / FreeIPA. It exposes
IdM state to automation through inventory, lookup plugins, modules, roles,
wrapper playbooks, an execution-environment scaffold, and reporting workflows.

The collection is built around a narrow premise: if IdM already records a fact
that automation needs, Ansible should be able to consume that fact directly and
produce reviewable evidence from it.

## Use With, Not Instead Of

`eigenstate.ipa` is a companion collection for Red Hat IdM / FreeIPA
automation. It is not a replacement for `redhat.rhel_idm` or
`freeipa.ansible_freeipa`.

Use `redhat.rhel_idm` or `freeipa.ansible_freeipa` for core IdM lifecycle:
server installation, replica installation, client enrollment, and broad IdM
object management.

Use `eigenstate.ipa` when the automation task starts from existing IdM state
and needs that state as live inventory, policy evidence, vault, keytab, or
certificate workflow input, temporary-access context, AAP execution material,
or OpenShift/Kubernetes review artifacts.

| Need | Use |
| --- | --- |
| Install IdM server, replica, or client | `redhat.rhel_idm` or `freeipa.ansible_freeipa` |
| Manage broad IdM object lifecycle | `redhat.rhel_idm` or `freeipa.ansible_freeipa` |
| Build live Ansible inventory from IdM host and policy state | `eigenstate.ipa` |
| Retrieve or render vault, keytab, or certificate material for automation | `eigenstate.ipa` |
| Preflight HBAC, sudo, SELinux, DNS, or access-path state | `eigenstate.ipa` |
| Produce AAP, OpenShift, Kubernetes, or reporting evidence before mutation | `eigenstate.ipa` |

## What It Covers

The collection includes:

- live inventory from IdM hosts, hostgroups, netgroups, and HBAC-related state
- lookups for IdM vaults, principals, keytabs, certificates, OTP, DNS, sudo,
  SELinux maps, and HBAC rules
- modules for vault lifecycle, keytab management, certificate requests, and
  temporary access boundaries
- roles for AAP execution environments, OpenShift identity validation,
  workload Secret rendering, temporary access, sealed artifact delivery, and
  read-only reports
- playbooks that wrap common role workflows

## Why It Exists

Without an IdM-backed automation path, operators often maintain a second copy
of host inventory, access policy, static secrets, keytab handling, or
certificate workflow state. That duplicated state drifts from the identity
system that already owns the source records.

`eigenstate.ipa` keeps the source of truth visible. It reads IdM where reads are
enough, renders review artifacts where runtime systems need configuration, and
uses explicit modules where the workflow must change IdM or key material.

## What It Is Not

The collection is not a general-purpose vault, a PAM suite, a dynamic secret
lease engine, a cluster policy engine, or the canonical IdM lifecycle and CRUD
collection. It does not make AAP the identity authority, and reports do not
remediate anything by themselves.

Use it where the workflow is naturally tied to IdM identity, Kerberos,
certificates, DNS, sudo, HBAC, SELinux maps, vaults, host enrollment, or user
expiry state.

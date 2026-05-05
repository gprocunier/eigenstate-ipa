---
layout: default
title: Compatibility Policy
description: >-
  Compatibility and migration policy for eigenstate.ipa lookup plugins,
  modules, and side-effecting automation surfaces.
---

{% raw %}

# Compatibility Policy

`eigenstate.ipa` keeps the v1 surfaces usable while adding safer module
interfaces for operations that change IdM state or write sensitive local
artifacts.

## Policy

- Existing v1 lookups remain supported.
- New module surfaces are additive.
- Destructive or side-effecting lookup modes may gain warnings only after
  replacement documentation exists.
- Any removal or hard-disablement must wait for a v2 boundary.
- Migration examples must exist before a deprecation notice becomes stronger
  than a warning.
- Secret-bearing module returns must not include raw payloads unless the
  operator explicitly requests them.

## Current Boundary

| Surface | v1 status | Preferred new automation |
| --- | --- | --- |
| `eigenstate.ipa.keytab` lookup | supported | `eigenstate.ipa.keytab_manage` for retrieval to disk or rotation |
| `eigenstate.ipa.cert` lookup request mode | supported | `eigenstate.ipa.cert_request` for certificate issuance |
| `eigenstate.ipa.vault_write` module | supported | remains the module surface for vault mutation |
| read-only lookups such as `principal`, `dns`, `sudo`, `hbacrule` | supported | no migration needed |

The project does not remove an established lookup mode in this phase.

## Why Add Modules

Lookups are convenient for retrieving values into expressions. They are less
clear for operations that:

- rotate key material
- issue certificates
- write files
- need check-mode behavior
- should return metadata without returning secret payloads

Modules make side effects visible as Ansible tasks with `changed`, check mode,
argument specs, and safer return contracts.

## Version Boundary

The v1 line keeps compatibility for early adopters. A future v2 may remove or
hard-disable destructive lookup modes only after:

1. replacement module documentation exists
2. migration examples exist
3. at least one minor release overlaps old and new surfaces
4. adoption data and issue feedback indicate the migration path is usable

## Documentation Standard

Public docs should be useful to independent operators, platform teams, IdM
administrators, AAP operators, OpenShift administrators, security engineers,
and maintainers. The project should persuade through correctness,
repeatability, safe defaults, and evidence from validation workflows.

{% endraw %}

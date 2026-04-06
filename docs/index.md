---
layout: default
title: eigenstate.ipa
description: >-
  Ansible collection for Red Hat IdM / FreeIPA with dynamic inventory,
  IdM vault lookup, Kerberos automation, AAP integration, and secure secret
  retrieval.
---

# eigenstate.ipa

`eigenstate.ipa` is an Ansible collection for Red Hat IdM / FreeIPA. It has
two main jobs:

- dynamic inventory from IdM hosts, hostgroups, netgroups, and HBAC policy
- IdM vault lookup for Kerberos-authenticated secret retrieval in Ansible and
  AAP

It fits environments that already use IdM for host data, policy context, and
runtime secret retrieval.

## Current Release

- `1.4.0`
- added `eigenstate.ipa.vault_write` action module for vault lifecycle management
- create, archive, modify, and delete IdM vaults from Ansible
- full idempotency for standard vaults; check mode support
- delta-only member management

## Start Here

- [Collection Overview](https://github.com/gprocunier/eigenstate-ipa)
- [Documentation Map](https://gprocunier.github.io/eigenstate-ipa/documentation-map.html)
- [Inventory Plugin](./inventory-plugin.md)
- [Vault Plugin](./vault-plugin.md)
- [Vault Write Module](./vault-write-plugin.md)
- [Inventory Use Cases](./inventory-use-cases.md)
- [Vault Use Cases](./vault-use-cases.md)
- [Vault Write Use Cases](./vault-write-use-cases.md)
- [AAP Integration](./aap-integration.md)

## What The Collection Provides

- `eigenstate.ipa.idm`
  Dynamic inventory for live IdM-backed infrastructure targeting.
- `eigenstate.ipa.vault`
  IdM vault retrieval, metadata inspection, scoped search, and binary-safe
  secret lookup.
- `eigenstate.ipa.vault_write`
  IdM vault lifecycle management — create, archive, rotate, and delete
  vaults from Ansible with full idempotency and check mode support.

## Best Fit

- Red Hat IdM / FreeIPA environments
- Kerberos-first automation
- Ansible Automation Platform execution environments
- teams that want to use IdM as inventory and runtime secret source

## Repository

- GitHub: [gprocunier/eigenstate-ipa](https://github.com/gprocunier/eigenstate-ipa)
- Issues: [github.com/gprocunier/eigenstate-ipa/issues](https://github.com/gprocunier/eigenstate-ipa/issues)

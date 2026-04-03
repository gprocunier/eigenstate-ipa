---
layout: default
title: eigenstate.ipa
description: >-
  Ansible collection for Red Hat IdM / FreeIPA with dynamic inventory,
  vault lookup, Kerberos automation, AAP integration, and secure secret
  retrieval.
---

# eigenstate.ipa

`eigenstate.ipa` is an Ansible collection for Red Hat IdM / FreeIPA. It
focuses on two high-value operator paths:

- dynamic inventory from IdM hosts, hostgroups, netgroups, and HBAC policy
- vault lookup for Kerberos-authenticated secret retrieval in Ansible and AAP

That makes the project discoverable for the search terms people actually use:
Ansible FreeIPA inventory, Red Hat IdM Ansible, FreeIPA vault Ansible,
Kerberos automation, and AAP secret retrieval.

## Start Here

- [Collection Overview](https://github.com/gprocunier/eigenstate-ipa)
- [Documentation Map](https://gprocunier.github.io/eigenstate-ipa/)
- [Inventory Plugin](./inventory-plugin.md)
- [Vault Plugin](./vault-plugin.md)
- [Inventory Use Cases](./inventory-use-cases.md)
- [Vault Use Cases](./vault-use-cases.md)
- [AAP Integration](./aap-integration.md)

## What The Collection Provides

- `eigenstate.ipa.idm`
  Dynamic inventory for live IdM-backed infrastructure targeting.
- `eigenstate.ipa.vault`
  Vault retrieval, metadata inspection, scoped search, and binary-safe secret lookup.

## Best Fit

- Red Hat IdM / FreeIPA environments
- Kerberos-first automation
- Ansible Automation Platform execution environments
- teams that want to consume IdM as inventory and secret source of truth

## Repository

- GitHub: [gprocunier/eigenstate-ipa](https://github.com/gprocunier/eigenstate-ipa)
- Issues: [github.com/gprocunier/eigenstate-ipa/issues](https://github.com/gprocunier/eigenstate-ipa/issues)

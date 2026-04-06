---
layout: default
title: eigenstate.ipa
description: >-
  Ansible collection for Red Hat IdM / FreeIPA with dynamic inventory,
  IdM vault lookup, Kerberos keytab delivery, certificate automation,
  AAP integration, and secure secret retrieval.
---

# eigenstate.ipa

`eigenstate.ipa` is an Ansible collection for Red Hat IdM / FreeIPA. It has
four main jobs:

- dynamic inventory from IdM hosts, hostgroups, netgroups, and HBAC policy
- IdM vault lookup for Kerberos-authenticated secret retrieval in Ansible and
  AAP
- Kerberos keytab retrieval for host and service principals
- IdM CA certificate request, retrieval, and expiry search via the Dogtag PKI
  backend

It fits environments that already use IdM for host data, policy context, and
runtime secret retrieval.

## Current Release

- `1.2.0`
- adds `eigenstate.ipa.cert` and preserves the released `eigenstate.ipa.keytab`
  plugin in the integrated collection

## Start Here

- [Collection Overview](https://github.com/gprocunier/eigenstate-ipa)
- [Documentation Map](https://gprocunier.github.io/eigenstate-ipa/documentation-map.html)
- [Inventory Plugin](./inventory-plugin.md)
- [Vault Plugin](./vault-plugin.md)
- [Keytab Plugin](./keytab-plugin.md)
- [Cert Plugin](./cert-plugin.md)
- [Inventory Use Cases](./inventory-use-cases.md)
- [Vault Use Cases](./vault-use-cases.md)
- [Keytab Use Cases](./keytab-use-cases.md)
- [Cert Use Cases](./cert-use-cases.md)
- [AAP Integration](./aap-integration.md)

## What The Collection Provides

- `eigenstate.ipa.idm`
  Dynamic inventory for live IdM-backed infrastructure targeting.
- `eigenstate.ipa.vault`
  IdM vault retrieval, metadata inspection, scoped search, and binary-safe
  secret lookup.
- `eigenstate.ipa.keytab`
  Kerberos keytab retrieval for host and service principals via
  `ipa-getkeytab`.
- `eigenstate.ipa.cert`
  IdM CA certificate request and retrieval. Signs CSRs against service
  principals, retrieves existing certs by serial number, and finds certs by
  expiry window or principal — all via `ipalib` without certmonger.

## Best Fit

- Red Hat IdM / FreeIPA environments
- Kerberos-first automation
- Ansible Automation Platform execution environments
- teams that want to use IdM as inventory and runtime secret source

## Repository

- GitHub: [gprocunier/eigenstate-ipa](https://github.com/gprocunier/eigenstate-ipa)
- Issues: [github.com/gprocunier/eigenstate-ipa/issues](https://github.com/gprocunier/eigenstate-ipa/issues)

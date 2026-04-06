---
layout: default
title: eigenstate.ipa
description: >-
  Ansible collection for Red Hat IdM / FreeIPA with dynamic inventory,
  IdM vault lookup, Kerberos principal state, Kerberos keytab delivery,
  certificate automation, OTP workflows, IdM vault lifecycle automation,
  AAP integration, and secure secret retrieval.
---

{% raw %}

# eigenstate.ipa

`eigenstate.ipa` is an Ansible collection for Red Hat IdM / FreeIPA. It has
seven main jobs:

- dynamic inventory from IdM hosts, hostgroups, netgroups, and HBAC policy
- IdM vault lookup for Kerberos-authenticated secret retrieval in Ansible and
  AAP
- Kerberos principal state inspection for user, host, and service objects
- Kerberos keytab retrieval for host and service principals
- IdM CA certificate request, retrieval, and expiry search via the Dogtag PKI
  backend
- OTP token issue, lookup, revoke, and host enrollment password generation
- IdM vault lifecycle management for create, archive, update, and delete flows

It fits environments that already use IdM for host data, policy context, and
runtime secret retrieval.

## Current Release

- `1.5.0`
- adds `eigenstate.ipa.vault_write` to the integrated collection alongside the
  released inventory, vault, principal, keytab, cert, and OTP components
- create, archive, modify, and delete IdM vaults from Ansible
- full idempotency for standard vaults; check mode support
- delta-only member management

## Start Here

- [Collection Overview](https://github.com/gprocunier/eigenstate-ipa)
- [Documentation Map](https://gprocunier.github.io/eigenstate-ipa/documentation-map.html)
- [Inventory Plugin](./inventory-plugin.md)
- [Vault Plugin](./vault-plugin.md)
- [Vault Write Module](./vault-write-plugin.md)
- [Principal Plugin](./principal-plugin.md)
- [Keytab Plugin](./keytab-plugin.md)
- [Cert Plugin](./cert-plugin.md)
- [OTP Plugin](./otp-plugin.md)
- [Inventory Use Cases](./inventory-use-cases.md)
- [Vault Use Cases](./vault-use-cases.md)
- [Vault Write Use Cases](./vault-write-use-cases.md)
- [Principal Use Cases](./principal-use-cases.md)
- [Keytab Use Cases](./keytab-use-cases.md)
- [Cert Use Cases](./cert-use-cases.md)
- [OTP Use Cases](./otp-use-cases.md)
- [AAP Integration](./aap-integration.md)

## What The Collection Provides

- `eigenstate.ipa.idm`
  Dynamic inventory for live IdM-backed infrastructure targeting.
- `eigenstate.ipa.vault`
  IdM vault retrieval, metadata inspection, scoped search, and binary-safe
  secret lookup.
- `eigenstate.ipa.vault_write`
  IdM vault lifecycle management for create, archive, rotate, and delete
  flows from Ansible with full idempotency for standard vaults and
  check-mode support.
- `eigenstate.ipa.principal`
  Kerberos principal existence, key, lock, and last-auth inspection for user,
  host, and service principals.
- `eigenstate.ipa.keytab`
  Kerberos keytab retrieval for host and service principals via
  `ipa-getkeytab`.
- `eigenstate.ipa.cert`
  IdM CA certificate request and retrieval. Signs CSRs against service
  principals, retrieves existing certs by serial number, and finds certs by
  expiry window or principal — all via `ipalib` without certmonger.
- `eigenstate.ipa.otp`
  OTP token issue, search, inspection, revocation, and one-time host
  enrollment password generation through IdM.

## Best Fit

- Red Hat IdM / FreeIPA environments
- Kerberos-first automation
- Ansible Automation Platform execution environments
- teams that want to use IdM as inventory and runtime secret source

## Repository

- GitHub: [gprocunier/eigenstate-ipa](https://github.com/gprocunier/eigenstate-ipa)
- Issues: [github.com/gprocunier/eigenstate-ipa/issues](https://github.com/gprocunier/eigenstate-ipa/issues)

{% endraw %}

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

`eigenstate.ipa` is an Ansible collection for Red Hat IdM / FreeIPA. I use it
to treat IdM as more than an authentication service. The collection turns IdM
into a source of inventory, policy context, Kerberos material, certificate
automation, OTP state, and vault-backed secret retrieval for Ansible and AAP.

## Collection Scope

The collection covers seven main areas:

- dynamic inventory from IdM hosts, hostgroups, netgroups, and HBAC policy
- IdM vault lookup for Kerberos-authenticated secret retrieval in Ansible and AAP
- Kerberos principal state inspection for user, host, and service objects
- Kerberos keytab retrieval for host and service principals
- IdM CA certificate request, retrieval, and expiry search through the Dogtag backend
- OTP token issue, lookup, revoke, and host enrollment password generation
- IdM vault lifecycle management for create, archive, update, and delete flows

It fits environments that already use IdM for host data, policy context, and
runtime secret retrieval.

## Current Release

- `1.5.1`
- adds `eigenstate.ipa.vault_write` alongside the released inventory, vault,
  principal, keytab, cert, and OTP components
- create, archive, modify, and delete IdM vaults from Ansible
- full idempotency for standard vaults and check-mode support
- delta-only member management

## Start Here

<a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>COLLECTION OVERVIEW</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>DOCUMENTATION MAP</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

## Plugin Reference

Use these pages when you need formal option reference, auth behavior, return
data, or operation-specific details.

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>INVENTORY PLUGIN</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>VAULT PLUGIN</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html"><kbd>VAULT WRITE MODULE</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html"><kbd>PRINCIPAL PLUGIN</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>KEYTAB PLUGIN</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>CERT PLUGIN</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>OTP PLUGIN</kbd></a>

## Capability Guides

Use these pages when you are deciding which IdM boundary, retrieval path, or
automation pattern fits the problem.

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>INVENTORY CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>VAULT CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html"><kbd>VAULT WRITE CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>PRINCIPAL CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>KEYTAB CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>CERT CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html"><kbd>OTP CAPABILITIES</kbd></a>

## Use Cases

Use these when you want worked examples, role patterns, or end-to-end
playbooks.

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>INVENTORY USE CASES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>VAULT USE CASES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-use-cases.html"><kbd>VAULT WRITE USE CASES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>PRINCIPAL USE CASES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>KEYTAB USE CASES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>CERT USE CASES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html"><kbd>OTP USE CASES</kbd></a>

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
  expiry window or principal via `ipalib` without certmonger.
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

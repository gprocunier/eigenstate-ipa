---
layout: default
title: eigenstate.ipa
description: >-
  Ansible collection for Red Hat IdM / FreeIPA with dynamic inventory,
  IdM vault lookup, Kerberos principal state, Kerberos keytab delivery,
  certificate automation, OTP workflows, SELinux user map inspection,
  HBAC rule inspection and access testing, IdM vault lifecycle automation,
  AAP integration, and secure secret retrieval.
---

{% raw %}

# eigenstate.ipa

`eigenstate.ipa` is an Ansible collection for Red Hat IdM / FreeIPA. I use it
to treat IdM as more than an authentication service. The collection turns IdM
into a source of inventory, policy context, Kerberos material, certificate
automation, OTP state, and vault-backed secret retrieval for Ansible and AAP.

## Collection Scope

The collection covers nine main areas:

- dynamic inventory from IdM hosts, hostgroups, netgroups, and HBAC policy
- IdM vault lookup for Kerberos-authenticated secret retrieval in Ansible and AAP
- Kerberos principal state inspection for user, host, and service objects
- Kerberos keytab retrieval for host and service principals
- IdM CA certificate request, retrieval, and expiry search through the Dogtag backend
- OTP token issue, lookup, revoke, and host enrollment password generation
- IdM vault lifecycle management for create, archive, update, and delete flows
- SELinux user map inspection for confinement model pre-flight and audit
- HBAC rule inspection and live access testing via the FreeIPA hbactest engine

It fits environments that already use IdM for host data, policy context, and
runtime secret retrieval.

## Current Release

- `1.6.2`
- clarifies Vault/CyberArk positioning for the collection's session recording
  and rotation guidance
- keeps the primer aligned with IdM users, groups, and host-side SSSD policy
  resolution for session recording
- refreshes the docs landing pages and release references to match the updated
  comparison language

## Start Here

<a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>COLLECTION OVERVIEW</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>DOCUMENTATION MAP</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>VAULT/CYBERARK PRIMER</kbd></a>
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
<a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-plugin.html"><kbd>SELINUX MAP PLUGIN</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-plugin.html"><kbd>HBAC RULE PLUGIN</kbd></a>

## Capability Guides

Use these pages when you are deciding which IdM boundary, retrieval path, or
automation pattern fits the problem. If you are coming from HashiCorp Vault or
CyberArk, start with
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>VAULT/CYBERARK PRIMER</kbd></a>
before drilling into the rotation and plugin-specific pages.

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>INVENTORY CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>VAULT CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html"><kbd>VAULT WRITE CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>PRINCIPAL CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>KEYTAB CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>CERT CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html"><kbd>OTP CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-capabilities.html"><kbd>SELINUX MAP CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-capabilities.html"><kbd>HBAC RULE CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>ROTATION CAPABILITIES</kbd></a>

## Primer

Use this page when the first question is whether the collection can replace or
reduce a Vault or CyberArk footprint for an IdM-centric automation estate.

<a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>VAULT/CYBERARK PRIMER</kbd></a>

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
<a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-use-cases.html"><kbd>SELINUX MAP USE CASES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html"><kbd>HBAC RULE USE CASES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>ROTATION USE CASES</kbd></a>

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
- `eigenstate.ipa.selinuxmap`
  Read-only inspection of SELinux user map state from FreeIPA/IdM.
  Returns the SELinux user, enabled state, linked HBAC rule name,
  direct member lists, and description for named maps or bulk
  enumeration.
- `eigenstate.ipa.hbacrule`
  Read-only inspection of HBAC rule state and live access testing via
  the FreeIPA `hbactest` engine. Supports `show`, `find`, and `test`;
  the `test` operation invokes the same evaluation logic SSSD uses at
  login and returns `denied`, `matched`, and `notmatched`.

## Best Fit

- Red Hat IdM / FreeIPA environments
- Kerberos-first automation
- Ansible Automation Platform execution environments
- teams that want to use IdM as inventory and runtime secret source

## Repository

- GitHub: [gprocunier/eigenstate-ipa](https://github.com/gprocunier/eigenstate-ipa)
- Issues: [github.com/gprocunier/eigenstate-ipa/issues](https://github.com/gprocunier/eigenstate-ipa/issues)

{% endraw %}

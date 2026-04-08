---
layout: default
title: Documentation Map
description: >-
  Navigation map for the eigenstate.ipa documentation set, organized by
  reading intent, workflow area, and document type rather than a flat list of
  pages.
---

{% raw %}

# Documentation Map

Use this page when you know the kind of problem you are solving but do not yet
know which document is the right starting point.

Current release: `1.6.4`

## Start Here

<a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>TOP README</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/"><kbd>DOCS HOME</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>VAULT/CYBERARK PRIMER</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

## How To Use This Docs Set

- open a plugin reference when you need exact option names, auth behavior, or return data
- open a capabilities guide when you are deciding whether a collection boundary fits the problem
- open a use-case guide when you want a playbook pattern or worked example
- open the Vault/CyberArk primer when you are translating external secrets or PAM expectations into the collection's IdM-native model
- open the AAP guide when the workflow runs in Controller or an execution environment

## Common Starting Points

### I am new to the collection

- start with <a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>TOP README</kbd></a>
- then read <a href="https://gprocunier.github.io/eigenstate-ipa/"><kbd>DOCS HOME</kbd></a>
- use this page to choose the first capability or plugin area you actually need

### I use Vault or CyberArk today

- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>VAULT/CYBERARK PRIMER</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>ROTATION CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

This path explains where the collection overlaps with external secrets or PAM
platforms, where AAP helps, and where the boundary remains static-secret and
IdM-native rather than lease-based.

### I need exact module or lookup syntax

- go straight to the plugin reference pages listed under [Reference By Area](#reference-by-area)

## Choose By Problem

### Inventory and targeting

Use this when the problem is host discovery, grouping, or policy-driven target
selection.

- <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>INVENTORY PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>INVENTORY CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>INVENTORY USE CASES</kbd></a>

### Vault retrieval and secret lifecycle

Use this when the problem is reading from IdM vaults, managing vault contents,
or understanding how static secret workflows fit compared to Vault or CyberArk.

- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>VAULT PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>VAULT CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>VAULT USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html"><kbd>VAULT WRITE MODULE</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html"><kbd>VAULT WRITE CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-use-cases.html"><kbd>VAULT WRITE USE CASES</kbd></a>

### Rotation and external-platform positioning

Use this when the question is not just how to call one plugin, but how the
collection handles rotation, controller scheduling, or comparison against
HashiCorp Vault and CyberArk.

- <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>ROTATION CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>ROTATION USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>VAULT/CYBERARK PRIMER</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

### Kerberos, certificates, and identity pre-flight

Use this when the workflow depends on principal state, keytabs, or IdM CA
certificate operations.

- <a href="https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html"><kbd>PRINCIPAL PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>PRINCIPAL CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>PRINCIPAL USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>KEYTAB PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>KEYTAB CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>KEYTAB USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>CERT PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>CERT CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>CERT USE CASES</kbd></a>

### OTP, SELinux, and access policy validation

Use this when the workflow is about MFA and enrollment bootstrap, SELinux user
maps, or HBAC access decisions.

- <a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>OTP PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html"><kbd>OTP CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html"><kbd>OTP USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-plugin.html"><kbd>SELINUX MAP PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-capabilities.html"><kbd>SELINUX MAP CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-use-cases.html"><kbd>SELINUX MAP USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-plugin.html"><kbd>HBAC RULE PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-capabilities.html"><kbd>HBAC RULE CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html"><kbd>HBAC RULE USE CASES</kbd></a>

## Reference By Area

| Area | Reference | Capability guide | Use cases |
| --- | --- | --- | --- |
| Inventory | [Inventory Plugin](https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html) | [Inventory Capabilities](https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html) | [Inventory Use Cases](https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html) |
| Vault retrieval | [Vault Plugin](https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html) | [Vault Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html) | [Vault Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html) |
| Vault lifecycle | [Vault Write Module](https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html) | [Vault Write Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html) | [Vault Write Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-write-use-cases.html) |
| Principal state | [Principal Plugin](https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html) | [Principal Capabilities](https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html) | [Principal Use Cases](https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html) |
| Keytabs | [Keytab Plugin](https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html) | [Keytab Capabilities](https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html) | [Keytab Use Cases](https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html) |
| Certificates | [Cert Plugin](https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html) | [Cert Capabilities](https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html) | [Cert Use Cases](https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html) |
| OTP | [OTP Plugin](https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html) | [OTP Capabilities](https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html) | [OTP Use Cases](https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html) |
| SELinux maps | [SELinux Map Plugin](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-plugin.html) | [SELinux Map Capabilities](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-capabilities.html) | [SELinux Map Use Cases](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-use-cases.html) |
| HBAC rules | [HBAC Rule Plugin](https://gprocunier.github.io/eigenstate-ipa/hbacrule-plugin.html) | [HBAC Rule Capabilities](https://gprocunier.github.io/eigenstate-ipa/hbacrule-capabilities.html) | [HBAC Rule Use Cases](https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html) |

## Collection-Wide Guides

| Document | Purpose |
| --- | --- |
| [Rotation Capabilities](https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html) | Collection-wide rotation model for static secrets, keytabs, and certificates |
| [Rotation Use Cases](https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html) | Controller-side rotation workflows built from the collection primitives |
| [Vault/CyberArk Primer](https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html) | Positioning guide for Vault and CyberArk users evaluating the collection |
| [AAP Integration](https://gprocunier.github.io/eigenstate-ipa/aap-integration.html) | Execution environment and controller integration patterns |
| [Top README](https://github.com/gprocunier/eigenstate-ipa) | Collection overview, install, and repository framing |

## Suggested Reading Order

1. <a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>TOP README</kbd></a>
2. <a href="https://gprocunier.github.io/eigenstate-ipa/"><kbd>DOCS HOME</kbd></a>
3. choose one problem area from [Choose By Problem](#choose-by-problem)
4. read the capability guide before the use-case guide when you are still deciding approach
5. read the plugin reference last when you need exact lookup, module, or return-field detail

{% endraw %}

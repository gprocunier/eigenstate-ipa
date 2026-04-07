---
layout: default
title: Documentation Map
---

{% raw %}

# Documentation Map

This page is the entry point to the docs set. Use it when you know the kind of
problem you are solving, but you do not yet know which document is the right
one to open.

## Start Here

<a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>TOP README</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/"><kbd>DOCS HOME</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

Use this page as the navigation layer for the docs set:

- start with plugin reference when you need option or auth behavior
- use capability guides when you are choosing an IdM boundary or retrieval model
- use use-case guides when you want concrete inventory or playbook patterns
- use the AAP guide when the job runs inside Controller or an execution environment

## Choose Your Path

### I want to build dynamic inventory from IdM

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>INVENTORY PLUGIN</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>INVENTORY CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>INVENTORY USE CASES</kbd></a>

- option reference and authentication behavior
- object-model guidance for hosts, hostgroups, netgroups, and HBAC
- worked scenarios such as compliance scans, role targeting, and policy audits

### I want to retrieve secrets from IdM vaults

<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>VAULT PLUGIN</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>VAULT CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>VAULT USE CASES</kbd></a>

- vault type behavior and lookup options
- scope and retrieval-form guidance
- examples for passwords, API keys, certs, and binary artifacts

### I want to create, archive, or rotate secrets in IdM vaults

<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html"><kbd>VAULT WRITE MODULE</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html"><kbd>VAULT WRITE CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-use-cases.html"><kbd>VAULT WRITE USE CASES</kbd></a>

- create, archive, modify, and delete flows
- symmetric and asymmetric vault creation
- delegated access and member management
- idempotency and check-mode behavior

### I want to check principal state before keytab or cert operations

<a href="https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html"><kbd>PRINCIPAL PLUGIN</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>PRINCIPAL CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>PRINCIPAL USE CASES</kbd></a>

- pre-flight checks before keytab issue or cert request
- host enrollment confirmation
- user account lock and last-auth inspection
- bulk principal audit workflows

### I want to retrieve Kerberos keytabs from IdM

<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>KEYTAB PLUGIN</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>KEYTAB CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>KEYTAB USE CASES</kbd></a>

- keytab retrieval options and auth behavior
- retrieve vs generate modes and rotation risk
- deployment examples for host and service principals

### I want to request or manage certificates from IdM CA

<a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>CERT PLUGIN</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>CERT CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>CERT USE CASES</kbd></a>

- request, retrieve, or find certificate flows
- CSR input behavior and result shapes
- expiry-window maintenance and delivery patterns

### I want to issue OTP tokens or host enrollment passwords

<a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>OTP PLUGIN</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html"><kbd>OTP CAPABILITIES</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html"><kbd>OTP USE CASES</kbd></a>

- MFA token issue, search, inspection, and revoke flows
- host enrollment password generation
- guidance on treating OTP URIs and enrollment passwords as sensitive material

### I want to run this in Automation Controller / AAP

<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

- execution environment dependencies
- password vs keytab auth guidance
- inventory source and credential-source wiring patterns

## Document Intent

| Document | Purpose |
| --- | --- |
| [Top README](../README.md) | Collection overview, install, and project framing |
| [Inventory Plugin](./inventory-plugin.md) | Formal reference for `eigenstate.ipa.idm` |
| [Vault Plugin](./vault-plugin.md) | Formal reference for `eigenstate.ipa.vault` |
| [Vault Write Module](./vault-write-plugin.md) | Formal reference for `eigenstate.ipa.vault_write` |
| [Principal Plugin](./principal-plugin.md) | Formal reference for `eigenstate.ipa.principal` |
| [Keytab Plugin](./keytab-plugin.md) | Formal reference for `eigenstate.ipa.keytab` |
| [Cert Plugin](./cert-plugin.md) | Formal reference for `eigenstate.ipa.cert` |
| [OTP Plugin](./otp-plugin.md) | Formal reference for `eigenstate.ipa.otp` |
| [Inventory Capabilities](./inventory-capabilities.md) | Scenario-driven guidance for inventory use cases |
| [Vault Capabilities](./vault-capabilities.md) | Scenario-driven guidance for vault retrieval use cases |
| [Vault Write Capabilities](./vault-write-capabilities.md) | Vault type matrix, idempotency guarantees, and rotation patterns |
| [Principal Capabilities](./principal-capabilities.md) | Scenario-driven guidance for principal-state lookup workflows |
| [Keytab Capabilities](./keytab-capabilities.md) | Scenario-driven guidance for Kerberos keytab deployment |
| [Cert Capabilities](./cert-capabilities.md) | Scenario-driven guidance for IdM CA certificate workflows |
| [OTP Capabilities](./otp-capabilities.md) | Scenario-driven guidance for OTP token and host enrollment workflows |
| [Inventory Use Cases](./inventory-use-cases.md) | Detailed worked examples for inventory-backed automation |
| [Vault Use Cases](./vault-use-cases.md) | Detailed worked examples for vault-backed secret retrieval |
| [Vault Write Use Cases](./vault-write-use-cases.md) | Detailed worked examples for vault lifecycle automation |
| [Principal Use Cases](./principal-use-cases.md) | Detailed worked examples for principal pre-flight and audit workflows |
| [Keytab Use Cases](./keytab-use-cases.md) | Detailed worked examples for keytab retrieval and deployment |
| [Cert Use Cases](./cert-use-cases.md) | Detailed worked examples for certificate issuance, retrieval, and expiry audits |
| [OTP Use Cases](./otp-use-cases.md) | Detailed worked examples for OTP issue, rotation, inspection, and host enrollment |
| [AAP Integration](./aap-integration.md) | Execution environment and controller integration patterns |

## Recommended Reading Order

1. <a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>TOP README</kbd></a>
2. <a href="https://gprocunier.github.io/eigenstate-ipa/"><kbd>DOCS HOME</kbd></a>
3. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>INVENTORY PLUGIN</kbd></a>
4. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>VAULT PLUGIN</kbd></a>
5. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html"><kbd>VAULT WRITE MODULE</kbd></a>
6. <a href="https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html"><kbd>PRINCIPAL PLUGIN</kbd></a>
7. <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>KEYTAB PLUGIN</kbd></a>
8. <a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>CERT PLUGIN</kbd></a>
9. <a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>OTP PLUGIN</kbd></a>

{% endraw %}

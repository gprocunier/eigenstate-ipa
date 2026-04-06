---
layout: default
title: Documentation Map
description: >-
  Navigation map for the eigenstate.ipa documentation set, including
  inventory, IdM vault, keytab, cert, use cases, and AAP integration guidance.
---

# Documentation Map

Start with the navigation buttons below. They are the quickest way to get to
the part of the collection you actually need.

Current release: `1.2.0`

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>&nbsp;&nbsp;INVENTORY PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>&nbsp;&nbsp;IDM VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>&nbsp;&nbsp;KEYTAB PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>&nbsp;&nbsp;IDM CERT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>&nbsp;&nbsp;INVENTORY CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>&nbsp;&nbsp;IDM VAULT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>&nbsp;&nbsp;KEYTAB CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>&nbsp;&nbsp;IDM CERT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>&nbsp;&nbsp;INVENTORY USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>&nbsp;&nbsp;IDM VAULT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>&nbsp;&nbsp;KEYTAB USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>&nbsp;&nbsp;IDM CERT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>
<a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>&nbsp;&nbsp;TOP README&nbsp;&nbsp;</kbd></a>

Use this page as the entry point to the docs set:

- start with the plugin reference when you need option or auth behavior
- use the capability guides when you are choosing an IdM boundary or vault scope
- use the use-case guides when you want concrete inventory or playbook patterns
- use the AAP guide when the job runs inside Controller or an execution environment

## Choose Your Path

### I Want To Build Dynamic Inventory From IdM

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>&nbsp;&nbsp;INVENTORY PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>&nbsp;&nbsp;INVENTORY CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>&nbsp;&nbsp;INVENTORY USE CASES&nbsp;&nbsp;</kbd></a>

Use these when you need:

- option reference and authentication behavior
- conceptual explanation of which IdM object type matches which automation boundary
- group-building rules for hosts, hostgroups, netgroups, and HBAC rules
- worked scenarios such as compliance scans, role targeting, and policy audits

### I Want To Retrieve Secrets From IdM Vaults

<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>&nbsp;&nbsp;IDM VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>&nbsp;&nbsp;IDM VAULT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>&nbsp;&nbsp;IDM VAULT USE CASES&nbsp;&nbsp;</kbd></a>

Use these when you need:

- vault type behavior and lookup options
- conceptual explanation of vault scope and retrieval form
- metadata inspection and scope search behavior
- examples for passwords, API keys, certificates, and binary artifacts
- guidance on user, service, and shared vault scopes

### I Want To Retrieve Kerberos Keytabs From IdM

<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>&nbsp;&nbsp;KEYTAB PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>&nbsp;&nbsp;KEYTAB CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>&nbsp;&nbsp;KEYTAB USE CASES&nbsp;&nbsp;</kbd></a>

Use these when you need:

- keytab retrieval options and auth behavior
- explanation of retrieve vs generate modes and key rotation risk
- encryption type selection
- examples for deploying keytabs to HTTP, NFS, and host principals
- worked playbook patterns for new service onboarding, fleet deployment, rotation, and vault-gated bootstrap

### I Want To Request Or Manage Certificates From IdM CA

<a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>&nbsp;&nbsp;IDM CERT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>&nbsp;&nbsp;IDM CERT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>&nbsp;&nbsp;IDM CERT USE CASES&nbsp;&nbsp;</kbd></a>

Use these when you need:

- cert operations: request, retrieve, or find
- CSR input formats and per-operation parameters
- result shapes and cert metadata fields
- pre-expiry maintenance workflows and expiry window searches
- cert plus private key bundle delivery patterns
- worked playbook examples for service cert issuance, renewal, and audit

### I Want To Run This In Automation Controller / AAP

<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>

Use this when you need:

- execution environment dependencies
- password versus keytab auth guidance
- inventory source and credential-source wiring patterns

### I Want The High-Level Project View

<a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>&nbsp;&nbsp;TOP README&nbsp;&nbsp;</kbd></a>

The top README covers collection scope, installation, and repository layout.

## Document Intent

| Document | Purpose |
| --- | --- |
| [Top README](https://github.com/gprocunier/eigenstate-ipa) | Collection overview, install, project framing |
| [Inventory Plugin](https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html) | Formal reference for `eigenstate.ipa.idm` |
| [Vault Plugin](https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html) | Formal reference for `eigenstate.ipa.vault` |
| [Keytab Plugin](https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html) | Formal reference for `eigenstate.ipa.keytab` |
| [Cert Plugin](https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html) | Formal reference for `eigenstate.ipa.cert` |
| [Inventory Capabilities](https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html) | Scenario-driven guidance for inventory use cases |
| [Vault Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html) | Scenario-driven guidance for vault retrieval use cases |
| [Keytab Capabilities](https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html) | Scenario-driven guidance for keytab retrieval and deployment |
| [Cert Capabilities](https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html) | Scenario-driven guidance for cert request, retrieve, and find |
| [Inventory Use Cases](https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html) | Detailed worked examples for inventory-backed automation |
| [Vault Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html) | Detailed worked examples for vault-backed secret retrieval |
| [Keytab Use Cases](https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html) | Detailed worked examples for keytab retrieval and deployment |
| [Cert Use Cases](https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html) | Detailed worked examples for cert issuance, renewal, and expiry audit |
| [AAP Integration](https://gprocunier.github.io/eigenstate-ipa/aap-integration.html) | Execution environment and controller integration patterns |

## Recommended Reading Order

1. <a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>TOP README</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>INVENTORY PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>IDM VAULT PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>KEYTAB PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>IDM CERT PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>INVENTORY CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>IDM VAULT CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>KEYTAB CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>IDM CERT CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>INVENTORY USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>IDM VAULT USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>KEYTAB USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>IDM CERT USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

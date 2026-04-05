---
layout: default
title: Documentation Map
description: >-
  Navigation map for the eigenstate.ipa documentation set, including
  inventory, IdM vault, use cases, and AAP integration guidance.
---

# Documentation Map

Start with the navigation buttons below. They are the quickest way to get to
the part of the collection you actually need.

Current release: `1.2.0`

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>&nbsp;&nbsp;INVENTORY PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>&nbsp;&nbsp;IDM VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html"><kbd>&nbsp;&nbsp;PRINCIPAL PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>&nbsp;&nbsp;INVENTORY CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>&nbsp;&nbsp;IDM VAULT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>&nbsp;&nbsp;PRINCIPAL CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>&nbsp;&nbsp;INVENTORY USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>&nbsp;&nbsp;IDM VAULT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>&nbsp;&nbsp;PRINCIPAL USE CASES&nbsp;&nbsp;</kbd></a>
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

### I Want To Check Principal State Before Keytab Or Cert Operations

<a href="https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html"><kbd>&nbsp;&nbsp;PRINCIPAL PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>&nbsp;&nbsp;PRINCIPAL CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>&nbsp;&nbsp;PRINCIPAL USE CASES&nbsp;&nbsp;</kbd></a>

Use these when you need:

- pre-flight checks before keytab issuance or cert requests
- confirmation that a host is enrolled in IdM before automation proceeds
- user account lock and last-auth state inspection
- bulk audits of all service or host principals for missing keys
- pipeline gates that abort when a required principal is absent or unkeyed

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
| [Principal Plugin](https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html) | Formal reference for `eigenstate.ipa.principal` |
| [Inventory Capabilities](https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html) | Scenario-driven guidance for inventory use cases |
| [Vault Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html) | Scenario-driven guidance for vault retrieval use cases |
| [Principal Capabilities](https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html) | Scenario-driven guidance for principal state lookup patterns |
| [Inventory Use Cases](https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html) | Detailed worked examples for inventory-backed automation |
| [Vault Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html) | Detailed worked examples for vault-backed secret retrieval |
| [Principal Use Cases](https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html) | Detailed worked examples for principal state pre-flight checks |
| [AAP Integration](https://gprocunier.github.io/eigenstate-ipa/aap-integration.html) | Execution environment and controller integration patterns |

## Recommended Reading Order

1. <a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>TOP README</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>INVENTORY PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>IDM VAULT PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html"><kbd>PRINCIPAL PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>INVENTORY CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>IDM VAULT CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>PRINCIPAL CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>INVENTORY USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>IDM VAULT USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>PRINCIPAL USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

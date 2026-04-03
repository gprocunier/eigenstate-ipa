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

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>&nbsp;&nbsp;INVENTORY PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>&nbsp;&nbsp;IDM VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>&nbsp;&nbsp;INVENTORY CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>&nbsp;&nbsp;IDM VAULT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>&nbsp;&nbsp;INVENTORY USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>&nbsp;&nbsp;IDM VAULT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>
<a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>&nbsp;&nbsp;TOP README&nbsp;&nbsp;</kbd></a>

The root `README.md` explains what the collection is. This page answers:

- where to start for a specific automation goal
- which docs explain operator usage versus plugin behavior versus AAP wiring
- how the collection documentation is intentionally split

## Choose Your Path

### I Want To Build Dynamic Inventory From IdM

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>&nbsp;&nbsp;INVENTORY PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>&nbsp;&nbsp;INVENTORY CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>&nbsp;&nbsp;INVENTORY USE CASES&nbsp;&nbsp;</kbd></a>

Pick these when you need:

- option reference and authentication behavior
- conceptual explanation of which IdM object type matches which automation boundary
- group-building rules for hosts, hostgroups, netgroups, and HBAC rules
- real operator scenarios such as compliance scans, role targeting, and policy audits

### I Want To Retrieve Secrets From IdM Vaults

<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>&nbsp;&nbsp;IDM VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>&nbsp;&nbsp;IDM VAULT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>&nbsp;&nbsp;IDM VAULT USE CASES&nbsp;&nbsp;</kbd></a>

Pick these when you need:

- vault type behavior and lookup options
- conceptual explanation of vault scope and retrieval form
- metadata inspection and scope search behavior
- examples for passwords, API keys, certificates, and binary artifacts
- guidance on user, service, and shared vault scopes

### I Want To Run This In Automation Controller / AAP

<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>

Pick this when you need:

- execution environment dependencies
- password versus keytab auth guidance
- inventory source and credential-source wiring patterns

### I Want The High-Level Project View

<a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>&nbsp;&nbsp;TOP README&nbsp;&nbsp;</kbd></a>

The top README gives the collection purpose, plugin map, install entrypoint, and
repo-level layout.

## Document Intent

| Document | Purpose |
| --- | --- |
| [Top README](https://github.com/gprocunier/eigenstate-ipa) | Collection overview, install, project framing |
| [Inventory Plugin](https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html) | Formal reference for `eigenstate.ipa.idm` |
| [Vault Plugin](https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html) | Formal reference for `eigenstate.ipa.vault` |
| [Inventory Capabilities](https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html) | Scenario-driven guidance for inventory use cases |
| [Vault Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html) | Scenario-driven guidance for vault retrieval use cases |
| [Inventory Use Cases](https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html) | Detailed worked examples for inventory-backed automation |
| [Vault Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html) | Detailed worked examples for vault-backed secret retrieval |
| [AAP Integration](https://gprocunier.github.io/eigenstate-ipa/aap-integration.html) | Execution environment and controller integration patterns |

## Recommended Reading Order

1. <a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>TOP README</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>INVENTORY PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>IDM VAULT PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>INVENTORY CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>IDM VAULT CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>INVENTORY USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>IDM VAULT USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

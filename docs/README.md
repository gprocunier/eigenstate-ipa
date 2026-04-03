# Documentation Map

Start with the navigation buttons below. They are the quickest way to get to
the part of the collection you actually need.

<a href="./inventory-plugin.md"><kbd>&nbsp;&nbsp;INVENTORY PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="./vault-plugin.md"><kbd>&nbsp;&nbsp;VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="./inventory-capabilities.md"><kbd>&nbsp;&nbsp;INVENTORY CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="./vault-capabilities.md"><kbd>&nbsp;&nbsp;VAULT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="./inventory-use-cases.md"><kbd>&nbsp;&nbsp;INVENTORY USE CASES&nbsp;&nbsp;</kbd></a>
<a href="./vault-use-cases.md"><kbd>&nbsp;&nbsp;VAULT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="./aap-integration.md"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>
<a href="../README.md"><kbd>&nbsp;&nbsp;TOP README&nbsp;&nbsp;</kbd></a>

The root `README.md` explains what the collection is. This page answers:

- where to start for a specific automation goal
- which docs explain operator usage versus plugin behavior versus AAP wiring
- how the collection documentation is intentionally split

## Choose Your Path

### I Want To Build Dynamic Inventory From IdM

<a href="./inventory-plugin.md"><kbd>&nbsp;&nbsp;INVENTORY PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="./inventory-capabilities.md"><kbd>&nbsp;&nbsp;INVENTORY CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="./inventory-use-cases.md"><kbd>&nbsp;&nbsp;INVENTORY USE CASES&nbsp;&nbsp;</kbd></a>

Pick these when you need:

- option reference and authentication behavior
- conceptual explanation of which IdM object type matches which automation boundary
- group-building rules for hosts, hostgroups, netgroups, and HBAC rules
- real operator scenarios such as compliance scans, role targeting, and policy audits

### I Want To Retrieve Secrets From IdM Vaults

<a href="./vault-plugin.md"><kbd>&nbsp;&nbsp;VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="./vault-capabilities.md"><kbd>&nbsp;&nbsp;VAULT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="./vault-use-cases.md"><kbd>&nbsp;&nbsp;VAULT USE CASES&nbsp;&nbsp;</kbd></a>

Pick these when you need:

- vault type behavior and lookup options
- conceptual explanation of vault scope and retrieval form
- metadata inspection and scope search behavior
- examples for passwords, API keys, certificates, and binary artifacts
- guidance on user, service, and shared vault scopes

### I Want To Run This In Automation Controller / AAP

<a href="./aap-integration.md"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>

Pick this when you need:

- execution environment dependencies
- password versus keytab auth guidance
- inventory source and credential-source wiring patterns

### I Want The High-Level Project View

<a href="../README.md"><kbd>&nbsp;&nbsp;TOP README&nbsp;&nbsp;</kbd></a>

The top README gives the collection purpose, plugin map, install entrypoint, and
repo-level layout.

## Document Intent

| Document | Purpose |
| --- | --- |
| [Top README](../README.md) | Collection overview, install, project framing |
| [Inventory Plugin](./inventory-plugin.md) | Formal reference for `eigenstate.ipa.idm` |
| [Vault Plugin](./vault-plugin.md) | Formal reference for `eigenstate.ipa.vault` |
| [Inventory Capabilities](./inventory-capabilities.md) | Scenario-driven guidance for inventory use cases |
| [Vault Capabilities](./vault-capabilities.md) | Scenario-driven guidance for vault retrieval use cases |
| [Inventory Use Cases](./inventory-use-cases.md) | Detailed worked examples for inventory-backed automation |
| [Vault Use Cases](./vault-use-cases.md) | Detailed worked examples for vault-backed secret retrieval |
| [AAP Integration](./aap-integration.md) | Execution environment and controller integration patterns |

## Recommended Reading Order

1. <a href="../README.md"><kbd>TOP README</kbd></a>
1. <a href="./inventory-plugin.md"><kbd>INVENTORY PLUGIN</kbd></a>
1. <a href="./vault-plugin.md"><kbd>VAULT PLUGIN</kbd></a>
1. <a href="./inventory-capabilities.md"><kbd>INVENTORY CAPABILITIES</kbd></a>
1. <a href="./vault-capabilities.md"><kbd>VAULT CAPABILITIES</kbd></a>
1. <a href="./inventory-use-cases.md"><kbd>INVENTORY USE CASES</kbd></a>
1. <a href="./vault-use-cases.md"><kbd>VAULT USE CASES</kbd></a>
1. <a href="./aap-integration.md"><kbd>AAP INTEGRATION</kbd></a>

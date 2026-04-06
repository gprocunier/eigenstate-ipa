# Documentation Map

Start with the navigation buttons below. They are the quickest way to get to
the part of the collection you actually need.

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>&nbsp;&nbsp;INVENTORY PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>&nbsp;&nbsp;IDM VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html"><kbd>&nbsp;&nbsp;PRINCIPAL PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>&nbsp;&nbsp;KEYTAB PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>&nbsp;&nbsp;IDM CERT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>&nbsp;&nbsp;OTP PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>&nbsp;&nbsp;INVENTORY CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>&nbsp;&nbsp;IDM VAULT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>&nbsp;&nbsp;PRINCIPAL CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>&nbsp;&nbsp;KEYTAB CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>&nbsp;&nbsp;IDM CERT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html"><kbd>&nbsp;&nbsp;OTP CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>&nbsp;&nbsp;INVENTORY USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>&nbsp;&nbsp;IDM VAULT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>&nbsp;&nbsp;PRINCIPAL USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>&nbsp;&nbsp;KEYTAB USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>&nbsp;&nbsp;IDM CERT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html"><kbd>&nbsp;&nbsp;OTP USE CASES&nbsp;&nbsp;</kbd></a>
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
- host enrollment confirmation before automation proceeds
- user account lock and last-auth inspection
- bulk audits of principals missing key material

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

### I Want To Issue OTP Tokens Or Host Enrollment Passwords

<a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>&nbsp;&nbsp;OTP PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html"><kbd>&nbsp;&nbsp;OTP CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html"><kbd>&nbsp;&nbsp;OTP USE CASES&nbsp;&nbsp;</kbd></a>

Use these when you need:

- user MFA token creation through IdM-managed TOTP or HOTP records
- host enrollment password generation for first-use IPA client install flows
- token search, inspection, and revocation patterns
- guidance on treating OTP URIs and enrollment passwords as sensitive material

### I Want The High-Level Project View

<a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>&nbsp;&nbsp;TOP README&nbsp;&nbsp;</kbd></a>

The top README covers collection scope, installation, and repository layout.

## Document Intent

| Document | Purpose |
| --- | --- |
| [Top README](../README.md) | Collection overview, install, project framing |
| [Inventory Plugin](./inventory-plugin.md) | Formal reference for `eigenstate.ipa.idm` |
| [Vault Plugin](./vault-plugin.md) | Formal reference for `eigenstate.ipa.vault` |
| [Principal Plugin](./principal-plugin.md) | Formal reference for `eigenstate.ipa.principal` |
| [Keytab Plugin](./keytab-plugin.md) | Formal reference for `eigenstate.ipa.keytab` |
| [Cert Plugin](./cert-plugin.md) | Formal reference for `eigenstate.ipa.cert` |
| [OTP Plugin](./otp-plugin.md) | Formal reference for `eigenstate.ipa.otp` |
| [Inventory Capabilities](./inventory-capabilities.md) | Scenario-driven guidance for inventory use cases |
| [Vault Capabilities](./vault-capabilities.md) | Scenario-driven guidance for vault retrieval use cases |
| [Principal Capabilities](./principal-capabilities.md) | Scenario-driven guidance for principal-state lookup workflows |
| [Keytab Capabilities](./keytab-capabilities.md) | Scenario-driven guidance for Kerberos keytab deployment |
| [Cert Capabilities](./cert-capabilities.md) | Scenario-driven guidance for IdM CA certificate workflows |
| [OTP Capabilities](./otp-capabilities.md) | Scenario-driven guidance for OTP token and host enrollment workflows |
| [Inventory Use Cases](./inventory-use-cases.md) | Detailed worked examples for inventory-backed automation |
| [Vault Use Cases](./vault-use-cases.md) | Detailed worked examples for vault-backed secret retrieval |
| [Principal Use Cases](./principal-use-cases.md) | Detailed worked examples for principal pre-flight and audit workflows |
| [Keytab Use Cases](./keytab-use-cases.md) | Detailed worked examples for keytab retrieval and deployment |
| [Cert Use Cases](./cert-use-cases.md) | Detailed worked examples for certificate issuance, retrieval, and expiry audits |
| [OTP Use Cases](./otp-use-cases.md) | Detailed worked examples for OTP issue, rotation, inspection, and host enrollment |
| [AAP Integration](./aap-integration.md) | Execution environment and controller integration patterns |

## Recommended Reading Order

1. <a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>TOP README</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>INVENTORY PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>IDM VAULT PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html"><kbd>PRINCIPAL PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>KEYTAB PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>IDM CERT PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>OTP PLUGIN</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>INVENTORY CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>IDM VAULT CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>PRINCIPAL CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>KEYTAB CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>IDM CERT CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html"><kbd>OTP CAPABILITIES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>INVENTORY USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>IDM VAULT USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>PRINCIPAL USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>KEYTAB USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>IDM CERT USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html"><kbd>OTP USE CASES</kbd></a>
1. <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

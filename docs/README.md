---
layout: default
title: Docs README
description: >-
  Short compatibility landing page for readers who arrive at the docs folder in
  the repository rather than through the published site.
---

{% raw %}

# Docs README

This directory contains the published documentation for `eigenstate.ipa`.

Use these entry points instead of reading the files as a flat list:

- <a href="https://gprocunier.github.io/eigenstate-ipa/"><kbd>DOCS HOME</kbd></a>
  for the collection overview and plugin-family index
- <a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>DOCUMENTATION MAP</kbd></a>
  for reading order and problem-based navigation
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>VAULT/CYBERARK PRIMER</kbd></a>
  if you are comparing the collection to Vault or CyberArk
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html"><kbd>OPENSHIFT ECOSYSTEM PRIMER</kbd></a>
  if OpenShift uses Keycloak and IdM-backed trust and you want the surrounding workflow model
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-keycloak-idm-reference.html"><kbd>OPENSHIFT IDENTITY REFERENCE</kbd></a>
  if you need the preferred IdM, Keycloak, OIDC, RBAC, and breakglass boundary
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-identity-validation-walkthrough.html"><kbd>OPENSHIFT IDENTITY VALIDATION</kbd></a>
  if you want render-only and validation-only OpenShift identity reports
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-breakglass-validation.html"><kbd>OPENSHIFT BREAKGLASS VALIDATION</kbd></a>
  if emergency access evidence and RBAC bindings are the review target
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-ldap-fallback.html"><kbd>OPENSHIFT LDAP FALLBACK</kbd></a>
  if direct LDAP is required as a documented exception
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-use-cases.html"><kbd>OPENSHIFT RHOSO USE CASES</kbd></a>
  if RHOSO cloud-operator or tenant identity boundaries are part of the workflow
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhacm-use-cases.html"><kbd>OPENSHIFT RHACM USE CASES</kbd></a>
  if RHACM is the event source for policy or lifecycle automation
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhacs-use-cases.html"><kbd>OPENSHIFT RHACS USE CASES</kbd></a>
  if RHACS findings or enforcement need an identity-aware response path
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-quay-use-cases.html"><kbd>OPENSHIFT QUAY USE CASES</kbd></a>
  if Quay workflows need cleaner identity, mirroring, and repository-event automation
- <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>
  if the workflow runs in Controller or an execution environment
- <a href="https://gprocunier.github.io/eigenstate-ipa/aap-ee-quickstart.html"><kbd>AAP EE QUICKSTART</kbd></a>
  if you need the ready-to-build execution environment path first
- <a href="https://gprocunier.github.io/eigenstate-ipa/aap-golden-path-roles.html"><kbd>AAP GOLDEN PATH ROLES</kbd></a>
  if you want packaged AAP workflow roles after the EE is available
- <a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>EPHEMERAL ACCESS CAPABILITIES</kbd></a>
  if the question is temporary access or lease-like behavior inside IdM
- <a href="https://gprocunier.github.io/eigenstate-ipa/compatibility-policy.html"><kbd>COMPATIBILITY POLICY</kbd></a>
  if you are choosing between lookup compatibility and explicit module surfaces
- <a href="https://gprocunier.github.io/eigenstate-ipa/mutation-surface-migration.html"><kbd>MUTATION SURFACE MIGRATION</kbd></a>
  if you are moving side-effecting keytab or certificate workflows to modules

## Plugin Families

| Area | Reference | Capabilities | Use cases |
| --- | --- | --- | --- |
| Inventory | [Inventory Plugin](https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html) | [Inventory Capabilities](https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html) | [Inventory Use Cases](https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html) |
| Vault retrieval | [Vault Plugin](https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html) | [Vault Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html) | [Vault Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html) |
| Vault lifecycle | [Vault Write Module](https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html) | [Vault Write Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html) | [Vault Write Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-write-use-cases.html) |
| Principal state | [Principal Plugin](https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html) | [Principal Capabilities](https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html) | [Principal Use Cases](https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html) |
| Keytabs | [Keytab Plugin](https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html) | [Keytab Capabilities](https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html) | [Keytab Use Cases](https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html) |
| Keytab management | [Keytab Manage Module](https://gprocunier.github.io/eigenstate-ipa/keytab-manage-module.html) | [Compatibility Policy](https://gprocunier.github.io/eigenstate-ipa/compatibility-policy.html) | [Mutation Surface Migration](https://gprocunier.github.io/eigenstate-ipa/mutation-surface-migration.html) |
| User lease | [User Lease Module](https://gprocunier.github.io/eigenstate-ipa/user-lease-plugin.html) | [User Lease Capabilities](https://gprocunier.github.io/eigenstate-ipa/user-lease-capabilities.html) | [User Lease Use Cases](https://gprocunier.github.io/eigenstate-ipa/user-lease-use-cases.html) |
| Certificates | [Cert Plugin](https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html) | [Cert Capabilities](https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html) | [Cert Use Cases](https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html) |
| Certificate request | [Cert Request Module](https://gprocunier.github.io/eigenstate-ipa/cert-request-module.html) | [Compatibility Policy](https://gprocunier.github.io/eigenstate-ipa/compatibility-policy.html) | [Mutation Surface Migration](https://gprocunier.github.io/eigenstate-ipa/mutation-surface-migration.html) |
| OTP | [OTP Plugin](https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html) | [OTP Capabilities](https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html) | [OTP Use Cases](https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html) |
| DNS | [DNS Plugin](https://gprocunier.github.io/eigenstate-ipa/dns-plugin.html) | [DNS Capabilities](https://gprocunier.github.io/eigenstate-ipa/dns-capabilities.html) | [DNS Use Cases](https://gprocunier.github.io/eigenstate-ipa/dns-use-cases.html) |
| SELinux maps | [SELinux Map Plugin](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-plugin.html) | [SELinux Map Capabilities](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-capabilities.html) | [SELinux Map Use Cases](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-use-cases.html) |
| Sudo policy | [Sudo Plugin](https://gprocunier.github.io/eigenstate-ipa/sudo-plugin.html) | [Sudo Capabilities](https://gprocunier.github.io/eigenstate-ipa/sudo-capabilities.html) | [Sudo Use Cases](https://gprocunier.github.io/eigenstate-ipa/sudo-use-cases.html) |
| HBAC rules | [HBAC Rule Plugin](https://gprocunier.github.io/eigenstate-ipa/hbacrule-plugin.html) | [HBAC Rule Capabilities](https://gprocunier.github.io/eigenstate-ipa/hbacrule-capabilities.html) | [HBAC Rule Use Cases](https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html) |

The canonical navigation page is still
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>DOCUMENTATION MAP</kbd></a>.

{% endraw %}

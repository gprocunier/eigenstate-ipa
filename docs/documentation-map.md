---
layout: default
title: Documentation Map
description: >-
  Navigation map for the eigenstate.ipa documentation set, organized by
  reading intent, workflow area, and document type.
---

{% raw %}

# Documentation Map

Use this page when you know the problem category but do not yet know which
collection page should be your first stop.

Current release: `1.14.0`

## Reading Model

The docs are organized on purpose:

- read a `capabilities` page when you are deciding whether a plugin boundary fits the job
- read a `use cases` page when you want a workflow or playbook pattern
- read a `plugin` page last when you need exact option names or return fields
- read a mutation module page when the workflow changes IdM state, rotates
  key material, issues a certificate, or writes sensitive artifacts

That keeps the decision pages from turning into reference dumps and keeps the
reference pages from wandering into broad architectural prose.

## First Route By Intent

### I am evaluating the collection overall

1. <a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>TOP README</kbd></a>
2. <a href="https://gprocunier.github.io/eigenstate-ipa/"><kbd>DOCS HOME</kbd></a>
3. choose one workflow from [High-Value Workflows](#high-value-workflows)

### I use Vault or CyberArk today

1. <a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>VAULT/CYBERARK PRIMER</kbd></a>
2. <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>ROTATION CAPABILITIES</kbd></a>
3. <a href="https://gprocunier.github.io/eigenstate-ipa/aap-ee-quickstart.html"><kbd>AAP EE QUICKSTART</kbd></a>
4. <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>
5. <a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>EPHEMERAL ACCESS CAPABILITIES</kbd></a>

### I run OpenShift, OpenShift Virtualization, or RHOSO

1. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html"><kbd>OPENSHIFT ECOSYSTEM PRIMER</kbd></a>
2. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-keycloak-idm-reference.html"><kbd>OPENSHIFT IDENTITY REFERENCE</kbd></a>
3. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-identity-validation-walkthrough.html"><kbd>OPENSHIFT IDENTITY VALIDATION</kbd></a>
4. <a href="https://gprocunier.github.io/eigenstate-ipa/kubernetes-secret-delivery-threat-model.html"><kbd>KUBERNETES SECRET THREAT MODEL</kbd></a>
5. <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>
6. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-operator-use-cases.html"><kbd>OPENSHIFT OPERATOR USE CASES</kbd></a>
7. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-use-cases.html"><kbd>OPENSHIFT RHOSO USE CASES</kbd></a>
8. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-operator-use-cases.html"><kbd>RHOSO OPERATOR USE CASES</kbd></a>
9. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-tenant-use-cases.html"><kbd>RHOSO TENANT USE CASES</kbd></a>
10. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhacm-use-cases.html"><kbd>OPENSHIFT RHACM USE CASES</kbd></a>
11. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhacs-use-cases.html"><kbd>OPENSHIFT RHACS USE CASES</kbd></a>
12. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-quay-use-cases.html"><kbd>OPENSHIFT QUAY USE CASES</kbd></a>
13. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-developer-use-cases.html"><kbd>OPENSHIFT DEVELOPER USE CASES</kbd></a>

### I already know the plugin and just need syntax

Go straight to [Plugin Family Index](#plugin-family-index).

## High-Value Workflows

These are the collection combinations worth learning as flows.

| Need | Best starting point | Why |
| --- | --- | --- |
| IdM-backed targeting and scoped inventory | [Inventory Use Cases](https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html) | combines host data, hostgroups, netgroups, HBAC scope, and host metadata |
| Service onboarding and key material | [Principal Use Cases](https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html) | principal pre-flight is the gate before keytab and cert work |
| Safe mutation surface migration | [Mutation Surface Migration](https://gprocunier.github.io/eigenstate-ipa/mutation-surface-migration.html) | shows how to move side-effecting keytab and cert flows from lookups to modules |
| TLS bootstrap and renewal | [Cert Use Cases](https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html) | cert issuance, retrieval, renewal, and vault-backed private-key handling |
| Static secret lifecycle in Controller | [Rotation Use Cases](https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html) | `vault_write`, `vault`, `keytab`, and `cert` in scheduled jobs |
| AAP execution environment validation | [AAP EE Quickstart](https://gprocunier.github.io/eigenstate-ipa/aap-ee-quickstart.html) | render, build, smoke-test, push, and register the IdM runtime image |
| AAP packaged workflow roles | [AAP Golden Path Roles](https://gprocunier.github.io/eigenstate-ipa/aap-golden-path-roles.html) | run sealed artifact delivery, temporary access windows, and cert expiry reporting as AAP jobs |
| OpenShift identity validation | [OpenShift Identity Validation](https://gprocunier.github.io/eigenstate-ipa/openshift-identity-validation-walkthrough.html) | render OpenShift OIDC configuration examples and validate IdM, Keycloak, RBAC, and breakglass evidence |
| Workload Secret delivery | [Kubernetes Secret Threat Model](https://gprocunier.github.io/eigenstate-ipa/kubernetes-secret-delivery-threat-model.html) | review cluster controls before rendering IdM-backed secrets, TLS material, or keytabs into Kubernetes Secret manifests |
| Lease-like temporary access in IdM | [Ephemeral Access Capabilities](https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html) | `user_lease` for delegated temporary users plus Kerberos key retirement patterns without pretending they are dynamic secret leases |
| Host enrollment | [OTP Use Cases](https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html) | OTP bootstrap plus official IdM enrollment modules and post-checks |
| Policy validation before privileged change | [AAP Integration](https://gprocunier.github.io/eigenstate-ipa/aap-integration.html) | `hbacrule`, `selinuxmap`, `sudo`, `principal`, and `dns` as controller-side gates |
| Vault or CyberArk displacement analysis | [Vault/CyberArk Primer](https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html) | comparison framing without pretending the collection is a lease engine or PAM suite |
| OpenShift platform and app workflows | [OpenShift Ecosystem Primer](https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html) | routes cluster admins, virtualization operators, RHOSO operators, RHOSO tenant admins, developers, RHACM operators, RHACS operators, and Quay operators into the right IdM-backed workflow pages |
| RHOSO operator and tenant workflows | [OpenShift RHOSO Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-use-cases.html) | RHOSO cloud operations and tenant-facing identity boundaries become cleaner AAP workflows instead of a mix of standing admin access and side-channel onboarding |
| RHACM event-driven remediation | [OpenShift RHACM Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhacm-use-cases.html) | RHACM policy violations and lifecycle hooks become AAP jobs that verify real IdM identity, policy, and supporting artifacts before they run |
| RHACS findings and enforcement | [OpenShift RHACS Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhacs-use-cases.html) | RHACS alerts, admission controls, and network-policy output become governed workflows instead of generic follow-up tickets |
| Quay identity and repo automation | [OpenShift Quay Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-quay-use-cases.html) | Quay team access, mirroring, notifications, and registry onboarding become IdM-aware workflows instead of local credential sprawl |

## Plugin Family Index

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

Use this table when you already know the plugin family and need the exact
three-page lane. For collection-wide questions, stay in the intent routes and
workflow guides above.

## Collection-Wide Guides

| Question | Best page |
| --- | --- |
| How does this compare to Vault or CyberArk? | [Vault/CyberArk Primer](https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html) |
| How does this fit into Controller and execution environments? | [AAP Integration](https://gprocunier.github.io/eigenstate-ipa/aap-integration.html) |
| Which mutation surface should I use? | [Compatibility Policy](https://gprocunier.github.io/eigenstate-ipa/compatibility-policy.html) |
| How do I migrate side-effecting lookups? | [Mutation Surface Migration](https://gprocunier.github.io/eigenstate-ipa/mutation-surface-migration.html) |
| How do I build the AAP EE? | [AAP EE Quickstart](https://gprocunier.github.io/eigenstate-ipa/aap-ee-quickstart.html) |
| Which packaged AAP workflow role should I use? | [AAP Golden Path Roles](https://gprocunier.github.io/eigenstate-ipa/aap-golden-path-roles.html) |
| How should I think about rotation workflows? | [Rotation Capabilities](https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html) |
| What is the temporary-access / lease boundary? | [Ephemeral Access Capabilities](https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html) |
| Where do the OpenShift and RHOSO branches begin? | [OpenShift Ecosystem Primer](https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html) |
| How do I validate OpenShift OIDC without mutating a cluster? | [OpenShift Identity Validation](https://gprocunier.github.io/eigenstate-ipa/openshift-identity-validation-walkthrough.html) |
| How do I deliver IdM-backed material to workloads safely? | [Kubernetes Secret Threat Model](https://gprocunier.github.io/eigenstate-ipa/kubernetes-secret-delivery-threat-model.html) |

## OpenShift Workflow Branches

- [OpenShift Keycloak IdM Reference](https://gprocunier.github.io/eigenstate-ipa/openshift-keycloak-idm-reference.html)
- [OpenShift Identity Validation Walkthrough](https://gprocunier.github.io/eigenstate-ipa/openshift-identity-validation-walkthrough.html)
- [OpenShift Breakglass Validation](https://gprocunier.github.io/eigenstate-ipa/openshift-breakglass-validation.html)
- [OpenShift LDAP Fallback](https://gprocunier.github.io/eigenstate-ipa/openshift-ldap-fallback.html)
- [Kubernetes Secret Delivery Threat Model](https://gprocunier.github.io/eigenstate-ipa/kubernetes-secret-delivery-threat-model.html)
- [Kubernetes Secret From IdM Vault](https://gprocunier.github.io/eigenstate-ipa/kubernetes-secret-from-idm-vault.html)
- [Kubernetes TLS From IdM Cert](https://gprocunier.github.io/eigenstate-ipa/kubernetes-tls-from-idm-cert.html)
- [Keytab Delivery To Workloads](https://gprocunier.github.io/eigenstate-ipa/keytab-delivery-to-workloads.html)
- [OpenShift Operator Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-operator-use-cases.html)
- [OpenShift RHOSO Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-use-cases.html)
- [RHOSO Operator Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-operator-use-cases.html)
- [RHOSO Tenant Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-tenant-use-cases.html)
- [OpenShift RHACM Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhacm-use-cases.html)
- [OpenShift RHACS Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhacs-use-cases.html)
- [OpenShift Quay Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-quay-use-cases.html)
- [OpenShift Developer Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-developer-use-cases.html)

## Validation Walkthroughs

- [AAP EE Validation Walkthrough](https://gprocunier.github.io/eigenstate-ipa/aap-ee-validation-walkthrough.html)
  validates the EE, Controller registration, smoke job, IdM inventory, vault
  metadata, HBAC checks, and `user_lease` check mode
- [Phase 2 Validation Walkthrough](https://gprocunier.github.io/eigenstate-ipa/phase2-validation-walkthrough.html)
  validates the golden-path AAP roles for certificate reporting, temporary
  access windows, and sealed artifact delivery
- [OpenShift Identity Validation Walkthrough](https://gprocunier.github.io/eigenstate-ipa/openshift-identity-validation-walkthrough.html)
  validates render-only OpenShift OIDC, Keycloak federation, IdM group, and
  breakglass readiness evidence
- [User Lease Demo](https://gprocunier.github.io/eigenstate-ipa/user-lease-demo.html)
  shows the exact boundary the demo proves: fresh `kinit` and SSH succeed during the lease,
  then a fresh `kinit` fails after expiry

## Keep The Flow Clean

To avoid circular writing:

- do not use this page as a substitute for plugin reference
- do not restate comparison framing from the primer inside plugin pages
- do not restate exact option tables inside capability pages
- keep cross-plugin workflow detail in use-case pages and collection-wide guides

{% endraw %}

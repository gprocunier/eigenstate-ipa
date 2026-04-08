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

Current release: `1.10.3`

## Reading Model

The docs are organized on purpose:

- read a `capabilities` page when you are deciding whether a plugin boundary fits the job
- read a `use cases` page when you want a workflow or playbook pattern
- read a `plugin` page last when you need exact option names or return fields

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
3. <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>
4. <a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>EPHEMERAL ACCESS CAPABILITIES</kbd></a>

### I run OpenShift, OpenShift Virtualization, or RHOSO

1. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html"><kbd>OPENSHIFT ECOSYSTEM PRIMER</kbd></a>
2. <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>
3. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-operator-use-cases.html"><kbd>OPENSHIFT OPERATOR USE CASES</kbd></a>
4. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-use-cases.html"><kbd>OPENSHIFT RHOSO USE CASES</kbd></a>
5. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-operator-use-cases.html"><kbd>RHOSO OPERATOR USE CASES</kbd></a>
6. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-tenant-use-cases.html"><kbd>RHOSO TENANT USE CASES</kbd></a>
7. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhacm-use-cases.html"><kbd>OPENSHIFT RHACM USE CASES</kbd></a>
8. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhacs-use-cases.html"><kbd>OPENSHIFT RHACS USE CASES</kbd></a>
9. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-quay-use-cases.html"><kbd>OPENSHIFT QUAY USE CASES</kbd></a>
10. <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-developer-use-cases.html"><kbd>OPENSHIFT DEVELOPER USE CASES</kbd></a>

### I already know the plugin and just need syntax

Go straight to [Reference By Area](#reference-by-area).

## High-Value Workflows

These are the collection combinations worth learning as flows.

| Need | Best starting point | Why |
| --- | --- | --- |
| IdM-backed targeting and scoped inventory | [Inventory Use Cases](https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html) | combines host data, hostgroups, netgroups, HBAC scope, and host metadata |
| Service onboarding and key material | [Principal Use Cases](https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html) | principal pre-flight is the gate before keytab and cert work |
| TLS bootstrap and renewal | [Cert Use Cases](https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html) | cert issuance, retrieval, renewal, and vault-backed private-key handling |
| Static secret lifecycle in Controller | [Rotation Use Cases](https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html) | `vault_write`, `vault`, `keytab`, and `cert` in scheduled jobs |
| Lease-like temporary access in IdM | [Ephemeral Access Capabilities](https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html) | `user_lease` for delegated temporary users plus Kerberos key retirement patterns without pretending they are dynamic secret leases |
| Host enrollment | [OTP Use Cases](https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html) | OTP bootstrap plus official IdM enrollment modules and post-checks |
| Policy validation before privileged change | [AAP Integration](https://gprocunier.github.io/eigenstate-ipa/aap-integration.html) | `hbacrule`, `selinuxmap`, `sudo`, `principal`, and `dns` as controller-side gates |
| Vault or CyberArk displacement analysis | [Vault/CyberArk Primer](https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html) | comparison framing without pretending the collection is a lease engine or PAM suite |
| OpenShift platform and app workflows | [OpenShift Ecosystem Primer](https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html) | routes cluster admins, virtualization operators, RHOSO operators, RHOSO tenant admins, developers, RHACM operators, RHACS operators, and Quay operators into the right IdM-backed workflow pages |
| RHOSO operator and tenant workflows | [OpenShift RHOSO Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-use-cases.html) | RHOSO cloud operations and tenant-facing identity boundaries become cleaner AAP workflows instead of a mix of standing admin access and side-channel onboarding |
| RHACM event-driven remediation | [OpenShift RHACM Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhacm-use-cases.html) | RHACM policy violations and lifecycle hooks become AAP jobs that verify real IdM identity, policy, and supporting artifacts before they run |
| RHACS findings and enforcement | [OpenShift RHACS Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhacs-use-cases.html) | RHACS alerts, admission controls, and network-policy output become governed workflows instead of generic follow-up tickets |
| Quay identity and repo automation | [OpenShift Quay Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-quay-use-cases.html) | Quay team access, mirroring, notifications, and registry onboarding become IdM-aware workflows instead of local credential sprawl |

## Choose By Problem

### Inventory and targeting

- [Inventory Plugin](https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html)
- [Inventory Capabilities](https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html)
- [Inventory Use Cases](https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html)

### Static secrets and vault lifecycle

- [Vault Plugin](https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html)
- [Vault Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html)
- [Vault Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html)
- [Vault Write Module](https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html)
- [Vault Write Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html)
- [Vault Write Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-write-use-cases.html)

### Kerberos, certificates, and enrollment

- [Principal Plugin](https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html)
- [Principal Capabilities](https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html)
- [Principal Use Cases](https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html)
- [Keytab Plugin](https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html)
- [Keytab Capabilities](https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html)
- [Keytab Use Cases](https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html)
- [User Lease Module](https://gprocunier.github.io/eigenstate-ipa/user-lease-plugin.html)
- [User Lease Capabilities](https://gprocunier.github.io/eigenstate-ipa/user-lease-capabilities.html)
- [User Lease Use Cases](https://gprocunier.github.io/eigenstate-ipa/user-lease-use-cases.html)
- [Cert Plugin](https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html)
- [Cert Capabilities](https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html)
- [Cert Use Cases](https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html)
- [OTP Plugin](https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html)
- [OTP Capabilities](https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html)
- [OTP Use Cases](https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html)

### DNS and policy validation

- [DNS Plugin](https://gprocunier.github.io/eigenstate-ipa/dns-plugin.html)
- [DNS Capabilities](https://gprocunier.github.io/eigenstate-ipa/dns-capabilities.html)
- [DNS Use Cases](https://gprocunier.github.io/eigenstate-ipa/dns-use-cases.html)
- [Sudo Plugin](https://gprocunier.github.io/eigenstate-ipa/sudo-plugin.html)
- [Sudo Capabilities](https://gprocunier.github.io/eigenstate-ipa/sudo-capabilities.html)
- [Sudo Use Cases](https://gprocunier.github.io/eigenstate-ipa/sudo-use-cases.html)
- [SELinux Map Plugin](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-plugin.html)
- [SELinux Map Capabilities](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-capabilities.html)
- [SELinux Map Use Cases](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-use-cases.html)
- [HBAC Rule Plugin](https://gprocunier.github.io/eigenstate-ipa/hbacrule-plugin.html)
- [HBAC Rule Capabilities](https://gprocunier.github.io/eigenstate-ipa/hbacrule-capabilities.html)
- [HBAC Rule Use Cases](https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html)

### Controller workflows and comparison framing

- [AAP Integration](https://gprocunier.github.io/eigenstate-ipa/aap-integration.html)
- [Rotation Capabilities](https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html)
- [Rotation Use Cases](https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html)
- [Vault/CyberArk Primer](https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html)
- [Ephemeral Access Capabilities](https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html)
- [OpenShift Ecosystem Primer](https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html)
- [OpenShift Operator Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-operator-use-cases.html)
- [OpenShift RHOSO Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-use-cases.html)
- [RHOSO Operator Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-operator-use-cases.html)
- [RHOSO Tenant Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-tenant-use-cases.html)
- [OpenShift RHACM Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhacm-use-cases.html)
- [OpenShift RHACS Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-rhacs-use-cases.html)
- [OpenShift Quay Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-quay-use-cases.html)
- [OpenShift Developer Use Cases](https://gprocunier.github.io/eigenstate-ipa/openshift-developer-use-cases.html)

## Reference By Area

| Area | Reference | Capabilities | Use cases |
| --- | --- | --- | --- |
| Inventory | [Inventory Plugin](https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html) | [Inventory Capabilities](https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html) | [Inventory Use Cases](https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html) |
| Vault retrieval | [Vault Plugin](https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html) | [Vault Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html) | [Vault Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html) |
| Vault lifecycle | [Vault Write Module](https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html) | [Vault Write Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html) | [Vault Write Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-write-use-cases.html) |
| Principal state | [Principal Plugin](https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html) | [Principal Capabilities](https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html) | [Principal Use Cases](https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html) |
| Keytabs | [Keytab Plugin](https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html) | [Keytab Capabilities](https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html) | [Keytab Use Cases](https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html) |
| User lease | [User Lease Module](https://gprocunier.github.io/eigenstate-ipa/user-lease-plugin.html) | [User Lease Capabilities](https://gprocunier.github.io/eigenstate-ipa/user-lease-capabilities.html) | [User Lease Use Cases](https://gprocunier.github.io/eigenstate-ipa/user-lease-use-cases.html) |
| Certificates | [Cert Plugin](https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html) | [Cert Capabilities](https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html) | [Cert Use Cases](https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html) |
| OTP | [OTP Plugin](https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html) | [OTP Capabilities](https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html) | [OTP Use Cases](https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html) |
| DNS | [DNS Plugin](https://gprocunier.github.io/eigenstate-ipa/dns-plugin.html) | [DNS Capabilities](https://gprocunier.github.io/eigenstate-ipa/dns-capabilities.html) | [DNS Use Cases](https://gprocunier.github.io/eigenstate-ipa/dns-use-cases.html) |
| SELinux maps | [SELinux Map Plugin](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-plugin.html) | [SELinux Map Capabilities](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-capabilities.html) | [SELinux Map Use Cases](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-use-cases.html) |
| Sudo policy | [Sudo Plugin](https://gprocunier.github.io/eigenstate-ipa/sudo-plugin.html) | [Sudo Capabilities](https://gprocunier.github.io/eigenstate-ipa/sudo-capabilities.html) | [Sudo Use Cases](https://gprocunier.github.io/eigenstate-ipa/sudo-use-cases.html) |
| HBAC rules | [HBAC Rule Plugin](https://gprocunier.github.io/eigenstate-ipa/hbacrule-plugin.html) | [HBAC Rule Capabilities](https://gprocunier.github.io/eigenstate-ipa/hbacrule-capabilities.html) | [HBAC Rule Use Cases](https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html) |

## Keep The Flow Clean

To avoid circular writing:

- do not use this page as a substitute for plugin reference
- do not restate comparison framing from the primer inside plugin pages
- do not restate exact option tables inside capability pages
- keep cross-plugin workflow detail in use-case pages and collection-wide guides

{% endraw %}

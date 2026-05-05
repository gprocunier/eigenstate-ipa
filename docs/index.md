---
layout: default
title: eigenstate.ipa
description: >-
  Ansible collection for Red Hat IdM / FreeIPA covering inventory, vault
  retrieval and lifecycle, Kerberos principal and keytab workflows,
  certificates, OTP, delegated user-lease control, DNS, sudo, SELinux maps, and HBAC policy validation.
---

{% raw %}

`eigenstate.ipa` is an Ansible collection for Red Hat IdM / FreeIPA. It treats
IdM as a live automation system of record for inventory, secrets, Kerberos
material, certificates, DNS, and access policy instead of forcing those
surfaces into separate inventory files, ad hoc shell scripts, or external
stores.

Current release: `1.11.0`

## Start Here

Pick the lane that matches the problem first, then branch into the deeper docs:

<table>
  <thead>
    <tr>
      <th>Problem</th>
      <th>Start here</th>
      <th>Why this page first</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Need reading order or the full doc map</td>
      <td><a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>DOCUMENTATION MAP</kbd></a></td>
      <td>Routes by intent and keeps the three-page model visible.</td>
    </tr>
    <tr>
      <td>Translating Vault or CyberArk expectations</td>
      <td><a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>VAULT/CYBERARK PRIMER</kbd></a></td>
      <td>Explains the IdM-native boundary before you pick a workflow.</td>
    </tr>
    <tr>
      <td>Working around OpenShift, RHOSO, RHACM, RHACS, or Quay</td>
      <td><a href="https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html"><kbd>OPENSHIFT ECOSYSTEM PRIMER</kbd></a></td>
      <td>Gives the platform-wide framing before the branch-specific pages.</td>
    </tr>
    <tr>
      <td>Running Controller or execution-environment jobs</td>
      <td><a href="https://gprocunier.github.io/eigenstate-ipa/aap-ee-quickstart.html"><kbd>AAP EE QUICKSTART</kbd></a></td>
      <td>Starts with the ready-to-build runtime before the broader Controller model.</td>
    </tr>
    <tr>
      <td>Managing static secrets or scheduled rotation</td>
      <td><a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>ROTATION CAPABILITIES</kbd></a></td>
      <td>Separates scheduled lifecycle work from one-off lookups.</td>
    </tr>
    <tr>
      <td>Opening or closing temporary access windows</td>
      <td><a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>EPHEMERAL ACCESS CAPABILITIES</kbd></a></td>
      <td>Explains the lease-like boundary before you read the workflow pages.</td>
    </tr>
  </tbody>
</table>

## How The Docs Work

Every plugin area uses the same three-page shape:

- `plugin` pages for exact syntax, auth behavior, return data, and option details
- `capabilities` pages for decision boundaries and operational fit
- `use cases` pages for worked playbook patterns and cross-plugin flow

That split is intentional. The reference pages should stay precise. The
capability pages should answer "is this the right boundary?" The use-case pages
should show how the pieces combine without restating the full reference.

## High-Value Workflows

These are the combinations that matter most in practice and are worth reading
as workflows rather than as isolated plugins.

| Workflow | Main combination | Start here |
| --- | --- | --- |
| Identity-driven targeting | `idm` inventory + host metadata + HBAC-backed grouping | [Inventory Use Cases](https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html) |
| Service onboarding | `principal` pre-flight + `keytab` retrieval + optional `cert` issuance | [Principal Use Cases](https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html) |
| TLS bootstrap and renewal | `cert` + `vault_write` for private key archival + `vault` retrieval | [Cert Use Cases](https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html) |
| Static secret lifecycle | `vault_write` mutation + `vault` retrieval + AAP scheduling | [Rotation Use Cases](https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html) |
| AAP runtime adoption | EE scaffold + `aap_execution_environment` role + smoke checks | [AAP EE Quickstart](https://gprocunier.github.io/eigenstate-ipa/aap-ee-quickstart.html) |
| Lease-like temporary access | `user_lease` for delegated temporary users or `principal` + `keytab` retirement for machine identity | [Ephemeral Access Capabilities](https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html) |
| Host enrollment | `otp` bootstrap + official IdM enrollment modules + `principal` verification | [OTP Use Cases](https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html) |
| Policy validation before change | `hbacrule` + `selinuxmap` + `sudo` + optional `dns`/`principal` checks | [AAP Integration](https://gprocunier.github.io/eigenstate-ipa/aap-integration.html) |
| Sealed artifact delivery | `cert` recipient + `vault_write` archive + `vault` retrieval | [Vault Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html) |
| OpenShift platform workflows | Keycloak + IdM trust + AAP workflows for break-glass, guest enrollment, RHOSO operator paths, RHOSO tenant onboarding, RHACM remediation, RHACS response paths, Quay automation, and service onboarding | [OpenShift Ecosystem Primer](https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html) |

## Plugin Families

| Area | Reference | Capabilities | Use cases |
| --- | --- | --- | --- |
| Inventory | [Inventory Plugin](https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html) | [Inventory Capabilities](https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html) | [Inventory Use Cases](https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html) |
| Vault retrieval | [Vault Plugin](https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html) | [Vault Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html) | [Vault Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html) |
| Vault lifecycle | [Vault Write Module](https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html) | [Vault Write Capabilities](https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html) | [Vault Write Use Cases](https://gprocunier.github.io/eigenstate-ipa/vault-write-use-cases.html) |
| Principal state | [Principal Plugin](https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html) | [Principal Capabilities](https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html) | [Principal Use Cases](https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html) |
| Keytabs | [Keytab Plugin](https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html) | [Keytab Capabilities](https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html) | [Keytab Use Cases](https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html) |
| User lease | [User Lease Module](https://gprocunier.github.io/eigenstate-ipa/user-lease-plugin.html) | [User Lease Capabilities](https://gprocunier.github.io/eigenstate-ipa/user-lease-capabilities.html) | [User Lease Use Cases](https://gprocunier.github.io/eigenstate-ipa/user-lease-use-cases.html) |
| Certificates | [Cert Plugin](https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html) | [Cert Capabilities](https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html) | [Cert Use Cases](https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html) |
| OTP and enrollment | [OTP Plugin](https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html) | [OTP Capabilities](https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html) | [OTP Use Cases](https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html) |
| DNS state | [DNS Plugin](https://gprocunier.github.io/eigenstate-ipa/dns-plugin.html) | [DNS Capabilities](https://gprocunier.github.io/eigenstate-ipa/dns-capabilities.html) | [DNS Use Cases](https://gprocunier.github.io/eigenstate-ipa/dns-use-cases.html) |
| SELinux maps | [SELinux Map Plugin](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-plugin.html) | [SELinux Map Capabilities](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-capabilities.html) | [SELinux Map Use Cases](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-use-cases.html) |
| Sudo policy | [Sudo Plugin](https://gprocunier.github.io/eigenstate-ipa/sudo-plugin.html) | [Sudo Capabilities](https://gprocunier.github.io/eigenstate-ipa/sudo-capabilities.html) | [Sudo Use Cases](https://gprocunier.github.io/eigenstate-ipa/sudo-use-cases.html) |
| HBAC rules | [HBAC Rule Plugin](https://gprocunier.github.io/eigenstate-ipa/hbacrule-plugin.html) | [HBAC Rule Capabilities](https://gprocunier.github.io/eigenstate-ipa/hbacrule-capabilities.html) | [HBAC Rule Use Cases](https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html) |

## Collection-Wide Guides

- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>VAULT/CYBERARK PRIMER</kbd></a>
  explains where the collection overlaps with Vault or CyberArk and where it does not
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html"><kbd>OPENSHIFT ECOSYSTEM PRIMER</kbd></a>
  frames the collection for OpenShift-adjacent estates using Keycloak and IdM-backed trust
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-operator-use-cases.html"><kbd>OPENSHIFT OPERATOR USE CASES</kbd></a>
  focuses on cluster-admin and OpenShift Virtualization workflows
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-use-cases.html"><kbd>OPENSHIFT RHOSO USE CASES</kbd></a>
  frames the RHOSO branch around cloud-operator and tenant identity boundaries
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-operator-use-cases.html"><kbd>RHOSO OPERATOR USE CASES</kbd></a>
  focuses on operator maintenance windows, data-plane host access, and supporting cloud services
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-tenant-use-cases.html"><kbd>RHOSO TENANT USE CASES</kbd></a>
  focuses on tenant identity separation, delegated interventions, and tenant-facing service onboarding
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhacm-use-cases.html"><kbd>OPENSHIFT RHACM USE CASES</kbd></a>
  focuses on RHACM policy events and cluster lifecycle hooks
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhacs-use-cases.html"><kbd>OPENSHIFT RHACS USE CASES</kbd></a>
  focuses on RHACS findings, enforcement, and identity-aware response workflows
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-quay-use-cases.html"><kbd>OPENSHIFT QUAY USE CASES</kbd></a>
  focuses on Quay identity, mirroring, repository notifications, and registry onboarding workflows
- <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-developer-use-cases.html"><kbd>OPENSHIFT DEVELOPER USE CASES</kbd></a>
  focuses on app-team onboarding and developer-facing platform workflows
- <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>
  explains execution-environment dependencies, non-interactive auth, and controller-side patterns
- <a href="https://gprocunier.github.io/eigenstate-ipa/aap-ee-quickstart.html"><kbd>AAP EE QUICKSTART</kbd></a>
  gives the render, build, smoke, push, and Controller registration path for the IdM EE
- <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>ROTATION CAPABILITIES</kbd></a>
  explains the collection-wide rotation model for static assets
- <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>ROTATION USE CASES</kbd></a>
  shows scheduled workflows built from the collection primitives
- <a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>EPHEMERAL ACCESS CAPABILITIES</kbd></a>
  explains IdM-native lease-like temporary access patterns for users and Kerberos principals
- <a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-demo.html"><kbd>USER LEASE DEMO</kbd></a>
  shows the recorded manual `user_lease` behavior with a vaulted password, a real SSH login during the lease, and a post-expiry `kinit` failure

## Best Fit

This collection fits best when:

- IdM or FreeIPA already exists and should remain the source of truth
- Kerberos-authenticated controller-side automation is preferable to external token systems
- the workflow is static-secret retrieval, keytabs, certs, DNS, identity-aware inventory, or access-policy validation
- AAP is available for scheduling, approvals, credential injection, and repeatable execution environments

For the repository overview and install path, return to
<a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>TOP README</kbd></a>.

{% endraw %}

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

Current release: `1.16.0`

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
      <td>Mapping IdM workflows to OpenShift, RHOSO, RHACM, RHACS, or Quay</td>
      <td><a href="https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html"><kbd>OPENSHIFT ECOSYSTEM PRIMER</kbd></a></td>
      <td>Gives the platform-wide framing before the branch-specific pages.</td>
    </tr>
    <tr>
      <td>Validating OpenShift identity through Keycloak and IdM</td>
      <td><a href="https://gprocunier.github.io/eigenstate-ipa/openshift-identity-validation-walkthrough.html"><kbd>OPENSHIFT IDENTITY VALIDATION</kbd></a></td>
      <td>Renders OIDC config examples and readiness reports without mutating a cluster.</td>
    </tr>
    <tr>
      <td>Delivering IdM-backed workload secrets to Kubernetes or OpenShift</td>
      <td><a href="https://gprocunier.github.io/eigenstate-ipa/workload-secret-delivery-controls.html"><kbd>WORKLOAD SECRET DELIVERY CONTROLS</kbd></a></td>
      <td>Starts with the cluster control boundary before rendering or applying payload manifests.</td>
    </tr>
    <tr>
      <td>Producing safe operational evidence and drift reports</td>
      <td><a href="https://gprocunier.github.io/eigenstate-ipa/reporting-overview.html"><kbd>REPORTING OVERVIEW</kbd></a></td>
      <td>Routes into read-only JSON, YAML, and Markdown reports for readiness, inventory, access, and drift.</td>
    </tr>
    <tr>
      <td>Running Controller or execution-environment jobs</td>
      <td><a href="https://gprocunier.github.io/eigenstate-ipa/aap-ee-quickstart.html"><kbd>AAP EE QUICKSTART</kbd></a></td>
      <td>Starts with the ready-to-build runtime before the broader Controller model.</td>
    </tr>
    <tr>
      <td>Using packaged AAP workflow roles</td>
      <td><a href="https://gprocunier.github.io/eigenstate-ipa/aap-idm-workflow-roles.html"><kbd>AAP IDM WORKFLOW ROLES</kbd></a></td>
      <td>Routes into the sealed artifact, temporary access, and cert reporting roles.</td>
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
| Side-effecting keytab and cert operations | `keytab_manage` + `cert_request` | [Mutation Surface Migration](https://gprocunier.github.io/eigenstate-ipa/mutation-surface-migration.html) |
| TLS bootstrap and renewal | `cert` + `vault_write` for private key archival + `vault` retrieval | [Cert Use Cases](https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html) |
| Static secret lifecycle | `vault_write` mutation + `vault` retrieval + AAP scheduling | [Rotation Use Cases](https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html) |
| AAP runtime validation | EE scaffold + `aap_execution_environment` role + smoke checks | [AAP EE Quickstart](https://gprocunier.github.io/eigenstate-ipa/aap-ee-quickstart.html) |
| AAP packaged workflows | `sealed_artifact_delivery` + `temporary_access_window` + `cert_expiry_report` | [AAP IdM Workflow Roles](https://gprocunier.github.io/eigenstate-ipa/aap-idm-workflow-roles.html) |
| OpenShift identity validation | `openshift_idm_oidc_validation` + `keycloak_idm_federation_validation` + `openshift_breakglass_validation` | [OpenShift Identity Validation](https://gprocunier.github.io/eigenstate-ipa/openshift-identity-validation-walkthrough.html) |
| Workload Secret delivery | `kubernetes_secret_from_idm_vault` + `kubernetes_tls_from_idm_cert` + `keytab_secret_render` | [Workload Secret Delivery Controls](https://gprocunier.github.io/eigenstate-ipa/workload-secret-delivery-controls.html) |
| Operational evidence reporting | `idm_readiness_report` + `certificate_inventory_report` + `keytab_rotation_candidates` + `temporary_access_report` + `policy_drift_report` | [Reporting Overview](https://gprocunier.github.io/eigenstate-ipa/reporting-overview.html) |
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
| Keytab management | [Keytab Manage Module](https://gprocunier.github.io/eigenstate-ipa/keytab-manage-module.html) | [Compatibility Policy](https://gprocunier.github.io/eigenstate-ipa/compatibility-policy.html) | [Mutation Surface Migration](https://gprocunier.github.io/eigenstate-ipa/mutation-surface-migration.html) |
| User lease | [User Lease Module](https://gprocunier.github.io/eigenstate-ipa/user-lease-plugin.html) | [User Lease Capabilities](https://gprocunier.github.io/eigenstate-ipa/user-lease-capabilities.html) | [User Lease Use Cases](https://gprocunier.github.io/eigenstate-ipa/user-lease-use-cases.html) |
| Certificates | [Cert Plugin](https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html) | [Cert Capabilities](https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html) | [Cert Use Cases](https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html) |
| Certificate request | [Cert Request Module](https://gprocunier.github.io/eigenstate-ipa/cert-request-module.html) | [Compatibility Policy](https://gprocunier.github.io/eigenstate-ipa/compatibility-policy.html) | [Mutation Surface Migration](https://gprocunier.github.io/eigenstate-ipa/mutation-surface-migration.html) |
| OTP and enrollment | [OTP Plugin](https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html) | [OTP Capabilities](https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html) | [OTP Use Cases](https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html) |
| DNS state | [DNS Plugin](https://gprocunier.github.io/eigenstate-ipa/dns-plugin.html) | [DNS Capabilities](https://gprocunier.github.io/eigenstate-ipa/dns-capabilities.html) | [DNS Use Cases](https://gprocunier.github.io/eigenstate-ipa/dns-use-cases.html) |
| SELinux maps | [SELinux Map Plugin](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-plugin.html) | [SELinux Map Capabilities](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-capabilities.html) | [SELinux Map Use Cases](https://gprocunier.github.io/eigenstate-ipa/selinuxmap-use-cases.html) |
| Sudo policy | [Sudo Plugin](https://gprocunier.github.io/eigenstate-ipa/sudo-plugin.html) | [Sudo Capabilities](https://gprocunier.github.io/eigenstate-ipa/sudo-capabilities.html) | [Sudo Use Cases](https://gprocunier.github.io/eigenstate-ipa/sudo-use-cases.html) |
| HBAC rules | [HBAC Rule Plugin](https://gprocunier.github.io/eigenstate-ipa/hbacrule-plugin.html) | [HBAC Rule Capabilities](https://gprocunier.github.io/eigenstate-ipa/hbacrule-capabilities.html) | [HBAC Rule Use Cases](https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html) |

## Collection-Wide Guides

| Topic | Start here | Boundary |
| --- | --- | --- |
| Vault and CyberArk comparison | [IdM Vault Boundary](https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html) | where IdM vault workflows fit and where broader secret-manager semantics still belong elsewhere |
| Ansible Automation Platform | [AAP EE Quickstart](https://gprocunier.github.io/eigenstate-ipa/aap-ee-quickstart.html) | execution-environment dependencies, Controller registration, and job evidence |
| Packaged AAP workflows | [AAP IdM Workflow Roles](https://gprocunier.github.io/eigenstate-ipa/aap-idm-workflow-roles.html) | sealed artifacts, temporary access windows, and certificate-expiry reporting |
| OpenShift identity | [OpenShift Ecosystem Primer](https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html) | IdM, Keycloak, OAuth, RBAC, and breakglass evidence before live enforcement |
| Workload Secret delivery | [Workload Secret Delivery Controls](https://gprocunier.github.io/eigenstate-ipa/workload-secret-delivery-controls.html) | cluster controls required before applying payload-bearing manifests |
| Operational reports | [Reporting Overview](https://gprocunier.github.io/eigenstate-ipa/reporting-overview.html) | read-only evidence artifacts for readiness, inventory, rotation, access, and drift |
| Temporary access | [Ephemeral Access Capabilities](https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html) | IdM expiry attributes, delegated operators, and post-expiry validation |
| Release engineering | [Support Matrix](https://gprocunier.github.io/eigenstate-ipa/support-matrix.html) | supported ansible-core, Python, IdM, execution-environment, test, and release boundaries |

## Best Fit

This collection fits best when:

- IdM or FreeIPA already exists and should remain the source of truth
- Kerberos-authenticated controller-side automation is preferable to external token systems
- the workflow is static-secret retrieval, keytabs, certs, DNS, identity-aware inventory, or access-policy validation
- AAP is available for scheduling, approvals, credential injection, and repeatable execution environments

For the repository overview and install path, return to
<a href="https://github.com/gprocunier/eigenstate-ipa"><kbd>TOP README</kbd></a>.

{% endraw %}

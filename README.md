# eigenstate.ipa

**An Ansible collection for Red Hat IdM / FreeIPA with dynamic inventory, IdM vault retrieval and lifecycle automation, Kerberos principal state, keytab delivery, delegated user-lease control, certificate automation, OTP workflows, DNS record inspection, sudo policy inspection, SELinux user map inspection, and HBAC rule inspection and access testing.**

[![License: GPL-3.0](https://img.shields.io/github/license/gprocunier/eigenstate-ipa)](COPYING)
![Ansible 2.15+](https://img.shields.io/badge/Ansible-2.15%2B-blue)
![FreeIPA 4.6+](https://img.shields.io/badge/FreeIPA-4.6%2B-blue)
![RHEL](https://img.shields.io/badge/RHEL-9%20%7C%2010-red)

<a href="https://gprocunier.github.io/eigenstate-ipa/"><kbd>&nbsp;&nbsp;DOCS HOME&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/support-matrix.html"><kbd>&nbsp;&nbsp;SUPPORT MATRIX&nbsp;&nbsp;</kbd></a>

Core workflow routes:

<a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>&nbsp;&nbsp;IDM VAULT BOUNDARY&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-ee-quickstart.html"><kbd>&nbsp;&nbsp;AAP EE QUICKSTART&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html"><kbd>&nbsp;&nbsp;OPENSHIFT WORKFLOWS&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/reporting-overview.html"><kbd>&nbsp;&nbsp;REPORTING&nbsp;&nbsp;</kbd></a>

---

`eigenstate` is a nod to the quantum-mechanical idea of a stable observable
state. In practice, the collection assumes IdM already knows what the estate
looks like and what secrets it should hand out. The Ansible side should consume
that state directly instead of maintaining a parallel copy in static inventory
files and side-channel secret stores.

The GitHub repository name is `eigenstate-ipa`; the Ansible collection name is
`eigenstate.ipa`.

## Why This Collection Exists

Ansible already has strong support for managing IdM objects. The missing piece
has been consuming IdM as an input system:

- dynamic inventory from enrolled IdM hosts, hostgroups, netgroups, and HBAC
  policy
- secret retrieval from IdM vaults without copying those values into Git or
  inventory vars

Without those two paths, operators usually end up with:

- static inventory that drifts from the enrollment reality
- policy data duplicated outside the identity platform
- credentials copied into other stores because automation cannot read IdM vaults
- keytabs staged by hand outside the automation lifecycle
- certificate requests handled in separate CA workflows outside the automation lifecycle

This collection closes that gap with one inventory plugin, nine lookup plugins,
and four write modules.

## What The Collection Contains

The collection has three practical layers:

- live inventory from IdM host and policy data
- controller-side lookup plugins for Kerberos, vaults, certificates, OTP, DNS, and policy state
- narrow write modules for vault lifecycle, keytab management, certificate
  issuance, and delegated temporary-user expiry
- render-only validation roles for OpenShift OIDC, Keycloak federation,
  breakglass readiness evidence, and workload secret delivery review
- read-only reporting roles for readiness, certificate inventory, rotation
  candidate, temporary access, and policy drift evidence

The table below is the authoritative surface summary.

| Plugin | Type | FQCN | Purpose |
| --- | --- | --- | --- |
| IdM inventory | inventory | `eigenstate.ipa.idm` | Builds live inventory from IdM-enrolled hosts and policy-backed group relationships |
| IdM vault | lookup | `eigenstate.ipa.vault` | Retrieves vault payloads, inspects metadata, and searches vault scopes in IdM |
| IdM vault lifecycle | module | `eigenstate.ipa.vault_write` | Creates, archives, updates, and deletes IdM vaults with check-mode and member-management support |
| Kerberos principal state | lookup | `eigenstate.ipa.principal` | Reads user, host, and service principal existence, key, lock, and last-auth state from IdM |
| Kerberos keytab | lookup | `eigenstate.ipa.keytab` | Retrieves Kerberos keytab files for service and host principals via `ipa-getkeytab` |
| Kerberos keytab management | module | `eigenstate.ipa.keytab_manage` | Retrieves existing keytabs to disk or rotates keys with explicit confirmation |
| User lease boundary | module | `eigenstate.ipa.user_lease` | Sets, expires, or clears user expiry attributes for delegated temporary-access workflows |
| IdM certificates | lookup | `eigenstate.ipa.cert` | Requests, retrieves, and searches IdM CA certificates for host and service principals |
| IdM certificate request | module | `eigenstate.ipa.cert_request` | Requests IdM CA certificates from CSRs with metadata-first returns and optional file deployment |
| OTP and enrollment credentials | lookup | `eigenstate.ipa.otp` | Issues user OTP tokens and one-time host enrollment passwords through IdM |
| DNS record state | lookup | `eigenstate.ipa.dns` | Reads forward, reverse, zone-apex, and broad-search DNS records from IdM |
| SELinux user map state | lookup | `eigenstate.ipa.selinuxmap` | Reads SELinux user map configuration and HBAC-linked scope from IdM |
| Sudo policy state | lookup | `eigenstate.ipa.sudo` | Reads sudo rules, sudo commands, and sudo command groups from IdM |
| HBAC rule state and access test | lookup | `eigenstate.ipa.hbacrule` | Reads HBAC rule configuration and runs live access tests via the FreeIPA hbactest engine |

The collection also includes render-first roles for OpenShift and Kubernetes
workload delivery. These roles create reviewable manifests by default and do
not apply cluster changes unless explicitly configured with kubeconfig and
context inputs.

It also includes read-only reporting roles that render JSON, YAML, and Markdown
artifacts from explicit records. These roles are evidence producers; any
remediation remains a separate opt-in workflow.

## Start Here

Use the published docs by task, not as a flat file list.

| Need | First page |
| --- | --- |
| Choose a reading path | <a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>DOCUMENTATION MAP</kbd></a> |
| Build from IdM inventory and policy state | <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>INVENTORY CAPABILITIES</kbd></a> |
| Retrieve or manage IdM vault material | <a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>IDM VAULT BOUNDARY</kbd></a> |
| Work with Kerberos principals, keytabs, certificates, or OTPs | <a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>PRINCIPAL USE CASES</kbd></a> |
| Open or close delegated temporary access | <a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>EPHEMERAL ACCESS CAPABILITIES</kbd></a> |
| Run the collection in Ansible Automation Platform | <a href="https://gprocunier.github.io/eigenstate-ipa/aap-ee-quickstart.html"><kbd>AAP EE QUICKSTART</kbd></a> |
| Validate OpenShift identity and workload delivery boundaries | <a href="https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html"><kbd>OPENSHIFT WORKFLOWS</kbd></a> |
| Produce read-only operational evidence | <a href="https://gprocunier.github.io/eigenstate-ipa/reporting-overview.html"><kbd>REPORTING OVERVIEW</kbd></a> |

Plugin pages are reference material. Capability pages explain fit and
authority boundaries. Use-case and walkthrough pages show the operator flow and
the evidence produced by the workflow.

## For Vault Or CyberArk Users

Start with the comparison framing, then move into the collection-wide workflow guides.

<a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>&nbsp;&nbsp;VAULT/CYBERARK PRIMER&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>&nbsp;&nbsp;ROTATION CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>&nbsp;&nbsp;ROTATION USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>&nbsp;&nbsp;EPHEMERAL ACCESS CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>

If the comparison translates into an IdM-native workflow for you, these are the first concrete surfaces worth reading:

<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>&nbsp;&nbsp;IDM VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html"><kbd>&nbsp;&nbsp;VAULT WRITE MODULE&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>&nbsp;&nbsp;KEYTAB PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-manage-module.html"><kbd>&nbsp;&nbsp;KEYTAB MANAGE MODULE&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-plugin.html"><kbd>&nbsp;&nbsp;USER LEASE MODULE&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>&nbsp;&nbsp;IDM CERT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-request-module.html"><kbd>&nbsp;&nbsp;CERT REQUEST MODULE&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-plugin.html"><kbd>&nbsp;&nbsp;HBAC RULE PLUGIN&nbsp;&nbsp;</kbd></a>

## Quick Install

```bash
ansible-galaxy collection install eigenstate-ipa-1.16.0.tar.gz
```

Verify the main surfaces you plan to use. For example:

```bash
ansible-doc -t inventory eigenstate.ipa.idm
ansible-doc -t lookup eigenstate.ipa.vault
ansible-doc -t lookup eigenstate.ipa.keytab
ansible-doc -t module eigenstate.ipa.keytab_manage
ansible-doc -t module eigenstate.ipa.vault_write
ansible-doc -t module eigenstate.ipa.cert_request
ansible-doc -t module eigenstate.ipa.user_lease
```

For the full plugin index, use <a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>DOCS MAP</kbd></a>.

> [!NOTE]
> The inventory plugin talks to the IdM JSON-RPC API and can use either
> password authentication or Kerberos with an optional keytab. The vault
> lookup, vault write, principal, cert, OTP, and DNS components use `ipalib` and
> therefore depend on the local IdM client Python libraries being available on
> the control node or execution environment. The keytab
> plugin shells out to `ipa-getkeytab` and does not require `ipalib`; on RHEL
> 10 install `ipa-client`, and on other releases install the package that
> provides `ipa-getkeytab` on the control node or EE. The cert plugin uses
> `ipalib` like the vault plugin and can request, retrieve, and search IdM CA
> certificates without `certmonger` on the target. The OTP, selinuxmap,
> sudo, hbacrule, and user_lease surfaces use the same IdM client Python stack as the
> vault, principal, and cert lookups.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `plugins/inventory/idm.py` | Dynamic inventory plugin for hosts, hostgroups, netgroups, and HBAC rules |
| `plugins/lookup/vault.py` | Lookup plugin for IdM vault retrieval |
| `plugins/modules/vault_write.py` | Module for IdM vault lifecycle operations |
| `plugins/module_utils/ipa_client.py` | Shared Kerberos auth and `ipalib` connection utilities for IPA write operations |
| `plugins/lookup/principal.py` | Lookup plugin for Kerberos principal state queries |
| `plugins/lookup/keytab.py` | Lookup plugin for Kerberos keytab retrieval via `ipa-getkeytab` |
| `plugins/modules/keytab_manage.py` | Module for guarded keytab retrieval, deployment, and rotation |
| `plugins/modules/user_lease.py` | Module for delegated temporary-user expiry and lease boundaries in IdM |
| `plugins/lookup/cert.py` | Lookup plugin for IdM CA certificate request, retrieval, and search |
| `plugins/modules/cert_request.py` | Module for IdM CA certificate requests from CSRs |
| `plugins/lookup/otp.py` | Lookup plugin for OTP token issuance and host enrollment password generation |
| `plugins/lookup/selinuxmap.py` | Lookup plugin for SELinux user map state inspection |
| `plugins/lookup/sudo.py` | Lookup plugin for sudo rules, commands, and command groups |
| `plugins/lookup/hbacrule.py` | Lookup plugin for HBAC rule state inspection and access testing |
| `execution-environment/eigenstate-idm/` | Ready-to-build AAP execution environment scaffold for IdM-backed automation |
| `roles/aap_execution_environment/` | Role that renders, builds, smokes, pushes, and optionally registers the AAP EE |
| `roles/openshift_idm_oidc_validation/` | Role that renders OpenShift OAuth/OIDC examples and validates IdM group evidence |
| `roles/keycloak_idm_federation_validation/` | Role that validates Keycloak federation and OIDC claim evidence |
| `roles/openshift_breakglass_validation/` | Role that validates OpenShift breakglass groups, controls, and RBAC evidence |
| `roles/kubernetes_secret_from_idm_vault/` | Role that renders review-first Kubernetes Secret manifests from IdM vault material |
| `roles/kubernetes_tls_from_idm_cert/` | Role that renders review-first Kubernetes TLS Secret manifests from certificate material |
| `roles/keytab_secret_render/` | Role that renders review-first Kubernetes Secret manifests for Kerberos keytab delivery |
| `roles/idm_readiness_report/` | Role that renders read-only IdM readiness evidence in JSON, YAML, and Markdown |
| `roles/certificate_inventory_report/` | Role that renders certificate inventory evidence without private keys |
| `roles/keytab_rotation_candidates/` | Role that reports keytab rotation candidates without keytab bytes |
| `roles/temporary_access_report/` | Role that reports temporary access windows and controls |
| `roles/policy_drift_report/` | Role that reports policy drift without remediation |
| `playbooks/aap-ee-*.yml` | Wrapper playbooks for the AAP EE render, build, smoke, push, and Controller registration path |
| `playbooks/render-openshift-oidc-config.yml` | Render-only OpenShift OAuth/OIDC validation wrapper |
| `playbooks/validate-openshift-*.yml` | Validation-only OpenShift identity and breakglass wrappers |
| `playbooks/validate-keycloak-idm-claims.yml` | Validation-only Keycloak federation wrapper |
| `playbooks/render-kubernetes-*.yml` and `playbooks/render-keytab-secret.yml` | Render-only workload Secret delivery wrappers |
| `playbooks/report-*.yml` | Wrapper playbooks for read-only reporting workflows |
| `docs/` | Operator and maintainer documentation aligned with the collection interface |
| `scripts/validate-collection.sh` | Lightweight repo validation for YAML, plugin syntax, and collection build hygiene |
| `Makefile` | Wrapper for repo validation targets |
| `llms.txt` | Project-level navigation file for model consumers |
| `CITATION.cff` | Citation metadata for GitHub and downstream tooling |
| `CHANGELOG.md` | Release-history placeholder for Galaxy and repo hygiene |
| `meta/runtime.yml` | Collection runtime metadata |

## Author

Greg Procunier

## License

GPL-3.0-or-later. See [COPYING](https://github.com/gprocunier/eigenstate-ipa/blob/main/COPYING).

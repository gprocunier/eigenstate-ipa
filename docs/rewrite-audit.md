---
layout: default
title: Rewrite Audit
diataxis: reference
diataxis_type: reference
audience: Documentation maintainers
outcome: Classify current documentation and code surfaces before the Diataxis rewrite.
authority_boundary:
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: audit
description: Documentation inventory and governance map for the Diataxis rewrite.
---

# Rewrite Audit

This audit records the current public documentation and code surface before the
Diataxis rewrite. It is an implementation map, not reader-facing product copy.

## Current Docs Inventory

| Path | Title | Current type | Likely target | Action | Source dependencies |
| --- | --- | --- | --- | --- | --- |
| `docs/README.md` | Docs README | local index | Start / reference index | merge | `docs/index.md`, `llms.txt` |
| `docs/index.md` | eigenstate.ipa | homepage | Home | rewrite | `README.md`, `llms.txt`, all surfaces |
| `docs/documentation-map.md` | Documentation Map | navigation map | Start | rewrite | all current docs |
| `docs/capabilities.md` | Capabilities | capability overview | Explanation / reference index | merge | plugin and role inventory |
| `docs/aap-ee-disconnected-build.md` | AAP EE Disconnected Build | task guide | How-to | rewrite | `roles/aap_execution_environment/`, `execution-environment/eigenstate-idm/`, `playbooks/aap-ee-*.yml` |
| `docs/aap-ee-quickstart.md` | AAP EE Quickstart | task guide | Tutorial / how-to | rewrite | `roles/aap_execution_environment/`, `playbooks/aap-ee-render.yml`, `playbooks/aap-ee-build.yml`, `playbooks/aap-ee-smoke.yml` |
| `docs/aap-ee-troubleshooting.md` | AAP EE Troubleshooting | troubleshooting | How-to / reference | merge | `roles/aap_execution_environment/`, EE scaffold |
| `docs/aap-ee-validation-walkthrough.md` | AAP EE Validation Walkthrough | walkthrough | Tutorial | rewrite | `playbooks/aap-ee-smoke.yml`, `tests/test_aap_execution_environment_role.py` |
| `docs/aap-idm-workflow-roles.md` | AAP IdM Workflow Roles | role guide | Reference / how-to | rewrite | `roles/sealed_artifact_delivery/`, `roles/temporary_access_window/`, `roles/cert_expiry_report/` |
| `docs/aap-idm-workflow-validation-walkthrough.md` | AAP IdM Workflow Validation Walkthrough | walkthrough | Tutorial | rewrite | `playbooks/aap-idm-workflow-*.yml`, AAP workflow role tests |
| `docs/aap-integration.md` | AAP Integration | integration guide | Explanation / how-to | rewrite | EE role, AAP wrapper playbooks |
| `docs/cert-capabilities.md` | IdM Cert Capabilities | capability page | Explanation | merge | `plugins/lookup/cert.py`, `plugins/modules/cert_request.py` |
| `docs/cert-expiry-report-role.md` | Cert Expiry Report Role | role guide | Reference / how-to | rewrite | `roles/cert_expiry_report/`, `playbooks/cert-expiry-report.yml` |
| `docs/cert-plugin.md` | IdM Cert Plugin | plugin reference | Reference | rewrite | `plugins/lookup/cert.py`, `tests/test_cert.py` |
| `docs/cert-request-module.md` | Cert Request Module | module reference | Reference | rewrite | `plugins/modules/cert_request.py`, `tests/test_cert_request_module.py` |
| `docs/cert-use-cases.md` | IdM Cert Use Cases | use cases | How-to | rewrite | cert lookup and module |
| `docs/certificate-inventory-report.md` | Certificate Inventory Report | report guide | Reference / how-to | rewrite | `roles/certificate_inventory_report/`, `playbooks/report-certificate-inventory.yml` |
| `docs/compatibility-policy.md` | Compatibility Policy | policy | Reference | keep | `meta/runtime.yml`, tests, release validation |
| `docs/dns-capabilities.md` | DNS Capabilities | capability page | Explanation | merge | `plugins/lookup/dns.py` |
| `docs/dns-plugin.md` | DNS Plugin | plugin reference | Reference | rewrite | `plugins/lookup/dns.py`, `tests/test_dns.py` |
| `docs/dns-use-cases.md` | DNS Use Cases | use cases | How-to | rewrite | `plugins/lookup/dns.py` |
| `docs/ephemeral-access-capabilities.md` | Ephemeral Access Capabilities | capability page | Explanation | merge | `plugins/modules/user_lease.py`, temporary access roles |
| `docs/hbacrule-capabilities.md` | HBAC Rule Capabilities | capability page | Explanation | merge | `plugins/lookup/hbacrule.py` |
| `docs/hbacrule-plugin.md` | HBAC Rule Plugin | plugin reference | Reference | rewrite | `plugins/lookup/hbacrule.py`, `tests/test_hbacrule.py` |
| `docs/hbacrule-use-cases.md` | HBAC Rule Use Cases | use cases | How-to | rewrite | `plugins/lookup/hbacrule.py` |
| `docs/inventory-capabilities.md` | Inventory Capabilities | capability page | Explanation | merge | `plugins/inventory/idm.py` |
| `docs/inventory-plugin.md` | Inventory Plugin | plugin reference | Reference | rewrite | `plugins/inventory/idm.py`, `tests/test_inventory.py` |
| `docs/inventory-use-cases.md` | Inventory Use Cases | use cases | Tutorial / how-to | rewrite | `plugins/inventory/idm.py`, integration inventory |
| `docs/keytab-capabilities.md` | Keytab Capabilities | capability page | Explanation | merge | `plugins/lookup/keytab.py`, `plugins/modules/keytab_manage.py` |
| `docs/keytab-delivery-to-workloads.md` | Keytab Delivery To Workloads | workload guide | How-to | rewrite | `roles/keytab_secret_render/`, `playbooks/render-keytab-secret.yml` |
| `docs/keytab-manage-module.md` | Keytab Manage Module | module reference | Reference | rewrite | `plugins/modules/keytab_manage.py`, `tests/test_keytab_manage.py` |
| `docs/keytab-plugin.md` | Keytab Plugin | plugin reference | Reference | rewrite | `plugins/lookup/keytab.py`, `tests/test_keytab.py` |
| `docs/keytab-rotation-candidate-report.md` | Keytab Rotation Candidate Report | report guide | Reference / how-to | rewrite | `roles/keytab_rotation_candidates/`, `playbooks/report-keytab-rotation-candidates.yml` |
| `docs/keytab-use-cases.md` | Keytab Use Cases | use cases | How-to | rewrite | keytab lookup and module |
| `docs/kubernetes-secret-from-idm-vault.md` | Kubernetes Secret From IdM Vault | workload guide | How-to | rewrite | `roles/kubernetes_secret_from_idm_vault/`, `playbooks/render-kubernetes-secret-from-idm-vault.yml` |
| `docs/kubernetes-tls-from-idm-cert.md` | Kubernetes TLS From IdM Certificate | workload guide | How-to | rewrite | `roles/kubernetes_tls_from_idm_cert/`, `playbooks/render-kubernetes-tls-secret-from-idm-cert.yml` |
| `docs/mutation-surface-migration.md` | Mutation Surface Migration | migration guide | How-to / explanation | rewrite | keytab and cert lookup/module pairs |
| `docs/openshift-breakglass-validation.md` | OpenShift Breakglass Validation | validation guide | How-to | rewrite | `roles/openshift_breakglass_validation/`, `playbooks/validate-openshift-breakglass-path.yml` |
| `docs/openshift-developer-use-cases.md` | OpenShift Developer Use Cases | use cases | How-to | merge | OpenShift and workload roles |
| `docs/openshift-identity-validation-walkthrough.md` | OpenShift Identity Validation Walkthrough | walkthrough | Tutorial | rewrite | OpenShift validation roles and playbooks |
| `docs/openshift-keycloak-idm-reference.md` | OpenShift Keycloak IdM Reference | integration reference | Reference / explanation | rewrite | `roles/keycloak_idm_federation_validation/` |
| `docs/openshift-ldap-fallback.md` | OpenShift LDAP Fallback | explanation | Explanation | keep | OpenShift identity role docs |
| `docs/openshift-operator-use-cases.md` | OpenShift Operator Use Cases | use cases | How-to | merge | OpenShift validation roles |
| `docs/openshift-primer.md` | OpenShift Ecosystem Primer | primer | Explanation / start route | rewrite | OpenShift validation and workload roles |
| `docs/openshift-quay-use-cases.md` | OpenShift Quay Use Cases | use cases | How-to | merge | OpenShift routes, IdM policy lookups |
| `docs/openshift-rhacm-use-cases.md` | OpenShift RHACM Use Cases | use cases | How-to | merge | OpenShift routes, reporting roles |
| `docs/openshift-rhacs-use-cases.md` | OpenShift RHACS Use Cases | use cases | How-to | merge | OpenShift routes, policy reporting |
| `docs/openshift-rhoso-operator-use-cases.md` | RHOSO Operator Use Cases | use cases | How-to | merge | OpenShift/RHOSO route docs |
| `docs/openshift-rhoso-tenant-use-cases.md` | RHOSO Tenant Use Cases | use cases | How-to | merge | OpenShift/RHOSO route docs |
| `docs/openshift-rhoso-use-cases.md` | OpenShift RHOSO Use Cases | use cases | How-to | merge | OpenShift/RHOSO route docs |
| `docs/otp-capabilities.md` | OTP Capabilities | capability page | Explanation | merge | `plugins/lookup/otp.py` |
| `docs/otp-plugin.md` | OTP Plugin | plugin reference | Reference | rewrite | `plugins/lookup/otp.py`, `tests/test_otp.py` |
| `docs/otp-use-cases.md` | OTP Use Cases | use cases | How-to | rewrite | `plugins/lookup/otp.py` |
| `docs/policy-drift-report.md` | Policy Drift Report | report guide | Reference / how-to | rewrite | `roles/policy_drift_report/`, `playbooks/report-policy-drift.yml` |
| `docs/principal-capabilities.md` | Principal Capabilities | capability page | Explanation | merge | `plugins/lookup/principal.py` |
| `docs/principal-plugin.md` | Principal Plugin | plugin reference | Reference | rewrite | `plugins/lookup/principal.py`, `tests/test_principal.py` |
| `docs/principal-use-cases.md` | Principal Use Cases | use cases | How-to | rewrite | `plugins/lookup/principal.py`, service onboarding flows |
| `docs/readiness-report-schema.md` | Readiness Report Schema | schema guide | Reference | rewrite | report role templates |
| `docs/release-process.md` | Release Process | process reference | Reference | keep | `scripts/validate-collection.sh`, metadata files |
| `docs/reporting-overview.md` | Reporting Overview | overview | Explanation / how-to | rewrite | reporting roles and report playbooks |
| `docs/rotation-capabilities.md` | Rotation Capabilities | capability page | Explanation | merge | vault, keytab, cert, report surfaces |
| `docs/rotation-use-cases.md` | Rotation Use Cases | use cases | How-to | rewrite | vault write, keytab manage, cert request |
| `docs/sealed-artifact-delivery-role.md` | Sealed Artifact Delivery Role | role guide | Reference / how-to | rewrite | `roles/sealed_artifact_delivery/`, `playbooks/sealed-artifact-delivery.yml` |
| `docs/selinuxmap-capabilities.md` | SELinux Map Capabilities | capability page | Explanation | merge | `plugins/lookup/selinuxmap.py` |
| `docs/selinuxmap-plugin.md` | SELinux Map Plugin | plugin reference | Reference | rewrite | `plugins/lookup/selinuxmap.py`, `tests/test_selinuxmap.py` |
| `docs/selinuxmap-use-cases.md` | SELinux Map Use Cases | use cases | How-to | rewrite | `plugins/lookup/selinuxmap.py` |
| `docs/sudo-capabilities.md` | Sudo Capabilities | capability page | Explanation | merge | `plugins/lookup/sudo.py` |
| `docs/sudo-plugin.md` | Sudo Plugin | plugin reference | Reference | rewrite | `plugins/lookup/sudo.py`, `tests/test_sudo.py` |
| `docs/sudo-use-cases.md` | Sudo Use Cases | use cases | How-to | rewrite | `plugins/lookup/sudo.py` |
| `docs/support-matrix.md` | Support Matrix | compatibility reference | Reference | keep | `meta/runtime.yml`, CI validation |
| `docs/temporary-access-report.md` | Temporary Access Report | report guide | Reference / how-to | rewrite | `roles/temporary_access_report/`, `playbooks/report-temporary-access.yml` |
| `docs/temporary-access-window-role.md` | Temporary Access Window Role | role guide | Reference / how-to | rewrite | `roles/temporary_access_window/`, `playbooks/temporary-access-window.yml` |
| `docs/test-strategy.md` | Test Strategy | validation reference | Reference | keep | `tests/`, `scripts/validate-collection.sh` |
| `docs/user-lease-capabilities.md` | User Lease Capabilities | capability page | Explanation | merge | `plugins/modules/user_lease.py` |
| `docs/user-lease-plugin.md` | User Lease Module | module reference | Reference | rewrite | `plugins/modules/user_lease.py`, `tests/test_user_lease.py` |
| `docs/user-lease-rbac-setup.md` | User Lease RBAC Setup | setup guide | How-to | rewrite | `plugins/modules/user_lease.py`, temporary access role |
| `docs/user-lease-use-cases.md` | User Lease Use Cases | use cases | How-to | rewrite | user lease module and roles |
| `docs/user-lease-validation-walkthrough.md` | User Lease Validation Walkthrough | walkthrough | Tutorial | rewrite | `plugins/modules/user_lease.py`, `docs/user-lease.cast` |
| `docs/vault-capabilities.md` | IdM Vault Capabilities | capability page | Explanation | merge | `plugins/lookup/vault.py` |
| `docs/vault-cyberark-primer.md` | Vault And CyberArk Primer | comparison primer | Explanation | rewrite | vault lookup/module, keytab and cert boundaries |
| `docs/vault-plugin.md` | IdM Vault Plugin | plugin reference | Reference | rewrite | `plugins/lookup/vault.py`, `tests/test_vault.py` |
| `docs/vault-use-cases.md` | IdM Vault Use Cases | use cases | How-to | rewrite | `plugins/lookup/vault.py` |
| `docs/vault-write-capabilities.md` | IdM Vault Write Capabilities | capability page | Explanation | merge | `plugins/modules/vault_write.py` |
| `docs/vault-write-plugin.md` | IdM Vault Write Module | module reference | Reference | rewrite | `plugins/modules/vault_write.py`, `tests/test_vault_write.py` |
| `docs/vault-write-use-cases.md` | IdM Vault Write Use Cases | use cases | How-to | rewrite | `plugins/modules/vault_write.py` |
| `docs/workload-secret-delivery-controls.md` | Workload Secret Delivery Controls | controls guide | Explanation / how-to | rewrite | Kubernetes secret, TLS, and keytab render roles |

## Code Surface Inventory

### Inventory Plugin

| Surface | Purpose | Target reference |
| --- | --- | --- |
| `plugins/inventory/idm.py` | Builds live inventory from IdM hosts, groups, netgroups, HBAC scope, and selected host attributes. | `docs/reference/inventory/idm.md` |

### Lookup Plugins

| Surface | Purpose | Target reference |
| --- | --- | --- |
| `plugins/lookup/vault.py` | Retrieves, shows, and searches IdM vault material and metadata. | `docs/reference/lookups/vault.md` |
| `plugins/lookup/principal.py` | Reads user, host, and service principal state. | `docs/reference/lookups/principal.md` |
| `plugins/lookup/keytab.py` | Retrieves or explicitly generates Kerberos keytabs through platform tooling. | `docs/reference/lookups/keytab.md` |
| `plugins/lookup/cert.py` | Requests, retrieves, and searches IdM CA certificates. | `docs/reference/lookups/cert.md` |
| `plugins/lookup/otp.py` | Issues and inspects OTP tokens and host enrollment passwords. | `docs/reference/lookups/otp.md` |
| `plugins/lookup/dns.py` | Reads IdM DNS zones and records. | `docs/reference/lookups/dns.md` |
| `plugins/lookup/selinuxmap.py` | Reads SELinux user map state and HBAC-linked scope. | `docs/reference/lookups/selinuxmap.md` |
| `plugins/lookup/sudo.py` | Reads sudo rules, commands, and command groups. | `docs/reference/lookups/sudo.md` |
| `plugins/lookup/hbacrule.py` | Reads HBAC rules and runs live access tests. | `docs/reference/lookups/hbacrule.md` |

### Modules And Shared Utilities

| Surface | Purpose | Target reference |
| --- | --- | --- |
| `plugins/modules/vault_write.py` | Creates, modifies, archives, and deletes IdM vaults. | `docs/reference/modules/vault_write.md` |
| `plugins/modules/keytab_manage.py` | Retrieves, deploys, or rotates keytabs with explicit rotation confirmation. | `docs/reference/modules/keytab_manage.md` |
| `plugins/modules/cert_request.py` | Requests IdM CA certificates from CSRs with metadata-first returns. | `docs/reference/modules/cert_request.md` |
| `plugins/modules/user_lease.py` | Sets, clears, or expires user access attributes in IdM. | `docs/reference/modules/user_lease.md` |
| `plugins/module_utils/ipa_client.py` | Shared IdM client, Kerberos, and API utility layer. | `docs/reference/authentication.md` |

### Roles

| Role | Purpose | Target reference |
| --- | --- | --- |
| `roles/aap_execution_environment/` | Render, build, smoke, push, and register the IdM execution environment. | `docs/reference/roles/aap_execution_environment.md` |
| `roles/openshift_idm_oidc_validation/` | Render OpenShift OAuth/OIDC examples and validate IdM group evidence. | `docs/reference/roles/openshift_identity.md` |
| `roles/keycloak_idm_federation_validation/` | Validate Keycloak federation and claim evidence. | `docs/reference/roles/openshift_identity.md` |
| `roles/openshift_breakglass_validation/` | Validate breakglass groups, controls, and report evidence. | `docs/reference/roles/openshift_identity.md` |
| `roles/kubernetes_secret_from_idm_vault/` | Render review-first Secret manifests from IdM vault material. | `docs/reference/roles/workload_secret_delivery.md` |
| `roles/kubernetes_tls_from_idm_cert/` | Render review-first TLS Secret manifests from certificate material. | `docs/reference/roles/workload_secret_delivery.md` |
| `roles/keytab_secret_render/` | Render review-first keytab Secret manifests. | `docs/reference/roles/workload_secret_delivery.md` |
| `roles/sealed_artifact_delivery/` | Retrieve, stage, hand off, and report sealed artifact delivery. | `docs/reference/roles/workload_secret_delivery.md` |
| `roles/idm_readiness_report/` | Render read-only IdM readiness evidence. | `docs/reference/roles/reports.md` |
| `roles/cert_expiry_report/` | Render certificate expiry evidence. | `docs/reference/roles/reports.md` |
| `roles/certificate_inventory_report/` | Render certificate inventory evidence. | `docs/reference/roles/reports.md` |
| `roles/keytab_rotation_candidates/` | Render keytab rotation candidate evidence without keytab bytes. | `docs/reference/roles/reports.md` |
| `roles/temporary_access_report/` | Render temporary access evidence. | `docs/reference/roles/reports.md` |
| `roles/policy_drift_report/` | Render policy drift evidence without remediation. | `docs/reference/roles/reports.md` |
| `roles/temporary_access_window/` | Open, expire, clear, preflight, and report temporary access windows. | `docs/reference/roles/temporary_access.md` |

### Playbooks

| Playbook | Purpose | Target reference |
| --- | --- | --- |
| `playbooks/aap-ee-render.yml` | Render the AAP EE build context. | `docs/reference/playbooks.md` |
| `playbooks/aap-ee-build.yml` | Build the AAP EE image. | `docs/reference/playbooks.md` |
| `playbooks/aap-ee-smoke.yml` | Smoke test the AAP EE image. | `docs/reference/playbooks.md` |
| `playbooks/aap-ee-push.yml` | Push the AAP EE image. | `docs/reference/playbooks.md` |
| `playbooks/aap-ee-register-controller.yml` | Register the AAP EE in Controller. | `docs/reference/playbooks.md` |
| `playbooks/aap-idm-workflow-static-validation.yml` | Validate AAP IdM workflow role wiring without IdM. | `docs/reference/playbooks.md` |
| `playbooks/aap-idm-workflow-live-smoke.yml` | Run a live IdM smoke path. | `docs/reference/playbooks.md` |
| `playbooks/cert-expiry-report.yml` | Generate certificate expiry evidence. | `docs/reference/playbooks.md` |
| `playbooks/openshift-identity-static-validation.yml` | Validate OpenShift identity roles without live services. | `docs/reference/playbooks.md` |
| `playbooks/render-openshift-oidc-config.yml` | Render OpenShift OAuth/OIDC configuration. | `docs/reference/playbooks.md` |
| `playbooks/validate-openshift-idm-groups.yml` | Validate OpenShift IdM group inputs. | `docs/reference/playbooks.md` |
| `playbooks/validate-keycloak-idm-claims.yml` | Validate Keycloak IdM claim inputs. | `docs/reference/playbooks.md` |
| `playbooks/validate-openshift-breakglass-path.yml` | Validate OpenShift breakglass inputs. | `docs/reference/playbooks.md` |
| `playbooks/render-kubernetes-secret-from-idm-vault.yml` | Render a Kubernetes Secret manifest from IdM vault material. | `docs/reference/playbooks.md` |
| `playbooks/render-kubernetes-tls-secret-from-idm-cert.yml` | Render a Kubernetes TLS Secret manifest from certificate material. | `docs/reference/playbooks.md` |
| `playbooks/render-keytab-secret.yml` | Render a keytab Secret manifest. | `docs/reference/playbooks.md` |
| `playbooks/workload-secret-delivery-static-validation.yml` | Validate workload Secret delivery roles without a live cluster. | `docs/reference/playbooks.md` |
| `playbooks/report-idm-readiness.yml` | Render IdM readiness evidence. | `docs/reference/playbooks.md` |
| `playbooks/report-certificate-inventory.yml` | Render certificate inventory evidence. | `docs/reference/playbooks.md` |
| `playbooks/report-keytab-rotation-candidates.yml` | Render keytab rotation candidate evidence. | `docs/reference/playbooks.md` |
| `playbooks/report-temporary-access.yml` | Render temporary access evidence. | `docs/reference/playbooks.md` |
| `playbooks/report-policy-drift.yml` | Render policy drift evidence. | `docs/reference/playbooks.md` |
| `playbooks/reporting-static-validation.yml` | Validate reporting roles. | `docs/reference/playbooks.md` |
| `playbooks/sealed-artifact-delivery.yml` | Deliver a sealed artifact from IdM vault material. | `docs/reference/playbooks.md` |
| `playbooks/temporary-access-window.yml` | Manage a temporary access window. | `docs/reference/playbooks.md` |

### Execution Environment

| Path | Purpose | Target reference |
| --- | --- | --- |
| `execution-environment/eigenstate-idm/` | Ready-to-build execution environment scaffold with Ansible, Python, bindep, and collection requirements. | `docs/reference/execution-environment/eigenstate-idm.md` |

### Tests

| Area | Files | Coverage target |
| --- | --- | --- |
| Plugin and module unit tests | `tests/test_inventory.py`, `tests/test_vault.py`, `tests/test_principal.py`, `tests/test_keytab.py`, `tests/test_cert.py`, `tests/test_otp.py`, `tests/test_dns.py`, `tests/test_selinuxmap.py`, `tests/test_sudo.py`, `tests/test_hbacrule.py`, `tests/test_vault_write.py`, `tests/test_keytab_manage.py`, `tests/test_cert_request_module.py`, `tests/test_user_lease.py` | Reference option and return claims |
| Role structure and argument specs | `tests/test_*_role_structure.py`, `tests/test_*_argument_specs.py`, role-specific tests | Role reference and playbook syntax |
| Secret safety tests | `tests/test_*_secret_safety.py`, `tests/test_reporting_secret_safety.py` | Secret-handling guidance |
| Compatibility and integration fixtures | `tests/test_compatibility_warnings.py`, `tests/integration/*.yml` | Support matrix and tutorial assumptions |

## Proposed New Docs Tree

```text
docs/
  index.md
  start.md
  tutorials/
    index.md
    first-idm-inventory.md
    first-vault-retrieval.md
    build-aap-execution-environment.md
    service-onboarding-with-principal-keytab-cert.md
    render-workload-secret.md
    temporary-access-window.md
    readiness-report.md
  how-to/
    index.md
    use-idm-as-live-inventory.md
    retrieve-idm-vault-secret.md
    manage-idm-vault-lifecycle.md
    query-principal-state.md
    retrieve-keytab.md
    rotate-keytab-explicitly.md
    request-idm-certificate.md
    issue-otp-or-host-enrollment-password.md
    inspect-dns-state.md
    test-hbac-access.md
    inspect-sudo-policy.md
    inspect-selinux-map-scope.md
    open-temporary-access-window.md
    render-openshift-identity-evidence.md
    render-kubernetes-secret-from-idm-vault.md
    render-kubernetes-tls-from-idm-cert.md
    render-keytab-secret.md
    build-disconnected-aap-ee.md
    generate-operational-evidence.md
    migrate-side-effecting-lookups.md
  reference/
    index.md
    inventory/idm.md
    lookups/vault.md
    lookups/principal.md
    lookups/keytab.md
    lookups/cert.md
    lookups/otp.md
    lookups/dns.md
    lookups/selinuxmap.md
    lookups/sudo.md
    lookups/hbacrule.md
    modules/vault_write.md
    modules/keytab_manage.md
    modules/cert_request.md
    modules/user_lease.md
    roles/aap_execution_environment.md
    roles/openshift_identity.md
    roles/workload_secret_delivery.md
    roles/temporary_access.md
    roles/reports.md
    playbooks.md
    authentication.md
    return-shapes.md
    report-schemas.md
    execution-environment/eigenstate-idm.md
    support-matrix.md
    release-process.md
  explanation/
    index.md
    what-is-eigenstate-ipa.md
    idm-as-automation-state-plane.md
    authority-boundaries.md
    secret-boundary.md
    kerberos-keytab-boundary.md
    certificate-boundary.md
    temporary-access-boundary.md
    aap-execution-model.md
    openshift-identity-and-workload-model.md
    evidence-and-reporting-model.md
    comparison-vault-cyberark.md
    security-threat-model.md
  _templates/
  _data/
  _includes/
  _layouts/
  assets/
```

## Legacy URL Handling Plan

Keep current URLs available until the new tree has production content. When a
legacy page is replaced, use one of these routes:

- If the Jekyll build supports redirects, add a redirect from the legacy page to
  the new Diataxis page.
- If redirects are not available, keep a short moved-page stub at the legacy
  path with a canonical link to the new page.
- Preserve these first: `documentation-map.html`, `aap-ee-quickstart.html`,
  `aap-integration.html`, `vault-cyberark-primer.html`,
  `reporting-overview.html`, `openshift-primer.html`,
  `workload-secret-delivery-controls.html`,
  `ephemeral-access-capabilities.html`, all current `*-plugin.html` pages, all
  current module pages, `support-matrix.html`, `test-strategy.html`, and
  `release-process.html`.
- Do not delete legacy docs until replacement pages are written, linked, and
  validated.

## First Five Pages To Rewrite

1. `docs/index.md`
2. `docs/start.md`
3. `docs/explanation/idm-as-automation-state-plane.md`
4. `docs/explanation/authority-boundaries.md`
5. `docs/reference/index.md`

These pages set the reader route, the authority model, and the reference map
before long-tail migration begins.

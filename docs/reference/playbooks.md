---
layout: default
title: Playbook reference
diataxis: reference
diataxis_type: reference
audience: Operators and maintainers looking up exact facts
outcome: Exact source-verified reference for this Ansible collection surface.
authority_boundary:
  - collection
workflow_boundary: read-only
evidence_shape:
  - ansible-doc
public_status: rewritten
source_material:
  - ../../playbooks
last_verified: 2026-05-07
---

# Playbook reference

| Playbook | Name | Roles or imports | Boundary |
| --- | --- | --- | --- |
| `playbooks/aap-ee-build.yml` | Render and build eigenstate.ipa AAP execution environment | {{ playbook_dir }}/../roles/aap_execution_environment | mutating |
| `playbooks/aap-ee-push.yml` | Push eigenstate.ipa AAP execution environment image | {{ playbook_dir }}/../roles/aap_execution_environment | mutating |
| `playbooks/aap-ee-register-controller.yml` | Register eigenstate.ipa AAP execution environment in Controller | {{ playbook_dir }}/../roles/aap_execution_environment | mutating |
| `playbooks/aap-ee-render.yml` | Render eigenstate.ipa AAP execution environment build context | {{ playbook_dir }}/../roles/aap_execution_environment | mutating |
| `playbooks/aap-ee-smoke.yml` | Smoke test an eigenstate.ipa AAP execution environment image | {{ playbook_dir }}/../roles/aap_execution_environment | read-only |
| `playbooks/aap-idm-workflow-live-smoke.yml` | Run AAP IdM workflow live IdM smoke path |  | read-only |
| `playbooks/aap-idm-workflow-static-validation.yml` | Validate AAP IdM workflow role wiring without IdM |  | read-only |
| `playbooks/cert-expiry-report.yml` | Generate IdM certificate expiry report | eigenstate.ipa.cert_expiry_report | mutating |
| `playbooks/openshift-identity-static-validation.yml` | Validate OpenShift identity roles without live services |  | read-only |
| `playbooks/render-keytab-secret.yml` | Render Kubernetes Secret manifest for keytab delivery | eigenstate.ipa.keytab_secret_render | render-only |
| `playbooks/render-kubernetes-secret-from-idm-vault.yml` | Render Kubernetes Secret manifest from IdM vault material | eigenstate.ipa.kubernetes_secret_from_idm_vault | render-only |
| `playbooks/render-kubernetes-tls-secret-from-idm-cert.yml` | Render Kubernetes TLS Secret manifest from IdM certificate material | eigenstate.ipa.kubernetes_tls_from_idm_cert | render-only |
| `playbooks/render-openshift-oidc-config.yml` | Render OpenShift OAuth OIDC configuration | eigenstate.ipa.openshift_idm_oidc_validation | render-only |
| `playbooks/report-certificate-inventory.yml` | Render certificate inventory report |  | read-only |
| `playbooks/report-idm-readiness.yml` | Render IdM readiness report |  | read-only |
| `playbooks/report-keytab-rotation-candidates.yml` | Render keytab rotation candidate report |  | read-only |
| `playbooks/report-policy-drift.yml` | Render policy drift report |  | read-only |
| `playbooks/report-temporary-access.yml` | Render temporary access report |  | read-only |
| `playbooks/reporting-static-validation.yml` | Validate reporting roles without live systems |  | read-only |
| `playbooks/sealed-artifact-delivery.yml` | Deliver sealed artifact from IdM vault | eigenstate.ipa.sealed_artifact_delivery | mutating |
| `playbooks/temporary-access-window.yml` | Manage temporary access window in IdM | eigenstate.ipa.temporary_access_window | mutating |
| `playbooks/validate-keycloak-idm-claims.yml` | Validate Keycloak IdM claim inputs | eigenstate.ipa.keycloak_idm_federation_validation | mutating |
| `playbooks/validate-openshift-breakglass-path.yml` | Validate OpenShift breakglass identity path | eigenstate.ipa.openshift_breakglass_validation | mutating |
| `playbooks/validate-openshift-idm-groups.yml` | Validate OpenShift IdM group inputs | eigenstate.ipa.openshift_idm_oidc_validation | mutating |
| `playbooks/workload-secret-delivery-static-validation.yml` | Validate workload Secret delivery roles without a live cluster |  | read-only |

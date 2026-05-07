---
layout: default
title: Openshift Identity role reference
diataxis: reference
diataxis_type: reference
audience: Operators and maintainers looking up exact facts
outcome: Exact source-verified reference for this Ansible collection surface.
authority_boundary:
  - collection
workflow_boundary: render-only
evidence_shape:
  - ansible-doc
public_status: rewritten
source_material:
  - ../../roles/openshift_idm_oidc_validation/README.md
last_verified: 2026-05-07
---

# Openshift Identity role reference

| Role | Purpose | Defaults | Argument spec |
| --- | --- | --- | --- |
| `openshift_idm_oidc_validation` | Render an OpenShift OAuth/OIDC configuration example and validate local evidence | `roles/openshift_idm_oidc_validation/defaults/main.yml` | `roles/openshift_idm_oidc_validation/meta/argument_specs.yml` |
| `keycloak_idm_federation_validation` | Validate local evidence for a Keycloak realm that federates IdM or AD identities | `roles/keycloak_idm_federation_validation/defaults/main.yml` | `roles/keycloak_idm_federation_validation/meta/argument_specs.yml` |
| `openshift_breakglass_validation` | Validate local evidence for an OpenShift emergency-access model backed by IdM | `roles/openshift_breakglass_validation/defaults/main.yml` | `roles/openshift_breakglass_validation/meta/argument_specs.yml` |

## Variables

### `openshift_idm_oidc_validation`

| Default variable | Default value |
| --- | --- |
| `eigenstate_oidc_basename` | `openshift-idm-oidc` |
| `eigenstate_oidc_ca_configmap_name` | `` |
| `eigenstate_oidc_claims` | `{'preferred_username': ['preferred_username'], 'name': ['name'], 'email': ['email'], 'groups': ['groups']}` |
| `eigenstate_oidc_client_id` | `openshift` |
| `eigenstate_oidc_client_secret_name` | `openid-client-secret` |
| `eigenstate_oidc_expected_groups` | `ocp-platform-admins, ocp-developers` |
| `eigenstate_oidc_expected_principals` | `` |
| `eigenstate_oidc_expected_rbac_bindings` | `{'name': 'ocp-platform-admins-cluster-admin', 'kind': 'ClusterRoleBinding', 'role_ref_kind': 'ClusterRole', 'role_ref_name': 'cluster-admin', 'subjects': [{'kind': 'Group', 'name': 'ocp-platform-admins'}]}` |
| `eigenstate_oidc_fail_on_missing` | `true` |
| `eigenstate_oidc_idm_known_groups` | `ocp-platform-admins, ocp-developers` |
| `eigenstate_oidc_idm_known_principals` | `` |
| `eigenstate_oidc_issuer_url` | `https://keycloak.example.com/realms/openshift` |
| `eigenstate_oidc_mapping_method` | `claim` |
| `eigenstate_oidc_output_dir` | `./artifacts` |
| `eigenstate_oidc_render_config` | `true` |
| `eigenstate_oidc_render_report` | `true` |
| `eigenstate_oidc_report_formats` | `json, md` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_oidc_basename` | str | no | `openshift-idm-oidc` | Basename for rendered artifacts. |
| `eigenstate_oidc_ca_configmap_name` | str | no | `` | Optional ConfigMap name containing the issuer CA bundle. |
| `eigenstate_oidc_claims` | dict | no | `` | OpenShift OIDC claim mapping. |
| `eigenstate_oidc_client_id` | str | yes | `` | OpenShift OAuth OIDC client identifier. |
| `eigenstate_oidc_client_secret_name` | str | yes | `` | Name of the OpenShift Secret that stores the OIDC client secret. |
| `eigenstate_oidc_expected_groups` | list | no | `` | Group names expected in OIDC group claims. |
| `eigenstate_oidc_expected_principals` | list | no | `` | IdM principals referenced by the identity model. |
| `eigenstate_oidc_expected_rbac_bindings` | list | no | `` | Expected OpenShift RBAC bindings that consume OIDC groups. |
| `eigenstate_oidc_fail_on_missing` | bool | no | `true` | Fail validation when required groups or principals are absent. |
| `eigenstate_oidc_idm_known_groups` | list | no | `` | Locally supplied evidence of existing IdM groups. |
| `eigenstate_oidc_idm_known_principals` | list | no | `` | Locally supplied evidence of existing IdM principals. |
| `eigenstate_oidc_issuer_url` | str | yes | `` | OIDC issuer URL, typically a Keycloak realm endpoint. |
| `eigenstate_oidc_mapping_method` | str | no | `claim` | OpenShift identity mapping method. |
| `eigenstate_oidc_output_dir` | str | no | `./artifacts` | Directory for rendered config and reports. |
| `eigenstate_oidc_render_config` | bool | no | `true` | Render an OpenShift OAuth/OIDC configuration example. |
| `eigenstate_oidc_render_report` | bool | no | `true` | Render readiness report artifacts. |
| `eigenstate_oidc_report_formats` | list | no | `json, md` | Readiness report formats. |

### `keycloak_idm_federation_validation`

| Default variable | Default value |
| --- | --- |
| `eigenstate_keycloak_basename` | `keycloak-idm-federation` |
| `eigenstate_keycloak_configured_mappers` | `{'name': 'idm-groups', 'type': 'group-ldap-mapper'}, {'name': 'kerberos-principal', 'type': 'user-attribute-ldap-mapper'}` |
| `eigenstate_keycloak_configured_protocol_mappers` | `{'name': 'groups', 'claim': 'groups'}, {'name': 'preferred_username', 'claim': 'preferred_username'}` |
| `eigenstate_keycloak_expected_groups` | `ocp-platform-admins, ocp-developers` |
| `eigenstate_keycloak_expected_mappers` | `{'name': 'idm-groups', 'type': 'group-ldap-mapper'}, {'name': 'kerberos-principal', 'type': 'user-attribute-ldap-mapper'}` |
| `eigenstate_keycloak_expected_principals` | `` |
| `eigenstate_keycloak_fail_on_missing` | `true` |
| `eigenstate_keycloak_group_claim` | `groups` |
| `eigenstate_keycloak_idm_provider_alias` | `idm` |
| `eigenstate_keycloak_kerberos_enabled` | `true` |
| `eigenstate_keycloak_known_idm_groups` | `ocp-platform-admins, ocp-developers` |
| `eigenstate_keycloak_known_idm_principals` | `` |
| `eigenstate_keycloak_ldap_vendor` | `rhds` |
| `eigenstate_keycloak_output_dir` | `./artifacts` |
| `eigenstate_keycloak_realm` | `openshift` |
| `eigenstate_keycloak_render_report` | `true` |
| `eigenstate_keycloak_report_formats` | `json, md` |
| `eigenstate_keycloak_required_protocol_mappers` | `{'name': 'groups', 'claim': 'groups'}, {'name': 'preferred_username', 'claim': 'preferred_username'}` |
| `eigenstate_keycloak_spnego_enabled` | `true` |
| `eigenstate_keycloak_username_claim` | `preferred_username` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_keycloak_basename` | str | no | `keycloak-idm-federation` | Basename for rendered artifacts. |
| `eigenstate_keycloak_configured_mappers` | list | no | `` | Locally supplied evidence of configured federation mappers. |
| `eigenstate_keycloak_configured_protocol_mappers` | list | no | `` | Locally supplied evidence of configured protocol mappers. |
| `eigenstate_keycloak_expected_groups` | list | no | `` | IdM groups expected to be federated through Keycloak. |
| `eigenstate_keycloak_expected_mappers` | list | no | `` | Required Keycloak LDAP/federation mappers. |
| `eigenstate_keycloak_expected_principals` | list | no | `` | IdM principals expected by the federation design. |
| `eigenstate_keycloak_fail_on_missing` | bool | no | `true` | Fail validation when required evidence is absent. |
| `eigenstate_keycloak_group_claim` | str | no | `groups` | OIDC group claim expected by OpenShift. |
| `eigenstate_keycloak_idm_provider_alias` | str | yes | `` | Keycloak user-federation provider alias for IdM or AD. |
| `eigenstate_keycloak_kerberos_enabled` | bool | no | `true` | Whether Kerberos federation is expected. |
| `eigenstate_keycloak_known_idm_groups` | list | no | `` | Locally supplied evidence of existing IdM groups. |
| `eigenstate_keycloak_known_idm_principals` | list | no | `` | Locally supplied evidence of existing IdM principals. |
| `eigenstate_keycloak_ldap_vendor` | str | no | `rhds` | LDAP vendor model used for validation notes. |
| `eigenstate_keycloak_output_dir` | str | no | `./artifacts` | Directory for readiness reports. |
| `eigenstate_keycloak_realm` | str | yes | `` | Keycloak realm that backs OpenShift OIDC. |
| `eigenstate_keycloak_render_report` | bool | no | `true` | Render readiness report artifacts. |
| `eigenstate_keycloak_report_formats` | list | no | `json, md` | Readiness report formats. |
| `eigenstate_keycloak_required_protocol_mappers` | list | no | `` | Required Keycloak OIDC protocol mappers. |
| `eigenstate_keycloak_spnego_enabled` | bool | no | `true` | Whether browser SPNEGO is expected. |
| `eigenstate_keycloak_username_claim` | str | no | `preferred_username` | OIDC username claim expected by OpenShift. |

### `openshift_breakglass_validation`

| Default variable | Default value |
| --- | --- |
| `eigenstate_breakglass_basename` | `openshift-breakglass` |
| `eigenstate_breakglass_documented_controls` | `named IdM group for emergency administrators, documented approval path, expiry or review process, audited OpenShift RBAC binding` |
| `eigenstate_breakglass_expected_groups` | `ocp-breakglass-admins` |
| `eigenstate_breakglass_expected_principals` | `breakglass-admin` |
| `eigenstate_breakglass_expected_rbac_bindings` | `{'name': 'ocp-breakglass-admins-cluster-admin', 'kind': 'ClusterRoleBinding', 'role_ref_kind': 'ClusterRole', 'role_ref_name': 'cluster-admin', 'subjects': [{'kind': 'Group', 'name': 'ocp-breakglass-admins'}]}` |
| `eigenstate_breakglass_fail_on_missing` | `true` |
| `eigenstate_breakglass_known_idm_groups` | `ocp-breakglass-admins` |
| `eigenstate_breakglass_known_idm_principals` | `breakglass-admin` |
| `eigenstate_breakglass_output_dir` | `./artifacts` |
| `eigenstate_breakglass_render_report` | `true` |
| `eigenstate_breakglass_report_formats` | `json, md` |
| `eigenstate_breakglass_required_controls` | `named IdM group for emergency administrators, documented approval path, expiry or review process, audited OpenShift RBAC binding` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_breakglass_basename` | str | no | `openshift-breakglass` | Basename for rendered artifacts. |
| `eigenstate_breakglass_documented_controls` | list | no | `` | Controls currently documented by the site operator. |
| `eigenstate_breakglass_expected_groups` | list | no | `` | IdM groups expected to hold emergency administrators. |
| `eigenstate_breakglass_expected_principals` | list | no | `` | IdM principals expected in the breakglass model. |
| `eigenstate_breakglass_expected_rbac_bindings` | list | no | `` | Expected OpenShift RBAC bindings for breakglass groups. |
| `eigenstate_breakglass_fail_on_missing` | bool | no | `true` | Fail validation when required evidence is absent. |
| `eigenstate_breakglass_known_idm_groups` | list | no | `` | Locally supplied evidence of existing IdM groups. |
| `eigenstate_breakglass_known_idm_principals` | list | no | `` | Locally supplied evidence of existing IdM principals. |
| `eigenstate_breakglass_output_dir` | str | no | `./artifacts` | Directory for readiness reports. |
| `eigenstate_breakglass_render_report` | bool | no | `true` | Render readiness report artifacts. |
| `eigenstate_breakglass_report_formats` | list | no | `json, md` | Readiness report formats. |
| `eigenstate_breakglass_required_controls` | list | no | `` | Required operational controls for emergency access. |

## Related Pages

- [Playbook reference](../playbooks.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

---
layout: default
title: Temporary Access role reference
diataxis: reference
diataxis_type: reference
audience: Operators and maintainers looking up exact facts
outcome: Exact source-verified reference for this Ansible collection surface.
authority_boundary:
  - collection
workflow_boundary: mutating
evidence_shape:
  - ansible-doc
public_status: rewritten
source_material:
  - ../../roles/temporary_access_window/README.md
last_verified: 2026-05-07
---

# Temporary Access role reference

| Role | Purpose | Defaults | Argument spec |
| --- | --- | --- | --- |
| `temporary_access_window` | Packages the `eigenstate.ipa.user_lease` module into an AAP-ready workflow that | `roles/temporary_access_window/defaults/main.yml` | `roles/temporary_access_window/meta/argument_specs.yml` |
| `temporary_access_report` | Renders read-only evidence for temporary access windows. The role is intended | `roles/temporary_access_report/defaults/main.yml` | `roles/temporary_access_report/meta/argument_specs.yml` |

## Variables

### `temporary_access_window`

| Default variable | Default value |
| --- | --- |
| `eigenstate_taw_clear_password_expiration` | `false` |
| `eigenstate_taw_fail_on_preflight_denied` | `true` |
| `eigenstate_taw_hbac_preflight_enabled` | `true` |
| `eigenstate_taw_hbac_service` | `sshd` |
| `eigenstate_taw_hbac_targethost` | `` |
| `eigenstate_taw_ipaadmin_password` | `` |
| `eigenstate_taw_ipaadmin_principal` | `lease-operator` |
| `eigenstate_taw_kerberos_keytab` | `` |
| `eigenstate_taw_no_log` | `false` |
| `eigenstate_taw_password_expiration` | `` |
| `eigenstate_taw_password_expiration_matches_principal` | `true` |
| `eigenstate_taw_principal_expiration` | `01:00` |
| `eigenstate_taw_report_dir` | `./artifacts` |
| `eigenstate_taw_report_enabled` | `true` |
| `eigenstate_taw_report_formats` | `json, md` |
| `eigenstate_taw_require_groups` | `` |
| `eigenstate_taw_selinux_maps` | `` |
| `eigenstate_taw_selinuxmap_preflight_enabled` | `false` |
| `eigenstate_taw_server` | `` |
| `eigenstate_taw_state` | `preflight` |
| `eigenstate_taw_sudo_preflight_enabled` | `false` |
| `eigenstate_taw_sudo_rules` | `` |
| `eigenstate_taw_username` | `` |
| `eigenstate_taw_verify` | `` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_taw_clear_password_expiration` | bool | no | `false` | Clear password expiration when state is clear. |
| `eigenstate_taw_hbac_preflight_enabled` | bool | no | `true` | Run hbactest before mutating lease state. |
| `eigenstate_taw_hbac_service` | str | no | `sshd` | HBAC service name used by hbactest. |
| `eigenstate_taw_hbac_targethost` | str | no | `` | HBAC target host used by hbactest. |
| `eigenstate_taw_ipaadmin_password` | str | no | `` | Password for the Kerberos principal. |
| `eigenstate_taw_ipaadmin_principal` | str | no | `lease-operator` | Kerberos principal used for IdM authentication. |
| `eigenstate_taw_kerberos_keytab` | str | no | `` | Keytab path for non-interactive Kerberos authentication. |
| `eigenstate_taw_no_log` | bool | no | `false` | Hide temporary access module output. |
| `eigenstate_taw_password_expiration` | raw | no | `` | Optional explicit password expiration. |
| `eigenstate_taw_password_expiration_matches_principal` | bool | no | `true` | Set password expiration to the principal lease end. |
| `eigenstate_taw_principal_expiration` | raw | no | `01:00` | Principal expiration for open state. |
| `eigenstate_taw_report_enabled` | bool | no | `true` | Whether to render metadata-only reports. |
| `eigenstate_taw_require_groups` | list | no | `` | Required direct IdM group memberships. |
| `eigenstate_taw_selinux_maps` | list | no | `` | SELinux user map names to inspect. |
| `eigenstate_taw_selinuxmap_preflight_enabled` | bool | no | `false` | Inspect named SELinux user maps before mutation. |
| `eigenstate_taw_server` | str | yes | `` | IdM server FQDN. |
| `eigenstate_taw_state` | str | no | `preflight` | Temporary access workflow state. |
| `eigenstate_taw_sudo_preflight_enabled` | bool | no | `false` | Inspect named sudo rules before mutation. |
| `eigenstate_taw_sudo_rules` | list | no | `` | Sudo rule names to inspect. |
| `eigenstate_taw_username` | str | yes | `` | IdM user receiving the temporary access window. |
| `eigenstate_taw_verify` | str | no | `` | IPA CA certificate path or false-like override. |

### `temporary_access_report`

| Default variable | Default value |
| --- | --- |
| `eigenstate_temporary_access_report_basename` | `temporary-access-report` |
| `eigenstate_temporary_access_report_context` | `static validation` |
| `eigenstate_temporary_access_report_formats` | `json, yaml, md` |
| `eigenstate_temporary_access_report_generated_at_utc` | `1970-01-01T00:00:00Z` |
| `eigenstate_temporary_access_report_output_dir` | `./artifacts` |
| `eigenstate_temporary_access_report_schema_version` | `1.0` |
| `eigenstate_temporary_access_report_site` | `example` |
| `eigenstate_temporary_access_report_windows` | `{'principal': 'contractor01', 'target': 'bastion.example.com', 'access_type': 'ssh', 'opened_at': '2026-05-01T14:00:00Z', 'expires_at': '2026-05-01T18:00:00Z', 'status': 'expired', 'controls': ['documented approval', 'expiry enforced in IdM', 'audited session path'], 'evidence': 'Principal expiration is before the report timestamp.'}` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_temporary_access_report_basename` | str | no | `temporary-access-report` | Basename for rendered report files. |
| `eigenstate_temporary_access_report_context` | str | no | `static validation` | Human-readable scope for this report run. |
| `eigenstate_temporary_access_report_formats` | list | no | `json, yaml, md` | Report formats to render. |
| `eigenstate_temporary_access_report_generated_at_utc` | str | no | `1970-01-01T00:00:00Z` | Deterministic UTC timestamp recorded in the report. |
| `eigenstate_temporary_access_report_output_dir` | str | no | `./artifacts` | Directory for report artifacts. |
| `eigenstate_temporary_access_report_schema_version` | str | no | `1.0` | Stable schema version for report consumers. |
| `eigenstate_temporary_access_report_site` | str | no | `example` | Site or environment label for the report. |
| `eigenstate_temporary_access_report_windows` | list | no | `` | Temporary access window metadata without passwords, tokens, or session payloads. |

## Related Pages

- [Playbook reference](/reference/playbooks.html)
- [Authority boundaries](/explanation/authority-boundaries.html)

---
layout: default
title: Reports role reference
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
  - ../../roles/idm_readiness_report/README.md
last_verified: 2026-05-07
---

# Reports role reference

| Role | Purpose | Defaults | Argument spec |
| --- | --- | --- | --- |
| `idm_readiness_report` | Renders deterministic IdM readiness evidence in JSON, YAML, and Markdown. | `roles/idm_readiness_report/defaults/main.yml` | `roles/idm_readiness_report/meta/argument_specs.yml` |
| `cert_expiry_report` | Finds IdM certificates matching an expiry or identity filter and renders JSON, | `roles/cert_expiry_report/defaults/main.yml` | `roles/cert_expiry_report/meta/argument_specs.yml` |
| `certificate_inventory_report` | Renders a safe certificate inventory report from explicit certificate metadata. | `roles/certificate_inventory_report/defaults/main.yml` | `roles/certificate_inventory_report/meta/argument_specs.yml` |
| `keytab_rotation_candidates` | Renders a read-only report of service or host principals that should be | `roles/keytab_rotation_candidates/defaults/main.yml` | `roles/keytab_rotation_candidates/meta/argument_specs.yml` |
| `policy_drift_report` | Renders a read-only comparison between expected and observed policy records. | `roles/policy_drift_report/defaults/main.yml` | `roles/policy_drift_report/meta/argument_specs.yml` |

## Variables

### `idm_readiness_report`

| Default variable | Default value |
| --- | --- |
| `eigenstate_idm_readiness_report_basename` | `idm-readiness-report` |
| `eigenstate_idm_readiness_report_checks` | `{'id': 'kerberos-auth', 'title': 'Kerberos authentication path', 'status': 'pass', 'severity': 'high', 'evidence': 'Controller has a documented Kerberos authentication method.', 'recommendation': 'Keep keytab or credential refresh under normal rotation control.'}, {'id': 'idm-api', 'title': 'IdM API reachability', 'status': 'pass', 'severity': 'high', 'evidence': 'IdM JSON-RPC endpoint is represented in the automation inventory.', 'recommendation': 'Monitor API availability from the execution environment subnet.'}` |
| `eigenstate_idm_readiness_report_context` | `static validation` |
| `eigenstate_idm_readiness_report_formats` | `json, yaml, md` |
| `eigenstate_idm_readiness_report_generated_at_utc` | `1970-01-01T00:00:00Z` |
| `eigenstate_idm_readiness_report_output_dir` | `./artifacts` |
| `eigenstate_idm_readiness_report_schema_version` | `1.0` |
| `eigenstate_idm_readiness_report_site` | `example` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_idm_readiness_report_basename` | str | no | `idm-readiness-report` | Basename for rendered report files. |
| `eigenstate_idm_readiness_report_checks` | list | no | `` | Readiness check records with id, title, status, evidence, and recommendation. |
| `eigenstate_idm_readiness_report_context` | str | no | `static validation` | Human-readable scope for this report run. |
| `eigenstate_idm_readiness_report_formats` | list | no | `json, yaml, md` | Report formats to render. |
| `eigenstate_idm_readiness_report_generated_at_utc` | str | no | `1970-01-01T00:00:00Z` | Deterministic UTC timestamp recorded in the report. |
| `eigenstate_idm_readiness_report_output_dir` | str | no | `./artifacts` | Directory for report artifacts. |
| `eigenstate_idm_readiness_report_schema_version` | str | no | `1.0` | Stable schema version for report consumers. |
| `eigenstate_idm_readiness_report_site` | str | no | `example` | Site or environment label for the report. |

### `cert_expiry_report`

| Default variable | Default value |
| --- | --- |
| `eigenstate_cert_report_basename` | `cert-expiry-report` |
| `eigenstate_cert_report_exactly` | `false` |
| `eigenstate_cert_report_fail_on_expiring` | `false` |
| `eigenstate_cert_report_fail_threshold_count` | `1` |
| `eigenstate_cert_report_formats` | `json, md, csv` |
| `eigenstate_cert_report_ipaadmin_password` | `` |
| `eigenstate_cert_report_ipaadmin_principal` | `admin` |
| `eigenstate_cert_report_kerberos_keytab` | `` |
| `eigenstate_cert_report_live_lookup_enabled` | `true` |
| `eigenstate_cert_report_output_dir` | `./artifacts` |
| `eigenstate_cert_report_principal` | `` |
| `eigenstate_cert_report_revocation_reason` | `` |
| `eigenstate_cert_report_server` | `` |
| `eigenstate_cert_report_state` | `present` |
| `eigenstate_cert_report_subject` | `` |
| `eigenstate_cert_report_valid_not_after_from` | `` |
| `eigenstate_cert_report_valid_not_after_to` | `` |
| `eigenstate_cert_report_verify` | `` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_cert_report_basename` | str | no | `cert-expiry-report` | Basename for rendered report files. |
| `eigenstate_cert_report_exactly` | bool | no | `false` | Match subject exactly. |
| `eigenstate_cert_report_fail_on_expiring` | bool | no | `false` | Fail when count meets or exceeds threshold. |
| `eigenstate_cert_report_fail_threshold_count` | int | no | `1` | Failure threshold count. |
| `eigenstate_cert_report_formats` | list | no | `json, md, csv` | Report formats to render. |
| `eigenstate_cert_report_ipaadmin_password` | str | no | `` | Password for the Kerberos principal. |
| `eigenstate_cert_report_ipaadmin_principal` | str | no | `admin` | Kerberos principal used for IdM authentication. |
| `eigenstate_cert_report_kerberos_keytab` | str | no | `` | Keytab path for non-interactive Kerberos authentication. |
| `eigenstate_cert_report_live_lookup_enabled` | bool | no | `true` | Whether the find task may contact IdM. |
| `eigenstate_cert_report_output_dir` | str | no | `./artifacts` | Directory for report artifacts. |
| `eigenstate_cert_report_principal` | str | no | `` | Host or service principal filter. |
| `eigenstate_cert_report_revocation_reason` | int | no | `` | Optional revocation reason filter. |
| `eigenstate_cert_report_server` | str | yes | `` | IdM server FQDN. |
| `eigenstate_cert_report_state` | str | no | `present` | Certificate report state. |
| `eigenstate_cert_report_subject` | str | no | `` | Certificate subject substring filter. |
| `eigenstate_cert_report_valid_not_after_from` | str | no | `` | Lower bound for certificate expiry date. |
| `eigenstate_cert_report_valid_not_after_to` | str | no | `` | Upper bound for certificate expiry date. |
| `eigenstate_cert_report_verify` | str | no | `` | IPA CA certificate path or false-like override. |

### `certificate_inventory_report`

| Default variable | Default value |
| --- | --- |
| `eigenstate_certificate_inventory_report_basename` | `certificate-inventory-report` |
| `eigenstate_certificate_inventory_report_certificates` | `{'principal': 'HTTP/app.example.com@EXAMPLE.COM', 'serial_number': '1001', 'subject': 'CN=app.example.com,O=EXAMPLE.COM', 'issuer': 'CN=Certificate Authority,O=EXAMPLE.COM', 'not_before': '2026-01-01T00:00:00Z', 'not_after': '2026-12-31T23:59:59Z', 'state': 'valid', 'profile_id': 'caIPAserviceCert', 'san_names': ['app.example.com'], 'rotation_required': False, 'evidence': 'Certificate is present and inside the expected renewal window.'}` |
| `eigenstate_certificate_inventory_report_context` | `static validation` |
| `eigenstate_certificate_inventory_report_formats` | `json, yaml, md` |
| `eigenstate_certificate_inventory_report_generated_at_utc` | `1970-01-01T00:00:00Z` |
| `eigenstate_certificate_inventory_report_output_dir` | `./artifacts` |
| `eigenstate_certificate_inventory_report_schema_version` | `1.0` |
| `eigenstate_certificate_inventory_report_site` | `example` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_certificate_inventory_report_basename` | str | no | `certificate-inventory-report` | Basename for rendered report files. |
| `eigenstate_certificate_inventory_report_certificates` | list | no | `` | Certificate inventory records without private keys or secret payloads. |
| `eigenstate_certificate_inventory_report_context` | str | no | `static validation` | Human-readable scope for this report run. |
| `eigenstate_certificate_inventory_report_formats` | list | no | `json, yaml, md` | Report formats to render. |
| `eigenstate_certificate_inventory_report_generated_at_utc` | str | no | `1970-01-01T00:00:00Z` | Deterministic UTC timestamp recorded in the report. |
| `eigenstate_certificate_inventory_report_output_dir` | str | no | `./artifacts` | Directory for report artifacts. |
| `eigenstate_certificate_inventory_report_schema_version` | str | no | `1.0` | Stable schema version for report consumers. |
| `eigenstate_certificate_inventory_report_site` | str | no | `example` | Site or environment label for the report. |

### `keytab_rotation_candidates`

| Default variable | Default value |
| --- | --- |
| `eigenstate_keytab_rotation_candidates_basename` | `keytab-rotation-candidates` |
| `eigenstate_keytab_rotation_candidates_context` | `static validation` |
| `eigenstate_keytab_rotation_candidates_formats` | `json, yaml, md` |
| `eigenstate_keytab_rotation_candidates_generated_at_utc` | `1970-01-01T00:00:00Z` |
| `eigenstate_keytab_rotation_candidates_output_dir` | `./artifacts` |
| `eigenstate_keytab_rotation_candidates_records` | `{'principal': 'HTTP/app.example.com@EXAMPLE.COM', 'owner': 'platform-services', 'location_hint': 'controller credential', 'last_rotated_at': '2026-01-01T00:00:00Z', 'max_age_days': 90, 'candidate': True, 'reason': 'Rotation review window has been reached.', 'remediation_workflow': 'separate opt-in rotation workflow'}` |
| `eigenstate_keytab_rotation_candidates_schema_version` | `1.0` |
| `eigenstate_keytab_rotation_candidates_site` | `example` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_keytab_rotation_candidates_basename` | str | no | `keytab-rotation-candidates` | Basename for rendered report files. |
| `eigenstate_keytab_rotation_candidates_context` | str | no | `static validation` | Human-readable scope for this report run. |
| `eigenstate_keytab_rotation_candidates_formats` | list | no | `json, yaml, md` | Report formats to render. |
| `eigenstate_keytab_rotation_candidates_generated_at_utc` | str | no | `1970-01-01T00:00:00Z` | Deterministic UTC timestamp recorded in the report. |
| `eigenstate_keytab_rotation_candidates_output_dir` | str | no | `./artifacts` | Directory for report artifacts. |
| `eigenstate_keytab_rotation_candidates_records` | list | no | `` | Principal metadata used to identify rotation candidates without keytab bytes. |
| `eigenstate_keytab_rotation_candidates_schema_version` | str | no | `1.0` | Stable schema version for report consumers. |
| `eigenstate_keytab_rotation_candidates_site` | str | no | `example` | Site or environment label for the report. |

### `policy_drift_report`

| Default variable | Default value |
| --- | --- |
| `eigenstate_policy_drift_report_basename` | `policy-drift-report` |
| `eigenstate_policy_drift_report_context` | `static validation` |
| `eigenstate_policy_drift_report_expected_policies` | `{'id': 'hbac-admin-ssh', 'kind': 'hbacrule', 'desired_state': 'enabled', 'owner': 'identity-platform'}` |
| `eigenstate_policy_drift_report_findings` | `{'id': 'hbac-admin-ssh', 'kind': 'hbacrule', 'status': 'in_sync', 'severity': 'low', 'expected': 'enabled', 'observed': 'enabled', 'remediation_workflow': 'none'}` |
| `eigenstate_policy_drift_report_formats` | `json, yaml, md` |
| `eigenstate_policy_drift_report_generated_at_utc` | `1970-01-01T00:00:00Z` |
| `eigenstate_policy_drift_report_observed_policies` | `{'id': 'hbac-admin-ssh', 'kind': 'hbacrule', 'observed_state': 'enabled', 'source': 'idm-fixture'}` |
| `eigenstate_policy_drift_report_output_dir` | `./artifacts` |
| `eigenstate_policy_drift_report_schema_version` | `1.0` |
| `eigenstate_policy_drift_report_site` | `example` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_policy_drift_report_basename` | str | no | `policy-drift-report` | Basename for rendered report files. |
| `eigenstate_policy_drift_report_context` | str | no | `static validation` | Human-readable scope for this report run. |
| `eigenstate_policy_drift_report_expected_policies` | list | no | `` | Expected policy records from the reference baseline. |
| `eigenstate_policy_drift_report_findings` | list | no | `` | Drift findings with remediation separated from this report workflow. |
| `eigenstate_policy_drift_report_formats` | list | no | `json, yaml, md` | Report formats to render. |
| `eigenstate_policy_drift_report_generated_at_utc` | str | no | `1970-01-01T00:00:00Z` | Deterministic UTC timestamp recorded in the report. |
| `eigenstate_policy_drift_report_observed_policies` | list | no | `` | Observed policy records from IdM, AAP, or cluster-adjacent fixtures. |
| `eigenstate_policy_drift_report_output_dir` | str | no | `./artifacts` | Directory for report artifacts. |
| `eigenstate_policy_drift_report_schema_version` | str | no | `1.0` | Stable schema version for report consumers. |
| `eigenstate_policy_drift_report_site` | str | no | `example` | Site or environment label for the report. |

## Related Pages

- [Playbook reference](/reference/playbooks.html)
- [Authority boundaries](/explanation/authority-boundaries.html)

---
layout: default
title: Workload Secret Delivery role reference
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
  - ../../roles/kubernetes_secret_from_idm_vault/README.md
last_verified: 2026-05-07
---

# Workload Secret Delivery role reference

| Role | Purpose | Defaults | Argument spec |
| --- | --- | --- | --- |
| `kubernetes_secret_from_idm_vault` | Render Kubernetes Secret manifests from IdM vault material with safe defaults. | `roles/kubernetes_secret_from_idm_vault/defaults/main.yml` | `roles/kubernetes_secret_from_idm_vault/meta/argument_specs.yml` |
| `kubernetes_tls_from_idm_cert` | Render Kubernetes TLS Secret manifests from certificate material that has been | `roles/kubernetes_tls_from_idm_cert/defaults/main.yml` | `roles/kubernetes_tls_from_idm_cert/meta/argument_specs.yml` |
| `keytab_secret_render` | Render Kubernetes Secret manifests for Kerberos keytab delivery to workloads. | `roles/keytab_secret_render/defaults/main.yml` | `roles/keytab_secret_render/meta/argument_specs.yml` |
| `sealed_artifact_delivery` | Retrieves an opaque sealed artifact from an IdM vault, stages it with | `roles/sealed_artifact_delivery/defaults/main.yml` | `roles/sealed_artifact_delivery/meta/argument_specs.yml` |

## Variables

### `kubernetes_secret_from_idm_vault`

| Default variable | Default value |
| --- | --- |
| `eigenstate_k8s_secret_annotations` | `{}` |
| `eigenstate_k8s_secret_apply` | `false` |
| `eigenstate_k8s_secret_basename` | `kubernetes-secret-from-idm-vault` |
| `eigenstate_k8s_secret_context` | `` |
| `eigenstate_k8s_secret_correlation_id` | `` |
| `eigenstate_k8s_secret_data` | `{'artifact': 'static-validation-value'}` |
| `eigenstate_k8s_secret_delegate_to` | `localhost` |
| `eigenstate_k8s_secret_ipaadmin_password` | `` |
| `eigenstate_k8s_secret_ipaadmin_principal` | `admin` |
| `eigenstate_k8s_secret_kerberos_keytab` | `` |
| `eigenstate_k8s_secret_kubeconfig` | `` |
| `eigenstate_k8s_secret_kubectl` | `kubectl` |
| `eigenstate_k8s_secret_labels` | `{'app.kubernetes.io/managed-by': 'eigenstate.ipa', 'app.kubernetes.io/component': 'workload-secret-delivery'}` |
| `eigenstate_k8s_secret_live_lookup_enabled` | `false` |
| `eigenstate_k8s_secret_name` | `idm-vault-secret` |
| `eigenstate_k8s_secret_namespace` | `default` |
| `eigenstate_k8s_secret_no_log` | `true` |
| `eigenstate_k8s_secret_output_dir` | `./artifacts` |
| `eigenstate_k8s_secret_render_only` | `true` |
| `eigenstate_k8s_secret_render_review_manifest` | `true` |
| `eigenstate_k8s_secret_server` | `` |
| `eigenstate_k8s_secret_service` | `` |
| `eigenstate_k8s_secret_type` | `Opaque` |
| `eigenstate_k8s_secret_username` | `` |
| `eigenstate_k8s_secret_vault_key` | `artifact` |
| `eigenstate_k8s_secret_vault_name` | `` |
| `eigenstate_k8s_secret_vault_scope` | `shared` |
| `eigenstate_k8s_secret_verify` | `` |
| `eigenstate_k8s_secret_write_payload_manifest` | `false` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_k8s_secret_annotations` | dict | no | `` | Additional safe annotations for rendered manifests. |
| `eigenstate_k8s_secret_apply` | bool | no | `false` | Apply the protected manifest with kubectl when explicitly enabled. |
| `eigenstate_k8s_secret_basename` | str | no | `kubernetes-secret-from-idm-vault` | Basename for rendered artifacts. |
| `eigenstate_k8s_secret_context` | str | no | `` | Kubernetes context required when apply is enabled. |
| `eigenstate_k8s_secret_correlation_id` | str | no | `` | Optional non-secret correlation identifier. |
| `eigenstate_k8s_secret_data` | dict | no | `` | Secret key/value data used when live IdM vault lookup is disabled. |
| `eigenstate_k8s_secret_delegate_to` | str | no | `localhost` | Host that performs live IdM lookup. |
| `eigenstate_k8s_secret_ipaadmin_password` | str | no | `` | Password used for IdM live lookup. |
| `eigenstate_k8s_secret_ipaadmin_principal` | str | no | `admin` | Principal used for IdM live lookup. |
| `eigenstate_k8s_secret_kerberos_keytab` | str | no | `` | Kerberos keytab path for live lookup. |
| `eigenstate_k8s_secret_kubeconfig` | str | no | `` | Kubeconfig path required when apply is enabled. |
| `eigenstate_k8s_secret_kubectl` | str | no | `kubectl` | kubectl command path. |
| `eigenstate_k8s_secret_labels` | dict | no | `` | Additional safe labels for rendered manifests. |
| `eigenstate_k8s_secret_live_lookup_enabled` | bool | no | `false` | Retrieve payload from IdM vault using the collection vault lookup. |
| `eigenstate_k8s_secret_name` | str | yes | `` | Kubernetes Secret name. |
| `eigenstate_k8s_secret_namespace` | str | yes | `` | Kubernetes namespace for the rendered Secret. |
| `eigenstate_k8s_secret_no_log` | bool | no | `true` | Hide secret-bearing task output. |
| `eigenstate_k8s_secret_output_dir` | str | no | `./artifacts` | Directory for rendered artifacts. |
| `eigenstate_k8s_secret_render_only` | bool | no | `true` | Refuse cluster apply behavior when true. |
| `eigenstate_k8s_secret_render_review_manifest` | bool | no | `true` | Render a review manifest with payload values redacted. |
| `eigenstate_k8s_secret_server` | str | no | `` | IdM server for live lookup. |
| `eigenstate_k8s_secret_service` | str | no | `` | Service vault owner for service-scoped live lookup. |
| `eigenstate_k8s_secret_type` | str | no | `Opaque` | Kubernetes Secret type. |
| `eigenstate_k8s_secret_username` | str | no | `` | User vault owner for user-scoped live lookup. |
| `eigenstate_k8s_secret_vault_key` | str | no | `artifact` | Kubernetes Secret data key used for live lookup payloads. |
| `eigenstate_k8s_secret_vault_name` | str | no | `` | IdM vault name for live lookup. |
| `eigenstate_k8s_secret_vault_scope` | str | no | `shared` | IdM vault scope for live lookup. |
| `eigenstate_k8s_secret_verify` | str | no | `` | IPA CA certificate path or verification mode. |
| `eigenstate_k8s_secret_write_payload_manifest` | bool | no | `false` | Write a protected manifest containing encoded payload values. |

### `kubernetes_tls_from_idm_cert`

| Default variable | Default value |
| --- | --- |
| `eigenstate_k8s_tls_annotations` | `{}` |
| `eigenstate_k8s_tls_apply` | `false` |
| `eigenstate_k8s_tls_basename` | `kubernetes-tls-from-idm-cert` |
| `eigenstate_k8s_tls_ca_certificate` | `` |
| `eigenstate_k8s_tls_certificate` | `static-validation-certificate` |
| `eigenstate_k8s_tls_context` | `` |
| `eigenstate_k8s_tls_correlation_id` | `` |
| `eigenstate_k8s_tls_kubeconfig` | `` |
| `eigenstate_k8s_tls_kubectl` | `kubectl` |
| `eigenstate_k8s_tls_labels` | `{'app.kubernetes.io/managed-by': 'eigenstate.ipa', 'app.kubernetes.io/component': 'workload-tls-delivery'}` |
| `eigenstate_k8s_tls_namespace` | `default` |
| `eigenstate_k8s_tls_no_log` | `true` |
| `eigenstate_k8s_tls_output_dir` | `./artifacts` |
| `eigenstate_k8s_tls_private_key` | `static-validation-private-key` |
| `eigenstate_k8s_tls_render_only` | `true` |
| `eigenstate_k8s_tls_render_review_manifest` | `true` |
| `eigenstate_k8s_tls_secret_name` | `idm-tls-secret` |
| `eigenstate_k8s_tls_write_payload_manifest` | `false` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_k8s_tls_annotations` | dict | no | `` | Additional safe annotations for rendered manifests. |
| `eigenstate_k8s_tls_apply` | bool | no | `false` | Apply the protected manifest with kubectl when explicitly enabled. |
| `eigenstate_k8s_tls_basename` | str | no | `kubernetes-tls-from-idm-cert` | Basename for rendered artifacts. |
| `eigenstate_k8s_tls_ca_certificate` | str | no | `` | Optional PEM CA certificate material. |
| `eigenstate_k8s_tls_certificate` | str | no | `` | PEM certificate material for tls.crt. |
| `eigenstate_k8s_tls_context` | str | no | `` | Kubernetes context required when apply is enabled. |
| `eigenstate_k8s_tls_correlation_id` | str | no | `` | Optional non-secret correlation identifier. |
| `eigenstate_k8s_tls_kubeconfig` | str | no | `` | Kubeconfig path required when apply is enabled. |
| `eigenstate_k8s_tls_kubectl` | str | no | `kubectl` | kubectl command path. |
| `eigenstate_k8s_tls_labels` | dict | no | `` | Additional safe labels for rendered manifests. |
| `eigenstate_k8s_tls_namespace` | str | yes | `` | Kubernetes namespace for the TLS Secret. |
| `eigenstate_k8s_tls_no_log` | bool | no | `true` | Hide secret-bearing task output. |
| `eigenstate_k8s_tls_output_dir` | str | no | `./artifacts` | Directory for rendered artifacts. |
| `eigenstate_k8s_tls_private_key` | str | no | `` | PEM private key material for tls.key. |
| `eigenstate_k8s_tls_render_only` | bool | no | `true` | Refuse cluster apply behavior when true. |
| `eigenstate_k8s_tls_render_review_manifest` | bool | no | `true` | Render a review manifest with payload values redacted. |
| `eigenstate_k8s_tls_secret_name` | str | yes | `` | Kubernetes TLS Secret name. |
| `eigenstate_k8s_tls_write_payload_manifest` | bool | no | `false` | Write a protected manifest containing encoded TLS payloads. |

### `keytab_secret_render`

| Default variable | Default value |
| --- | --- |
| `eigenstate_keytab_secret_annotations` | `{}` |
| `eigenstate_keytab_secret_apply` | `false` |
| `eigenstate_keytab_secret_basename` | `keytab-secret` |
| `eigenstate_keytab_secret_context` | `` |
| `eigenstate_keytab_secret_correlation_id` | `` |
| `eigenstate_keytab_secret_key` | `service.keytab` |
| `eigenstate_keytab_secret_keytab_b64` | `c3RhdGljLXZhbGlkYXRpb24ta2V5dGFi` |
| `eigenstate_keytab_secret_kubeconfig` | `` |
| `eigenstate_keytab_secret_kubectl` | `kubectl` |
| `eigenstate_keytab_secret_labels` | `{'app.kubernetes.io/managed-by': 'eigenstate.ipa', 'app.kubernetes.io/component': 'workload-keytab-delivery'}` |
| `eigenstate_keytab_secret_name` | `idm-keytab-secret` |
| `eigenstate_keytab_secret_namespace` | `default` |
| `eigenstate_keytab_secret_no_log` | `true` |
| `eigenstate_keytab_secret_output_dir` | `./artifacts` |
| `eigenstate_keytab_secret_principal` | `` |
| `eigenstate_keytab_secret_render_only` | `true` |
| `eigenstate_keytab_secret_render_review_manifest` | `true` |
| `eigenstate_keytab_secret_write_payload_manifest` | `false` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_keytab_secret_annotations` | dict | no | `` | Additional safe annotations for rendered manifests. |
| `eigenstate_keytab_secret_apply` | bool | no | `false` | Apply the protected manifest with kubectl when explicitly enabled. |
| `eigenstate_keytab_secret_basename` | str | no | `keytab-secret` | Basename for rendered artifacts. |
| `eigenstate_keytab_secret_context` | str | no | `` | Kubernetes context required when apply is enabled. |
| `eigenstate_keytab_secret_correlation_id` | str | no | `` | Optional non-secret correlation identifier. |
| `eigenstate_keytab_secret_key` | str | no | `service.keytab` | Data key that stores the keytab bytes. |
| `eigenstate_keytab_secret_keytab_b64` | str | no | `` | Base64-encoded keytab payload. |
| `eigenstate_keytab_secret_kubeconfig` | str | no | `` | Kubeconfig path required when apply is enabled. |
| `eigenstate_keytab_secret_kubectl` | str | no | `kubectl` | kubectl command path. |
| `eigenstate_keytab_secret_labels` | dict | no | `` | Additional safe labels for rendered manifests. |
| `eigenstate_keytab_secret_name` | str | yes | `` | Kubernetes Secret name for the keytab. |
| `eigenstate_keytab_secret_namespace` | str | yes | `` | Kubernetes namespace for the rendered Secret. |
| `eigenstate_keytab_secret_no_log` | bool | no | `true` | Hide secret-bearing task output. |
| `eigenstate_keytab_secret_output_dir` | str | no | `./artifacts` | Directory for rendered artifacts. |
| `eigenstate_keytab_secret_principal` | str | no | `` | Optional non-secret Kerberos principal label for review. |
| `eigenstate_keytab_secret_render_only` | bool | no | `true` | Refuse cluster apply behavior when true. |
| `eigenstate_keytab_secret_render_review_manifest` | bool | no | `true` | Render a review manifest with payload values redacted. |
| `eigenstate_keytab_secret_write_payload_manifest` | bool | no | `false` | Write a protected manifest containing the keytab payload. |

### `sealed_artifact_delivery`

| Default variable | Default value |
| --- | --- |
| `eigenstate_sealed_check_mode_retrieve` | `false` |
| `eigenstate_sealed_cleanup_after_handoff` | `true` |
| `eigenstate_sealed_delegate_to` | `localhost` |
| `eigenstate_sealed_encoding` | `base64` |
| `eigenstate_sealed_handoff_argv` | `` |
| `eigenstate_sealed_handoff_chdir` | `` |
| `eigenstate_sealed_handoff_creates` | `` |
| `eigenstate_sealed_handoff_enabled` | `false` |
| `eigenstate_sealed_ipaadmin_password` | `` |
| `eigenstate_sealed_ipaadmin_principal` | `admin` |
| `eigenstate_sealed_kerberos_keytab` | `` |
| `eigenstate_sealed_live_lookup_enabled` | `true` |
| `eigenstate_sealed_no_log` | `true` |
| `eigenstate_sealed_output_group` | `` |
| `eigenstate_sealed_output_mode` | `0600` |
| `eigenstate_sealed_output_owner` | `` |
| `eigenstate_sealed_output_path` | `` |
| `eigenstate_sealed_report_dir` | `./artifacts` |
| `eigenstate_sealed_report_enabled` | `true` |
| `eigenstate_sealed_report_formats` | `json, md` |
| `eigenstate_sealed_result_format` | `record` |
| `eigenstate_sealed_scope` | `shared` |
| `eigenstate_sealed_server` | `` |
| `eigenstate_sealed_service` | `` |
| `eigenstate_sealed_state` | `preflight` |
| `eigenstate_sealed_target_host` | `` |
| `eigenstate_sealed_tempdir_parent` | `` |
| `eigenstate_sealed_use_tempdir` | `true` |
| `eigenstate_sealed_username` | `` |
| `eigenstate_sealed_vault_name` | `` |
| `eigenstate_sealed_verify` | `` |

| Argument | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `eigenstate_sealed_encoding` | str | no | `base64` | Encoding requested from the vault lookup. |
| `eigenstate_sealed_handoff_argv` | list | no | `` | Command argv for the handoff command. |
| `eigenstate_sealed_handoff_enabled` | bool | no | `false` | Whether to run a handoff command after staging. |
| `eigenstate_sealed_ipaadmin_password` | str | no | `` | Password for the Kerberos principal. |
| `eigenstate_sealed_ipaadmin_principal` | str | no | `admin` | Kerberos principal used for IdM authentication. |
| `eigenstate_sealed_kerberos_keytab` | str | no | `` | Keytab path for non-interactive Kerberos authentication. |
| `eigenstate_sealed_live_lookup_enabled` | bool | no | `true` | Whether preflight/retrieve tasks may contact IdM. |
| `eigenstate_sealed_no_log` | bool | no | `true` | Hide secret-bearing sealed artifact tasks. |
| `eigenstate_sealed_output_mode` | str | no | `0600` | File mode for staged artifact. |
| `eigenstate_sealed_output_path` | str | no | `` | Destination path for staged artifact states. |
| `eigenstate_sealed_report_enabled` | bool | no | `true` | Whether to render metadata-only reports. |
| `eigenstate_sealed_scope` | str | no | `shared` | Vault ownership scope. |
| `eigenstate_sealed_server` | str | yes | `` | IdM server FQDN. |
| `eigenstate_sealed_service` | str | no | `` | Service owner for service-scoped vaults. |
| `eigenstate_sealed_state` | str | no | `preflight` | Role state to run. |
| `eigenstate_sealed_username` | str | no | `` | User owner for user-scoped vaults. |
| `eigenstate_sealed_vault_name` | str | yes | `` | IdM vault name containing the sealed artifact. |
| `eigenstate_sealed_verify` | str | no | `` | IPA CA certificate path or false-like override. |

## Related Pages

- [Playbook reference](../playbooks.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

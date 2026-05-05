---
layout: default
title: Kubernetes Secret From IdM Vault
description: >-
  Render-first workflow for preparing Kubernetes Secret manifests from
  IdM vault material without exposing payloads in default output.
---

{% raw %}

# Kubernetes Secret From IdM Vault

`kubernetes_secret_from_idm_vault` prepares Kubernetes Secret manifests from
IdM vault material. It is built for review-first delivery: the default artifact
is a Secret manifest with redacted values and safe metadata.

Read the [Kubernetes Secret Delivery Threat Model](https://gprocunier.github.io/eigenstate-ipa/kubernetes-secret-delivery-threat-model.html)
before applying payload-bearing manifests to a cluster.

## Render A Review Manifest

```bash
ansible-playbook playbooks/render-kubernetes-secret-from-idm-vault.yml \
  -e eigenstate_k8s_secret_name=app-runtime-secret \
  -e eigenstate_k8s_secret_namespace=payments \
  -e eigenstate_k8s_secret_output_dir=./artifacts/workload-secret
```

By default this renders:

```text
artifacts/workload-secret/kubernetes-secret-from-idm-vault.review.yaml
```

The review manifest includes key names but redacts values.

## Static Input Mode

When live IdM lookup is disabled, provide already retrieved material through
`eigenstate_k8s_secret_data`. Secret-bearing tasks remain hidden with
`no_log: true`.

```yaml
eigenstate_k8s_secret_data:
  application.conf: "{{ application_config_material }}"
```

## Live IdM Vault Lookup

Live lookup is opt-in:

```yaml
eigenstate_k8s_secret_live_lookup_enabled: true
eigenstate_k8s_secret_vault_name: app-runtime-material
eigenstate_k8s_secret_vault_scope: shared
eigenstate_k8s_secret_vault_key: application.conf
```

Use the existing vault lookup authentication variables for IdM access. Password
and keytab inputs are marked as secret-bearing.

## Protected Payload Manifest

To write a payload-bearing manifest:

```yaml
eigenstate_k8s_secret_write_payload_manifest: true
```

The file is written with mode `0600` and should be handled as sensitive.

## Apply Path

Cluster apply requires all of the following:

```yaml
eigenstate_k8s_secret_render_only: false
eigenstate_k8s_secret_apply: true
eigenstate_k8s_secret_kubeconfig: /secure/path/kubeconfig
eigenstate_k8s_secret_context: workload-admin
```

Default CI never enables this path.

{% endraw %}

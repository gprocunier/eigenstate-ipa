---
layout: default
title: Kubernetes TLS From IdM Certificate
description: >-
  Render-first workflow for preparing Kubernetes TLS Secret manifests from
  certificate material governed by an IdM-centered process.
---

{% raw %}

# Kubernetes TLS From IdM Certificate

`kubernetes_tls_from_idm_cert` renders Kubernetes `kubernetes.io/tls` Secret
manifests from certificate material that has been issued, reviewed, or tracked
through an IdM-centered process.

Read the [Kubernetes Secret Delivery Threat Model](https://gprocunier.github.io/eigenstate-ipa/kubernetes-secret-delivery-threat-model.html)
before applying payload-bearing manifests to a cluster.

## Render A Review Manifest

```bash
ansible-playbook playbooks/render-kubernetes-tls-secret-from-idm-cert.yml \
  -e eigenstate_k8s_tls_secret_name=app-tls \
  -e eigenstate_k8s_tls_namespace=payments \
  -e eigenstate_k8s_tls_output_dir=./artifacts/workload-tls
```

The default review manifest shows the Secret name, namespace, metadata, and TLS
keys with values redacted.

## Payload Inputs

Payload-bearing values are secret-bearing and hidden from task output:

```yaml
eigenstate_k8s_tls_certificate: "{{ issued_certificate_pem }}"
eigenstate_k8s_tls_private_key: "{{ private_key_pem }}"
eigenstate_k8s_tls_ca_certificate: "{{ issuing_ca_pem }}"
```

The CA certificate is optional. The role writes `tls.crt` and `tls.key`, and
adds `ca.crt` when a CA certificate is supplied.

## Protected Payload Manifest

To write the encoded TLS Secret manifest:

```yaml
eigenstate_k8s_tls_write_payload_manifest: true
```

The file is written with mode `0600` and should be handled as sensitive.

## Apply Path

Cluster apply requires all of the following:

```yaml
eigenstate_k8s_tls_render_only: false
eigenstate_k8s_tls_apply: true
eigenstate_k8s_tls_kubeconfig: /secure/path/kubeconfig
eigenstate_k8s_tls_context: workload-admin
```

Default CI never enables this path.

{% endraw %}

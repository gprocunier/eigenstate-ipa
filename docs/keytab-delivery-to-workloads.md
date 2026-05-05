---
layout: default
title: Keytab Delivery To Workloads
description: >-
  Render-first workflow for delivering Kerberos keytabs to Kubernetes and
  OpenShift workloads through protected Secret manifests.
---

{% raw %}

# Keytab Delivery To Workloads

`keytab_secret_render` prepares Kubernetes Secret manifests for Kerberos keytab
delivery. It is intended for workloads that already have a clear Kerberos
service principal boundary and a site-approved rotation plan.

Read the [Kubernetes Secret Delivery Threat Model](https://gprocunier.github.io/eigenstate-ipa/kubernetes-secret-delivery-threat-model.html)
before applying payload-bearing manifests to a cluster.

## Render A Review Manifest

```bash
ansible-playbook playbooks/render-keytab-secret.yml \
  -e eigenstate_keytab_secret_name=app-keytab \
  -e eigenstate_keytab_secret_namespace=payments \
  -e eigenstate_keytab_secret_principal=HTTP/app.example.com@EXAMPLE.COM \
  -e eigenstate_keytab_secret_output_dir=./artifacts/workload-keytab
```

The review manifest includes safe metadata and the keytab data key name, but it
does not disclose the keytab bytes.

## Payload Input

Provide keytab bytes as base64:

```yaml
eigenstate_keytab_secret_key: service.keytab
eigenstate_keytab_secret_keytab_b64: "{{ keytab_bytes_b64 }}"
```

The payload input is secret-bearing and hidden from task output.

## Protected Payload Manifest

To write the payload-bearing manifest:

```yaml
eigenstate_keytab_secret_write_payload_manifest: true
```

The file is written with mode `0600`. Treat it like the keytab itself.

## Apply Path

Cluster apply requires all of the following:

```yaml
eigenstate_keytab_secret_render_only: false
eigenstate_keytab_secret_apply: true
eigenstate_keytab_secret_kubeconfig: /secure/path/kubeconfig
eigenstate_keytab_secret_context: workload-admin
```

Default CI never enables this path.

## Rotation Notes

A keytab mounted into a pod is not automatically retired when IdM material is
rotated. A complete workflow should include:

- creating or retrieving the new keytab
- updating the Kubernetes Secret
- restarting or reloading consuming workloads
- retiring old Kerberos keys when the workload no longer needs them

{% endraw %}

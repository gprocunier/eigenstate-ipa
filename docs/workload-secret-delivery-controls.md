---
layout: default
title: Workload Secret Delivery Controls
description: >-
  Controls and review checklist for delivering IdM-backed secrets,
  certificates, and keytabs into Kubernetes and OpenShift workloads.
---

{% raw %}

# Workload Secret Delivery Controls

Kubernetes Secrets are a workload delivery mechanism, not a complete secret
management system. They can be the right boundary when the cluster is already
the runtime authority for a workload, but they need explicit controls around
storage, access, rotation, and review.

The workload Secret delivery roles default to render-only behavior. They
produce review manifests with payload values redacted. A payload-bearing
manifest is written only when an operator explicitly requests it, and cluster
apply is disabled unless the role is configured with explicit kubeconfig and
context inputs.

## Required Cluster Controls

Before applying a payload-bearing Secret manifest, confirm these controls:

| Control | Why it matters |
| --- | --- |
| etcd encryption at rest | Secret data is stored in the cluster backing store. Encryption should be enabled and key management should be understood. |
| narrow RBAC | Anyone who can read the Secret, create pods that mount it, or exec into consuming pods may be able to recover the payload. |
| namespace scope | The Secret should live only in the namespace that runs the workload. Cross-namespace reuse expands the review boundary. |
| workload service accounts | Bind Secret read/use permissions to the workload service account, not broad human or automation groups. |
| audit retention | Secret read, update, and pod mount activity should be auditable for the review window. |
| rotation plan | Kubernetes does not rotate mounted payloads by itself. Workloads may need restart or reload handling. |

## Safe Defaults

The roles use the following defaults:

- render a review manifest with redacted values
- do not write a payload-bearing manifest
- do not apply anything to a cluster
- require explicit kubeconfig and context for apply
- mark secret-bearing task output with `no_log: true`
- write protected payload manifests with mode `0600`

## Review Manifest Versus Payload Manifest

The review manifest is intended for pull requests, change records, and operator
review. It shows:

- Secret name and namespace
- Secret type
- labels and annotations
- safe source metadata
- payload key names
- redacted payload values

The payload manifest is intended only for controlled local handling or an
explicit apply operation. Store it in a protected location and remove it after
handoff if the site process does not require retention.

## Rotation Limitations

Secret delivery into Kubernetes does not automatically solve rotation. A
complete rotation workflow should define:

- how IdM vault content, certificates, or keytabs are rotated
- when the Kubernetes Secret is updated
- whether workloads need restart, reload, or rollout
- who verifies that old material is retired
- how stale mounted volumes, environment variables, and pod replicas are found

{% endraw %}

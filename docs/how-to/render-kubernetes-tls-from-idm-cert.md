---
layout: default
title: Render Kubernetes TLS from an IdM certificate
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this to render TLS Secret manifests from certificate material without applying them by default.
authority_boundary:
  - idm
  - certificate-authority
  - kubernetes
  - collection
workflow_boundary: render-only
evidence_shape:
  - review-manifest
public_status: rewritten
last_verified: 2026-05-17
---
{% raw %}

# Render Kubernetes TLS from an IdM certificate

## When To Use This

Use this to render TLS Secret manifests from certificate material without applying them by default.

## Required Authority

IdM CA owns certificate issuance. Kubernetes enforces only after apply.

## Safety Boundary

This workflow is `render-only`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Inputs

- Named target objects
- Credentials with the required IdM or platform authority
- A reviewed output path or downstream task

## Steps

1. Confirm the target objects and authority before running.
2. Run the command or task with review-friendly output.
3. Inspect the returned evidence before continuing to any mutating step.

```bash
ansible-playbook playbooks/render-kubernetes-tls-secret-from-idm-cert.yml
```

{% endraw %}
{% include task_example.html id="render-kubernetes-tls-from-idm-cert" %}
{% raw %}

## Expected Evidence

The role renders a review-only TLS Secret manifest with redacted certificate
fields. A captured render run produced:

```text
PLAY [Render Kubernetes TLS Secret manifest from IdM certificate material]

TASK [eigenstate.ipa.kubernetes_tls_from_idm_cert : Render reviewable Kubernetes TLS Secret manifest] ***
changed: [localhost]

PLAY RECAP ************************************************************
localhost                  : ok=5    changed=2    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0
```

The review artifact redacts both TLS fields:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: "idm-tls-secret"
  namespace: "default"
  annotations:
    eigenstate.ipa/payload: "redacted-in-review-manifest"
    eigenstate.ipa/source: "idm-cert"
type: kubernetes.io/tls
stringData:
  tls.crt: "REDACTED"
  tls.key: "REDACTED"
```

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/roles/workload_secret_delivery.html](../reference/roles/workload_secret_delivery.html)
- [/explanation/authority-boundaries.html](../explanation/authority-boundaries.html)

{% endraw %}

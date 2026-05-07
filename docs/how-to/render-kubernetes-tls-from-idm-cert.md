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
last_verified: 2026-05-07
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

## Expected Result

The workflow produces the expected evidence or artifact for review.

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/roles/workload_secret_delivery.html](../reference/roles/workload_secret_delivery.html)
- [/explanation/authority-boundaries.html](../explanation/authority-boundaries.html)

{% endraw %}

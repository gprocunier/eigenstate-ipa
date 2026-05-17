---
layout: default
title: Render a Kubernetes Secret from an IdM vault
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this to render review-first Kubernetes Secret manifests from IdM vault material.
authority_boundary:
  - idm
  - kubernetes
  - collection
workflow_boundary: render-only
evidence_shape:
  - review-manifest
public_status: rewritten
last_verified: 2026-05-17
---
{% raw %}

# Render a Kubernetes Secret from an IdM vault

## When To Use This

Use this to render review-first Kubernetes Secret manifests from IdM vault material.

## Required Authority

IdM owns the payload. Kubernetes enforces only if the rendered manifest is applied.

## Safety Boundary

This workflow is `render-only`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Secret Handling

Do not print payload material. Use `no_log: true` on payload-bearing tasks. Review artifacts should redact secret values, and payload manifest rendering should be opt-in.

## Inputs

- Named target objects
- Credentials with the required IdM or platform authority
- A reviewed output path or downstream task

## Steps

1. Confirm the target objects and authority before running.
2. Run the command or task with review-friendly output.
3. Inspect the returned evidence before continuing to any mutating step.

```bash
ansible-playbook playbooks/render-kubernetes-secret-from-idm-vault.yml
```

{% endraw %}
{% include task_example.html id="render-kubernetes-secret-from-idm-vault" %}
{% raw %}

## Expected Evidence

The role renders a review-only Kubernetes Secret manifest with payload fields
redacted. A captured wrapper run with static payload inputs produced:

```text
PLAY [Render Kubernetes Secret manifest from IdM vault material] ********

TASK [eigenstate.ipa.kubernetes_secret_from_idm_vault : Validate Kubernetes Secret delivery variables] ***
ok: [localhost] => {
    "changed": false,
    "msg": "All assertions passed"
}

TASK [kubernetes_secret_from_idm_vault : Render reviewable Kubernetes Secret manifest]
changed: [localhost]

PLAY RECAP ************************************************************
localhost                  : ok=6    changed=2    unreachable=0    failed=0    skipped=10   rescued=0    ignored=0
```

The rendered review artifact contains redacted data, not the vault payload:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: "idm-vault-secret"
  namespace: "default"
  annotations:
    eigenstate.ipa/payload: "redacted-in-review-manifest"
    eigenstate.ipa/source: "idm-vault"
type: "Opaque"
stringData:
  artifact: "REDACTED"
```

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/roles/workload_secret_delivery.html](../reference/roles/workload_secret_delivery.html)
- [/explanation/authority-boundaries.html](../explanation/authority-boundaries.html)

{% endraw %}

---
layout: default
title: Render a keytab Secret
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this to render review-first keytab Secret manifests.
authority_boundary:
  - idm
  - kerberos
  - kubernetes
  - collection
workflow_boundary: render-only
evidence_shape:
  - review-manifest
public_status: rewritten
last_verified: 2026-05-17
---
{% raw %}

# Render a keytab Secret

## When To Use This

Use this to render review-first keytab Secret manifests.

## Required Authority

Kerberos and IdM own key material. Kubernetes receives it only if a reviewed payload manifest is applied.

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
ansible-playbook playbooks/render-keytab-secret.yml
```

{% endraw %}
{% include task_example.html id="render-keytab-secret" %}
{% raw %}

## Expected Evidence

The role renders a review manifest with redacted payload fields and no secret
material in clear text. A captured render run produced:

```text
PLAY [Render Kubernetes Secret manifest for keytab delivery] *************

TASK [eigenstate.ipa.keytab_secret_render : Render reviewable keytab Secret manifest] ***
changed: [localhost]

PLAY RECAP ************************************************************
localhost                  : ok=6    changed=2    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0
```

The review artifact keeps the keytab payload redacted:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: "idm-keytab-secret"
  namespace: "default"
  annotations:
    eigenstate.ipa/payload: "redacted-in-review-manifest"
    eigenstate.ipa/principal: "HTTP/app.example.com@EXAMPLE.COM"
    eigenstate.ipa/source: "idm-keytab"
type: Opaque
stringData:
  service.keytab: "REDACTED"
```

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/roles/workload_secret_delivery.html](../reference/roles/workload_secret_delivery.html)
- [/explanation/authority-boundaries.html](../explanation/authority-boundaries.html)

{% endraw %}

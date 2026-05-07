---
layout: default
title: Render a workload Secret from IdM material
diataxis: tutorial
diataxis_type: tutorial
audience: Operators learning IdM-backed automation flows
outcome: Learn review-first Kubernetes and OpenShift Secret rendering.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-07
---
{% raw %}

# Render a workload Secret from IdM material

## What You Will Build

A redacted review manifest from IdM-sourced material.

## What You Need Before Starting

- A lab vault, certificate, or keytab source
- A local output directory for manifests
- No live cluster credentials for the first pass

## Lab Assumptions

- Review manifests are safe to inspect.
- Payload manifests are opt-in.
- Nothing is applied to a cluster during the tutorial.

## Step-By-Step Path

1. Select the render role for vault, TLS, or keytab material.
2. Run the wrapper playbook with review output enabled.
3. Inspect the redacted review manifest.
4. Defer payload rendering and cluster apply until controls are reviewed.

```bash
ansible-playbook playbooks/render-kubernetes-secret-from-idm-vault.yml
```

{% endraw %}
{% include task_example.html id="render-workload-secret" %}
{% raw %}

## Expected Output

```text
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
data:
  password: REDACTED
```

## What You Learned

- Render-first roles separate review from runtime enforcement.
- Kubernetes does not enforce anything until a manifest is applied.
- Payload-bearing artifacts need restrictive handling.

## Next Page

Continue with [/how-to/render-kubernetes-secret-from-idm-vault.html](../how-to/render-kubernetes-secret-from-idm-vault.html).

{% endraw %}

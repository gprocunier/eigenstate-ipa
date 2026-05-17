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
last_verified: 2026-05-17
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
3. Inspect the redacted review manifest in `./artifacts`.
4. Defer payload rendering and cluster apply until controls are reviewed.

```bash
ansible-playbook render-workload-secret.yml
ls -l artifacts
sed -n '1,80p' artifacts/kubernetes-secret-from-idm-vault.review.yaml
```

{% endraw %}
{% include task_example.html id="render-workload-secret" %}
{% raw %}

## Expected Evidence

The playbook creates a review-only manifest and keeps payload values redacted.
A captured render run with `app-config` in the `tutorial` namespace produced:

```text
PLAY [Render Kubernetes Secret manifest from IdM vault material] ***************

TASK [eigenstate.ipa.kubernetes_secret_from_idm_vault : Create Kubernetes Secret output directory] ***
changed: [localhost]

TASK [eigenstate.ipa.kubernetes_secret_from_idm_vault : Render reviewable Kubernetes Secret manifest] ***
changed: [localhost]

TASK [eigenstate.ipa.kubernetes_secret_from_idm_vault : Render protected Kubernetes Secret manifest with payload] ***
skipping: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=6    changed=2    unreachable=0    failed=0    skipped=10   rescued=0    ignored=0
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: "app-config"
  namespace: "tutorial"
  labels:
    app.kubernetes.io/managed-by: "eigenstate.ipa"
    app.kubernetes.io/component: "workload-secret-delivery"
  annotations:
    eigenstate.ipa/source: "idm-vault"
    eigenstate.ipa/payload: "redacted-in-review-manifest"
type: "Opaque"
stringData:
  artifact: "REDACTED"
```

## What You Learned

- Render-first roles separate review from runtime enforcement.
- Kubernetes does not enforce anything until a manifest is applied.
- Payload-bearing artifacts need restrictive handling.

## Next Page

Continue with [/how-to/render-kubernetes-secret-from-idm-vault.html](../how-to/render-kubernetes-secret-from-idm-vault.html).

{% endraw %}

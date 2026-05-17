---
layout: default
title: Render OpenShift identity evidence
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this to render OpenShift OAuth/OIDC and readiness evidence without applying cluster configuration.
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

# Render OpenShift identity evidence

## When To Use This

Use this to render OpenShift OAuth/OIDC and readiness evidence without applying cluster configuration.

## Required Authority

IdM and Keycloak own identity inputs. OpenShift enforces only after reviewed configuration is applied.

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
ansible-playbook playbooks/render-openshift-oidc-config.yml
```

{% endraw %}
{% include task_example.html id="render-openshift-identity-evidence" %}
{% raw %}

## Expected Evidence

The role renders review configuration plus readiness evidence artifacts. A
captured render run produced:

```text
PLAY [Render OpenShift OAuth OIDC configuration] ***********************

TASK [openshift_idm_oidc_validation : Validate OpenShift OIDC inputs]
ok: [localhost]

TASK [openshift_idm_oidc_validation : Render OpenShift OAuth OIDC configuration example]
changed: [localhost]

TASK [openshift_idm_oidc_validation : Render OpenShift OIDC JSON report]
changed: [localhost]

PLAY RECAP ************************************************************
localhost                  : ok=12   changed=4    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0
```

The OAuth review artifact has the concrete OpenShift API shape:

```yaml
apiVersion: config.openshift.io/v1
kind: OAuth
metadata:
  name: cluster
spec:
  identityProviders:
  - mappingMethod: claim
    name: openshift
    openID:
      clientID: openshift
      clientSecret:
        name: openid-client-secret
      issuer: https://keycloak.example.com/realms/openshift
    type: OpenID
```

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/roles/openshift_identity.html](../reference/roles/openshift_identity.html)
- [/explanation/authority-boundaries.html](../explanation/authority-boundaries.html)

{% endraw %}

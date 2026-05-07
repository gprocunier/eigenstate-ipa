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
source_material:
  - ../rewrite-audit.md
last_verified: 2026-05-07
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

## Expected Result

The workflow produces the expected evidence or artifact for review.

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/roles/openshift_identity.html](/reference/roles/openshift_identity.html)
- [/explanation/authority-boundaries.html](/explanation/authority-boundaries.html)

{% endraw %}

---
layout: default
title: Migrate side-effecting lookups
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when older keytab or certificate lookup patterns should move to explicit modules.
authority_boundary:
  - collection
  - ansible
workflow_boundary: preflight
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-07
---
{% raw %}

# Migrate side-effecting lookups

## When To Use This

Use this when older keytab or certificate lookup patterns should move to explicit modules.

## Required Authority

Lookups should be read-focused. Modules carry explicit mutation semantics and check-mode behavior.

## Safety Boundary

This workflow is `preflight`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Inputs

- Named target objects
- Credentials with the required IdM or platform authority
- A reviewed output path or downstream task

## Steps

1. Confirm the target objects and authority before running.
2. Run the command or task with review-friendly output.
3. Inspect the returned evidence before continuing to any mutating step.

```bash
ansible-playbook --syntax-check playbooks/service-onboarding.yml
```

## Expected Result

The workflow produces the expected evidence or artifact for review.

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/modules/keytab_manage.html](../reference/modules/keytab_manage.html)
- [/reference/modules/cert_request.html](../reference/modules/cert_request.html)
- [/explanation/authority-boundaries.html](../explanation/authority-boundaries.html)

{% endraw %}

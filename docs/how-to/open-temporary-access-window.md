---
layout: default
title: Open a temporary access window
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when an existing user needs a bounded access window represented by IdM expiry attributes.
authority_boundary:
  - idm
  - collection
workflow_boundary: mutating
evidence_shape:
  - command-output
public_status: rewritten
source_material:
  - ../rewrite-audit.md
last_verified: 2026-05-07
---
{% raw %}

# Open a temporary access window

## When To Use This

Use this when an existing user needs a bounded access window represented by IdM expiry attributes.

## Required Authority

IdM owns user expiry attributes. The role or module sets, clears, or expires them explicitly.

## Safety Boundary

This workflow is `mutating`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Inputs

- Named target objects
- Credentials with the required IdM or platform authority
- A reviewed output path or downstream task

## Steps

1. Confirm the target objects and authority before running.
2. Run the command or task with review-friendly output.
3. Inspect the returned evidence before continuing to any mutating step.

```yaml
eigenstate.ipa.user_lease:
    user: alice
    state: present
    lease_seconds: 3600
```

## Expected Result

The workflow produces the expected evidence or artifact for review.

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/modules/user_lease.html](/reference/modules/user_lease.html)
- [/explanation/authority-boundaries.html](/explanation/authority-boundaries.html)

{% endraw %}

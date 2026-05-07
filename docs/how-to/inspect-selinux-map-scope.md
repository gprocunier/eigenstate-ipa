---
layout: default
title: Inspect SELinux map scope
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when SELinux user maps and HBAC-linked scope should be reviewed before access or automation changes.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - command-output
public_status: rewritten
source_material:
  - ../rewrite-audit.md
last_verified: 2026-05-07
---
{% raw %}

# Inspect SELinux map scope

## When To Use This

Use this when SELinux user maps and HBAC-linked scope should be reviewed before access or automation changes.

## Required Authority

IdM owns SELinux map records. The lookup reads direct members and linked HBAC scope.

## Safety Boundary

This workflow is `read-only`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Inputs

- Named target objects
- Credentials with the required IdM or platform authority
- A reviewed output path or downstream task

## Steps

1. Confirm the target objects and authority before running.
2. Run the command or task with review-friendly output.
3. Inspect the returned evidence before continuing to any mutating step.

```bash
lookup('eigenstate.ipa.selinuxmap', 'staff_u_map', result_format='record')
```

## Expected Result

The workflow produces the expected evidence or artifact for review.

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/lookups/selinuxmap.html](/reference/lookups/selinuxmap.html)
- [/explanation/authority-boundaries.html](/explanation/authority-boundaries.html)

{% endraw %}

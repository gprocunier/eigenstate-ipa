---
layout: default
title: Generate operational evidence
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this to render readiness, certificate, keytab, temporary access, or drift reports without remediation.
authority_boundary:
  - idm
  - reports
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

# Generate operational evidence

## When To Use This

Use this to render readiness, certificate, keytab, temporary access, or drift reports without remediation.

## Required Authority

Reports record supplied evidence. They do not enforce remediation.

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
ansible-playbook playbooks/report-idm-readiness.yml
```

## Expected Result

The workflow produces the expected evidence or artifact for review.

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/roles/reports.html](/reference/roles/reports.html)
- [/explanation/authority-boundaries.html](/explanation/authority-boundaries.html)

{% endraw %}

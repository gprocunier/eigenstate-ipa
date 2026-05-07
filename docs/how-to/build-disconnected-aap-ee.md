---
layout: default
title: Build a disconnected AAP execution environment
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when the IdM execution environment must be built from mirrored or pre-staged dependencies.
authority_boundary:
  - ansible
  - aap
  - collection
workflow_boundary: mutating
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-07
---
{% raw %}

# Build a disconnected AAP execution environment

## When To Use This

Use this when the IdM execution environment must be built from mirrored or pre-staged dependencies.

## Required Authority

AAP uses the resulting image. Dependency source and registry trust are site responsibilities.

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

```bash
ansible-playbook playbooks/aap-ee-build.yml
```

## Expected Result

The workflow produces the expected evidence or artifact for review.

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/roles/aap_execution_environment.html](../reference/roles/aap_execution_environment.html)
- [/explanation/authority-boundaries.html](../explanation/authority-boundaries.html)

{% endraw %}

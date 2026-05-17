---
layout: default
title: Inspect sudo policy
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when sudo rules, commands, or command groups should be reviewed before privileged automation.
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

# Inspect sudo policy

## When To Use This

Use this when sudo rules, commands, or command groups should be reviewed before privileged automation.

## Required Authority

IdM owns sudo policy. The lookup reads rules and related objects.

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
lookup('eigenstate.ipa.sudo', 'deploy-web', sudo_object='rule', result_format='record')
```

{% endraw %}
{% include task_example.html id="inspect-sudo-policy" %}
{% raw %}

## Expected Evidence

The lookup returns the rule payload so you can validate command allow-lists before privileged execution.

```text
{
  "changed": false,
  "exists": true,
  "enabled": true,
  "commands": [
    "/usr/bin/systemctl",
    "/usr/bin/journalctl"
  ],
  "usercategory": "all",
  "hostcategory": "all",
  "hostgroup": []
}
```

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/lookups/sudo.html](../reference/lookups/sudo.html)
- [/explanation/authority-boundaries.html](../explanation/authority-boundaries.html)

{% endraw %}

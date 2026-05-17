---
layout: default
title: Test HBAC access
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when an automation job must prove a user, host, and service tuple is allowed before continuing.
authority_boundary:
  - idm
  - collection
workflow_boundary: preflight
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-17
---
{% raw %}

# Test HBAC access

## When To Use This

Use this when an automation job must prove a user, host, and service tuple is allowed before continuing.

## Required Authority

IdM owns HBAC policy. The lookup runs IdM hbactest and returns the decision.

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
lookup('eigenstate.ipa.hbacrule',
       'automation-svc',
       operation='test',
       targethost='client01.example.com',
       service='sshd',
       server='idm-01.example.com',
       kerberos_keytab='/runner/env/ipa/automation.keytab')
```

{% endraw %}
{% include task_example.html id="test-hbac-access" %}
{% raw %}

## Expected Evidence

The lookup returns an HBAC allow/deny decision object and the rule set evaluated on IdM.

```text
{
  "targethost": "client01.example.com",
  "service": "sshd",
  "denied": false,
  "matched": [
    "ops-ssh"
  ],
  "notmatched": [
    "ops-db"
  ]
}
```

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/lookups/hbacrule.html](../reference/lookups/hbacrule.html)
- [/explanation/authority-boundaries.html](../explanation/authority-boundaries.html)

{% endraw %}

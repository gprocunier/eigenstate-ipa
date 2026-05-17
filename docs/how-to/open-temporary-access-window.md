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
last_verified: 2026-05-17
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
---
- name: Open a governed temporary access window
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Open access window through packaged role
      ansible.builtin.import_role:
        name: eigenstate.ipa.temporary_access_window
      vars:
        eigenstate_taw_state: open
        eigenstate_taw_username: contractor01
        eigenstate_taw_server: idm-01.example.com
        eigenstate_taw_kerberos_keytab: /runner/env/ipa/automation.keytab
        eigenstate_taw_principal_expiration: "02:00"
        eigenstate_taw_password_expiration_matches_principal: true
        eigenstate_taw_hbac_targethost: bastion01.example.com
```

{% endraw %}
{% include task_example.html id="open-temporary-access-window" %}
{% raw %}

## Expected Evidence

The role opens the lease and writes temporary-access metadata as review-only
evidence. Static report validation produces this artifact shape:

```text
TASK [eigenstate.ipa.temporary_access_report : Render temporary access report JSON] ***
changed: [localhost]

TASK [eigenstate.ipa.temporary_access_report : Render temporary access report Markdown] ***
changed: [localhost]
```

```json
{
  "schema": "eigenstate.ipa/temporary_access_report/v1",
  "read_only": true,
  "summary": {
    "total_windows": "1",
    "active_windows": "0",
    "expired_windows": "1"
  },
  "windows": [
    {
      "principal": "contractor01",
      "target": "bastion.example.com",
      "status": "expired",
      "evidence": "Principal expiration is before the report timestamp."
    }
  ]
}
```

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/modules/user_lease.html](../reference/modules/user_lease.html)
- [/explanation/authority-boundaries.html](../explanation/authority-boundaries.html)

{% endraw %}

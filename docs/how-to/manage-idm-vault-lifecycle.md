---
layout: default
title: Manage IdM vault lifecycle
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when automation must create, update, archive, or delete IdM vaults through an explicit module surface.
authority_boundary:
  - idm
  - collection
  - ansible
workflow_boundary: mutating
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-17
---
{% raw %}

# Manage IdM vault lifecycle

## When To Use This

Use this when automation must create, update, archive, or delete IdM vaults through an explicit module surface.

## Required Authority

IdM owns vault state. The module changes vault lifecycle only when invoked with the requested state.

## Safety Boundary

This workflow is `mutating`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Secret Handling

Do not print payload material. Use `no_log: true` on payload-bearing tasks. Review artifacts should redact secret values, and payload manifest rendering should be opt-in.

## Inputs

- Vault name, scope, and type
- IdM credentials allowed to manage vaults
- Check-mode plan for review before mutation

## Steps

1. Run the module in check mode with the intended state.
2. Review the predicted change and member changes.
3. Run without check mode only after the requested lifecycle action is clear.

```yaml
- name: Ensure shared application vault exists
  eigenstate.ipa.vault_write:
    name: app-db-password
    scope: shared
    state: present
    vault_type: standard
    description: Application database credential
  check_mode: true
```

{% endraw %}
{% include task_example.html id="manage-idm-vault-lifecycle" %}
{% raw %}

## Expected Evidence

A captured live validation archived a value, read it back, and classified
negative-path failures without exposing payload material. The hash is a
sanitized example of the evidence field shape:

```json
{
  "vault_artifact": {
    "read_back_verified": true,
    "missing_failure_class": "vault_not_found",
    "mismatch_failure_class": "digest_mismatch",
    "sha256": "e57691568be539495e554041efba1b046effca98de5b309c275ff1f24f7e06c1"
  }
}
```

## Troubleshooting

- Permission denied: verify IdM vault management ACLs.
- Archive changed unexpectedly: check vault type and archive semantics.
- Member drift: use `members` and `members_absent` deliberately.

## Related Reference

- [/reference/modules/vault_write.html](../reference/modules/vault_write.html)
- [/how-to/retrieve-idm-vault-secret.html](retrieve-idm-vault-secret.html)

{% endraw %}

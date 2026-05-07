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
source_material:
  - ../rewrite-audit.md
last_verified: 2026-05-07
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

## Expected Result

The module reports whether IdM vault state would change, then can apply the explicit lifecycle action.

## Troubleshooting

- Permission denied: verify IdM vault management ACLs.
- Archive changed unexpectedly: check vault type and archive semantics.
- Member drift: use `members` and `members_absent` deliberately.

## Related Reference

- [/reference/modules/vault_write.html](/reference/modules/vault_write.html)
- [/how-to/retrieve-idm-vault-secret.html](/how-to/retrieve-idm-vault-secret.html)

{% endraw %}

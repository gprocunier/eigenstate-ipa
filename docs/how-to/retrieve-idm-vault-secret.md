---
layout: default
title: Retrieve an IdM vault secret
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when Ansible or AAP needs a value already stored in an IdM vault.
authority_boundary:
  - idm
  - collection
  - ansible
workflow_boundary: read-only
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-17
---
{% raw %}

# Retrieve an IdM vault secret

## When To Use This

Use this when Ansible or AAP needs a value already stored in an IdM vault.

## Required Authority

IdM owns the vault and payload. The lookup retrieves it under the caller authority. Ansible must avoid printing payload material.

## Safety Boundary

This workflow is `read-only`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Secret Handling

Do not print payload material. Use `no_log: true` on payload-bearing tasks. Review artifacts should redact secret values, and payload manifest rendering should be opt-in.

## Inputs

- Vault name and scope
- Control-node or EE IdM client libraries
- Credentials allowed to retrieve the vault payload

## Steps

1. Confirm the vault exists with metadata-only retrieval first.
2. Retrieve the payload in a task marked `no_log: true`.
3. Pass the value directly to the consuming task or render a redacted review artifact.

```yaml
- name: Retrieve database password from IdM vault
  ansible.builtin.set_fact:
    db_password: "{{ lookup('eigenstate.ipa.vault', 'app-db-password', scope='shared') }}"
  no_log: true
```

{% endraw %}
{% include task_example.html id="retrieve-idm-vault-secret" %}
{% raw %}

## Expected Evidence

The live validation proves the vault payload was retrieved and verified without
printing the payload:

```json
{
  "vault_artifact": {
    "read_back_verified": true,
    "missing_failure_class": "vault_not_found",
    "mismatch_failure_class": "digest_mismatch"
  }
}
```

## Troubleshooting

- Vault not found: verify name and scope.
- Authentication failure: verify IdM client libraries and Kerberos state.
- Unexpected binary data: use `encoding='base64'`.

## Related Reference

- [/reference/lookups/vault.html](../reference/lookups/vault.html)
- [/explanation/secret-boundary.html](../explanation/secret-boundary.html)

{% endraw %}

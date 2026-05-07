---
layout: default
title: Retrieve your first IdM vault value
diataxis: tutorial
diataxis_type: tutorial
audience: Operators learning IdM-backed automation flows
outcome: Learn the safe vault retrieval flow with sample material.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-07
---
{% raw %}

# Retrieve your first IdM vault value

## What You Will Build

A task that retrieves one lab vault value without printing it.

## What You Need Before Starting

- A lab vault containing non-production sample material
- IdM client Python libraries in the control node or EE
- Credentials allowed to retrieve the vault

## Lab Assumptions

- The vault is named `sample-api-token`.
- The value is fake lab data.
- Every payload-bearing task uses `no_log: true`.

## Step-By-Step Path

1. Run a metadata-only check for the vault.
2. Retrieve the value into a fact with `no_log: true`.
3. Use only a redacted confirmation in output.

```yaml
- name: Retrieve sample vault value
  ansible.builtin.set_fact:
    sample_token: "{{ lookup('eigenstate.ipa.vault', 'sample-api-token', scope='shared') }}"
  no_log: true

- name: Confirm retrieval without printing payload
  ansible.builtin.debug:
    msg: "sample-api-token retrieved and redacted"
```

## Expected Output

```text
TASK [Confirm retrieval without printing payload]
ok: [localhost] => {
  "msg": "sample-api-token retrieved and redacted"
}
```

## What You Learned

- Vault payloads can be consumed without copying them into inventory.
- `no_log: true` belongs on payload-bearing tasks.
- Reference output should show shape, not real secret values.

## Next Page

Continue with [/how-to/retrieve-idm-vault-secret.html](../how-to/retrieve-idm-vault-secret.html).

{% endraw %}

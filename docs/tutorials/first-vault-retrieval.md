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
last_verified: 2026-05-17
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

- The vault is named `app-bootstrap`.
- The value is fake lab data.
- Every payload-bearing task uses `no_log: true`.

## Step-By-Step Path

1. Run a metadata-only check for the vault.
2. Retrieve the value into a fact with `no_log: true`.
3. Use only a redacted confirmation in output.

Create `first-vault-retrieval.yml` from the example below and keep the
payload-bearing retrieval task redacted.

```bash
ansible-playbook first-vault-retrieval.yml
```

{% endraw %}
{% include task_example.html id="first-vault-retrieval" %}
{% raw %}

## Expected Evidence

The successful run confirms collection usage and stops output at shape-only proof.

```text
PLAY [Retrieve one IdM vault value safely] *****************************

TASK [Read a shared vault value into memory] ***************************
ok: [localhost] => (output suppressed by no_log)

TASK [Report only that retrieval succeeded] ****************************
ok: [localhost] => {
    "msg": "Retrieved app-bootstrap from IdM vault for this job."
}

PLAY RECAP ************************************************************
localhost : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## What You Learned

- Vault payloads can be consumed without copying them into inventory.
- `no_log: true` belongs on payload-bearing tasks.
- Reference output should show shape, not real secret values.

## Next Page

Continue with [/how-to/retrieve-idm-vault-secret.html](../how-to/retrieve-idm-vault-secret.html).

{% endraw %}

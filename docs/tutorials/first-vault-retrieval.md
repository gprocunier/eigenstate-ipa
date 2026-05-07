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

- The vault is named `app-bootstrap`.
- The value is fake lab data.
- Every payload-bearing task uses `no_log: true`.

## Step-By-Step Path

1. Run a metadata-only check for the vault.
2. Retrieve the value into a fact with `no_log: true`.
3. Use only a redacted confirmation in output.

Create `first-vault-retrieval.yml` from the example below and keep the
payload-bearing retrieval task redacted.

{% endraw %}
{% include task_example.html id="first-vault-retrieval" %}
{% raw %}

## Expected Result

The visible output should confirm that the play reached the final reporting task
without printing the vault payload. Secret-bearing retrieval remains hidden by
`no_log: true`, so do not expect the vault value to appear in stdout.

## What You Learned

- Vault payloads can be consumed without copying them into inventory.
- `no_log: true` belongs on payload-bearing tasks.
- Reference output should show shape, not real secret values.

## Next Page

Continue with [/how-to/retrieve-idm-vault-secret.html](../how-to/retrieve-idm-vault-secret.html).

{% endraw %}

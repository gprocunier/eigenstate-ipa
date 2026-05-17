---
layout: default
title: Query principal state
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this before keytab retrieval, certificate issuance, OTP enrollment, or access workflows that depend on an existing principal.
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

# Query principal state

## When To Use This

Use this before keytab retrieval, certificate issuance, OTP enrollment, or access workflows that depend on an existing principal.

## Required Authority

IdM owns principal state. The lookup reads existence, object type, lock, key, and last-auth facts.

## Safety Boundary

This workflow is `read-only`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Inputs

- User, host, or service principal names
- Read access to IdM principal records

## Steps

1. Run a `show` lookup for specific principals.
2. Gate downstream tasks on `exists` and object type.
3. Use `find` when discovery is needed before a batch workflow.

```yaml
- name: Check service principal
  ansible.builtin.debug:
    var: lookup('eigenstate.ipa.principal', 'HTTP/app.example.com', principal_type='service', result_format='record')
```

{% endraw %}
{% include task_example.html id="query-principal-state" %}
{% raw %}

## Expected Evidence

`result_format='record'` returns principal state that can drive assertions:

```yaml
principal_state:
  exists: true
  principal: HTTP/app.example.com@EXAMPLE.COM
  principal_type: service
  has_keytab: true
  disabled: false
```

## Troubleshooting

- Wrong type: set `principal_type` to `user`, `host`, or `service`.
- Missing key material: inspect returned key state before keytab work.
- Locked account: stop the workflow and resolve IdM state.

## Related Reference

- [/reference/lookups/principal.html](../reference/lookups/principal.html)
- [/tutorials/service-onboarding-with-principal-keytab-cert.html](../tutorials/service-onboarding-with-principal-keytab-cert.html)

{% endraw %}

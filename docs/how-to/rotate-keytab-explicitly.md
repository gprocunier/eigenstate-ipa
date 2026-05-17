---
layout: default
title: Rotate a keytab explicitly
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this only when rotating principal keys is the intended maintenance action.
authority_boundary:
  - idm
  - kerberos
  - collection
workflow_boundary: mutating
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-17
---
{% raw %}

# Rotate a keytab explicitly

## When To Use This

Use this only when rotating principal keys is the intended maintenance action.

## Required Authority

IdM and Kerberos own the principal keys. The module rotates only with explicit confirmation.

## Safety Boundary

This workflow is `mutating`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Secret Handling

Do not print payload material. Use `no_log: true` on payload-bearing tasks. Review artifacts should redact secret values, and payload manifest rendering should be opt-in.

## Inputs

- Principal name
- Destination or return-content decision
- `confirm_rotation: true` when `state: rotated` is intended

## Steps

1. Notify owners that existing keytabs will be invalidated.
2. Run check mode or a retrieve-only task first.
3. Run rotation with `confirm_rotation: true` and protect output with `no_log: true`.

```yaml
- name: Rotate service keytab with explicit confirmation
  eigenstate.ipa.keytab_manage:
    principal: HTTP/app.example.com
    state: rotated
    confirm_rotation: true
    destination: /secure/keytabs/http-app.keytab
    mode: "0600"
  no_log: true
```

{% endraw %}
{% include task_example.html id="rotate-keytab-explicitly" %}
{% raw %}

## Expected Evidence

The task reports an explicit rotation and the destination written by the module;
the keytab bytes remain hidden by `no_log: true`:

```yaml
keytab_result:
  changed: true
  principal: HTTP/app.example.com@EXAMPLE.COM
  state: rotated
  destination: /secure/keytabs/http-app.keytab
  mode: "0600"
```

## Troubleshooting

- Module refuses rotation: verify `confirm_rotation: true`.
- Dependent services fail: deploy the new keytab before restarting services.
- Unexpected content return: keep `return_content` disabled unless required.

## Related Reference

- [/reference/modules/keytab_manage.html](../reference/modules/keytab_manage.html)
- [/explanation/kerberos-keytab-boundary.html](../explanation/kerberos-keytab-boundary.html)

{% endraw %}

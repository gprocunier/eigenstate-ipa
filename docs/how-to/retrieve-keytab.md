---
layout: default
title: Retrieve a keytab
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when automation needs an existing keytab and must not rotate the principal keys.
authority_boundary:
  - idm
  - kerberos
  - collection
workflow_boundary: read-only
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-17
---
{% raw %}

# Retrieve a keytab

## When To Use This

Use this when automation needs an existing keytab and must not rotate the principal keys.

## Required Authority

IdM and Kerberos own the principal and keys. The lookup retrieves existing key material through `ipa-getkeytab` when configured for retrieve behavior.

## Safety Boundary

This workflow is `read-only`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Secret Handling

Do not print payload material. Use `no_log: true` on payload-bearing tasks. Review artifacts should redact secret values, and payload manifest rendering should be opt-in.

## Inputs

- Service or host principal
- Control node or EE package that provides `ipa-getkeytab`
- Kerberos authority allowed to retrieve the keytab

## Steps

1. Preflight the principal with the principal lookup.
2. Retrieve the keytab with retrieve behavior and `no_log: true`.
3. Write payloads only to controlled destinations or pass them directly to a render role.

```yaml
- name: Retrieve existing service keytab
  ansible.builtin.set_fact:
    service_keytab_b64: "{{ lookup('eigenstate.ipa.keytab', 'HTTP/app.example.com', retrieve_mode='retrieve') }}"
  no_log: true
```

{% endraw %}
{% include task_example.html id="retrieve-keytab" %}
{% raw %}

## Expected Evidence

The lookup returns base64 keytab content for the requested principal with no key rotation.

```text
TASK [Retrieve existing service keytab] ********************************
changed: [localhost] => (output redacted by no_log)
```

## Troubleshooting

- `ipa-getkeytab` missing: use the IdM execution environment or install the platform IPA client package.
- Existing key not retrievable: verify principal and IdM keytab retrieval policy.
- Payload printed: add `no_log: true` and remove debug output.

## Related Reference

- [/reference/lookups/keytab.html](../reference/lookups/keytab.html)
- [/explanation/kerberos-keytab-boundary.html](../explanation/kerberos-keytab-boundary.html)

{% endraw %}

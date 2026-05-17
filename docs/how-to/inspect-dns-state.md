---
layout: default
title: Inspect DNS state
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when IdM integrated DNS records should gate automation decisions.
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

# Inspect DNS state

## When To Use This

Use this when IdM integrated DNS records should gate automation decisions.

## Required Authority

IdM DNS owns the queried records. The lookup reads them without changing DNS.

## Safety Boundary

This workflow is `read-only`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Inputs

- Zone name
- Record name or search criteria
- Read access to IdM DNS APIs

## Steps

1. Query the exact record with `show`.
2. Use `find` for discovery or batch checks.
3. Gate downstream tasks on existence and returned record types.

```bash
ansible localhost -m ansible.builtin.debug -a "msg={{ lookup('eigenstate.ipa.dns', 'app', zone='example.com', result_format='record') }}"
```

{% endraw %}
{% include task_example.html id="inspect-dns-state" %}
{% raw %}

## Expected Evidence

The lookup result is a structured record that can be asserted before the
deployment continues:

```yaml
app_dns:
  exists: true
  zone: example.com
  name: app
  arecord:
    - 192.0.2.25
```

## Troubleshooting

- Zone not found: verify the IdM DNS zone name.
- Record missing: check relative name versus FQDN.
- API unavailable: verify IdM DNS is enabled.

## Related Reference

- [/reference/lookups/dns.html](../reference/lookups/dns.html)

{% endraw %}

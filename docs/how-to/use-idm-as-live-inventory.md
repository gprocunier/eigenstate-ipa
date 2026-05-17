---
layout: default
title: Use IdM as live Ansible inventory
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when enrolled hosts, hostgroups, netgroups, HBAC relationships, or selected IdM host attributes should drive Ansible targeting.
authority_boundary:
  - idm
  - collection
  - ansible
workflow_boundary: read-only
evidence_shape:
  - inventory-output
public_status: rewritten
last_verified: 2026-05-17
---
{% raw %}

# Use IdM as live Ansible inventory

## When To Use This

Use this when enrolled hosts, hostgroups, netgroups, HBAC relationships, or selected IdM host attributes should drive Ansible targeting.

## Required Authority

IdM owns host and policy state. The inventory plugin reads that state and Ansible consumes the generated inventory.

## Safety Boundary

This workflow is `read-only`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Inputs

- An IdM server reachable from the control node or EE
- Inventory source YAML using `plugin: eigenstate.ipa.idm`
- Password or Kerberos credentials allowed to read host and policy records

## Steps

1. Create an inventory source file with IdM connection settings.
2. Run `ansible-inventory --list -i inventory.eigenstate_ipa.yml`.
3. Inspect generated groups and hostvars before using the inventory in a playbook or AAP sync.

```bash
ansible-inventory -i inventory.eigenstate_ipa.yml --graph
ansible-inventory -i inventory.eigenstate_ipa.yml --host idm-client01.example.com
```

{% endraw %}
{% include task_example.html id="use-idm-as-live-inventory" %}
{% raw %}

## Expected Evidence

A captured live inventory validation produced host data directly from IdM. The
hostnames below are sanitized, but the graph shape and hostvar result are the
captured output shape:

```text
@all:
  |--@ungrouped:
  |  |--apps.ocp.example.com
  |  |--bastion-01.example.com
  |  |--idm-01.example.com
  |  |--mirror-registry.example.com
  |  |--podinfo.apps.ocp.example.com
  |  |--stale-app-01.example.com
```

```json
{
  "idm_schema_warnings": [],
  "idm_userclass": [],
  "idm_userclass_raw": null,
  "idm_userclass_type": "missing"
}
```

## Troubleshooting

- Authentication failure: verify Kerberos ticket, keytab, or password credentials.
- Missing hosts: verify the hosts are enrolled and visible to the IdM account.
- Unexpected grouping: inspect hostgroup, netgroup, and HBAC inputs in IdM.

## Related Reference

- [/reference/inventory/idm.html](../reference/inventory/idm.html)
- [/explanation/idm-as-automation-state-plane.html](../explanation/idm-as-automation-state-plane.html)

{% endraw %}

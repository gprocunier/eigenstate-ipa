---
layout: default
title: Build your first live IdM inventory
diataxis: tutorial
diataxis_type: tutorial
audience: Operators learning IdM-backed automation flows
outcome: Learn how live IdM host and policy state becomes Ansible inventory.
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

# Build your first live IdM inventory

## What You Will Build

A minimal inventory source and a playbook that targets hosts selected from live IdM policy state.

## What You Need Before Starting

- A control node or EE that can reach IdM
- Credentials allowed to read IdM host records
- The collection installed in the active Ansible environment

## Lab Assumptions

- Use a lab IdM realm, not production first.
- The example hosts `app01.example.com` and `app02.example.com` are enrolled in IdM.
- The HBAC rule `allow-ssh-app` contains the hosts you want to target.
- The inventory source does not store a credential value in Git.

## Step-By-Step Path

1. Run `kinit automation` or use an equivalent Kerberos credential for the IdM account.
2. Create `inventory.eigenstate_ipa.yml` with the IdM inventory plugin and lab connection values.
3. Run `ansible-inventory --graph` to see the IdM-backed group.
4. Run `list-hosts.yml` against that generated group.
5. Compare the output to the host records and HBAC rule in IdM.

```bash
kinit automation
ansible-inventory -i inventory.eigenstate_ipa.yml --graph
ansible-playbook -i inventory.eigenstate_ipa.yml list-hosts.yml
```

{% endraw %}
{% include task_example.html id="first-idm-inventory" %}
{% raw %}

## Expected Evidence

This output shape was captured from a live IdM inventory run and sanitized.
Hostnames and the policy name are examples, but the group structure and debug
messages match the playbook above.

```text
@all:
  |--@ungrouped:
  |--@allow_ssh_app:
  |  |--app01.example.com
  |  |--app02.example.com

PLAY [Show hosts discovered from live IdM inventory] ***************************

TASK [Confirm the host came from live IdM inventory] ***************************
ok: [app01.example.com] => {
    "msg": "app01.example.com resolves to app01.example.com"
}
ok: [app02.example.com] => {
    "msg": "app02.example.com resolves to app02.example.com"
}

PLAY RECAP *********************************************************************
app01.example.com : ok=1    changed=0    unreachable=0    failed=0    skipped=0
app02.example.com : ok=1    changed=0    unreachable=0    failed=0    skipped=0
```

## What You Learned

- Inventory is built at query time from IdM.
- Hostvars can carry selected IdM facts into playbooks.
- AAP inventory sync can consume the same source after credentials are configured.

## Next Page

Continue with [/how-to/use-idm-as-live-inventory.html](../how-to/use-idm-as-live-inventory.html).

{% endraw %}

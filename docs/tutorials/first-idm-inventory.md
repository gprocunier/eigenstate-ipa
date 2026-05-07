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
source_material:
  - ../rewrite-audit.md
last_verified: 2026-05-07
---
{% raw %}

# Build your first live IdM inventory

## What You Will Build

A minimal inventory source and two inspection commands that show IdM-backed hosts and hostvars.

## What You Need Before Starting

- A control node or EE that can reach IdM
- Credentials allowed to read IdM host records
- The collection installed in the active Ansible environment

## Lab Assumptions

- Use a lab IdM realm, not production first.
- The example host `client01.example.com` is enrolled in IdM.
- The inventory source does not store a credential value in Git.

## Step-By-Step Path

1. Create `inventory.eigenstate_ipa.yml` with the IdM inventory plugin and lab connection values.
2. Run `ansible-inventory --graph` to see IdM-backed groups.
3. Run `ansible-inventory --host client01.example.com` to inspect hostvars.
4. Compare the output to the host record in IdM.

```bash
ansible-inventory -i inventory.eigenstate_ipa.yml --graph
ansible-inventory -i inventory.eigenstate_ipa.yml --host client01.example.com
```

## Expected Output

```text
@all:
  |--@idm_hosts:
  |  |--client01.example.com

{
  "ipa_host_fqdn": "client01.example.com",
  "ipa_host_exists": true
}
```

## What You Learned

- Inventory is built at query time from IdM.
- Hostvars can carry selected IdM facts into playbooks.
- AAP inventory sync can consume the same source after credentials are configured.

## Next Page

Continue with [/how-to/use-idm-as-live-inventory.html](/how-to/use-idm-as-live-inventory.html).

{% endraw %}

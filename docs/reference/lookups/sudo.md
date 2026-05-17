---
layout: default
title: eigenstate.ipa.sudo lookup reference
diataxis: reference
diataxis_type: reference
audience: Operators and maintainers looking up exact facts
outcome: Exact source-verified reference for this Ansible collection surface.
authority_boundary:
  - collection
workflow_boundary: read-only
evidence_shape:
  - ansible-doc
public_status: rewritten
source_material:
  - ../../plugins/lookup/sudo.py
last_verified: 2026-05-17
---
{% raw %}

# `eigenstate.ipa.sudo` lookup reference

Query IdM sudo rules, sudo commands, and sudo command groups

## Synopsis

Returns the configuration of IdM sudo policy objects from FreeIPA/IdM.

Supports read-only C(show) and C(find) operations for sudo rules, sudo commands, and sudo command groups through one lookup surface.

Sudo policy in IdM is split across multiple object types. Rules define who may run what and where. Sudo commands define the command paths themselves. Sudo command groups bundle commands into reusable sets.

This plugin reads that policy state for use in playbook conditionals, audit tasks, and pre-flight validation. To create, modify, or delete sudo objects use the official FreeIPA modules C(freeipa.ansible_freeipa.ipasudorule), C(freeipa.ansible_freeipa.ipasudocmd), and C(freeipa.ansible_freeipa.ipasudocmdgroup).

Uses the C(ipalib) framework for all queries. Authentication follows the same keytab/password/existing-ticket pattern as other plugins in this collection.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Authentication follows the options documented for this surface.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `_terms` | list | no |  |  | One or more object names to look up when C(operation=show). The exact meaning depends on C(sudo_object): rule name for C(rule), command path for C(command), and command group name for C(commandgroup). Not required when C(operation=find). |
| `criteria` | str | no |  |  | Optional search string for C(operation=find). When omitted, all objects of the selected C(sudo_object) type are returned. |
| `ipaadmin_password` | str | no |  |  | Password for the admin principal. Used to obtain a Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket already exists. |
| `ipaadmin_principal` | str | no | admin |  | The Kerberos principal to authenticate as. |
| `kerberos_keytab` | str | no |  |  | Path to a Kerberos keytab file. Used to obtain a ticket non-interactively (required for AAP Execution Environments). |
| `operation` | str | no | show | show, find | Which operation to perform. C(show) queries each named object and returns its configuration. C(find) searches all objects of the selected C(sudo_object) type, optionally filtered by C(criteria). |
| `result_format` | str | no | record | record, map_record | How to shape the lookup result. C(record) returns a list of records, one per object. C(map_record) returns a single dictionary keyed by object name. |
| `server` | str | yes |  |  | FQDN of the IPA server. |
| `sudo_object` | str | no | rule | rule, command, commandgroup | Which IdM sudo object type to query. C(rule) inspects sudo rules. C(command) inspects individual sudo command objects. C(commandgroup) inspects sudo command groups. |
| `verify` | str | no |  |  | Path to the IPA CA certificate for TLS verification. Set to C(false) to skip an explicit CA override and rely on the system trust behavior from C(ipalib). Falls back to C(/etc/ipa/ca.crt) when present; disables verification with a warning otherwise. |

## Notes

- This plugin requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible controller.
- RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)
- For objects that do not exist, C(operation=show) returns a record with C(exists=false) rather than raising an error, allowing pre-flight conditionals without C(ignore_errors).
- Rule records expose direct member lists, category-wide scope, allowed and denied command assignments, RunAs assignments, and enablement state.
- Command records expose the sudo command path and optional description.
- Command-group records expose the group members and optional description.

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `_raw` | list |  | One record per sudo object. When C(result_format=record) (default), returns a list of records; a single-term lookup is unwrapped by Ansible to a plain dict. When C(result_format=map_record), returns a dictionary keyed by object name. |

## Examples

```yaml
# Inspect a named sudo rule before relying on it
- name: Read sudo rule state
  ansible.builtin.set_fact:
    sudo_rule: "{{ lookup('eigenstate.ipa.sudo',
                    'ops-maintenance',
                    sudo_object='rule',
                    server='idm-01.example.com',
                    kerberos_keytab='/etc/admin.keytab') }}"

# Find all sudo command groups
- name: List sudo command groups
  ansible.builtin.set_fact:
    cmd_groups: "{{ lookup('eigenstate.ipa.sudo',
                     operation='find',
                     sudo_object='commandgroup',
                     server='idm-01.example.com',
                     kerberos_keytab='/etc/admin.keytab') }}"

# Inspect a sudo command path directly
- name: Read sudo command object
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.sudo',
             '/usr/bin/systemctl',
             sudo_object='command',
             server='idm-01.example.com',
             kerberos_keytab='/etc/admin.keytab') }}"

# Load several rules as a keyed dict
- name: Build sudo rule map
  ansible.builtin.set_fact:
    sudo_rules: "{{ lookup('eigenstate.ipa.sudo',
                     'ops-maintenance', 'ops-deploy',
                     sudo_object='rule',
                     result_format='map_record',
                     server='idm-01.example.com',
                     kerberos_keytab='/etc/admin.keytab') }}"
```

## Example Result Shapes

```yaml
# rule_state (operation=show, record format)
rule_state:
  name: "ops-maintenance"
  object_type: "rule"
  exists: true
  description: "Standard ops maintenance rule"
  enabled: true
  users: ["automation-svc"]
  groups: []
  hosts: ["idm-01.example.com"]
  hostgroups: []
  allow_sudocmds: ["/usr/bin/systemctl", "/usr/bin/journalctl"]
  allow_sudocmdgroups: []
  deny_sudocmds: []
  deny_sudocmdgroups: []
  hostmasks: []
  sudooptions: ["ignore_lecture=1"]

# rules_by_name (map_record)
rules_by_name:
  - ops-maintenance:
      name: "ops-maintenance"
      object_type: "rule"
      exists: true
      description: "Standard ops maintenance rule"
      enabled: true
    ops-deploy:
      name: "ops-deploy"
      object_type: "rule"
      exists: true
      description: "Deployment exception rule"
      enabled: false
```

## Error Behavior

Lookup failures are task failures unless the caller handles them with Ansible error controls. Authentication, missing objects, invalid modes, and unavailable IdM APIs should be treated as explicit workflow failures.

## Related Pages

- [Authentication reference](../authentication.html)
- [Return shapes](../return-shapes.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

{% endraw %}

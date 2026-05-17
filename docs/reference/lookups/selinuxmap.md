---
layout: default
title: eigenstate.ipa.selinuxmap lookup reference
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
  - ../../plugins/lookup/selinuxmap.py
last_verified: 2026-05-17
---
{% raw %}

# `eigenstate.ipa.selinuxmap` lookup reference

Query SELinux user map state from FreeIPA/IdM

## Synopsis

Returns the configuration of SELinux user map entries registered in FreeIPA/IdM, including the SELinux user context assigned, the host and user scope, and any linked HBAC rule.

SELinux user maps are the FreeIPA mechanism that answers the question C(which SELinux user should this identity receive on this host?). SSSD and C(pam_selinux) evaluate the map at login and launch the session in the mapped context.

This plugin reads map state for use in playbook conditionals and validation workflows. To create, modify, or delete SELinux user maps use C(freeipa.ansible_freeipa.ipaselinuxusermap).

Uses the C(ipalib) framework for all queries. Authentication follows the same keytab/password/existing-ticket pattern as other plugins in this collection.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Authentication follows the options documented for this surface.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `_terms` | list | no |  |  | One or more SELinux user map names to look up when C(operation=show). Not required when C(operation=find). |
| `criteria` | str | no |  |  | Optional search string for C(operation=find). When omitted, all SELinux user maps are returned. |
| `ipaadmin_password` | str | no |  |  | Password for the admin principal. Used to obtain a Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket already exists. |
| `ipaadmin_principal` | str | no | admin |  | The Kerberos principal to authenticate as. |
| `kerberos_keytab` | str | no |  |  | Path to a Kerberos keytab file. Used to obtain a ticket non-interactively (required for AAP Execution Environments). |
| `operation` | str | no | show | show, find | Which operation to perform. C(show) queries each named map and returns its configuration. C(find) searches all maps, optionally filtered by C(criteria). |
| `result_format` | str | no | record | record, map_record | How to shape the lookup result. C(record) returns a list of map dictionaries, one per entry. C(map_record) returns a single dictionary keyed by map name. |
| `server` | str | yes |  |  | FQDN of the IPA server. |
| `verify` | str | no |  |  | Path to the IPA CA certificate for TLS verification. Set to C(false) to skip an explicit CA override and rely on the system trust behavior from C(ipalib). Falls back to C(/etc/ipa/ca.crt) when present; disables verification with a warning otherwise. |

## Notes

- This plugin requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible controller.
- RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)
- For maps that do not exist, C(operation=show) returns a record with C(exists=false) rather than raising an error, allowing pre-flight conditionals without C(ignore_errors).
- A map may use either direct user/host scope (members listed in C(users), C(groups), C(hosts), C(hostgroups)) or HBAC-linked scope (C(hbacrule) is set). These are mutually exclusive in FreeIPA.
- The SELinux user string in C(selinuxuser) is in the compound form required by FreeIPA, C(selinux_user:mls_range), for example C(staff_u:s0-s0:c0.c1023).

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `_raw` | list |  | One configuration record per SELinux user map. When C(result_format=record) (default), returns a list of records; a single-term lookup is unwrapped by Ansible to a plain dict. When C(result_format=map_record), returns a dictionary keyed by map name. |

## Examples

```yaml
# Validate a confinement map exists before proceeding
- name: Assert ops-deploy map is configured
  ansible.builtin.assert:
    that:
      - map_state.exists
      - map_state.enabled
    fail_msg: "SELinux user map 'ops-deploy-map' is missing or disabled"
  vars:
    map_state: "{{ lookup('eigenstate.ipa.selinuxmap',
                   'ops-deploy-map',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/admin.keytab') }}"

# Check what SELinux context a named map assigns
- name: Read SELinux user map configuration
  ansible.builtin.debug:
    msg: "Map {{ map.name }} assigns context {{ map.selinuxuser }} to users {{ map.users }}"
  vars:
    map: "{{ lookup('eigenstate.ipa.selinuxmap',
             'ops-patch-map',
             server='idm-01.example.com',
             ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"

# Find all configured SELinux user maps
- name: List all SELinux user maps
  ansible.builtin.set_fact:
    all_maps: "{{ lookup('eigenstate.ipa.selinuxmap',
                  operation='find',
                  server='idm-01.example.com',
                  kerberos_keytab='/etc/admin.keytab') }}"

# Retrieve multiple maps as a keyed dict
- name: Load map state for several roles
  ansible.builtin.set_fact:
    map_state: "{{ lookup('eigenstate.ipa.selinuxmap',
                   'ops-deploy-map', 'ops-patch-map', 'ops-inventory-map',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/admin.keytab',
                   result_format='map_record') }}"
- ansible.builtin.assert:
    that: map_state['ops-deploy-map'].enabled

# Check whether a map uses HBAC-linked scope
- name: Inspect HBAC linkage on a map
  ansible.builtin.debug:
    msg: "Map is scoped via HBAC rule: {{ map.hbacrule }}"
  when: map.hbacrule is not none
  vars:
    map: "{{ lookup('eigenstate.ipa.selinuxmap',
             'ops-root-local-map',
             server='idm-01.example.com',
             kerberos_keytab='/etc/admin.keytab') }}"
```

## Example Result Shapes

```yaml
# map_state (single map show result)
map_state:
  name: "ops-deploy-map"
  exists: true
  selinuxuser: "staff_u:s0-s0:c0.c1023"
  enabled: true
  usercategory: "all"
  hostcategory: null
  hbacrule: null
  users: []
  groups: []
  hosts: ["idm-01.example.com"]
  hostgroups: []
  description: "Confine ops workloads to staff_u"

# map_records_map (map_record)
map_records_map:
  - ops-deploy-map:
      name: "ops-deploy-map"
      exists: true
      selinuxuser: "staff_u:s0-s0:c0.c1023"
      enabled: true
      usercategory: "all"
      hostcategory: null
      hbacrule: null
      users: []
      groups: []
      hosts: ["idm-01.example.com"]
      hostgroups: []
      description: "Confine ops workloads to staff_u"
```

## Error Behavior

Lookup failures are task failures unless the caller handles them with Ansible error controls. Authentication, missing objects, invalid modes, and unavailable IdM APIs should be treated as explicit workflow failures.

## Related Pages

- [Authentication reference](../authentication.html)
- [Return shapes](../return-shapes.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

{% endraw %}

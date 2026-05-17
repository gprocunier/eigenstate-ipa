---
layout: default
title: eigenstate.ipa.idm inventory reference
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
  - ../../plugins/inventory/idm.py
last_verified: 2026-05-16
---
{% raw %}

# `eigenstate.ipa.idm` inventory reference

Build dynamic inventory from Red Hat IDM/FreeIPA

## Synopsis

Creates Ansible inventory from Red Hat Identity Management (IDM/FreeIPA) hosts, hostgroups, netgroups, and HBAC rules.

IDM hostgroups, netgroups, and HBAC rules are mapped to Ansible groups with configurable prefixes.

A curated set of host attributes from IDM is exposed as host variables with a C(idm_) prefix.

Exported host attributes include normalized values plus companion C(_raw) and C(_type) variables so playbooks can detect source shape drift without losing the original IdM value.

C(idm_schema_warnings) reports attributes that were normalized or rejected because their source shape did not match the expected inventory shape.

Nested hostgroups are fully resolved when building group membership.

HBAC rules with C(hostcategory=all) automatically include all enrolled hosts.

Supports standard Ansible inventory plugin features including compose, keyed_groups, groups, and caching.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Authentication follows the options documented for this surface.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `cache` | bool | no | false |  | Toggle to enable/disable the caching of the inventory's source data, requires a cache plugin setup to work. |
| `cache_connection` | str | no |  |  | Cache connection data or path, read cache plugin documentation for specifics. |
| `cache_plugin` | str | no | memory |  | Cache plugin to use for the inventory's source data. |
| `cache_prefix` |  | no | ansible_inventory_ |  | Prefix to use for cache plugin files/tables. |
| `cache_timeout` | int | no | 3600 |  | Cache duration in seconds. |
| `compose` | dict | no | {} |  | Create vars from jinja2 expressions. |
| `groups` | dict | no | {} |  | Add hosts to group based on Jinja2 conditionals. |
| `hbacrule_filter` | list | no |  |  | Limit HBAC-rule-based groups to this list of rule names. An empty list means all HBAC rules are included. |
| `hbacrule_prefix` | str | no | idm_hbacrule_ |  | Prefix applied to Ansible group names created from IDM HBAC rules. |
| `host_filter_from_groups` | bool | no | false |  | When set to C(true), hosts that do not belong to any group created by the configured sources and filters are removed from the inventory.  This prevents unrelated hosts from appearing under C(ungrouped).  When C(false) (the default), all enrolled IDM hosts are kept regardless of group membership. |
| `hostgroup_filter` | list | no |  |  | Limit hostgroup-based groups to this list of hostgroup names. An empty list means all hostgroups are included. |
| `hostgroup_prefix` | str | no | idm_hostgroup_ |  | Prefix applied to Ansible group names created from IDM hostgroups. |
| `hostvars_enabled` | bool | no | true |  | Export curated IDM host attributes as C(idm_*) host variables. Disable this when you only want host attribute export. Group variables derived from hostgroups, netgroups, or HBAC rules may still merge into hostvars during inventory processing. |
| `hostvars_include` | list | no |  |  | Restrict exported host-attribute IDM variables to this allowlist of C(idm_*) names. An empty list keeps the default curated set. Group variables derived from generated inventory groups are not filtered by this setting. Unknown variable names are rejected so inventory config fails fast instead of silently dropping requested metadata. |
| `include_disabled_hbacrules` | bool | no | false |  | Whether to include disabled HBAC rules. |
| `ipaadmin_password` | str | no |  |  | The admin password. Required when not using Kerberos authentication. |
| `ipaadmin_principal` | str | no | admin |  | The admin principal. |
| `kerberos_keytab` | str | no |  |  | Path to a Kerberos keytab file. When set together with C(use_kerberos), the plugin automatically runs C(kinit) with the keytab to obtain a ticket before authenticating to the IPA server. This eliminates the need for an interactive C(kinit) and is required for use inside AAP Execution Environments. The principal used with the keytab is taken from C(ipaadmin_principal) (default C(admin)). |
| `keyed_groups` | list | no |  |  | Add hosts to group based on the values of a variable. |
| `leading_separator` | boolean | no | true |  | Use in conjunction with O(keyed_groups). By default, a keyed group that does not have a prefix or a separator provided will have a name that starts with an underscore. This is because the default prefix is V("") and the default separator is V("_"). Set this option to V(false) to omit the leading underscore (or other separator) if no prefix is given. If the group name is derived from a mapping the separator is still used to concatenate the items. To not use a separator in the group name at all, set the separator for the keyed group to an empty string instead. |
| `netgroup_filter` | list | no |  |  | Limit netgroup-based groups to this list of netgroup names. An empty list means all netgroups are included. |
| `netgroup_prefix` | str | no | idm_netgroup_ |  | Prefix applied to Ansible group names created from IDM netgroups. |
| `plugin` |  | yes |  | eigenstate.ipa.idm, idm | Marks this as an instance of the C(idm) plugin. |
| `server` | str | yes |  |  | FQDN of the IPA server to query. |
| `sources` | list | no | hosts, hostgroups, netgroups, hbacrules |  | List of IDM object types to include in the inventory. C(hosts) adds all enrolled hosts. C(hostgroups), C(netgroups), and C(hbacrules) create Ansible groups from the corresponding IDM objects and populate them with their member hosts. |
| `strict` | bool | no | false |  | If V(yes) make invalid entries a fatal error, otherwise skip and continue. Since it is possible to use facts in the expressions they might not always be available and we ignore those errors by default. |
| `use_extra_vars` | bool | no | false |  | Merge extra vars into the available variables for composition (highest precedence). |
| `use_kerberos` | bool | no | false |  | Use Kerberos (GSSAPI) authentication instead of password authentication. Requires either a valid Kerberos ticket (obtained via C(kinit)) or a keytab file (see C(kerberos_keytab)). The following packages must be installed on the controller: C(krb5-workstation) (provides kinit), and one of C(python3-requests-gssapi) or C(python3-requests-kerberos) (provides the GSSAPI transport for requests). On RHEL/Fedora install with C(dnf install python3-requests-gssapi krb5-workstation). |
| `verify` | str | no |  |  | Path to the server TLS certificate file for verification (e.g. /etc/ipa/ca.crt). If not set, the plugin auto-detects C(/etc/ipa/ca.crt) when present and only falls back to disabled verification with a warning when no IdM CA path is available. |

## Return Values

This surface does not document structured return values.

## Examples

```yaml
# Minimal - all sources, password auth via environment
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"

# With explicit TLS verification
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
verify: /etc/ipa/ca.crt

# Only hostgroups and HBAC rules, filtered
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
sources:
  - hosts
  - hostgroups
  - hbacrules
hostgroup_filter:
  - webservers
  - databases
hbacrule_filter:
  - allow_ssh_admins

# Kerberos authentication with compose and keyed_groups
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
use_kerberos: true
compose:
  ansible_host: idm_fqdn
keyed_groups:
  - key: idm_location
    prefix: location
    separator: "_"
  - key: idm_os
    prefix: os
    separator: "_"
groups:
  has_keytab: idm_has_keytab | default(false)

# Kerberos with keytab (for AAP Execution Environments)
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
use_kerberos: true
kerberos_keytab: /path/to/admin.keytab
ipaadmin_principal: admin
verify: /etc/ipa/ca.crt

# Only keep hosts that belong to a filtered group
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
sources:
  - hosts
  - hostgroups
hostgroup_filter:
  - webservers
host_filter_from_groups: true

# Keep only selected host variables
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
hostvars_include:
  - idm_location
  - idm_os
  - idm_hostgroups
  - idm_userclass

# Selected host variables include normalized values and raw/type companions:
#   idm_userclass: ["platform", "database"]
#   idm_userclass_raw: ["platform", "database"]
#   idm_userclass_type: list
#   idm_location: "DC East"
#   idm_location_raw: ["DC East"]
#   idm_location_type: list
#   idm_schema_warnings: []

# With caching enabled (useful for large IDM deployments)
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
cache: true
cache_plugin: jsonfile
cache_timeout: 3600
cache_connection: ~/.ansible/cache/idm_inventory
```

## Error Behavior

Inventory failures prevent inventory construction. Validate IdM connectivity and authentication before using the inventory source in AAP or scheduled jobs.

## Related Pages

- [Authentication reference](../authentication.html)
- [Return shapes](../return-shapes.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

{% endraw %}

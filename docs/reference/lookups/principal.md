---
layout: default
title: eigenstate.ipa.principal lookup reference
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
  - ../../plugins/lookup/principal.py
last_verified: 2026-05-07
---
{% raw %}

# `eigenstate.ipa.principal` lookup reference

Query Kerberos principal state from FreeIPA/IDM

## Synopsis

Returns the existence, key state, lock state, and last authentication timestamp for Kerberos principals registered in FreeIPA/IDM.

Supports user, host, and service principal types with auto-detection from the principal name format.

Uses the C(ipalib) framework for all queries. Authentication follows the same keytab/password/existing-ticket pattern as other plugins in this collection.

Intended as a pre-flight check before keytab issuance, cert requests, or enrollment operations that silently fail when the target principal is absent or has no keys.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Authentication follows the options documented for this surface.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `_terms` | list | no |  |  | One or more principal names to inspect when C(operation=show). Accepts any of: C(HTTP/host.example.com), C(host/host.example.com), C(HTTP/host.example.com@REALM), C(admin), C(admin@REALM). Not required when C(operation=find). |
| `criteria` | str | no |  |  | Optional search string for C(operation=find). When omitted, all principals of the selected type are returned. |
| `ipaadmin_password` | str | no |  |  | Password for the admin principal. The plugin uses this to obtain a Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket already exists. |
| `ipaadmin_principal` | str | no | admin |  | The Kerberos principal to authenticate as. |
| `kerberos_keytab` | str | no |  |  | Path to a Kerberos keytab file. Used to obtain a ticket non-interactively (required for AAP Execution Environments). |
| `operation` | str | no | show | show, find | Which operation to perform. C(show) queries each named principal and returns its state. C(find) searches for principals matching optional C(criteria) within the specified C(principal_type). |
| `principal_type` | str | no | auto | auto, user, host, service | Which IdM object class to query. C(auto) detects from the principal name format: names containing C(/) are treated as service or host principals; names without C(/) are treated as users. C(host) expects C(host/fqdn) form or a bare FQDN. Required (non-auto) when C(operation=find). |
| `result_format` | str | no | record | record, map_record | How to shape the lookup result. C(record) returns a list of state dictionaries, one per principal. C(map_record) returns a single dictionary keyed by the input principal name. |
| `server` | str | yes |  |  | FQDN of the IPA server. |
| `verify` | str | no |  |  | Path to the IPA CA certificate for TLS verification. Set to C(false) to skip an explicit CA override and rely on the system trust behavior from C(ipalib). Falls back to C(/etc/ipa/ca.crt) when present; disables verification with a warning otherwise. |

## Notes

- This plugin requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible controller.
- RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)
- For principals that do not exist, the plugin returns a record with C(exists=false) rather than raising an error, allowing pre-flight conditionals without C(ignore_errors).
- C(disabled) is C(null) for host and service principals because IdM does not expose a lock state for those object types through the same mechanism as user accounts.
- C(last_auth) is populated only for user principals that have the C(krblastsuccessfulauth) attribute set in IdM (requires auditing to be enabled on the IdM server).

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `_raw` | list |  | One state record per principal. Each record is a dictionary with the fields below. When C(result_format=record) (default), returns a list of records; a single-term lookup is unwrapped by Ansible to a plain dict. When C(result_format=map_record), the lookup returns a dictionary keyed by the input principal name. |

## Examples

```yaml
# Check whether a service principal exists and has keys
- name: Pre-flight check before keytab issuance
  ansible.builtin.assert:
    that:
      - principal_state.exists
      - principal_state.has_keytab
    fail_msg: "Service principal is missing or has no keys"
  vars:
    principal_state: "{{ lookup('eigenstate.ipa.principal',
                          'HTTP/web01.example.com',
                          server='idm-01.example.com',
                          ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"

# Check a host principal
- name: Verify host enrolled before requesting cert
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.principal',
             'host/node01.example.com',
             server='idm-01.example.com',
             kerberos_keytab='/etc/admin.keytab') }}"

# Check a user principal for lock state
- name: Inspect user principal state
  ansible.builtin.set_fact:
    user_state: "{{ lookup('eigenstate.ipa.principal',
                    'svc-deploy',
                    server='idm-01.example.com',
                    kerberos_keytab='/etc/admin.keytab') }}"
- ansible.builtin.debug:
    msg: "Account locked: {{ user_state.disabled }}, last auth: {{ user_state.last_auth }}"

# Multiple principals in one lookup
- name: Pre-flight for several services
  ansible.builtin.set_fact:
    states: "{{ lookup('eigenstate.ipa.principal',
                'HTTP/web01.example.com', 'ldap/ldap01.example.com',
                server='idm-01.example.com',
                kerberos_keytab='/etc/admin.keytab') }}"

# Named mapping of multiple principals
- name: Pre-flight map for several services
  ansible.builtin.set_fact:
    state_map: "{{ lookup('eigenstate.ipa.principal',
                   'HTTP/web01.example.com', 'ldap/ldap01.example.com',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/admin.keytab',
                   result_format='map_record') }}"

# Find all service principals
- name: List all registered services
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.principal',
             operation='find',
             principal_type='service',
             server='idm-01.example.com',
             kerberos_keytab='/etc/admin.keytab') }}"

# Find service principals matching a pattern
- name: Find HTTP services
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.principal',
             operation='find',
             principal_type='service',
             criteria='HTTP',
             server='idm-01.example.com',
             kerberos_keytab='/etc/admin.keytab') }}"

# Use with environment variables
- name: Check principal using env-backed auth
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.principal', 'HTTP/web01.example.com') }}"
```

## Error Behavior

Lookup failures are task failures unless the caller handles them with Ansible error controls. Authentication, missing objects, invalid modes, and unavailable IdM APIs should be treated as explicit workflow failures.

## Related Pages

- [Authentication reference](/reference/authentication.html)
- [Return shapes](/reference/return-shapes.html)
- [Authority boundaries](/explanation/authority-boundaries.html)

{% endraw %}

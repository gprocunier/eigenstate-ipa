---
layout: default
title: eigenstate.ipa.hbacrule lookup reference
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
  - ../../plugins/lookup/hbacrule.py
last_verified: 2026-05-07
---
{% raw %}

# `eigenstate.ipa.hbacrule` lookup reference

Query HBAC rule state and run access tests against FreeIPA/IdM

## Synopsis

Returns the configuration of Host-Based Access Control (HBAC) rules registered in FreeIPA/IdM, including the identities and hosts in scope and whether the rule is currently active.

Can also invoke the FreeIPA C(hbactest) engine (C(operation=test)) to determine whether a specific user would be granted access to a specific host and service. This is the server-side evaluation of all applicable HBAC rules — the same logic SSSD uses at login.

HBAC rules are a dual-purpose object in FreeIPA. They control access directly, and they also provide the combined identity-and-host scope for SELinux user maps when a map is configured with HBAC-linked scope (C(seealso) set). Reading HBAC state is therefore a prerequisite for validating the full confinement model.

This plugin reads HBAC state for use in playbook conditionals and validation workflows. To create, modify, or delete HBAC rules use C(freeipa.ansible_freeipa.ipahbacrule).

Uses the C(ipalib) framework for all queries. Authentication follows the same keytab/password/existing-ticket pattern as other plugins in this collection.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Authentication follows the options documented for this surface.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `_terms` | list | no |  |  | For C(operation=show): one or more HBAC rule names to look up. For C(operation=test), the single username to test access for. Not required when C(operation=find). |
| `criteria` | str | no |  |  | Optional search string for C(operation=find). When omitted, all HBAC rules are returned. |
| `ipaadmin_password` | str | no |  |  | Password for the admin principal. Used to obtain a Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket already exists. |
| `ipaadmin_principal` | str | no | admin |  | The Kerberos principal to authenticate as. |
| `kerberos_keytab` | str | no |  |  | Path to a Kerberos keytab file. Used to obtain a ticket non-interactively (required for AAP Execution Environments). |
| `operation` | str | no | show | show, find, test | Which operation to perform. C(show) queries each named rule and returns its configuration. C(find) searches all rules, optionally filtered by C(criteria). C(test) invokes the FreeIPA C(hbactest) engine to evaluate whether C(_terms[0]) (the username) would be allowed to access C(targethost) via C(service). |
| `result_format` | str | no | record | record, map_record | How to shape the lookup result for C(operation=show) and C(operation=find). C(record) returns a list of rule dictionaries, one per entry. C(map_record) returns a single dictionary keyed by rule name. Ignored for C(operation=test). |
| `server` | str | yes |  |  | FQDN of the IPA server. |
| `service` | str | no |  |  | The HBAC service name to test against (e.g. C(sshd), C(sudo)). Required for C(operation=test). |
| `targethost` | str | no |  |  | The fully-qualified host name to test against. Required for C(operation=test). |
| `verify` | str | no |  |  | Path to the IPA CA certificate for TLS verification. Set to C(false) to skip an explicit CA override and rely on the system trust behavior from C(ipalib). Falls back to C(/etc/ipa/ca.crt) when present; disables verification with a warning otherwise. |

## Notes

- This plugin requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible controller.
- RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)
- For rules that do not exist, C(operation=show) returns a record with C(exists=false) rather than raising an error, allowing pre-flight conditionals without C(ignore_errors).
- C(operation=test) evaluates all applicable HBAC rules on the server. The C(denied) field is C(true) when access would be blocked. The C(matched) and C(notmatched) fields list every rule the server considered, which is useful for diagnosing unexpected allow or deny results.
- C(operation=test) requires that the test user and target host exist in FreeIPA. The test does not create authentication sessions — it is a dry-run policy evaluation only.

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `_raw` | list |  | For C(operation=show) and C(operation=find): one configuration record per HBAC rule. When C(result_format=record) (default), returns a list of records; a single-term lookup is unwrapped by Ansible to a plain dict. When C(result_format=map_record), returns a dictionary keyed by rule name. For C(operation=test), a single access test result record. |

## Examples

```yaml
# Validate that a named HBAC rule exists and is enabled
- name: Assert ops-deploy HBAC rule is active
  ansible.builtin.assert:
    that:
      - rule.exists
      - rule.enabled
    fail_msg: "HBAC rule 'ops-deploy' is missing or disabled"
  vars:
    rule: "{{ lookup('eigenstate.ipa.hbacrule',
               'ops-deploy',
               server='idm-01.example.com',
               kerberos_keytab='/etc/admin.keytab') }}"

# Test whether an automation account would be allowed to SSH to a host
- name: Verify automation-svc access before deploying
  ansible.builtin.assert:
    that: not access.denied
    fail_msg: >-
      automation-svc would be denied SSH on {{ inventory_hostname }}.
      Matched: {{ access.matched }}, Not matched: {{ access.notmatched }}
  vars:
    access: "{{ lookup('eigenstate.ipa.hbacrule',
                'automation-svc',
                operation='test',
                targethost=inventory_hostname,
                service='sshd',
                server='idm-01.example.com',
                kerberos_keytab='/etc/admin.keytab') }}"

# Find all enabled HBAC rules and log their names
- name: List all HBAC rules
  ansible.builtin.set_fact:
    all_rules: "{{ lookup('eigenstate.ipa.hbacrule',
                   operation='find',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/admin.keytab') }}"

# Retrieve multiple rules as a keyed dict
- name: Load rule state for several automation identities
  ansible.builtin.set_fact:
    rule_state: "{{ lookup('eigenstate.ipa.hbacrule',
                    'ops-deploy', 'ops-patch', 'ops-inventory',
                    server='idm-01.example.com',
                    kerberos_keytab='/etc/admin.keytab',
                    result_format='map_record') }}"
- ansible.builtin.assert:
    that: rule_state['ops-deploy'].enabled

# Inspect which services an HBAC rule permits
- name: Check allowed services for a rule
  ansible.builtin.debug:
    msg: >-
      Rule {{ rule.name }} allows services {{ rule.services }}
      and service groups {{ rule.servicegroups }}
  vars:
    rule: "{{ lookup('eigenstate.ipa.hbacrule',
               'ops-deploy',
               server='idm-01.example.com',
               kerberos_keytab='/etc/admin.keytab') }}"
```

## Error Behavior

Lookup failures are task failures unless the caller handles them with Ansible error controls. Authentication, missing objects, invalid modes, and unavailable IdM APIs should be treated as explicit workflow failures.

## Related Pages

- [Authentication reference](../authentication.html)
- [Return shapes](../return-shapes.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

{% endraw %}

---
layout: default
title: Sudo Use Cases
---

{% raw %}

# Sudo Use Cases

Related docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/sudo-plugin.html"><kbd>&nbsp;&nbsp;SUDO PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/sudo-capabilities.html"><kbd>&nbsp;&nbsp;SUDO CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html"><kbd>&nbsp;&nbsp;HBAC RULE USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

## Purpose

This page contains worked examples for `eigenstate.ipa.sudo` against
FreeIPA/IdM.

Use the capability guide to choose the right query shape. Use this page when
you need the corresponding playbook pattern or when sudo policy is only one
part of a broader IdM access gate.

## Contents

- [Use Case Flow](#use-case-flow)
- [1. Pre-flight Assert for a Named Sudo Rule](#1-pre-flight-assert-for-a-named-sudo-rule)
- [2. Verify a Rule Grants the Expected Command Surface](#2-verify-a-rule-grants-the-expected-command-surface)
- [3. Confirm a Shared Command Group Exists](#3-confirm-a-shared-command-group-exists)
- [4. Bulk Audit Disabled Sudo Rules](#4-bulk-audit-disabled-sudo-rules)
- [5. Build a Named Map of Rule State](#5-build-a-named-map-of-rule-state)
- [6. Gate Privileged Maintenance on Sudo and HBAC Together](#6-gate-privileged-maintenance-on-sudo-and-hbac-together)

## Use Case Flow

```mermaid
flowchart LR
    need["Privileged workflow or audit need"]
    type["Pick rule, command, or commandgroup"]
    lookup["Show one or find many"]
    gate["Assert, report, or combine with another policy check"]
    act["Proceed or fail"]

    need --> type --> lookup --> gate --> act
```

## 1. Pre-flight Assert for a Named Sudo Rule

Verify that the required sudo rule exists and is enabled before a play relies
on that policy.

```yaml
- name: Pre-flight - confirm sudo rule before maintenance
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Read sudo rule
      ansible.builtin.set_fact:
        sudo_rule: "{{ lookup('eigenstate.ipa.sudo',
                        'ops-maintenance',
                        sudo_object='rule',
                        server='idm-01.corp.example.com',
                        kerberos_keytab='/runner/env/ipa/admin.keytab',
                        verify='/etc/ipa/ca.crt') }}"

    - name: Assert sudo rule is present and enabled
      ansible.builtin.assert:
        that:
          - sudo_rule.exists
          - sudo_rule.enabled
        fail_msg: "Required sudo rule 'ops-maintenance' is missing or disabled."
```

## 2. Verify a Rule Grants the Expected Command Surface

Check that a rule grants the expected command or command group and does not
rely on a broader surface than intended.

```yaml
- name: Check sudo rule command assignments
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Read sudo rule
      ansible.builtin.set_fact:
        sudo_rule: "{{ lookup('eigenstate.ipa.sudo',
                        'ops-maintenance',
                        sudo_object='rule',
                        server='idm-01.corp.example.com',
                        kerberos_keytab='/runner/env/ipa/admin.keytab',
                        verify='/etc/ipa/ca.crt') }}"

    - name: Assert required commands are present
      ansible.builtin.assert:
        that:
          - "'/usr/bin/systemctl' in sudo_rule.allow_sudocmds"
          - "'system-ops' in sudo_rule.allow_sudocmdgroups"
        fail_msg: "The sudo rule does not grant the expected operations surface."
```

## 3. Confirm a Shared Command Group Exists

Validate that a reusable command group exists before expecting multiple rules to
reference it.

```yaml
- name: Confirm command group exists
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Read command group
      ansible.builtin.set_fact:
        system_ops: "{{ lookup('eigenstate.ipa.sudo',
                        'system-ops',
                        sudo_object='commandgroup',
                        server='idm-01.corp.example.com',
                        kerberos_keytab='/runner/env/ipa/admin.keytab',
                        verify='/etc/ipa/ca.crt') }}"

    - name: Assert group is present and contains systemctl
      ansible.builtin.assert:
        that:
          - system_ops.exists
          - "'/usr/bin/systemctl' in system_ops.commands"
        fail_msg: "Required sudo command group is missing or incomplete."
```

## 4. Bulk Audit Disabled Sudo Rules

Enumerate all sudo rules and report the disabled ones.

```yaml
- name: Audit disabled sudo rules
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Read all sudo rules
      ansible.builtin.set_fact:
        sudo_rules: "{{ lookup('eigenstate.ipa.sudo',
                        operation='find',
                        sudo_object='rule',
                        server='idm-01.corp.example.com',
                        kerberos_keytab='/runner/env/ipa/admin.keytab',
                        verify='/etc/ipa/ca.crt') }}"

    - name: Report disabled rules
      ansible.builtin.debug:
        msg: "Disabled sudo rules: {{ sudo_rules | selectattr('enabled', 'equalto', false) | map(attribute='name') | list }}"
```

## 5. Build a Named Map of Rule State

Load multiple rules as a keyed dict when later tasks need direct named access.

```yaml
- name: Build keyed sudo rule map
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Load rule state map
      ansible.builtin.set_fact:
        sudo_rule_map: "{{ lookup('eigenstate.ipa.sudo',
                            'ops-maintenance', 'breakglass',
                            sudo_object='rule',
                            result_format='map_record',
                            server='idm-01.corp.example.com',
                            kerberos_keytab='/runner/env/ipa/admin.keytab',
                            verify='/etc/ipa/ca.crt') }}"

    - name: Assert breakglass rule remains disabled in steady state
      ansible.builtin.assert:
        that:
          - not sudo_rule_map['breakglass'].enabled
        fail_msg: "breakglass rule is unexpectedly enabled."
```

## 6. Gate Privileged Maintenance on Sudo and HBAC Together

A sudo rule alone is not enough to make a maintenance workflow safe. The
identity also has to be allowed onto the host by current HBAC policy. This is
one of the highest-value cross-plugin checks in the collection.

```yaml
- name: Confirm privileged maintenance boundary
  hosts: localhost
  gather_facts: false

  vars:
    maintenance_identity: svc-maintenance
    target_host: app01.corp.example.com

  tasks:
    - name: Read sudo rule
      ansible.builtin.set_fact:
        sudo_rule: "{{ lookup('eigenstate.ipa.sudo',
                        'ops-maintenance',
                        sudo_object='rule',
                        server='idm-01.corp.example.com',
                        kerberos_keytab='/runner/env/ipa/admin.keytab',
                        verify='/etc/ipa/ca.crt') }}"

    - name: Run HBAC access test
      ansible.builtin.set_fact:
        access_result: "{{ lookup('eigenstate.ipa.hbacrule',
                            maintenance_identity,
                            operation='test',
                            targethost=target_host,
                            service='sshd',
                            server='idm-01.corp.example.com',
                            kerberos_keytab='/runner/env/ipa/admin.keytab',
                            verify='/etc/ipa/ca.crt') }}"

    - name: Assert privilege and access boundaries are both in place
      ansible.builtin.assert:
        that:
          - sudo_rule.exists
          - sudo_rule.enabled
          - not access_result.denied
        fail_msg: >-
          Maintenance should not proceed until both sudo policy and HBAC access
          allow {{ maintenance_identity }} onto {{ target_host }}.
```

Read next:
<a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html"><kbd>HBAC RULE USE CASES</kbd></a>

{% endraw %}

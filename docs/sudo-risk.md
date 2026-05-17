---
layout: default
title: Sudo risk classification
diataxis: how-to
diataxis_type: how-to
audience: Operators reviewing privileged sudo policy before automation consumes it
outcome: Classify sudo rule shapes with conservative advisory findings.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - command-output
public_status: new
last_verified: 2026-05-16
---
{% raw %}

# Sudo risk classification

Use the `eigenstate.ipa.sudo_risk` filter to classify an existing sudo rule
record. The classifier is advisory. The caller decides whether a finding blocks
a workflow.

```yaml
- name: Read a sudo rule
  ansible.builtin.set_fact:
    sudo_rule: "{{ lookup('eigenstate.ipa.sudo',
                    'automation-root',
                    sudo_object='rule',
                    server='idm-01.example.com',
                    kerberos_keytab='/runner/env/ipa/automation.keytab') }}"

- name: Classify sudo rule risk
  ansible.builtin.set_fact:
    sudo_risk: "{{ sudo_rule | eigenstate.ipa.sudo_risk }}"
```

Example result:

```yaml
risk_level: high
findings:
  - category: package_manager
    severity: high
    command: /usr/bin/dnf
    reason: package managers can alter host privileged state
recommendation: review_or_split_identity
```

Default categories include:

```text
shell_escape
package_manager
policy_management
idm_management
broad_file_write
unrestricted_runas
custom
```

Add site-specific patterns:

```yaml
- name: Classify with a local wrapper pattern
  ansible.builtin.set_fact:
    sudo_risk: >-
      {{ sudo_rule
         | eigenstate.ipa.classify_sudo_rule(
             custom_patterns={'package_manager': ['/opt/tools/pkgctl']}) }}
```

## Release gate

Validate a low-risk narrow command and high-risk package-manager,
policy-management, IdM-management, wildcard, and unrestricted RunAs examples.

{% endraw %}

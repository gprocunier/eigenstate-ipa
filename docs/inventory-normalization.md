---
layout: default
title: Inventory attribute normalization
diataxis: how-to
diataxis_type: how-to
audience: Operators consuming IdM host attributes in inventory or playbooks
outcome: Consume IdM host attributes with stable value, raw value, and type metadata.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - inventory-output
public_status: new
last_verified: 2026-05-16
---
{% raw %}

# Inventory attribute normalization

Use this when playbooks depend on IdM host attributes such as `userClass`,
hostgroup membership, or location and the source shape might vary between
hosts or FreeIPA responses.

The `eigenstate.ipa.idm` inventory plugin now exports three fields for each
selected host attribute:

```yaml
idm_userclass: ["platform", "database"]
idm_userclass_raw: ["platform", "database"]
idm_userclass_type: list
idm_schema_warnings: []
```

The normalized value is stable for automation. The `_raw` value preserves the
source value returned by IdM. The `_type` value records whether the source was
`list`, `string`, `dict`, `none`, `missing`, or `unexpected`.

## Normalize `idm_userclass`

```yaml
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
use_kerberos: true
kerberos_keytab: /runner/env/ipa/automation.keytab
verify: /etc/ipa/ca.crt
hostvars_include:
  - idm_userclass
  - idm_location
keyed_groups:
  - key: idm_userclass
    prefix: userclass
    separator: "_"
```

Expected hostvars:

```yaml
idm_userclass:
  - platform
  - database
idm_userclass_raw:
  - platform
  - database
idm_userclass_type: list
idm_schema_warnings: []
```

If `userClass` is missing, the normalized value is an empty list:

```yaml
idm_userclass: []
idm_userclass_raw:
idm_userclass_type: missing
```

If IdM returns a dictionary where a list is expected, the dictionary is not
stringified into a usable value:

```yaml
idm_userclass: []
idm_userclass_raw:
  role: database
idm_userclass_type: dict
idm_schema_warnings:
  - attribute: idm_userclass
    expected: list[str]
    actual: dict
    action: rejected
```

## Template filters

Use the filters when lookup or module data needs the same behavior outside the
inventory plugin.

```yaml
- name: Normalize a raw attribute
  ansible.builtin.set_fact:
    normalized_userclass: >-
      {{ raw_userclass
         | eigenstate.ipa.normalize_attribute(attribute='idm_userclass',
                                             expected='list') }}

- name: Keep only the normalized list
  ansible.builtin.set_fact:
    userclass_list: "{{ raw_userclass | eigenstate.ipa.ensure_list }}"
```

## Release gate

Before release, validate:

```bash
python -m pytest -q tests/test_attribute_normalization.py tests/test_inventory.py
ansible-doc -t inventory eigenstate.ipa.idm
ansible-doc -t filter eigenstate.ipa.normalization
```

{% endraw %}

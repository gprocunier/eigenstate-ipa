---
layout: default
title: Keytab Manage Module
description: >-
  Explicit Ansible module surface for safe Kerberos keytab retrieval,
  destination deployment, and guarded rotation in FreeIPA or Red Hat IdM.
---

{% raw %}

# Keytab Manage Module

Related docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>&nbsp;&nbsp;KEYTAB LOOKUP&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/mutation-surface-migration.html"><kbd>&nbsp;&nbsp;MUTATION MIGRATION&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/compatibility-policy.html"><kbd>&nbsp;&nbsp;COMPATIBILITY POLICY&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

`eigenstate.ipa.keytab_manage` retrieves existing keytabs or rotates keytab
material with explicit module semantics. It is the preferred surface for new
automation that writes keytabs to disk or intentionally rotates principal keys.

The existing `eigenstate.ipa.keytab` lookup remains supported. Use the module
when the task is a managed operation with side effects. Use the lookup when the
play needs compatibility with an established lookup-based workflow.

## Safety Model

| Operation | Module state | IdM side effect | Guardrail |
| --- | --- | --- | --- |
| Retrieve existing keys | `state: retrieved` | none beyond keytab extraction | uses `ipa-getkeytab -r` |
| Rotate principal keys | `state: rotated` | invalidates existing keytabs | requires `confirm_rotation: true` |
| Write keytab to disk | `destination` set | local file update | compares content and applies mode/owner/group |
| Return keytab content | `return_content: true` | none | explicit opt-in only |

By default, the module returns metadata only:

```yaml
changed: true
principal: HTTP/app.example.com@EXAMPLE.COM
state: retrieved
destination: /etc/httpd/conf/httpd.keytab
rotation_performed: false
mode: "0600"
```

It does not return keytab bytes unless `return_content: true` is set.

## Retrieval

```yaml
- name: Retrieve service keytab and deploy it
  eigenstate.ipa.keytab_manage:
    principal: HTTP/app.example.com@EXAMPLE.COM
    state: retrieved
    destination: /etc/httpd/conf/httpd.keytab
    mode: "0600"
    owner: apache
    group: apache
    server: idm-01.example.com
    kerberos_keytab: /runner/env/ipa/admin.keytab
```

`state: retrieved` uses existing keys only. It is appropriate for rebuilt
hosts, rehydrated execution environments, and repeatable service bootstrap
where the principal keys already exist.

## Rotation

```yaml
- name: Rotate service keytab with an explicit confirmation gate
  eigenstate.ipa.keytab_manage:
    principal: HTTP/app.example.com@EXAMPLE.COM
    state: rotated
    confirm_rotation: true
    destination: /etc/httpd/conf/httpd.keytab
    mode: "0600"
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"
```

Rotation generates new keys for the principal. Existing keytabs for that
principal stop working as soon as IdM accepts the rotation. Plan rotation as a
coordinated workflow:

1. preflight the consuming hosts and services
2. rotate the keytab once
3. deploy the new keytab to every consumer
4. restart or reload consumers as needed
5. verify Kerberos authentication from the deployed keytab

The module refuses `state: rotated` unless `confirm_rotation: true` is present.

## Check Mode

Check mode does not retrieve keytab content and does not rotate keys. It reports
the intended change boundary:

- `state: rotated` reports `changed: true` when confirmed
- `destination` reports `changed: true` because content comparison requires retrieval
- metadata-only retrieval without a destination reports no local change

Use live validation for the final content and service checks.

## Option Notes

- `kerberos_keytab`, `destination`, and `verify` are path-like where applicable.
- `mode` defaults to `0600`.
- `enctypes` maps to repeated `ipa-getkeytab -e` arguments.
- `verify: false` relies on local trust rather than passing an explicit CA path.

## When To Use The Lookup Instead

Keep using `eigenstate.ipa.keytab` when an existing playbook expects a lookup
return shape and does not need module-level destination management. New
automation that changes local files or rotates keys should use
`keytab_manage` so the side effect is visible in task output, check mode, and
review.

{% endraw %}

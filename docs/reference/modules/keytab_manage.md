---
layout: default
title: eigenstate.ipa.keytab_manage module reference
diataxis: reference
diataxis_type: reference
audience: Operators and maintainers looking up exact facts
outcome: Exact source-verified reference for this Ansible collection surface.
authority_boundary:
  - collection
workflow_boundary: mutating
evidence_shape:
  - ansible-doc
public_status: rewritten
source_material:
  - ../../plugins/modules/keytab_manage.py
last_verified: 2026-05-07
---
{% raw %}

# `eigenstate.ipa.keytab_manage` module reference

Retrieve or rotate Kerberos keytabs with explicit module semantics

## Synopsis

Retrieves existing Kerberos keytabs or explicitly rotates principal keys through C(ipa-getkeytab).

Provides a safer module surface for automation that writes keytabs to disk or performs rotation. The existing C(eigenstate.ipa.keytab) lookup remains available for compatibility.

Does not return raw keytab content unless C(return_content=true) is set.

Supports Ansible check mode where the module can report intended changes.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Uses platform Kerberos tooling and `ipa-getkeytab` for keytab retrieval or rotation behavior.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `confirm_rotation` | bool | no | false |  | Required confirmation gate for C(state=rotated). |
| `destination` | path | no |  |  | Optional controller-local path where the keytab should be written. |
| `enctypes` | list | no |  |  | Kerberos encryption types to request. |
| `group` | str | no |  |  | File group name or numeric GID for C(destination). |
| `ipaadmin_password` | str | no |  |  | Password for the principal. Used to obtain a Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket already exists. |
| `ipaadmin_principal` | str | no | admin |  | Kerberos principal to authenticate as. |
| `kerberos_keytab` | path | no |  |  | Path to a Kerberos keytab file for non-interactive authentication. |
| `mode` | raw | no | 0600 |  | File mode to apply when C(destination) is set. |
| `owner` | str | no |  |  | File owner name or numeric UID for C(destination). |
| `principal` | str | yes |  |  | Kerberos service or host principal whose keytab is managed. |
| `return_content` | bool | no | false |  | Return the base64-encoded keytab content. |
| `server` | str | yes |  |  | FQDN of the IPA server. |
| `state` | str | no | retrieved | retrieved, rotated | C(retrieved) retrieves existing keys only. C(rotated) generates new keys and invalidates all existing keytabs for the principal. |
| `verify` | raw | no |  |  | IPA CA certificate path for C(ipa-getkeytab --cacert), or C(false) to rely on the local trust store. |

## Notes

- Requires the platform package that provides C(ipa-getkeytab).
- C(state=rotated) invalidates every existing keytab for the principal.
- Keytab content is secret-bearing. Prefer C(destination) with restrictive mode.

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `changed` | bool | always | Whether the module changed the destination or rotated keys. |
| `content` | str | when return_content=true and not check mode | Base64-encoded keytab content. |
| `destination` | str | always | Destination path written by the module, if any. |
| `mode` | str | when destination is set | Effective file mode when C(destination) was written. |
| `principal` | str | always | Target Kerberos principal. |
| `rotation_performed` | bool | always | Whether the module rotated principal keys. |
| `state` | str | always | Requested module state. |

## Examples

```yaml
- name: Retrieve an existing service keytab
  eigenstate.ipa.keytab_manage:
    principal: HTTP/app.example.com@EXAMPLE.COM
    state: retrieved
    destination: /etc/httpd/conf/httpd.keytab
    mode: "0600"
    owner: apache
    group: apache
    server: idm-01.example.com
    kerberos_keytab: /runner/env/ipa/admin.keytab

- name: Rotate a service keytab with an explicit guard
  eigenstate.ipa.keytab_manage:
    principal: HTTP/app.example.com@EXAMPLE.COM
    state: rotated
    confirm_rotation: true
    destination: /etc/httpd/conf/httpd.keytab
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"
```

## Error Behavior

Module failures return through normal Ansible module failure handling. Use check mode where supported before mutating IdM, keytab, certificate, or filesystem state.

## Related Pages

- [Authentication reference](../authentication.html)
- [Return shapes](../return-shapes.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

{% endraw %}

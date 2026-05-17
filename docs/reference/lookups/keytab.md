---
layout: default
title: eigenstate.ipa.keytab lookup reference
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
  - ../../plugins/lookup/keytab.py
last_verified: 2026-05-16
---
{% raw %}

# `eigenstate.ipa.keytab` lookup reference

Retrieve Kerberos keytabs from FreeIPA/IDM

## Synopsis

Retrieves Kerberos keytab files for service or host principals registered in FreeIPA/IDM.

Uses C(ipa-getkeytab) from the local IdM client packages to perform the keytab extraction over an authenticated LDAP connection.

Authenticates via password (converted to a Kerberos ticket) or an existing Kerberos ticket/keytab.

Returns the keytab as a base64-encoded string suitable for writing to disk or injecting into an AAP credential type.

Supports retrieving existing keys (safe, default) or generating new random keys (rotates the principal and invalidates all existing keytabs).

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Uses platform Kerberos tooling and `ipa-getkeytab` for keytab retrieval or rotation behavior.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `_terms` | list | yes |  |  | One or more Kerberos principal names whose keytabs should be retrieved. Examples: C(HTTP/service.example.com), C(host/server.example.com@REALM), C(nfs/storage.example.com). |
| `enctypes` | list | no |  |  | List of Kerberos encryption types to request, for example C(["aes256-cts", "aes128-cts"]). When empty (the default) the IPA server chooses the encryption types based on its policy. |
| `ipaadmin_password` | str | no |  |  | Password for the admin principal. The plugin uses this to obtain a Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket already exists. The password must be usable for non-interactive C(kinit); an IPA account that is forced to change its password on first login will fail in this mode. |
| `ipaadmin_principal` | str | no | admin |  | The Kerberos principal to authenticate as. |
| `kerberos_keytab` | str | no |  |  | Path to a Kerberos keytab file. Used to obtain a ticket non-interactively (required for AAP Execution Environments). |
| `result_format` | str | no | value | value, record, map | Controls the shape of each returned item. C(value) returns the base64-encoded keytab string directly. C(record) returns a dict with C(principal) and C(value) keys. C(map) returns a single dict keyed by principal name with base64 values. |
| `retrieve_mode` | str | no | retrieve | retrieve, generate | Controls whether C(ipa-getkeytab) retrieves existing keys or generates new ones. C(retrieve) passes the C(-r) flag and only retrieves existing keys; it fails if no keys exist yet. C(generate) omits C(-r) and may generate new random keys for the principal. WARNING - C(generate) rotates the principal's keys and immediately invalidates every existing keytab for that principal, including those held by running services. |
| `server` | str | yes |  |  | FQDN of the IPA server. |
| `verify` | raw | no |  |  | Path to the IPA CA certificate for an explicit C(--cacert) override, or C(false) to rely on the local system trust configuration instead. If not set, the plugin tries C(/etc/ipa/ca.crt) and otherwise falls back to the system trust store with a warning. |

## Notes

- The package that provides C(ipa-getkeytab) must be installed on the control node or execution environment. On RHEL 10, install C(ipa-client). On other releases, install the package that provides C(/usr/sbin/ipa-getkeytab).
- C(ipaadmin_password) requires a password that can be used with non-interactive C(kinit). Accounts forced to change password on first login are not suitable for this mode.
- The C(generate) retrieve mode rotates the principal's keys. Any service or host that holds an existing keytab for the principal will be unable to authenticate until it receives the new keytab. Use C(retrieve) unless you are explicitly rotating credentials.
- Keytabs are binary files. The plugin always returns base64-encoded content regardless of result_format. Decode before writing to disk.
- The authenticating principal must have permission to retrieve keytabs for the target principal. In most environments this requires admin rights or explicit delegation via IPA RBAC.

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `_raw` | list |  | A list containing one item per requested principal. Each item is either a base64-encoded keytab string (C(result_format=value)), a dict with C(principal) and C(value) keys (C(result_format=record)), or a single dict keyed by principal name (C(result_format=map), returned as a one-element list containing the dict). |

## Examples

```yaml
# Retrieve an existing keytab for an HTTP service principal
- name: Retrieve HTTP service keytab
  ansible.builtin.set_fact:
    http_keytab_b64: "{{ lookup('eigenstate.ipa.keytab',
                          'HTTP/webserver.idm.corp.lan',
                          server='idm-01.idm.corp.lan',
                          ipaadmin_password=lookup('env', 'IPA_PASSWORD'),
                          verify='/etc/ipa/ca.crt') }}"
  no_log: true

# Retrieve using a keytab for non-interactive authentication
- name: Retrieve NFS service keytab via admin keytab auth
  ansible.builtin.set_fact:
    nfs_keytab_b64: "{{ lookup('eigenstate.ipa.keytab',
                          'nfs/storage.idm.corp.lan',
                          server='idm-01.idm.corp.lan',
                          ipaadmin_principal='admin',
                          kerberos_keytab='/runner/env/ipa/admin.keytab',
                          verify='/etc/ipa/ca.crt') }}"
  no_log: true

# Write the keytab to disk on the target host
- name: Deploy HTTP keytab
  ansible.builtin.copy:
    content: "{{ lookup('eigenstate.ipa.keytab',
                   'HTTP/webserver.idm.corp.lan',
                   server='idm-01.idm.corp.lan',
                   kerberos_keytab='/runner/env/ipa/admin.keytab',
                   verify='/etc/ipa/ca.crt') | b64decode }}"
    dest: /etc/httpd/conf/httpd.keytab
    mode: "0600"
    owner: apache
    group: apache
  no_log: true

# Retrieve keytab as a record with principal metadata
- name: Retrieve keytab with record format
  ansible.builtin.set_fact:
    keytab_record: "{{ query('eigenstate.ipa.keytab',
                        'HTTP/webserver.idm.corp.lan',
                        server='idm-01.idm.corp.lan',
                        kerberos_keytab='/runner/env/ipa/admin.keytab',
                        result_format='record',
                        verify='/etc/ipa/ca.crt') | first }}"
  no_log: true
  # keytab_record.principal == 'HTTP/webserver.idm.corp.lan'
  # keytab_record.value     == base64-encoded keytab

# Retrieve keytabs for multiple principals in one lookup
- name: Retrieve keytabs for all web services
  ansible.builtin.set_fact:
    web_keytabs: "{{ query('eigenstate.ipa.keytab',
                      'HTTP/web-01.idm.corp.lan',
                      'HTTP/web-02.idm.corp.lan',
                      server='idm-01.idm.corp.lan',
                      kerberos_keytab='/runner/env/ipa/admin.keytab',
                      result_format='map',
                      verify='/etc/ipa/ca.crt') | first }}"
  no_log: true
  # web_keytabs['HTTP/web-01.idm.corp.lan'] == base64 keytab
  # web_keytabs['HTTP/web-02.idm.corp.lan'] == base64 keytab

# Retrieve with explicit encryption types
- name: Retrieve keytab with aes256 only
  ansible.builtin.set_fact:
    keytab_b64: "{{ lookup('eigenstate.ipa.keytab',
                      'HTTP/webserver.idm.corp.lan',
                      server='idm-01.idm.corp.lan',
                      kerberos_keytab='/runner/env/ipa/admin.keytab',
                      enctypes=['aes256-cts'],
                      verify='/etc/ipa/ca.crt') }}"
  no_log: true

# Generate new keys (ROTATES - invalidates all existing keytabs)
- name: Rotate HTTP service keytab
  ansible.builtin.set_fact:
    new_keytab_b64: "{{ lookup('eigenstate.ipa.keytab',
                          'HTTP/webserver.idm.corp.lan',
                          server='idm-01.idm.corp.lan',
                          kerberos_keytab='/runner/env/ipa/admin.keytab',
                          retrieve_mode='generate',
                          verify='/etc/ipa/ca.crt') }}"
  no_log: true
```

## Output Shape

```yaml
# value (default)
- "MIIEvQIBADANBgkqhk...<base64>"

# result_format: record
- principal: "HTTP/webserver.idm.corp.lan"
  value: "MIIEvQIBADANBgkqhk...<base64>"
  encoding: "base64"

# result_format: map
- HTTP/webserver.idm.corp.lan: "MIIEvQIBADANBgkqhk...<base64>"
```

## Error Behavior

Lookup failures are task failures unless the caller handles them with Ansible error controls. Authentication, missing objects, invalid modes, and unavailable IdM APIs should be treated as explicit workflow failures.

## Related Pages

- [Authentication reference](../authentication.html)
- [Return shapes](../return-shapes.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

{% endraw %}

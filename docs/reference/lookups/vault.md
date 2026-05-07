---
layout: default
title: eigenstate.ipa.vault lookup reference
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
  - ../../plugins/lookup/vault.py
last_verified: 2026-05-07
---
{% raw %}

# `eigenstate.ipa.vault` lookup reference

Retrieve secrets from FreeIPA/IDM vaults

## Synopsis

Retrieves secret data from FreeIPA/IDM vaults.

Supports standard, symmetric, and asymmetric vault types.

Uses the C(ipalib) framework for vault operations, which handles transport encryption and vault-level decryption automatically.

Authenticates via password (converted to a Kerberos ticket) or an existing Kerberos ticket/keytab.

Can be used as a credential source in AAP by referencing the lookup in a custom credential type injector.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Authentication follows the options documented for this surface.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `_terms` | list | no |  |  | One or more vault names to retrieve or inspect when C(operation=retrieve) or C(operation=show). Not required when C(operation=find). |
| `criteria` | str | no |  |  | Search criteria used when C(operation=find). If omitted, the find operation lists the selected vault scope without a text filter. |
| `decode_json` | bool | no | false |  | When set to C(true), parse decoded UTF-8 vault payloads as JSON and return structured data instead of a raw string. Only valid with C(encoding=utf-8) and C(operation=retrieve). |
| `encoding` | str | no | utf-8 | utf-8, base64 | How to return the vault data. C(utf-8) decodes the bytes to a string (suitable for passwords, API keys, PEM certificates). C(base64) returns the data as a base64-encoded string (suitable for binary secrets like keytabs or PKCS12 bundles). |
| `include_metadata` | bool | no | false |  | When set to C(true), include vault metadata fields in retrieved structured records. This is only valid with C(operation=retrieve) and C(result_format=record) or C(result_format=map_record). The lookup uses vault metadata already read during preflight when possible, and falls back to best-effort metadata retrieval if needed. |
| `ipaadmin_password` | str | no |  |  | Password for the admin principal. The plugin uses this to obtain a Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket already exists. |
| `ipaadmin_principal` | str | no | admin |  | The Kerberos principal to authenticate as. |
| `kerberos_keytab` | str | no |  |  | Path to a Kerberos keytab file. Used to obtain a ticket non-interactively (required for AAP Execution Environments). |
| `operation` | str | no | retrieve | retrieve, show, find | Which vault operation to perform. C(retrieve) returns secret payloads, C(show) returns metadata for the named vaults, and C(find) searches the selected vault scope and returns matching metadata records. |
| `private_key_file` | str | no |  |  | Path to the private key file for decrypting an asymmetric vault. |
| `result_format` | str | no | value | value, record, map, map_record | How to shape the lookup result. C(value) returns only the decoded secret value. C(record) returns a list of structured result records with the vault name, scope, encoding, and value. C(map) returns a dictionary of vault name to decoded value. C(map_record) returns a dictionary of vault name to structured result record. |
| `server` | str | yes |  |  | FQDN of the IPA server. |
| `service` | str | no |  |  | Retrieve a service vault owned by this service principal. Mutually exclusive with C(username) and C(shared). |
| `shared` | bool | no | false |  | Retrieve a shared vault. Mutually exclusive with C(username) and C(service). |
| `strip_trailing_newline` | bool | no | false |  | When set to C(true), remove a single trailing newline from decoded UTF-8 payloads before returning them. Useful for password-like secrets stored with a trailing newline. |
| `username` | str | no |  |  | Retrieve a user vault owned by this user. Mutually exclusive with C(service) and C(shared). |
| `vault_password` | str | no |  |  | Password to decrypt a symmetric vault. |
| `vault_password_file` | str | no |  |  | Path to a file containing the symmetric vault password. |
| `verify` | str | no |  |  | Path to the IPA CA certificate for TLS verification. If omitted, the plugin tries C(/etc/ipa/ca.crt). If no CA path is available, the lookup fails unless C(verify) is set to C(false) explicitly. |

## Notes

- This plugin requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible controller. These handle the vault transport encryption and vault-level decryption automatically.
- RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)
- For symmetric vaults, provide C(vault_password) or C(vault_password_file).
- For asymmetric vaults, provide C(private_key_file).
- Standard vaults require no additional decryption parameters.
- Local secret material referenced through C(kerberos_keytab), C(vault_password_file), or C(private_key_file) should normally be owner-readable only, such as mode C(0600).

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `_raw` | raw |  | The decrypted vault data. One element per vault name requested. Returned as a UTF-8 string by default, or base64-encoded if C(encoding=base64). If C(result_format=record), each element is a structured dictionary containing the name, scope, encoding, and decoded value. If C(include_metadata=true), retrieved structured records also include vault metadata fields such as type, description, and vault_id. When C(decode_json=true), UTF-8 payloads are parsed into structured JSON values. When C(result_format=map) or C(result_format=map_record), the return value is a dictionary keyed by vault name. Metadata-only operations C(show) and C(find) return structured records. |

## Examples

```yaml
# Retrieve a standard shared vault using environment-backed auth
- name: Get database password
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault', 'database-password',
             server='idm-01.example.com',
             ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
             shared=true) }}"

# Retrieve a symmetric vault
- name: Get API key from symmetric vault
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault', 'api-key',
             server='idm-01.example.com',
             ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
             shared=true,
             vault_password=lookup('env', 'IPA_VAULT_PASSWORD')) }}"

# Retrieve an asymmetric vault
- name: Get TLS private key from asymmetric vault
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault', 'tls-key',
             server='idm-01.example.com',
             ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
             shared=true,
             private_key_file='/path/to/private.pem') }}"

# Retrieve a user vault with keytab auth (AAP)
- name: Get user secret
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault', 'my-secret',
             server='idm-01.example.com',
             kerberos_keytab='/path/to/admin.keytab',
             username='appuser') }}"

# Retrieve a binary secret as base64
- name: Get keytab from vault
  ansible.builtin.copy:
    content: "{{ lookup('eigenstate.ipa.vault', 'service-keytab',
                  server='idm-01.example.com',
                  ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
                  shared=true,
                  encoding='base64') | b64decode }}"
    dest: /etc/krb5.keytab
    mode: "0600"

# Multiple vaults in one lookup
- name: Retrieve several secrets
  ansible.builtin.set_fact:
    secrets: "{{ lookup('eigenstate.ipa.vault', 'db-pass', 'api-key',
                  server='idm-01.example.com',
                  ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
                  shared=true) }}"

# Return a named mapping instead of a positional list
- name: Retrieve several secrets as a dictionary
  ansible.builtin.set_fact:
    secrets_by_name: "{{ lookup('eigenstate.ipa.vault', 'db-pass', 'api-key',
                          server='idm-01.example.com',
                          ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
                          shared=true,
                          result_format='map') }}"

# Decode a JSON secret into structured data
- name: Retrieve structured JSON config
  ansible.builtin.set_fact:
    app_config: "{{ lookup('eigenstate.ipa.vault', 'app-config',
                    server='idm-01.example.com',
                    kerberos_keytab='/path/to/admin.keytab',
                    shared=true,
                    decode_json=true) }}"

# Retrieve an encrypted artifact with metadata for brokered delivery
- name: Get sealed artifact with routing metadata
  ansible.builtin.set_fact:
    sealed_artifact: "{{ lookup('eigenstate.ipa.vault', 'payments-bootstrap-bundle',
                         server='idm-01.example.com',
                         kerberos_keytab='/path/to/admin.keytab',
                         shared=true,
                         encoding='base64',
                         result_format='record',
                         include_metadata=true) }}"

# Inspect one vault without retrieving the secret payload
- name: Show vault metadata
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault', 'database-password',
             server='idm-01.example.com',
             kerberos_keytab='/path/to/admin.keytab',
             shared=true,
             operation='show') }}"

# Find vaults in the selected scope
- name: List shared vaults that match a string
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault',
             server='idm-01.example.com',
             kerberos_keytab='/path/to/admin.keytab',
             shared=true,
             operation='find',
             criteria='database') }}"

# Use with env vars (set IPA_SERVER, IPA_ADMIN_PASSWORD)
- name: Get secret using environment
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault', 'my-secret', shared=true) }}"
```

## Error Behavior

Lookup failures are task failures unless the caller handles them with Ansible error controls. Authentication, missing objects, invalid modes, and unavailable IdM APIs should be treated as explicit workflow failures.

## Related Pages

- [Authentication reference](../authentication.html)
- [Return shapes](../return-shapes.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

{% endraw %}

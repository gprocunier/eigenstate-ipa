---
layout: default
title: eigenstate.ipa.otp lookup reference
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
  - ../../plugins/lookup/otp.py
last_verified: 2026-05-07
---
{% raw %}

# `eigenstate.ipa.otp` lookup reference

Generate and manage OTP tokens and host enrollment passwords in FreeIPA/IdM

## Synopsis

Generates TOTP and HOTP two-factor authentication tokens for IdM users via C(otptoken_add).

Generates one-time enrollment passwords for IdM hosts via C(host_mod --random), suitable for consumption by C(freeipa.ansible_freeipa.ipaclient) or C(freeipa.ansible_freeipa.ipahost).

Supports full token lifecycle management via C(find), C(show), and C(revoke) operations.

All operations use the C(ipalib) RPC framework. No CLI tools are invoked.

Authenticates via password (converted to a Kerberos ticket), a keytab file, or an existing Kerberos ticket.

Can be used as a credential source in AAP by referencing the lookup in a custom credential type injector.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Authentication follows the options documented for this surface.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `_terms` | list | no |  |  | Identifiers to operate on. Meaning varies by C(operation) and C(token_type). For C(operation=add) with C(token_type=totp) or C(token_type=hotp), one or more IdM usernames whose tokens should be created. For C(operation=add) with C(token_type=host), one or more host FQDNs for which enrollment passwords should be generated. For C(operation=find), an optional substring search pattern; omit to return all tokens accessible to the authenticated principal. For C(operation=show) and C(operation=revoke), one or more token unique IDs (C(ipatokenuniqueid)). |
| `algorithm` | str | no | sha1 | sha1, sha256, sha384, sha512 | HMAC algorithm used to generate the OTP value. Only applies to C(token_type=totp) and C(token_type=hotp). |
| `description` | str | no |  |  | Optional description attached to the new token. Only used by C(operation=add) with C(token_type=totp) or C(token_type=hotp). |
| `digits` | int | no | 6 | 6, 8 | Number of digits in the generated OTP value. Only applies to C(token_type=totp) and C(token_type=hotp). |
| `interval` | int | no | 30 |  | Time step in seconds for TOTP tokens. Only meaningful for C(token_type=totp). Ignored with a warning for C(token_type=hotp) and C(token_type=host). |
| `ipaadmin_password` | str | no |  |  | Password for the admin principal. The plugin uses this to obtain a Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket already exists. |
| `ipaadmin_principal` | str | no | admin |  | The Kerberos principal to authenticate as. |
| `kerberos_keytab` | str | no |  |  | Path to a Kerberos keytab file. Used to obtain a ticket non-interactively (required for AAP Execution Environments). |
| `operation` | str | no | add | add, find, show, revoke | Which OTP operation to perform. C(add) creates a new token or host enrollment password. C(find) searches for existing tokens. C(show) retrieves metadata for a specific token by ID. C(revoke) permanently deletes one or more tokens by ID. |
| `owner` | str | no |  |  | Filter C(operation=find) results to tokens owned by this user. Ignored with a warning for other operations. |
| `result_format` | str | no |  | value, record, map, map_record | How to shape the lookup result. C(value) returns only the token URI (C(otpauth://) string) for user tokens, or only the enrollment password for host tokens. C(record) returns a list of structured result records. C(map) returns a dictionary of identifier to bare value. C(map_record) returns a dictionary of identifier to structured record. C(value) is the default for C(operation=add); C(record) is the default for C(operation=find) and C(operation=show). Not applicable to C(operation=revoke), which always returns a list of deleted token IDs. |
| `server` | str | yes |  |  | FQDN of the IPA server. |
| `token_type` | str | no | totp | totp, hotp, host | The kind of credential to create. C(totp) generates a time-based one-time password token for an IdM user. C(hotp) generates an HMAC-based counter token. C(host) generates a one-time enrollment password for an IdM host. Only used by C(operation=add). |
| `verify` | raw | no |  |  | Path to the IPA CA certificate for TLS verification. Set C(false) to disable verification explicitly. If omitted, C(/etc/ipa/ca.crt) is used when present; otherwise the lookup fails until the operator provides a CA path or opts out explicitly. |

## Notes

- This plugin requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible controller.
- RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)
- SECURITY: TOTP and HOTP token URIs (C(otpauth://)) embed the shared secret. Treat the C(uri) field as sensitive credential material. Use C(no_log: true) on any task that registers or displays a token URI. Store URIs only in encrypted storage (vaults, AAP credentials, etc.).
- The C(uri) field is only present in C(operation=add) results. C(find) and C(show) return token metadata without the shared secret.
- Host enrollment passwords (C(token_type=host)) are consumed on first use by C(ipa-client-install). Pass them to C(freeipa.ansible_freeipa.ipaclient) or C(freeipa.ansible_freeipa.ipahost) rather than invoking the CLI directly.
- C(operation=show) returns a record with C(exists=false) when the token ID is not found, rather than raising an error. This enables non-fatal pre-flight checks.
- C(operation=revoke) raises an error if a token ID is not found. Revocation is not idempotent by design.
- The authenticating principal must have the C(Manage OTP Tokens) privilege in IdM to create, find, show, or revoke tokens. Host enrollment password generation requires the C(Modify Hosts) privilege.

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `_raw` | raw |  | One element per term. When C(operation=add) and C(result_format=value) (the default), each element is the C(otpauth://) URI string for user tokens, or the one-time enrollment password string for C(token_type=host). When C(result_format=record), each element is a structured dictionary (see below). When C(result_format=map) or C(result_format=map_record), the return is a dictionary keyed by owner username, host FQDN, or token ID depending on operation. For C(operation=find) and C(operation=show), the default is C(result_format=record). For C(operation=revoke), a list of deleted token unique IDs is returned regardless of C(result_format). |

## Examples

```yaml
# Generate a TOTP token for a user (URI contains the shared secret)
- name: Provision user MFA token
  ansible.builtin.set_fact:
    totp_uri: "{{ lookup('eigenstate.ipa.otp', 'jsmith',
                   server='idm-01.example.com',
                   ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"
  no_log: true

# Generate a host enrollment OTP and pass it to ansible-freeipa
- name: Generate enrollment password
  ansible.builtin.set_fact:
    enroll_pass: "{{ lookup('eigenstate.ipa.otp', inventory_hostname,
                      token_type='host',
                      server='idm-01.example.com',
                      kerberos_keytab='/etc/ansible/admin.keytab') }}"
  no_log: true
  delegate_to: localhost

- name: Enroll host using ansible-freeipa
  ansible.builtin.include_role:
    name: freeipa.ansible_freeipa.ipaclient
  vars:
    ipaclient_hostname: "{{ inventory_hostname }}"
    ipaclient_password: "{{ enroll_pass }}"

# Generate an HOTP token with 8-digit codes using sha256
- name: Provision HOTP token
  ansible.builtin.set_fact:
    token_record: "{{ lookup('eigenstate.ipa.otp', 'svcaccount',
                       token_type='hotp',
                       algorithm='sha256',
                       digits=8,
                       result_format='record',
                       server='idm-01.example.com',
                       ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"
  no_log: true

# Find all tokens for a specific user
- name: List user tokens
  ansible.builtin.set_fact:
    user_tokens: "{{ lookup('eigenstate.ipa.otp',
                      owner='jsmith',
                      operation='find',
                      server='idm-01.example.com',
                      ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"

# Check whether a token exists before rotation (no_log not needed; show returns no secret)
- name: Inspect token by ID
  ansible.builtin.set_fact:
    token_state: "{{ lookup('eigenstate.ipa.otp', 'some-token-uuid',
                      operation='show',
                      server='idm-01.example.com',
                      ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"

# Revoke a specific token
- name: Revoke token
  ansible.builtin.debug:
    msg: "Revoked: {{ lookup('eigenstate.ipa.otp', 'some-token-uuid',
                      operation='revoke',
                      server='idm-01.example.com',
                      ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"

# Rotate: revoke old token, issue new one
- name: Rotate user token
  ansible.builtin.set_fact:
    new_uri: "{{ lookup('eigenstate.ipa.otp', 'jsmith',
                  server='idm-01.example.com',
                  ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"
  no_log: true
  when: >-
    lookup('eigenstate.ipa.otp', (old_token_id | string),
      operation='show',
      server='idm-01.example.com',
      ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'))[0].exists
```

## Error Behavior

Lookup failures are task failures unless the caller handles them with Ansible error controls. Authentication, missing objects, invalid modes, and unavailable IdM APIs should be treated as explicit workflow failures.

## Related Pages

- [Authentication reference](../authentication.html)
- [Return shapes](../return-shapes.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

{% endraw %}

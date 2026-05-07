---
layout: default
title: eigenstate.ipa.cert_request module reference
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
  - ../../plugins/modules/cert_request.py
last_verified: 2026-05-07
---
{% raw %}

# `eigenstate.ipa.cert_request` module reference

Request IdM CA certificates with safe module returns

## Synopsis

Submits a CSR to the FreeIPA/IdM CA and optionally writes the issued certificate to a controller-local destination.

Provides explicit module semantics for certificate issuance while the existing C(eigenstate.ipa.cert) lookup remains available for compatibility.

Returns certificate metadata by default. Certificate content is returned only when C(return_content=true) is set.

Private key generation and handling remain outside this module.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Authentication follows the options documented for this surface.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `add` | bool | no | false |  | Create the principal if it does not already exist. |
| `ca` | str | no |  |  | Sub-CA name to issue from. |
| `csr` | str | no |  |  | Inline PEM certificate signing request. |
| `csr_file` | path | no |  |  | Controller-local path to a PEM certificate signing request. |
| `destination` | path | no |  |  | Optional controller-local path where the certificate should be written. |
| `encoding` | str | no | pem | pem, base64 | Certificate output encoding. |
| `group` | str | no |  |  | File group name or numeric GID for C(destination). |
| `ipaadmin_password` | str | no |  |  | Password for the principal. |
| `ipaadmin_principal` | str | no | admin |  | Kerberos principal to authenticate as. |
| `kerberos_keytab` | path | no |  |  | Path to a Kerberos keytab file for non-interactive authentication. |
| `mode` | raw | no | 0644 |  | File mode to apply when C(destination) is set. |
| `owner` | str | no |  |  | File owner name or numeric UID for C(destination). |
| `principal` | str | yes |  |  | Service or host principal to request a certificate for. |
| `profile` | str | no |  |  | Certificate profile ID to use. |
| `return_content` | bool | no | false |  | Return the issued certificate content. |
| `server` | str | yes |  |  | FQDN of the IPA server. |
| `verify` | raw | no |  |  | IPA CA certificate path for TLS verification, or C(false). |

## Notes

- Requires C(python3-ipalib) and C(python3-ipaclient).
- The module never accepts or returns private key material.

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `changed` | bool | always | Whether the module requested a certificate or changed the destination. |
| `content` | str | when return_content=true and not check mode | Issued certificate content. |
| `destination` | str | always | Destination path written by the module, if any. |
| `metadata` | dict | always | Safe certificate metadata. |
| `principal` | str | always | Target principal. |

## Examples

```yaml
- name: Request a service certificate and write it to disk
  eigenstate.ipa.cert_request:
    principal: HTTP/app.example.com@EXAMPLE.COM
    csr_file: /etc/pki/tls/certs/app.csr
    destination: /etc/pki/tls/certs/app.pem
    mode: "0644"
    server: idm-01.example.com
    kerberos_keytab: /runner/env/ipa/admin.keytab

- name: Request a certificate and keep the result metadata-only
  eigenstate.ipa.cert_request:
    principal: HTTP/app.example.com@EXAMPLE.COM
    csr: "{{ app_csr }}"
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"
```

## Error Behavior

Module failures return through normal Ansible module failure handling. Use check mode where supported before mutating IdM, keytab, certificate, or filesystem state.

## Related Pages

- [Authentication reference](/reference/authentication.html)
- [Return shapes](/reference/return-shapes.html)
- [Authority boundaries](/explanation/authority-boundaries.html)

{% endraw %}

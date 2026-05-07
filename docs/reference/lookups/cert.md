---
layout: default
title: eigenstate.ipa.cert lookup reference
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
  - ../../plugins/lookup/cert.py
last_verified: 2026-05-07
---
{% raw %}

# `eigenstate.ipa.cert` lookup reference

Request or retrieve certificates from FreeIPA/IDM PKI

## Synopsis

Submits a CSR to the IdM/FreeIPA Dogtag CA and returns a signed certificate (C(operation=request)).

Retrieves an existing certificate by serial number (C(operation=retrieve)).

Searches certificates by principal, subject, or expiry window (C(operation=find)).

Uses the C(ipalib) framework for all CA operations and Kerberos transport.  No C(certmonger) daemon is required on the target.

Authenticates via a Kerberos keytab, a password, or an existing Kerberos ticket in the environment.

Designed as a drop-in alternative to HashiCorp Vault's PKI secrets engine when Red Hat IdM is already the identity backend.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Authentication follows the options documented for this surface.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `_terms` | list | no |  |  | For C(operation=request): one or more service or host principals to request a certificate for (e.g. C(HTTP/web.example.com@EXAMPLE.COM)).  For C(operation=retrieve): one or more certificate serial numbers (decimal or hex C(0x...)). Not used when C(operation=find). |
| `add` | bool | no | false |  | When C(true), automatically create the service or host principal in IdM if it does not already exist.  Equivalent to C(ipa cert-request --add). |
| `ca` | str | no |  |  | Name of the sub-CA to issue the certificate from.  Defaults to the root IPA CA.  Run C(ipa ca-find) to list available CAs. |
| `csr` | str | no |  |  | Certificate Signing Request as an inline PEM string.  Used only with C(operation=request).  Mutually exclusive with C(csr_file). |
| `csr_file` | str | no |  |  | Path to a PEM-formatted CSR file on the Ansible controller.  Used only with C(operation=request).  Mutually exclusive with C(csr). |
| `encoding` | str | no | pem | pem, base64 | Certificate output format.  C(pem) wraps the DER bytes in PEM headers (suitable for writing directly to files or passing to other modules).  C(base64) returns the raw base64-encoded DER (suitable for binary pipelines or storage in IdM vaults). |
| `exactly` | bool | no | false |  | When C(true), C(subject) is matched exactly rather than as a substring.  Used only with C(operation=find). |
| `ipaadmin_password` | str | no |  |  | Password for the admin principal.  The plugin uses this to obtain a Kerberos ticket via C(kinit).  Not required if C(kerberos_keytab) is set or a valid ticket already exists. |
| `ipaadmin_principal` | str | no | admin |  | The Kerberos principal to authenticate as. |
| `kerberos_keytab` | str | no |  |  | Path to a Kerberos keytab file.  Used to obtain a ticket non-interactively (required for AAP Execution Environments). |
| `operation` | str | no | request | request, retrieve, find | Which PKI operation to perform.  C(request) submits a CSR and returns the signed certificate.  C(retrieve) fetches a certificate by serial number.  C(find) searches the CA for certificates matching the supplied filters. |
| `principal` | str | no |  |  | Filter certificates by service or host principal.  Used only with C(operation=find). |
| `profile` | str | no |  |  | Certificate profile ID to use when signing.  If not set, the IdM default profile (C(caIPAserviceCert)) is used.  Run C(ipa certprofile-find) to list available profiles. |
| `result_format` | str | no | value | value, record, map, map_record | How to shape the lookup result.  C(value) returns only the certificate string.  C(record) returns a structured dictionary with the certificate value and metadata.  C(map) returns a dictionary keyed by principal or serial number to certificate value.  C(map_record) returns a dictionary keyed by principal or serial number to the full structured record. |
| `revocation_reason` | int | no |  |  | Filter by revocation reason code (0-10).  Used only with C(operation=find).  See RFC 5280 section 5.3.1 for reason codes. |
| `server` | str | yes |  |  | FQDN of the IPA server. |
| `subject` | str | no |  |  | Filter certificates by subject DN substring.  Used only with C(operation=find). |
| `valid_not_after_from` | str | no |  |  | Lower bound for the certificate expiry date (ISO 8601 YYYY-MM-DD). Returns certificates that expire on or after this date.  Used only with C(operation=find).  Combine with C(valid_not_after_to) to build a maintenance window query. |
| `valid_not_after_to` | str | no |  |  | Upper bound for the certificate expiry date (ISO 8601 YYYY-MM-DD). Returns certificates that expire on or before this date.  Used only with C(operation=find). |
| `verify` | str | no |  |  | Path to the IPA CA certificate for TLS verification. Defaults to C(/etc/ipa/ca.crt) when that file exists. If no CA path is available, the lookup fails unless C(verify) is set to C(false) explicitly. |

## Notes

- Requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible controller.
- RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)
- The authenticating principal must hold the C(Request Certificate) IdM privilege (or equivalent ACI) to use C(operation=request).
- C(operation=retrieve) and C(operation=find) require only standard read access to the IPA CA.
- CSR files referenced via C(csr_file) should be owner-readable only (mode C(0600)) when they contain private material.
- When C(add=true) the principal must not already exist, otherwise IdM returns an error.  Use C(operation=find) to check first.

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `_raw` | raw |  | Certificate data for the requested operation.  The exact structure depends on C(result_format) and C(operation). For C(operation=request) or C(operation=retrieve): one element per term.  For C(operation=find): a list of matching certificates. With C(result_format=value) (default): a PEM string per certificate, or base64-encoded DER when C(encoding=base64). With C(result_format=record): each element is a structured dictionary containing the certificate value plus metadata (serial_number, subject, issuer, valid_not_before, valid_not_after, san, revoked, revocation_reason). With C(result_format=map) or C(result_format=map_record): a dictionary keyed by the service principal (for C(request)) or serial number string (for C(retrieve) and C(find)). |

## Examples

```yaml
# Request a certificate for an HTTP service principal
- name: Request TLS certificate for web server
  ansible.builtin.copy:
    content: "{{ lookup('eigenstate.ipa.cert',
                  'HTTP/web.example.com@EXAMPLE.COM',
                  operation='request',
                  server='idm-01.example.com',
                  kerberos_keytab='/etc/krb5.keytab',
                  csr_file='/etc/pki/tls/certs/web.csr') }}"
    dest: /etc/pki/tls/certs/web.pem
    mode: "0644"

# Request a cert and capture full metadata
- name: Request cert with metadata
  ansible.builtin.set_fact:
    cert_record: "{{ lookup('eigenstate.ipa.cert',
                      'HTTP/web.example.com@EXAMPLE.COM',
                      operation='request',
                      server='idm-01.example.com',
                      ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
                      csr=my_csr_variable,
                      result_format='record') }}"

- name: Show expiry date
  ansible.builtin.debug:
    msg: "Certificate expires: {{ cert_record.metadata.valid_not_after }}"

# Request with a specific profile and sub-CA
- name: Request cert with custom profile
  ansible.builtin.set_fact:
    cert_pem: "{{ lookup('eigenstate.ipa.cert',
                   'vault/backup.example.com@EXAMPLE.COM',
                   operation='request',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/krb5.keytab',
                   csr=csr_content,
                   profile='caIPAserviceCert',
                   ca='internal-ca') }}"

# Request and auto-create the principal if missing
- name: Bootstrap new service principal with cert
  ansible.builtin.set_fact:
    new_cert: "{{ lookup('eigenstate.ipa.cert',
                   'HTTP/newhost.example.com@EXAMPLE.COM',
                   operation='request',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/krb5.keytab',
                   csr=csr_content,
                   add=true) }}"

# Retrieve a certificate by serial number (decimal)
- name: Retrieve cert by serial
  ansible.builtin.set_fact:
    cert_pem: "{{ lookup('eigenstate.ipa.cert', '12345',
                   operation='retrieve',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/krb5.keytab') }}"

# Retrieve multiple certificates by serial; map by serial number
- name: Retrieve several certs as a dictionary
  ansible.builtin.set_fact:
    certs: "{{ lookup('eigenstate.ipa.cert',
                '12345', '67890',
                operation='retrieve',
                server='idm-01.example.com',
                kerberos_keytab='/etc/krb5.keytab',
                result_format='map') }}"

# Find all certificates expiring within 30 days (pre-expiry maintenance)
- name: Find certs expiring soon
  ansible.builtin.set_fact:
    expiring: "{{ lookup('eigenstate.ipa.cert',
                   operation='find',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/krb5.keytab',
                   valid_not_after_from='2026-04-05',
                   valid_not_after_to='2026-05-05',
                   result_format='record') }}"

# Find all certs issued to a specific service principal
- name: Find certs for a principal
  ansible.builtin.set_fact:
    principal_certs: "{{ lookup('eigenstate.ipa.cert',
                          operation='find',
                          server='idm-01.example.com',
                          kerberos_keytab='/etc/krb5.keytab',
                          principal='HTTP/web.example.com@EXAMPLE.COM',
                          result_format='map_record') }}"

# Retrieve cert as raw base64 DER for use with Java keystores
- name: Get cert as base64 DER
  ansible.builtin.set_fact:
    cert_der_b64: "{{ lookup('eigenstate.ipa.cert', '12345',
                       operation='retrieve',
                       server='idm-01.example.com',
                       kerberos_keytab='/etc/krb5.keytab',
                       encoding='base64') }}"
```

## Error Behavior

Lookup failures are task failures unless the caller handles them with Ansible error controls. Authentication, missing objects, invalid modes, and unavailable IdM APIs should be treated as explicit workflow failures.

## Related Pages

- [Authentication reference](../authentication.html)
- [Return shapes](../return-shapes.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

{% endraw %}

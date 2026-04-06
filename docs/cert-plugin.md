# IdM Cert Plugin

Nearby docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>&nbsp;&nbsp;IDM CERT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>&nbsp;&nbsp;IDM VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

## Purpose

`eigenstate.ipa.cert` requests, retrieves, and searches certificates from the
IdM CA directly from Ansible.

This reference covers:

- how the plugin authenticates to IdM
- which operations it supports and when to use each
- how to supply a CSR for signing
- how to return a certificate as PEM or base64
- what metadata fields accompany each result
- how result shapes differ across formats

IdM runs a full Dogtag CA. This plugin gives automation a direct interface to
it without requiring certmonger on the target host or shell-out tasks for each
service principal.

## Contents

- [Request Model](#request-model)
- [Authentication Model](#authentication-model)
- [Operations](#operations)
- [CSR Input](#csr-input)
- [Serial Number Format](#serial-number-format)
- [Find Filters](#find-filters)
- [Return Encoding](#return-encoding)
- [Return Shapes And Normalization](#return-shapes-and-normalization)
- [Result Metadata Fields](#result-metadata-fields)
- [Minimal Examples](#minimal-examples)
- [Failure Boundaries](#failure-boundaries)
- [When To Read The Scenario Guide](#when-to-read-the-scenario-guide)

## Request Model

```mermaid
flowchart LR
    ans["Ansible task or template"]
    lookup["eigenstate.ipa.cert"]
    krb["Kerberos ticket\nexisting, password-derived,\nor keytab-derived"]
    ipa["ipalib cert APIs"]
    ca["IdM CA\nDogtag PKI"]
    out["Lookup return value\nPEM or base64, with metadata"]

    ans --> lookup
    lookup --> krb
    krb --> ipa
    ipa --> ca
    ca --> out
```

The lookup calls the IdM Python client library directly through `ipalib`. No
external HTTP or REST call is made outside that stack. The CA backend is
Dogtag. The authentication layer is Kerberos.

## Authentication Model

The lookup always operates with a Kerberos credential cache.

It can get there in three ways:

- `ipaadmin_password`:
  - obtains a ticket before connecting
- `kerberos_keytab`:
  - obtains a ticket non-interactively
- neither password nor keytab:
  - assumes a valid existing ticket is already available

> [!IMPORTANT]
> The lookup plugin requires `python3-ipalib` and `python3-ipaclient` on the
> controller or execution environment. It also requires `krb5-workstation` when
> a ticket must be acquired dynamically. The plugin warns if any input file
> (`kerberos_keytab`, `csr_file`) has permissions broader than `0600`.

TLS behavior:

- `verify: /path/to/ca.crt` enables explicit certificate verification
- omitting `verify` first tries `/etc/ipa/ca.crt`
- if no local IdM CA path is available, the plugin warns and falls back to the
  system CA bundle behavior from `ipalib`

## Operations

The lookup supports three operations:

- `request`:
  - default
  - submits a CSR to the IdM CA and returns the signed certificate
  - requires `terms` to be one or more service principals
  - requires a CSR via `csr` or `csr_file`
  - returns one result per term
- `retrieve`:
  - returns an existing certificate by serial number without re-signing
  - `terms` must be one or more serial numbers (decimal, hex `0x...`, or int)
  - returns one result per term
- `find`:
  - searches the CA for certificates matching optional filter criteria
  - `terms` is ignored
  - returns a list of zero or more results

`request` and `retrieve` are per-term and return a list of the same length as
`terms`. `find` is a single bulk call and returns however many the CA matches.

## CSR Input

For `operation='request'`, provide the CSR as one of:

- `csr`:
  - inline PEM string
- `csr_file`:
  - path to a PEM file on the controller

These are mutually exclusive. Exactly one must be provided.

The CSR must be PEM-formatted. The plugin passes it to `ipalib` unchanged. The
subject CN in the CSR should match the principal being requested.

> [!NOTE]
> When a single CSR is used with multiple principals in `terms`, the same CSR
> is submitted for each principal. If each principal needs a distinct CSR,
> call the lookup once per principal.

Profile and CA override parameters for `request`:

- `profile`:
  - certificate profile ID (default: `caIPAserviceCert`)
- `ca`:
  - CA name (default: `ipa`)
- `add`:
  - boolean; auto-creates the principal in IdM if it does not already exist
    (default: `false`)

## Serial Number Format

For `operation='retrieve'`, each term must be a serial number. Accepted forms:

- decimal string: `"12345"`
- hexadecimal string with prefix: `"0x3039"`
- integer: `12345`

The plugin normalizes all forms to an integer before calling `cert_show`.

## Find Filters

For `operation='find'`, all filter parameters are optional. Calling `find`
with no filters returns all certificates the principal has access to and emits a
warning. Useful filters:

- `principal`:
  - filter by service or host principal string
- `subject`:
  - substring match against the certificate subject
- `valid_not_after_from`:
  - ISO 8601 date string; return certs expiring on or after this date
- `valid_not_after_to`:
  - ISO 8601 date string; return certs expiring on or before this date
- `revocation_reason`:
  - integer 0–10; filter by revocation reason code
- `exactly`:
  - boolean; when `true`, requires an exact subject match rather than substring

Combining `valid_not_after_from` and `valid_not_after_to` creates an expiry
window. That is the primary pattern for pre-expiry maintenance plays.

## Return Encoding

Each certificate result carries a `value` field. Encoding controls its form:

- `pem`:
  - default
  - `-----BEGIN CERTIFICATE-----` / `-----END CERTIFICATE-----` wrapped at 64
    characters per line
  - best for writing `.crt` files or inlining a cert for a service config
- `base64`:
  - raw base64-encoded DER
  - best when the consuming task will decode the bytes directly

Both encodings are derived from the base64 DER returned by `ipalib`. No
external cryptography dependency is required.

## Return Shapes And Normalization

The default return shape is `value`: a plain list of certificate strings, one
per result.

Use `result_format: record` when the caller needs cert identity alongside the
value. Each element is then a dictionary:

- `name`:
  - principal (for `request`), serial number string (for `retrieve` and `find`)
- `value`:
  - PEM or base64 string
- `encoding`:
  - `pem` or `base64`
- `metadata`:
  - nested dict; see [Result Metadata Fields](#result-metadata-fields)

Additional container shapes:

- `result_format: map`:
  - returns `{name: value}`
- `result_format: map_record`:
  - returns `{name: {name, value, encoding, metadata}}`

The mapping forms are useful when multiple principals or serials are requested
in one call and the playbook must not depend on positional list ordering.

For `operation='find'`, the key in `map` and `map_record` is the
`serial_number` string from the metadata. Serial numbers are unique per IdM CA
and unambiguous as a key.

## Result Metadata Fields

Every `record` or `map_record` result includes a `metadata` dict with:

| Field | Type | Description |
| --- | --- | --- |
| `serial_number` | int | CA-assigned serial number |
| `subject` | str | Certificate subject DN |
| `issuer` | str | Certificate issuer DN |
| `valid_not_before` | str | Validity start (ISO string from IdM) |
| `valid_not_after` | str | Validity end (ISO string from IdM) |
| `san` | list | Subject Alternative Names; may be empty |
| `revoked` | bool | Whether the certificate has been revoked |
| `revocation_reason` | int or None | Revocation reason code, or None if not revoked |

`valid_not_after` is the field to compare when building expiry-window plays.
Use `result_format: map_record` with `operation='find'` and
`valid_not_after_to` to retrieve a pre-indexed map of certificates expiring
before a given date.

## Minimal Examples

Request a signed certificate for a service principal:

```yaml
- ansible.builtin.set_fact:
    api_cert: "{{ lookup('eigenstate.ipa.cert',
                   'HTTP/api.example.com@EXAMPLE.COM',
                   operation='request',
                   server='idm-01.example.com',
                   kerberos_keytab='/runner/env/ipa/admin.keytab',
                   csr_file='/runner/env/csr/api.example.com.csr',
                   verify='/etc/ipa/ca.crt') }}"
```

Retrieve an existing certificate by serial number:

```yaml
- ansible.builtin.set_fact:
    cert_pem: "{{ lookup('eigenstate.ipa.cert',
                   '12345',
                   operation='retrieve',
                   server='idm-01.example.com',
                   kerberos_keytab='/runner/env/ipa/admin.keytab',
                   verify='/etc/ipa/ca.crt') }}"
```

Find certificates expiring within a window:

```yaml
- ansible.builtin.set_fact:
    expiring_certs: "{{ lookup('eigenstate.ipa.cert',
                          operation='find',
                          server='idm-01.example.com',
                          kerberos_keytab='/runner/env/ipa/admin.keytab',
                          valid_not_after_from='2026-04-01',
                          valid_not_after_to='2026-06-30',
                          result_format='map_record',
                          verify='/etc/ipa/ca.crt') }}"
```

Request with full record including metadata:

```yaml
- ansible.builtin.set_fact:
    cert_record: "{{ lookup('eigenstate.ipa.cert',
                      'HTTP/web.example.com@EXAMPLE.COM',
                      operation='request',
                      server='idm-01.example.com',
                      ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
                      csr=my_csr_pem_string,
                      profile='caIPAserviceCert',
                      result_format='record',
                      verify='/etc/ipa/ca.crt') }}"
```

Return the signed cert as base64 DER:

```yaml
- ansible.builtin.set_fact:
    cert_der: "{{ lookup('eigenstate.ipa.cert',
                   'HTTP/svc.example.com@EXAMPLE.COM',
                   operation='request',
                   server='idm-01.example.com',
                   kerberos_keytab='/runner/env/ipa/admin.keytab',
                   csr_file='/runner/env/csr/svc.csr',
                   encoding='base64',
                   verify='/etc/ipa/ca.crt') }}"
```

## Failure Boundaries

Common failure classes are:

- missing `ipalib` libraries on the controller or EE
- no valid Kerberos ticket and no password or keytab supplied
- CSR subject or SAN does not match the principal under `request`
- principal does not exist in IdM and `add=false`
- serial number not found under `retrieve`
- CA rejected the CSR due to profile mismatch or policy violation

> [!NOTE]
> A `request` failure citing a subject mismatch usually means the CN or SAN in
> the CSR does not match the service principal name registered in IdM. Verify
> the principal with `ipa service-show` before submitting.

> [!CAUTION]
> The `add=true` parameter auto-creates the principal if it is missing. Use
> this only in controlled automation where principal namespace hygiene is
> managed at the play level. In shared environments, prefer requiring the
> principal to exist first.

## When To Read The Scenario Guide

Use <a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>IDM CERT CAPABILITIES</kbd></a> when
you need operator patterns rather than option-by-option reference:

- TLS certificate deployment for a service principal
- pre-expiry maintenance and mass renewal
- cert lifecycle from request through install
- expiry audits integrated with inventory-backed targeting
- cert plus private key bundle assembly patterns

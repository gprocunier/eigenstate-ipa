---
layout: default
title: eigenstate.ipa.dns lookup reference
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
  - ../../plugins/lookup/dns.py
last_verified: 2026-05-07
---
{% raw %}

# `eigenstate.ipa.dns` lookup reference

Query IdM integrated DNS records from FreeIPA/IdM

## Synopsis

Returns DNS record state from the integrated FreeIPA/IdM DNS service.

Supports read-only C(show) and C(find) operations for zone-scoped DNS records through the IdM C(dnsrecord_show) and C(dnsrecord_find) APIs.

Uses the C(ipalib) framework for all queries. Authentication follows the same keytab/password/existing-ticket pattern as other plugins in this collection.

Use this plugin when playbooks need to validate forward or reverse records, confirm zone-apex entries, or audit the DNS names and record data that the IdM DNS APIs expose directly.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Authentication follows the options documented for this surface.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `_terms` | list | no |  |  | One or more DNS record names to look up when C(operation=show). Names are relative to C(zone). Use C(@) for the zone apex record. Not required when C(operation=find). |
| `criteria` | str | no |  |  | Optional search string for C(operation=find). When omitted, all records in C(zone) are returned. |
| `ipaadmin_password` | str | no |  |  | Password for the admin principal. Used to obtain a Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket already exists. |
| `ipaadmin_principal` | str | no | admin |  | The Kerberos principal to authenticate as. |
| `kerberos_keytab` | str | no |  |  | Path to a Kerberos keytab file. Used to obtain a ticket non-interactively (required for AAP Execution Environments). |
| `operation` | str | no | show | show, find | Which operation to perform. C(show) queries each named record and returns its state. C(find) searches all records in C(zone), optionally filtered by C(criteria) and C(record_type). Native IdM DNS search semantics apply, so treat this as an IdM-side search surface rather than a full zone transfer. |
| `record_type` | str | no |  | arecord, aaaarecord, cnamerecord, mxrecord, naptrrecord, nsrecord, ptrrecord, srvrecord, sshfprecord, tlsarecord, txtrecord, urirecord | Optional record-type filter for C(operation=find). When set, only records containing that concrete DNS RR type are returned. The filter applies to the record data returned by IdM, not to the record name. |
| `result_format` | str | no | record | record, map_record | How to shape the lookup result. C(record) returns a list of records, one per DNS entry. C(map_record) returns a single dictionary keyed by the record name. |
| `server` | str | yes |  |  | FQDN or IP address of the IPA server. |
| `verify` | str | no |  |  | Path to the IPA CA certificate for TLS verification. Set to C(false) to skip an explicit CA override and rely on the system trust behavior from C(ipalib). Falls back to C(/etc/ipa/ca.crt) when present; disables verification with a warning otherwise. |
| `zone` | str | yes |  |  | DNS zone to query. This is required for both C(show) and C(find). Examples include C(workshop.lan) and C(0.16.172.in-addr.arpa). |

## Notes

- This plugin requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible controller.
- RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)
- For records that do not exist, C(operation=show) returns a record with C(exists=false) rather than raising an error, allowing pre-flight conditionals without C(ignore_errors).
- The plugin returns DNS RR data in the generic C(records) dictionary, keyed by record type (for example C(arecord), C(ptrrecord), or C(sshfprecord)). This keeps the surface stable across the wide IdM DNS schema.
- Template-backed DNS attributes such as location-aware CNAME templates are returned in the C(template_records) dictionary.
- Zone-apex metadata fields such as C(zone_active) and the SOA values are returned when the IdM DNS APIs expose them for the queried record.

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `_raw` | list |  | One record per DNS entry. When C(result_format=record) (default), returns a list of records; a single-term lookup is unwrapped by Ansible to a plain dict. When C(result_format=map_record), returns a dictionary keyed by record name. |

## Examples

```yaml
# Read one host record from a zone
- name: Load idm-01 DNS record
  ansible.builtin.set_fact:
    dns_record: "{{ lookup('eigenstate.ipa.dns',
                     'idm-01',
                     zone='workshop.lan',
                     server='idm-01.example.com',
                     kerberos_keytab='/etc/admin.keytab') }}"

# Read the zone apex record
- name: Inspect the zone apex entry
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.dns',
             '@',
             zone='workshop.lan',
             server='idm-01.example.com',
             kerberos_keytab='/etc/admin.keytab') }}"

# Find PTR records in a reverse zone
- name: List PTR records in 0.16.172.in-addr.arpa
  ansible.builtin.set_fact:
    ptr_records: "{{ lookup('eigenstate.ipa.dns',
                      operation='find',
                      zone='0.16.172.in-addr.arpa',
                      record_type='ptrrecord',
                      server='idm-01.example.com',
                      kerberos_keytab='/etc/admin.keytab') }}"

# Load several records into a keyed map
- name: Build a record map for core infrastructure names
  ansible.builtin.set_fact:
    dns_map: "{{ lookup('eigenstate.ipa.dns',
                  'idm-01', 'bastion-01', 'mirror-registry',
                  zone='workshop.lan',
                  result_format='map_record',
                  server='idm-01.example.com',
                  kerberos_keytab='/etc/admin.keytab') }}"
```

## Error Behavior

Lookup failures are task failures unless the caller handles them with Ansible error controls. Authentication, missing objects, invalid modes, and unavailable IdM APIs should be treated as explicit workflow failures.

## Related Pages

- [Authentication reference](/reference/authentication.html)
- [Return shapes](/reference/return-shapes.html)
- [Authority boundaries](/explanation/authority-boundaries.html)

{% endraw %}

---
layout: default
title: Certificate Inventory Report
description: Schema and workflow notes for certificate inventory reporting.
---

{% raw %}

# Certificate Inventory Report

Role: `eigenstate.ipa.certificate_inventory_report`

Schema: `eigenstate.ipa/certificate_inventory_report/v1`

This report captures certificate metadata for renewal planning and audit
handoff. It is not a certificate export mechanism and must not contain private
keys or secret payloads.

## Required Record Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `principal` | string | Host or service principal associated with the certificate. |
| `serial_number` | string | Certificate serial number. |
| `not_after` | string | Expiration timestamp or date. |
| `state` | string | `valid`, `expiring`, `expired`, `revoked`, or `unknown`. |

Useful optional fields include `subject`, `issuer`, `not_before`, `profile_id`,
`san_names`, `rotation_required`, and `evidence`.

Run:

```bash
ansible-playbook playbooks/report-certificate-inventory.yml
```

{% endraw %}

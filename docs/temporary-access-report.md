---
layout: default
title: Temporary Access Report
description: Schema and workflow notes for temporary access evidence reporting.
---

{% raw %}

# Temporary Access Report

Role: `eigenstate.ipa.temporary_access_report`

Schema: `eigenstate.ipa/temporary_access_report/v1`

This report records temporary access windows and associated controls. It is a
read-only evidence artifact for active, expired, scheduled, or revoked access.

## Required Record Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `principal` | string | User, host, or service principal. |
| `target` | string | Target system, group, service, or access boundary. |
| `status` | string | `active`, `expired`, `scheduled`, `revoked`, or `unknown`. |

Useful optional fields include `access_type`, `opened_at`, `expires_at`,
`controls`, and `evidence`.

Run:

```bash
ansible-playbook playbooks/report-temporary-access.yml
```

{% endraw %}

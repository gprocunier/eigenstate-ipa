---
layout: default
title: Keytab Rotation Candidate Report
description: Schema and workflow notes for keytab rotation candidate reporting.
---

{% raw %}

# Keytab Rotation Candidate Report

Role: `eigenstate.ipa.keytab_rotation_candidates`

Schema: `eigenstate.ipa/keytab_rotation_candidates/v1`

This report identifies principals that should be reviewed for keytab rotation.
It does not retrieve, render, or rotate keytabs. Rotation remains a separate
opt-in remediation workflow.

## Required Record Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `principal` | string | Host or service principal. |
| `candidate` | boolean | Whether the principal is a rotation candidate. |
| `remediation_workflow` | string | The separate workflow that would rotate keys. |

Useful optional fields include `owner`, `location_hint`, `last_rotated_at`,
`max_age_days`, and `reason`.

Run:

```bash
ansible-playbook playbooks/report-keytab-rotation-candidates.yml
```

{% endraw %}

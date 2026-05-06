---
layout: default
title: Policy Drift Report
description: Schema and workflow notes for read-only policy drift reporting.
---

{% raw %}

# Policy Drift Report

Role: `eigenstate.ipa.policy_drift_report`

Schema: `eigenstate.ipa/policy_drift_report/v1`

This report compares expected and observed policy records from IdM, AAP, and
OpenShift-adjacent contexts. It reports drift without changing policy.

## Finding Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Stable policy identifier. |
| `kind` | string | Policy type, such as `hbacrule`, `sudo`, or `rbac`. |
| `status` | string | `in_sync`, `drifted`, `missing`, `extra`, or `unknown`. |
| `remediation_workflow` | string | Separate opt-in workflow that would make changes. |

Useful optional fields include `severity`, `expected`, `observed`, and
`recommendation`.

Run:

```bash
ansible-playbook playbooks/report-policy-drift.yml
```

{% endraw %}

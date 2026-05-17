---
layout: default
title: Generate operational evidence
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this to render readiness, certificate, keytab, temporary access, or drift reports without remediation.
authority_boundary:
  - idm
  - reports
  - collection
workflow_boundary: read-only
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-17
---
{% raw %}

# Generate operational evidence

## When To Use This

Use this to render readiness, certificate, keytab, temporary access, or drift reports without remediation.

## Required Authority

Reports record supplied evidence. They do not enforce remediation.

## Safety Boundary

This workflow is `read-only`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Inputs

- Named target objects
- Credentials with the required IdM or platform authority
- A reviewed output path or downstream task

## Steps

1. Confirm the target objects and authority before running.
2. Run the command or task with review-friendly output.
3. Inspect the returned evidence before continuing to any mutating step.

```bash
ansible-playbook playbooks/report-idm-readiness.yml
```

{% endraw %}
{% include task_example.html id="generate-operational-evidence" %}
{% raw %}

## Expected Evidence

The playbook renders read-only JSON, YAML, and Markdown report artifacts. A
captured local validation run of `playbooks/report-idm-readiness.yml` produced
this output:

```text
PLAY [Render IdM readiness report] *********************************************

TASK [eigenstate.ipa.idm_readiness_report : Validating arguments against arg spec 'main' - Render deterministic IdM readiness evidence reports.] ***
ok: [localhost]

TASK [eigenstate.ipa.idm_readiness_report : Validate IdM readiness report format choices] ***
ok: [localhost] => {
    "changed": false,
    "msg": "All assertions passed"
}

TASK [eigenstate.ipa.idm_readiness_report : Build IdM readiness report object] ***
ok: [localhost]

TASK [eigenstate.ipa.idm_readiness_report : Render IdM readiness JSON report] ***
changed: [localhost]

TASK [eigenstate.ipa.idm_readiness_report : Render IdM readiness YAML report] ***
changed: [localhost]

TASK [eigenstate.ipa.idm_readiness_report : Render IdM readiness Markdown report] ***
changed: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=8    changed=4    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

The JSON artifact carries stable review fields:

```json
{
  "schema": "eigenstate.ipa/idm_readiness_report/v1",
  "schema_version": "1.0",
  "role": "idm_readiness_report",
  "read_only": true,
  "summary": {
    "total_checks": 2,
    "passed_checks": 2,
    "warning_checks": 0,
    "failed_checks": 0,
    "informational_checks": 0
  }
}
```

## Troubleshooting

- Permission failure: verify the account and delegated authority.
- Unexpected empty result: verify target names and source records.
- Unsafe output: redact payloads and add `no_log: true` where secret material is present.

## Related Reference

- [/reference/roles/reports.html](../reference/roles/reports.html)
- [/explanation/authority-boundaries.html](../explanation/authority-boundaries.html)

{% endraw %}

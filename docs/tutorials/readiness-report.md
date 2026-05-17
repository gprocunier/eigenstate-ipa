---
layout: default
title: Generate an IdM readiness report
diataxis: tutorial
diataxis_type: tutorial
audience: Operators learning IdM-backed automation flows
outcome: Learn read-only operational evidence generation.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-17
---
{% raw %}

# Generate an IdM readiness report

## What You Will Build

JSON, YAML, or Markdown readiness evidence from explicit inputs.

## What You Need Before Starting

- Report role dependencies available in the active Ansible environment
- Input records from inventory, lookups, or lab fixtures
- An output directory for report artifacts

## Lab Assumptions

- Reports are read-only.
- Missing records should be represented as status, not fixed automatically.
- Use lab fixtures before live evidence.

## Step-By-Step Path

1. Prepare explicit input records.
2. Run the readiness report wrapper.
3. Inspect JSON for automation and Markdown for review.
4. Use findings to decide a separate remediation workflow.

```bash
ansible-playbook readiness-report.yml
```

{% endraw %}
{% include task_example.html id="readiness-report" %}
{% raw %}

## Expected Evidence

The role writes JSON/YAML/Markdown outputs under `./artifacts`. A captured run
from this checkout produced:

```text
PLAY [Render IdM readiness report] *********************************************

TASK [eigenstate.ipa.idm_readiness_report : Create IdM readiness report output directory] ***
changed: [localhost]

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

The JSON artifact is deterministic and reviewable:

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

## What You Learned

- Reports are evidence artifacts.
- JSON/YAML/Markdown outputs serve different reviewers.
- Remediation remains an explicit follow-on workflow.

## Next Page

Continue with [/how-to/generate-operational-evidence.html](../how-to/generate-operational-evidence.html).

{% endraw %}

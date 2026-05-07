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
source_material:
  - ../rewrite-audit.md
last_verified: 2026-05-07
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
ansible-playbook playbooks/report-idm-readiness.yml
```

## Expected Output

```text
{
  "status": "review",
  "idm_reachable": true,
  "inventory_records": 3,
  "remediation_applied": false
}
```

## What You Learned

- Reports are evidence artifacts.
- JSON/YAML/Markdown outputs serve different reviewers.
- Remediation remains an explicit follow-on workflow.

## Next Page

Continue with [/how-to/generate-operational-evidence.html](/how-to/generate-operational-evidence.html).

{% endraw %}

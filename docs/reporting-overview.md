---
layout: default
title: Reporting Overview
description: >-
  Read-only reporting workflows for IdM readiness, certificate inventory,
  keytab rotation candidates, temporary access evidence, and policy drift.
---

{% raw %}

# Reporting Overview

Phase 6 adds read-only reporting roles for operational evidence. The roles
consume explicit records from inventory, Controller surveys, fixture files, or
prior discovery jobs and render deterministic artifacts that are safe to
archive.

The reporting roles do not mutate IdM, AAP, OpenShift, Kubernetes, or adjacent
systems. Any remediation belongs in a separate opt-in workflow.

## Roles

| Role | Purpose |
| --- | --- |
| `idm_readiness_report` | Summarizes IdM automation readiness checks and recommendations. |
| `certificate_inventory_report` | Captures certificate metadata for renewal and lifecycle review. |
| `keytab_rotation_candidates` | Identifies principals that should be reviewed for keytab rotation without exposing keytab bytes. |
| `temporary_access_report` | Records temporary access windows, status, controls, and evidence. |
| `policy_drift_report` | Compares expected and observed policy records and reports drift findings. |

## Output Formats

Every role supports:

- JSON for automation and scheduled comparison
- YAML for peer review
- Markdown for operator handoff

Each report includes:

- `schema`
- `schema_version`
- `role`
- `generated_at_utc`
- `site`
- `context`
- `read_only`
- `summary`
- role-specific record arrays

Use a fixed `*_generated_at_utc` value in CI when byte-for-byte deterministic
fixtures matter. Use an explicit timestamp from the surrounding job when the
report is archival evidence from a real run.

## Safety Boundary

Reports must not include:

- private keys
- passwords
- API tokens
- keytab bytes
- Kubernetes Secret payloads
- IdM vault payload values

For remediation, schedule a separate playbook that reads the report and then
applies an explicitly approved change plan.

{% endraw %}

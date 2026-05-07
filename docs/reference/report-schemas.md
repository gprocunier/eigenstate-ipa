---
layout: default
title: Report schemas reference
diataxis: reference
diataxis_type: reference
audience: Operators and maintainers looking up exact facts
outcome: Exact source-verified reference for this Ansible collection surface.
authority_boundary:
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
source_material:
  - ../../scripts/validate-collection.sh
last_verified: 2026-05-07
---

# Report schemas reference

Report artifact formats and schema expectations.

## Facts

- Report roles render JSON, YAML, and Markdown where templates exist.
- Reports are evidence artifacts; they do not enforce remediation.
- Report inputs should be explicit records from inventory, lookups, modules, or role variables.

## Related Pages

- [Reference index](./)
- [Authority boundaries](../explanation/authority-boundaries.html)

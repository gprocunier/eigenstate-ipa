---
layout: default
title: Execution environment reference
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

# Execution environment reference

AAP execution environment scaffold files and dependencies.

## Facts

- `execution-environment.yml` defines the build scaffold.
- `requirements.yml` defines collection dependencies.
- `python-requirements.txt` carries Python runtime requirements.
- `bindep.txt` carries system package requirements.
- `ansible.cfg.example` documents local config expectations.

## Related Pages

- [Reference index](/reference/)
- [Authority boundaries](/explanation/authority-boundaries.html)

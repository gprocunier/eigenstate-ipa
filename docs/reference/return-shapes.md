---
layout: default
title: Return shapes reference
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

# Return shapes reference

Common lookup return shapes used across the collection.

## Facts

- `value` returns the direct value for simple lookup use.
- `record` returns one structured record per term.
- `map` returns a mapping keyed by input term.
- `map_record` returns structured records keyed by input term.
- Secret-bearing values must be handled with `no_log: true` and redacted artifacts.

## Related Pages

- [Reference index](/reference/)
- [Authority boundaries](/explanation/authority-boundaries.html)

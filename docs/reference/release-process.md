---
layout: default
title: Release process
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

# Release process

Release validation and publication gates.

## Facts

- Run repository validation before release.
- Verify docs language, docs examples, plugin documentation parsing, syntax checks, unit tests, and collection build hygiene.
- Do not publish transient rewrite or local-only behavior as release behavior.

## Related Pages

- [Reference index](/reference/)
- [Authority boundaries](/explanation/authority-boundaries.html)

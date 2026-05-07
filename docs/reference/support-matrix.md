---
layout: default
title: Support matrix
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

# Support matrix

Version and platform support boundaries.

## Facts

- The collection metadata declares `requires_ansible: >=2.15.0`.
- RHEL 9 compatibility is intentional in repository validation.
- IdM and FreeIPA support depends on available IdM client libraries and APIs.
- See legacy `docs/support-matrix.md` until this reference is expanded from release metadata.

## Related Pages

- [Reference index](/reference/)
- [Authority boundaries](/explanation/authority-boundaries.html)

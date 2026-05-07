---
layout: default
title: Authentication reference
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

# Authentication reference

Kerberos, password, keytab, ipalib, ipa-getkeytab, and execution-environment dependencies.

## Facts

- IdM JSON-RPC inventory can use password authentication or Kerberos with an optional keytab.
- ipalib-backed lookups and modules require IdM client Python libraries on the control node or execution environment.
- Keytab lookup and keytab management use platform tooling that provides `ipa-getkeytab`.
- AAP use should package these dependencies into a controlled execution environment.

## Related Pages

- [Reference index](/reference/)
- [Authority boundaries](/explanation/authority-boundaries.html)

---
layout: default
title: Test strategy
diataxis: reference
diataxis_type: reference
audience: Maintainers validating collection changes
outcome: Exact validation lanes and publish gates for this collection.
authority_boundary:
  - collection
workflow_boundary: read-only
evidence_shape:
  - validation-evidence
public_status: rewritten
source_material:
  - ../../scripts/validate-collection.sh
last_verified: 2026-05-07
---

# Test strategy

The collection uses a layered validation path. Fast checks protect local edits,
collection sanity checks protect Ansible compatibility, and release checks
protect the published artifact.

## Required Local Gate

Run the collection validator before publishing:

```bash
./scripts/validate-collection.sh
```

The validator checks:

- support metadata in `meta/runtime.yml`
- YAML parsing and yamllint where available
- Python syntax for plugins and tests
- ansible-lint where available
- selected `ansible-test sanity` checks where available
- plugin documentation parsing through `ansible-doc`
- public documentation language
- documentation examples
- execution-environment scaffold rendering
- wrapper playbook syntax where `ansible-playbook` is available

## Fixture Boundary

Unit and static tests must not require a live IdM server. Live IdM, AAP, or
OpenShift behavior belongs in explicit integration lanes with documented
credentials, inventory, and environment assumptions.

## Publish Gate

Before a GitHub push, release, or tag, review the diff for transient local
workarounds and rerun-only behavior. Published changes must make sense for the
fresh deployment path, not only for a partially converged local workspace.

## Related Pages

- [Support matrix](support-matrix.html)
- [Release process](release-process.html)

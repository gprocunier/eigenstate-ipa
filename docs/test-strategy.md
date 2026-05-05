---
layout: default
title: Test Strategy
description: >-
  Release validation strategy for fast CI, optional integration tests,
  documentation checks, and lab validation.
---

{% raw %}

# Test Strategy

Current release: `1.16.0`

The project separates fast, repeatable checks from live-environment checks. Fast
CI must pass before release publication. Integration and lab tests add evidence
for live IdM behavior without making every pull request depend on a privileged
service container or private lab.

## Fast CI

`.github/workflows/ci.yml` runs `scripts/validate-collection.sh` across
ansible-core `2.15`, `2.16`, `2.17`, and `2.18` on Python `3.11`.

The validation script checks:

- YAML parsing and `yamllint`
- Python syntax for plugins and unit tests
- blocking `ansible-lint` for collection metadata
- `ansible-test sanity` when the CI Python is available
- plugin documentation parsing with `ansible-doc`
- documentation language hygiene
- Markdown YAML example parsing and playbook syntax where feasible
- execution-environment scaffold rendering
- packaged workflow playbook syntax and static validation
- unit tests for the plugin and role families
- collection artifact buildability

## Integration Profile

`.github/workflows/integration.yml` is intentionally separate. It starts a
FreeIPA container, seeds test data, and runs the integration playbooks against
the live service. It is path-scoped and manually dispatchable because it needs
privileged containers and takes materially longer than fast CI.

The workflow defaults to ansible-core `2.18`, with a manual dispatch input for
testing another minor line when a compatibility question needs direct evidence.

## Lab Validation

Private on-prem validation should run from the documented lab execution
boundary: the workstation stages source, the jump host reaches the bastion, and
the bastion runs live IdM playbooks against the lab. Public release notes should
describe the validated behavior, not the private lab names or access details.

## Release Gate

The release workflow repeats the fast CI matrix before building the collection
artifact. It then checks that the Git tag matches `galaxy.yml`, builds the
artifact, records a SHA256 checksum, inspects required files, installs the
artifact into a clean collection path, and smoke-tests selected documentation
with `ansible-doc`.

{% endraw %}

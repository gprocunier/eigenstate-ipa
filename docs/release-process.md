---
layout: default
title: Release Process
description: >-
  Release engineering process for version hygiene, CI gates, artifact checks,
  GitHub releases, and Ansible Galaxy publication.
---

{% raw %}

# Release Process

Current release: `1.16.0`

The release process is designed around a clean deployment path. Temporary
migration helpers, lab-only assumptions, or rerun-only fixes should be removed
or clearly documented before a tag is cut.

## Version Hygiene

Update all public version references before tagging:

- `galaxy.yml`
- `CITATION.cff`
- `CHANGELOG.md`
- `README.md`
- `docs/index.md`
- `docs/documentation-map.md`
- `docs/support-matrix.md`
- `docs/test-strategy.md`
- `docs/release-process.md`
- `llms.txt`
- `roles/aap_execution_environment/defaults/main.yml`
- `roles/aap_execution_environment/README.md`

## Required Checks

Before pushing a release tag:

1. Run the standard validation script.
2. Confirm documentation language hygiene passes.
3. Confirm the execution-environment scaffold renders.
4. Build the collection artifact locally.
5. Install the built artifact into a clean collection path and run `ansible-doc`
   against representative plugin families.
6. Validate the feature set in the on-prem lab when the release changes live
   IdM behavior or operational workflows.

## Tag And Release

Tags use the form `vX.Y.Z`. The GitHub release workflow blocks if the tag does
not match the collection version in `galaxy.yml`. The workflow publishes the
collection tarball and a `SHA256SUMS` file to the GitHub release.

## Galaxy Publication

After the release artifact has passed the local and CI gates, publish the same
version to Ansible Galaxy. Then verify a clean install by installing
`eigenstate.ipa:<version>` into a temporary collection path and running
`ansible-doc` against representative inventory, lookup, and module plugins.

{% endraw %}

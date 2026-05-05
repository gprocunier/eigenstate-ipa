---
layout: default
title: Support Matrix
description: >-
  Tested ansible-core, Python, IdM, and execution-environment boundaries for
  eigenstate.ipa releases.
---

{% raw %}

# Support Matrix

Current release: `1.16.0`

`meta/runtime.yml` declares `requires_ansible: ">=2.15.0"`. Each release gates
the collection against the supported lower bound and the current tested minor
lines listed below.

| Component | Release-gated coverage | Notes |
| --- | --- | --- |
| ansible-core | `2.15`, `2.16`, `2.17`, `2.18` | Fast CI and release validation run on every listed minor line. |
| Python | `3.11` | CI uses Python 3.11 so `ansible-test sanity --python 3.11` is available. |
| IdM / FreeIPA | FreeIPA-compatible JSON-RPC and platform client tools | Live behavior depends on the server features enabled in the target realm. |
| Controller / AAP | Rendered EE scaffold and playbook syntax | Image build, push, and Controller registration remain environment-specific. |
| Kubernetes / OpenShift | Render-first manifests and local validation artifacts | Applying rendered manifests is outside default CI and requires site controls. |

## Compatibility Statement

The `>=2.15.0` runtime lower bound means the collection is intended to load on
ansible-core 2.15 and newer 2.x releases. The release gate proves 2.15 through
2.18 at publication time. Newer ansible-core releases should be treated as
compatible only after the same validation path has been run locally or in CI.

## Known Limits

- Integration tests that require a FreeIPA server are separate from default
  fast CI and run in the optional integration workflow.
- The execution-environment scaffold is validated by render and syntax checks;
  building or pushing an image requires container tooling and registry access.
- Workflows that contact IdM, OpenShift, Keycloak, Controller, or registries
  need operator-provided credentials and are not run in the public fast path.

{% endraw %}

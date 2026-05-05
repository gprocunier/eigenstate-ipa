---
layout: default
title: OpenShift Identity Validation Walkthrough
description: >-
  Render-only and validation-only walkthrough for OpenShift OIDC, Keycloak
  federation, IdM group evidence, and readiness reporting.
---

{% raw %}

# OpenShift Identity Validation Walkthrough

This walkthrough validates the identity design without requiring a live
OpenShift cluster, Keycloak realm, or IdM server. It uses local variables as
evidence and renders reviewable artifacts.

## Static Validation

Run the full Phase 4 static validation path:

```bash
ansible-playbook playbooks/phase4-static-validation.yml
```

The playbook imports all three validation roles and renders local reports under
`build/phase4-static` by default.

## Render OpenShift OIDC Config

```bash
ansible-playbook playbooks/render-openshift-oidc-config.yml \
  -e eigenstate_oidc_output_dir=./artifacts/openshift-identity
```

The rendered OAuth document references an existing OpenShift Secret by name. It
does not contain the client secret value.

## Validate IdM Groups For OpenShift

```bash
ansible-playbook playbooks/validate-openshift-idm-groups.yml \
  -e eigenstate_oidc_expected_groups='["ocp-platform-admins","ocp-developers"]' \
  -e eigenstate_oidc_idm_known_groups='["ocp-platform-admins","ocp-developers"]'
```

Use this when the evidence source is a reviewed inventory file, a read-only
export, or a prior AAP job. Missing groups fail the job by default.

## Validate Keycloak Claims

```bash
ansible-playbook playbooks/validate-keycloak-idm-claims.yml \
  -e eigenstate_keycloak_realm=openshift \
  -e eigenstate_keycloak_group_claim=groups
```

This checks that expected federation mappers and OIDC protocol mappers are
represented in the local evidence variables.

## Expected Result

A passing run proves that the declared identity model is internally coherent:

- expected IdM groups are represented in the evidence
- expected Keycloak mapper names are represented in the evidence
- expected OIDC claim names match the OpenShift OAuth render path
- expected RBAC bindings reference groups rather than individual users

It does not prove that a live cluster has been changed. That is intentional.

{% endraw %}

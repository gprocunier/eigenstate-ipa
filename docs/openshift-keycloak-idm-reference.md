---
layout: default
title: OpenShift Keycloak IdM Reference
description: >-
  Reference model for validating OpenShift OIDC identity with Keycloak
  federation and IdM-backed groups.
---

{% raw %}

# OpenShift, Keycloak, and IdM Reference

The preferred identity path for this collection is:

1. IdM or AD remains the source of users, groups, Kerberos policy, and access
   review evidence.
2. Keycloak federates that identity source and handles OIDC claim shaping.
3. OpenShift consumes OIDC identity and group claims through the cluster OAuth
   configuration.
4. OpenShift RBAC binds groups, not individual emergency users, to platform
   privileges.
5. AAP runs render-only or validation-only jobs that produce repeatable
   evidence before a site operator applies any cluster-side change.

This keeps direct cluster mutation outside the default workflow. The collection
renders configuration examples and readiness reports from supplied variables;
it does not store client secrets, kubeconfigs, Kerberos keys, or IdM
credentials.

## Responsibility Boundary

| Layer | Responsibility | Validation focus |
| --- | --- | --- |
| IdM / AD | group membership, principals, Kerberos policy | expected groups and principals exist |
| Keycloak | federation, Kerberos/SPNEGO, claim mapping | LDAP mappers and OIDC protocol mappers match the design |
| OpenShift OAuth | OIDC provider configuration | issuer, client id, claim names, and secret reference are coherent |
| OpenShift RBAC | authorization after authentication | group-based bindings exist in the intended model |
| Breakglass | emergency access path | named group, review process, and audited binding are documented |

## Roles

| Role | Purpose | Default behavior |
| --- | --- | --- |
| `openshift_idm_oidc_validation` | Render OpenShift OAuth/OIDC configuration and validate local IdM group evidence | render and report only |
| `keycloak_idm_federation_validation` | Validate local evidence for Keycloak federation and OIDC claim mappers | report only |
| `openshift_breakglass_validation` | Validate local evidence for emergency-access groups, principals, controls, and RBAC bindings | report only |

## Output Artifacts

The default roles write only local artifacts under `./artifacts`:

- OpenShift OAuth/OIDC YAML example
- JSON readiness reports
- Markdown readiness reports

Those artifacts are intended for review, pull requests, approvals, and
change-control records. Applying configuration to a live cluster remains a
separate operator action.

{% endraw %}

---
layout: default
title: OpenShift LDAP Fallback
description: >-
  Safe fallback guidance for direct OpenShift LDAP integration when OIDC through
  Keycloak is not available.
---

{% raw %}

# OpenShift LDAP Fallback

Direct OpenShift LDAP integration is a fallback path, not the preferred model
for this collection. Prefer Keycloak federation with OIDC group claims when the
site can operate it, because it separates federation, claim shaping, browser
authentication behavior, and cluster RBAC consumption.

Use direct LDAP only when the site has a clear operational reason:

- Keycloak is not available yet.
- OIDC federation is not approved for the environment.
- A migration period requires temporary direct LDAP validation.
- The cluster is isolated and cannot depend on the federation service.

## Fallback Principles

- Bind OpenShift authorization to groups, not individual users.
- Keep bind credentials and CA material out of repository examples.
- Validate group names and RBAC bindings from local evidence before applying
  cluster configuration.
- Treat the fallback as a documented exception with an owner and review date.
- Keep the migration path back to OIDC visible.

## What This Collection Provides

The OpenShift identity roles can still validate local evidence for group names, expected
RBAC bindings, and breakglass controls. They do not render an LDAP OAuth
provider by default because the reference path is OIDC through Keycloak.

If a site later adds LDAP rendering, it should require an explicit opt-in
variable and should render only references to existing OpenShift Secrets, never
secret values.

{% endraw %}

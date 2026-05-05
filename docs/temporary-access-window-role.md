---
layout: default
title: Temporary Access Window Role
description: >-
  Preflight IdM policy and manage user_lease temporary access windows from AAP.
---

{% raw %}

# Temporary Access Window Role

`temporary_access_window` packages `eigenstate.ipa.user_lease` with HBAC, sudo,
and SELinux map preflight checks. The access boundary is enforced in IdM by
principal and optional password expiry attributes.

This is not a Vault-style dynamic secret lease. It is an IdM-native temporary
access control that blocks future authentication after the expiry while still
requiring normal Kerberos ticket-lifetime discipline.

## Preflight

```yaml
eigenstate_taw_state: preflight
eigenstate_taw_username: temp-maintenance
eigenstate_taw_server: idm-01.example.com
eigenstate_taw_hbac_targethost: host01.example.com
```

## Open

```yaml
eigenstate_taw_state: open
eigenstate_taw_principal_expiration: "02:00"
eigenstate_taw_password_expiration_matches_principal: true
eigenstate_taw_require_groups:
  - lease-targets
```

## Expire

```yaml
eigenstate_taw_state: expire
```

## Clear

```yaml
eigenstate_taw_state: clear
eigenstate_taw_password_expiration_matches_principal: false
eigenstate_taw_clear_password_expiration: true
```

Reports include username, state, before/after expiry metadata, and preflight
results. They do not contain passwords or credential payloads.

{% endraw %}

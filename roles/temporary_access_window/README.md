# temporary_access_window

Packages the `eigenstate.ipa.user_lease` module into an AAP-ready workflow that
can preflight IdM policy, open a temporary access window, expire it, clear it,
and render a metadata-only report.

This role does not retrieve passwords or secret payloads. `eigenstate_taw_no_log`
defaults to `false`, but authentication variables remain module/plugin secrets.

## Required Variables

```yaml
eigenstate_taw_username: temp-maintenance
eigenstate_taw_server: idm-01.example.com
```

HBAC preflight is enabled by default:

```yaml
eigenstate_taw_hbac_targethost: host01.example.com
eigenstate_taw_hbac_service: sshd
```

## States

- `preflight`: run enabled policy checks only.
- `open`: call `user_lease` with `state: present`.
- `expire`: call `user_lease` with `state: expired`.
- `clear`: call `user_lease` with `state: cleared`.

## Open Example

```yaml
eigenstate_taw_state: open
eigenstate_taw_principal_expiration: "02:00"
eigenstate_taw_password_expiration_matches_principal: true
eigenstate_taw_require_groups:
  - lease-targets
```

## Clear Example

```yaml
eigenstate_taw_state: clear
eigenstate_taw_password_expiration_matches_principal: false
eigenstate_taw_clear_password_expiration: true
```

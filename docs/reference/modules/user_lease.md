---
layout: default
title: eigenstate.ipa.user_lease module reference
diataxis: reference
diataxis_type: reference
audience: Operators and maintainers looking up exact facts
outcome: Exact source-verified reference for this Ansible collection surface.
authority_boundary:
  - collection
workflow_boundary: mutating
evidence_shape:
  - ansible-doc
public_status: rewritten
source_material:
  - ../../plugins/modules/user_lease.py
last_verified: 2026-05-17
---
{% raw %}

# `eigenstate.ipa.user_lease` module reference

Manage IdM user expiry attributes as lease-like access boundaries

## Synopsis

Manages C(krbPrincipalExpiration) and optionally C(krbPasswordExpiration) on existing FreeIPA/IdM user accounts.

Designed for temporary user-backed automation or delegated temporary operator access where IdM expiry is the primary cutoff and later cleanup is hygiene.

Supports absolute UTC timestamps, generalized-time values, and simple relative C(HH:MM) durations.

Can assert that the target user belongs to one or more governed groups before mutating the expiry attributes.

Supports Ansible check mode.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Authentication follows the options documented for this surface.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `clear_password_expiration` | bool | no | false |  | When C(state=cleared), also remove C(krbPasswordExpiration). Ignored for other states. |
| `ipaadmin_password` | str | no |  |  | Password for the principal. Used to obtain a Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket already exists. |
| `ipaadmin_principal` | str | no | admin |  | Kerberos principal to authenticate as. |
| `kerberos_keytab` | str | no |  |  | Path to a Kerberos keytab file. Takes precedence over C(ipaadmin_password). Required for non-interactive use in AAP Execution Environments. |
| `password_expiration` | raw | no |  |  | Desired C(krbPasswordExpiration) when C(state=present). Uses the same input formats as C(principal_expiration). Leave unset to avoid changing the password-expiry attribute. |
| `password_expiration_matches_principal` | bool | no | true |  | When true, set C(krbPasswordExpiration) to the same effective time as C(krbPrincipalExpiration). Defaults to C(true) because leaving password expiry behind the principal lease is generally unsafe for temporary-access workflows. With C(state=expired), this expires both attributes immediately. Mutually exclusive with an explicit C(password_expiration). |
| `principal_expiration` | raw | no |  |  | Desired lease end for C(krbPrincipalExpiration) when C(state=present). Accepts UTC generalized time C(YYYYmmddHHMMSSZ), ISO 8601 UTC C(YYYY-MM-DDTHH:MM[:SS]Z), C(now), or a relative C(HH:MM) duration. Relative durations are evaluated at runtime and therefore are not stable across repeated runs. |
| `require_groups` | list | no |  |  | Require the target user to be a direct member of all listed IdM groups before mutating the expiry attributes. Useful when the authenticated principal only has delegated write rights for members of a governed group. |
| `server` | str | yes |  |  | FQDN of the IPA server. |
| `state` | str | no | present | present, expired, cleared | C(present) ensures one or both expiry attributes are set. C(expired) sets C(krbPrincipalExpiration) to the current UTC time. C(cleared) removes C(krbPrincipalExpiration) and, when C(clear_password_expiration=true), also removes C(krbPasswordExpiration). |
| `username` | str | yes |  |  | IdM username to modify. |
| `verify` | str | no |  |  | Path to the IPA CA certificate for TLS verification. Auto-detected from C(/etc/ipa/ca.crt) when not set. If neither is available, the module fails unless C(verify) is set to C(false) explicitly. |

## Notes

- Requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible controller.
- RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)
- Setting C(password_expiration_matches_principal=false) leaves the password authentication path outside the lease boundary unless C(password_expiration) is managed separately. That is generally unsafe for temporary-access workflows.
- The authenticated principal needs write access to C(krbPrincipalExpiration) on the target user. Managing C(krbPasswordExpiration) additionally requires write access to that attribute.
- A common delegated model is an IdM permission like: C(ipa permission-add lease-expiry-write --right=write --attrs=krbprincipalexpiration --attrs=krbpasswordexpiration --type=user --memberof=lease-targets) attached to a privilege and role granted to the automation user.
- Expiring a principal blocks future authentication. It does not revoke already-issued Kerberos tickets; short ticket lifetime still matters when a hard cutoff is required.

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `changed` | bool | always | Whether the module made any changes. |
| `groups_checked` | list | always | Groups that were required through C(require_groups). |
| `lease_end` | str | always | Alias for C(principal_expiration_after). |
| `memberof_group` | list | always | Direct group memberships returned by IdM for the target user. |
| `password_expiration_after` | str | always | Final C(krbPasswordExpiration) value in generalized UTC format. |
| `password_expiration_before` | str | always | Prior C(krbPasswordExpiration) value in generalized UTC format. |
| `principal_expiration_after` | str | always | Final C(krbPrincipalExpiration) value in generalized UTC format. |
| `principal_expiration_before` | str | always | Prior C(krbPrincipalExpiration) value in generalized UTC format. |
| `uid` | str | always | Target user login as returned by IdM. |
| `username` | str | always | Target user that was inspected or modified. |

## Examples

```yaml
# Give a temporary user a two-hour lease window
- name: Set a two-hour principal lease
  eigenstate.ipa.user_lease:
    username: temp-deploy
    principal_expiration: "02:00"
    password_expiration_matches_principal: true
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"

# Expire principal and password together for a governed user
- name: End temporary user access now
  eigenstate.ipa.user_lease:
    username: temp-maintenance
    state: expired
    password_expiration_matches_principal: true
    require_groups:
      - lease-targets
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/lease-operator.keytab
    ipaadmin_principal: lease-operator

# Pin an absolute UTC lease end
- name: Set explicit lease end
  eigenstate.ipa.user_lease:
    username: temp-build
    principal_expiration: "2026-04-09T18:30:00Z"
    password_expiration_matches_principal: true
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/lease-operator.keytab
    ipaadmin_principal: lease-operator

# Remove the principal expiry while leaving password expiry alone
- name: Clear temporary principal cutoff
  eigenstate.ipa.user_lease:
    username: temp-build
    state: cleared
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"

# Clear both expiry attributes
- name: Clear all lease state
  eigenstate.ipa.user_lease:
    username: temp-build
    state: cleared
    clear_password_expiration: true
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"
```

## Output Shape

```yaml
- changed: true
  uid: "temp-deploy"
  username: "temp-deploy"
  groups_checked:
    - "lease-targets"
  principal_expiration_before: null
  principal_expiration_after: "2026-05-16T20:00:00Z"
  password_expiration_before: null
  password_expiration_after: "2026-05-16T20:00:00Z"
  lease_end: "2026-05-16T20:00:00Z"
  memberof_group:
    - "ipausers"
    - "lease-targets"
```

## Error Behavior

Module failures return through normal Ansible module failure handling. Use check mode where supported before mutating IdM, keytab, certificate, or filesystem state.

## Related Pages

- [Authentication reference](../authentication.html)
- [Return shapes](../return-shapes.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

{% endraw %}

---
layout: default
title: User Lease Capabilities
---

{% raw %}

# User Lease Capabilities

Related docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-plugin.html"><kbd>&nbsp;&nbsp;USER LEASE PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-use-cases.html"><kbd>&nbsp;&nbsp;USER LEASE USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>&nbsp;&nbsp;EPHEMERAL ACCESS CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

## Purpose

Use this guide to decide whether `eigenstate.ipa.user_lease` is the right
boundary for temporary user-backed access in IdM.

The short answer: use it when the access boundary should be expressed by IdM
user expiry attributes, not by a later cleanup job alone.

## What The Module Is Good At

`user_lease` is strong when all of these are true:

- the identity is already an IdM user
- the access window should end through `krbPrincipalExpiration`
- delegated RBAC should be able to narrow who can set that boundary
- AAP or Ansible is orchestrating the workflow, but IdM owns the actual cutoff

That makes it a good fit for:

- temporary operator access
- temporary user-backed automation identities
- delegated lease management by a non-admin role
- workflows where cleanup is hygiene and expiry is the real control

## What The Module Is Not

This module is not:

- user lifecycle CRUD
- Vault-style dynamic secret issuance
- ticket revocation
- Kerberos ticket policy management
- service-principal or keytab rotation

The machine-identity pattern still belongs to the
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>KEYTAB CAPABILITIES</kbd></a>
side of the collection.

## RBAC Model

The strongest operating model is delegated, not full admin.

A practical pattern on live IdM is:

1. put governed target users in a group such as `lease-targets`
2. create a permission limited to members of that group
3. grant write access to `krbPrincipalExpiration` and, if needed,
   `krbPasswordExpiration`
4. attach that permission to a privilege and role
5. assign the automation user to that role

Representative CLI:

```bash
ipa permission-add lease-expiry-write   --right=write   --attrs=krbprincipalexpiration   --attrs=krbpasswordexpiration   --type=user   --memberof=lease-targets

ipa privilege-add lease-expiry-priv
ipa privilege-add-permission lease-expiry-priv --permissions=lease-expiry-write
ipa role-add lease-expiry-role
ipa role-add-privilege lease-expiry-role --privileges=lease-expiry-priv
ipa role-add-member lease-expiry-role --users=lease-operator
```

That is exactly the shape validated on the lab IdM server for this module.

## Expiry Model

`krbPrincipalExpiration` is the main access boundary.

`krbPasswordExpiration` is secondary and useful when password-based login must
stop on the same timeline. When the workload is password-authenticated rather
than keytab-authenticated, it is reasonable to set both.

The important limit remains:

- existing Kerberos tickets can outlive the later principal expiry until their
  ticket lifetime ends

So the stronger design is:

- principal expiry through `user_lease`
- short Kerberos ticket lifetime where hard cutoffs matter
- cleanup afterward for hygiene

## Time Inputs And Convergence

Use absolute UTC times when you want clean, repeatable convergence.

Use relative `HH:MM` when you want a true lease window starting from the moment
of execution. That is operationally useful, but it is intentionally time-based,
not static desired state.

## Cross-Plugin Fit

High-value combinations:

- `user_lease` + `hbacrule`
  validate that the temporary user is actually allowed onto the target host
- `user_lease` + `sudo`
  confirm the temporary user's privilege surface before the lease is opened
- `user_lease` + `aap-integration`
  let Controller schedule and approve the change while IdM owns the cutoff
- `user_lease` + `otp`
  bootstrap a temporary user workflow that begins with a one-time credential
  and ends with an explicit IdM expiry boundary

## Quick Decision Matrix

| Need | Better fit |
| --- | --- |
| temporary user access with an IdM-owned cutoff | `user_lease` |
| temporary machine identity with Kerberos key retirement | `principal` + `keytab` |
| static password rotation on a schedule | AAP + `vault_write` |
| dynamic leased credentials from the issuer | Vault or another true dynamic secret system |

{% endraw %}

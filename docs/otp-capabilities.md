---
layout: default
title: OTP Capabilities
---

{% raw %}

# OTP Capabilities

Related docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>&nbsp;&nbsp;OTP PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html"><kbd>&nbsp;&nbsp;OTP USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>&nbsp;&nbsp;PRINCIPAL CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

## Purpose

Use this guide to choose the right OTP credential pattern for your automation.

It is the companion to the OTP plugin reference. Use the reference for exact
option syntax; use this guide when you are designing a workflow and need to
know which capability fits your situation.

## Contents

- [Capability Model](#capability-model)
- [Token Type Decision](#token-type-decision)
- [Operation Decision](#operation-decision)
- [1. Provision User TOTP Token](#1-provision-user-totp-token)
- [2. Rotate Existing User Token](#2-rotate-existing-user-token)
- [3. Host Enrollment Credential Delivery](#3-host-enrollment-credential-delivery)
- [4. Bulk Host Enrollment](#4-bulk-host-enrollment)
- [5. Emergency Revoke All Tokens for a User](#5-emergency-revoke-all-tokens-for-a-user)
- [6. Pre-flight Token Existence Check](#6-pre-flight-token-existence-check)
- [7. AAP Credential Type Injection](#7-aap-credential-type-injection)
- [8. Cross-Plugin: Principal Check Before Token Issuance](#8-cross-plugin-principal-check-before-token-issuance)
- [Quick Decision Matrix](#quick-decision-matrix)

## Capability Model

```mermaid
flowchart TD
    q["What do you need?"]

    new_token["New TOTP/HOTP token\nfor a user"]
    enroll_pw["Enrollment password\nfor a host"]
    rotate["Rotate existing token\n(revoke old, add new)"]
    find_tokens["Find tokens\nfor audit or revoke"]
    revoke_all["Revoke all tokens\nfor a user"]
    check["Confirm token exists\nbefore acting"]
    cross["Pre-validate principal\nthen issue token"]

    q --> new_token
    q --> enroll_pw
    q --> rotate
    q --> find_tokens
    q --> revoke_all
    q --> check
    q --> cross

    new_token --> add_totp["add, token_type=totp/hotp"]
    enroll_pw --> add_host["add, token_type=host"]
    rotate --> find_then_add["show → revoke → add"]
    find_tokens --> find_op["find, owner= filter"]
    revoke_all --> bulk_revoke["find → loop revoke"]
    check --> show_op["show — exists=false is not an error"]
    cross --> principal_first["principal show → assert → otp add"]
```

The OTP plugin is a write-capable credential primitive. `add` and `revoke`
change IdM state. `find` and `show` are read-only.

## Token Type Decision

| Type | When to use | IdM object created | URI returned |
| --- | --- | --- | --- |
| `totp` | Standard 2FA for users; works with authenticator apps (Google Authenticator, FreeOTP, etc.) | Yes — persistent token record | Yes — `otpauth://totp/...` |
| `hotp` | Counter-based OTP for hardware tokens or offline use cases | Yes — persistent token record | Yes — `otpauth://hotp/...` |
| `host` | One-time enrollment password for `ipa-client-install` or ansible-freeipa | No — password is ephemeral | No — plain text password |

When in doubt, use `totp`. It is the most widely supported and the default.

Use `hotp` only if the target authenticator does not support TOTP or if the
use case requires counter-based semantics.

Use `host` when automating host enrollment. The password is consumed by
`ipa-client-install` and does not persist in IdM.

## Operation Decision

```mermaid
flowchart TD
    q["What action?"]

    create{"Creating a\nnew credential?"}
    lookup{"Looking up\nexisting state?"}

    q --> create
    q --> lookup

    create --> type_q{"What kind?"}
    type_q -->|"User 2FA"| add_totp["add, token_type=totp or hotp"]
    type_q -->|"Host enrollment"| add_host["add, token_type=host"]

    lookup --> know_id{"Know the\ntoken ID?"}
    know_id -->|yes| show_op["show — returns state or exists=false"]
    know_id -->|no| find_op["find — search, optionally filter by owner"]

    find_op --> need_del{"Need to\ndelete?"}
    need_del -->|yes| revoke_op["revoke — permanent, non-idempotent"]
    need_del -->|no| done["done — use record for audit/display"]
```

## 1. Provision User TOTP Token

Use `operation=add` with `token_type=totp` (default) to create a new 2FA token for
a user. The result is an `otpauth://` URI suitable for QR code generation or
direct import into an authenticator app.

```mermaid
flowchart TD
    add["otp add\ntoken_type=totp\nowner=alice"] --> uri["otpauth:// URI"]
    uri --> qr["QR code generation task\n(optional)"]
    uri --> vault_store["eigenstate.ipa.vault\narchive URI for recovery"]
```

The token is active immediately. The user can add it to any TOTP-compatible
authenticator. IdM will require this token as a second factor on next login
if the user's auth policy requires OTP.

Use `description` to label tokens when a user may have more than one (work
device vs personal device, primary vs backup).

## 2. Rotate Existing User Token

To replace a token without leaving the old one active:

1. Use `show` to confirm the old token ID exists.
2. Use `revoke` to delete it.
3. Use `add` to issue a new one.

```mermaid
flowchart TD
    show["otp show\ntoken_id=old-tok"] --> exists{"exists?"}
    exists -->|no| skip["nothing to revoke"]
    exists -->|yes| revoke["otp revoke\ntoken_id=old-tok"]
    revoke --> add["otp add\ntoken_type=totp\nowner=alice"]
    add --> new_uri["new otpauth:// URI"]
```

Why this order: revoke before add ensures the user cannot authenticate with
both the old and new token simultaneously during the rotation window.

## 3. Host Enrollment Credential Delivery

Use `operation=add`, `token_type=host` to generate a one-time enrollment password
for a host, then pass it to `freeipa.ansible_freeipa.ipaclient`.

```mermaid
flowchart TD
    ipahost["freeipa.ansible_freeipa.ipahost\ncreate host record in IdM"] --> enroll_pw["otp add, token_type=host\nFQDN=web-01.example.com"]
    enroll_pw --> pw["one-time password"]
    pw --> ipaclient["freeipa.ansible_freeipa.ipaclient\nwith ipaadmin_password=pw"]
    ipaclient --> enrolled["host enrolled in IdM"]
```

The host record must already exist in IdM before calling `token_type=host`. The
`ipahost` module creates the record; `otp add token_type=host` then sets the
enrollment password on it.

After `ipaclient` consumes the password, the host is enrolled and the
credential is invalidated. No cleanup is needed.

## 4. Bulk Host Enrollment

Loop `operation=add`, `token_type=host` over an inventory group to generate
enrollment passwords for multiple hosts at once. Pair the result map with
`freeipa.ansible_freeipa.ipaclient` using `delegate_to`.

```mermaid
flowchart TD
    group["inventory group\nnew_hosts"] --> loop["loop: otp add token_type=host\nfor each FQDN"]
    loop --> pw_map["map: fqdn → password"]
    pw_map --> delegate["ipaclient role\ndelegate_to each host\nwith its password"]
    delegate --> enrolled["all hosts enrolled"]
```

Use `result_format=map` to get a `{fqdn: password}` dictionary directly.
The map form avoids positional list indexing when correlating passwords back
to host names.

## 5. Emergency Revoke All Tokens for a User

When a user's authenticator is lost, stolen, or compromised, revoke all their
tokens in one play:

1. `find` with `owner=` filter to enumerate the user's token IDs.
2. Loop `revoke` over the result.

```mermaid
flowchart TD
    find["otp find\nowner=alice"] --> tokens["list of token IDs"]
    tokens --> empty{"any tokens?"}
    empty -->|no| done["nothing to revoke"]
    empty -->|yes| revoke["loop: otp revoke\nfor each token_id"]
    revoke --> clean["all tokens revoked"]
```

After revocation, the user cannot generate valid OTP codes and cannot
authenticate with second-factor requirements until a new token is issued.

## 6. Pre-flight Token Existence Check

Use `operation=show` to check whether a token still exists before rotating
or revoking it. A missing token returns `exists=false` — this is not an
error.

```mermaid
flowchart TD
    show["otp show\ntoken_id=tok-abc"] --> exists{"exists?"}
    exists -->|no| skip["log: token already gone\nno action needed"]
    exists -->|yes| rotate["proceed with rotation"]
```

This pattern is useful in idempotent plays that may run multiple times. The
existence check lets the play skip revocation cleanly when the token was
already removed by an earlier run or by an operator.

## 7. AAP Credential Type Injection

Ansible Automation Platform supports custom credential types with injector
templates. An OTP lookup at job launch time generates a fresh enrollment
credential per-run, injecting it as an extra variable without persisting it
to disk.

```mermaid
flowchart TD
    cred_type["AAP custom credential type\nIPA_SERVER, IPA_KEYTAB fields"] --> launch["job launch"]
    launch --> injector["injector template\nenroll_pass={{ lookup('eigenstate.ipa.otp',\ntarget_fqdn, token_type='host', ...) | first }}"]
    injector --> play["play receives enroll_pass\nas extra var"]
    play --> ipaclient["freeipa.ansible_freeipa.ipaclient\nwith ipaadmin_password=enroll_pass"]
```

The credential type stores the IPA server and keytab path. The injector
template calls the OTP lookup at runtime. The enrollment password is never
stored in AAP's credential vault.

## 8. Cross-Plugin: Principal Check Before Token Issuance

Combine `eigenstate.ipa.principal` and `eigenstate.ipa.otp` when issuing a
token for a host or user that may not yet be registered in IdM.

```mermaid
flowchart TD
    principal["principal show\nuser or host principal"] --> exists{"exists in IdM?"}
    exists -->|no| fail["fail — principal not enrolled\nno token to issue"]
    exists -->|yes| otp["otp add\nissue token or enrollment password"]
    otp --> deliver["deliver credential\nto user or enrollment job"]
```

This pattern prevents issuing a token for a username or hostname that IdM
does not have a record for. Without the pre-flight check, `otp add` would
raise a `NotFound` error from ipalib; the principal check produces a cleaner
message earlier.

## Quick Decision Matrix

| Need | Best capability |
| --- | --- |
| Issue a TOTP token for a new user | Provision user TOTP token (#1) |
| Replace a user's compromised or lost token | Rotate existing user token (#2) |
| Automate joining a new host to IdM | Host enrollment credential delivery (#3) |
| Enroll a batch of new hosts | Bulk host enrollment (#4) |
| Revoke all tokens for a user immediately | Emergency revoke all tokens (#5) |
| Check token status before acting | Pre-flight token existence check (#6) |
| Generate enrollment credentials at AAP job launch | AAP credential type injection (#7) |
| Confirm user/host exists before issuing token | Cross-plugin: principal + OTP (#8) |

For option-level behavior, field definitions, and exact lookup syntax, return
to
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>OTP PLUGIN</kbd></a>.

{% endraw %}

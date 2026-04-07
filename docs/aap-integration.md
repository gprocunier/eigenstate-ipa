---
layout: default
title: AAP Integration
---

{% raw %}

# AAP Integration

Related docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>&nbsp;&nbsp;INVENTORY PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>&nbsp;&nbsp;IDM VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html"><kbd>&nbsp;&nbsp;PRINCIPAL PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>&nbsp;&nbsp;KEYTAB PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>&nbsp;&nbsp;IDM CERT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>&nbsp;&nbsp;OTP PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>&nbsp;&nbsp;ROTATION CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

## Purpose

This page describes how to run `eigenstate.ipa` inside Ansible Automation
Platform / Automation Controller.

It covers:

- what must exist in the execution environment
- how to authenticate non-interactively
- how to wire the inventory plugin and the lookup plugins into controller objects

## Contents

- [Controller Integration Model](#controller-integration-model)
- [Execution Environment Requirements](#execution-environment-requirements)
- [Authentication Guidance](#authentication-guidance)
- [Inventory Source Pattern](#inventory-source-pattern)
- [IdM Vault Lookup Pattern](#idm-vault-lookup-pattern)
- [Credential-Source Pattern](#credential-source-pattern)
- [Operational Guardrails](#operational-guardrails)

## Controller Integration Model

```mermaid
flowchart TD
    ctrl["Controller job"]
    cred["Password or keytab credential"]
    ee["Execution environment"]
    inv["idm inventory"]
    vault["vault lookup"]
    principal["principal lookup"]
    keytab["keytab lookup"]
    cert["cert lookup"]
    otp["otp lookup"]
    idm["IdM / FreeIPA"]

    ctrl --> ee
    cred --> ee
    ee --> inv
    ee --> vault
    ee --> principal
    ee --> keytab
    ee --> cert
    ee --> otp
    inv --> idm
    vault --> idm
    principal --> idm
    keytab --> idm
    cert --> idm
    otp --> idm
```

## Execution Environment Requirements

The current collection code implies two dependency sets.

For the inventory plugin:

- `python3-requests`
- either `python3-requests-gssapi` or `python3-requests-kerberos` for Kerberos
  mode
- `python3-gssapi`
- `krb5-workstation` when keytab-driven `kinit` is needed

For the IdM vault lookup:

- `python3-ipalib`
- `python3-ipaclient`
- `krb5-workstation` when password-driven or keytab-driven ticket acquisition is
  needed

> [!IMPORTANT]
> The IdM vault lookup is not just a pure Python helper. If the EE does not
> contain
> the IdM client libraries, vault retrieval will fail even if network access and
> credentials are otherwise correct.

For the principal-state lookup:

- `python3-ipalib`
- `python3-ipaclient`
- `krb5-workstation` when password-driven or keytab-driven ticket acquisition is
  needed

> [!NOTE]
> The principal lookup is read-only but still depends on the same IdM client
> Python stack as the vault and cert lookups.

For the Kerberos keytab lookup:

- on RHEL 10, `ipa-client` (provides the `ipa-getkeytab` binary there)
- on other EE bases, the package that provides `ipa-getkeytab`
- `krb5-workstation` when password-driven or keytab-driven ticket acquisition is
  needed

> [!NOTE]
> The keytab lookup does not require `python3-ipalib` or `python3-ipaclient`.
> It shells out to `ipa-getkeytab` directly. If that binary is not installed,
> the lookup fails immediately with a release-aware install hint.

For the IdM certificate lookup:

- `python3-ipalib`
- `python3-ipaclient`
- `krb5-workstation` when password-driven or keytab-driven ticket acquisition is
  needed

> [!NOTE]
> The cert lookup talks to the IdM CA through `ipalib` and does not require
> `certmonger` in the EE. It does require the IdM client Python libraries to be
> present, like the vault lookup.

For the OTP lookup:

- `python3-ipalib`
- `python3-ipaclient`
- `krb5-workstation` when password-driven or keytab-driven ticket acquisition is
  needed

> [!NOTE]
> The OTP lookup uses `ipalib` to create, inspect, and revoke OTP tokens and to
> generate one-time host enrollment passwords. Treat returned OTP URIs and host
> enrollment passwords as secret material in controller logs and credentials.

## Authentication Guidance

For controller use, prefer Kerberos with a keytab over plaintext password auth.

Why:

- no interactive `kinit`
- cleaner non-interactive execution
- consistent behavior for both inventory syncs and job runs

Recommended pattern:

- store the keytab as a controller credential-managed file
- inject it into the EE at runtime
- point `kerberos_keytab` at that mounted path
- provide `verify` with the IdM CA path

Password auth still works for the inventory plugin and for the IdM lookup
plugins' ticket acquisition path, but it is the weaker controller posture.

## Inventory Source Pattern

Example controller inventory source content:

```yaml
plugin: eigenstate.ipa.idm
server: idm-01.corp.example.com
use_kerberos: true
kerberos_keytab: /runner/env/ipa/admin.keytab
ipaadmin_principal: admin
verify: /runner/env/ipa/ca.crt
sources:
  - hosts
  - hostgroups
hostgroup_filter:
  - webservers
  - databases
host_filter_from_groups: true
compose:
  ansible_host: idm_fqdn
```

## IdM Vault Lookup Pattern

Example task usage from a controller job template:

```yaml
- name: Retrieve a shared secret from IdM vault
  ansible.builtin.set_fact:
    db_password: "{{ lookup('eigenstate.ipa.vault',
                     'database-password',
                     server='idm-01.corp.example.com',
                     kerberos_keytab='/runner/env/ipa/admin.keytab',
                     shared=true,
                     verify='/runner/env/ipa/ca.crt') }}"
```

## Credential-Source Pattern

One AAP pattern is to use the IdM vault lookup inside a custom credential type
injector or job vars resolution path.

That works well when:

- a controller-managed job needs a secret only at runtime
- the secret should remain in IdM rather than being copied into controller
  storage
- the same secret should resolve differently by scope or by rotated value over
  time

## Operational Guardrails

- keep the IdM CA available inside the EE and set `verify`
- prefer keytab auth for repeatable non-interactive jobs
- use `encoding='base64'` for keytabs or binary bundles
- keep vault ownership scope explicit when ambiguity is possible

> [!NOTE]
> If an inventory sync works but IdM vault lookups fail inside the same EE, suspect
> missing `ipalib`/`ipaclient` content first. The two plugins do not share the
> same client dependency stack.

{% endraw %}

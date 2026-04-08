# eigenstate.ipa

**An Ansible collection for Red Hat IdM / FreeIPA with dynamic inventory, IdM vault retrieval and lifecycle automation, Kerberos principal state, keytab delivery, certificate automation, OTP workflows, DNS record inspection, sudo policy inspection, SELinux user map inspection, and HBAC rule inspection and access testing.**

[![License: GPL-3.0](https://img.shields.io/github/license/gprocunier/eigenstate-ipa)](COPYING)
![Ansible 2.14+](https://img.shields.io/badge/Ansible-2.14%2B-blue)
![FreeIPA 4.6+](https://img.shields.io/badge/FreeIPA-4.6%2B-blue)
![RHEL](https://img.shields.io/badge/RHEL-9%20%7C%2010-red)

<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>&nbsp;&nbsp;INVENTORY PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>&nbsp;&nbsp;IDM VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html"><kbd>&nbsp;&nbsp;VAULT WRITE MODULE&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html"><kbd>&nbsp;&nbsp;PRINCIPAL PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>&nbsp;&nbsp;KEYTAB PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>&nbsp;&nbsp;IDM CERT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>&nbsp;&nbsp;OTP PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/dns-plugin.html"><kbd>&nbsp;&nbsp;DNS PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-plugin.html"><kbd>&nbsp;&nbsp;SELINUX MAP PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/sudo-plugin.html"><kbd>&nbsp;&nbsp;SUDO PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-plugin.html"><kbd>&nbsp;&nbsp;HBAC RULE PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>&nbsp;&nbsp;INVENTORY CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>&nbsp;&nbsp;IDM VAULT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html"><kbd>&nbsp;&nbsp;VAULT WRITE CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>&nbsp;&nbsp;PRINCIPAL CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>&nbsp;&nbsp;KEYTAB CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>&nbsp;&nbsp;IDM CERT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html"><kbd>&nbsp;&nbsp;OTP CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/dns-capabilities.html"><kbd>&nbsp;&nbsp;DNS CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-capabilities.html"><kbd>&nbsp;&nbsp;SELINUX MAP CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/sudo-capabilities.html"><kbd>&nbsp;&nbsp;SUDO CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-capabilities.html"><kbd>&nbsp;&nbsp;HBAC RULE CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>&nbsp;&nbsp;ROTATION CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>&nbsp;&nbsp;INVENTORY USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>&nbsp;&nbsp;IDM VAULT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-use-cases.html"><kbd>&nbsp;&nbsp;VAULT WRITE USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>&nbsp;&nbsp;PRINCIPAL USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>&nbsp;&nbsp;KEYTAB USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>&nbsp;&nbsp;IDM CERT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html"><kbd>&nbsp;&nbsp;OTP USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/dns-use-cases.html"><kbd>&nbsp;&nbsp;DNS USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-use-cases.html"><kbd>&nbsp;&nbsp;SELINUX MAP USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/sudo-use-cases.html"><kbd>&nbsp;&nbsp;SUDO USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html"><kbd>&nbsp;&nbsp;HBAC RULE USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>&nbsp;&nbsp;ROTATION USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>&nbsp;&nbsp;VAULT/CYBERARK PRIMER&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/"><kbd>&nbsp;&nbsp;WEBSITE&nbsp;&nbsp;</kbd></a>

---

`eigenstate` is a nod to the quantum-mechanical idea of a stable observable
state. In practice, the collection assumes IdM already knows what the estate
looks like and what secrets it should hand out. The Ansible side should consume
that state directly instead of maintaining a parallel copy in static inventory
files and side-channel secret stores.

The GitHub repository name is `eigenstate-ipa`; the Ansible collection name is
`eigenstate.ipa`.

## Contents

- [Why This Collection Exists](#why-this-collection-exists)
- [What The Collection Contains](#what-the-collection-contains)
- [Start Here](#start-here)
- [Quick Install](#quick-install)
- [For Vault Or CyberArk Users](#for-vault-or-cyberark-users)
- [Repository Layout](#repository-layout)
- [Author](#author)
- [License](#license)

## Why This Collection Exists

Ansible already has strong support for managing IdM objects. The missing piece
has been consuming IdM as an input system:

- dynamic inventory from enrolled IdM hosts, hostgroups, netgroups, and HBAC
  policy
- secret retrieval from IdM vaults without copying those values into Git or
  inventory vars

Without those two paths, operators usually end up with:

- static inventory that drifts from the enrollment reality
- policy data duplicated outside the identity platform
- credentials copied into other stores because automation cannot read IdM vaults
- keytabs staged by hand outside the automation lifecycle
- certificate requests handled in separate CA workflows outside the automation lifecycle

This collection closes that gap with one inventory plugin, nine lookup plugins,
and one vault lifecycle module.

## What The Collection Contains

At a high level:

- `eigenstate.ipa.idm` reads IdM hosts, hostgroups, netgroups, and HBAC rules
  and turns them into Ansible inventory
- `eigenstate.ipa.vault` uses `ipalib` to retrieve, inspect, and search IdM
  vault content for playbooks and AAP jobs
- `eigenstate.ipa.vault_write` uses `ipalib` to create, archive, modify, and
  delete IdM vaults from Ansible
- `eigenstate.ipa.principal` uses `ipalib` to query Kerberos principal state
  before enrollment, keytab, or certificate workflows proceed
- `eigenstate.ipa.keytab` uses `ipa-getkeytab` to retrieve Kerberos keytab
  files for service and host principals, returning base64-encoded content ready
  to write to disk or inject into an AAP credential type
- `eigenstate.ipa.cert` uses `ipalib` to request, retrieve, and search IdM CA
  certificates for host and service principals via the Dogtag backend
- `eigenstate.ipa.otp` uses `ipalib` to issue OTP tokens for users and
  one-time host enrollment passwords for IdM-managed onboarding flows
- `eigenstate.ipa.dns` uses `ipalib` to read integrated IdM DNS records for
  forward, reverse, zone-apex, and broad zone validation workflows
- `eigenstate.ipa.selinuxmap` uses `ipalib` to read SELinux user map state from
  IdM, returning the assigned SELinux user string, enabled state, and the linked
  HBAC rule name when HBAC-linked scope is configured
- `eigenstate.ipa.sudo` uses `ipalib` to read sudo rules, sudo commands, and
  sudo command groups for pre-flight checks and policy audit
- `eigenstate.ipa.hbacrule` uses `ipalib` to read HBAC rule state and to invoke
  the FreeIPA `hbactest` engine for live access simulation

| Plugin | Type | FQCN | Purpose |
| --- | --- | --- | --- |
| IdM inventory | inventory | `eigenstate.ipa.idm` | Builds live inventory from IdM-enrolled hosts and policy-backed group relationships |
| IdM vault | lookup | `eigenstate.ipa.vault` | Retrieves vault payloads, inspects metadata, and searches vault scopes in IdM |
| IdM vault lifecycle | module | `eigenstate.ipa.vault_write` | Creates, archives, updates, and deletes IdM vaults with check-mode and member-management support |
| Kerberos principal state | lookup | `eigenstate.ipa.principal` | Reads user, host, and service principal existence, key, lock, and last-auth state from IdM |
| Kerberos keytab | lookup | `eigenstate.ipa.keytab` | Retrieves Kerberos keytab files for service and host principals via `ipa-getkeytab` |
| IdM certificates | lookup | `eigenstate.ipa.cert` | Requests, retrieves, and searches IdM CA certificates for host and service principals |
| OTP and enrollment credentials | lookup | `eigenstate.ipa.otp` | Issues user OTP tokens and one-time host enrollment passwords through IdM |
| DNS record state | lookup | `eigenstate.ipa.dns` | Reads forward, reverse, zone-apex, and broad-search DNS records from IdM |
| SELinux user map state | lookup | `eigenstate.ipa.selinuxmap` | Reads SELinux user map configuration and HBAC-linked scope from IdM |
| Sudo policy state | lookup | `eigenstate.ipa.sudo` | Reads sudo rules, sudo commands, and sudo command groups from IdM |
| HBAC rule state and access test | lookup | `eigenstate.ipa.hbacrule` | Reads HBAC rule configuration and runs live access tests via the FreeIPA hbactest engine |

## Start Here

If you want the project map and reading order, open
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>DOCS MAP</kbd></a>.

If you are deciding whether the collection fits your use case, start with:

- <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>INVENTORY CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>IDM VAULT CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html"><kbd>VAULT WRITE CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>PRINCIPAL CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>KEYTAB CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>IDM CERT CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html"><kbd>OTP CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/dns-capabilities.html"><kbd>DNS CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-capabilities.html"><kbd>SELINUX MAP CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/sudo-capabilities.html"><kbd>SUDO CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-capabilities.html"><kbd>HBAC RULE CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>ROTATION CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>INVENTORY USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>IDM VAULT USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-use-cases.html"><kbd>VAULT WRITE USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>PRINCIPAL USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>KEYTAB USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>IDM CERT USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html"><kbd>OTP USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/dns-use-cases.html"><kbd>DNS USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-use-cases.html"><kbd>SELINUX MAP USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/sudo-use-cases.html"><kbd>SUDO USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html"><kbd>HBAC RULE USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>ROTATION USE CASES</kbd></a>

## For Vault Or CyberArk Users

If you are evaluating the collection from a HashiCorp Vault or CyberArk point
of view, start with
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>VAULT/CYBERARK PRIMER</kbd></a>.

Then read the collection-wide guides in this order:

- <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>ROTATION CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>ROTATION USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

That keeps the primer as the single comparison entry point and moves the rest
of the flow into the collection-wide execution and rotation guidance.

If you are wiring the plugins into actual automation, start with:

- <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>INVENTORY PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>IDM VAULT PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html"><kbd>VAULT WRITE MODULE</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/principal-plugin.html"><kbd>PRINCIPAL PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>KEYTAB PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>IDM CERT PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>OTP PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-plugin.html"><kbd>SELINUX MAP PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/sudo-plugin.html"><kbd>SUDO PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-plugin.html"><kbd>HBAC RULE PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>ROTATION CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>ROTATION USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

## Quick Install

```bash
ansible-galaxy collection install eigenstate-ipa-1.9.0.tar.gz
```

Verify:

```bash
ansible-doc -t inventory eigenstate.ipa.idm
ansible-doc -t lookup eigenstate.ipa.vault
ansible-doc -t module eigenstate.ipa.vault_write
ansible-doc -t lookup eigenstate.ipa.principal
ansible-doc -t lookup eigenstate.ipa.keytab
ansible-doc -t lookup eigenstate.ipa.cert
ansible-doc -t lookup eigenstate.ipa.otp
ansible-doc -t lookup eigenstate.ipa.dns
ansible-doc -t lookup eigenstate.ipa.selinuxmap
ansible-doc -t lookup eigenstate.ipa.sudo
ansible-doc -t lookup eigenstate.ipa.hbacrule
```

> [!NOTE]
> The inventory plugin talks to the IdM JSON-RPC API and can use either
> password authentication or Kerberos with an optional keytab. The vault
> lookup, vault write, principal, cert, OTP, and DNS components use `ipalib` and
> therefore depend on the local IdM client Python libraries being available on
> the control node or execution environment. The keytab
> plugin shells out to `ipa-getkeytab` and does not require `ipalib`; on RHEL
> 10 install `ipa-client`, and on other releases install the package that
> provides `ipa-getkeytab` on the control node or EE. The cert plugin uses
> `ipalib` like the vault plugin and can request, retrieve, and search IdM CA
> certificates without `certmonger` on the target. The OTP, selinuxmap,
> sudo, and hbacrule plugins use the same IdM client Python stack as the
> vault, principal, and cert lookups.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `plugins/inventory/idm.py` | Dynamic inventory plugin for hosts, hostgroups, netgroups, and HBAC rules |
| `plugins/lookup/vault.py` | Lookup plugin for IdM vault retrieval |
| `plugins/modules/vault_write.py` | Module for IdM vault lifecycle operations |
| `plugins/module_utils/ipa_client.py` | Shared Kerberos auth and `ipalib` connection utilities for IPA write operations |
| `plugins/lookup/principal.py` | Lookup plugin for Kerberos principal state queries |
| `plugins/lookup/keytab.py` | Lookup plugin for Kerberos keytab retrieval via `ipa-getkeytab` |
| `plugins/lookup/cert.py` | Lookup plugin for IdM CA certificate request, retrieval, and search |
| `plugins/lookup/otp.py` | Lookup plugin for OTP token issuance and host enrollment password generation |
| `plugins/lookup/selinuxmap.py` | Lookup plugin for SELinux user map state inspection |
| `plugins/lookup/sudo.py` | Lookup plugin for sudo rules, commands, and command groups |
| `plugins/lookup/hbacrule.py` | Lookup plugin for HBAC rule state inspection and access testing |
| `docs/` | Operator and maintainer documentation aligned with the collection interface |
| `scripts/validate-collection.sh` | Lightweight repo validation for YAML, plugin syntax, and collection build hygiene |
| `Makefile` | Wrapper for repo validation targets |
| `llms.txt` | Project-level navigation file for model consumers |
| `CITATION.cff` | Citation metadata for GitHub and downstream tooling |
| `CHANGELOG.md` | Release-history placeholder for Galaxy and repo hygiene |
| `meta/runtime.yml` | Collection runtime metadata |

## Author

Greg Procunier

## License

GPL-3.0-or-later. See [COPYING](https://github.com/gprocunier/eigenstate-ipa/blob/main/COPYING).

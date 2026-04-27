# eigenstate.ipa

**An Ansible collection for Red Hat IdM / FreeIPA with dynamic inventory, IdM vault retrieval and lifecycle automation, Kerberos principal state, keytab delivery, delegated user-lease control, certificate automation, OTP workflows, DNS record inspection, sudo policy inspection, SELinux user map inspection, and HBAC rule inspection and access testing.**

[![License: GPL-3.0](https://img.shields.io/github/license/gprocunier/eigenstate-ipa)](COPYING)
![Ansible 2.15+](https://img.shields.io/badge/Ansible-2.15%2B-blue)
![FreeIPA 4.6+](https://img.shields.io/badge/FreeIPA-4.6%2B-blue)
![RHEL](https://img.shields.io/badge/RHEL-9%20%7C%2010-red)

<a href="https://gprocunier.github.io/eigenstate-ipa/"><kbd>&nbsp;&nbsp;DOCS HOME&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

If you are mapping the collection into OpenShift ecosystem workflows:

<a href="https://gprocunier.github.io/eigenstate-ipa/openshift-primer.html"><kbd>&nbsp;&nbsp;OPENSHIFT ECOSYSTEM PRIMER&nbsp;&nbsp;</kbd></a>

For the adjacent branches off that primer:

<a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhoso-use-cases.html"><kbd>&nbsp;&nbsp;OPENSHIFT RHOSO USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhacm-use-cases.html"><kbd>&nbsp;&nbsp;OPENSHIFT RHACM USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/openshift-rhacs-use-cases.html"><kbd>&nbsp;&nbsp;OPENSHIFT RHACS USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/openshift-quay-use-cases.html"><kbd>&nbsp;&nbsp;OPENSHIFT QUAY USE CASES&nbsp;&nbsp;</kbd></a>

---

`eigenstate` is a nod to the quantum-mechanical idea of a stable observable
state. In practice, the collection assumes IdM already knows what the estate
looks like and what secrets it should hand out. The Ansible side should consume
that state directly instead of maintaining a parallel copy in static inventory
files and side-channel secret stores.

The GitHub repository name is `eigenstate-ipa`; the Ansible collection name is
`eigenstate.ipa`.

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
and two write modules.

## What The Collection Contains

The collection has three practical layers:

- live inventory from IdM host and policy data
- controller-side lookup plugins for Kerberos, vaults, certificates, OTP, DNS, and policy state
- narrow write modules for vault lifecycle and delegated temporary-user expiry

The table below is the authoritative surface summary.

| Plugin | Type | FQCN | Purpose |
| --- | --- | --- | --- |
| IdM inventory | inventory | `eigenstate.ipa.idm` | Builds live inventory from IdM-enrolled hosts and policy-backed group relationships |
| IdM vault | lookup | `eigenstate.ipa.vault` | Retrieves vault payloads, inspects metadata, and searches vault scopes in IdM |
| IdM vault lifecycle | module | `eigenstate.ipa.vault_write` | Creates, archives, updates, and deletes IdM vaults with check-mode and member-management support |
| Kerberos principal state | lookup | `eigenstate.ipa.principal` | Reads user, host, and service principal existence, key, lock, and last-auth state from IdM |
| Kerberos keytab | lookup | `eigenstate.ipa.keytab` | Retrieves Kerberos keytab files for service and host principals via `ipa-getkeytab` |
| User lease boundary | module | `eigenstate.ipa.user_lease` | Sets, expires, or clears user expiry attributes for delegated temporary-access workflows |
| IdM certificates | lookup | `eigenstate.ipa.cert` | Requests, retrieves, and searches IdM CA certificates for host and service principals |
| OTP and enrollment credentials | lookup | `eigenstate.ipa.otp` | Issues user OTP tokens and one-time host enrollment passwords through IdM |
| DNS record state | lookup | `eigenstate.ipa.dns` | Reads forward, reverse, zone-apex, and broad-search DNS records from IdM |
| SELinux user map state | lookup | `eigenstate.ipa.selinuxmap` | Reads SELinux user map configuration and HBAC-linked scope from IdM |
| Sudo policy state | lookup | `eigenstate.ipa.sudo` | Reads sudo rules, sudo commands, and sudo command groups from IdM |
| HBAC rule state and access test | lookup | `eigenstate.ipa.hbacrule` | Reads HBAC rule configuration and runs live access tests via the FreeIPA hbactest engine |

## Start Here

### Orientation

Use these first if you want the project map before you dive into individual surfaces.

<a href="https://gprocunier.github.io/eigenstate-ipa/"><kbd>&nbsp;&nbsp;DOCS HOME&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

### Core Capabilities

For identity-backed inventory and static secret handling:

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>&nbsp;&nbsp;INVENTORY CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>&nbsp;&nbsp;IDM VAULT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html"><kbd>&nbsp;&nbsp;VAULT WRITE CAPABILITIES&nbsp;&nbsp;</kbd></a>

For Kerberos, temporary access, certificates, and enrollment:

<a href="https://gprocunier.github.io/eigenstate-ipa/principal-capabilities.html"><kbd>&nbsp;&nbsp;PRINCIPAL CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>&nbsp;&nbsp;KEYTAB CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-capabilities.html"><kbd>&nbsp;&nbsp;USER LEASE CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>&nbsp;&nbsp;IDM CERT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html"><kbd>&nbsp;&nbsp;OTP CAPABILITIES&nbsp;&nbsp;</kbd></a>

For DNS and policy-aware controller checks:

<a href="https://gprocunier.github.io/eigenstate-ipa/dns-capabilities.html"><kbd>&nbsp;&nbsp;DNS CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-capabilities.html"><kbd>&nbsp;&nbsp;SELINUX MAP CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/sudo-capabilities.html"><kbd>&nbsp;&nbsp;SUDO CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-capabilities.html"><kbd>&nbsp;&nbsp;HBAC RULE CAPABILITIES&nbsp;&nbsp;</kbd></a>

For collection-wide workflow guidance:

<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>&nbsp;&nbsp;ROTATION CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>&nbsp;&nbsp;ROTATION USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>&nbsp;&nbsp;EPHEMERAL ACCESS CAPABILITIES&nbsp;&nbsp;</kbd></a>

### Worked Examples

When you already believe the plugin boundary fits and want the playbook shape:

<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>&nbsp;&nbsp;INVENTORY USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>&nbsp;&nbsp;IDM VAULT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-use-cases.html"><kbd>&nbsp;&nbsp;VAULT WRITE USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>&nbsp;&nbsp;PRINCIPAL USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>&nbsp;&nbsp;KEYTAB USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-use-cases.html"><kbd>&nbsp;&nbsp;USER LEASE USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>&nbsp;&nbsp;IDM CERT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-use-cases.html"><kbd>&nbsp;&nbsp;OTP USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/dns-use-cases.html"><kbd>&nbsp;&nbsp;DNS USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/selinuxmap-use-cases.html"><kbd>&nbsp;&nbsp;SELINUX MAP USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/sudo-use-cases.html"><kbd>&nbsp;&nbsp;SUDO USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-use-cases.html"><kbd>&nbsp;&nbsp;HBAC RULE USE CASES&nbsp;&nbsp;</kbd></a>

## For Vault Or CyberArk Users

Start with the comparison framing, then move into the collection-wide workflow guides.

<a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>&nbsp;&nbsp;VAULT/CYBERARK PRIMER&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>&nbsp;&nbsp;ROTATION CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>&nbsp;&nbsp;ROTATION USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>&nbsp;&nbsp;EPHEMERAL ACCESS CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>

If the comparison translates into an IdM-native workflow for you, these are the first concrete surfaces worth reading:

<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>&nbsp;&nbsp;IDM VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html"><kbd>&nbsp;&nbsp;VAULT WRITE MODULE&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>&nbsp;&nbsp;KEYTAB PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-plugin.html"><kbd>&nbsp;&nbsp;USER LEASE MODULE&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>&nbsp;&nbsp;IDM CERT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/hbacrule-plugin.html"><kbd>&nbsp;&nbsp;HBAC RULE PLUGIN&nbsp;&nbsp;</kbd></a>

## Quick Install

```bash
ansible-galaxy collection install eigenstate-ipa-1.10.12.tar.gz
```

Verify the main surfaces you plan to use. For example:

```bash
ansible-doc -t inventory eigenstate.ipa.idm
ansible-doc -t lookup eigenstate.ipa.vault
ansible-doc -t lookup eigenstate.ipa.keytab
ansible-doc -t module eigenstate.ipa.vault_write
ansible-doc -t module eigenstate.ipa.user_lease
```

For the full plugin index, use <a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>DOCS MAP</kbd></a>.

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
> sudo, hbacrule, and user_lease surfaces use the same IdM client Python stack as the
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
| `plugins/modules/user_lease.py` | Module for delegated temporary-user expiry and lease boundaries in IdM |
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

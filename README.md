# eigenstate.ipa

**An Ansible collection for Red Hat IdM / FreeIPA with dynamic inventory, IdM vault lookup, Kerberos keytab retrieval, and certificate issuance plugins for Kerberos-friendly automation, AAP, and secure secret delivery.**

[![License: GPL-3.0](https://img.shields.io/github/license/gprocunier/eigenstate-ipa)](COPYING)
![Ansible 2.14+](https://img.shields.io/badge/Ansible-2.14%2B-blue)
![FreeIPA 4.6+](https://img.shields.io/badge/FreeIPA-4.6%2B-blue)
![RHEL](https://img.shields.io/badge/RHEL-9%20%7C%2010-red)

<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>&nbsp;&nbsp;INVENTORY PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>&nbsp;&nbsp;IDM VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>&nbsp;&nbsp;KEYTAB PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>&nbsp;&nbsp;IDM CERT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>&nbsp;&nbsp;INVENTORY CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>&nbsp;&nbsp;IDM VAULT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>&nbsp;&nbsp;KEYTAB CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>&nbsp;&nbsp;IDM CERT CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>&nbsp;&nbsp;INVENTORY USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>&nbsp;&nbsp;IDM VAULT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>&nbsp;&nbsp;KEYTAB USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>&nbsp;&nbsp;IDM CERT USE CASES&nbsp;&nbsp;</kbd></a>
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

This collection closes that gap with one inventory plugin and three lookup plugins.

## What The Collection Contains

At a high level:

- `eigenstate.ipa.idm` reads IdM hosts, hostgroups, netgroups, and HBAC rules
  and turns them into Ansible inventory
- `eigenstate.ipa.vault` uses `ipalib` to retrieve, inspect, and search IdM
  vault content for playbooks and AAP jobs
- `eigenstate.ipa.keytab` uses `ipa-getkeytab` to retrieve Kerberos keytab
  files for service and host principals, returning base64-encoded content ready
  to write to disk or inject into an AAP credential type
- `eigenstate.ipa.cert` uses `ipalib` to request, retrieve, and search IdM CA
  certificates for host and service principals via the Dogtag backend

| Plugin | Type | FQCN | Purpose |
| --- | --- | --- | --- |
| IdM inventory | inventory | `eigenstate.ipa.idm` | Builds live inventory from IdM-enrolled hosts and policy-backed group relationships |
| IdM vault | lookup | `eigenstate.ipa.vault` | Retrieves vault payloads, inspects metadata, and searches vault scopes in IdM |
| Kerberos keytab | lookup | `eigenstate.ipa.keytab` | Retrieves Kerberos keytab files for service and host principals via `ipa-getkeytab` |
| IdM certificates | lookup | `eigenstate.ipa.cert` | Requests, retrieves, and searches IdM CA certificates for host and service principals |

## Start Here

If you want the project map and reading order, open
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>DOCS MAP</kbd></a>.

If you are deciding whether the collection fits your use case, start with:

- <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-capabilities.html"><kbd>INVENTORY CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-capabilities.html"><kbd>IDM VAULT CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-capabilities.html"><kbd>KEYTAB CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/cert-capabilities.html"><kbd>IDM CERT CAPABILITIES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>INVENTORY USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>IDM VAULT USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-use-cases.html"><kbd>KEYTAB USE CASES</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/cert-use-cases.html"><kbd>IDM CERT USE CASES</kbd></a>

If you are wiring the plugins into actual automation, start with:

- <a href="https://gprocunier.github.io/eigenstate-ipa/inventory-plugin.html"><kbd>INVENTORY PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/vault-plugin.html"><kbd>IDM VAULT PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/keytab-plugin.html"><kbd>KEYTAB PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/cert-plugin.html"><kbd>IDM CERT PLUGIN</kbd></a>
- <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>

## Quick Install

```bash
ansible-galaxy collection install eigenstate-ipa-1.2.0.tar.gz
```

Verify:

```bash
ansible-doc -t inventory eigenstate.ipa.idm
ansible-doc -t lookup eigenstate.ipa.vault
ansible-doc -t lookup eigenstate.ipa.keytab
ansible-doc -t lookup eigenstate.ipa.cert
```

> [!NOTE]
> The inventory plugin talks to the IdM JSON-RPC API and can use either
> password authentication or Kerberos with an optional keytab. The vault plugin
> uses `ipalib` and therefore depends on the local IdM client Python libraries
> being available on the control node or execution environment. The keytab
> plugin shells out to `ipa-getkeytab` and does not require `ipalib`; on RHEL
> 10 install `ipa-client`, and on other releases install the package that
> provides `ipa-getkeytab` on the control node or EE. The cert plugin uses
> `ipalib` like the vault plugin and can request, retrieve, and search IdM CA
> certificates without `certmonger` on the target.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `plugins/inventory/idm.py` | Dynamic inventory plugin for hosts, hostgroups, netgroups, and HBAC rules |
| `plugins/lookup/vault.py` | Lookup plugin for IdM vault retrieval |
| `plugins/lookup/keytab.py` | Lookup plugin for Kerberos keytab retrieval via `ipa-getkeytab` |
| `plugins/lookup/cert.py` | Lookup plugin for IdM CA certificate request, retrieval, and search |
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

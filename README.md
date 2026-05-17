# eigenstate.ipa

**An Ansible collection for Red Hat IdM / FreeIPA with live inventory, IdM
vault retrieval, KRA-aware vault diagnostics, vault artifact custody,
Kerberos principal state, keytab
delivery, certificate automation, OTP workflows, DNS inspection, sudo
inspection, sudo risk classification, SELinux map inspection, HBAC
inspection/testing, access-path preflight summaries, AAP execution
environment support, OpenShift/Kubernetes render-first workflows, temporary
access boundaries, and read-only operational evidence.**

[![License: GPL-3.0](https://img.shields.io/github/license/gprocunier/eigenstate-ipa)](COPYING)
![Ansible 2.15+](https://img.shields.io/badge/Ansible-2.15%2B-blue)
![FreeIPA 4.6+](https://img.shields.io/badge/FreeIPA-4.6%2B-blue)
![RHEL](https://img.shields.io/badge/RHEL-9%20%7C%2010-red)

<a href="https://gprocunier.github.io/eigenstate-ipa/"><kbd>&nbsp;&nbsp;DOCS HOME&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/start.html"><kbd>&nbsp;&nbsp;START HERE&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/reference/"><kbd>&nbsp;&nbsp;REFERENCE&nbsp;&nbsp;</kbd></a>

`eigenstate.ipa` treats IdM as live automation state where IdM is already the
right authority: hosts, groups, vaults, Kerberos principals, certificates, DNS,
sudo, HBAC, SELinux maps, and user expiry attributes.

The repository name is `eigenstate-ipa`; the Ansible collection name is
`eigenstate.ipa`.

## Use With, Not Instead Of

`eigenstate.ipa` is not a replacement for `redhat.rhel_idm` or
`freeipa.ansible_freeipa`.

Use `redhat.rhel_idm` or `freeipa.ansible_freeipa` for IdM server, replica,
and client lifecycle and broad IdM object management.

Use `eigenstate.ipa` when automation needs to consume live IdM state as
inventory, policy evidence, vault/keytab/certificate input, temporary-access
context, AAP execution material, or OpenShift/Kubernetes review artifacts.

## What The Collection Contains

| Surface | FQCN or path | Purpose |
| --- | --- | --- |
| Inventory | `eigenstate.ipa.idm` | Build live Ansible inventory from IdM host and policy state with normalized host attribute metadata. |
| Lookups | `eigenstate.ipa.vault`, `principal`, `keytab`, `cert`, `otp`, `dns`, `selinuxmap`, `sudo`, `hbacrule` | Read vault, Kerberos, certificate, OTP, DNS, sudo, SELinux map, and HBAC state. |
| Modules | `eigenstate.ipa.vault_write`, `vault_health`, `vault_artifact`, `access_path`, `keytab_manage`, `cert_request`, `user_lease` | Mutate narrow IdM boundaries explicitly, check vault/KRA health, manage generic vault artifact custody, and summarize access-path readiness. |
| Filters | `ensure_list`, `normalize_attribute`, `attribute_type`, `sudo_risk`, `classify_sudo_rule` | Normalize IdM attribute shapes and classify sudo policy risk in playbooks. |
| Roles | `roles/` | AAP EE, OpenShift identity validation, workload Secret rendering, temporary access, and reports. |
| Playbooks | `playbooks/` | Wrapper playbooks for common role workflows. |
| Execution environment | `execution-environment/eigenstate-idm/` | Ready-to-build AAP runtime scaffold for IdM-backed automation. |
| Tests | `tests/` | Unit, role-structure, argument-spec, secret-safety, compatibility, and integration fixtures. |

## Documentation

The public docs now use Diataxis:

- [Tutorials](https://gprocunier.github.io/eigenstate-ipa/tutorials/) teach the
  main flows safely.
- [How-to guides](https://gprocunier.github.io/eigenstate-ipa/how-to/) complete
  production tasks.
- [Reference](https://gprocunier.github.io/eigenstate-ipa/reference/) gives
  exact options, return shapes, roles, playbooks, schemas, and support facts.
- [Explanation](https://gprocunier.github.io/eigenstate-ipa/explanation/)
  describes architecture, authority boundaries, non-goals, and risks.

## Install

Install a built collection artifact:

```bash
ansible-galaxy collection install eigenstate-ipa-1.18.1.tar.gz
```

Verify the main surfaces you plan to use:

```bash
ansible-doc -t inventory eigenstate.ipa.idm
ansible-doc -t lookup eigenstate.ipa.vault
ansible-doc -t lookup eigenstate.ipa.keytab
ansible-doc -t module eigenstate.ipa.keytab_manage
ansible-doc -t module eigenstate.ipa.vault_write
ansible-doc -t module eigenstate.ipa.vault_health
ansible-doc -t module eigenstate.ipa.vault_artifact
ansible-doc -t module eigenstate.ipa.access_path
ansible-doc -t module eigenstate.ipa.cert_request
ansible-doc -t module eigenstate.ipa.user_lease
ansible-doc -t filter eigenstate.ipa.sudo_risk
```

## Boundaries

- IdM remains the authority for IdM records.
- The collection reads, renders, validates, or mutates through explicit Ansible
  surfaces.
- AAP orchestrates jobs and records evidence; it is not the identity authority.
- Kubernetes and OpenShift enforce only after reviewed configuration is applied.
- Reports are evidence artifacts, not remediation.

This project does not claim that IdM replaces a general-purpose vault, PAM
suite, or dynamic secret-lease system.

## License

GPL-3.0-or-later. See [COPYING](COPYING).

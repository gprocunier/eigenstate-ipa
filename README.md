# eigenstate.ipa

**An Ansible collection for Red Hat IdM / FreeIPA with live inventory, IdM
vault retrieval and lifecycle automation, Kerberos principal state, keytab
delivery, certificate automation, OTP workflows, DNS inspection, sudo
inspection, SELinux map inspection, HBAC inspection/testing, AAP execution
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

## What The Collection Contains

| Surface | FQCN or path | Purpose |
| --- | --- | --- |
| Inventory | `eigenstate.ipa.idm` | Build live Ansible inventory from IdM host and policy state. |
| Lookups | `eigenstate.ipa.vault`, `principal`, `keytab`, `cert`, `otp`, `dns`, `selinuxmap`, `sudo`, `hbacrule` | Read vault, Kerberos, certificate, OTP, DNS, sudo, SELinux map, and HBAC state. |
| Modules | `eigenstate.ipa.vault_write`, `keytab_manage`, `cert_request`, `user_lease` | Mutate narrow IdM, keytab, certificate, and temporary access boundaries explicitly. |
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
ansible-galaxy collection install eigenstate-ipa-1.16.0.tar.gz
```

Verify the main surfaces you plan to use:

```bash
ansible-doc -t inventory eigenstate.ipa.idm
ansible-doc -t lookup eigenstate.ipa.vault
ansible-doc -t lookup eigenstate.ipa.keytab
ansible-doc -t module eigenstate.ipa.keytab_manage
ansible-doc -t module eigenstate.ipa.vault_write
ansible-doc -t module eigenstate.ipa.cert_request
ansible-doc -t module eigenstate.ipa.user_lease
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

---
layout: default
title: Reference
diataxis: reference
diataxis_type: reference
audience: Operators and maintainers looking up exact facts
outcome: Find exact inventory, lookup, module, role, playbook, authentication, return, schema, support, and release details.
authority_boundary:
  - collection
workflow_boundary: read-only
evidence_shape:
  - ansible-doc
public_status: rewritten
source_material:
  - ../../plugins
  - ../../roles
  - ../../playbooks
last_verified: 2026-05-07
---

# Reference

Use reference pages when you already know the surface and need exact facts.
Reference pages should be terse, source-verified, and free of broad
architecture prose.

## Inventory

| Surface | Page | Source |
| --- | --- | --- |
| `eigenstate.ipa.idm` | [IdM inventory plugin](inventory/idm.html) | `plugins/inventory/idm.py` |

## Lookups

| Surface | Page | Source |
| --- | --- | --- |
| `eigenstate.ipa.vault` | [Vault lookup](lookups/vault.html) | `plugins/lookup/vault.py` |
| `eigenstate.ipa.principal` | [Principal lookup](lookups/principal.html) | `plugins/lookup/principal.py` |
| `eigenstate.ipa.keytab` | [Keytab lookup](lookups/keytab.html) | `plugins/lookup/keytab.py` |
| `eigenstate.ipa.cert` | [Certificate lookup](lookups/cert.html) | `plugins/lookup/cert.py` |
| `eigenstate.ipa.otp` | [OTP lookup](lookups/otp.html) | `plugins/lookup/otp.py` |
| `eigenstate.ipa.dns` | [DNS lookup](lookups/dns.html) | `plugins/lookup/dns.py` |
| `eigenstate.ipa.selinuxmap` | [SELinux map lookup](lookups/selinuxmap.html) | `plugins/lookup/selinuxmap.py` |
| `eigenstate.ipa.sudo` | [Sudo lookup](lookups/sudo.html) | `plugins/lookup/sudo.py` |
| `eigenstate.ipa.hbacrule` | [HBAC rule lookup](lookups/hbacrule.html) | `plugins/lookup/hbacrule.py` |

## Modules

| Surface | Page | Boundary |
| --- | --- | --- |
| `eigenstate.ipa.vault_write` | [Vault write module](modules/vault_write.html) | Mutates IdM vault lifecycle. |
| `eigenstate.ipa.keytab_manage` | [Keytab manage module](modules/keytab_manage.html) | Retrieves or explicitly rotates keytabs. |
| `eigenstate.ipa.cert_request` | [Certificate request module](modules/cert_request.html) | Requests certificates from CSRs; private keys stay outside the module. |
| `eigenstate.ipa.user_lease` | [User lease module](modules/user_lease.html) | Sets, clears, or expires IdM user access attributes. |

## Roles

| Area | Page |
| --- | --- |
| AAP execution environment | [AAP execution environment role](roles/aap_execution_environment.html) |
| OpenShift and Keycloak identity validation | [OpenShift identity roles](roles/openshift_identity.html) |
| Workload Secret, TLS, keytab, and sealed artifact delivery | [Workload Secret delivery roles](roles/workload_secret_delivery.html) |
| Temporary access | [Temporary access roles](roles/temporary_access.html) |
| Read-only reports | [Report roles](roles/reports.html) |

## Playbooks And Runtime

| Topic | Page |
| --- | --- |
| Wrapper playbooks | [Playbook reference](playbooks.html) |
| Kerberos, password, keytab, ipalib, and execution-environment dependencies | [Authentication reference](authentication.html) |
| Common lookup return shapes | [Return shapes](return-shapes.html) |
| Report output schemas | [Report schemas](report-schemas.html) |
| AAP execution environment scaffold | [Execution environment reference](execution-environment/eigenstate-idm.html) |

## Support And Release

| Topic | Page |
| --- | --- |
| Supported ansible-core, Python, RHEL, IdM, and AAP boundaries | [Support matrix](support-matrix.html) |
| Validation lanes, fixture boundaries, and publish gates | [Test strategy](test-strategy.html) |
| Release validation and publication gates | [Release process](release-process.html) |

---
layout: default
title: Documentation Map
diataxis: orientation
diataxis_type: orientation
audience: Readers following legacy documentation links
outcome: Route old documentation URLs to the new Diataxis structure.
authority_boundary:
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
source_material:
  - rewrite-audit.md
last_verified: 2026-05-07
---

# Documentation Map

The documentation now uses Diataxis:

- [Tutorials](/tutorials/) teach the main flows safely.
- [How-to guides](/how-to/) complete production tasks.
- [Reference](/reference/) gives exact facts for inventory, lookups, modules,
  roles, playbooks, schemas, support, and release process.
- [Explanation](/explanation/) covers architecture, authority boundaries,
  non-goals, and residual risk.

Legacy URLs are preserved as compatibility stubs and point to their canonical
replacement pages.

## Common Legacy Routes

| Old page | New page |
| --- | --- |
| `aap-ee-quickstart.html` | [Build an AAP execution environment](/tutorials/build-aap-execution-environment.html) |
| `aap-integration.html` | [AAP execution model](/explanation/aap-execution-model.html) |
| `vault-cyberark-primer.html` | [Comparison with Vault and CyberArk expectations](/explanation/comparison-vault-cyberark.html) |
| `reporting-overview.html` | [Generate operational evidence](/how-to/generate-operational-evidence.html) |
| `openshift-primer.html` | [OpenShift identity and workload model](/explanation/openshift-identity-and-workload-model.html) |
| `workload-secret-delivery-controls.html` | [OpenShift identity and workload model](/explanation/openshift-identity-and-workload-model.html) |
| `ephemeral-access-capabilities.html` | [Temporary access boundary](/explanation/temporary-access-boundary.html) |
| `inventory-plugin.html` | [IdM inventory plugin reference](/reference/inventory/idm.html) |
| `vault-plugin.html` | [Vault lookup reference](/reference/lookups/vault.html) |
| `keytab-plugin.html` | [Keytab lookup reference](/reference/lookups/keytab.html) |
| `cert-plugin.html` | [Certificate lookup reference](/reference/lookups/cert.html) |
| `user-lease-plugin.html` | [User lease module reference](/reference/modules/user_lease.html) |
| `support-matrix.html` | [Support matrix](/reference/support-matrix.html) |

## Current Routes

Use [Start Here](/start.html) for task routing or [Reference](/reference/) when
you already know the exact collection surface.

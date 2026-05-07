---
layout: default
title: Comparison with Vault and CyberArk expectations
diataxis: explanation
diataxis_type: explanation
audience: Operators and maintainers
outcome: Compare IdM-native workflows with broader vault and PAM expectations.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
last_verified: 2026-05-07
---

# Comparison with Vault and CyberArk expectations

## What Claim Is Being Made?

The fair comparison is boundary-based: IdM-backed automation is useful when the secret or access workflow is already tied to IdM identity, Kerberos, certificates, host enrollment, or policy state.

## What Problem Does It Address?

Operators familiar with Vault or CyberArk may expect dynamic leases, brokering, PAM session control, or enterprise-wide secret inventory. This collection intentionally does not claim all of those jobs.

## Which System Owns Which Responsibility?

| System | Responsibility |
| --- | --- |
| IdM vaults | Store IdM vault material under IdM scope and membership. |
| Collection | Retrieves and manages IdM-native material for Ansible workflows. |
| Vault/CyberArk-class platforms | Remain appropriate for broad dynamic secret, PAM, brokering, and non-IdM estates. |
| AAP | Can schedule and evidence either model, but does not collapse their boundaries. |

## What Evidence Proves The Boundary?

- Vault lookup and vault lifecycle module behavior.
- Keytab and certificate workflows tied to IdM principals.
- Temporary access expiry evidence.
- Explicit non-claim statements in task pages.

## What Does This Not Claim?

- IdM replaces every secret manager.
- IdM provides dynamic database credential leases.
- The collection records privileged session activity like a PAM suite.

## What Risks Remain?

- Readers may over-extend IdM vaults beyond their intended scope.
- Static secrets still need lifecycle controls.
- Mixed estates may need both IdM-native and external secret-manager patterns.

---
layout: default
title: Secret boundary
diataxis: explanation
diataxis_type: explanation
audience: Operators and maintainers
outcome: Understand where IdM vault workflows fit and where they do not.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
last_verified: 2026-05-07
---

# Secret boundary

## What Claim Is Being Made?

IdM vaults are useful for IdM-native automation secrets, especially when Kerberos-authenticated Ansible jobs already run near IdM. They are not a claim that IdM replaces every enterprise secret manager.

## What Problem Does It Address?

Automation often copies static secrets into inventory, Controller variables, local files, or unrelated stores because the job cannot retrieve IdM vault material directly.

## Which System Owns Which Responsibility?

| System | Responsibility |
| --- | --- |
| IdM | Stores vault metadata, membership, and payloads under IdM vault semantics. |
| eigenstate.ipa | Retrieves or manages vaults through lookup and module surfaces. |
| Ansible/AAP | Runs the workflow and must protect variables, logs, and credentials. |
| External secret platforms | Remain appropriate for dynamic leases, broad application secret brokering, and non-IdM use cases. |

## What Evidence Proves The Boundary?

- Vault lookup metadata or payload retrieval output with payload redacted.
- `vault_write` module results for explicit lifecycle changes.
- AAP job output showing no payload disclosure.

## What Does This Not Claim?

- IdM is not a general-purpose dynamic secret lease engine.
- The collection is not a PAM suite.
- A retrieved secret is not automatically safe after Ansible stores it in a variable.

## What Risks Remain?

- Ansible variables can leak through debug, failed tasks, or fact caches.
- Vault membership and IdM ACLs must be maintained correctly.
- Long-lived static secrets still need rotation and review.

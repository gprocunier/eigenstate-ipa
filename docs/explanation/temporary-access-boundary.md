---
layout: default
title: Temporary access boundary
diataxis: explanation
diataxis_type: explanation
audience: Operators and maintainers
outcome: Understand lease-like access and what it is not.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
source_material:
  - ../rewrite-audit.md
last_verified: 2026-05-07
---

# Temporary access boundary

## What Claim Is Being Made?

Temporary access is represented by IdM expiry attributes for existing users. It is lease-like operational control, not a dynamic secret lease system.

## What Problem Does It Address?

Delegated operators need a bounded way to open and close access without owning full IdM administration.

## Which System Owns Which Responsibility?

| System | Responsibility |
| --- | --- |
| IdM | Owns user objects and expiry attributes. |
| `user_lease` module | Sets, clears, or immediately expires the configured access boundary. |
| Temporary access roles | Add preflight and evidence around the module. |
| Reports | Record access-window evidence but do not enforce it. |

## What Evidence Proves The Boundary?

- Module return showing previous and final expiry values.
- Fresh authentication success during the window and failure after expiry.
- Temporary access report artifact.

## What Does This Not Claim?

- This is not a general PAM workflow.
- It does not revoke already-active sessions by itself.
- It does not replace site breakglass policy.

## What Risks Remain?

- Existing sessions may survive until separately terminated.
- Clock skew can confuse short windows.
- Delegated permissions must be scoped carefully.

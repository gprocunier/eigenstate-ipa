---
layout: default
title: Kerberos keytab boundary
diataxis: explanation
diataxis_type: explanation
audience: Operators and maintainers
outcome: Understand keytab retrieval, rotation, and residual risk.
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

# Kerberos keytab boundary

## What Claim Is Being Made?

Keytab retrieval and key rotation are different safety boundaries. Retrieval should not be documented as harmless if it returns key material; rotation invalidates existing keytabs and must be explicit.

## What Problem Does It Address?

Keytabs often move through manual staging or side scripts. That hides who retrieved the material, whether keys rotated, and where payload bytes landed.

## Which System Owns Which Responsibility?

| System | Responsibility |
| --- | --- |
| IdM/Kerberos | Own principal keys and keytab issuance behavior. |
| `keytab` lookup | Retrieves keytab content for playbook use. |
| `keytab_manage` module | Retrieves, writes, or rotates keytabs through explicit module semantics. |
| Ansible/AAP | Must protect payload output and destination file permissions. |

## What Evidence Proves The Boundary?

- Principal preflight result before keytab work.
- Module return showing `rotated` state only when explicitly requested.
- Destination path, mode, owner, and group when writing a keytab.

## What Does This Not Claim?

- Retrieval is not the same as rotation.
- Rotation is not safe to run implicitly.
- Base64 keytab content is still secret material.

## What Risks Remain?

- Existing services can fail after rotation if not updated.
- Payload bytes can leak through logs or artifacts.
- Host or service principal ACLs can be too broad.

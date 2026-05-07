---
layout: default
title: AAP execution model
diataxis: explanation
diataxis_type: explanation
audience: Operators and maintainers
outcome: Understand execution environments, Controller jobs, inventory sync, and evidence.
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

# AAP execution model

## What Claim Is Being Made?

AAP is the orchestration and evidence layer. It should consume IdM-backed collection surfaces from a controlled execution environment rather than becoming the identity authority.

## What Problem Does It Address?

IdM-backed automation depends on platform packages, Python libraries, Kerberos tooling, and repeatable credentials. AAP needs a consistent runtime image and job record.

## Which System Owns Which Responsibility?

| System | Responsibility |
| --- | --- |
| Execution environment | Packages Ansible, collection dependencies, IdM client libraries, and platform tooling. |
| AAP Controller | Runs jobs, schedules workflows, injects credentials, and records job output. |
| IdM | Remains the identity and policy source. |
| Collection roles/playbooks | Render, validate, build, smoke, and optionally register the runtime. |

## What Evidence Proves The Boundary?

- Rendered EE build context.
- Build and smoke-test output.
- Controller registration result if that optional step is run.
- AAP job output for inventory, lookup, role, or report runs.

## What Does This Not Claim?

- AAP does not create IdM truth.
- Controller credentials are not a substitute for IdM ACL design.
- A successful EE build is not proof that every IdM workflow is authorized.

## What Risks Remain?

- Execution environments can drift from release expectations.
- Credentials can be over-scoped.
- Job output can leak values if tasks are not marked correctly.

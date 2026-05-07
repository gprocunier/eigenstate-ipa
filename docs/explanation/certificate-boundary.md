---
layout: default
title: Certificate boundary
diataxis: explanation
diataxis_type: explanation
audience: Operators and maintainers
outcome: Understand CSR, CA, certificate, and private-key responsibilities.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
last_verified: 2026-05-07
---

# Certificate boundary

## What Claim Is Being Made?

The collection can request and retrieve certificates, but private key creation and protection stay outside the certificate request surface.

## What Problem Does It Address?

Certificate automation often hides where CSRs came from and whether private keys were protected. The boundary must keep public certificate material separate from private key material.

## Which System Owns Which Responsibility?

| System | Responsibility |
| --- | --- |
| IdM CA | Issues certificates from CSRs under CA/profile policy. |
| `cert` lookup | Requests, retrieves, or searches certificate records. |
| `cert_request` module | Submits CSR content or a CSR file and returns certificate metadata/content. |
| Operator/site workflow | Generates and stores private keys securely before CSR submission. |

## What Evidence Proves The Boundary?

- CSR path or CSR content reference.
- Certificate metadata from the module or lookup.
- Written certificate destination and mode when configured.

## What Does This Not Claim?

- The module does not generate private keys.
- A certificate is not proof that the private key is protected.
- Certificate issuance is not cluster runtime enforcement.

## What Risks Remain?

- Bad CSR inputs can request the wrong identity.
- Private keys can leak outside this module.
- CA profile and sub-CA policy must be reviewed separately.

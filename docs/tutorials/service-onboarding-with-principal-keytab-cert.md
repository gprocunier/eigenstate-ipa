---
layout: default
title: Onboard a service with principal, keytab, and certificate checks
diataxis: tutorial
diataxis_type: tutorial
audience: Operators learning IdM-backed automation flows
outcome: Learn the sequence for principal preflight, keytab retrieval, and certificate request.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-07
---
{% raw %}

# Onboard a service with principal, keytab, and certificate checks

## What You Will Build

A safe service onboarding sequence that checks principal state before handling keytab or certificate material.

## What You Need Before Starting

- A lab service principal
- A CSR generated outside the certificate request module
- Authority to retrieve keytabs and request certificates

## Lab Assumptions

- The private key never appears in docs or task output.
- Keytab retrieval is protected with `no_log: true`.
- Certificate request uses a lab CSR.

## Step-By-Step Path

1. Check the service principal exists.
2. Retrieve or manage keytab material only after the principal check passes.
3. Submit a CSR for certificate issuance.
4. Record safe metadata from the result.

Create `onboard-service.yml` from the example below. Keep the keytab task
redacted and use a CSR generated outside the playbook.

{% endraw %}
{% include task_example.html id="service-onboarding-with-principal-keytab-cert" %}
{% raw %}

## Expected Result

The play should stop at the principal preflight if IdM is missing the service
principal. When the preflight passes, the keytab retrieval task remains redacted
and the certificate task writes only the issued certificate, not private-key
material.

## What You Learned

- Principal preflight prevents blind key material workflows.
- Keytab retrieval and rotation are different boundaries.
- Certificate requests should not own private-key handling.

## Next Page

Continue with [/how-to/request-idm-certificate.html](../how-to/request-idm-certificate.html).

{% endraw %}

---
layout: default
title: Request an IdM certificate
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when a CSR already exists and IdM CA should issue a certificate for a host or service principal.
authority_boundary:
  - idm
  - certificate-authority
  - collection
workflow_boundary: mutating
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-07
---
{% raw %}

# Request an IdM certificate

## When To Use This

Use this when a CSR already exists and IdM CA should issue a certificate for a host or service principal.

## Required Authority

The IdM CA issues the certificate. Private key generation and storage stay outside the module.

## Safety Boundary

This workflow is `mutating`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Inputs

- CSR content or controller-local CSR path
- Principal name
- Optional certificate profile or sub-CA

## Steps

1. Generate and protect the private key outside the module.
2. Submit the CSR through `cert_request`.
3. Write the issued certificate or return safe metadata for downstream tasks.

```yaml
- name: Request certificate from IdM CA
  eigenstate.ipa.cert_request:
    principal: HTTP/app.example.com
    csr_path: /secure/csr/http-app.csr
    destination: /secure/certs/http-app.crt
    mode: "0644"
```

{% endraw %}
{% include task_example.html id="request-idm-certificate" %}
{% raw %}

## Expected Result

The module returns certificate metadata and optionally writes the issued certificate. It does not handle private-key material.

## Troubleshooting

- CSR rejected: verify principal, SANs, profile, and CA policy.
- Private key missing: create it before calling the module.
- Wrong issuer: verify profile and sub-CA options.

## Related Reference

- [/reference/modules/cert_request.html](../reference/modules/cert_request.html)
- [/explanation/certificate-boundary.html](../explanation/certificate-boundary.html)

{% endraw %}

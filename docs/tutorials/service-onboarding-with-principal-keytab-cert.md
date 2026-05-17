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
last_verified: 2026-05-17
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

```bash
ansible-playbook -i inventory.eigenstate_ipa.yml onboard-service.yml
```

## Expected Evidence

If the principal exists, the run proceeds through keytab retrieval (redacted)
and certificate request.

```text
PLAY [Onboard an HTTP service through IdM-backed checks] ***************

TASK [Confirm the service principal exists] ****************************
ok: [app01.example.com] => {
    "msg": "Assertion passed"
}

TASK [Retrieve the existing service keytab] ****************************
changed: [app01.example.com] => (output redacted by no_log)

TASK [Request certificate from an existing CSR] ************************
changed: [app01.example.com]

PLAY RECAP ************************************************************
app01.example.com : ok=3    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

When the principal is missing, the role fails at the preflight stage and does not
retrieve keytab/certificate material:

```text
TASK [Confirm the service principal exists] *****************************
failed: [app01.example.com] => {"msg": "Assertion failed"}
...preflight for service principal failed; workflow stopped
```

## What You Learned

- Principal preflight prevents blind key material workflows.
- Keytab retrieval and rotation are different boundaries.
- Certificate requests should not own private-key handling.

## Next Page

Continue with [/how-to/request-idm-certificate.html](../how-to/request-idm-certificate.html).

{% endraw %}

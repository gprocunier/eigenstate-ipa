---
layout: default
title: Open and close a temporary access window
diataxis: tutorial
diataxis_type: tutorial
audience: Operators learning IdM-backed automation flows
outcome: Learn the lease-like access boundary and expiry evidence.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - command-output
public_status: rewritten
source_material:
  - ../rewrite-audit.md
last_verified: 2026-05-07
---
{% raw %}

# Open and close a temporary access window

## What You Will Build

A lab-only temporary access window and a report showing the boundary.

## What You Need Before Starting

- An existing lab user
- Delegated permission to manage user expiry attributes
- A short test window that can expire safely

## Lab Assumptions

- Use a disposable lab user.
- Do not test against a production breakglass account.
- The tutorial demonstrates expiry behavior, not dynamic secret leasing.

## Step-By-Step Path

1. Open a short access window for the lab user.
2. Run a fresh authentication check during the window.
3. Expire or wait out the window.
4. Run a fresh authentication check after expiry.

```bash
ansible-playbook playbooks/temporary-access-window.yml -e user=lab-temp-user -e lease_seconds=900
ansible-playbook playbooks/report-temporary-access.yml
```

## Expected Output

```text
temporary_access_state: open
principal_expiration_after: 2026-05-07T15:15:00Z
post_expiry_fresh_auth: denied
```

## What You Learned

- Temporary access is represented through IdM expiry attributes.
- Fresh authentication after expiry is the important proof.
- Reports record evidence but do not enforce remediation.

## Next Page

Continue with [/how-to/open-temporary-access-window.html](/how-to/open-temporary-access-window.html).

{% endraw %}

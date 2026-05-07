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
ansible-playbook temporary-access.yml
```

{% endraw %}
{% include task_example.html id="temporary-access-window" %}
{% raw %}

## Expected Result

The role should open the temporary access window and write metadata-only report
artifacts under `./artifacts`. Expiration timestamps depend on when the play
runs, so verify the generated report from your own run instead of comparing
against a fixed timestamp.

## What You Learned

- Temporary access is represented through IdM expiry attributes.
- Fresh authentication after expiry is the important proof.
- Reports record evidence but do not enforce remediation.

## Next Page

Continue with [/how-to/open-temporary-access-window.html](../how-to/open-temporary-access-window.html).

{% endraw %}

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
last_verified: 2026-05-17
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
2. Optionally verify authentication behavior while the window is active.
3. Expire the window with the same playbook.
4. Verify authentication behavior after expiry.

```bash
ansible-playbook temporary-access.yml
ansible-playbook temporary-access.yml -e access_state=expire
ls -l artifacts
```

{% endraw %}
{% include task_example.html id="temporary-access-window" %}
{% raw %}

## Expected Evidence

Open and expire each produce metadata-only evidence. Static report validation
produces this review shape:

```text
TASK [eigenstate.ipa.temporary_access_report : Render temporary access report JSON] ***
changed: [localhost]

TASK [eigenstate.ipa.temporary_access_report : Render temporary access report YAML] ***
changed: [localhost]

TASK [eigenstate.ipa.temporary_access_report : Render temporary access report Markdown] ***
changed: [localhost]
```

Sanitized JSON fields look like:

```json
{
  "schema": "eigenstate.ipa/temporary_access_report/v1",
  "read_only": true,
  "summary": {
    "total_windows": "1",
    "expired_windows": "1"
  },
  "windows": [
    {
      "principal": "contractor01",
      "target": "bastion.example.com",
      "status": "expired",
      "opened_at": "2026-05-01T14:00:00Z",
      "expires_at": "2026-05-01T18:00:00Z"
    }
  ]
}
```

## What You Learned

- Temporary access is represented through IdM expiry attributes.
- Fresh authentication after expiry is the important proof.
- Reports record evidence but do not enforce remediation.

## Next Page

Continue with [/how-to/open-temporary-access-window.html](../how-to/open-temporary-access-window.html).

{% endraw %}

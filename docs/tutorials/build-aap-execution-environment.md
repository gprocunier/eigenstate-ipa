---
layout: default
title: Build an AAP execution environment
diataxis: tutorial
diataxis_type: tutorial
audience: Operators learning IdM-backed automation flows
outcome: Learn the render, build, smoke, and optional registration path.
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

# Build an AAP execution environment

## What You Will Build

A rendered EE build context and a smoke-tested image tag for IdM-backed automation.

## What You Need Before Starting

- Container build tooling available to the role
- Registry access if pushing is part of the lab
- AAP Controller access only if registering the image

## Lab Assumptions

- The lab can build locally first.
- Registration is optional.
- No production Controller object is changed during the first pass.

## Step-By-Step Path

1. Render the EE build context.
2. Build the image from that context.
3. Run the smoke playbook.
4. Register in Controller only after the smoke output is acceptable.

```bash
ansible-playbook playbooks/aap-ee-render.yml
ansible-playbook playbooks/aap-ee-build.yml
ansible-playbook playbooks/aap-ee-smoke.yml
```

## Expected Output

```text
TASK [Smoke test IdM client tools]
ok: [localhost] => {
  "changed": false,
  "eigenstate_ipa_runtime": "available"
}
```

## What You Learned

- The EE packages IdM client dependencies for repeatable AAP jobs.
- Smoke output is the first proof before Controller registration.
- Disconnected builds need mirrored inputs but the same validation shape.

## Next Page

Continue with [/how-to/build-disconnected-aap-ee.html](../how-to/build-disconnected-aap-ee.html).

{% endraw %}

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
last_verified: 2026-05-17
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
ansible-playbook build-ee.yml
```

{% endraw %}
{% include task_example.html id="build-aap-execution-environment" %}
{% raw %}

## Expected Evidence

The first required evidence is the rendered Ansible Builder context. A captured
render run from this checkout produced:

```text
PLAY [Render eigenstate.ipa AAP execution environment build context] ***********

TASK [Create execution environment build context directory] *************
changed: [localhost]

TASK [Render execution environment build context files] ****************
changed: [localhost] => (item=execution-environment.yml)
changed: [localhost] => (item=requirements.yml)
changed: [localhost] => (item=bindep.txt)
changed: [localhost] => (item=python-requirements.txt)
changed: [localhost] => (item=ansible.cfg.example)
changed: [localhost] => (item=README.md)

TASK [Show rendered execution environment file list] *******************
ok: [localhost] => {
    "eigenstate_ee_rendered_files": [
        ".../build/eigenstate-idm-ee/execution-environment.yml",
        ".../build/eigenstate-idm-ee/requirements.yml",
        ".../build/eigenstate-idm-ee/bindep.txt",
        ".../build/eigenstate-idm-ee/python-requirements.txt",
        ".../build/eigenstate-idm-ee/ansible.cfg.example",
        ".../build/eigenstate-idm-ee/README.md"
    ]
}

PLAY RECAP *********************************************************************
localhost                  : ok=4    changed=2    unreachable=0    failed=0    skipped=14   rescued=0    ignored=0
```

In a build-capable lab, the next expected tasks are `Verify ansible-builder is
available`, `Build execution environment image`, and then the smoke command
loop. Controller registration remains a separate, optional step.

## What You Learned

- The EE packages IdM client dependencies for repeatable AAP jobs.
- Smoke output is the first proof before Controller registration.
- Disconnected builds need mirrored inputs but the same validation shape.

## Next Page

Continue with [/how-to/build-disconnected-aap-ee.html](../how-to/build-disconnected-aap-ee.html).

{% endraw %}

---
layout: default
title: AAP EE Disconnected Build
description: >-
  Build the eigenstate.ipa IdM execution environment with mirrored images,
  mirrored collections, and internal RPM repositories.
---

{% raw %}

# AAP EE Disconnected Build

Use this page when the Controller environment cannot pull directly from public
registries or Galaxy endpoints.

## Mirror Base EE Image

Mirror the selected RHEL 9 AAP minimal EE image into a trusted internal
registry, then render with that image:

```bash
ansible-playbook playbooks/aap-ee-render.yml \
  -e eigenstate_ee_base_image=registry.example.com/aap/ee-minimal-rhel9:latest \
  -e eigenstate_ee_output_dir=/tmp/eigenstate-idm-ee
```

Pin a digest when the environment requires repeatable proofs.

## Mirror Collections

Mirror these collections into private automation hub or an internal Galaxy
server:

- `eigenstate.ipa`
- `freeipa.ansible_freeipa`
- `community.general`
- `community.crypto`
- optional `kubernetes.core`, `community.okd`, and `ansible.controller`

Use a local, untracked `ansible.cfg` or environment-provided automation hub
configuration. Do not commit tokens into `ansible.cfg.example`.

## Provide RPM Repositories

The default EE relies on RPMs for FreeIPA client support:

- `ipa-client`
- `python3-ipalib`
- `python3-ipaclient`
- `krb5-workstation`

Expose those packages through Satellite or an equivalent internal repository
that the selected base image can use during `ansible-builder build`.

## Avoid Token Leakage

Keep registry credentials, automation hub tokens, IPA passwords, keytabs,
private keys, vault passwords, and pull secrets outside the repository. Use
runtime credentials, environment variables, or local files ignored by source
control.

## Safe Config Inputs

Use `ansible.cfg.example` only as a reference for collection paths and enabled
inventory plugins. For private automation hub, put token-bearing config in a
local file or Controller credential. For build-time proxies or internal repos,
prefer controlled build settings and documented environment variables over
committed secrets.

{% endraw %}

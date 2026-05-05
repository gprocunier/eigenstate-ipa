---
layout: default
title: AAP EE Quickstart
description: >-
  Build, smoke-test, publish, and register the eigenstate.ipa IdM execution
  environment for Ansible Automation Platform.
---

{% raw %}

# AAP EE Quickstart

Related docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/aap-ee-disconnected-build.html"><kbd>&nbsp;&nbsp;DISCONNECTED BUILD&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-ee-troubleshooting.html"><kbd>&nbsp;&nbsp;TROUBLESHOOTING&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-ee-seller-demo.html"><kbd>&nbsp;&nbsp;SELLER DEMO&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>

## What This EE Solves

Ansible Automation Platform execution environments are consistent container
images containing Ansible Core, Runner, collections, Python libraries, system
packages, and site-specific runtime needs. For `eigenstate.ipa`, the important
runtime needs are the collection itself, the FreeIPA client Python libraries,
Kerberos tooling, `ipa-getkeytab`, and collection documentation that can be
validated inside the image.

AAP users normally build an EE, push it to a registry, add it to Controller,
and then reference it from inventory sources or job templates. This quickstart
uses the checked-in scaffold and the `aap_execution_environment` role to make
that path repeatable.

## Prerequisites

- Podman or Docker
- `ansible-builder`
- access to `registry.redhat.io`
- optional private automation hub or registry for customer environments

## Render Build Context

```bash
ansible-playbook playbooks/aap-ee-render.yml \
  -e eigenstate_ee_output_dir=/tmp/eigenstate-idm-ee
```

The rendered directory contains `execution-environment.yml`,
`requirements.yml`, `bindep.txt`, `python-requirements.txt`, `README.md`, and
`ansible.cfg.example`.

## Build Image

```bash
cd /tmp/eigenstate-idm-ee
ansible-builder build -t localhost/eigenstate-idm-ee:dev
```

Pin a base-image digest only when your environment requires reproducibility:

```bash
ansible-playbook playbooks/aap-ee-render.yml \
  -e eigenstate_ee_base_image=registry.example.com/aap/ee-minimal-rhel9@sha256:...
```

## Smoke Test Image

```bash
ansible-playbook playbooks/aap-ee-smoke.yml \
  -e eigenstate_ee_image=localhost/eigenstate-idm-ee:dev
```

The smoke test checks `ansible`, `ansible-doc` for the important
`eigenstate.ipa` inventory, lookup, and module surfaces, `ipalib` imports,
`kinit`, and `ipa-getkeytab`.

## Push To Registry

Authenticate outside the role:

```bash
podman login registry.example.com
```

Push explicitly:

```bash
ansible-playbook playbooks/aap-ee-push.yml \
  -e eigenstate_ee_image=localhost/eigenstate-idm-ee:dev \
  -e eigenstate_ee_registry_image=registry.example.com/automation/eigenstate-idm-ee:dev
```

Do not commit registry credentials, automation hub tokens, or pull secrets.

## Add To Automation Controller

Register explicitly with token auth:

```bash
ansible-playbook playbooks/aap-ee-register-controller.yml \
  -e eigenstate_controller_host=https://controller.example.com \
  -e eigenstate_controller_oauthtoken="${CONTROLLER_OAUTH_TOKEN}" \
  -e eigenstate_controller_organization=Default \
  -e eigenstate_ee_registry_image=registry.example.com/automation/eigenstate-idm-ee:dev
```

Then select the EE on the inventory source or job template that runs
`eigenstate.ipa`.

## Mount IdM Credentials In AAP

Use Controller credentials or job settings to place runtime material inside the
EE:

- IdM CA certificate: `/etc/ipa/ca.crt`
- admin keytab: `/runner/env/ipa/admin.keytab`
- service keytab: `/runner/env/ipa/<service>.keytab`
- optional Kerberos cache: set `KRB5CCNAME` only when a workflow manages a
  custom cache path

Prefer keytab-backed Kerberos over reusable admin passwords. If a task consumes
secret payloads, keytab bytes, OTP values, private keys, vault passwords, or
admin passwords, put `no_log: true` on the task or block.

## First Working Jobs

Documentation smoke:

```yaml
---
- name: Validate eigenstate.ipa docs inside the EE
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Show vault lookup documentation
      ansible.builtin.command:
        argv:
          - ansible-doc
          - -t
          - lookup
          - eigenstate.ipa.vault
      changed_when: false
```

Vault metadata lookup:

```yaml
---
- name: Read vault metadata without exposing payloads
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Query shared vault metadata
      ansible.builtin.set_fact:
        vault_meta: "{{ lookup('eigenstate.ipa.vault', 'shared/app-config', operation='metadata') }}"
      no_log: true
```

Keytab availability check:

```yaml
---
- name: Check service keytab availability
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Retrieve service keytab into a protected runtime path
      ansible.builtin.copy:
        dest: /runner/env/ipa/http.keytab
        content: "{{ lookup('eigenstate.ipa.keytab', 'HTTP/app.example.com@EXAMPLE.COM') }}"
        mode: "0600"
      no_log: true
```

`user_lease` check-mode preview:

```yaml
---
- name: Preview delegated user expiry
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Preview temporary user lease
      eigenstate.ipa.user_lease:
        user: contractor1
        expires_at: "2026-06-01T17:00:00Z"
        ipaadmin_keytab: /runner/env/ipa/admin.keytab
        ipaadmin_principal: admin
      check_mode: true
```

## Troubleshooting

Start with
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-ee-troubleshooting.html"><kbd>AAP EE TROUBLESHOOTING</kbd></a>
for missing packages, Kerberos cache issues, CA certificate problems, registry
pull errors, and collection discovery failures.

{% endraw %}

---
layout: default
title: AAP EE Validation Walkthrough
description: >-
  Validation walkthrough for the eigenstate.ipa IdM execution environment.
---

{% raw %}

# AAP EE Validation Walkthrough

Use this path to validate the runtime image, Controller registration, and
representative IdM-backed automation workflows.

## 1. Build Or Use Prebuilt EE

Build locally:

```bash
ansible-playbook playbooks/aap-ee-render.yml \
  -e eigenstate_ee_output_dir=/tmp/eigenstate-idm-ee
cd /tmp/eigenstate-idm-ee
ansible-builder build -t localhost/eigenstate-idm-ee:validation
```

Or start from a prebuilt image already pushed to the target registry.

## 2. Add It To Controller

Register the image in Controller and select it on the validation inventory
source or job template.

## 3. Run Smoke Job

Verify that the EE contains the collection and IdM runtime dependencies:

```bash
ansible-playbook playbooks/aap-ee-smoke.yml \
  -e eigenstate_ee_image=localhost/eigenstate-idm-ee:validation
```

## 4. Run IdM Inventory Sync

Use `eigenstate.ipa.idm` to verify live host, hostgroup, netgroup, or
HBAC-shaped inventory from IdM instead of a parallel static file.

## 5. Run Vault Metadata Lookup

Verify metadata or existence checks first. If the job touches payloads, keep
the task under `no_log: true`.

## 6. Run HBAC Access Test

Use `eigenstate.ipa.hbacrule` to verify that the workflow can ask IdM whether a
user, host, service, or access path is actually allowed before the change runs.

## 7. Run `user_lease` Check Mode

Preview a temporary user expiry change:

```yaml
---
- name: Preview temporary user lease
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Preview delegated expiry
      eigenstate.ipa.user_lease:
        user: contractor1
        expires_at: "2026-06-01T17:00:00Z"
        ipaadmin_keytab: /runner/env/ipa/admin.keytab
        ipaadmin_principal: admin
      check_mode: true
```

## Technical Significance

RHEL, AAP, and OpenShift deployments often already trust IdM for host identity,
Kerberos, certificates, DNS, and access policy. The EE makes that identity
state usable in Controller jobs without hand-built runtime images, copied
secrets, or static inventory drift.

{% endraw %}

---
layout: default
title: User Lease Use Cases
---

{% raw %}

# User Lease Use Cases

Related docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-plugin.html"><kbd>&nbsp;&nbsp;USER LEASE PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-capabilities.html"><kbd>&nbsp;&nbsp;USER LEASE CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-demo.html"><kbd>&nbsp;&nbsp;USER LEASE DEMO&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-rbac-setup.html"><kbd>&nbsp;&nbsp;USER LEASE RBAC SETUP&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>&nbsp;&nbsp;EPHEMERAL ACCESS CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

## Purpose

This page contains worked playbook patterns for `eigenstate.ipa.user_lease`.
Use the capability guide to decide whether the module fits the temporary-access
problem. Use this page when you need the corresponding playbook shape.

If the IdM operator has not yet created the governed group, delegated
permission, privilege, role, and operator user, start with
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-rbac-setup.html"><kbd>USER LEASE RBAC SETUP</kbd></a>.

## Contents

- [0. Watch the Manual Demo](#0-watch-the-manual-demo)
- [1. Give a Temporary User a Two-Hour Lease](#1-give-a-temporary-user-a-two-hour-lease)
- [2. End Temporary Access Immediately](#2-end-temporary-access-immediately)
- [3. Use a Governed Group Boundary](#3-use-a-governed-group-boundary)
- [4. Pair the Lease with an HBAC Gate](#4-pair-the-lease-with-an-hbac-gate)
- [5. Use It from AAP](#5-use-it-from-aap)

---

## 0. Watch the Manual Demo

If you want to see the boundary before reading playbooks, start with
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-demo.html"><kbd>USER LEASE DEMO</kbd></a>.

That page walks through the recorded manual flow in
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease.svg"><kbd>USER-LEASE.SVG</kbd></a>:

- delegated operator authenticates as `jdoe`
- opens a short lease on `jdoe-autobot`
- retrieves the vaulted password
- performs a real `kinit` and SSH login as `jdoe-autobot`
- destroys the cache and waits for expiry
- shows the post-expiry `kinit` failure

Use the demo page when the question is behavioral. Use the rest of this page
when the question is the playbook shape.

---

## 1. Give a Temporary User a Two-Hour Lease

```yaml
- name: Open a two-hour access window for a temporary user
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Set the principal lease boundary
      eigenstate.ipa.user_lease:
        username: temp-deploy
        principal_expiration: "02:00"
        server: idm-01.example.com
        kerberos_keytab: /etc/ipa/lease-operator.keytab
        ipaadmin_principal: lease-operator
        verify: /etc/ipa/ca.crt
      register: lease_result

    - ansible.builtin.debug:
        msg: "Lease ends at {{ lease_result.lease_end }}"
```

Why this pattern:

- the access window is expressed by IdM, not by a later cleanup task alone
- the relative input makes the lease start at job execution time
- `lease_end` can be passed to downstream audit or notification steps

---

## 2. End Temporary Access Immediately

```yaml
- name: Close the access window now
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Expire both the principal and password path
      eigenstate.ipa.user_lease:
        username: temp-maintenance
        state: expired
        password_expiration_matches_principal: true
        server: idm-01.example.com
        kerberos_keytab: /etc/ipa/lease-operator.keytab
        ipaadmin_principal: lease-operator
        verify: /etc/ipa/ca.crt
```

Why this pattern:

- `state: expired` makes the cutoff explicit instead of relying on cleanup
- matching password expiry closes both auth paths on the same boundary
- later removal of the user or group membership is hygiene, not the main control

---

## 3. Use a Governed Group Boundary

In the delegated model, the automation user only gets rights over users in a
particular group such as `lease-targets`. Add `require_groups` so the play
refuses to mutate a user outside that boundary.

```yaml
- name: Set a lease only for governed users
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Refuse to touch users outside the governed target group
      eigenstate.ipa.user_lease:
        username: temp-build
        principal_expiration: "2026-04-09T18:30:00Z"
        password_expiration_matches_principal: true
        require_groups:
          - lease-targets
        server: idm-01.example.com
        kerberos_keytab: /etc/ipa/lease-operator.keytab
        ipaadmin_principal: lease-operator
        verify: /etc/ipa/ca.crt
```

Why this pattern:

- it keeps the playbook aligned with the delegated RBAC design
- a caller mistake fails fast instead of probing for an authorization error later
- the group boundary is visible in task parameters, not buried in IdM only

---

## 4. Pair the Lease with an HBAC Gate

A temporary user lease is stronger when the workflow also checks whether the
user would actually be allowed onto the target host.

```yaml
- name: Open access only if IdM policy already allows it
  hosts: localhost
  gather_facts: false

  vars:
    lease_user: temp-maintenance
    target_host: bastion-01.workshop.lan

  tasks:
    - name: Confirm HBAC allows the login path
      ansible.builtin.set_fact:
        hbactest_result: >-
          {{ lookup('eigenstate.ipa.hbacrule',
                    operation='test',
                    user=lease_user,
                    host=target_host,
                    service='sshd',
                    server='idm-01.example.com',
                    kerberos_keytab='/etc/ipa/lease-operator.keytab',
                    ipaadmin_principal='lease-operator',
                    verify='/etc/ipa/ca.crt') }}

    - name: Stop if IdM policy already denies the login path
      ansible.builtin.assert:
        that:
          - not hbactest_result.denied
        fail_msg: "HBAC denies {{ lease_user }} on {{ target_host }}"

    - name: Open the temporary access window
      eigenstate.ipa.user_lease:
        username: "{{ lease_user }}"
        principal_expiration: "01:00"
        password_expiration_matches_principal: true
        require_groups:
          - lease-targets
        server: idm-01.example.com
        kerberos_keytab: /etc/ipa/lease-operator.keytab
        ipaadmin_principal: lease-operator
        verify: /etc/ipa/ca.crt
```

Why this pattern:

- it avoids opening a lease window for a login path that IdM policy already blocks
- `user_lease` controls the cutoff, while `hbacrule` answers whether access would work at all
- this is one of the collection’s stronger identity-native combinations

---

## 5. Use It from AAP

AAP is the scheduler and execution boundary here, not the lease engine. IdM is
still what makes the user unusable after the cutoff.

Recommended Controller posture:

- store the delegated operator keytab as a Controller-managed credential file
- mount the keytab into the execution environment
- point `ipaadmin_principal` at the delegated operator user
- let the workflow template schedule the lease-open and cleanup jobs separately

Minimal task shape:

```yaml
- name: Controller task to open a temporary user lease
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Set the lease boundary in IdM
      eigenstate.ipa.user_lease:
        username: temp-release
        principal_expiration: "00:45"
        password_expiration_matches_principal: true
        require_groups:
          - lease-targets
        server: idm-01.workshop.lan
        kerberos_keytab: /runner/env/ipa/lease-operator.keytab
        ipaadmin_principal: lease-operator
        verify: /etc/ipa/ca.crt
```

Why this pattern:

- AAP handles schedule, approval, and reporting
- IdM still owns the actual expiration boundary
- the cleanup job can remove the user or group membership later without being
  the only thing preventing continued access

{% endraw %}

---
layout: default
title: Mutation Surface Migration
description: >-
  Migration examples for moving side-effecting keytab and certificate
  workflows from lookup expressions to explicit module tasks.
---

{% raw %}

# Mutation Surface Migration

Existing lookups remain supported. This guide shows how to move new or revised
automation to explicit module surfaces when the workflow changes IdM state or
writes sensitive artifacts.

## Keytab Retrieval To Disk

Lookup-based shape:

```yaml
- name: Write service keytab from lookup result
  ansible.builtin.copy:
    content: "{{ lookup('eigenstate.ipa.keytab',
                   'HTTP/app.example.com@EXAMPLE.COM',
                   server='idm-01.example.com',
                   kerberos_keytab='/runner/env/ipa/admin.keytab') | b64decode }}"
    dest: /etc/httpd/conf/httpd.keytab
    mode: "0600"
  no_log: true
```

Module shape:

```yaml
- name: Retrieve and write service keytab
  eigenstate.ipa.keytab_manage:
    principal: HTTP/app.example.com@EXAMPLE.COM
    state: retrieved
    destination: /etc/httpd/conf/httpd.keytab
    mode: "0600"
    server: idm-01.example.com
    kerberos_keytab: /runner/env/ipa/admin.keytab
```

The module keeps the keytab payload out of the task result unless
`return_content: true` is set.

## Keytab Rotation

Lookup-based rotation:

```yaml
- name: Rotate service keys through lookup generate mode
  ansible.builtin.set_fact:
    rotated_keytab_b64: "{{ lookup('eigenstate.ipa.keytab',
                              'HTTP/app.example.com@EXAMPLE.COM',
                              retrieve_mode='generate',
                              server='idm-01.example.com',
                              kerberos_keytab='/runner/env/ipa/admin.keytab') }}"
  no_log: true
```

Module shape:

```yaml
- name: Rotate service keytab with explicit confirmation
  eigenstate.ipa.keytab_manage:
    principal: HTTP/app.example.com@EXAMPLE.COM
    state: rotated
    confirm_rotation: true
    destination: /etc/httpd/conf/httpd.keytab
    mode: "0600"
    server: idm-01.example.com
    kerberos_keytab: /runner/env/ipa/admin.keytab
```

The confirmation flag makes the destructive boundary reviewable. Rotation
invalidates existing keytabs for the principal.

## Certificate Request

Lookup-based issuance:

```yaml
- name: Request certificate through lookup
  ansible.builtin.copy:
    content: "{{ lookup('eigenstate.ipa.cert',
                   'HTTP/app.example.com@EXAMPLE.COM',
                   operation='request',
                   csr_file='/etc/pki/tls/certs/app.csr',
                   server='idm-01.example.com',
                   kerberos_keytab='/runner/env/ipa/admin.keytab') }}"
    dest: /etc/pki/tls/certs/app.pem
    mode: "0644"
```

Module shape:

```yaml
- name: Request certificate through module
  eigenstate.ipa.cert_request:
    principal: HTTP/app.example.com@EXAMPLE.COM
    csr_file: /etc/pki/tls/certs/app.csr
    destination: /etc/pki/tls/certs/app.pem
    mode: "0644"
    server: idm-01.example.com
    kerberos_keytab: /runner/env/ipa/admin.keytab
```

The module returns safe certificate metadata by default. Set
`return_content: true` only when a later task needs the certificate body in a
registered variable.

## Recommended Review Questions

- Does the task change IdM state, rotate credentials, or issue a certificate?
- Does the task write a sensitive artifact to disk?
- Would `changed` and check mode make the workflow easier to audit?
- Can the task avoid returning secret-bearing payloads?

If the answer is yes, prefer a module surface.

{% endraw %}

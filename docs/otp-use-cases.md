---
layout: default
title: OTP Use Cases
---

{% raw %}

# OTP Use Cases

Related docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/otp-plugin.html"><kbd>&nbsp;&nbsp;OTP PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/otp-capabilities.html"><kbd>&nbsp;&nbsp;OTP CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>&nbsp;&nbsp;PRINCIPAL USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

## Purpose

This page contains worked examples for `eigenstate.ipa.otp`.

Use the capability guide to choose the right OTP or host-enrollment pattern.
Use this page when you need the corresponding playbook.

## Contents

1. [Provision New User TOTP Token](#1-provision-new-user-totp-token)
2. [Rotate User Token](#2-rotate-user-token)
3. [Enroll a New Host via ansible-freeipa](#3-enroll-a-new-host-via-ansible-freeipa)
4. [Bulk Host Enrollment](#4-bulk-host-enrollment)
5. [Emergency Revoke All Tokens for a User](#5-emergency-revoke-all-tokens-for-a-user)
6. [Pre-flight Token Existence Check Before Rotation](#6-pre-flight-token-existence-check-before-rotation)
7. [AAP Credential Type Injection Pattern](#7-aap-credential-type-injection-pattern)
8. [Cross-Plugin: Principal Check Before Token Issuance](#8-cross-plugin-principal-check-before-token-issuance)

---

## 1. Provision New User TOTP Token

Scenario: a new employee account has been created in IdM. A provisioning play
needs to generate a TOTP seed, archive it in the IdM vault for recovery, and
output the `otpauth://` URI so an operator or downstream task can generate a
QR code.

```yaml
---
- name: Provision TOTP token for new user
  hosts: localhost
  gather_facts: false
  vars:
    ipa_server: idm-01.corp.example.com
    ipa_keytab: /runner/env/ipa/admin.keytab
    ipa_ca: /etc/ipa/ca.crt
    new_username: alice

  tasks:
    - name: Create TOTP token
      ansible.builtin.set_fact:
        totp_record: "{{ query('eigenstate.ipa.otp', new_username,
                          operation='add',
                          token_type='totp',
                          description='Primary 2FA token',
                          result_format='record',
                          server=ipa_server,
                          kerberos_keytab=ipa_keytab,
                          verify=ipa_ca) | first }}"
      no_log: true

    - name: Archive URI in IdM vault for recovery
      ansible.builtin.set_fact:
        # placeholder: use eigenstate.ipa vault write module when available
        _vault_note: "Archive {{ totp_record.token_id }} URI to vault"
      no_log: true

    - name: Record token ID for operator reference
      ansible.builtin.debug:
        msg: "Token ID {{ totp_record.token_id }} issued for {{ new_username }}"
```

Notes:

- `no_log: true` on the `set_fact` task prevents the URI from appearing in
  job output
- the `token_id` is safe to log — it does not contain the secret
- if the user already has a token from a previous run, this will add a second
  one; use the rotation pattern (use case 2) to replace rather than add

---

## 2. Rotate User Token

Scenario: a user has reported that their authenticator app was lost or reset.
The existing token must be revoked and a new one issued.

```yaml
---
- name: Rotate TOTP token for user
  hosts: localhost
  gather_facts: false
  vars:
    ipa_server: idm-01.corp.example.com
    ipa_keytab: /runner/env/ipa/admin.keytab
    ipa_ca: /etc/ipa/ca.crt
    username: alice

  tasks:
    - name: Find existing tokens for user
      ansible.builtin.set_fact:
        existing_tokens: "{{ lookup('eigenstate.ipa.otp',
                              operation='find',
                              owner=username,
                              server=ipa_server,
                              kerberos_keytab=ipa_keytab,
                              verify=ipa_ca) }}"

    - name: Revoke existing tokens
      ansible.builtin.set_fact:
        _revoked: "{{ lookup('eigenstate.ipa.otp', item.token_id,
                      operation='revoke',
                      server=ipa_server,
                      kerberos_keytab=ipa_keytab,
                      verify=ipa_ca) }}"
      loop: "{{ existing_tokens }}"
      when: existing_tokens | length > 0

    - name: Issue replacement token
      ansible.builtin.set_fact:
        new_token: "{{ query('eigenstate.ipa.otp', username,
                        operation='add',
                        token_type='totp',
                        description='Replacement token after device loss',
                        result_format='record',
                        server=ipa_server,
                        kerberos_keytab=ipa_keytab,
                        verify=ipa_ca) | first }}"
      no_log: true

    - name: Confirm rotation
      ansible.builtin.debug:
        msg: >
          Rotated token for {{ username }}.
          Old token count: {{ existing_tokens | length }}.
          New token ID: {{ new_token.token_id }}.
```

Notes:

- revoking before adding ensures the old token cannot be used during the
  window between the old and new token
- if the user had no tokens (`existing_tokens | length == 0`), the revoke
  loop is skipped and a new token is issued directly
- `no_log: true` covers only the `set_fact` task that receives the URI; the
  confirmation debug is safe because `token_id` does not contain the secret

---

## 3. Enroll a New Host via ansible-freeipa

Scenario: a new server has been added to DNS but not yet enrolled in IdM.
The play creates the host record, generates an enrollment password, and runs
`freeipa.ansible_freeipa.ipaclient` on the target host.

```yaml
---
- name: Create IdM host record
  hosts: localhost
  gather_facts: false
  vars:
    ipa_server: idm-01.corp.example.com
    ipa_keytab: /runner/env/ipa/admin.keytab
    ipa_ca: /etc/ipa/ca.crt
    target_fqdn: web-01.corp.example.com

  tasks:
    - name: Add host record to IdM
      freeipa.ansible_freeipa.ipahost:
        ipaadmin_keytab: "{{ ipa_keytab }}"
        ipaadmin_principal: admin
        name: "{{ target_fqdn }}"
        state: present

    - name: Generate enrollment password
      ansible.builtin.set_fact:
        enroll_pass: "{{ lookup('eigenstate.ipa.otp', target_fqdn,
                          token_type='host',
                          server=ipa_server,
                          kerberos_keytab=ipa_keytab,
                          verify=ipa_ca) | first }}"
      no_log: true

- name: Enroll host
  hosts: web-01.corp.example.com
  gather_facts: false
  vars:
    ipa_server: idm-01.corp.example.com
    ipa_ca: /etc/ipa/ca.crt

  tasks:
    - name: Run ipa-client-install via ansible-freeipa
      freeipa.ansible_freeipa.ipaclient:
        servers: "{{ ipa_server }}"
        domain: corp.example.com
        realm: CORP.EXAMPLE.COM
        ipaadmin_password: "{{ hostvars['localhost']['enroll_pass'] }}"
        ca_cert_file: "{{ ipa_ca }}"
        state: present
      no_log: true
```

Notes:

- the `ipahost` task (play 1) creates the IdM record; `otp add token_type=host`
  (also play 1) sets the enrollment password on it
- `ipaclient` (play 2) uses the password and consumes it; the host is enrolled
  after this task completes
- `hostvars['localhost']['enroll_pass']` passes the credential from the
  controller play to the target host play
- both `set_fact` and `ipaclient` tasks use `no_log: true`

---

## 4. Bulk Host Enrollment

Scenario: a staging environment refresh needs 10 new hosts enrolled in IdM.
All host records were pre-created. Generate passwords for all of them in one
pass and enroll concurrently.

```yaml
---
- name: Generate enrollment passwords for all new hosts
  hosts: localhost
  gather_facts: false
  vars:
    ipa_server: idm-01.corp.example.com
    ipa_keytab: /runner/env/ipa/admin.keytab
    ipa_ca: /etc/ipa/ca.crt

  tasks:
    - name: Generate enrollment passwords
      ansible.builtin.set_fact:
        enroll_map: "{{ query('eigenstate.ipa.otp',
                         *groups['new_hosts'],
                         token_type='host',
                         result_format='map',
                         server=ipa_server,
                          kerberos_keytab=ipa_keytab,
                         verify=ipa_ca) | first }}"
      no_log: true

- name: Enroll all new hosts
  hosts: new_hosts
  gather_facts: false
  vars:
    ipa_server: idm-01.corp.example.com
    ipa_ca: /etc/ipa/ca.crt

  tasks:
    - name: Run ipa-client-install
      freeipa.ansible_freeipa.ipaclient:
        servers: "{{ ipa_server }}"
        domain: corp.example.com
        realm: CORP.EXAMPLE.COM
        ipaadmin_password: "{{ hostvars['localhost']['enroll_map'][inventory_hostname] }}"
        ca_cert_file: "{{ ipa_ca }}"
        state: present
      no_log: true
```

Notes:

- `*groups['new_hosts']` unpacks the group member list as positional terms
- `result_format='map'` returns `{fqdn: password}`, which is indexed by
  `inventory_hostname` in the enrollment play
- `forks` on the `new_hosts` play controls enrollment concurrency
- all host records must exist in IdM before the password generation task runs

---

## 5. Emergency Revoke All Tokens for a User

Scenario: a user's device has been reported stolen. All their OTP tokens must
be revoked immediately to prevent unauthorized authentication.

```yaml
---
- name: Emergency token revocation
  hosts: localhost
  gather_facts: false
  vars:
    ipa_server: idm-01.corp.example.com
    ipa_keytab: /runner/env/ipa/admin.keytab
    ipa_ca: /etc/ipa/ca.crt
    target_user: alice

  tasks:
    - name: Find all tokens for user
      ansible.builtin.set_fact:
        tokens_to_revoke: "{{ lookup('eigenstate.ipa.otp',
                               operation='find',
                               owner=target_user,
                               server=ipa_server,
                               kerberos_keytab=ipa_keytab,
                               verify=ipa_ca) }}"

    - name: Fail if no tokens found (may indicate wrong username)
      ansible.builtin.fail:
        msg: "No OTP tokens found for '{{ target_user }}'. Verify the username."
      when: tokens_to_revoke | length == 0

    - name: Revoke all tokens
      ansible.builtin.set_fact:
        _revoked: "{{ lookup('eigenstate.ipa.otp', item.token_id,
                      operation='revoke',
                      server=ipa_server,
                      kerberos_keytab=ipa_keytab,
                      verify=ipa_ca) }}"
      loop: "{{ tokens_to_revoke }}"

    - name: Confirm revocation
      ansible.builtin.debug:
        msg: "Revoked {{ tokens_to_revoke | length }} token(s) for {{ target_user }}"
```

Notes:

- the failure on empty token list is intentional — an empty result may mean
  the username was mistyped, and it is important to surface that rather than
  silently succeeding
- the revoke loop will raise an error if any token ID disappears between the
  find and revoke steps (race with another operator); this is expected
  behavior — revoke is non-idempotent by design
- after revocation, the user must request a new token before they can
  authenticate with OTP policies

---

## 6. Pre-flight Token Existence Check Before Rotation

Scenario: a scheduled token rotation play may run multiple times. Use
`operation=show` to check whether the target token still exists before
attempting to revoke it, so the play is safely re-entrant.

```yaml
---
- name: Idempotent token rotation
  hosts: localhost
  gather_facts: false
  vars:
    ipa_server: idm-01.corp.example.com
    ipa_keytab: /runner/env/ipa/admin.keytab
    ipa_ca: /etc/ipa/ca.crt
    username: bob
    old_token_id: tok-abc123

  tasks:
    - name: Check whether old token still exists
      ansible.builtin.set_fact:
        old_state: "{{ lookup('eigenstate.ipa.otp', old_token_id,
                        operation='show',
                        server=ipa_server,
                        kerberos_keytab=ipa_keytab,
                        verify=ipa_ca) | first }}"

    - name: Revoke old token if it still exists
      ansible.builtin.set_fact:
        _revoked: "{{ lookup('eigenstate.ipa.otp', old_token_id,
                      operation='revoke',
                      server=ipa_server,
                      kerberos_keytab=ipa_keytab,
                      verify=ipa_ca) }}"
      when: old_state.exists

    - name: Issue new token
      ansible.builtin.set_fact:
        new_token: "{{ query('eigenstate.ipa.otp', username,
                        operation='add',
                        token_type='totp',
                        result_format='record',
                        server=ipa_server,
                        kerberos_keytab=ipa_keytab,
                        verify=ipa_ca) | first }}"
      no_log: true

    - name: Record new token ID
      ansible.builtin.debug:
        msg: "New token ID for {{ username }}: {{ new_token.token_id }}"
```

Notes:

- `operation=show` returns `exists=false` for a missing token — no
  `ignore_errors` needed
- the `when: old_state.exists` guard makes the revoke step a no-op on
  subsequent runs after the token has already been removed
- the `add` step always creates a new token regardless of whether the old
  one existed

---

## 7. AAP Credential Type Injection Pattern

Scenario: an Ansible Automation Platform job template needs to enroll a host
on each run. Rather than storing a static enrollment password in AAP, generate
a fresh one at job launch using a custom credential type.

**Custom credential type definition (AAP UI or API):**

Input fields:

```yaml
fields:
  - id: ipa_server
    type: string
    label: IPA Server
  - id: ipa_keytab_path
    type: string
    label: Keytab Path (on EE)
  - id: ipa_ca_cert
    type: string
    label: CA Certificate Path (on EE)
  - id: target_fqdn
    type: string
    label: Target Host FQDN
required:
  - ipa_server
  - ipa_keytab_path
  - target_fqdn
```

Injector template:

```yaml
extra_vars:
  ipa_server: "{{ ipa_server }}"
  ipa_keytab: "{{ ipa_keytab_path }}"
  ipa_ca: "{{ ipa_ca_cert | default('/etc/ipa/ca.crt') }}"
  enroll_target_fqdn: "{{ target_fqdn }}"
```

**Playbook that consumes the injected vars:**

```yaml
---
- name: Enroll host using AAP-injected credentials
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Generate enrollment password at runtime
      ansible.builtin.set_fact:
        enroll_pass: "{{ lookup('eigenstate.ipa.otp', enroll_target_fqdn,
                          token_type='host',
                          server=ipa_server,
                          kerberos_keytab=ipa_keytab,
                          verify=ipa_ca) | first }}"
      no_log: true

- name: Run enrollment on target host
  hosts: "{{ enroll_target_fqdn }}"
  gather_facts: false

  tasks:
    - name: Enroll with ansible-freeipa
      freeipa.ansible_freeipa.ipaclient:
        servers: "{{ ipa_server }}"
        domain: "{{ enroll_target_fqdn.split('.', 1)[1] }}"
        realm: "{{ enroll_target_fqdn.split('.', 1)[1] | upper }}"
        ipaadmin_password: "{{ hostvars['localhost']['enroll_pass'] }}"
        state: present
      no_log: true
```

Notes:

- the enrollment password is generated fresh per job run — it is never stored
  in AAP's credential vault or the playbook itself
- the custom credential type stores the keytab path on the execution
  environment; the EE image must have the keytab baked in or mounted
- `no_log: true` on both `set_fact` and `ipaclient` prevents the password
  from appearing in AAP job output

---

## 8. Cross-Plugin: Principal Check Before Token Issuance

Scenario: a provisioning play issues TOTP tokens for a list of users. Some
users may have been deprovisioned or never fully enrolled. Use
`eigenstate.ipa.principal` to gate token issuance on IdM principal existence.

```yaml
---
- name: Issue TOTP tokens only for enrolled users
  hosts: localhost
  gather_facts: false
  vars:
    ipa_server: idm-01.corp.example.com
    ipa_keytab: /runner/env/ipa/admin.keytab
    ipa_ca: /etc/ipa/ca.crt
    candidate_users:
      - alice
      - bob
      - charlie     # may not exist in IdM

  tasks:
    - name: Check principal state for all candidates
      ansible.builtin.set_fact:
        principal_states: "{{ query('eigenstate.ipa.principal',
                               *candidate_users,
                               result_format='map_record',
                               server=ipa_server,
                               kerberos_keytab=ipa_keytab,
                               verify=ipa_ca) | first }}"

    - name: Build enrolled user list
      ansible.builtin.set_fact:
        enrolled_users: "{{ candidate_users | select('in', principal_states)
                            | selectattr('__dummy__', 'undefined')
                            | list
                            | map('extract', principal_states)
                            | selectattr('exists')
                            | map(attribute='name')
                            | list }}"
      vars:
        # simpler inline form
        enrolled_users: "{{ candidate_users
                            | select('in', principal_states)
                            | map('extract', principal_states)
                            | selectattr('exists')
                            | map(attribute='name')
                            | list }}"

    - name: Warn about unknown users
      ansible.builtin.debug:
        msg: "User '{{ item }}' not found in IdM — skipping token issuance"
      loop: "{{ candidate_users | difference(enrolled_users) }}"

    - name: Issue TOTP tokens for enrolled users
      ansible.builtin.set_fact:
        new_tokens: "{{ query('eigenstate.ipa.otp',
                         *enrolled_users,
                         operation='add',
                         token_type='totp',
                         result_format='map_record',
                         server=ipa_server,
                          kerberos_keytab=ipa_keytab,
                         verify=ipa_ca) | first }}"
      no_log: true
      when: enrolled_users | length > 0

    - name: Log token IDs (safe — no secrets)
      ansible.builtin.debug:
        msg: "Token {{ item.value.token_id }} issued for {{ item.key }}"
      loop: "{{ new_tokens | dict2items }}"
      when: new_tokens is defined
```

Notes:

- `eigenstate.ipa.principal` with `result_format=map_record` returns a
  dictionary keyed by principal name — filtering by `exists` eliminates
  unknown users before any OTP calls are made
- the OTP `add` call only runs against confirmed principals, so no
  `NotFound` errors from ipalib are expected
- `no_log: true` covers only the task receiving URIs; the token ID debug loop
  is safe
- `*enrolled_users` unpacks the filtered list as positional terms to the OTP
  lookup
- when a later task reuses `token_id` from a prior lookup result as an input
  term, use `| string` to force a plain text token ID in the Jinja layer

{% endraw %}

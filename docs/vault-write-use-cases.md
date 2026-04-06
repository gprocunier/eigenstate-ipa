---
layout: default
title: IdM Vault Write Use Cases
---

{% raw %}

# IdM Vault Write Use Cases

Nearby docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-plugin.html"><kbd>&nbsp;&nbsp;VAULT WRITE PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-write-capabilities.html"><kbd>&nbsp;&nbsp;VAULT WRITE CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/vault-use-cases.html"><kbd>&nbsp;&nbsp;IDM VAULT USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

## Contents

- [1. Create a Standard Vault](#1-create-a-standard-vault)
- [2. Archive a Static Secret](#2-archive-a-static-secret)
- [3. Rotate a Secret In Place](#3-rotate-a-secret-in-place)
- [4. Delete a Vault](#4-delete-a-vault)
- [5. Add a Service Account as a Vault Member](#5-add-a-service-account-as-a-vault-member)
- [6. Bootstrap Credential for a New Host](#6-bootstrap-credential-for-a-new-host)
- [7. Archive a Private Key After Certificate Issuance](#7-archive-a-private-key-after-certificate-issuance)
- [8. Idempotent Secret Provisioning in a Role](#8-idempotent-secret-provisioning-in-a-role)
- [9. Symmetric Vault Creation and Password Rotation](#9-symmetric-vault-creation-and-password-rotation)
- [10. Check-Mode Pre-Flight for Rotation Automation](#10-check-mode-pre-flight-for-rotation-automation)

---

## 1. Create a Standard Vault

Create a shared standard vault that will hold an automation secret. The
vault is empty after creation. A subsequent archive task populates it.

```yaml
- name: Ensure rotation-target vault exists
  eigenstate.ipa.vault_write:
    name: rotation-target
    state: present
    shared: true
    description: "Database credential targeted for rotation automation"
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/automation.keytab
    ipaadmin_principal: automation@EXAMPLE.COM
    verify: /etc/ipa/ca.crt
  register: vault_create

- ansible.builtin.debug:
    msg: "Vault created: {{ vault_create.changed }}"
```

Why this pattern:

- separates vault provisioning from secret archival so the two steps can
  run in different plays or pipelines
- the `state: present` step is idempotent: re-running the play when the
  vault already exists makes no change
- using `kerberos_keytab` instead of a password is preferred for AAP
  Execution Environments where interactive auth is not available

---

## 2. Archive a Static Secret

Store a known static credential into an existing vault. Useful for
bootstrapping a vault with its initial value.

```yaml
- name: Archive initial database password
  eigenstate.ipa.vault_write:
    name: db-password
    state: archived
    shared: true
    data: "{{ initial_db_password }}"
    server: idm-01.example.com
    ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
    verify: /etc/ipa/ca.crt
  no_log: true
```

For a file-based payload:

```yaml
- name: Archive configuration blob from file
  eigenstate.ipa.vault_write:
    name: app-config-blob
    state: archived
    shared: true
    data_file: /runner/env/secrets/app-config.json
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/automation.keytab
    ipaadmin_principal: automation@EXAMPLE.COM
```

Why this pattern:

- `state: archived` creates the vault if it does not exist, then archives
  the payload — a single task replaces the create + archive two-step when
  the vault properties do not need to be pre-configured
- for standard vaults, repeated runs with the same payload produce no
  change (`changed: false`)
- `no_log: true` prevents the payload from appearing in job output when
  using the inline `data` parameter

---

## 3. Rotate a Secret In Place

Retrieve the current credential, generate a replacement, archive the new
value, and notify consumers. This is the primary operational use case for
the vault write module.

```yaml
- name: Rotate app-secret
  hosts: localhost
  gather_facts: false

  vars:
    ipa_server: idm-01.example.com
    ipa_keytab: /etc/ipa/automation.keytab
    ipa_principal: automation@EXAMPLE.COM

  tasks:
    - name: Retrieve current secret
      ansible.builtin.set_fact:
        current_secret: >-
          {{ lookup('eigenstate.ipa.vault', 'app-secret',
                    server=ipa_server,
                    kerberos_keytab=ipa_keytab,
                    ipaadmin_principal=ipa_principal,
                    shared=true,
                    verify='/etc/ipa/ca.crt') }}
      no_log: true

    - name: Generate new 32-character secret
      ansible.builtin.set_fact:
        new_secret: "{{ lookup('community.general.random_string',
                               length=32, special=false) }}"
      no_log: true

    - name: Archive rotated secret
      eigenstate.ipa.vault_write:
        name: app-secret
        state: archived
        shared: true
        data: "{{ new_secret }}"
        server: "{{ ipa_server }}"
        kerberos_keytab: "{{ ipa_keytab }}"
        ipaadmin_principal: "{{ ipa_principal }}"
        verify: /etc/ipa/ca.crt
      no_log: true
      register: rotation_result

    - name: Report outcome
      ansible.builtin.debug:
        msg: >-
          Rotation {{ 'completed' if rotation_result.changed else 'skipped (no change)' }}
```

Why this pattern:

- the retrieve step lets the automation record the previous value for
  rollback or audit before overwriting
- the module compares the new payload to the current payload for standard
  vaults; if the generator produces the same value the archive is skipped
- `check_mode: true` on the archive task previews the change before running
  the full rotation in production (see use case 10)

---

## 4. Delete a Vault

Remove a vault when it is no longer needed. The `state: absent` step is
idempotent: re-running the play when the vault is already gone makes no
change.

```yaml
- name: Decommission service credential vault
  eigenstate.ipa.vault_write:
    name: old-service-credential
    state: absent
    shared: true
    server: idm-01.example.com
    ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
    verify: /etc/ipa/ca.crt
  register: vault_delete

- ansible.builtin.debug:
    msg: >-
      {{ 'Vault deleted' if vault_delete.changed else 'Vault was already absent' }}
```

> [!CAUTION]
> Vault deletion is not recoverable. If the vault contains active secrets,
> retrieve and store them in another location before running `state: absent`.
> Confirm the vault name and scope before executing a deletion play in
> production.

---

## 5. Add a Service Account as a Vault Member

Grant a service principal read access to an existing vault by adding it as
a vault member. The module uses delta-only reconciliation: it only makes the
API call if the principal is not already a member.

```yaml
- name: Grant automation service account access to app-secret vault
  eigenstate.ipa.vault_write:
    name: app-secret
    state: present
    shared: true
    members:
      - HTTP/automation.example.com@EXAMPLE.COM
    server: idm-01.example.com
    ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
    verify: /etc/ipa/ca.crt

- name: Remove a decommissioned service account from vault membership
  eigenstate.ipa.vault_write:
    name: app-secret
    state: present
    shared: true
    members_absent:
      - HTTP/old-automation.example.com@EXAMPLE.COM
    server: idm-01.example.com
    ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
    verify: /etc/ipa/ca.crt
```

Why this pattern:

- `state: present` with `members` or `members_absent` combines vault
  existence enforcement with membership reconciliation in a single task
- both operations are idempotent — adding an existing member or removing a
  non-member produces no change
- use this pattern in roles that provision per-service secret access

---

## 6. Bootstrap Credential for a New Host

When a new host is enrolled into IdM, provision its bootstrap credential in
a single play: create the vault, archive the initial credential, and grant
access to the host's service principal.

```yaml
- name: Bootstrap host credential
  hosts: localhost
  gather_facts: false

  vars:
    host: appserv-01.example.com
    ipa_server: idm-01.example.com
    ipa_keytab: /etc/ipa/automation.keytab
    ipa_principal: automation@EXAMPLE.COM

  tasks:
    - name: Generate bootstrap token
      ansible.builtin.set_fact:
        bootstrap_token: "{{ lookup('community.general.random_string',
                                    length=24, special=false) }}"
      no_log: true

    - name: Create and populate bootstrap vault
      eigenstate.ipa.vault_write:
        name: "bootstrap-{{ host }}"
        state: archived
        shared: true
        data: "{{ bootstrap_token }}"
        description: "Bootstrap credential for {{ host }}"
        members:
          - "host/{{ host }}@EXAMPLE.COM"
        server: "{{ ipa_server }}"
        kerberos_keytab: "{{ ipa_keytab }}"
        ipaadmin_principal: "{{ ipa_principal }}"
        verify: /etc/ipa/ca.crt
      no_log: true
      register: bootstrap_result

    - name: Confirm vault ready
      ansible.builtin.assert:
        that:
          - bootstrap_result.vault.name == "bootstrap-" ~ host
          - bootstrap_result.vault.scope == "shared"
        fail_msg: "Bootstrap vault not in expected state"
```

Why this pattern:

- `state: archived` creates the vault and archives the credential in one
  task; the `members` parameter grants the host access in the same call
- each vault is host-scoped by name, keeping bootstrap credentials
  isolated per host
- the vault persists after first retrieval; the consuming host deletes or
  rotates the credential after consuming it

---

## 7. Archive a Private Key After Certificate Issuance

After requesting a certificate via `eigenstate.ipa.cert`, the private key
is temporarily on the controller. Archive it into IdM immediately so the
controller does not hold it as a long-term secret.

```yaml
- name: Request certificate
  eigenstate.ipa.cert:
    operation: request
    principal: "HTTP/app01.example.com"
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/automation.keytab
    ipaadmin_principal: automation@EXAMPLE.COM
    verify: /etc/ipa/ca.crt
  register: cert_result

- name: Ensure private key vault exists
  eigenstate.ipa.vault_write:
    name: "tls-key-app01"
    state: present
    shared: true
    description: "TLS private key for app01 — archived after issuance"
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/automation.keytab
    ipaadmin_principal: automation@EXAMPLE.COM
    verify: /etc/ipa/ca.crt

- name: Archive private key into vault
  eigenstate.ipa.vault_write:
    name: "tls-key-app01"
    state: archived
    shared: true
    data_file: "/tmp/app01-private.key"
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/automation.keytab
    ipaadmin_principal: automation@EXAMPLE.COM
    verify: /etc/ipa/ca.crt
  no_log: true

- name: Remove private key from controller
  ansible.builtin.file:
    path: /tmp/app01-private.key
    state: absent
```

Why this pattern:

- the vault becomes the durable private key store; the controller holds the
  key only transiently during the issuance/archive window
- the private key can be retrieved later via the vault lookup plugin without
  ever hitting the controller disk again
- this closes the private key lifecycle gap documented in the cert plugin
  use cases

---

## 8. Idempotent Secret Provisioning in a Role

Roles that provision secrets should be safe to run repeatedly. Use
`state: archived` with a standard vault to get the full idempotency
guarantee: the role creates the vault on first run and only archives again
if the payload changes.

```yaml
# roles/app_secrets/tasks/main.yml

- name: Ensure app credentials vault exists and is populated
  eigenstate.ipa.vault_write:
    name: "{{ app_name }}-credentials"
    state: archived
    shared: "{{ vault_shared | default(true) }}"
    data: "{{ app_credentials | to_json }}"
    description: "Credentials for {{ app_name }}"
    server: "{{ ipa_server }}"
    kerberos_keytab: "{{ ipa_keytab }}"
    ipaadmin_principal: "{{ ipa_principal }}"
    verify: "{{ ipa_verify | default('/etc/ipa/ca.crt') }}"
  no_log: true
  register: credentials_vault

- name: Grant app service account access
  eigenstate.ipa.vault_write:
    name: "{{ app_name }}-credentials"
    state: present
    shared: "{{ vault_shared | default(true) }}"
    members: "{{ app_service_accounts | default([]) }}"
    server: "{{ ipa_server }}"
    kerberos_keytab: "{{ ipa_keytab }}"
    ipaadmin_principal: "{{ ipa_principal }}"
    verify: "{{ ipa_verify | default('/etc/ipa/ca.crt') }}"
  when: app_service_accounts | default([]) | length > 0
```

Why this pattern:

- `state: archived` with a standard vault only writes when the payload
  differs from the current content — re-running the role with the same
  credentials produces `changed: false`
- separating the archive step from the member-grant step makes the role
  composable: callers can omit `app_service_accounts` to skip membership
  management without affecting credential storage
- JSON-encoding the credentials dict keeps multi-field secrets in a single
  vault and the vault lookup plugin can return them as structured data with
  `decode_json=true`

---

## 9. Symmetric Vault Creation and Password Rotation

Create a symmetric vault and rotate the symmetric encryption password. The
password rotation requires delete-and-recreate because IdM does not expose
a vault salt update operation. Data must be re-archived after the password
changes.

```yaml
- name: Provision symmetric vault
  hosts: localhost
  gather_facts: false

  vars:
    vault_name: encrypted-api-key
    ipa_server: idm-01.example.com
    ipa_keytab: /etc/ipa/automation.keytab
    ipa_principal: automation@EXAMPLE.COM

  tasks:
    - name: Create symmetric vault
      eigenstate.ipa.vault_write:
        name: "{{ vault_name }}"
        state: present
        vault_type: symmetric
        shared: true
        description: "API key with symmetric encryption"
        server: "{{ ipa_server }}"
        kerberos_keytab: "{{ ipa_keytab }}"
        ipaadmin_principal: "{{ ipa_principal }}"
        verify: /etc/ipa/ca.crt

    - name: Archive API key with current vault password
      eigenstate.ipa.vault_write:
        name: "{{ vault_name }}"
        state: archived
        shared: true
        data: "{{ api_key_value }}"
        vault_password: "{{ vault_password_current }}"
        server: "{{ ipa_server }}"
        kerberos_keytab: "{{ ipa_keytab }}"
        ipaadmin_principal: "{{ ipa_principal }}"
        verify: /etc/ipa/ca.crt
      no_log: true
```

Password rotation for a symmetric vault:

```yaml
# Password rotation requires delete → recreate → archive
# because IdM has no vault_mod_password operation.

- name: Delete symmetric vault before password rotation
  eigenstate.ipa.vault_write:
    name: "{{ vault_name }}"
    state: absent
    shared: true
    server: "{{ ipa_server }}"
    kerberos_keytab: "{{ ipa_keytab }}"
    ipaadmin_principal: "{{ ipa_principal }}"
    verify: /etc/ipa/ca.crt

- name: Recreate symmetric vault with new salt
  eigenstate.ipa.vault_write:
    name: "{{ vault_name }}"
    state: present
    vault_type: symmetric
    shared: true
    description: "API key with symmetric encryption (rotated)"
    server: "{{ ipa_server }}"
    kerberos_keytab: "{{ ipa_keytab }}"
    ipaadmin_principal: "{{ ipa_principal }}"
    verify: /etc/ipa/ca.crt

- name: Archive data with new vault password
  eigenstate.ipa.vault_write:
    name: "{{ vault_name }}"
    state: archived
    shared: true
    data: "{{ api_key_value }}"
    vault_password: "{{ vault_password_new }}"
    server: "{{ ipa_server }}"
    kerberos_keytab: "{{ ipa_keytab }}"
    ipaadmin_principal: "{{ ipa_principal }}"
    verify: /etc/ipa/ca.crt
  no_log: true
```

> [!NOTE]
> Symmetric vault password rotation is destructive: the vault is deleted and
> recreated with a new salt, then the data is re-archived under the new
> password. This is a write-window where the vault is briefly absent. Run
> this during a maintenance window or against a non-production vault first.
> The consuming automation must also update its vault password source before
> running the next retrieval.

---

## 10. Check-Mode Pre-Flight for Rotation Automation

Run the rotation play in check mode before execution to confirm what would
change. This is especially useful in CI gates and change management workflows
where a rotation job requires a pre-approval diff.

```yaml
- name: Pre-flight check for secret rotation
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Generate candidate secret
      ansible.builtin.set_fact:
        candidate_secret: "{{ lookup('community.general.random_string',
                                     length=32, special=false) }}"
      no_log: true

    - name: Check what rotation would do (no writes)
      eigenstate.ipa.vault_write:
        name: app-secret
        state: archived
        shared: true
        data: "{{ candidate_secret }}"
        server: idm-01.example.com
        kerberos_keytab: /etc/ipa/automation.keytab
        ipaadmin_principal: automation@EXAMPLE.COM
        verify: /etc/ipa/ca.crt
      check_mode: true
      register: rotation_preview
      no_log: true

    - name: Report rotation impact
      ansible.builtin.debug:
        msg: >-
          Rotation would {{ 'update' if rotation_preview.changed else 'make no change to' }}
          vault 'app-secret' (scope: {{ rotation_preview.vault.scope }},
          type: {{ rotation_preview.vault.type }})
```

Why this pattern:

- the check-mode run reads the current vault state from IdM but makes no
  changes
- `rotation_preview.changed` is `true` if the archive step would have
  executed, `false` if the payload is identical to the current content
- the vault field in the return value reflects the projected post-rotation
  state, which is useful for downstream gate assertions
- integrate this as a `--check` pre-run in a CI pipeline before the actual
  rotation job is approved and dispatched

{% endraw %}

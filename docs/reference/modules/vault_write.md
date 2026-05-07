---
layout: default
title: eigenstate.ipa.vault_write module reference
diataxis: reference
diataxis_type: reference
audience: Operators and maintainers looking up exact facts
outcome: Exact source-verified reference for this Ansible collection surface.
authority_boundary:
  - collection
workflow_boundary: mutating
evidence_shape:
  - ansible-doc
public_status: rewritten
source_material:
  - ../../plugins/modules/vault_write.py
last_verified: 2026-05-07
---
{% raw %}

# `eigenstate.ipa.vault_write` module reference

Create, archive, modify, and delete FreeIPA/IdM vaults

## Synopsis

Manages FreeIPA/IdM vault lifecycle, including creating vaults, archiving secrets, updating membership, and deleting vaults.

Complements the C(eigenstate.ipa.vault) lookup plugin, which handles secret retrieval.

Supports standard, symmetric, and asymmetric vault types.

Fully idempotent; repeated runs with the same parameters produce no additional changes.

Supports Ansible check mode.

## Requirements

- See the authentication and runtime notes below.

## Authentication

- Authentication follows the options documented for this surface.

## Options

| Option | Type | Required | Default | Choices | Notes |
| --- | --- | --- | --- | --- | --- |
| `data` | str | no |  |  | Secret payload to archive. Required when C(state=archived) and C(data_file) is not set. Mutually exclusive with C(data_file). |
| `data_file` | path | no |  |  | Path to a file whose contents will be archived as the secret payload. Mutually exclusive with C(data). |
| `description` | str | no |  |  | Human-readable description for the vault. |
| `ipaadmin_password` | str | no |  |  | Password for the principal. Used to obtain a Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket already exists. |
| `ipaadmin_principal` | str | no | admin |  | Kerberos principal to authenticate as. |
| `kerberos_keytab` | str | no |  |  | Path to a Kerberos keytab file. Takes precedence over C(ipaadmin_password). Required for non-interactive use in AAP Execution Environments. |
| `members` | list | no |  |  | List of users, groups, or service principals to ensure are vault members. Delta-only — only adds members not already present. |
| `members_absent` | list | no |  |  | List of users, groups, or service principals to ensure are not vault members. Delta-only — only removes members currently present. |
| `name` | str | yes |  |  | Name of the vault. |
| `server` | str | yes |  |  | FQDN of the IPA server. |
| `service` | str | no |  |  | Service vault scope — the vault is owned by this service principal. Mutually exclusive with C(username) and C(shared). |
| `shared` | bool | no | false |  | Shared vault scope. Mutually exclusive with C(username) and C(service). |
| `state` | str | no | present | present, absent, archived | C(present) ensures the vault exists. Creates it if absent; updates C(description) or C(vault_type) if changed. C(absent) removes the vault. A no-op if the vault does not exist. C(archived) ensures the vault exists and then stores the payload in it. For standard vaults, the current payload is retrieved and compared; the archive step is skipped when the payload is identical. For symmetric and asymmetric vaults, the payload is always archived because comparison would require re-encryption. |
| `username` | str | no |  |  | User vault scope — the vault is owned by this user. Mutually exclusive with C(service) and C(shared). |
| `vault_password` | str | no |  |  | Password for a symmetric vault. Required when creating or archiving a C(vault_type=symmetric) vault. Mutually exclusive with C(vault_password_file). |
| `vault_password_file` | path | no |  |  | Path to a file containing the symmetric vault password. Mutually exclusive with C(vault_password). |
| `vault_public_key` | str | no |  |  | RSA public key (PEM format) for an asymmetric vault. Required when C(vault_type=asymmetric) and the vault is being created. Mutually exclusive with C(vault_public_key_file). |
| `vault_public_key_file` | path | no |  |  | Path to a file containing the RSA public key (PEM format) for an asymmetric vault. Mutually exclusive with C(vault_public_key). |
| `vault_type` | str | no | standard | standard, symmetric, asymmetric | Vault encryption type. Used when creating the vault and validated when the vault already exists. The module fails if the existing vault type does not match this value because changing vault type in place is not supported. |
| `verify` | str | no |  |  | Path to the IPA CA certificate for TLS verification. Auto-detected from C(/etc/ipa/ca.crt) when not set. If neither is available, the module fails unless C(verify) is set to C(false) explicitly. |

## Notes

- Requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible controller.
- RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)
- Sensitive files (C(kerberos_keytab), C(vault_password_file)) should have mode C(0600) or more restrictive.
- Changing the vault type of an existing vault is not supported. Delete and recreate the vault to change its type. Existing vaults fail closed when C(vault_type) does not match the IdM record.
- For symmetric vaults, C(vault_password) or C(vault_password_file) is required when creating or archiving the vault.
- For asymmetric vaults, C(vault_public_key) or C(vault_public_key_file) is required at creation time.

## Return Values

| Field | Type | Returned | Notes |
| --- | --- | --- | --- |
| `changed` | bool | always | Whether the module made any changes. |
| `vault` | dict | when state is present or archived | Current state of the vault after the operation. |

## Examples

```yaml
# Create a standard shared vault
- name: Ensure rotation-target vault exists
  eigenstate.ipa.vault_write:
    name: rotation-target
    state: present
    shared: true
    description: "Credential targeted for rotation automation"
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/automation.keytab
    ipaadmin_principal: automation@EXAMPLE.COM

# Archive a secret into a standard vault
- name: Archive new database password
  eigenstate.ipa.vault_write:
    name: db-password
    state: archived
    shared: true
    data: "{{ new_db_password }}"
    server: idm-01.example.com
    ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"

# Rotation pattern: retrieve, generate, archive
- name: Retrieve current secret
  ansible.builtin.set_fact:
    current_secret: >-
      {{ lookup('eigenstate.ipa.vault', 'app-secret',
                server='idm-01.example.com',
                shared=true,
                ipaadmin_password=ipa_password) }}

- name: Generate new secret
  ansible.builtin.set_fact:
    new_secret: "{{ lookup('community.general.random_string', length=32) }}"

- name: Archive rotated secret
  eigenstate.ipa.vault_write:
    name: app-secret
    state: archived
    shared: true
    data: "{{ new_secret }}"
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"

# Create a symmetric vault and archive a secret with a password
- name: Create symmetric vault
  eigenstate.ipa.vault_write:
    name: encrypted-secret
    state: present
    vault_type: symmetric
    shared: true
    vault_password: "{{ vault_encryption_password }}"
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"

- name: Archive into symmetric vault
  eigenstate.ipa.vault_write:
    name: encrypted-secret
    state: archived
    shared: true
    data: "{{ sensitive_value }}"
    vault_password: "{{ vault_encryption_password }}"
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"

# Create an asymmetric vault
- name: Create asymmetric vault for sealed artifact
  eigenstate.ipa.vault_write:
    name: cert-private-key
    state: present
    vault_type: asymmetric
    vault_public_key_file: /etc/pki/ipa/automation-public.pem
    shared: true
    description: "Private key sealed after certificate issuance"
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/automation.keytab
    ipaadmin_principal: automation@EXAMPLE.COM

# Add a service account as a vault member
- name: Grant app-server read access to vault
  eigenstate.ipa.vault_write:
    name: app-secret
    state: present
    shared: true
    members:
      - app-server/app01.example.com@EXAMPLE.COM
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"

# Delete a vault (decommission)
- name: Remove decommissioned vault
  eigenstate.ipa.vault_write:
    name: old-service-credential
    state: absent
    shared: true
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"

# Check mode — preview what would change
- name: Check rotation would update the secret
  eigenstate.ipa.vault_write:
    name: app-secret
    state: archived
    shared: true
    data: "{{ candidate_secret }}"
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"
  check_mode: true
  register: rotation_preview
```

## Error Behavior

Module failures return through normal Ansible module failure handling. Use check mode where supported before mutating IdM, keytab, certificate, or filesystem state.

## Related Pages

- [Authentication reference](/reference/authentication.html)
- [Return shapes](/reference/return-shapes.html)
- [Authority boundaries](/explanation/authority-boundaries.html)

{% endraw %}

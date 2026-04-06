# -*- coding: utf-8 -*-

# Authors:
#   Greg Procunier
#
# Copyright (C) 2026 Red Hat
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r"""
---
module: vault_write
version_added: "1.5.0"
short_description: Create, archive, modify, and delete FreeIPA/IdM vaults
description:
  - >-
    Manages FreeIPA/IdM vault lifecycle, including creating vaults,
    archiving secrets, updating membership, and deleting vaults.
  - >-
    Complements the C(eigenstate.ipa.vault) lookup plugin, which handles
    secret retrieval.
  - >-
    Supports standard, symmetric, and asymmetric vault types.
  - >-
    Fully idempotent; repeated runs with the same parameters produce no
    additional changes.
  - >-
    Supports Ansible check mode.
options:
  name:
    description: Name of the vault.
    type: str
    required: true
  state:
    description:
      - C(present) ensures the vault exists. Creates it if absent; updates
        C(description) or C(vault_type) if changed.
      - C(absent) removes the vault. A no-op if the vault does not exist.
      - C(archived) ensures the vault exists and then stores the payload
        in it. For standard vaults, the current payload is retrieved and
        compared; the archive step is skipped when the payload is
        identical. For symmetric and asymmetric vaults, the payload is
        always archived because comparison would require re-encryption.
    type: str
    default: present
    choices: [present, absent, archived]
  server:
    description: FQDN of the IPA server.
    type: str
    required: true
    env:
      - name: IPA_SERVER
    ini:
      - section: eigenstate_ipa
        key: server
  ipaadmin_principal:
    description: Kerberos principal to authenticate as.
    type: str
    default: admin
  ipaadmin_password:
    description: >-
      Password for the principal. Used to obtain a Kerberos ticket via
      C(kinit). Not required if C(kerberos_keytab) is set or a valid
      ticket already exists.
    type: str
    no_log: true
    env:
      - name: IPA_ADMIN_PASSWORD
  kerberos_keytab:
    description: >-
      Path to a Kerberos keytab file. Takes precedence over
      C(ipaadmin_password). Required for non-interactive use in AAP
      Execution Environments.
    type: str
    env:
      - name: IPA_KEYTAB
  verify:
    description: >-
      Path to the IPA CA certificate for TLS verification. Auto-detected
      from C(/etc/ipa/ca.crt) when not set. Disabled with a warning if
      neither is available.
    type: str
    env:
      - name: IPA_CERT
  username:
    description: >-
      User vault scope — the vault is owned by this user. Mutually
      exclusive with C(service) and C(shared).
    type: str
  service:
    description: >-
      Service vault scope — the vault is owned by this service principal.
      Mutually exclusive with C(username) and C(shared).
    type: str
  shared:
    description: >-
      Shared vault scope. Mutually exclusive with C(username) and
      C(service).
    type: bool
    default: false
  vault_type:
    description: >-
      Vault encryption type. Only used when C(state=present) and the
      vault is being created. Has no effect when the vault already exists
      (changing the type of an existing vault is not supported by this
      module).
    type: str
    default: standard
    choices: [standard, symmetric, asymmetric]
  description:
    description: Human-readable description for the vault.
    type: str
  vault_public_key:
    description: >-
      RSA public key (PEM format) for an asymmetric vault. Required when
      C(vault_type=asymmetric) and the vault is being created. Mutually
      exclusive with C(vault_public_key_file).
    type: str
  vault_public_key_file:
    description: >-
      Path to a file containing the RSA public key (PEM format) for an
      asymmetric vault. Mutually exclusive with C(vault_public_key).
    type: str
  data:
    description: >-
      Secret payload to archive. Required when C(state=archived) and
      C(data_file) is not set. Mutually exclusive with C(data_file).
    type: str
    no_log: true
  data_file:
    description: >-
      Path to a file whose contents will be archived as the secret
      payload. Mutually exclusive with C(data).
    type: str
  vault_password:
    description: >-
      Password for a symmetric vault. Required when creating or archiving
      a C(vault_type=symmetric) vault. Mutually exclusive with
      C(vault_password_file).
    type: str
    no_log: true
  vault_password_file:
    description: >-
      Path to a file containing the symmetric vault password. Mutually
      exclusive with C(vault_password).
    type: str
  members:
    description: >-
      List of users, groups, or service principals to ensure are vault
      members. Delta-only — only adds members not already present.
    type: list
    elements: str
    default: []
  members_absent:
    description: >-
      List of users, groups, or service principals to ensure are not vault
      members. Delta-only — only removes members currently present.
    type: list
    elements: str
    default: []
notes:
  - Requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible
    controller.
  - "RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)"
  - Sensitive files (C(kerberos_keytab), C(vault_password_file)) should
    have mode C(0600) or more restrictive.
  - Changing the vault type of an existing vault is not supported. Delete
    and recreate the vault to change its type.
  - For symmetric vaults, C(vault_password) or C(vault_password_file) is
    required when creating or archiving the vault.
  - For asymmetric vaults, C(vault_public_key) or
    C(vault_public_key_file) is required at creation time.
seealso:
  - plugin: eigenstate.ipa.vault
    plugin_type: lookup
    description: Retrieve secrets from FreeIPA/IdM vaults.
  - module: redhat.rhel_idm.ipavault
author:
  - Greg Procunier
"""

EXAMPLES = r"""
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
"""

RETURN = r"""
changed:
  description: Whether the module made any changes.
  type: bool
  returned: always
vault:
  description: Current state of the vault after the operation.
  type: dict
  returned: when state is present or archived
  contains:
    name:
      description: Vault name.
      type: str
    scope:
      description: >-
        Vault ownership scope. One of C(shared), C(username=<user>),
        C(service=<svc>), or C(default).
      type: str
    type:
      description: Vault type — C(standard), C(symmetric), or C(asymmetric).
      type: str
    description:
      description: Vault description, or empty string when not set.
      type: str
    members:
      description: Current vault member list.
      type: list
      elements: str
    owners:
      description: Current vault owner list.
      type: list
      elements: str
"""

import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes, to_native, to_text
from ansible_collections.eigenstate.ipa.plugins.module_utils.ipa_client import (
    IPAClient,
    IPAClientError,
)

try:
    from ipalib import errors as ipalib_errors
    HAS_IPALIB = True
except ImportError:
    ipalib_errors = None
    HAS_IPALIB = False


def _read_file_bytes(path):
    with open(path, 'rb') as fh:
        return fh.read()


def _read_file_text(path):
    with open(path, 'r') as fh:
        return fh.read().rstrip('\n')


def _vault_find(api, name, scope_args):
    """Return the first matching vault record, or None."""
    result = api.Command.vault_find(
        name,
        all=True,
        **scope_args
    )
    entries = result.get('result', [])
    return entries[0] if entries else None


def _vault_show(api, name, scope_args):
    """Return the vault record for *name*, or None if not found."""
    try:
        result = api.Command.vault_show(
            name,
            all=True,
            no_members=False,
            **scope_args
        )
        return result.get('result')
    except ipalib_errors.NotFound:
        return None


def _unwrap(value):
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    return value


def _member_list(entry):
    """Extract member principal list from a vault_show result."""
    members = []
    for key in ('member_user', 'member_group', 'member_service'):
        for item in entry.get(key, []):
            members.append(to_text(item))
    return sorted(members)


def _bucket_member_principals(api, principals):
    """Partition principals into the IPA member argument buckets."""
    buckets = {
        'user': [],
        'group': [],
        'service': [],
    }
    unresolved = []

    def _show(command_name, principal):
        command = getattr(api.Command, command_name, None)
        if command is None:
            return None
        try:
            result = command(principal, all=True, raw=False)
            return result.get('result', {}) if isinstance(result, dict) else {}
        except ipalib_errors.NotFound:
            return None
        except Exception:
            return None

    for principal in sorted(set(to_text(p) for p in principals)):
        if '/' in principal:
            service_entry = _show('service_show', principal)
            if service_entry is not None:
                canonical = _unwrap(
                    service_entry.get('krbcanonicalname')
                    or service_entry.get('krbprincipalname')
                    or principal
                )
                buckets['service'].append(to_text(canonical))
                continue
        if _show('user_show', principal) is not None:
            buckets['user'].append(principal)
            continue
        if _show('group_show', principal) is not None:
            buckets['group'].append(principal)
            continue
        service_entry = _show('service_show', principal)
        if service_entry is not None:
            canonical = _unwrap(
                service_entry.get('krbcanonicalname')
                or service_entry.get('krbprincipalname')
                or principal
            )
            buckets['service'].append(to_text(canonical))
            continue
        unresolved.append(principal)

    return buckets, unresolved


def _canonicalize_member_for_compare(api, principal):
    """Normalize service principals to the canonical IPA member spelling."""
    principal = to_text(principal)
    if '/' not in principal:
        return principal

    command = getattr(api.Command, 'service_show', None)
    if command is None:
        return principal

    try:
        result = command(principal, all=True, raw=False)
        entry = result.get('result', {}) if isinstance(result, dict) else {}
    except Exception:
        return principal

    canonical = _unwrap(
        entry.get('krbcanonicalname')
        or entry.get('krbprincipalname')
        or principal
    )
    return to_text(canonical)


def _filter_member_buckets(buckets, selected):
    """Restrict bucketed members to the selected canonical identifiers."""
    filtered = {}
    for member_type, principals in buckets.items():
        kept = [principal for principal in principals if principal in selected]
        if kept:
            filtered[member_type] = kept
    return filtered


def _owner_list(entry):
    """Extract owner list from a vault_show result."""
    owners = []
    for key in ('owner_user', 'owner_group', 'owner_service'):
        for item in entry.get(key, []):
            owners.append(to_text(item))
    return sorted(owners)


def _format_vault_result(name, scope_label, entry):
    """Build the return dict from a vault_show/vault_find entry."""
    return {
        'name': name,
        'scope': scope_label,
        'type': to_native(_unwrap(entry.get('ipavaulttype', 'standard'))),
        'description': to_native(_unwrap(entry.get('description', '')) or ''),
        'members': _member_list(entry),
        'owners': _owner_list(entry),
    }


def _has_member_failures(value):
    """Return True when an IPA failed-member structure contains real failures."""
    if isinstance(value, dict):
        return any(_has_member_failures(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_has_member_failures(item) for item in value)
    return bool(value)


def _ensure_present(module, api, name, scope_args, scope_label, check_mode):
    """Ensure the vault exists; create or update as needed.

    Returns (changed, entry) where *entry* is the current vault record.
    """
    vault_type = module.params['vault_type']
    description = module.params['description']
    vault_public_key = module.params['vault_public_key']
    vault_public_key_file = module.params['vault_public_key_file']
    vault_password = module.params['vault_password']
    vault_password_file = module.params['vault_password_file']

    # Resolve public key bytes for asymmetric vaults
    public_key_bytes = None
    if vault_type == 'asymmetric':
        if vault_public_key_file:
            public_key_bytes = _read_file_bytes(vault_public_key_file)
        elif vault_public_key:
            public_key_bytes = to_bytes(vault_public_key)
        else:
            module.fail_json(
                msg="vault_type=asymmetric requires 'vault_public_key' "
                    "or 'vault_public_key_file'.")

    if vault_password_file:
        vault_password = _read_file_text(vault_password_file)
        module.warn_if_permissive = getattr(module, '_warn_if_permissive', None)

    entry = _vault_find(api, name, scope_args)
    changed = False

    if entry is None:
        # Vault does not exist — create it
        if not check_mode:
            add_args = dict(scope_args)
            add_args['ipavaulttype'] = vault_type
            if description is not None:
                add_args['description'] = description
            if vault_type == 'symmetric':
                if not vault_password:
                    module.fail_json(
                        msg="vault_type=symmetric requires 'vault_password' "
                            "or 'vault_password_file' when creating the vault."
                    )
                add_args['password'] = vault_password
            elif vault_type == 'asymmetric' and public_key_bytes:
                add_args['ipavaultpublickey'] = public_key_bytes
            result = api.Command.vault_add(name, **add_args)
            entry = result.get('result', {})
        else:
            # Synthesise a minimal entry for check mode
            entry = {
                'cn': [name],
                'ipavaulttype': [vault_type],
                'description': [description] if description else [],
            }
        changed = True
    else:
        # Vault exists — check for property drift
        current_type = to_native(_unwrap(entry.get('ipavaulttype')))
        current_desc = to_native(_unwrap(entry.get('description', '')) or '')

        mod_args = dict(scope_args)
        need_mod = False

        if description is not None and description != current_desc:
            mod_args['description'] = description
            need_mod = True

        if need_mod:
            if not check_mode:
                try:
                    api.Command.vault_mod(name, **mod_args)
                except ipalib_errors.EmptyModlist:
                    pass
                # Re-fetch after update
                entry = _vault_find(api, name, scope_args) or entry
            else:
                if description is not None:
                    entry = dict(entry)
                    entry['description'] = [description]
            changed = True

    return changed, entry


def _ensure_absent(module, api, name, scope_args, check_mode):
    """Delete the vault if it exists.

    Returns changed (bool).
    """
    entry = _vault_find(api, name, scope_args)
    if entry is None:
        return False

    if not check_mode:
        try:
            api.Command.vault_del(name, **scope_args)
        except ipalib_errors.NotFound:
            pass

    return True


def _ensure_archived(module, api, name, scope_args, scope_label, check_mode):
    """Ensure the vault exists and contains the desired payload.

    Returns (changed, entry).
    """
    # First ensure the vault exists
    present_changed, entry = _ensure_present(
        module, api, name, scope_args, scope_label, check_mode)

    vault_type = to_native(_unwrap(entry.get('ipavaulttype', 'standard')))

    # Resolve archive payload
    data_str = module.params['data']
    data_file = module.params['data_file']
    if data_file:
        payload = _read_file_bytes(data_file)
    elif data_str is not None:
        payload = to_bytes(data_str)
    else:
        module.fail_json(
            msg="state=archived requires 'data' or 'data_file'.")

    # Resolve symmetric vault password
    vault_password = module.params['vault_password']
    vault_password_file = module.params['vault_password_file']
    if vault_password_file:
        vault_password = _read_file_text(vault_password_file)
        module.warn_if_permissive = getattr(module, '_warn_if_permissive', None)

    if vault_type == 'symmetric' and not vault_password:
        module.fail_json(
            msg="vault_type=symmetric requires 'vault_password' or "
                "'vault_password_file' for state=archived.")

    # For standard vaults, compare current payload to avoid unnecessary writes
    archive_needed = True
    if vault_type == 'standard' and not present_changed:
        # Only skip the comparison if the vault was just created (no payload yet)
        try:
            retrieve_result = api.Command.vault_retrieve(name, **scope_args)
            current_data = retrieve_result.get('result', {}).get('data', b'')
            if isinstance(current_data, str):
                current_data = to_bytes(current_data)
            if current_data == payload:
                archive_needed = False
        except ipalib_errors.NotFound:
            archive_needed = True
        except Exception:
            # If retrieval fails for any reason, proceed with archive
            archive_needed = True

    archive_changed = False
    if archive_needed:
        if not check_mode:
            archive_args = dict(scope_args)
            archive_args['data'] = payload
            if vault_type == 'symmetric' and vault_password:
                archive_args['password'] = vault_password
            api.Command.vault_archive(name, **archive_args)
        archive_changed = True

    # Re-fetch current entry for accurate return value
    if not check_mode:
        fresh = _vault_find(api, name, scope_args)
        if fresh:
            entry = fresh

    return present_changed or archive_changed, entry


def _reconcile_members(module, api, name, scope_args, entry, check_mode):
    """Add/remove vault members to match desired state.

    Returns changed (bool).
    """
    desired_add = set(module.params.get('members') or [])
    desired_remove = set(module.params.get('members_absent') or [])

    if not desired_add and not desired_remove:
        return False

    current_members = set(_member_list(entry))
    desired_add_canonical = {
        _canonicalize_member_for_compare(api, principal)
        for principal in desired_add
    }
    desired_remove_canonical = {
        _canonicalize_member_for_compare(api, principal)
        for principal in desired_remove
    }
    to_add = desired_add_canonical - current_members
    to_remove = desired_remove_canonical & current_members

    if not to_add and not to_remove:
        return False

    if check_mode:
        return True

    changed = False
    member_arg_map = {
        'user': 'user',
        'group': 'group',
        'service': 'services',
    }

    if to_add:
        add_buckets, unresolved = _bucket_member_principals(api, to_add)
        if unresolved:
            module.fail_json(
                msg="Unable to resolve vault member principal(s): %s"
                    % ', '.join(sorted(unresolved)))
        add_buckets = _filter_member_buckets(add_buckets, to_add)
        add_args = dict(scope_args)
        for member_type, principals in add_buckets.items():
            if principals:
                add_args[member_arg_map[member_type]] = principals
        result = api.Command.vault_add_member(name, **add_args)
        failed = result.get('failed', {})
        if _has_member_failures(failed):
            if 'already a member' in str(failed).lower():
                failed = {}
        if _has_member_failures(failed):
            module.fail_json(
                msg="vault_add_member reported failures: %s"
                    % to_native(failed))
        changed = True

    if to_remove:
        remove_buckets, unresolved = _bucket_member_principals(api, to_remove)
        if unresolved:
            module.fail_json(
                msg="Unable to resolve vault member principal(s): %s"
                    % ', '.join(sorted(unresolved)))
        remove_buckets = _filter_member_buckets(remove_buckets, to_remove)
        remove_args = dict(scope_args)
        for member_type, principals in remove_buckets.items():
            if principals:
                remove_args[member_arg_map[member_type]] = principals
        result = api.Command.vault_remove_member(name, **remove_args)
        failed = result.get('failed', {})
        if _has_member_failures(failed):
            if 'not a member' in str(failed).lower():
                failed = {}
        if _has_member_failures(failed):
            module.fail_json(
                msg="vault_remove_member reported failures: %s"
                    % to_native(failed))
        changed = True

    return changed


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present',
                       choices=['present', 'absent', 'archived']),
            server=dict(type='str', required=True,
                        fallback=(os.environ.get, ['IPA_SERVER'])),
            ipaadmin_principal=dict(type='str', default='admin'),
            ipaadmin_password=dict(type='str', no_log=True,
                                   fallback=(os.environ.get,
                                             ['IPA_ADMIN_PASSWORD'])),
            kerberos_keytab=dict(type='str',
                                 fallback=(os.environ.get, ['IPA_KEYTAB'])),
            verify=dict(type='str',
                        fallback=(os.environ.get, ['IPA_CERT'])),
            username=dict(type='str'),
            service=dict(type='str'),
            shared=dict(type='bool', default=False),
            vault_type=dict(type='str', default='standard',
                            choices=['standard', 'symmetric', 'asymmetric']),
            description=dict(type='str'),
            vault_public_key=dict(type='str'),
            vault_public_key_file=dict(type='str'),
            data=dict(type='str', no_log=True),
            data_file=dict(type='str'),
            vault_password=dict(type='str', no_log=True),
            vault_password_file=dict(type='str'),
            members=dict(type='list', elements='str', default=[]),
            members_absent=dict(type='list', elements='str', default=[]),
        ),
        mutually_exclusive=[
            ('username', 'service', 'shared'),
            ('vault_public_key', 'vault_public_key_file'),
            ('data', 'data_file'),
            ('vault_password', 'vault_password_file'),
        ],
        supports_check_mode=True,
    )

    name = module.params['name']
    state = module.params['state']
    server = module.params['server']
    principal = module.params['ipaadmin_principal']
    password = module.params['ipaadmin_password']
    keytab = module.params['kerberos_keytab']
    verify = module.params['verify']
    username = module.params['username']
    service = module.params['service']
    shared = module.params['shared']
    vault_password_file = module.params['vault_password_file']
    vault_public_key_file = module.params['vault_public_key_file']
    data_file = module.params['data_file']

    # Validate scope
    try:
        IPAClient.validate_scope(username, service, shared)
    except IPAClientError as exc:
        module.fail_json(msg=to_native(exc))

    scope_args = IPAClient.scope_args(username, service, shared)
    scope_label = IPAClient.scope_label(username, service, shared)

    # Warn on permissive sensitive files before connecting
    client = IPAClient(warn_callback=module.warn)
    if keytab and os.path.exists(keytab):
        client.warn_if_permissive(keytab, 'kerberos_keytab')
    if vault_password_file and os.path.exists(vault_password_file):
        client.warn_if_permissive(vault_password_file, 'vault_password_file')
    if vault_public_key_file and os.path.exists(vault_public_key_file):
        client.warn_if_permissive(vault_public_key_file, 'vault_public_key_file')
    if data_file and os.path.exists(data_file):
        client.warn_if_permissive(data_file, 'data_file')

    try:
        client.connect(
            server=server,
            principal=principal,
            password=password,
            keytab=keytab,
            verify=verify,
        )
    except IPAClientError as exc:
        module.fail_json(msg=to_native(exc))

    try:
        api = client.api
        check_mode = module.check_mode
        changed = False
        vault_result = None

        if state == 'absent':
            changed = _ensure_absent(
                module, api, name, scope_args, check_mode)
            module.exit_json(changed=changed)

        elif state == 'present':
            try:
                changed, entry = _ensure_present(
                    module, api, name, scope_args, scope_label, check_mode)
                member_changed = _reconcile_members(
                    module, api, name, scope_args, entry, check_mode)
                if member_changed and not check_mode:
                    entry = _vault_find(api, name, scope_args) or entry
                changed = changed or member_changed
                vault_result = _format_vault_result(name, scope_label, entry)
            except IPAClientError as exc:
                module.fail_json(msg=to_native(exc))
            except Exception as exc:
                if ipalib_errors and isinstance(exc, ipalib_errors.AuthorizationError):
                    module.fail_json(
                        msg="Not authorized to manage vault '%s' as '%s': %s"
                            % (name, principal, to_native(exc)))
                module.fail_json(
                    msg="Failed to manage vault '%s': %s"
                        % (name, to_native(exc)))

        elif state == 'archived':
            try:
                changed, entry = _ensure_archived(
                    module, api, name, scope_args, scope_label, check_mode)
                member_changed = _reconcile_members(
                    module, api, name, scope_args, entry, check_mode)
                if member_changed and not check_mode:
                    entry = _vault_find(api, name, scope_args) or entry
                changed = changed or member_changed
                vault_result = _format_vault_result(name, scope_label, entry)
            except IPAClientError as exc:
                module.fail_json(msg=to_native(exc))
            except Exception as exc:
                if ipalib_errors and isinstance(exc, ipalib_errors.AuthorizationError):
                    module.fail_json(
                        msg="Not authorized to manage vault '%s' as '%s': %s"
                            % (name, principal, to_native(exc)))
                module.fail_json(
                    msg="Failed to archive into vault '%s': %s"
                        % (name, to_native(exc)))

        result = dict(changed=changed)
        if vault_result is not None:
            result['vault'] = vault_result
        module.exit_json(**result)

    finally:
        client.cleanup()


def main():
    run_module()


if __name__ == '__main__':
    main()

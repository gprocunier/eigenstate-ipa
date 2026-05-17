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
module: vault_artifact
version_added: "1.18.0"
short_description: Write, read, and verify opaque artifacts in IdM vaults
description:
  - Provides a generic custody helper for opaque artifacts stored in
    FreeIPA/IdM vaults.
  - Can create a vault, archive a payload, read it back, calculate a
    SHA-256 digest, and verify the read-back digest.
  - Does not implement signing, attestation, or application-specific
    interpretation of the artifact payload.
options:
  name:
    description: Vault/artifact name.
    type: str
    required: true
  state:
    description:
      - C(present), C(archived), and C(write) archive C(payload) into the vault.
      - C(read) retrieves the artifact digest and optional payload.
      - C(absent) removes the vault.
    type: str
    default: present
    choices: [present, archived, write, read, absent]
  server:
    description: FQDN of the IPA server.
    type: str
    required: true
  ipaadmin_principal:
    description: Kerberos principal to authenticate as.
    type: str
    default: admin
  ipaadmin_password:
    description: Password for the principal.
    type: str
  kerberos_keytab:
    description: Path to a Kerberos keytab file.
    type: path
  verify:
    description: Path to the IPA CA certificate for TLS verification.
    type: str
  username:
    description: User vault scope.
    type: str
  service:
    description: Service vault scope.
    type: str
  shared:
    description: Shared vault scope.
    type: bool
    default: false
  vault_type:
    description: Vault type to use when creating the vault.
    type: str
    default: standard
    choices: [standard, symmetric, asymmetric]
  description:
    description: Optional vault description when creating the vault.
    type: str
  payload:
    description: Artifact payload to archive.
    type: str
  payload_file:
    description: File containing the artifact payload to archive.
    type: path
  expected_sha256:
    description: Expected artifact SHA-256 digest.
    type: str
  read_back:
    description: Read the artifact after writing and verify the digest.
    type: bool
    default: true
  include_metadata:
    description: Include vault metadata in the result.
    type: bool
    default: true
  include_payload:
    description: >-
      Include retrieved payload in C(artifact_payload) for C(state=read).
      Use task-level C(no_log: true) when enabling this option.
    type: bool
    default: false
  payload_encoding:
    description: Encoding used when returning C(artifact_payload).
    type: str
    default: base64
    choices: [base64, utf-8]
  vault_password:
    description: Password for symmetric vault operations.
    type: str
  vault_password_file:
    description: File containing the symmetric vault password.
    type: path
  private_key_file:
    description: Private key file for asymmetric vault reads.
    type: path
author:
  - Greg Procunier (@gprocunier)
"""

EXAMPLES = r"""
- name: Archive a bootstrap bundle and verify read-back digest
  eigenstate.ipa.vault_artifact:
    name: app-bootstrap-bundle
    state: present
    shared: true
    payload_file: ./bootstrap-bundle.json
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/automation.keytab
    ipaadmin_principal: automation@EXAMPLE.COM
    verify: /etc/ipa/ca.crt
  no_log: true

- name: Read only artifact metadata and digest
  eigenstate.ipa.vault_artifact:
    name: certificate-rotation-evidence
    state: read
    shared: true
    expected_sha256: "{{ expected_digest }}"
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/automation.keytab
  register: artifact_check
"""

RETURN = r"""
changed:
  description: Whether the module changed vault state.
  type: bool
  returned: always
artifact_ref:
  description: Scope-qualified artifact reference.
  type: str
  returned: always
artifact_sha256:
  description: SHA-256 digest of the written or read payload.
  type: str
  returned: when payload is written or read
read_back_verified:
  description: Whether the read/read-back digest matched expectations.
  type: bool
  returned: always
vault_server:
  description: Server used for the vault operation.
  type: str
  returned: always
vault_id:
  description: Vault identifier from IdM when available.
  type: str
  returned: always
vault_type:
  description: Vault type from IdM when available.
  type: str
  returned: always
metadata:
  description: Vault metadata when requested.
  type: dict
  returned: when include_metadata=true
"""

import base64
import hashlib
import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes, to_native, to_text

try:
    from ansible_collections.eigenstate.ipa.plugins.module_utils.ipa_client import (
        IPAClient,
        IPAClientError,
    )
except ImportError:
    import importlib.util
    import pathlib
    _ipa_client_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / 'module_utils' / 'ipa_client.py')
    _ipa_client_spec = importlib.util.spec_from_file_location(
        'eigenstate_ipa_vault_artifact_ipa_client', _ipa_client_path)
    _ipa_client_mod = importlib.util.module_from_spec(_ipa_client_spec)
    _ipa_client_spec.loader.exec_module(_ipa_client_mod)
    IPAClient = _ipa_client_mod.IPAClient
    IPAClientError = _ipa_client_mod.IPAClientError

try:
    from ipalib import errors as ipalib_errors
except ImportError:
    ipalib_errors = None


class VaultArtifactError(Exception):
    def __init__(self, message, failure_class='unknown'):
        super(VaultArtifactError, self).__init__(message)
        self.failure_class = failure_class


def _unwrap(value, fallback=None):
    if value is None:
        return fallback
    if isinstance(value, (list, tuple)):
        return value[0] if value else fallback
    return value


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _read_file_bytes(path):
    with open(path, 'rb') as fh:
        return fh.read()


def _read_file_text(path):
    with open(path, 'r') as fh:
        return fh.read().rstrip('\n')


def _payload_bytes(params):
    if params.get('payload_file'):
        return _read_file_bytes(params['payload_file'])
    if params.get('payload') is not None:
        return to_bytes(params['payload'])
    raise VaultArtifactError(
        "state=%s requires 'payload' or 'payload_file'" % params['state'],
        failure_class='invalid',
    )


def _scope_label(username, service, shared):
    return IPAClient.scope_label(username, service, shared)


def _artifact_ref(scope_label, name):
    return "%s/%s" % (scope_label, name)


def _vault_find(api, name, scope_args):
    result = api.Command.vault_find(name, all=True, **scope_args)
    entries = result.get('result', [])
    return entries[0] if entries else None


def _vault_show(api, name, scope_args):
    try:
        result = api.Command.vault_show(
            name, all=True, no_members=False, **scope_args)
        return result.get('result', {})
    except Exception as exc:
        if _is_not_found(exc):
            return None
        raise


def _is_not_found(exc):
    return exc.__class__.__name__ == 'NotFound' or 'not found' in to_native(exc).lower()


def _classify_exception(exc):
    text = to_native(exc).lower()
    if _is_not_found(exc):
        return 'vault_not_found'
    if 'authorization' in exc.__class__.__name__.lower() or 'not authorized' in text:
        return 'auth'
    if 'scope' in text or 'shared' in text or 'service' in text or 'username' in text:
        return 'scope_mismatch'
    return 'unknown'


def _metadata(name, scope_label, entry):
    if not entry:
        return {
            'name': name,
            'scope': scope_label,
            'type': 'unknown',
            'description': None,
            'vault_id': None,
        }
    return {
        'name': name,
        'scope': scope_label,
        'type': to_native(_unwrap(entry.get('ipavaulttype'), 'unknown')),
        'description': to_native(_unwrap(entry.get('description'), '') or ''),
        'vault_id': _unwrap(entry.get('ipavaultid')),
    }


def _base_result(params, scope_label):
    return {
        'changed': False,
        'artifact_ref': _artifact_ref(scope_label, params['name']),
        'artifact_sha256': None,
        'read_back_verified': False,
        'vault_server': params['server'],
        'vault_id': None,
        'vault_type': 'unknown',
        'metadata': {},
    }


def _create_vault(api, name, scope_args, params):
    add_args = dict(scope_args)
    add_args['ipavaulttype'] = params.get('vault_type') or 'standard'
    if params.get('description') is not None:
        add_args['description'] = params['description']
    if params.get('vault_password'):
        add_args['password'] = params['vault_password']
    api.Command.vault_add(name, **add_args)


def _archive(api, name, scope_args, params, payload):
    archive_args = dict(scope_args)
    archive_args['data'] = payload
    if params.get('vault_password'):
        archive_args['password'] = params['vault_password']
    api.Command.vault_archive(name, **archive_args)


def _retrieve(api, name, scope_args, params):
    retrieve_args = dict(scope_args)
    if params.get('vault_password'):
        retrieve_args['password'] = params['vault_password']
    if params.get('private_key_file'):
        retrieve_args['private_key'] = _read_file_bytes(params['private_key_file'])
    result = api.Command.vault_retrieve(name, **retrieve_args)
    data = result.get('result', {}).get('data')
    if data is None:
        raise VaultArtifactError(
            "vault '%s' returned no artifact data" % name,
            failure_class='unknown',
        )
    if isinstance(data, bytes):
        return data
    return to_bytes(data)


def _payload_for_return(data, encoding):
    if encoding == 'base64':
        return base64.b64encode(data).decode('ascii')
    return to_text(data, errors='surrogate_or_strict')


def _apply_metadata(result, params, metadata):
    result['vault_id'] = metadata.get('vault_id')
    result['vault_type'] = metadata.get('type', 'unknown')
    if params.get('include_metadata'):
        result['metadata'] = metadata


def run_artifact(api, params, check_mode=False):
    IPAClient.validate_scope(
        params.get('username'), params.get('service'), params.get('shared'))
    scope_args = IPAClient.scope_args(
        params.get('username'), params.get('service'), params.get('shared'))
    scope_label = _scope_label(
        params.get('username'), params.get('service'), params.get('shared'))
    result = _base_result(params, scope_label)
    name = params['name']
    state = params['state']
    write_state = state in ('present', 'archived', 'write')

    try:
        entry = _vault_show(api, name, scope_args)
        if write_state:
            payload = _payload_bytes(params)
            expected = params.get('expected_sha256')
            digest = _sha256(payload)
            if expected and expected != digest:
                raise VaultArtifactError(
                    "payload digest does not match expected_sha256",
                    failure_class='digest_mismatch',
                )
            if entry is None:
                if not check_mode:
                    _create_vault(api, name, scope_args, params)
                    entry = _vault_show(api, name, scope_args)
                result['changed'] = True
            if not check_mode:
                _archive(api, name, scope_args, params, payload)
            result['changed'] = True
            result['artifact_sha256'] = digest
            metadata = _metadata(name, scope_label, entry)
            _apply_metadata(result, params, metadata)
            if params.get('read_back') and not check_mode:
                read_back = _retrieve(api, name, scope_args, params)
                read_back_digest = _sha256(read_back)
                result['read_back_verified'] = read_back_digest == digest
                if not result['read_back_verified']:
                    raise VaultArtifactError(
                        "read-back digest mismatch for '%s'" % name,
                        failure_class='digest_mismatch',
                    )
            else:
                result['read_back_verified'] = not params.get('read_back')
            return result

        if state == 'read':
            if entry is None:
                raise VaultArtifactError(
                    "vault '%s' not found" % name,
                    failure_class='vault_not_found',
                )
            data = _retrieve(api, name, scope_args, params)
            digest = _sha256(data)
            expected = params.get('expected_sha256')
            result['artifact_sha256'] = digest
            result['read_back_verified'] = expected is None or expected == digest
            if expected and expected != digest:
                raise VaultArtifactError(
                    "artifact digest does not match expected_sha256",
                    failure_class='digest_mismatch',
                )
            metadata = _metadata(name, scope_label, entry)
            _apply_metadata(result, params, metadata)
            if params.get('include_payload'):
                result['artifact_payload'] = _payload_for_return(
                    data, params.get('payload_encoding') or 'base64')
            return result

        if state == 'absent':
            if entry is None:
                return result
            if not check_mode:
                api.Command.vault_del(name, **scope_args)
            result['changed'] = True
            result['read_back_verified'] = True
            metadata = _metadata(name, scope_label, entry)
            _apply_metadata(result, params, metadata)
            return result

        raise VaultArtifactError(
            "unsupported state '%s'" % state,
            failure_class='invalid',
        )
    except VaultArtifactError:
        raise
    except Exception as exc:
        raise VaultArtifactError(
            to_native(exc), failure_class=_classify_exception(exc))


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present',
                       choices=['present', 'archived', 'write', 'read', 'absent']),
            server=dict(type='str', required=True,
                        fallback=(os.environ.get, ['IPA_SERVER'])),
            ipaadmin_principal=dict(type='str', default='admin'),
            ipaadmin_password=dict(type='str', no_log=True,
                                   fallback=(os.environ.get,
                                             ['IPA_ADMIN_PASSWORD'])),
            kerberos_keytab=dict(type='path',
                                 fallback=(os.environ.get, ['IPA_KEYTAB'])),
            verify=dict(type='str',
                        fallback=(os.environ.get, ['IPA_CERT'])),
            username=dict(type='str'),
            service=dict(type='str'),
            shared=dict(type='bool', default=False),
            vault_type=dict(type='str', default='standard',
                            choices=['standard', 'symmetric', 'asymmetric']),
            description=dict(type='str'),
            payload=dict(type='str', no_log=True),
            payload_file=dict(type='path'),
            expected_sha256=dict(type='str'),
            read_back=dict(type='bool', default=True),
            include_metadata=dict(type='bool', default=True),
            include_payload=dict(type='bool', default=False),
            payload_encoding=dict(type='str', default='base64',
                                  choices=['base64', 'utf-8']),
            vault_password=dict(type='str', no_log=True),
            vault_password_file=dict(type='path'),
            private_key_file=dict(type='path'),
        ),
        mutually_exclusive=[
            ('username', 'service', 'shared'),
            ('payload', 'payload_file'),
            ('vault_password', 'vault_password_file'),
        ],
        supports_check_mode=True,
    )

    if module.params.get('vault_password_file'):
        module.params['vault_password'] = _read_file_text(
            module.params['vault_password_file'])

    client = IPAClient(warn_callback=module.warn, require_trusted_tls=True)
    for option in ('kerberos_keytab', 'vault_password_file',
                   'payload_file', 'private_key_file'):
        path = module.params.get(option)
        if path and os.path.exists(path):
            client.warn_if_permissive(path, option)

    try:
        client.connect(
            server=module.params['server'],
            principal=module.params['ipaadmin_principal'],
            password=module.params['ipaadmin_password'],
            keytab=module.params['kerberos_keytab'],
            verify=module.params['verify'],
        )
        module.exit_json(**run_artifact(
            client.api, module.params, check_mode=module.check_mode))
    except IPAClientError as exc:
        module.fail_json(msg=to_native(exc), failure_class='auth')
    except VaultArtifactError as exc:
        module.fail_json(msg=to_native(exc), failure_class=exc.failure_class)
    finally:
        client.cleanup()


def main():
    run_module()


if __name__ == '__main__':
    main()

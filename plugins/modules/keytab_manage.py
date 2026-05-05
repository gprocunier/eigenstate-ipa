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

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r"""
---
module: keytab_manage
version_added: "1.12.0"
short_description: Retrieve or rotate Kerberos keytabs with explicit module semantics
description:
  - >-
    Retrieves existing Kerberos keytabs or explicitly rotates principal keys
    through C(ipa-getkeytab).
  - >-
    Provides a safer module surface for automation that writes keytabs to disk
    or performs rotation. The existing C(eigenstate.ipa.keytab) lookup remains
    available for compatibility.
  - >-
    Does not return raw keytab content unless C(return_content=true) is set.
  - Supports Ansible check mode where the module can report intended changes.
options:
  principal:
    description: Kerberos service or host principal whose keytab is managed.
    type: str
    required: true
  state:
    description:
      - C(retrieved) retrieves existing keys only.
      - C(rotated) generates new keys and invalidates all existing keytabs for the principal.
    type: str
    default: retrieved
    choices: [retrieved, rotated]
  confirm_rotation:
    description: Required confirmation gate for C(state=rotated).
    type: bool
    default: false
  server:
    description: FQDN of the IPA server.
    type: str
    required: true
    env:
      - name: IPA_SERVER
  ipaadmin_principal:
    description: Kerberos principal to authenticate as.
    type: str
    default: admin
  ipaadmin_password:
    description: >-
      Password for the principal. Used to obtain a Kerberos ticket via
      C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket
      already exists.
    type: str
    no_log: true
    env:
      - name: IPA_ADMIN_PASSWORD
  kerberos_keytab:
    description: Path to a Kerberos keytab file for non-interactive authentication.
    type: path
    env:
      - name: IPA_KEYTAB
  verify:
    description: >-
      IPA CA certificate path for C(ipa-getkeytab --cacert), or C(false) to
      rely on the local trust store.
    type: raw
    env:
      - name: IPA_CERT
  enctypes:
    description: Kerberos encryption types to request.
    type: list
    elements: str
    default: []
  destination:
    description: Optional controller-local path where the keytab should be written.
    type: path
  mode:
    description: File mode to apply when C(destination) is set.
    type: raw
    default: "0600"
  owner:
    description: File owner name or numeric UID for C(destination).
    type: str
  group:
    description: File group name or numeric GID for C(destination).
    type: str
  return_content:
    description: Return the base64-encoded keytab content.
    type: bool
    default: false
notes:
  - Requires the platform package that provides C(ipa-getkeytab).
  - C(state=rotated) invalidates every existing keytab for the principal.
  - Keytab content is secret-bearing. Prefer C(destination) with restrictive mode.
seealso:
  - lookup: eigenstate.ipa.keytab
  - module: redhat.rhel_idm.ipaservice
author:
  - Greg Procunier
"""

EXAMPLES = r"""
- name: Retrieve an existing service keytab
  eigenstate.ipa.keytab_manage:
    principal: HTTP/app.example.com@EXAMPLE.COM
    state: retrieved
    destination: /etc/httpd/conf/httpd.keytab
    mode: "0600"
    owner: apache
    group: apache
    server: idm-01.example.com
    kerberos_keytab: /runner/env/ipa/admin.keytab

- name: Rotate a service keytab with an explicit guard
  eigenstate.ipa.keytab_manage:
    principal: HTTP/app.example.com@EXAMPLE.COM
    state: rotated
    confirm_rotation: true
    destination: /etc/httpd/conf/httpd.keytab
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"
"""

RETURN = r"""
changed:
  description: Whether the module changed the destination or rotated keys.
  type: bool
  returned: always
principal:
  description: Target Kerberos principal.
  type: str
  returned: always
state:
  description: Requested module state.
  type: str
  returned: always
destination:
  description: Destination path written by the module, if any.
  type: str
  returned: always
mode:
  description: Effective file mode when C(destination) was written.
  type: str
  returned: when destination is set
rotation_performed:
  description: Whether the module rotated principal keys.
  type: bool
  returned: always
content:
  description: Base64-encoded keytab content.
  type: str
  returned: when return_content=true and not check mode
"""

import base64
import grp
import os
import pwd
import shutil
import subprocess
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible_collections.eigenstate.ipa.plugins.module_utils.ipa_client import (
    IPAClient,
    IPAClientError,
)


def _install_hint():
    return (
        "Install the package that provides ipa-getkeytab. On RHEL 10, "
        "install ipa-client in the control node or execution environment.")


def _ensure_ipa_getkeytab(module):
    if not shutil.which('ipa-getkeytab'):
        module.fail_json(msg="'ipa-getkeytab' not found. %s" % _install_hint())


def _retrieve_keytab(module, principal, server, enctypes, retrieve_mode, verify):
    temp_dir = tempfile.mkdtemp(prefix='eigenstate_keytab_')
    temp_path = os.path.join(temp_dir, 'managed.keytab')
    try:
        cmd = ['ipa-getkeytab', '-s', server, '-p', principal, '-k', temp_path]
        if verify:
            cmd.extend(['--cacert', verify])
        for enctype in enctypes:
            cmd.extend(['-e', enctype])
        if retrieve_mode == 'retrieve':
            cmd.append('-r')

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30,
                env=os.environ.copy())
        except FileNotFoundError:
            module.fail_json(msg="'ipa-getkeytab' not found. %s" % _install_hint())
        except subprocess.TimeoutExpired:
            module.fail_json(
                msg="'ipa-getkeytab' timed out for principal '%s'." % principal)

        if result.returncode != 0:
            module.fail_json(
                msg="ipa-getkeytab failed for '%s' on server '%s' (exit %d): %s"
                    % (principal, server, result.returncode,
                       to_native(result.stderr).strip()))

        if not os.path.exists(temp_path):
            module.fail_json(
                msg="ipa-getkeytab did not create a keytab for '%s'." % principal)
        with open(temp_path, 'rb') as fh:
            data = fh.read()
        if not data:
            module.fail_json(
                msg="ipa-getkeytab produced an empty keytab for '%s'." % principal)
        return data
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def _parse_mode(mode):
    if mode is None:
        return None
    if isinstance(mode, int):
        return mode
    text = to_text(mode).strip()
    if text.isdigit():
        return int(text, 8)
    raise ValueError("mode must be an octal string or integer")


def _resolve_owner(owner):
    if owner is None:
        return -1
    if owner.isdigit():
        return int(owner)
    return pwd.getpwnam(owner).pw_uid


def _resolve_group(group):
    if group is None:
        return -1
    if group.isdigit():
        return int(group)
    return grp.getgrnam(group).gr_gid


def _write_destination(module, destination, data, mode, owner, group):
    before = None
    if os.path.exists(destination):
        with open(destination, 'rb') as fh:
            before = fh.read()

    changed = before != data
    current_mode = None
    if os.path.exists(destination):
        current_mode = os.stat(destination).st_mode & 0o777

    desired_mode = _parse_mode(mode)
    if desired_mode is not None and current_mode != desired_mode:
        changed = True

    uid = _resolve_owner(owner)
    gid = _resolve_group(group)
    if os.path.exists(destination) and (uid != -1 or gid != -1):
        stat_result = os.stat(destination)
        if uid != -1 and stat_result.st_uid != uid:
            changed = True
        if gid != -1 and stat_result.st_gid != gid:
            changed = True

    if not changed:
        return False

    parent = os.path.dirname(destination)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, mode=0o700)

    fd, tmp_path = tempfile.mkstemp(
        prefix='.ansible-keytab-', dir=parent or None)
    try:
        with os.fdopen(fd, 'wb') as fh:
            fh.write(data)
        if desired_mode is not None:
            os.chmod(tmp_path, desired_mode)
        if uid != -1 or gid != -1:
            os.chown(tmp_path, uid, gid)
        os.replace(tmp_path, destination)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    return True


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            principal=dict(type='str', required=True),
            state=dict(type='str', default='retrieved',
                       choices=['retrieved', 'rotated']),
            confirm_rotation=dict(type='bool', default=False),
            server=dict(type='str', required=True,
                        fallback=(os.environ.get, ['IPA_SERVER'])),
            ipaadmin_principal=dict(type='str', default='admin'),
            ipaadmin_password=dict(type='str', no_log=True,
                                   fallback=(os.environ.get,
                                             ['IPA_ADMIN_PASSWORD'])),
            kerberos_keytab=dict(type='path',
                                 fallback=(os.environ.get, ['IPA_KEYTAB'])),
            verify=dict(type='raw',
                        fallback=(os.environ.get, ['IPA_CERT'])),
            enctypes=dict(type='list', elements='str', default=[]),
            destination=dict(type='path'),
            mode=dict(type='raw', default='0600'),
            owner=dict(type='str'),
            group=dict(type='str'),
            return_content=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )

    principal = module.params['principal']
    state = module.params['state']
    destination = module.params['destination']

    if state == 'rotated' and not module.params['confirm_rotation']:
        module.fail_json(
            msg="state=rotated requires confirm_rotation=true because key "
                "rotation invalidates existing keytabs for the principal.")

    client = IPAClient(warn_callback=module.warn)
    keytab = module.params['kerberos_keytab']
    if keytab and os.path.exists(keytab):
        client.warn_if_permissive(keytab, 'kerberos_keytab')

    result = {
        'changed': False,
        'principal': principal,
        'state': state,
        'destination': destination,
        'rotation_performed': False,
    }

    if destination:
        result['mode'] = to_text(module.params['mode'])

    if module.check_mode:
        result['changed'] = bool(destination or state == 'rotated')
        result['rotation_performed'] = False
        module.exit_json(**result)

    _ensure_ipa_getkeytab(module)

    try:
        verify = client.resolve_verify(module.params['verify'])
        client.authenticate(
            principal=module.params['ipaadmin_principal'],
            password=module.params['ipaadmin_password'],
            keytab=keytab,
        )
        retrieve_mode = 'generate' if state == 'rotated' else 'retrieve'
        data = _retrieve_keytab(
            module,
            principal,
            module.params['server'],
            module.params['enctypes'] or [],
            retrieve_mode,
            verify,
        )

        if destination:
            result['changed'] = _write_destination(
                module,
                destination,
                data,
                module.params['mode'],
                module.params['owner'],
                module.params['group'],
            )

        if state == 'rotated':
            result['changed'] = True
            result['rotation_performed'] = True

        if module.params['return_content']:
            result['content'] = base64.b64encode(data).decode('ascii')
            result['encoding'] = 'base64'

        module.exit_json(**result)
    except IPAClientError as exc:
        module.fail_json(msg=to_native(exc))
    except (KeyError, ValueError) as exc:
        module.fail_json(msg=to_native(exc))
    finally:
        client.cleanup()


def main():
    run_module()


if __name__ == '__main__':
    main()

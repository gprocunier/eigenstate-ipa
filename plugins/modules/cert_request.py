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
module: cert_request
version_added: "1.12.0"
short_description: Request IdM CA certificates with safe module returns
description:
  - >-
    Submits a CSR to the FreeIPA/IdM CA and optionally writes the issued
    certificate to a controller-local destination.
  - >-
    Provides explicit module semantics for certificate issuance while the
    existing C(eigenstate.ipa.cert) lookup remains available for compatibility.
  - >-
    Returns certificate metadata by default. Certificate content is returned
    only when C(return_content=true) is set.
  - Private key generation and handling remain outside this module.
options:
  principal:
    description: Service or host principal to request a certificate for.
    type: str
    required: true
  csr:
    description: Inline PEM certificate signing request.
    type: str
  csr_file:
    description: Controller-local path to a PEM certificate signing request.
    type: path
  destination:
    description: Optional controller-local path where the certificate should be written.
    type: path
  mode:
    description: File mode to apply when C(destination) is set.
    type: raw
    default: "0644"
  owner:
    description: File owner name or numeric UID for C(destination).
    type: str
  group:
    description: File group name or numeric GID for C(destination).
    type: str
  return_content:
    description: Return the issued certificate content.
    type: bool
    default: false
  encoding:
    description: Certificate output encoding.
    type: str
    default: pem
    choices: [pem, base64]
  profile:
    description: Certificate profile ID to use.
    type: str
  ca:
    description: Sub-CA name to issue from.
    type: str
  add:
    description: Create the principal if it does not already exist.
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
    description: Password for the principal.
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
    description: IPA CA certificate path for TLS verification, or C(false).
    type: raw
    env:
      - name: IPA_CERT
notes:
  - Requires C(python3-ipalib) and C(python3-ipaclient).
  - The module never accepts or returns private key material.
seealso:
  - lookup: eigenstate.ipa.cert
  - module: redhat.rhel_idm.ipacert
author:
  - Greg Procunier
"""

EXAMPLES = r"""
- name: Request a service certificate and write it to disk
  eigenstate.ipa.cert_request:
    principal: HTTP/app.example.com@EXAMPLE.COM
    csr_file: /etc/pki/tls/certs/app.csr
    destination: /etc/pki/tls/certs/app.pem
    mode: "0644"
    server: idm-01.example.com
    kerberos_keytab: /runner/env/ipa/admin.keytab

- name: Request a certificate and keep the result metadata-only
  eigenstate.ipa.cert_request:
    principal: HTTP/app.example.com@EXAMPLE.COM
    csr: "{{ app_csr }}"
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"
"""

RETURN = r"""
changed:
  description: Whether the module requested a certificate or changed the destination.
  type: bool
  returned: always
principal:
  description: Target principal.
  type: str
  returned: always
destination:
  description: Destination path written by the module, if any.
  type: str
  returned: always
metadata:
  description: Safe certificate metadata.
  type: dict
  returned: always
content:
  description: Issued certificate content.
  type: str
  returned: when return_content=true and not check mode
"""

import base64
import grp
import os
import pwd
import textwrap
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native, to_text
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


def _read_text(path):
    with open(path, 'r') as fh:
        return fh.read()


def _unwrap(value):
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    return value


def _der_b64_to_pem(b64_der):
    clean = to_text(b64_der, errors='surrogate_or_strict').strip()
    clean = clean.replace('\n', '').replace('\r', '')
    wrapped = textwrap.fill(clean, width=64)
    return (
        "-----BEGIN CERTIFICATE-----\n"
        "%s\n"
        "-----END CERTIFICATE-----\n" % wrapped
    )


def _collect_san(entry):
    san = []
    for key in ('san_rfc822name', 'san_dnsname', 'san_x400address',
                'san_directoryname', 'san_edipartyname', 'san_uri',
                'san_ipaddress', 'san_oid', 'san_other'):
        values = entry.get(key)
        if not values:
            continue
        if isinstance(values, (list, tuple)):
            san.extend(to_text(value) for value in values)
        else:
            san.append(to_text(values))
    return san


def _metadata(entry):
    def _s(key):
        raw = _unwrap(entry.get(key, ''))
        return to_text(raw or '', errors='surrogate_or_strict')

    return {
        'serial_number': entry.get('serial_number'),
        'subject': _s('subject'),
        'issuer': _s('issuer'),
        'valid_not_before': _s('valid_not_before'),
        'valid_not_after': _s('valid_not_after'),
        'san': _collect_san(entry),
        'revoked': bool(entry.get('revoked', False)),
        'revocation_reason': entry.get('revocation_reason'),
    }


def _certificate_value(entry, encoding):
    b64_der = entry.get('certificate', '')
    if encoding == 'base64':
        return to_text(b64_der, errors='surrogate_or_strict').strip()
    return _der_b64_to_pem(b64_der)


def _request_cert(module, api, principal, csr):
    request_args = {
        'principal': principal,
        'all': True,
    }
    if module.params['add']:
        request_args['add'] = True
    if module.params['profile']:
        request_args['profile_id'] = module.params['profile']
    if module.params['ca']:
        request_args['cacn'] = module.params['ca']

    try:
        result = api.Command.cert_request(csr, **request_args)
    except ipalib_errors.NotFound as exc:
        module.fail_json(
            msg="Principal '%s' not found in IdM: %s" %
                (principal, to_native(exc)))
    except ipalib_errors.AuthorizationError as exc:
        module.fail_json(
            msg="Permission denied requesting a certificate for '%s': %s" %
                (principal, to_native(exc)))
    except Exception as exc:
        module.fail_json(
            msg="cert_request failed for principal '%s': %s" %
                (principal, to_native(exc)))
    return result.get('result', {})


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


def _write_destination(destination, content, mode, owner, group):
    data = content.encode('utf-8')
    before = None
    if os.path.exists(destination):
        with open(destination, 'rb') as fh:
            before = fh.read()

    changed = before != data
    desired_mode = _parse_mode(mode)
    if os.path.exists(destination) and desired_mode is not None:
        if (os.stat(destination).st_mode & 0o777) != desired_mode:
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
        os.makedirs(parent, mode=0o755)

    fd, tmp_path = tempfile.mkstemp(
        prefix='.ansible-cert-', dir=parent or None, text=False)
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
            csr=dict(type='str'),
            csr_file=dict(type='path'),
            destination=dict(type='path'),
            mode=dict(type='raw', default='0644'),
            owner=dict(type='str'),
            group=dict(type='str'),
            return_content=dict(type='bool', default=False),
            encoding=dict(type='str', default='pem',
                          choices=['pem', 'base64']),
            profile=dict(type='str'),
            ca=dict(type='str'),
            add=dict(type='bool', default=False),
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
        ),
        mutually_exclusive=[('csr', 'csr_file')],
        required_one_of=[('csr', 'csr_file')],
        supports_check_mode=True,
    )

    principal = module.params['principal']
    destination = module.params['destination']
    result = {
        'changed': False,
        'principal': principal,
        'destination': destination,
        'metadata': {},
    }

    if not HAS_IPALIB:
        module.fail_json(
            msg="The 'ipalib' Python library is required for "
                "eigenstate.ipa.cert_request.")

    if module.check_mode:
        result['changed'] = True
        module.exit_json(**result)

    csr = module.params['csr']
    if module.params['csr_file']:
        csr = _read_text(module.params['csr_file'])

    client = IPAClient(warn_callback=module.warn, require_trusted_tls=True)
    keytab = module.params['kerberos_keytab']
    if keytab and os.path.exists(keytab):
        client.warn_if_permissive(keytab, 'kerberos_keytab')

    try:
        client.connect(
            server=module.params['server'],
            principal=module.params['ipaadmin_principal'],
            password=module.params['ipaadmin_password'],
            keytab=keytab,
            verify=module.params['verify'],
        )
        entry = _request_cert(module, client.api, principal, csr)
        cert_value = _certificate_value(entry, module.params['encoding'])
        result['metadata'] = _metadata(entry)
        result['changed'] = True

        if destination:
            _write_destination(
                destination,
                cert_value,
                module.params['mode'],
                module.params['owner'],
                module.params['group'],
            )

        if module.params['return_content']:
            result['content'] = cert_value
            result['encoding'] = module.params['encoding']

        module.exit_json(**result)
    except IPAClientError as exc:
        module.fail_json(msg=to_native(exc))
    except (OSError, KeyError, ValueError) as exc:
        module.fail_json(msg=to_native(exc))
    finally:
        client.cleanup()


def main():
    run_module()


if __name__ == '__main__':
    main()

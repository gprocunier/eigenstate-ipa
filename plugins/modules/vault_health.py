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
module: vault_health
version_added: "1.18.0"
short_description: Check IdM vault and KRA health separately from LDAP reachability
description:
  - Runs a read-only health check against a specific IdM/FreeIPA server.
  - Distinguishes generic IdM/Kerberos reachability from KRA-backed vault
    reachability where the server API exposes enough information.
  - Optionally checks a caller-provided canary vault and reports whether
    it is present and stale.
  - The module reports structured health fields instead of failing the
    play when IdM or vault health is bad. Invalid inputs and missing
    controller dependencies still fail normally.
options:
  server:
    description: FQDN of the IPA server to check.
    type: str
    required: true
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
  kerberos_keytab:
    description: Path to a Kerberos keytab file.
    type: path
  verify:
    description: Path to the IPA CA certificate for TLS verification.
    type: str
  canary_vault:
    description: Optional vault name to inspect as a health canary.
    type: str
  canary_max_age_seconds:
    description: >-
      Maximum acceptable age for the canary vault C(modifytimestamp).
      When omitted, staleness is not evaluated.
    type: int
  username:
    description: User vault scope for C(canary_vault).
    type: str
  service:
    description: Service vault scope for C(canary_vault).
    type: str
  shared:
    description: Shared vault scope for C(canary_vault).
    type: bool
    default: false
  require_direct_kra:
    description: >-
      Require the selected server to prove KRA-backed vault availability.
      If the API cannot prove KRA and no vault operation succeeds, the
      result is reported as unavailable.
    type: bool
    default: false
author:
  - Greg Procunier (@gprocunier)
"""

EXAMPLES = r"""
- name: Check shared vault health on an explicit replica
  eigenstate.ipa.vault_health:
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/automation.keytab
    ipaadmin_principal: automation@EXAMPLE.COM
    verify: /etc/ipa/ca.crt
    shared: true
    canary_vault: automation-health-canary
    require_direct_kra: true
  register: vault_health

- name: Stop when the vault plane is not ready
  ansible.builtin.assert:
    that:
      - vault_health.idm_reachable
      - vault_health.vault_reachable
      - vault_health.kra_available
      - vault_health.failure_class == 'none'
"""

RETURN = r"""
changed:
  description: Always false; the module is read-only.
  type: bool
  returned: always
server:
  description: Server that was checked.
  type: str
  returned: always
idm_reachable:
  description: Whether authentication and IdM API connection succeeded.
  type: bool
  returned: always
vault_reachable:
  description: Whether a vault command succeeded against the selected scope.
  type: bool
  returned: always
kra_available:
  description: Whether KRA-backed vault functionality appears available.
  type: raw
  returned: always
canary_present:
  description: Whether the optional canary vault exists.
  type: raw
  returned: always
canary_age_seconds:
  description: Age of the canary based on C(modifytimestamp), when available.
  type: raw
  returned: always
canary_stale:
  description: Whether the canary age exceeds C(canary_max_age_seconds).
  type: raw
  returned: always
proxy_detected:
  description: Whether the module detected an IPA proxy path.
  type: raw
  returned: always
failure_class:
  description: Stable failure class for automation decisions.
  type: str
  returned: always
message:
  description: Human-readable diagnostic summary.
  type: str
  returned: always
"""

from datetime import datetime, timezone
import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native, to_text

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
        'eigenstate_ipa_vault_health_ipa_client', _ipa_client_path)
    _ipa_client_mod = importlib.util.module_from_spec(_ipa_client_spec)
    _ipa_client_spec.loader.exec_module(_ipa_client_mod)
    IPAClient = _ipa_client_mod.IPAClient
    IPAClientError = _ipa_client_mod.IPAClientError

try:
    from ipalib import errors as ipalib_errors
except ImportError:
    ipalib_errors = None


def _base_result(server):
    return {
        'changed': False,
        'server': server,
        'idm_reachable': False,
        'vault_reachable': False,
        'kra_available': 'unknown',
        'canary_present': 'unknown',
        'canary_age_seconds': None,
        'canary_stale': 'unknown',
        'proxy_detected': 'unknown',
        'failure_class': 'unknown',
        'message': 'health check did not complete',
    }


def _unwrap(value, fallback=None):
    if value is None:
        return fallback
    if isinstance(value, (list, tuple)):
        return value[0] if value else fallback
    return value


def _classify_exception(exc):
    text = to_native(exc).lower()
    name = exc.__class__.__name__.lower()

    if 'notfound' in name or 'not found' in text:
        return 'vault_not_found'
    if 'authorization' in name or 'acierror' in name:
        return 'auth'
    if any(token in text for token in (
            'not authorized', 'access-control', 'credential',
            'kerberos', 'kinit', 'authentication', 'password')):
        return 'auth'
    if any(token in text for token in (
            'certificate verify', 'tls', 'ssl', 'ca certificate',
            'unknown ca')):
        return 'ca'
    if any(token in text for token in ('timeout', 'timed out')):
        return 'timeout'
    if any(token in text for token in (
            'kra', 'key recovery authority', 'vault service',
            'not configured for vault')):
        return 'kra_unavailable'
    if any(token in text for token in (
            'scope', 'shared', 'username', 'service')):
        return 'scope_mismatch'
    if any(token in text for token in (
            'failed to connect', 'connection', 'unreachable',
            'ldap', 'server')):
        return 'ldap'
    return 'unknown'


def _parse_timestamp(value, now=None):
    raw = _unwrap(value)
    if not raw:
        return None
    text = to_native(to_text(raw, errors='surrogate_or_strict'))
    candidates = (
        '%Y%m%d%H%M%SZ',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%SZ',
    )
    parsed = None
    for fmt in candidates:
        try:
            parsed = datetime.strptime(text, fmt)
            break
        except ValueError:
            continue
    if parsed is None:
        return None
    current = now or datetime.now(timezone.utc).replace(tzinfo=None)
    age = current - parsed
    return max(0, int(age.total_seconds()))


def _detect_kra_available(api):
    command = getattr(api.Command, 'kra_is_enabled', None)
    if command is not None:
        result = command()
        value = result.get('result', result) if isinstance(result, dict) else result
        if isinstance(value, bool):
            return value

    command = getattr(api.Command, 'vaultconfig_show', None)
    if command is not None:
        result = command()
        entry = result.get('result', {}) if isinstance(result, dict) else {}
        servers = (
            entry.get('kra_server_server')
            or entry.get('kra_server')
            or entry.get('servers')
        )
        if servers:
            return True
        if servers == []:
            return False

    return 'unknown'


def _scope_args(username, service, shared):
    return IPAClient.scope_args(username, service, shared)


def _mark_failure(result, exc):
    result['failure_class'] = _classify_exception(exc)
    result['message'] = to_native(exc)
    if result['failure_class'] == 'kra_unavailable':
        result['kra_available'] = False
    return result


def _check_vault_plane(api, result, scope_args, canary_vault,
                       canary_max_age_seconds):
    if canary_vault:
        show_args = dict(scope_args)
        show_args.update({'all': True, 'raw': False})
        try:
            response = api.Command.vault_show(canary_vault, **show_args)
        except Exception as exc:
            if _classify_exception(exc) == 'vault_not_found':
                result['vault_reachable'] = True
                result['canary_present'] = False
                result['canary_stale'] = 'unknown'
                result['failure_class'] = 'vault_not_found'
                result['message'] = (
                    "canary vault '%s' was not found" % canary_vault)
                if result['kra_available'] == 'unknown':
                    result['kra_available'] = True
                return result
            return _mark_failure(result, exc)

        entry = response.get('result', {}) if isinstance(response, dict) else {}
        result['vault_reachable'] = True
        result['canary_present'] = True
        if result['kra_available'] == 'unknown':
            result['kra_available'] = True
        age = _parse_timestamp(entry.get('modifytimestamp'))
        result['canary_age_seconds'] = age
        if canary_max_age_seconds is None or age is None:
            result['canary_stale'] = False if age is not None else 'unknown'
        else:
            result['canary_stale'] = age > canary_max_age_seconds
            if result['canary_stale']:
                result['failure_class'] = 'unknown'
                result['message'] = (
                    "canary vault '%s' is stale" % canary_vault)
                return result
        result['failure_class'] = 'none'
        result['message'] = "vault health check passed"
        return result

    find_args = dict(scope_args)
    find_args.update({'all': True, 'raw': False, 'sizelimit': 1})
    try:
        api.Command.vault_find('', **find_args)
    except Exception as exc:
        return _mark_failure(result, exc)

    result['vault_reachable'] = True
    if result['kra_available'] == 'unknown':
        result['kra_available'] = True
    result['canary_present'] = 'unknown'
    result['canary_stale'] = 'unknown'
    result['failure_class'] = 'none'
    result['message'] = "vault health check passed"
    return result


def run_health(api, params):
    result = _base_result(params['server'])
    result['idm_reachable'] = True
    username = params.get('username')
    service = params.get('service')
    shared = params.get('shared')
    scope_args = _scope_args(username, service, shared)

    try:
        result['kra_available'] = _detect_kra_available(api)
    except Exception as exc:
        if _classify_exception(exc) == 'kra_unavailable':
            result['kra_available'] = False
            if params.get('require_direct_kra'):
                return _mark_failure(result, exc)
        else:
            result['kra_available'] = 'unknown'

    result = _check_vault_plane(
        api,
        result,
        scope_args,
        params.get('canary_vault'),
        params.get('canary_max_age_seconds'),
    )

    if (params.get('require_direct_kra')
            and result['kra_available'] is not True
            and result['failure_class'] == 'none'):
        result['failure_class'] = 'kra_unavailable'
        result['message'] = 'direct KRA availability could not be proven'

    return result


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
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
            canary_vault=dict(type='str'),
            canary_max_age_seconds=dict(type='int'),
            username=dict(type='str'),
            service=dict(type='str'),
            shared=dict(type='bool', default=False),
            require_direct_kra=dict(type='bool', default=False),
        ),
        mutually_exclusive=[('username', 'service', 'shared')],
        supports_check_mode=True,
    )

    try:
        IPAClient.validate_scope(
            module.params['username'],
            module.params['service'],
            module.params['shared'],
        )
    except IPAClientError as exc:
        module.fail_json(msg=to_native(exc))

    client = IPAClient(warn_callback=module.warn, require_trusted_tls=True)
    if module.params['kerberos_keytab'] and os.path.exists(module.params['kerberos_keytab']):
        client.warn_if_permissive(
            module.params['kerberos_keytab'], 'kerberos_keytab')

    try:
        client.connect(
            server=module.params['server'],
            principal=module.params['ipaadmin_principal'],
            password=module.params['ipaadmin_password'],
            keytab=module.params['kerberos_keytab'],
            verify=module.params['verify'],
        )
    except IPAClientError as exc:
        result = _base_result(module.params['server'])
        _mark_failure(result, exc)
        module.exit_json(**result)

    try:
        module.exit_json(**run_health(client.api, module.params))
    finally:
        client.cleanup()


def main():
    run_module()


if __name__ == '__main__':
    main()

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
module: access_path
version_added: "1.18.0"
short_description: Summarize IdM principal, HBAC, sudo, and SELinux map readiness
description:
  - Reads existing IdM/FreeIPA objects and returns a generic access-path
    readiness summary for automation preflight checks.
  - Combines principal, HBAC rule, sudo rule, and SELinux user map facts
    into one machine-readable result.
  - This module is advisory and read-only. It does not create, modify, or
    delete IdM policy.
options:
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
  principal:
    description: IdM user principal to validate.
    type: str
    required: true
  host:
    description: Target host FQDN.
    type: str
    required: true
  hbac_service:
    description: HBAC service name, such as C(sshd).
    type: str
    required: true
    aliases: [service]
  hbac_rule:
    description: HBAC rule name to inspect.
    type: str
    required: true
  sudo_rule:
    description: Sudo rule name to inspect.
    type: str
    required: true
  selinux_map:
    description: SELinux user map name to inspect.
    type: str
    required: true
  expected_selinux_user:
    description: Expected SELinux user string.
    type: str
  expected_runas_user:
    description: Expected sudo RunAs user.
    type: str
author:
  - Greg Procunier (@gprocunier)
"""

EXAMPLES = r"""
- name: Validate an automation access path before running privileged work
  eigenstate.ipa.access_path:
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/automation.keytab
    principal: automation-svc
    host: app01.example.com
    hbac_service: sshd
    hbac_rule: automation-ssh
    sudo_rule: automation-root
    selinux_map: automation-confined
    expected_selinux_user: staff_u:s0
    expected_runas_user: root
  register: access_path
"""

RETURN = r"""
changed:
  description: Always false.
  type: bool
  returned: always
path_ready:
  description: Whether all checked path components are ready.
  type: bool
  returned: always
principal:
  description: Principal existence and normalized name facts.
  type: dict
  returned: always
hbac:
  description: HBAC readiness facts.
  type: dict
  returned: always
sudo:
  description: Sudo readiness facts.
  type: dict
  returned: always
selinux_map:
  description: SELinux user map readiness facts.
  type: dict
  returned: always
warnings:
  description: Non-blocking observations.
  type: list
  elements: str
  returned: always
errors:
  description: Readiness blockers.
  type: list
  elements: str
  returned: always
"""

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
        'eigenstate_ipa_access_path_ipa_client', _ipa_client_path)
    _ipa_client_mod = importlib.util.module_from_spec(_ipa_client_spec)
    _ipa_client_spec.loader.exec_module(_ipa_client_mod)
    IPAClient = _ipa_client_mod.IPAClient
    IPAClientError = _ipa_client_mod.IPAClientError


def _unwrap(value, fallback=None):
    if value is None:
        return fallback
    if isinstance(value, (list, tuple)):
        return value[0] if value else fallback
    return value


def _list(value):
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return [to_native(to_text(item, errors='surrogate_or_strict'))
                for item in value]
    return [to_native(to_text(value, errors='surrogate_or_strict'))]


def _text(value, fallback=None):
    raw = _unwrap(value, fallback)
    if raw is None:
        return None
    return to_native(to_text(raw, errors='surrogate_or_strict'))


def _enabled(entry):
    raw = _text(entry.get('ipaenabledflag'), 'TRUE')
    return raw.upper() == 'TRUE'


def _is_not_found(exc):
    return exc.__class__.__name__ == 'NotFound' or 'not found' in to_native(exc).lower()


def _principal_name(principal):
    return principal.split('@', 1)[0]


def _show_or_none(command, name):
    try:
        result = command(name, all=True, rights=False)
        return result.get('result', {})
    except Exception as exc:
        if _is_not_found(exc):
            return None
        raise


def _principal_facts(api, principal):
    username = _principal_name(principal)
    entry = _show_or_none(api.Command.user_show, username)
    if entry is None:
        return {
            'name': username,
            'exists': False,
        }
    return {
        'name': _text(entry.get('uid'), username),
        'principal': _text(entry.get('krbprincipalname'), principal),
        'exists': True,
        'enabled': not bool(_unwrap(entry.get('nsaccountlock'), False)),
    }


def _hbac_facts(api, rule_name, principal, host, service):
    entry = _show_or_none(api.Command.hbacrule_show, rule_name)
    if entry is None:
        return {
            'name': rule_name,
            'exists': False,
            'enabled': False,
            'permits_service': False,
            'user_ok': False,
            'host_ok': False,
        }
    username = _principal_name(principal)
    services = _list(entry.get('memberservice_hbacsvc'))
    hosts = _list(entry.get('memberhost_host'))
    users = _list(entry.get('memberuser_user'))
    service_ok = _text(entry.get('servicecategory')) == 'all' or service in services
    user_ok = _text(entry.get('usercategory')) == 'all' or username in users
    host_ok = _text(entry.get('hostcategory')) == 'all' or host in hosts
    return {
        'name': rule_name,
        'exists': True,
        'enabled': _enabled(entry),
        'permits_service': service_ok,
        'user_ok': user_ok,
        'host_ok': host_ok,
        'services': services,
        'users': users,
        'hosts': hosts,
    }


def _sudo_facts(api, rule_name, expected_runas_user):
    entry = _show_or_none(api.Command.sudorule_show, rule_name)
    if entry is None:
        return {
            'name': rule_name,
            'exists': False,
            'enabled': False,
            'runas_ok': False,
            'risky_options': [],
        }
    runas_users = _list(entry.get('ipasudorunas_user'))
    runas_category = _text(entry.get('ipasudorunasusercategory'))
    runas_ok = True
    if expected_runas_user:
        runas_ok = runas_category == 'all' or expected_runas_user in runas_users
    risky_options = [
        option for option in _list(entry.get('ipasudoopt'))
        if option in ('!authenticate', 'authenticate=false')
    ]
    return {
        'name': rule_name,
        'exists': True,
        'enabled': _enabled(entry),
        'runas_ok': runas_ok,
        'runasusers': runas_users,
        'runasusercategory': runas_category,
        'risky_options': risky_options,
    }


def _selinux_facts(api, map_name, expected_selinux_user):
    entry = _show_or_none(api.Command.selinuxusermap_show, map_name)
    if entry is None:
        return {
            'name': map_name,
            'exists': False,
            'enabled': False,
            'selinuxuser_matches': False,
            'selinuxuser': None,
        }
    selinuxuser = _text(entry.get('ipaselinuxuser'))
    matches = True
    if expected_selinux_user:
        matches = selinuxuser == expected_selinux_user
    return {
        'name': map_name,
        'exists': True,
        'enabled': _enabled(entry),
        'selinuxuser_matches': matches,
        'selinuxuser': selinuxuser,
    }


def _append_blockers(result):
    errors = result['errors']
    if not result['principal'].get('exists'):
        errors.append('principal does not exist')
    elif result['principal'].get('enabled') is False:
        errors.append('principal is disabled')

    hbac = result['hbac']
    if not hbac.get('exists'):
        errors.append('HBAC rule does not exist')
    elif not hbac.get('enabled'):
        errors.append('HBAC rule is disabled')
    else:
        if not hbac.get('permits_service'):
            errors.append('HBAC rule does not permit requested service')
        if not hbac.get('user_ok'):
            errors.append('HBAC rule does not include requested principal')
        if not hbac.get('host_ok'):
            errors.append('HBAC rule does not include requested host')

    sudo = result['sudo']
    if not sudo.get('exists'):
        errors.append('sudo rule does not exist')
    elif not sudo.get('enabled'):
        errors.append('sudo rule is disabled')
    elif not sudo.get('runas_ok'):
        errors.append('sudo rule RunAs target does not match expectation')

    selinux_map = result['selinux_map']
    if not selinux_map.get('exists'):
        errors.append('SELinux user map does not exist')
    elif not selinux_map.get('enabled'):
        errors.append('SELinux user map is disabled')
    elif not selinux_map.get('selinuxuser_matches'):
        errors.append('SELinux user does not match expectation')

    if sudo.get('risky_options'):
        result['warnings'].append('sudo rule contains risky options')


def run_access_path(api, params):
    result = {
        'changed': False,
        'path_ready': False,
        'principal': _principal_facts(api, params['principal']),
        'hbac': _hbac_facts(
            api,
            params['hbac_rule'],
            params['principal'],
            params['host'],
            params['hbac_service'],
        ),
        'sudo': _sudo_facts(
            api,
            params['sudo_rule'],
            params.get('expected_runas_user'),
        ),
        'selinux_map': _selinux_facts(
            api,
            params['selinux_map'],
            params.get('expected_selinux_user'),
        ),
        'warnings': [],
        'errors': [],
    }
    _append_blockers(result)
    result['path_ready'] = not result['errors']
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
            principal=dict(type='str', required=True),
            host=dict(type='str', required=True),
            hbac_service=dict(type='str', required=True,
                              aliases=['service']),
            hbac_rule=dict(type='str', required=True),
            sudo_rule=dict(type='str', required=True),
            selinux_map=dict(type='str', required=True),
            expected_selinux_user=dict(type='str'),
            expected_runas_user=dict(type='str'),
        ),
        supports_check_mode=True,
    )

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
        module.exit_json(**run_access_path(client.api, module.params))
    except IPAClientError as exc:
        module.fail_json(msg=to_native(exc))
    except Exception as exc:
        module.fail_json(msg=to_native(exc))
    finally:
        client.cleanup()


def main():
    run_module()


if __name__ == '__main__':
    main()

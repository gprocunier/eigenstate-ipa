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

DOCUMENTATION = """
---
name: sudo
version_added: "1.7.0"
short_description: Query IdM sudo rules, sudo commands, and sudo command groups
description:
  - Returns the configuration of IdM sudo policy objects from FreeIPA/IdM.
  - Supports read-only C(show) and C(find) operations for sudo rules,
    sudo commands, and sudo command groups through one lookup surface.
  - Sudo policy in IdM is split across multiple object types. Rules define
    who may run what and where. Sudo commands define the command paths
    themselves. Sudo command groups bundle commands into reusable sets.
  - >-
    This plugin reads that policy state for use in playbook conditionals,
    audit tasks, and pre-flight validation. To create, modify, or delete
    sudo objects use the official FreeIPA modules
    C(freeipa.ansible_freeipa.ipasudorule),
    C(freeipa.ansible_freeipa.ipasudocmd), and
    C(freeipa.ansible_freeipa.ipasudocmdgroup).
  - Uses the C(ipalib) framework for all queries. Authentication follows
    the same keytab/password/existing-ticket pattern as other plugins in
    this collection.
options:
  _terms:
    description: >-
      One or more object names to look up when C(operation=show).
      The exact meaning depends on C(sudo_object):
      rule name for C(rule), command path for C(command), and
      command group name for C(commandgroup).
      Not required when C(operation=find).
    type: list
    elements: str
  operation:
    description: >-
      Which operation to perform. C(show) queries each named object and
      returns its configuration. C(find) searches all objects of the
      selected C(sudo_object) type, optionally filtered by C(criteria).
    type: str
    default: show
    choices: ["show", "find"]
  sudo_object:
    description: >-
      Which IdM sudo object type to query. C(rule) inspects sudo rules.
      C(command) inspects individual sudo command objects.
      C(commandgroup) inspects sudo command groups.
    type: str
    default: rule
    choices: ["rule", "command", "commandgroup"]
  criteria:
    description: >-
      Optional search string for C(operation=find). When omitted, all
      objects of the selected C(sudo_object) type are returned.
    type: str
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
    description: The Kerberos principal to authenticate as.
    type: str
    default: admin
  ipaadmin_password:
    description: >-
      Password for the admin principal. Used to obtain a Kerberos ticket
      via C(kinit). Not required if C(kerberos_keytab) is set or a valid
      ticket already exists.
    type: str
    secret: true
    env:
      - name: IPA_ADMIN_PASSWORD
  kerberos_keytab:
    description: >-
      Path to a Kerberos keytab file. Used to obtain a ticket
      non-interactively (required for AAP Execution Environments).
    type: str
    env:
      - name: IPA_KEYTAB
  verify:
    description: >-
      Path to the IPA CA certificate for TLS verification. Set to C(false)
      to skip an explicit CA override and rely on the system trust behavior
      from C(ipalib). Falls back to C(/etc/ipa/ca.crt) when present;
      disables verification with a warning otherwise.
    type: str
    env:
      - name: IPA_CERT
  result_format:
    description: >-
      How to shape the lookup result. C(record) returns a list of records,
      one per object. C(map_record) returns a single dictionary keyed by
      object name.
    type: str
    default: record
    choices: ["record", "map_record"]
notes:
  - This plugin requires C(python3-ipalib) and C(python3-ipaclient) on
    the Ansible controller.
  - "RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)"
  - For objects that do not exist, C(operation=show) returns a record with
    C(exists=false) rather than raising an error, allowing pre-flight
    conditionals without C(ignore_errors).
  - Rule records expose direct member lists, category-wide scope, allowed
    and denied command assignments, RunAs assignments, and enablement state.
  - Command records expose the sudo command path and optional description.
  - Command-group records expose the group members and optional description.
seealso:
  - lookup: eigenstate.ipa.hbacrule
  - lookup: eigenstate.ipa.selinuxmap
  - lookup: eigenstate.ipa.principal
author:
  - Greg Procunier
"""

EXAMPLES = """
# Inspect a named sudo rule before relying on it
- name: Read sudo rule state
  ansible.builtin.set_fact:
    sudo_rule: "{{ lookup('eigenstate.ipa.sudo',
                    'ops-maintenance',
                    sudo_object='rule',
                    server='idm-01.example.com',
                    kerberos_keytab='/etc/admin.keytab') }}"

# Find all sudo command groups
- name: List sudo command groups
  ansible.builtin.set_fact:
    cmd_groups: "{{ lookup('eigenstate.ipa.sudo',
                     operation='find',
                     sudo_object='commandgroup',
                     server='idm-01.example.com',
                     kerberos_keytab='/etc/admin.keytab') }}"

# Inspect a sudo command path directly
- name: Read sudo command object
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.sudo',
             '/usr/bin/systemctl',
             sudo_object='command',
             server='idm-01.example.com',
             kerberos_keytab='/etc/admin.keytab') }}"

# Load several rules as a keyed dict
- name: Build sudo rule map
  ansible.builtin.set_fact:
    sudo_rules: "{{ lookup('eigenstate.ipa.sudo',
                     'ops-maintenance', 'ops-deploy',
                     sudo_object='rule',
                     result_format='map_record',
                     server='idm-01.example.com',
                     kerberos_keytab='/etc/admin.keytab') }}"
"""

RETURN = """
_raw:
  description: >-
    One record per sudo object. When C(result_format=record) (default),
    returns a list of records; a single-term lookup is unwrapped by
    Ansible to a plain dict. When C(result_format=map_record), returns
    a dictionary keyed by object name.
  type: list
  elements: dict
  contains:
    name:
      description: The sudo object name.
      type: str
    object_type:
      description: Which sudo object type this record represents.
      type: str
    exists:
      description: Whether the object is registered in IdM.
      type: bool
    description:
      description: Description field from the object entry, or C(null) if unset.
      type: str
    enabled:
      description: Present on C(rule) records only. Whether the rule is active.
      type: bool
    command:
      description: Present on C(command) records only. The sudo command path.
      type: str
    commands:
      description: Present on C(commandgroup) records only. Member sudo commands.
      type: list
      elements: str
    users:
      description: Present on C(rule) records only. Direct IdM users in scope.
      type: list
      elements: str
    groups:
      description: Present on C(rule) records only. Direct IdM groups in scope.
      type: list
      elements: str
    external_users:
      description: Present on C(rule) records only. External user identities in scope.
      type: list
      elements: str
    hosts:
      description: Present on C(rule) records only. Direct IdM hosts in scope.
      type: list
      elements: str
    hostgroups:
      description: Present on C(rule) records only. Direct IdM host groups in scope.
      type: list
      elements: str
    external_hosts:
      description: Present on C(rule) records only. External hosts in scope.
      type: list
      elements: str
    hostmasks:
      description: Present on C(rule) records only. Network masks in scope.
      type: list
      elements: str
    allow_sudocmds:
      description: Present on C(rule) records only. Direct allowed sudo commands.
      type: list
      elements: str
    allow_sudocmdgroups:
      description: Present on C(rule) records only. Allowed sudo command groups.
      type: list
      elements: str
    deny_sudocmds:
      description: Present on C(rule) records only. Direct denied sudo commands.
      type: list
      elements: str
    deny_sudocmdgroups:
      description: Present on C(rule) records only. Denied sudo command groups.
      type: list
      elements: str
    sudooptions:
      description: Present on C(rule) records only. Sudo options applied by the rule.
      type: list
      elements: str
    usercategory:
      description: Present on C(rule) records only. C(all) when the rule applies to every user.
      type: str
    hostcategory:
      description: Present on C(rule) records only. C(all) when the rule applies to every host.
      type: str
    cmdcategory:
      description: Present on C(rule) records only. C(all) when the rule applies to every command.
      type: str
    runasusercategory:
      description: Present on C(rule) records only. C(all) when the rule applies to every RunAs user.
      type: str
    runasgroupcategory:
      description: Present on C(rule) records only. C(all) when the rule applies to every RunAs group.
      type: str
    runasusers:
      description: Present on C(rule) records only. Direct IdM RunAs users.
      type: list
      elements: str
    external_runasusers:
      description: Present on C(rule) records only. External RunAs users.
      type: list
      elements: str
    runasuser_groups:
      description: Present on C(rule) records only. RunAs user groups.
      type: list
      elements: str
    runasgroups:
      description: Present on C(rule) records only. Direct IdM RunAs groups.
      type: list
      elements: str
    external_runasgroups:
      description: Present on C(rule) records only. External RunAs groups.
      type: list
      elements: str
    order:
      description: Present on C(rule) records only. Numeric sudo rule order.
      type: int
"""

import os
import stat
import subprocess
import shutil
import tempfile

from ansible.errors import AnsibleLookupError
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

try:
    from ipalib import api as _ipa_api
    from ipalib import errors as ipalib_errors
    HAS_IPALIB = True
except ImportError:
    HAS_IPALIB = False

try:
    from ipalib.install.kinit import kinit_password as _kinit_password
    HAS_KINIT_PASSWORD = True
except ImportError:
    try:
        from ipalib.kinit import kinit_password as _kinit_password
        HAS_KINIT_PASSWORD = True
    except ImportError:
        HAS_KINIT_PASSWORD = False

display = Display()


class LookupModule(LookupBase):
    """Query IdM sudo policy objects from FreeIPA/IdM."""

    def __init__(self, *args, **kwargs):
        super(LookupModule, self).__init__(*args, **kwargs)
        self._ccache_path = None
        self._previous_ccache = None
        self._managing_ccache = False

    def _ensure_ipalib(self):
        if not HAS_IPALIB:
            raise AnsibleLookupError(
                "The 'ipalib' Python library is required for the "
                "eigenstate.ipa.sudo lookup plugin.\n"
                "  RHEL/Fedora: dnf install python3-ipalib "
                "python3-ipaclient")

    @staticmethod
    def _resolve_kinit_command():
        preferred = '/usr/bin/kinit'
        if os.path.exists(preferred):
            return preferred

        resolved = shutil.which('kinit')
        if resolved:
            return resolved

        return preferred

    def _kinit_keytab(self, keytab, principal):
        if not os.path.isfile(keytab):
            raise AnsibleLookupError(
                "Kerberos keytab file not found: %s" % keytab)

        self._warn_if_sensitive_file_permissive(keytab, "kerberos_keytab")

        ccache_fd, ccache_path = tempfile.mkstemp(prefix='krb5cc_ipa_sudo_')
        os.close(ccache_fd)
        ccache_env = 'FILE:%s' % ccache_path

        env = os.environ.copy()
        env['KRB5CCNAME'] = ccache_env

        try:
            result = subprocess.run(
                [self._resolve_kinit_command(), '-kt', keytab, principal],
                capture_output=True, text=True, timeout=30, env=env)
        except FileNotFoundError:
            os.remove(ccache_path)
            raise AnsibleLookupError(
                "'kinit' not found. Expected /usr/bin/kinit from krb5-workstation or a PATH-resolved kinit. Install krb5-workstation:\n"
                "  dnf install krb5-workstation")
        except subprocess.TimeoutExpired:
            os.remove(ccache_path)
            raise AnsibleLookupError(
                "'kinit' timed out. Check KDC connectivity and "
                "/etc/krb5.conf.")

        if result.returncode != 0:
            os.remove(ccache_path)
            raise AnsibleLookupError(
                "kinit with keytab failed (exit %d): %s\n"
                "  keytab:    %s\n"
                "  principal: %s\n"
                "Verify: klist -kt %s"
                % (result.returncode, result.stderr.strip(),
                   keytab, principal, keytab))

        self._activate_ccache(ccache_path, ccache_env)
        return ccache_path

    def _kinit_password(self, principal, password):
        ccache_fd, ccache_path = tempfile.mkstemp(prefix='krb5cc_ipa_sudo_')
        os.close(ccache_fd)
        ccache_env = 'FILE:%s' % ccache_path

        if HAS_KINIT_PASSWORD:
            try:
                _kinit_password(principal, password, ccache_path)
            except Exception as exc:
                os.remove(ccache_path)
                raise AnsibleLookupError(
                    "kinit_password failed for '%s': %s"
                    % (principal, to_native(exc)))
        else:
            env = os.environ.copy()
            env['KRB5CCNAME'] = ccache_env
            try:
                result = subprocess.run(
                    [self._resolve_kinit_command(), principal],
                    input=password, capture_output=True, text=True,
                    timeout=30, env=env)
            except FileNotFoundError:
                os.remove(ccache_path)
                raise AnsibleLookupError(
                    "'kinit' not found and ipalib.kinit_password is "
                    "not available. Expected /usr/bin/kinit from krb5-workstation or a PATH-resolved kinit. Install one of:\n"
                    "  dnf install krb5-workstation\n"
                    "  dnf install python3-ipaclient")
            except subprocess.TimeoutExpired:
                os.remove(ccache_path)
                raise AnsibleLookupError(
                    "'kinit' timed out. Check KDC connectivity.")
            if result.returncode != 0:
                os.remove(ccache_path)
                raise AnsibleLookupError(
                    "kinit failed for '%s' (exit %d): %s"
                    % (principal, result.returncode,
                       result.stderr.strip()))

        self._activate_ccache(ccache_path, ccache_env)
        return ccache_path

    def _activate_ccache(self, ccache_path, ccache_env):
        if not self._managing_ccache:
            self._previous_ccache = os.environ.get('KRB5CCNAME')
            self._managing_ccache = True
        self._ccache_path = ccache_path
        os.environ['KRB5CCNAME'] = ccache_env

    def _cleanup_ccache(self):
        if self._managing_ccache and HAS_IPALIB:
            try:
                backend = _ipa_api.Backend.rpcclient
                if backend.isconnected():
                    backend.disconnect()
            except Exception:
                pass
        if self._ccache_path and os.path.exists(self._ccache_path):
            os.remove(self._ccache_path)
        if self._managing_ccache:
            if self._previous_ccache is None:
                os.environ.pop('KRB5CCNAME', None)
            else:
                os.environ['KRB5CCNAME'] = self._previous_ccache
        self._ccache_path = None
        self._previous_ccache = None
        self._managing_ccache = False

    def _default_verify_path(self):
        default_path = '/etc/ipa/ca.crt'
        if os.path.exists(default_path):
            return default_path
        return None

    def _resolve_verify(self, verify):
        if verify is False:
            return False

        if isinstance(verify, str):
            candidate = verify.strip()
            if candidate.lower() in ('false', 'no', 'off', '0'):
                return False
            if not candidate:
                raise AnsibleLookupError(
                    "Invalid verify value ''. Set a CA certificate path or false.")
            if not os.path.exists(candidate):
                raise AnsibleLookupError(
                    "TLS certificate file not found: %s" % candidate)
            return candidate

        if verify is not None:
            raise AnsibleLookupError(
                "Invalid verify value %r. Set a CA certificate path or false."
                % verify)

        default_verify = self._default_verify_path()
        if default_verify is not None:
            return default_verify

        display.warning(
            "TLS verification is disabled for eigenstate.ipa.sudo. "
            "Set 'verify' to the IPA CA certificate path for production use.")
        return False

    def _warn_if_sensitive_file_permissive(self, path, option_name):
        mode = stat.S_IMODE(os.stat(path).st_mode)
        if mode & 0o077:
            display.warning(
                "%s '%s' has permissions %s which are more permissive "
                "than 0600." % (option_name, path, oct(mode)))

    def _connect(self, server, principal, password, keytab, verify):
        if keytab:
            self._kinit_keytab(keytab, principal)
        elif password:
            self._kinit_password(principal, password)
        else:
            if 'KRB5CCNAME' not in os.environ:
                display.warning(
                    "No password or keytab provided and KRB5CCNAME "
                    "is not set. Assuming a valid Kerberos ticket "
                    "exists in the default ccache.")

        if not _ipa_api.isdone('bootstrap'):
            bootstrap_args = {
                'context': 'cli',
                'server': server,
                'log': None,
            }
            if verify:
                bootstrap_args['tls_ca_cert'] = verify

            try:
                _ipa_api.bootstrap(**bootstrap_args)
            except Exception as exc:
                raise AnsibleLookupError(
                    "ipalib bootstrap failed: %s" % to_native(exc))

        if not _ipa_api.isdone('finalize'):
            try:
                _ipa_api.finalize()
            except Exception as exc:
                raise AnsibleLookupError(
                    "ipalib finalize failed: %s" % to_native(exc))

        backend = _ipa_api.Backend.rpcclient
        if not backend.isconnected():
            try:
                backend.connect(ccache=os.environ.get('KRB5CCNAME', None))
            except Exception as exc:
                raise AnsibleLookupError(
                    "Failed to connect to IPA server '%s': %s\n"
                    "Check that a valid Kerberos ticket exists "
                    "(klist) and the server is reachable."
                    % (server, to_native(exc)))

    def _unwrap(self, val, fallback=None):
        if val is None:
            return fallback
        if isinstance(val, (list, tuple)):
            return val[0] if val else fallback
        return val

    def _unwrap_list(self, val):
        if not val:
            return []
        if isinstance(val, (list, tuple)):
            return [to_native(to_text(v, errors='surrogate_or_strict'))
                    for v in val]
        return [to_native(to_text(val, errors='surrogate_or_strict'))]

    def _normalize_text(self, val):
        if val is None:
            return None
        return to_native(to_text(val, errors='surrogate_or_strict'))

    def _normalize_int(self, val):
        raw = self._unwrap(val)
        if raw is None:
            return None
        return int(raw)

    def _rule_record(self, name, entry):
        enabled_raw = self._unwrap(entry.get('ipaenabledflag'))
        if enabled_raw is None:
            enabled = None
        else:
            enabled = self._normalize_text(enabled_raw).upper() == 'TRUE'

            return {
            'name': name,
            'object_type': 'rule',
            'exists': True,
            'description': self._normalize_text(
                self._unwrap(entry.get('description'))),
            'enabled': enabled,
            'usercategory': self._normalize_text(
                self._unwrap(entry.get('usercategory'))),
            'hostcategory': self._normalize_text(
                self._unwrap(entry.get('hostcategory'))),
            'cmdcategory': self._normalize_text(
                self._unwrap(entry.get('cmdcategory'))),
            'runasusercategory': self._normalize_text(
                self._unwrap(entry.get('ipasudorunasusercategory'))),
            'runasgroupcategory': self._normalize_text(
                self._unwrap(entry.get('ipasudorunasgroupcategory'))),
            'users': self._unwrap_list(entry.get('memberuser_user')),
            'groups': self._unwrap_list(entry.get('memberuser_group')),
            'external_users': self._unwrap_list(entry.get('externaluser')),
            'hosts': self._unwrap_list(entry.get('memberhost_host')),
            'hostgroups': self._unwrap_list(entry.get('memberhost_hostgroup')),
            'external_hosts': self._unwrap_list(entry.get('externalhost')),
            'hostmasks': self._unwrap_list(entry.get('hostmask')),
            'allow_sudocmds': self._unwrap_list(
                entry.get('memberallowcmd_sudocmd')),
            'allow_sudocmdgroups': self._unwrap_list(
                entry.get('memberallowcmd_sudocmdgroup')),
            'deny_sudocmds': self._unwrap_list(
                entry.get('memberdenycmd_sudocmd')),
            'deny_sudocmdgroups': self._unwrap_list(
                entry.get('memberdenycmd_sudocmdgroup')),
            'sudooptions': self._unwrap_list(entry.get('ipasudoopt')),
            'runasusers': self._unwrap_list(entry.get('ipasudorunas_user')),
            'external_runasusers': self._unwrap_list(
                entry.get('ipasudorunasextuser')),
            'runasuser_groups': self._unwrap_list(
                entry.get('ipasudorunas_group')),
            'runasgroups': self._unwrap_list(
                entry.get('ipasudorunasgroup_group')),
            'external_runasgroups': self._unwrap_list(
                entry.get('ipasudorunasextgroup')),
            'order': self._normalize_int(entry.get('sudoorder')),
        }

    def _command_record(self, name, entry):
        command = self._normalize_text(
            self._unwrap(entry.get('sudocmd'), fallback=name))
        return {
            'name': command,
            'object_type': 'command',
            'exists': True,
            'description': self._normalize_text(
                self._unwrap(entry.get('description'))),
            'command': command,
        }

    def _commandgroup_record(self, name, entry):
        return {
            'name': name,
            'object_type': 'commandgroup',
            'exists': True,
            'description': self._normalize_text(
                self._unwrap(entry.get('description'))),
            'commands': self._unwrap_list(entry.get('member_sudocmd')),
        }

    def _not_found_record(self, name, sudo_object):
        record = {
            'name': name,
            'object_type': sudo_object,
            'exists': False,
            'description': None,
        }
        if sudo_object == 'rule':
            record.update({
                'enabled': None,
                'usercategory': None,
                'hostcategory': None,
                'cmdcategory': None,
                'runasusercategory': None,
                'runasgroupcategory': None,
                'users': [],
                'groups': [],
                'external_users': [],
                'hosts': [],
                'hostgroups': [],
                'external_hosts': [],
                'hostmasks': [],
                'allow_sudocmds': [],
                'allow_sudocmdgroups': [],
                'deny_sudocmds': [],
                'deny_sudocmdgroups': [],
                'sudooptions': [],
                'runasusers': [],
                'external_runasusers': [],
                'runasuser_groups': [],
                'runasgroups': [],
                'external_runasgroups': [],
                'order': None,
            })
        elif sudo_object == 'command':
            record['command'] = name
        else:
            record['commands'] = []
        return record

    def _build_record(self, sudo_object, name, entry):
        if sudo_object == 'rule':
            return self._rule_record(name, entry)
        if sudo_object == 'command':
            return self._command_record(name, entry)
        return self._commandgroup_record(name, entry)

    def _show_object(self, sudo_object, name):
        try:
            if sudo_object == 'rule':
                result = _ipa_api.Command.sudorule_show(
                    to_text(name, errors='surrogate_or_strict'),
                    all=True, rights=False)
                entry = result.get('result', {})
                entry_name = self._normalize_text(
                    self._unwrap(entry.get('cn'), fallback=name))
            elif sudo_object == 'command':
                result = _ipa_api.Command.sudocmd_show(
                    to_text(name, errors='surrogate_or_strict'),
                    all=True, rights=False)
                entry = result.get('result', {})
                entry_name = self._normalize_text(
                    self._unwrap(entry.get('sudocmd'), fallback=name))
            else:
                result = _ipa_api.Command.sudocmdgroup_show(
                    to_text(name, errors='surrogate_or_strict'),
                    all=True, rights=False)
                entry = result.get('result', {})
                entry_name = self._normalize_text(
                    self._unwrap(entry.get('cn'), fallback=name))
            return self._build_record(sudo_object, entry_name, entry)
        except ipalib_errors.NotFound:
            return self._not_found_record(name, sudo_object)
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to query sudo %s '%s': %s"
                % (sudo_object, name, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to query sudo %s '%s': %s"
                % (sudo_object, name, to_native(exc)))

    def _find_objects(self, criteria, sudo_object):
        search_arg = criteria or ''
        records = []
        try:
            if sudo_object == 'rule':
                result = _ipa_api.Command.sudorule_find(
                    search_arg, sizelimit=0, all=True)
                for entry in result.get('result', []):
                    name = self._normalize_text(
                        self._unwrap(entry.get('cn'), fallback=''))
                    records.append(self._rule_record(name, entry))
            elif sudo_object == 'command':
                result = _ipa_api.Command.sudocmd_find(
                    search_arg, sizelimit=0, all=True)
                for entry in result.get('result', []):
                    name = self._normalize_text(
                        self._unwrap(entry.get('sudocmd'), fallback=''))
                    records.append(self._command_record(name, entry))
            else:
                result = _ipa_api.Command.sudocmdgroup_find(
                    search_arg, sizelimit=0, all=True)
                for entry in result.get('result', []):
                    name = self._normalize_text(
                        self._unwrap(entry.get('cn'), fallback=''))
                    records.append(self._commandgroup_record(name, entry))
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to search sudo %s objects: %s"
                % (sudo_object, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to search sudo %s objects: %s"
                % (sudo_object, to_native(exc)))
        return records

    def _finalize_results(self, results, result_format):
        if result_format == 'map_record':
            return [{item['name']: item for item in results}]
        return results

    def run(self, terms, variables=None, **kwargs):
        try:
            self._ensure_ipalib()
            self.set_options(var_options=variables, direct=kwargs)

            operation = self.get_option('operation')
            server = self.get_option('server')
            if not server:
                raise AnsibleLookupError(
                    "'server' is required. Set it directly or via the "
                    "IPA_SERVER environment variable.")

            principal = self.get_option('ipaadmin_principal')
            password = self.get_option('ipaadmin_password')
            keytab = self.get_option('kerberos_keytab')
            verify = self._resolve_verify(self.get_option('verify'))
            sudo_object = self.get_option('sudo_object')
            criteria = self.get_option('criteria')
            result_format = self.get_option('result_format')

            if operation == 'show':
                if not terms:
                    raise AnsibleLookupError(
                        "operation=show requires at least one sudo object "
                        "name in _terms.")
            elif operation != 'find':
                raise AnsibleLookupError(
                    "Unknown operation '%s'. Use: show, find." % operation)

            self._connect(server, principal, password, keytab, verify)

            if operation == 'find':
                return self._finalize_results(
                    self._find_objects(criteria, sudo_object), result_format)

            results = []
            for term in terms:
                term = to_text(term, errors='surrogate_or_strict')
                results.append(self._show_object(sudo_object, term))

            return self._finalize_results(results, result_format)
        finally:
            self._cleanup_ccache()

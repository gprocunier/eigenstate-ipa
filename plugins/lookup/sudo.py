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
    from ansible_collections.eigenstate.ipa.plugins.module_utils.ipa_client import (
        IPAClient, IPAClientError)
except ImportError:
    import importlib.util
    import pathlib
    _ipa_client_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / 'module_utils' / 'ipa_client.py')
    _ipa_client_spec = importlib.util.spec_from_file_location(
        'eigenstate_ipa_lookup_ipa_client', _ipa_client_path)
    _ipa_client_mod = importlib.util.module_from_spec(_ipa_client_spec)
    _ipa_client_spec.loader.exec_module(_ipa_client_mod)
    IPAClient = _ipa_client_mod.IPAClient
    IPAClientError = _ipa_client_mod.IPAClientError

display = Display()


class LookupModule(LookupBase):
    """Query IdM sudo policy objects from FreeIPA/IdM."""

    def __init__(self, *args, **kwargs):
        super(LookupModule, self).__init__(*args, **kwargs)
        self._ipa_client = IPAClient(warn_callback=lambda msg: display.warning(msg), require_trusted_tls=True)

    def _ensure_ipalib(self):
        try:
            self._ipa_client.api
        except IPAClientError as exc:
            raise AnsibleLookupError(str(exc))

    def _resolve_verify(self, verify):
        try:
            return self._ipa_client.resolve_verify(verify)
        except IPAClientError as exc:
            raise AnsibleLookupError(str(exc))

    def _connect(self, server, principal, password, keytab, verify):
        try:
            self._ipa_client.connect(
                server=server, principal=principal,
                password=password, keytab=keytab, verify=verify)
        except IPAClientError as exc:
            raise AnsibleLookupError(str(exc))

    def _cleanup_ccache(self):
        for attr in ('_ccache_path', '_previous_ccache', '_managing_ccache'):
            if hasattr(self, attr):
                setattr(self._ipa_client, attr, getattr(self, attr))
        self._ipa_client.cleanup.__globals__['_ipa_api'] = _ipa_api
        self._ipa_client.cleanup.__globals__['HAS_IPALIB'] = HAS_IPALIB
        self._ipa_client.cleanup()
        self._sync_legacy_ccache_state()

    def _sync_legacy_ccache_state(self):
        self._ccache_path = self._ipa_client._ccache_path
        self._previous_ccache = self._ipa_client._previous_ccache
        self._managing_ccache = self._ipa_client._managing_ccache

    def _resolve_kinit_command(self):
        return self._ipa_client._resolve_kinit_command()

    def _format_subprocess_stderr(self, stderr, limit=200):
        return self._ipa_client._format_subprocess_stderr(stderr, limit)

    def _activate_ccache(self, ccache_path, ccache_env):
        self._ipa_client._activate_ccache(ccache_path, ccache_env)
        self._sync_legacy_ccache_state()

    def _warn_if_sensitive_file_permissive(self, path, option_name):
        self._ipa_client.warn_if_permissive(path, option_name)

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
        return str(to_text(val, errors='surrogate_or_strict'))

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
                    self._normalize_text(name),
                    all=True, rights=False)
                entry = result.get('result', {})
                entry_name = self._normalize_text(
                    self._unwrap(entry.get('cn'), fallback=name))
            elif sudo_object == 'command':
                result = _ipa_api.Command.sudocmd_show(
                    self._normalize_text(name),
                    all=True, rights=False)
                entry = result.get('result', {})
                entry_name = self._normalize_text(
                    self._unwrap(entry.get('sudocmd'), fallback=name))
            else:
                result = _ipa_api.Command.sudocmdgroup_show(
                    self._normalize_text(name),
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
        search_arg = self._normalize_text(criteria or '')
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

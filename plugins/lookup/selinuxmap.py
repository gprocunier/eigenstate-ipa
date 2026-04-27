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
name: selinuxmap
version_added: "1.6.0"
short_description: Query SELinux user map state from FreeIPA/IdM
description:
  - Returns the configuration of SELinux user map entries registered in
    FreeIPA/IdM, including the SELinux user context assigned, the host and
    user scope, and any linked HBAC rule.
  - SELinux user maps are the FreeIPA mechanism that answers the question
    C(which SELinux user should this identity receive on this host?).
    SSSD and C(pam_selinux) evaluate the map at login and launch the
    session in the mapped context.
  - This plugin reads map state for use in playbook conditionals and
    validation workflows. To create, modify, or delete SELinux user maps
    use C(freeipa.ansible_freeipa.ipaselinuxusermap).
  - Uses the C(ipalib) framework for all queries. Authentication follows
    the same keytab/password/existing-ticket pattern as other plugins in
    this collection.
options:
  _terms:
    description: >-
      One or more SELinux user map names to look up when
      C(operation=show). Not required when C(operation=find).
    type: list
    elements: str
  operation:
    description: >-
      Which operation to perform. C(show) queries each named map and
      returns its configuration. C(find) searches all maps, optionally
      filtered by C(criteria).
    type: str
    default: show
    choices: ["show", "find"]
  criteria:
    description: >-
      Optional search string for C(operation=find). When omitted, all
      SELinux user maps are returned.
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
      How to shape the lookup result. C(record) returns a list of map
      dictionaries, one per entry. C(map_record) returns a single
      dictionary keyed by map name.
    type: str
    default: record
    choices: ["record", "map_record"]
notes:
  - This plugin requires C(python3-ipalib) and C(python3-ipaclient) on
    the Ansible controller.
  - "RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)"
  - For maps that do not exist, C(operation=show) returns a record with
    C(exists=false) rather than raising an error, allowing pre-flight
    conditionals without C(ignore_errors).
  - A map may use either direct user/host scope (members listed in
    C(users), C(groups), C(hosts), C(hostgroups)) or HBAC-linked scope
    (C(hbacrule) is set). These are mutually exclusive in FreeIPA.
  - The SELinux user string in C(selinuxuser) is in the compound form
    required by FreeIPA, C(selinux_user:mls_range), for example
    C(staff_u:s0-s0:c0.c1023).
seealso:
  - lookup: eigenstate.ipa.hbacrule
  - lookup: eigenstate.ipa.principal
  - lookup: eigenstate.ipa.vault
author:
  - Greg Procunier
"""

EXAMPLES = """
# Validate a confinement map exists before proceeding
- name: Assert ops-deploy map is configured
  ansible.builtin.assert:
    that:
      - map_state.exists
      - map_state.enabled
    fail_msg: "SELinux user map 'ops-deploy-map' is missing or disabled"
  vars:
    map_state: "{{ lookup('eigenstate.ipa.selinuxmap',
                   'ops-deploy-map',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/admin.keytab') }}"

# Check what SELinux context a named map assigns
- name: Read SELinux user map configuration
  ansible.builtin.debug:
    msg: "Map {{ map.name }} assigns context {{ map.selinuxuser }} to users {{ map.users }}"
  vars:
    map: "{{ lookup('eigenstate.ipa.selinuxmap',
             'ops-patch-map',
             server='idm-01.example.com',
             ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"

# Find all configured SELinux user maps
- name: List all SELinux user maps
  ansible.builtin.set_fact:
    all_maps: "{{ lookup('eigenstate.ipa.selinuxmap',
                  operation='find',
                  server='idm-01.example.com',
                  kerberos_keytab='/etc/admin.keytab') }}"

# Retrieve multiple maps as a keyed dict
- name: Load map state for several roles
  ansible.builtin.set_fact:
    map_state: "{{ lookup('eigenstate.ipa.selinuxmap',
                   'ops-deploy-map', 'ops-patch-map', 'ops-inventory-map',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/admin.keytab',
                   result_format='map_record') }}"
- ansible.builtin.assert:
    that: map_state['ops-deploy-map'].enabled

# Check whether a map uses HBAC-linked scope
- name: Inspect HBAC linkage on a map
  ansible.builtin.debug:
    msg: "Map is scoped via HBAC rule: {{ map.hbacrule }}"
  when: map.hbacrule is not none
  vars:
    map: "{{ lookup('eigenstate.ipa.selinuxmap',
             'ops-root-local-map',
             server='idm-01.example.com',
             kerberos_keytab='/etc/admin.keytab') }}"
"""

RETURN = """
_raw:
  description: >-
    One configuration record per SELinux user map. When
    C(result_format=record) (default), returns a list of records; a
    single-term lookup is unwrapped by Ansible to a plain dict. When
    C(result_format=map_record), returns a dictionary keyed by map name.
  type: list
  elements: dict
  contains:
    name:
      description: The SELinux user map name.
      type: str
    exists:
      description: Whether the map is registered in IdM.
      type: bool
    selinuxuser:
      description: >-
        The SELinux user string assigned by this map, in compound
        C(selinux_user:mls_range) form (e.g. C(staff_u:s0-s0:c0.c1023)).
        C(null) when C(exists=false).
      type: str
    enabled:
      description: >-
        Whether the map is active. Disabled maps are not evaluated at
        login. C(null) when C(exists=false).
      type: bool
    usercategory:
      description: >-
        C(all) when the map applies to every user regardless of membership.
        C(null) when user scope is determined by C(users) and C(groups).
      type: str
    hostcategory:
      description: >-
        C(all) when the map applies to every host regardless of membership.
        C(null) when host scope is determined by C(hosts) and C(hostgroups).
      type: str
    hbacrule:
      description: >-
        Name of the HBAC rule that provides the combined user and host
        scope for this map. C(null) when the map uses direct membership
        instead of HBAC-linked scope.
      type: str
    users:
      description: >-
        List of IdM users directly in scope for this map. Empty when
        C(usercategory=all) or when scope comes from C(hbacrule).
      type: list
      elements: str
    groups:
      description: >-
        List of IdM groups directly in scope for this map. Empty when
        C(usercategory=all) or when scope comes from C(hbacrule).
      type: list
      elements: str
    hosts:
      description: >-
        List of IdM hosts directly in scope for this map. Empty when
        C(hostcategory=all) or when scope comes from C(hbacrule).
      type: list
      elements: str
    hostgroups:
      description: >-
        List of IdM host groups directly in scope for this map. Empty
        when C(hostcategory=all) or when scope comes from C(hbacrule).
      type: list
      elements: str
    description:
      description: Description field from the map entry, or C(null) if unset.
      type: str
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
    _ipa_api = None
    ipalib_errors = None
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
    """Query SELinux user map state from FreeIPA/IdM."""

    def __init__(self, *args, **kwargs):
        super(LookupModule, self).__init__(*args, **kwargs)
        self._ipa_client = IPAClient(warn_callback=lambda msg: display.warning(msg), require_trusted_tls=True)

    # ------------------------------------------------------------------
    # Auth / connection plumbing — mirrors principal.py exactly.
    # ------------------------------------------------------------------

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
        self._ipa_client.cleanup(ipa_api=_ipa_api, has_ipalib=HAS_IPALIB)
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
        """Return the first element of a list, or the value itself."""
        if val is None:
            return fallback
        if isinstance(val, (list, tuple)):
            return val[0] if val else fallback
        return val

    def _unwrap_list(self, val):
        """Return a list of native strings, or an empty list."""
        if not val:
            return []
        if isinstance(val, (list, tuple)):
            return [to_native(to_text(v, errors='surrogate_or_strict'))
                    for v in val]
        return [to_native(to_text(val, errors='surrogate_or_strict'))]

    def _extract_cn_from_dn(self, dn_val):
        """Extract the CN value from a FreeIPA DN string.

        FreeIPA returns C(seealso) as a DN like
        C(cn=allow_all,cn=hbac,dc=example,dc=com). This method extracts
        the first CN component, returning C(None) when C(dn_val) is absent.
        """
        if not dn_val:
            return None
        dn_str = to_native(to_text(dn_val, errors='surrogate_or_strict'))
        first = dn_str.split(',')[0]
        if '=' in first:
            return first.split('=', 1)[1]
        return dn_str

    def _build_record(self, name, r):
        """Build a selinuxmap result record from an ipalib result dict."""
        selinuxuser_raw = self._unwrap(r.get('ipaselinuxuser'))
        selinuxuser = (to_native(to_text(selinuxuser_raw,
                                         errors='surrogate_or_strict'))
                       if selinuxuser_raw is not None else None)

        enabled_raw = self._unwrap(r.get('ipaenabledflag'))
        if enabled_raw is None:
            enabled = None
        else:
            enabled = to_native(
                to_text(enabled_raw,
                        errors='surrogate_or_strict')).upper() == 'TRUE'

        usercategory_raw = self._unwrap(r.get('usercategory'))
        usercategory = (to_native(to_text(usercategory_raw,
                                           errors='surrogate_or_strict'))
                        if usercategory_raw is not None else None)

        hostcategory_raw = self._unwrap(r.get('hostcategory'))
        hostcategory = (to_native(to_text(hostcategory_raw,
                                           errors='surrogate_or_strict'))
                        if hostcategory_raw is not None else None)

        seealso_raw = self._unwrap(r.get('seealso'))
        hbacrule = self._extract_cn_from_dn(seealso_raw)

        desc_raw = self._unwrap(r.get('description'))
        description = (to_native(to_text(desc_raw,
                                          errors='surrogate_or_strict'))
                       if desc_raw is not None else None)

        return {
            'name': name,
            'exists': True,
            'selinuxuser': selinuxuser,
            'enabled': enabled,
            'usercategory': usercategory,
            'hostcategory': hostcategory,
            'hbacrule': hbacrule,
            'users': self._unwrap_list(r.get('memberuser_user')),
            'groups': self._unwrap_list(r.get('memberuser_group')),
            'hosts': self._unwrap_list(r.get('memberhost_host')),
            'hostgroups': self._unwrap_list(r.get('memberhost_hostgroup')),
            'description': description,
        }

    def _not_found_record(self, name):
        """Return a record for a map that does not exist in IdM."""
        return {
            'name': name,
            'exists': False,
            'selinuxuser': None,
            'enabled': None,
            'usercategory': None,
            'hostcategory': None,
            'hbacrule': None,
            'users': [],
            'groups': [],
            'hosts': [],
            'hostgroups': [],
            'description': None,
        }

    def _show_map(self, name):
        """Query IdM for a single SELinux user map by name."""
        try:
            result = _ipa_api.Command.selinuxusermap_show(
                to_text(name, errors='surrogate_or_strict'),
                all=True, rights=False)
            r = result.get('result', {})
            cn = self._unwrap(r.get('cn'), fallback=name)
            return self._build_record(
                to_native(to_text(cn, errors='surrogate_or_strict')), r)
        except ipalib_errors.NotFound:
            return self._not_found_record(name)
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to query SELinux user map '%s': %s"
                % (name, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to query SELinux user map '%s': %s"
                % (name, to_native(exc)))

    def _find_maps(self, criteria):
        """Search IdM for SELinux user maps and return a list of records."""
        search_arg = criteria or ''
        records = []
        try:
            result = _ipa_api.Command.selinuxusermap_find(
                search_arg, sizelimit=0, all=True)
            for entry in result.get('result', []):
                cn_raw = self._unwrap(entry.get('cn'), fallback='')
                cn = to_native(to_text(cn_raw, errors='surrogate_or_strict'))
                records.append(self._build_record(cn, entry))
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to search SELinux user maps: %s"
                % to_native(exc))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to search SELinux user maps: %s" % to_native(exc))
        return records

    def _finalize_results(self, results, result_format):
        """Apply the requested top-level result container shape."""
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
            criteria = self.get_option('criteria')
            result_format = self.get_option('result_format')

            if operation == 'show':
                if not terms:
                    raise AnsibleLookupError(
                        "operation=show requires at least one map name "
                        "in _terms.")
            elif operation == 'find':
                pass
            else:
                raise AnsibleLookupError(
                    "Unknown operation '%s'. Use: show, find." % operation)

            self._connect(server, principal, password, keytab, verify)

            if operation == 'find':
                return self._finalize_results(
                    self._find_maps(criteria), result_format)

            results = []
            for term in terms:
                term = to_text(term, errors='surrogate_or_strict')
                results.append(self._show_map(term))

            return self._finalize_results(results, result_format)

        finally:
            self._cleanup_ccache()

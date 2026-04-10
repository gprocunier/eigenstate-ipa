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
name: hbacrule
version_added: "1.6.0"
short_description: Query HBAC rule state and run access tests against FreeIPA/IdM
description:
  - Returns the configuration of Host-Based Access Control (HBAC) rules
    registered in FreeIPA/IdM, including the identities and hosts in scope
    and whether the rule is currently active.
  - Can also invoke the FreeIPA C(hbactest) engine (C(operation=test)) to
    determine whether a specific user would be granted access to a specific
    host and service. This is the server-side evaluation of all applicable
    HBAC rules — the same logic SSSD uses at login.
  - HBAC rules are a dual-purpose object in FreeIPA. They control access
    directly, and they also provide the combined identity-and-host scope for
    SELinux user maps when a map is configured with HBAC-linked scope
    (C(seealso) set). Reading HBAC state is therefore a prerequisite for
    validating the full confinement model.
  - This plugin reads HBAC state for use in playbook conditionals and
    validation workflows. To create, modify, or delete HBAC rules use
    C(freeipa.ansible_freeipa.ipahbacrule).
  - Uses the C(ipalib) framework for all queries. Authentication follows
    the same keytab/password/existing-ticket pattern as other plugins in
    this collection.
options:
  _terms:
    description: >-
      For C(operation=show): one or more HBAC rule names to look up.
      For C(operation=test), the single username to test access for.
      Not required when C(operation=find).
    type: list
    elements: str
  operation:
    description: >-
      Which operation to perform. C(show) queries each named rule and
      returns its configuration. C(find) searches all rules, optionally
      filtered by C(criteria). C(test) invokes the FreeIPA C(hbactest)
      engine to evaluate whether C(_terms[0]) (the username) would be
      allowed to access C(targethost) via C(service).
    type: str
    default: show
    choices: ["show", "find", "test"]
  criteria:
    description: >-
      Optional search string for C(operation=find). When omitted, all
      HBAC rules are returned.
    type: str
  targethost:
    description: >-
      The fully-qualified host name to test against. Required for
      C(operation=test).
    type: str
  service:
    description: >-
      The HBAC service name to test against (e.g. C(sshd), C(sudo)).
      Required for C(operation=test).
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
      How to shape the lookup result for C(operation=show) and
      C(operation=find). C(record) returns a list of rule dictionaries,
      one per entry. C(map_record) returns a single dictionary keyed by
      rule name. Ignored for C(operation=test).
    type: str
    default: record
    choices: ["record", "map_record"]
notes:
  - This plugin requires C(python3-ipalib) and C(python3-ipaclient) on
    the Ansible controller.
  - "RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)"
  - For rules that do not exist, C(operation=show) returns a record with
    C(exists=false) rather than raising an error, allowing pre-flight
    conditionals without C(ignore_errors).
  - C(operation=test) evaluates all applicable HBAC rules on the server.
    The C(denied) field is C(true) when access would be blocked. The
    C(matched) and C(notmatched) fields list every rule the server
    considered, which is useful for diagnosing unexpected allow or deny
    results.
  - C(operation=test) requires that the test user and target host exist in
    FreeIPA. The test does not create authentication sessions — it is a
    dry-run policy evaluation only.
seealso:
  - lookup: eigenstate.ipa.selinuxmap
  - lookup: eigenstate.ipa.principal
  - lookup: eigenstate.ipa.vault
author:
  - Greg Procunier
"""

EXAMPLES = """
# Validate that a named HBAC rule exists and is enabled
- name: Assert ops-deploy HBAC rule is active
  ansible.builtin.assert:
    that:
      - rule.exists
      - rule.enabled
    fail_msg: "HBAC rule 'ops-deploy' is missing or disabled"
  vars:
    rule: "{{ lookup('eigenstate.ipa.hbacrule',
               'ops-deploy',
               server='idm-01.example.com',
               kerberos_keytab='/etc/admin.keytab') }}"

# Test whether an automation account would be allowed to SSH to a host
- name: Verify automation-svc access before deploying
  ansible.builtin.assert:
    that: not access.denied
    fail_msg: >-
      automation-svc would be denied SSH on {{ inventory_hostname }}.
      Matched: {{ access.matched }}, Not matched: {{ access.notmatched }}
  vars:
    access: "{{ lookup('eigenstate.ipa.hbacrule',
                'automation-svc',
                operation='test',
                targethost=inventory_hostname,
                service='sshd',
                server='idm-01.example.com',
                kerberos_keytab='/etc/admin.keytab') }}"

# Find all enabled HBAC rules and log their names
- name: List all HBAC rules
  ansible.builtin.set_fact:
    all_rules: "{{ lookup('eigenstate.ipa.hbacrule',
                   operation='find',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/admin.keytab') }}"

# Retrieve multiple rules as a keyed dict
- name: Load rule state for several automation identities
  ansible.builtin.set_fact:
    rule_state: "{{ lookup('eigenstate.ipa.hbacrule',
                    'ops-deploy', 'ops-patch', 'ops-inventory',
                    server='idm-01.example.com',
                    kerberos_keytab='/etc/admin.keytab',
                    result_format='map_record') }}"
- ansible.builtin.assert:
    that: rule_state['ops-deploy'].enabled

# Inspect which services an HBAC rule permits
- name: Check allowed services for a rule
  ansible.builtin.debug:
    msg: >-
      Rule {{ rule.name }} allows services {{ rule.services }}
      and service groups {{ rule.servicegroups }}
  vars:
    rule: "{{ lookup('eigenstate.ipa.hbacrule',
               'ops-deploy',
               server='idm-01.example.com',
               kerberos_keytab='/etc/admin.keytab') }}"
"""

RETURN = """
_raw:
  description: >-
    For C(operation=show) and C(operation=find): one configuration record
    per HBAC rule. When C(result_format=record) (default), returns a list
    of records; a single-term lookup is unwrapped by Ansible to a plain
    dict. When C(result_format=map_record), returns a dictionary keyed by
    rule name.

    For C(operation=test), a single access test result record.
  type: list
  elements: dict
  contains:
    name:
      description: The HBAC rule name. Present on C(show)/C(find) records.
      type: str
    exists:
      description: >-
        Whether the rule is registered in IdM. Present on C(show)/C(find)
        records only.
      type: bool
    enabled:
      description: >-
        Whether the rule is currently active. Disabled rules are not
        evaluated by SSSD. C(null) when C(exists=false).
      type: bool
    usercategory:
      description: >-
        C(all) when the rule applies to every user. C(null) when user
        scope is defined by C(users) and C(groups).
      type: str
    hostcategory:
      description: >-
        C(all) when the rule applies to every host. C(null) when host
        scope is defined by C(hosts) and C(hostgroups).
      type: str
    servicecategory:
      description: >-
        C(all) when the rule applies to every service. C(null) when
        service scope is defined by C(services) and C(servicegroups).
      type: str
    users:
      description: >-
        List of IdM users directly in scope for this rule. Empty when
        C(usercategory=all).
      type: list
      elements: str
    groups:
      description: >-
        List of IdM user groups directly in scope for this rule. Empty
        when C(usercategory=all).
      type: list
      elements: str
    hosts:
      description: >-
        List of IdM hosts directly in scope for this rule. Empty when
        C(hostcategory=all).
      type: list
      elements: str
    hostgroups:
      description: >-
        List of IdM host groups directly in scope for this rule. Empty
        when C(hostcategory=all).
      type: list
      elements: str
    services:
      description: >-
        List of HBAC services directly in scope for this rule. Empty
        when C(servicecategory=all).
      type: list
      elements: str
    servicegroups:
      description: >-
        List of HBAC service groups directly in scope for this rule.
        Empty when C(servicecategory=all).
      type: list
      elements: str
    description:
      description: Description field from the rule entry, or C(null) if unset.
      type: str
    user:
      description: >-
        The username that was tested. Present on C(test) records only.
      type: str
    targethost:
      description: >-
        The host name that was tested. Present on C(test) records only.
      type: str
    service:
      description: >-
        The service name that was tested. Present on C(test) records only.
      type: str
    matched:
      description: >-
        List of HBAC rules that matched and granted access during the test.
        Present on C(test) records only.
      type: list
      elements: str
    notmatched:
      description: >-
        List of HBAC rules that were evaluated but did not match during the
        test. Present on C(test) records only.
      type: list
      elements: str
    denied:
      description: >-
        C(true) when the C(hbactest) engine determined that access would be
        denied. C(false) when at least one rule would grant access.
        Present on C(test) records only.
      type: bool
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
    """Query HBAC rule state and run access tests against FreeIPA/IdM."""

    def __init__(self, *args, **kwargs):
        super(LookupModule, self).__init__(*args, **kwargs)
        self._ccache_path = None
        self._previous_ccache = None
        self._managing_ccache = False

    # ------------------------------------------------------------------
    # Auth / connection plumbing — mirrors principal.py exactly.
    # ------------------------------------------------------------------

    def _ensure_ipalib(self):
        if not HAS_IPALIB:
            raise AnsibleLookupError(
                "The 'ipalib' Python library is required for the "
                "eigenstate.ipa.hbacrule lookup plugin.\n"
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


    @staticmethod
    def _format_subprocess_stderr(stderr, limit=200):
        text = to_native(stderr or '').strip()
        if not text:
            return 'no stderr output'

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return 'no stderr output'

        summary = ' | '.join(lines[:2])
        if len(summary) > limit:
            return summary[:limit - 3].rstrip() + '...'

        return summary

    def _kinit_keytab(self, keytab, principal):
        """Obtain a Kerberos ticket from a keytab file."""
        if not os.path.isfile(keytab):
            raise AnsibleLookupError(
                "Kerberos keytab file not found: %s" % keytab)

        self._warn_if_sensitive_file_permissive(keytab, "kerberos_keytab")

        ccache_fd, ccache_path = tempfile.mkstemp(
            prefix='krb5cc_ipa_hbacrule_')
        os.close(ccache_fd)
        ccache_env = 'FILE:%s' % ccache_path

        env = os.environ.copy()
        env['KRB5CCNAME'] = ccache_env

        try:
            result = subprocess.run(
                [self._resolve_kinit_command(), '-kt', keytab, principal],
                capture_output=True, text=True, timeout=30,
                env=env)
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
                "Verify the keytab with: klist -kt %s"
                % (result.returncode, self._format_subprocess_stderr(result.stderr),
                   keytab))

        self._activate_ccache(ccache_path, ccache_env)
        return ccache_path

    def _kinit_password(self, principal, password):
        """Obtain a Kerberos ticket from a password."""
        ccache_fd, ccache_path = tempfile.mkstemp(
            prefix='krb5cc_ipa_hbacrule_')
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
                       self._format_subprocess_stderr(result.stderr)))

        self._activate_ccache(ccache_path, ccache_env)
        return ccache_path

    def _activate_ccache(self, ccache_path, ccache_env):
        """Track and activate a managed Kerberos credential cache."""
        if not self._managing_ccache:
            self._previous_ccache = os.environ.get('KRB5CCNAME')
            self._managing_ccache = True
        self._ccache_path = ccache_path
        os.environ['KRB5CCNAME'] = ccache_env

    def _cleanup_ccache(self):
        """Remove any managed Kerberos credential cache and restore env."""
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
        """Return the conventional IPA CA path when it exists locally."""
        default_path = '/etc/ipa/ca.crt'
        if os.path.exists(default_path):
            return default_path
        return None

    def _resolve_verify(self, verify):
        """Resolve TLS verification behavior for lookup requests."""
        if verify is False:
            return False

        if isinstance(verify, str):
            candidate = verify.strip()
            if candidate.lower() in ('false', 'no', 'off', '0'):
                return False
            if not candidate:
                raise AnsibleLookupError(
                    "Invalid verify value ''. Set a CA certificate path "
                    "or false.")
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
            "TLS verification is disabled for eigenstate.ipa.hbacrule. "
            "Set 'verify' to the IPA CA certificate path for production use.")
        return False

    def _warn_if_sensitive_file_permissive(self, path, option_name):
        """Warn when sensitive local files are readable by non-owners."""
        mode = stat.S_IMODE(os.stat(path).st_mode)
        if mode & 0o077:
            display.warning(
                "%s '%s' has permissions %s which are more permissive "
                "than 0600." % (option_name, path, oct(mode)))

    def _connect(self, server, principal, password, keytab, verify):
        """Authenticate and connect to the IPA server."""
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
                backend.connect(
                    ccache=os.environ.get('KRB5CCNAME', None))
            except Exception as exc:
                raise AnsibleLookupError(
                    "Failed to connect to IPA server '%s': %s\n"
                    "Check that a valid Kerberos ticket exists "
                    "(klist) and the server is reachable."
                    % (server, to_native(exc)))

    # ------------------------------------------------------------------
    # HBAC rule helpers
    # ------------------------------------------------------------------

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

    def _build_record(self, name, r):
        """Build an HBAC rule result record from an ipalib result dict."""
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

        servicecategory_raw = self._unwrap(r.get('servicecategory'))
        servicecategory = (to_native(to_text(servicecategory_raw,
                                             errors='surrogate_or_strict'))
                           if servicecategory_raw is not None else None)

        desc_raw = self._unwrap(r.get('description'))
        description = (to_native(to_text(desc_raw,
                                         errors='surrogate_or_strict'))
                       if desc_raw is not None else None)

        return {
            'name': name,
            'exists': True,
            'enabled': enabled,
            'usercategory': usercategory,
            'hostcategory': hostcategory,
            'servicecategory': servicecategory,
            'users': self._unwrap_list(r.get('memberuser_user')),
            'groups': self._unwrap_list(r.get('memberuser_group')),
            'hosts': self._unwrap_list(r.get('memberhost_host')),
            'hostgroups': self._unwrap_list(r.get('memberhost_hostgroup')),
            'services': self._unwrap_list(r.get('memberservice_hbacsvc')),
            'servicegroups': self._unwrap_list(
                r.get('memberservice_hbacsvcgroup')),
            'description': description,
        }

    def _not_found_record(self, name):
        """Return a record for a rule that does not exist in IdM."""
        return {
            'name': name,
            'exists': False,
            'enabled': None,
            'usercategory': None,
            'hostcategory': None,
            'servicecategory': None,
            'users': [],
            'groups': [],
            'hosts': [],
            'hostgroups': [],
            'services': [],
            'servicegroups': [],
            'description': None,
        }

    def _show_rule(self, name):
        """Query IdM for a single HBAC rule by name."""
        try:
            result = _ipa_api.Command.hbacrule_show(
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
                "Not authorized to query HBAC rule '%s': %s"
                % (name, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to query HBAC rule '%s': %s"
                % (name, to_native(exc)))

    def _find_rules(self, criteria):
        """Search IdM for HBAC rules and return a list of records."""
        search_arg = criteria or ''
        records = []
        try:
            result = _ipa_api.Command.hbacrule_find(
                search_arg, sizelimit=0, all=True)
            for entry in result.get('result', []):
                cn_raw = self._unwrap(entry.get('cn'), fallback='')
                cn = to_native(to_text(cn_raw, errors='surrogate_or_strict'))
                records.append(self._build_record(cn, entry))
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to search HBAC rules: %s" % to_native(exc))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to search HBAC rules: %s" % to_native(exc))
        return records

    def _test_access(self, user, targethost, service):
        """Invoke hbactest and return an access test result record.

        FreeIPA returns::

            {
                'result': {
                    'matched':    [...rule names...],
                    'notmatched': [...rule names...],
                    'error':      [...],
                    'value':      True   # True = access granted
                }
            }

        ``denied`` inverts ``value`` so that the caller can write
        ``assert not access.denied`` to express "access must be allowed".
        """
        try:
            result = _ipa_api.Command.hbactest(
                user=to_text(user, errors='surrogate_or_strict'),
                targethost=to_text(targethost, errors='surrogate_or_strict'),
                service=to_text(service, errors='surrogate_or_strict'),
                nodetail=False)
            r = result.get('result', result)
            granted = bool(r.get('value', False))
            return {
                'user': to_native(to_text(user,
                                          errors='surrogate_or_strict')),
                'targethost': to_native(
                    to_text(targethost, errors='surrogate_or_strict')),
                'service': to_native(
                    to_text(service, errors='surrogate_or_strict')),
                'matched': self._unwrap_list(r.get('matched')),
                'notmatched': self._unwrap_list(r.get('notmatched')),
                'denied': not granted,
            }
        except ipalib_errors.NotFound as exc:
            raise AnsibleLookupError(
                "hbactest failed: user, host, or service not found "
                "in IdM: %s" % to_native(exc))
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to run hbactest: %s" % to_native(exc))
        except Exception as exc:
            raise AnsibleLookupError(
                "hbactest failed for user='%s' targethost='%s' "
                "service='%s': %s"
                % (user, targethost, service, to_native(exc)))

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
            targethost = self.get_option('targethost')
            service = self.get_option('service')

            if operation == 'show':
                if not terms:
                    raise AnsibleLookupError(
                        "operation=show requires at least one rule name "
                        "in _terms.")
            elif operation == 'find':
                pass
            elif operation == 'test':
                if not terms:
                    raise AnsibleLookupError(
                        "operation=test requires a username in _terms.")
                if not targethost:
                    raise AnsibleLookupError(
                        "operation=test requires 'targethost'.")
                if not service:
                    raise AnsibleLookupError(
                        "operation=test requires 'service'.")
            else:
                raise AnsibleLookupError(
                    "Unknown operation '%s'. Use: show, find, test."
                    % operation)

            self._connect(server, principal, password, keytab, verify)

            if operation == 'find':
                return self._finalize_results(
                    self._find_rules(criteria), result_format)

            if operation == 'test':
                user = to_text(terms[0], errors='surrogate_or_strict')
                return [self._test_access(user, targethost, service)]

            # operation == 'show'
            results = []
            for term in terms:
                term = to_text(term, errors='surrogate_or_strict')
                results.append(self._show_rule(term))

            return self._finalize_results(results, result_format)

        finally:
            self._cleanup_ccache()

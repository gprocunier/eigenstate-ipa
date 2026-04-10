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
name: principal
version_added: "1.3.0"
short_description: Query Kerberos principal state from FreeIPA/IDM
description:
  - Returns the existence, key state, lock state, and last authentication
    timestamp for Kerberos principals registered in FreeIPA/IDM.
  - Supports user, host, and service principal types with auto-detection
    from the principal name format.
  - Uses the C(ipalib) framework for all queries. Authentication follows
    the same keytab/password/existing-ticket pattern as other plugins in
    this collection.
  - Intended as a pre-flight check before keytab issuance, cert requests,
    or enrollment operations that silently fail when the target principal
    is absent or has no keys.
options:
  _terms:
    description: >-
      One or more principal names to inspect when C(operation=show).
      Accepts any of: C(HTTP/host.example.com), C(host/host.example.com),
      C(HTTP/host.example.com@REALM), C(admin), C(admin@REALM).
      Not required when C(operation=find).
    type: list
    elements: str
  operation:
    description: >-
      Which operation to perform. C(show) queries each named principal
      and returns its state. C(find) searches for principals matching
      optional C(criteria) within the specified C(principal_type).
    type: str
    default: show
    choices: ["show", "find"]
  principal_type:
    description: >-
      Which IdM object class to query. C(auto) detects from the principal
      name format: names containing C(/) are treated as service or host
      principals; names without C(/) are treated as users. C(host) expects
      C(host/fqdn) form or a bare FQDN. Required (non-auto) when
      C(operation=find).
    type: str
    default: auto
    choices: ["auto", "user", "host", "service"]
  criteria:
    description: >-
      Optional search string for C(operation=find). When omitted, all
      principals of the selected type are returned.
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
      Password for the admin principal. The plugin uses this to obtain a
      Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is
      set or a valid ticket already exists.
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
      from C(ipalib). Falls back to C(/etc/ipa/ca.crt) when present; disables
      verification with a warning otherwise.
    type: str
    env:
      - name: IPA_CERT
  result_format:
    description: >-
      How to shape the lookup result. C(record) returns a list of state
      dictionaries, one per principal. C(map_record) returns a single
      dictionary keyed by the input principal name.
    type: str
    default: record
    choices: ["record", "map_record"]
notes:
  - This plugin requires C(python3-ipalib) and C(python3-ipaclient) on
    the Ansible controller.
  - "RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)"
  - For principals that do not exist, the plugin returns a record with
    C(exists=false) rather than raising an error, allowing pre-flight
    conditionals without C(ignore_errors).
  - C(disabled) is C(null) for host and service principals because IdM
    does not expose a lock state for those object types through the same
    mechanism as user accounts.
  - C(last_auth) is populated only for user principals that have the
    C(krblastsuccessfulauth) attribute set in IdM (requires auditing
    to be enabled on the IdM server).
seealso:
  - lookup: eigenstate.ipa.keytab
  - lookup: eigenstate.ipa.cert
  - lookup: eigenstate.ipa.vault
author:
  - Greg Procunier
"""

EXAMPLES = """
# Check whether a service principal exists and has keys
- name: Pre-flight check before keytab issuance
  ansible.builtin.assert:
    that:
      - principal_state.exists
      - principal_state.has_keytab
    fail_msg: "Service principal is missing or has no keys"
  vars:
    principal_state: "{{ lookup('eigenstate.ipa.principal',
                          'HTTP/web01.example.com',
                          server='idm-01.example.com',
                          ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"

# Check a host principal
- name: Verify host enrolled before requesting cert
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.principal',
             'host/node01.example.com',
             server='idm-01.example.com',
             kerberos_keytab='/etc/admin.keytab') }}"

# Check a user principal for lock state
- name: Inspect user principal state
  ansible.builtin.set_fact:
    user_state: "{{ lookup('eigenstate.ipa.principal',
                    'svc-deploy',
                    server='idm-01.example.com',
                    kerberos_keytab='/etc/admin.keytab') }}"
- ansible.builtin.debug:
    msg: "Account locked: {{ user_state.disabled }}, last auth: {{ user_state.last_auth }}"

# Multiple principals in one lookup
- name: Pre-flight for several services
  ansible.builtin.set_fact:
    states: "{{ lookup('eigenstate.ipa.principal',
                'HTTP/web01.example.com', 'ldap/ldap01.example.com',
                server='idm-01.example.com',
                kerberos_keytab='/etc/admin.keytab') }}"

# Named mapping of multiple principals
- name: Pre-flight map for several services
  ansible.builtin.set_fact:
    state_map: "{{ lookup('eigenstate.ipa.principal',
                   'HTTP/web01.example.com', 'ldap/ldap01.example.com',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/admin.keytab',
                   result_format='map_record') }}"

# Find all service principals
- name: List all registered services
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.principal',
             operation='find',
             principal_type='service',
             server='idm-01.example.com',
             kerberos_keytab='/etc/admin.keytab') }}"

# Find service principals matching a pattern
- name: Find HTTP services
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.principal',
             operation='find',
             principal_type='service',
             criteria='HTTP',
             server='idm-01.example.com',
             kerberos_keytab='/etc/admin.keytab') }}"

# Use with environment variables
- name: Check principal using env-backed auth
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.principal', 'HTTP/web01.example.com') }}"
"""

RETURN = """
_raw:
  description: >-
    One state record per principal. Each record is a dictionary with
    the fields below. When C(result_format=record) (default), returns
    a list of records; a single-term lookup is unwrapped by Ansible to
    a plain dict. When C(result_format=map_record), the lookup returns a
    dictionary keyed by the input principal name.
  type: list
  elements: dict
  contains:
    name:
      description: The input principal name as given.
      type: str
    canonical:
      description: >-
        The canonical Kerberos principal name as stored in IdM, including
        the realm suffix (e.g. C(HTTP/web01.example.com@EXAMPLE.COM)).
        For host principals this is the C(host/fqdn@REALM) form.
        Set to the input name when the principal does not exist.
      type: str
    type:
      description: The IdM object class — C(user), C(host), or C(service).
      type: str
    exists:
      description: Whether the principal is registered in IdM.
      type: bool
    has_keytab:
      description: >-
        Whether the principal has at least one Kerberos key (keytab) issued.
        Always C(false) when C(exists=false).
      type: bool
    disabled:
      description: >-
        Whether the account is locked. Populated for user principals only;
        C(null) for host and service principals.
      type: bool
    last_auth:
      description: >-
        ISO 8601 timestamp of the last successful Kerberos authentication,
        from C(krblastsuccessfulauth). C(null) when unknown or not recorded.
        Populated for user principals only.
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
    """Query Kerberos principal state from FreeIPA/IdM."""

    def __init__(self, *args, **kwargs):
        super(LookupModule, self).__init__(*args, **kwargs)
        self._ccache_path = None
        self._previous_ccache = None
        self._managing_ccache = False

    # ------------------------------------------------------------------
    # Auth / connection plumbing — mirrors vault.py exactly.
    # Only the ccache prefix and plugin name in messages differ.
    # ------------------------------------------------------------------

    def _ensure_ipalib(self):
        if not HAS_IPALIB:
            raise AnsibleLookupError(
                "The 'ipalib' Python library is required for the "
                "eigenstate.ipa.principal lookup plugin.\n"
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
        """Obtain a Kerberos ticket from a keytab file."""
        if not os.path.isfile(keytab):
            raise AnsibleLookupError(
                "Kerberos keytab file not found: %s" % keytab)

        self._warn_if_sensitive_file_permissive(keytab, "kerberos_keytab")

        ccache_fd, ccache_path = tempfile.mkstemp(
            prefix='krb5cc_ipa_principal_')
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
                "  keytab:    %s\n"
                "  principal: %s\n"
                "Verify: klist -kt %s"
                % (result.returncode, result.stderr.strip(),
                   keytab, principal, keytab))

        self._activate_ccache(ccache_path, ccache_env)
        return ccache_path

    def _kinit_password(self, principal, password):
        """Obtain a Kerberos ticket from a password."""
        ccache_fd, ccache_path = tempfile.mkstemp(
            prefix='krb5cc_ipa_principal_')
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
            "TLS verification is disabled for eigenstate.ipa.principal. "
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
    # Principal-specific helpers
    # ------------------------------------------------------------------

    def _unwrap(self, val, fallback=None):
        """Return the first element of a list, or the value itself."""
        if val is None:
            return fallback
        if isinstance(val, (list, tuple)):
            return val[0] if val else fallback
        return val

    def _ipadate_to_str(self, val):
        """Convert an ipalib date value to an ISO 8601 string or None."""
        if val is None:
            return None
        if hasattr(val, 'isoformat'):
            return val.isoformat()
        return to_native(str(val))

    def _detect_principal_type(self, name):
        """Auto-detect principal type and extract the ipalib lookup argument.

        Returns (ptype, lookup_arg) where ptype is 'user', 'host', or
        'service' and lookup_arg is the value to pass to the ipalib command.
        """
        bare = name.split('@')[0]
        if '/' in bare:
            service_part = bare.split('/')[0].lower()
            if service_part == 'host':
                fqdn = bare.split('/', 1)[1]
                return 'host', fqdn
            return 'service', bare
        return 'user', bare

    def _resolve_principal_type(self, name, override):
        """Return (ptype, lookup_arg), applying an explicit type override."""
        if override == 'auto':
            return self._detect_principal_type(name)

        if override == 'user':
            uid = name.split('@')[0]
            return 'user', uid

        if override == 'host':
            bare = name.split('@')[0]
            if bare.lower().startswith('host/'):
                fqdn = bare.split('/', 1)[1]
            elif '/' not in bare:
                fqdn = bare
            else:
                raise AnsibleLookupError(
                    "Cannot interpret '%s' as a host principal with "
                    "principal_type=host. Use 'host/fqdn' or a bare "
                    "FQDN." % name)
            return 'host', fqdn

        if override == 'service':
            bare = name.split('@')[0]
            return 'service', bare

        raise AnsibleLookupError(
            "Unknown principal_type '%s'. Use: auto, user, host, "
            "service." % override)

    def _not_found_record(self, name, ptype):
        """Return a state record for a principal that does not exist."""
        return {
            'name': name,
            'canonical': name,
            'type': ptype,
            'exists': False,
            'has_keytab': False,
            'disabled': None,
            'last_auth': None,
        }

    def _show_principal(self, name, principal_type_override):
        """Query IdM for a single principal and return its state record."""
        ptype, lookup_arg = self._resolve_principal_type(
            name, principal_type_override)

        try:
            if ptype == 'service':
                result = _ipa_api.Command.service_show(
                    lookup_arg, all=True, rights=False)
                r = result.get('result', {})
                canonical = self._unwrap(
                    r.get('krbcanonicalname') or r.get('krbprincipalname'),
                    fallback=name)
                return {
                    'name': name,
                    'canonical': to_text(
                        canonical, errors='surrogate_or_strict'),
                    'type': 'service',
                    'exists': True,
                    'has_keytab': bool(r.get('has_keytab', False)),
                    'disabled': None,
                    'last_auth': None,
                }

            if ptype == 'host':
                result = _ipa_api.Command.host_show(
                    lookup_arg, all=True, rights=False)
                r = result.get('result', {})
                fqdn = self._unwrap(r.get('fqdn'), fallback=lookup_arg)
                krb_names = r.get('krbprincipalname') or []
                canonical = (self._unwrap(krb_names, fallback=None)
                             or 'host/' + fqdn)
                return {
                    'name': name,
                    'canonical': to_text(
                        canonical, errors='surrogate_or_strict'),
                    'type': 'host',
                    'exists': True,
                    'has_keytab': bool(r.get('has_keytab', False)),
                    'disabled': None,
                    'last_auth': None,
                }

            # user
            result = _ipa_api.Command.user_show(
                lookup_arg, all=True, rights=False)
            r = result.get('result', {})
            canonical = self._unwrap(
                r.get('krbprincipalname'), fallback=lookup_arg)
            return {
                'name': name,
                'canonical': to_text(
                    canonical, errors='surrogate_or_strict'),
                'type': 'user',
                'exists': True,
                'has_keytab': bool(r.get('has_keytab', False)),
                'disabled': bool(r.get('nsaccountlock', False)),
                'last_auth': self._ipadate_to_str(
                    r.get('krblastsuccessfulauth')),
            }

        except ipalib_errors.NotFound:
            return self._not_found_record(name, ptype)
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to query principal '%s': %s"
                % (name, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to query principal '%s': %s"
                % (name, to_native(exc)))

    def _find_principals(self, criteria, principal_type):
        """Search IdM for principals and return a list of state records."""
        search_arg = criteria or ''
        records = []

        try:
            if principal_type == 'service':
                result = _ipa_api.Command.service_find(
                    search_arg, sizelimit=0, all=True)
                for entry in result.get('result', []):
                    canonical = self._unwrap(
                        entry.get('krbcanonicalname')
                        or entry.get('krbprincipalname'),
                        fallback='')
                    canonical_str = to_text(
                        canonical, errors='surrogate_or_strict')
                    records.append({
                        'name': canonical_str,
                        'canonical': canonical_str,
                        'type': 'service',
                        'exists': True,
                        'has_keytab': bool(entry.get('has_keytab', False)),
                        'disabled': None,
                        'last_auth': None,
                    })

            elif principal_type == 'host':
                result = _ipa_api.Command.host_find(
                    search_arg, sizelimit=0, all=True)
                for entry in result.get('result', []):
                    fqdn = self._unwrap(entry.get('fqdn'), fallback='')
                    krb_names = entry.get('krbprincipalname') or []
                    canonical = (self._unwrap(krb_names, fallback=None)
                                 or 'host/' + fqdn)
                    canonical_str = to_text(
                        canonical, errors='surrogate_or_strict')
                    records.append({
                        'name': canonical_str,
                        'canonical': canonical_str,
                        'type': 'host',
                        'exists': True,
                        'has_keytab': bool(entry.get('has_keytab', False)),
                        'disabled': None,
                        'last_auth': None,
                    })

            else:  # user
                result = _ipa_api.Command.user_find(
                    search_arg, sizelimit=0, all=True)
                for entry in result.get('result', []):
                    uid = self._unwrap(entry.get('uid'), fallback='')
                    canonical = self._unwrap(
                        entry.get('krbprincipalname'), fallback=uid)
                    canonical_str = to_text(
                        canonical, errors='surrogate_or_strict')
                    records.append({
                        'name': canonical_str,
                        'canonical': canonical_str,
                        'type': 'user',
                        'exists': True,
                        'has_keytab': bool(entry.get('has_keytab', False)),
                        'disabled': bool(
                            entry.get('nsaccountlock', False)),
                        'last_auth': self._ipadate_to_str(
                            entry.get('krblastsuccessfulauth')),
                    })

        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to search %s principals: %s"
                % (principal_type, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to search %s principals: %s"
                % (principal_type, to_native(exc)))

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
            principal_type = self.get_option('principal_type')
            criteria = self.get_option('criteria')
            result_format = self.get_option('result_format')

            if operation == 'find':
                if principal_type == 'auto':
                    raise AnsibleLookupError(
                        "operation=find requires an explicit principal_type "
                        "(user, host, or service). 'auto' is ambiguous for "
                        "searches.")
            elif operation == 'show':
                if not terms:
                    raise AnsibleLookupError(
                        "operation=show requires at least one principal name "
                        "in _terms.")
            else:
                raise AnsibleLookupError(
                    "Unknown operation '%s'. Use: show, find." % operation)

            self._connect(server, principal, password, keytab, verify)

            if operation == 'find':
                return self._finalize_results(
                    self._find_principals(criteria, principal_type),
                    result_format)

            results = []
            for term in terms:
                term = to_text(term, errors='surrogate_or_strict')
                results.append(self._show_principal(term, principal_type))

            return self._finalize_results(results, result_format)

        finally:
            self._cleanup_ccache()

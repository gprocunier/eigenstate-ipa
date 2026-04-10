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
name: keytab
version_added: "1.1.0"
short_description: Retrieve Kerberos keytabs from FreeIPA/IDM
description:
  - Retrieves Kerberos keytab files for service or host principals
    registered in FreeIPA/IDM.
  - Uses C(ipa-getkeytab) from the local IdM client packages to perform
    the keytab extraction over an authenticated LDAP connection.
  - Authenticates via password (converted to a Kerberos ticket) or an
    existing Kerberos ticket/keytab.
  - Returns the keytab as a base64-encoded string suitable for writing to
    disk or injecting into an AAP credential type.
  - Supports retrieving existing keys (safe, default) or generating new
    random keys (rotates the principal and invalidates all existing keytabs).
options:
  _terms:
    description: >-
      One or more Kerberos principal names whose keytabs should be
      retrieved. Examples: C(HTTP/service.example.com),
      C(host/server.example.com@REALM), C(nfs/storage.example.com).
    type: list
    elements: str
    required: true
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
    env:
      - name: IPA_PRINCIPAL
  ipaadmin_password:
    description: >-
      Password for the admin principal. The plugin uses this to obtain a
      Kerberos ticket via C(kinit). Not required if C(kerberos_keytab) is
      set or a valid ticket already exists. The password must be usable for
      non-interactive C(kinit); an IPA account that is forced to change its
      password on first login will fail in this mode.
    type: str
    secret: true
    env:
      - name: IPA_PASSWORD
  kerberos_keytab:
    description: >-
      Path to a Kerberos keytab file. Used to obtain a ticket
      non-interactively (required for AAP Execution Environments).
    type: str
    env:
      - name: IPA_KEYTAB
  verify:
    description: >-
      Path to the IPA CA certificate for an explicit C(--cacert) override, or
      C(false) to rely on the local system trust configuration instead. If not
      set, the plugin tries C(/etc/ipa/ca.crt) and otherwise falls back to the
      system trust store with a warning.
    type: raw
    env:
      - name: IPA_VERIFY
  retrieve_mode:
    description: >-
      Controls whether C(ipa-getkeytab) retrieves existing keys or
      generates new ones. C(retrieve) passes the C(-r) flag and only
      retrieves existing keys; it fails if no keys exist yet. C(generate)
      omits C(-r) and may generate new random keys for the principal.
      WARNING - C(generate) rotates the principal's keys and immediately
      invalidates every existing keytab for that principal, including those
      held by running services.
    type: str
    default: retrieve
    choices: ["retrieve", "generate"]
  enctypes:
    description: >-
      List of Kerberos encryption types to request, for example
      C(["aes256-cts", "aes128-cts"]). When empty (the default) the IPA
      server chooses the encryption types based on its policy.
    type: list
    elements: str
    default: []
  result_format:
    description: >-
      Controls the shape of each returned item. C(value) returns the
      base64-encoded keytab string directly. C(record) returns a dict with
      C(principal) and C(value) keys. C(map) returns a single dict keyed
      by principal name with base64 values.
    type: str
    default: value
    choices: ["value", "record", "map"]
notes:
  - The package that provides C(ipa-getkeytab) must be installed on the
    control node or execution environment. On RHEL 10, install
    C(ipa-client). On other releases, install the package that provides
    C(/usr/sbin/ipa-getkeytab).
  - C(ipaadmin_password) requires a password that can be used with
    non-interactive C(kinit). Accounts forced to change password on first
    login are not suitable for this mode.
  - The C(generate) retrieve mode rotates the principal's keys. Any service
    or host that holds an existing keytab for the principal will be unable
    to authenticate until it receives the new keytab. Use C(retrieve) unless
    you are explicitly rotating credentials.
  - Keytabs are binary files. The plugin always returns base64-encoded
    content regardless of result_format. Decode before writing to disk.
  - The authenticating principal must have permission to retrieve keytabs
    for the target principal. In most environments this requires admin rights
    or explicit delegation via IPA RBAC.
seealso:
  - module: redhat.rhel_idm.ipaservice
    description: Manage IPA service principals.
  - module: redhat.rhel_idm.ipahost
    description: Manage IPA host principals.
author:
  - Greg Procunier
"""

EXAMPLES = """
# Retrieve an existing keytab for an HTTP service principal
- name: Retrieve HTTP service keytab
  ansible.builtin.set_fact:
    http_keytab_b64: "{{ lookup('eigenstate.ipa.keytab',
                          'HTTP/webserver.idm.corp.lan',
                          server='idm-01.idm.corp.lan',
                          ipaadmin_password=lookup('env', 'IPA_PASSWORD'),
                          verify='/etc/ipa/ca.crt') }}"

# Retrieve using a keytab for non-interactive authentication
- name: Retrieve NFS service keytab via admin keytab auth
  ansible.builtin.set_fact:
    nfs_keytab_b64: "{{ lookup('eigenstate.ipa.keytab',
                          'nfs/storage.idm.corp.lan',
                          server='idm-01.idm.corp.lan',
                          ipaadmin_principal='admin',
                          kerberos_keytab='/runner/env/ipa/admin.keytab',
                          verify='/etc/ipa/ca.crt') }}"

# Write the keytab to disk on the target host
- name: Deploy HTTP keytab
  ansible.builtin.copy:
    content: "{{ lookup('eigenstate.ipa.keytab',
                   'HTTP/webserver.idm.corp.lan',
                   server='idm-01.idm.corp.lan',
                   kerberos_keytab='/runner/env/ipa/admin.keytab',
                   verify='/etc/ipa/ca.crt') | b64decode }}"
    dest: /etc/httpd/conf/httpd.keytab
    mode: "0600"
    owner: apache
    group: apache

# Retrieve keytab as a record with principal metadata
- name: Retrieve keytab with record format
  ansible.builtin.set_fact:
    keytab_record: "{{ query('eigenstate.ipa.keytab',
                        'HTTP/webserver.idm.corp.lan',
                        server='idm-01.idm.corp.lan',
                        kerberos_keytab='/runner/env/ipa/admin.keytab',
                        result_format='record',
                        verify='/etc/ipa/ca.crt') | first }}"
  # keytab_record.principal == 'HTTP/webserver.idm.corp.lan'
  # keytab_record.value     == base64-encoded keytab

# Retrieve keytabs for multiple principals in one lookup
- name: Retrieve keytabs for all web services
  ansible.builtin.set_fact:
    web_keytabs: "{{ query('eigenstate.ipa.keytab',
                      'HTTP/web-01.idm.corp.lan',
                      'HTTP/web-02.idm.corp.lan',
                      server='idm-01.idm.corp.lan',
                      kerberos_keytab='/runner/env/ipa/admin.keytab',
                      result_format='map',
                      verify='/etc/ipa/ca.crt') | first }}"
  # web_keytabs['HTTP/web-01.idm.corp.lan'] == base64 keytab
  # web_keytabs['HTTP/web-02.idm.corp.lan'] == base64 keytab

# Retrieve with explicit encryption types
- name: Retrieve keytab with aes256 only
  ansible.builtin.set_fact:
    keytab_b64: "{{ lookup('eigenstate.ipa.keytab',
                      'HTTP/webserver.idm.corp.lan',
                      server='idm-01.idm.corp.lan',
                      kerberos_keytab='/runner/env/ipa/admin.keytab',
                      enctypes=['aes256-cts'],
                      verify='/etc/ipa/ca.crt') }}"

# Generate new keys (ROTATES - invalidates all existing keytabs)
- name: Rotate HTTP service keytab
  ansible.builtin.set_fact:
    new_keytab_b64: "{{ lookup('eigenstate.ipa.keytab',
                          'HTTP/webserver.idm.corp.lan',
                          server='idm-01.idm.corp.lan',
                          kerberos_keytab='/runner/env/ipa/admin.keytab',
                          retrieve_mode='generate',
                          verify='/etc/ipa/ca.crt') }}"
"""

RETURN = """
_raw:
  description: >-
    A list containing one item per requested principal. Each item is either a
    base64-encoded keytab string (C(result_format=value)), a dict with
    C(principal) and C(value) keys (C(result_format=record)), or a single
    dict keyed by principal name (C(result_format=map), returned as a
    one-element list containing the dict).
  type: list
  elements: raw
"""

import base64
import os
import shutil
import stat
import subprocess
import tempfile

from ansible.errors import AnsibleLookupError
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

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
    """Retrieve Kerberos keytabs from FreeIPA/IDM."""

    def __init__(self, *args, **kwargs):
        super(LookupModule, self).__init__(*args, **kwargs)
        self._ccache_path = None
        self._previous_ccache = None
        self._managing_ccache = False

    # ------------------------------------------------------------------
    # Dependency checks
    # ------------------------------------------------------------------

    def _read_os_release(self):
        """Read os-release data when available."""
        for path in ('/etc/os-release', '/usr/lib/os-release'):
            if not os.path.exists(path):
                continue
            data = {}
            with open(path, 'r', encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    key, value = line.split('=', 1)
                    data[key] = value.strip().strip('\"')
            return data
        return {}

    def _rhel_major_version(self):
        """Return the local RHEL major version when it can be detected."""
        data = self._read_os_release()
        distro_id = data.get('ID', '').lower()
        distro_like = data.get('ID_LIKE', '').lower().split()
        if distro_id not in ('rhel', 'redhat') and 'rhel' not in distro_like:
            return None

        version_id = data.get('VERSION_ID', '')
        major = version_id.split('.', 1)[0]
        if major.isdigit():
            return int(major)
        return None

    def _ipa_getkeytab_install_hint(self):
        """Return a release-aware install hint for ipa-getkeytab."""
        rhel_major = self._rhel_major_version()
        if rhel_major == 10:
            return (
                "Install ipa-client:\n"
                "  dnf install ipa-client\n"
                "On a RHEL 10 AAP Execution Environment, add ipa-client "
                "to the EE package list.")

        return (
            "Install the package that provides ipa-getkeytab for this "
            "release. For example:\n"
            "  dnf provides '*/ipa-getkeytab'\n"
            "On RHEL 10, the provider is ipa-client.")

    def _ensure_ipa_getkeytab_available(self):
        if not shutil.which('ipa-getkeytab'):
            raise AnsibleLookupError(
                "'ipa-getkeytab' not found. %s"
                % self._ipa_getkeytab_install_hint())

    # ------------------------------------------------------------------
    # Kerberos credential acquisition
    # ------------------------------------------------------------------

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
            prefix='krb5cc_ipa_keytab_')
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
            prefix='krb5cc_ipa_keytab_')
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

    # ------------------------------------------------------------------
    # Credential cache lifecycle
    # ------------------------------------------------------------------

    def _activate_ccache(self, ccache_path, ccache_env):
        """Track and activate a managed Kerberos credential cache."""
        if not self._managing_ccache:
            self._previous_ccache = os.environ.get('KRB5CCNAME')
            self._managing_ccache = True
        self._ccache_path = ccache_path
        os.environ['KRB5CCNAME'] = ccache_env

    def _cleanup_ccache(self):
        """Remove any managed Kerberos credential cache and restore env."""
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

    # ------------------------------------------------------------------
    # TLS verification
    # ------------------------------------------------------------------

    def _default_verify_path(self):
        """Return the conventional IPA CA path when it exists locally."""
        default_path = '/etc/ipa/ca.crt'
        if os.path.exists(default_path):
            return default_path
        return None

    def _resolve_verify(self, verify):
        """Resolve TLS verification behavior for ipa-getkeytab requests."""
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
            "No explicit IPA CA certificate configured for "
            "eigenstate.ipa.keytab. Falling back to the system trust store."
        )
        return False

    # ------------------------------------------------------------------
    # File security
    # ------------------------------------------------------------------

    def _warn_if_sensitive_file_permissive(self, path, option_name):
        """Warn when sensitive local files are readable by non-owners."""
        mode = stat.S_IMODE(os.stat(path).st_mode)
        if mode & 0o077:
            display.warning(
                "%s '%s' has permissions %s which are more permissive "
                "than 0600." % (option_name, path, oct(mode))
            )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_retrieve_mode(self, retrieve_mode):
        valid = ('retrieve', 'generate')
        if retrieve_mode not in valid:
            raise AnsibleLookupError(
                "Invalid retrieve_mode '%s'. Choose one of: %s"
                % (retrieve_mode, ', '.join(valid)))

    def _validate_result_format(self, result_format):
        valid = ('value', 'record', 'map')
        if result_format not in valid:
            raise AnsibleLookupError(
                "Invalid result_format '%s'. Choose one of: %s"
                % (result_format, ', '.join(valid)))

    # ------------------------------------------------------------------
    # Keytab retrieval
    # ------------------------------------------------------------------

    def _retrieve_keytab(self, principal, server, enctypes, retrieve_mode, verify):
        """Run ipa-getkeytab and return binary keytab data."""
        temp_dir = tempfile.mkdtemp(prefix='krb5_keytab_')
        temp_path = os.path.join(temp_dir, 'retrieved.keytab')
        try:
            cmd = ['ipa-getkeytab',
                   '-s', server,
                   '-p', principal,
                   '-k', temp_path]
            if verify:
                cmd.extend(['--cacert', verify])
            for enctype in enctypes:
                cmd.extend(['-e', enctype])
            if retrieve_mode == 'retrieve':
                cmd.append('-r')

            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True,
                    timeout=30, env=os.environ.copy())
            except FileNotFoundError:
                raise AnsibleLookupError(
                    "'ipa-getkeytab' not found. %s"
                    % self._ipa_getkeytab_install_hint())
            except subprocess.TimeoutExpired:
                raise AnsibleLookupError(
                    "'ipa-getkeytab' timed out for principal '%s'. "
                    "Check IPA server connectivity and network configuration."
                    % principal)

            if result.returncode != 0:
                verify_args = ''
                if verify:
                    verify_args = ' --cacert %s' % verify
                raise AnsibleLookupError(
                    "ipa-getkeytab failed for '%s' on server '%s' "
                    "(exit %d): %s\n"
                    "Verify: ipa-getkeytab -r -s %s -p %s%s -k /tmp/test.keytab"
                    % (principal, server, result.returncode,
                       result.stderr.strip(), server, principal, verify_args))

            data = b''
            if os.path.exists(temp_path):
                with open(temp_path, 'rb') as fh:
                    data = fh.read()

            if not data:
                raise AnsibleLookupError(
                    "ipa-getkeytab produced an empty keytab for '%s'. "
                    "Verify the principal exists and the authenticating "
                    "account has permission to retrieve its keytab."
                    % principal)

            return data
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Result formatting
    # ------------------------------------------------------------------

    def _format_keytab_result(self, principal, data):
        """Encode a raw keytab and build a canonical record dict."""
        value = base64.b64encode(data).decode('ascii')
        return {
            'principal': principal,
            'value': value,
            'encoding': 'base64',
        }

    def _finalize_results(self, results, result_format):
        """Convert canonical record dicts to the requested output shape."""
        if result_format == 'map':
            return [{item['principal']: item['value'] for item in results}]
        if result_format == 'record':
            return results
        # value (default): return bare base64 strings
        return [item['value'] for item in results]

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self, terms, variables=None, **kwargs):
        try:
            self._ensure_ipa_getkeytab_available()
            self.set_options(var_options=variables, direct=kwargs)

            server = self.get_option('server')
            if not server:
                raise AnsibleLookupError(
                    "'server' is required. Set it directly or via the "
                    "IPA_SERVER environment variable.")

            principal = self.get_option('ipaadmin_principal')
            password = self.get_option('ipaadmin_password')
            keytab = self.get_option('kerberos_keytab')
            verify = self._resolve_verify(self.get_option('verify'))
            retrieve_mode = self.get_option('retrieve_mode')
            enctypes = self.get_option('enctypes') or []
            result_format = self.get_option('result_format')

            self._validate_retrieve_mode(retrieve_mode)
            self._validate_result_format(result_format)

            if not terms:
                raise AnsibleLookupError(
                    "At least one principal name is required.")

            if retrieve_mode == 'generate':
                display.warning(
                    "eigenstate.ipa.keytab: retrieve_mode='generate' will "
                    "rotate keys for the requested principal(s). All "
                    "existing keytabs for those principals will be "
                    "immediately invalidated.")

            if keytab:
                self._kinit_keytab(keytab, principal)
            elif password:
                self._kinit_password(principal, password)
            else:
                if 'KRB5CCNAME' not in os.environ:
                    display.warning(
                        "eigenstate.ipa.keytab: no password or keytab "
                        "provided and KRB5CCNAME is not set. Assuming a "
                        "valid Kerberos ticket exists in the default ccache.")

            results = []
            for target_principal in terms:
                target_principal = to_text(
                    target_principal, errors='surrogate_or_strict')
                data = self._retrieve_keytab(
                    target_principal, server, enctypes, retrieve_mode,
                    verify)
                item = self._format_keytab_result(target_principal, data)
                results.append(item)

            return self._finalize_results(results, result_format)
        finally:
            self._cleanup_ccache()

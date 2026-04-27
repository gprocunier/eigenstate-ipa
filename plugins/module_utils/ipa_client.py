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

"""Shared IPA client infrastructure for eigenstate.ipa modules.

Provides Kerberos authentication, ipalib connection management, and
common helpers used by action modules and lookup plugins in this
collection.
"""

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import os
import stat
import subprocess
import shutil
import tempfile

from ansible.module_utils.common.text.converters import to_native, to_text

try:
    from ipalib import api as _ipa_api
    from ipalib import errors as ipalib_errors
    HAS_IPALIB = True
except ImportError:
    _ipa_api = None
    ipalib_errors = None
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


class IPAClientError(Exception):
    """Raised by IPAClient when an operation fails."""


class IPAClient(object):
    """Kerberos-authenticated ipalib session for eigenstate.ipa modules.

    Usage::

        client = IPAClient()
        try:
            client.connect(
                server='idm-01.example.com',
                principal='admin',
                password=module.params['ipaadmin_password'],
                keytab=module.params['kerberos_keytab'],
                verify=module.params['verify'],
            )
            result = client.api.Command.vault_find(...)
        except IPAClientError as exc:
            module.fail_json(msg=str(exc))
        finally:
            client.cleanup()
    """

    def __init__(self, warn_callback=None, require_trusted_tls=False):
        """
        :param warn_callback: callable(msg) for issuing warnings.
            Pass ``module.warn`` from an AnsibleModule, or a display
            function from a lookup plugin.
        :param require_trusted_tls: when ``True``, require either an
            explicit CA path, the default local IPA CA path, or an
            explicit ``verify=false`` operator opt-out.
        """
        self._warn = warn_callback or (lambda msg: None)
        self._require_trusted_tls = require_trusted_tls
        self._ccache_path = None
        self._previous_ccache = None
        self._managing_ccache = False

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def api(self):
        """Return the ipalib API object for direct command calls."""
        if not HAS_IPALIB:
            raise IPAClientError(
                "The 'ipalib' Python library is required.\n"
                "  RHEL/Fedora: dnf install python3-ipalib python3-ipaclient")
        return _ipa_api

    @property
    def errors(self):
        """Return the ipalib errors module for exception handling."""
        if not HAS_IPALIB:
            raise IPAClientError(
                "The 'ipalib' Python library is required.\n"
                "  RHEL/Fedora: dnf install python3-ipalib python3-ipaclient")
        return ipalib_errors

    @staticmethod
    def authz_error_kind(exc):
        """Return a stable authz classification for known IPA errors."""
        if not HAS_IPALIB or ipalib_errors is None:
            return None

        authz_error = getattr(ipalib_errors, 'AuthorizationError', None)
        if authz_error and isinstance(exc, authz_error):
            return 'authorization'

        aci_error = getattr(ipalib_errors, 'ACIError', None)
        if aci_error and isinstance(exc, aci_error):
            return 'access_control'

        return None

    @classmethod
    def is_authz_error(cls, exc):
        return cls.authz_error_kind(exc) is not None

    @classmethod
    def authz_error_message(cls, exc, action, principal=None):
        kind = cls.authz_error_kind(exc)
        if kind == 'authorization':
            msg = "Not authorized to %s" % action
        elif kind == 'access_control':
            msg = "Access-control policy denied %s" % action
        else:
            return None

        if principal:
            msg += " as '%s'" % principal

        return "%s: %s" % (msg, to_native(exc))

    def connect(self, server, principal='admin', password=None,
                keytab=None, verify=None):
        """Authenticate and connect to the IPA server.

        Exactly one of *password*, *keytab*, or an existing Kerberos
        ticket in the environment is required.  When both *password* and
        *keytab* are provided, *keytab* takes precedence.

        :param server: FQDN of the IPA server.
        :param principal: Kerberos principal (default: 'admin').
        :param password: Password for *principal*.  Used to obtain a
            Kerberos ticket via ``kinit`` when *keytab* is not set.
        :param keytab: Path to a keytab file.  Takes precedence over
            *password*.
        :param verify: Path to the IPA CA certificate for TLS
            verification.  Auto-detected from ``/etc/ipa/ca.crt`` when
            not set; disabled with a warning if neither is available.
        :raises IPAClientError: on authentication or connection failure.
        """
        if not HAS_IPALIB:
            raise IPAClientError(
                "The 'ipalib' Python library is required for "
                "eigenstate.ipa modules.\n"
                "  RHEL/Fedora: dnf install python3-ipalib "
                "python3-ipaclient")

        resolved_verify = self.resolve_verify(verify)
        self.authenticate(principal=principal, password=password, keytab=keytab)

        if not _ipa_api.isdone('bootstrap'):
            bootstrap_args = {
                'context': 'cli',
                'log': None,
            }
            if resolved_verify:
                bootstrap_args['tls_ca_cert'] = resolved_verify
            try:
                _ipa_api.bootstrap(**bootstrap_args)
            except Exception as exc:
                if self._is_tls_ca_cert_bootstrap_override_error(exc):
                    if not _ipa_api.isdone('bootstrap'):
                        retry_args = dict(bootstrap_args)
                        retry_args.pop('tls_ca_cert', None)
                        try:
                            _ipa_api.bootstrap(**retry_args)
                        except Exception as retry_exc:
                            if not _ipa_api.isdone('bootstrap'):
                                raise IPAClientError(
                                    "ipalib bootstrap failed: %s"
                                    % to_native(retry_exc))
                else:
                    raise IPAClientError(
                        "ipalib bootstrap failed: %s" % to_native(exc))

        if not _ipa_api.isdone('finalize'):
            try:
                _ipa_api.finalize()
            except Exception as exc:
                raise IPAClientError(
                    "ipalib finalize failed: %s" % to_native(exc))

        backend = _ipa_api.Backend.rpcclient
        if not backend.isconnected():
            try:
                backend.connect(
                    ccache=os.environ.get('KRB5CCNAME', None))
            except Exception as exc:
                raise IPAClientError(
                    "Failed to connect to IPA server '%s': %s\n"
                    "Check that a valid Kerberos ticket exists (klist) "
                    "and the server is reachable." % (server, to_native(exc)))

    def cleanup(self, ipa_api=None, has_ipalib=None):
        """Remove any managed ccache and restore the ``KRB5CCNAME`` env var."""
        active_has_ipalib = HAS_IPALIB if has_ipalib is None else has_ipalib
        active_ipa_api = _ipa_api if ipa_api is None else ipa_api
        if active_has_ipalib and active_ipa_api is not None:
            try:
                backend = active_ipa_api.Backend.rpcclient
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

    def authenticate(self, principal='admin', password=None, keytab=None):
        """Prepare Kerberos credentials without opening an ipalib session."""
        if keytab:
            self._kinit_keytab(keytab, principal)
        elif password:
            self._kinit_password(principal, password)
        else:
            if 'KRB5CCNAME' not in os.environ:
                self._warn(
                    "No password or keytab provided and KRB5CCNAME is "
                    "not set. Assuming a valid Kerberos ticket exists "
                    "in the default ccache.")

    def resolve_verify(self, verify):
        """Resolve TLS verification setting for callers that need the path."""
        return self._resolve_verify(verify)

    @staticmethod
    def _is_tls_ca_cert_bootstrap_override_error(exc):
        """Return True for FreeIPA bootstrap rejecting a tls_ca_cert override."""
        args = getattr(exc, 'args', ())
        if len(args) == 1 and isinstance(args[0], tuple):
            args = args[0]
        return bool(args and args[0] == 'tls_ca_cert')

    # ------------------------------------------------------------------
    # Scope helpers
    # ------------------------------------------------------------------

    @staticmethod
    def scope_args(username, service, shared):
        """Build ipalib scope keyword arguments.

        :returns: dict suitable for unpacking into an ipalib Command call.
        """
        args = {}
        if username:
            args['username'] = to_text(username, errors='surrogate_or_strict')
        elif service:
            args['service'] = to_text(service, errors='surrogate_or_strict')
        elif shared:
            args['shared'] = True
        return args

    @staticmethod
    def scope_label(username, service, shared):
        """Return a human-readable scope string for messages."""
        if username:
            return "username=%s" % username
        if service:
            return "service=%s" % service
        if shared:
            return "shared"
        return "default"

    @staticmethod
    def validate_scope(username, service, shared):
        """Raise ``IPAClientError`` if more than one scope option is set."""
        if sum(bool(x) for x in [username, service, shared]) > 1:
            raise IPAClientError(
                "'username', 'service', and 'shared' are mutually "
                "exclusive. Specify at most one.")

    # ------------------------------------------------------------------
    # File security helpers
    # ------------------------------------------------------------------

    def warn_if_permissive(self, path, option_name):
        """Warn when a sensitive file has group- or world-readable bits."""
        mode = stat.S_IMODE(os.stat(path).st_mode)
        if mode & 0o077:
            self._warn(
                "%s '%s' has permissions %s which are more permissive "
                "than 0600." % (option_name, path, oct(mode)))

    # ------------------------------------------------------------------
    # Private: Kerberos credential management
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
        if not os.path.isfile(keytab):
            raise IPAClientError(
                "Kerberos keytab file not found: %s" % keytab)

        self.warn_if_permissive(keytab, "kerberos_keytab")

        ccache_fd, ccache_path = tempfile.mkstemp(
            prefix='krb5cc_ipa_vault_')
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
            raise IPAClientError(
                "'kinit' not found. Expected /usr/bin/kinit from krb5-workstation or a PATH-resolved kinit. Install krb5-workstation:\n"
                "  dnf install krb5-workstation")
        except subprocess.TimeoutExpired:
            os.remove(ccache_path)
            raise IPAClientError(
                "'kinit' timed out. Check KDC connectivity and "
                "/etc/krb5.conf.")

        if result.returncode != 0:
            os.remove(ccache_path)
            raise IPAClientError(
                "kinit with keytab failed (exit %d): %s\n"
                "Verify the keytab with: klist -kt %s"
                % (result.returncode, self._format_subprocess_stderr(result.stderr),
                   keytab))

        self._activate_ccache(ccache_path, ccache_env)

    def _kinit_password(self, principal, password):
        ccache_fd, ccache_path = tempfile.mkstemp(
            prefix='krb5cc_ipa_vault_')
        os.close(ccache_fd)
        ccache_env = 'FILE:%s' % ccache_path

        if HAS_KINIT_PASSWORD:
            try:
                _kinit_password(principal, password, ccache_path)
            except Exception as exc:
                os.remove(ccache_path)
                raise IPAClientError(
                    "kinit_password failed for '%s': %s"
                    % (principal, to_native(exc)))
        else:
            password_input = to_text(
                password, errors='surrogate_or_strict')
            if not password_input.endswith('\n'):
                password_input += '\n'
            env = os.environ.copy()
            env['KRB5CCNAME'] = ccache_env
            try:
                result = subprocess.run(
                    [self._resolve_kinit_command(), principal],
                    input=password_input, capture_output=True, text=True,
                    timeout=30, env=env)
            except FileNotFoundError:
                os.remove(ccache_path)
                raise IPAClientError(
                    "'kinit' not found and ipalib.kinit_password is "
                    "not available. Expected /usr/bin/kinit from krb5-workstation or a PATH-resolved kinit. Install one of:\n"
                    "  dnf install krb5-workstation\n"
                    "  dnf install python3-ipaclient")
            except subprocess.TimeoutExpired:
                os.remove(ccache_path)
                raise IPAClientError(
                    "'kinit' timed out. Check KDC connectivity.")
            if result.returncode != 0:
                os.remove(ccache_path)
                raise IPAClientError(
                    "kinit failed for '%s' (exit %d): %s"
                    % (principal, result.returncode,
                       self._format_subprocess_stderr(result.stderr)))

        self._activate_ccache(ccache_path, ccache_env)

    def _activate_ccache(self, ccache_path, ccache_env):
        if not self._managing_ccache:
            self._previous_ccache = os.environ.get('KRB5CCNAME')
            self._managing_ccache = True
        self._ccache_path = ccache_path
        os.environ['KRB5CCNAME'] = ccache_env

    # ------------------------------------------------------------------
    # Private: TLS verification
    # ------------------------------------------------------------------

    def _resolve_verify(self, verify):
        if isinstance(verify, bool):
            if not verify:
                self._warn(
                    "TLS verification is disabled for eigenstate.ipa. "
                    "Set 'verify' to the IPA CA certificate path for "
                    "production use.")
                return False
        elif isinstance(verify, str):
            verify = verify.strip()
            if verify.lower() in ('false', 'no', 'off', '0'):
                self._warn(
                    "TLS verification is disabled for eigenstate.ipa. "
                    "Set 'verify' to the IPA CA certificate path for "
                    "production use.")
                return False

        if verify is not None:
            if not os.path.exists(verify):
                raise IPAClientError(
                    "TLS certificate file not found: %s" % verify)
            return verify

        default_path = '/etc/ipa/ca.crt'
        if os.path.exists(default_path):
            return default_path

        if self._require_trusted_tls:
            raise IPAClientError(
                "TLS verification could not be established for "
                "eigenstate.ipa. Set 'verify' to the IPA CA certificate "
                "path, ensure /etc/ipa/ca.crt is present, or set "
                "'verify' to false explicitly if you intend to disable "
                "verification.")

        self._warn(
            "TLS verification is disabled for eigenstate.ipa. "
            "Set 'verify' to the IPA CA certificate path for "
            "production use.")
        return False

    # ------------------------------------------------------------------
    # Utility: unwrap IPA single-element lists
    # ------------------------------------------------------------------

    @staticmethod
    def unwrap(value):
        """Unwrap IPA-style single-element lists to a scalar."""
        if isinstance(value, (list, tuple)):
            if len(value) == 1:
                return value[0]
            if len(value) == 0:
                return None
        return value

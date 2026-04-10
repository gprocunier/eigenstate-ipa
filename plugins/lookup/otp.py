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
name: otp
version_added: "1.4.0"
short_description: Generate and manage OTP tokens and host enrollment passwords in FreeIPA/IdM
description:
  - Generates TOTP and HOTP two-factor authentication tokens for IdM users via
    C(otptoken_add).
  - Generates one-time enrollment passwords for IdM hosts via C(host_mod --random),
    suitable for consumption by C(freeipa.ansible_freeipa.ipaclient) or
    C(freeipa.ansible_freeipa.ipahost).
  - Supports full token lifecycle management via C(find), C(show), and C(revoke)
    operations.
  - All operations use the C(ipalib) RPC framework. No CLI tools are invoked.
  - Authenticates via password (converted to a Kerberos ticket), a keytab file,
    or an existing Kerberos ticket.
  - Can be used as a credential source in AAP by referencing the lookup in a
    custom credential type injector.
options:
  _terms:
    description: >-
      Identifiers to operate on. Meaning varies by C(operation) and
      C(token_type).
      For C(operation=add) with C(token_type=totp) or
      C(token_type=hotp), one or more
      IdM usernames whose tokens should be created.
      For C(operation=add) with C(token_type=host), one or more host FQDNs for
      which enrollment passwords should be generated.
      For C(operation=find), an optional substring search pattern; omit to
      return all tokens accessible to the authenticated principal.
      For C(operation=show) and C(operation=revoke), one or more token unique
      IDs (C(ipatokenuniqueid)).
    type: list
    elements: str
  operation:
    description: >-
      Which OTP operation to perform. C(add) creates a new token or host
      enrollment password. C(find) searches for existing tokens. C(show)
      retrieves metadata for a specific token by ID. C(revoke) permanently
      deletes one or more tokens by ID.
    type: str
    default: add
    choices: ["add", "find", "show", "revoke"]
  token_type:
    description: >-
      The kind of credential to create. C(totp) generates a time-based
      one-time password token for an IdM user. C(hotp) generates an
      HMAC-based counter token. C(host) generates a one-time enrollment
      password for an IdM host. Only used by C(operation=add).
    type: str
    default: totp
    choices: ["totp", "hotp", "host"]
  algorithm:
    description: >-
      HMAC algorithm used to generate the OTP value. Only applies to
      C(token_type=totp) and C(token_type=hotp).
    type: str
    default: sha1
    choices: ["sha1", "sha256", "sha384", "sha512"]
  digits:
    description: >-
      Number of digits in the generated OTP value. Only applies to
      C(token_type=totp) and C(token_type=hotp).
    type: int
    default: 6
    choices: [6, 8]
  interval:
    description: >-
      Time step in seconds for TOTP tokens. Only meaningful for
      C(token_type=totp). Ignored with a warning for C(token_type=hotp) and
      C(token_type=host).
    type: int
    default: 30
  owner:
    description: >-
      Filter C(operation=find) results to tokens owned by this user.
      Ignored with a warning for other operations.
    type: str
  description:
    description: >-
      Optional description attached to the new token. Only used by
      C(operation=add) with C(token_type=totp) or C(token_type=hotp).
    type: str
  result_format:
    description: >-
      How to shape the lookup result. C(value) returns only the token URI
      (C(otpauth://) string) for user tokens, or only the enrollment password
      for host tokens. C(record) returns a list of structured result records.
      C(map) returns a dictionary of identifier to bare value. C(map_record)
      returns a dictionary of identifier to structured record.
      C(value) is the default for C(operation=add); C(record) is the default
      for C(operation=find) and C(operation=show). Not applicable to
      C(operation=revoke), which always returns a list of deleted token IDs.
    type: str
    choices: ["value", "record", "map", "map_record"]
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
      Path to the IPA CA certificate for TLS verification. Set C(false) to
      disable verification explicitly. If omitted, C(/etc/ipa/ca.crt) is used
      when present; otherwise the plugin falls back to the system trust store
      with a warning.
    type: raw
    env:
      - name: IPA_CERT
notes:
  - This plugin requires C(python3-ipalib) and C(python3-ipaclient) on the
    Ansible controller.
  - "RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)"
  - >-
    SECURITY: TOTP and HOTP token URIs (C(otpauth://)) embed the shared
    secret. Treat the C(uri) field as sensitive credential material. Use
    C(no_log: true) on any task that registers or displays a token URI.
    Store URIs only in encrypted storage (vaults, AAP credentials, etc.).
  - >-
    The C(uri) field is only present in C(operation=add) results.
    C(find) and C(show) return token metadata without the shared secret.
  - >-
    Host enrollment passwords (C(token_type=host)) are consumed on first use by
    C(ipa-client-install). Pass them to C(freeipa.ansible_freeipa.ipaclient)
    or C(freeipa.ansible_freeipa.ipahost) rather than invoking the CLI
    directly.
  - >-
    C(operation=show) returns a record with C(exists=false) when the token
    ID is not found, rather than raising an error. This enables non-fatal
    pre-flight checks.
  - >-
    C(operation=revoke) raises an error if a token ID is not found. Revocation
    is not idempotent by design.
  - The authenticating principal must have the C(Manage OTP Tokens) privilege
    in IdM to create, find, show, or revoke tokens. Host enrollment password
    generation requires the C(Modify Hosts) privilege.
seealso:
  - name: freeipa.ansible_freeipa ipaclient role
    description: Consume host enrollment passwords to enroll IPA clients.
    link: https://github.com/freeipa/ansible-freeipa
  - plugin: eigenstate.ipa.principal
    plugin_type: lookup
  - plugin: eigenstate.ipa.keytab
    plugin_type: lookup
author:
  - Greg Procunier
"""

EXAMPLES = """
# Generate a TOTP token for a user (URI contains the shared secret)
- name: Provision user MFA token
  ansible.builtin.set_fact:
    totp_uri: "{{ lookup('eigenstate.ipa.otp', 'jsmith',
                   server='idm-01.example.com',
                   ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"
  no_log: true

# Generate a host enrollment OTP and pass it to ansible-freeipa
- name: Generate enrollment password
  ansible.builtin.set_fact:
    enroll_pass: "{{ lookup('eigenstate.ipa.otp', inventory_hostname,
                      token_type='host',
                      server='idm-01.example.com',
                      kerberos_keytab='/etc/ansible/admin.keytab') }}"
  no_log: true
  delegate_to: localhost

- name: Enroll host using ansible-freeipa
  ansible.builtin.include_role:
    name: freeipa.ansible_freeipa.ipaclient
  vars:
    ipaclient_hostname: "{{ inventory_hostname }}"
    ipaclient_password: "{{ enroll_pass }}"

# Generate an HOTP token with 8-digit codes using sha256
- name: Provision HOTP token
  ansible.builtin.set_fact:
    token_record: "{{ lookup('eigenstate.ipa.otp', 'svcaccount',
                       token_type='hotp',
                       algorithm='sha256',
                       digits=8,
                       result_format='record',
                       server='idm-01.example.com',
                       ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"
  no_log: true

# Find all tokens for a specific user
- name: List user tokens
  ansible.builtin.set_fact:
    user_tokens: "{{ lookup('eigenstate.ipa.otp',
                      owner='jsmith',
                      operation='find',
                      server='idm-01.example.com',
                      ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"

# Check whether a token exists before rotation (no_log not needed; show returns no secret)
- name: Inspect token by ID
  ansible.builtin.set_fact:
    token_state: "{{ lookup('eigenstate.ipa.otp', 'some-token-uuid',
                      operation='show',
                      server='idm-01.example.com',
                      ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"

# Revoke a specific token
- name: Revoke token
  ansible.builtin.debug:
    msg: "Revoked: {{ lookup('eigenstate.ipa.otp', 'some-token-uuid',
                      operation='revoke',
                      server='idm-01.example.com',
                      ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"

# Rotate: revoke old token, issue new one
- name: Rotate user token
  ansible.builtin.set_fact:
    new_uri: "{{ lookup('eigenstate.ipa.otp', 'jsmith',
                  server='idm-01.example.com',
                  ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD')) }}"
  no_log: true
  when: >-
    lookup('eigenstate.ipa.otp', (old_token_id | string),
      operation='show',
      server='idm-01.example.com',
      ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'))[0].exists
"""

RETURN = """
_raw:
  description: >-
    One element per term. When C(operation=add) and C(result_format=value)
    (the default), each element is the C(otpauth://) URI string for user
    tokens, or the one-time enrollment password string for
    C(token_type=host).
    When C(result_format=record), each element is a structured dictionary
    (see below). When C(result_format=map) or C(result_format=map_record),
    the return is a dictionary keyed by owner username, host FQDN, or token
    ID depending on operation.
    For C(operation=find) and C(operation=show), the default is
    C(result_format=record). For C(operation=revoke), a list of deleted
    token unique IDs is returned regardless of C(result_format).
  type: raw
  contains:
    owner:
      description: IdM username that owns the token (user tokens only).
      type: str
    fqdn:
      description: Host FQDN for which the enrollment password was generated
        (host type only).
      type: str
    token_id:
      description: Token unique identifier (C(ipatokenuniqueid)).
      type: str
    type:
      description: Token type. One of C(totp), C(hotp), or C(host).
      type: str
    uri:
      description: >-
        C(otpauth://) URI containing the shared secret. Only present for
        C(operation=add) with C(token_type=totp) or C(token_type=hotp). Absent for
        C(find) and C(show) operations. Treat as sensitive.
      type: str
    password:
      description: >-
        One-time enrollment password. Only present for C(operation=add)
        with C(token_type=host). Treat as sensitive.
      type: str
    algorithm:
      description: HMAC algorithm (C(sha1), C(sha256), C(sha384), C(sha512)).
      type: str
    digits:
      description: OTP digit count (6 or 8).
      type: int
    interval:
      description: TOTP time step in seconds. C(null) for HOTP tokens.
      type: int
    disabled:
      description: Whether the token is disabled. C(null) if unknown.
      type: bool
    description:
      description: Optional description attached to the token.
      type: str
    exists:
      description: >-
        Whether the token was found. Always C(true) for C(add) and
        C(find) results. C(false) only when C(operation=show) targets a
        token ID that does not exist.
      type: bool
"""

import os
import stat
import subprocess
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
    """Generate and manage OTP tokens and host enrollment passwords in FreeIPA/IdM."""

    def __init__(self, *args, **kwargs):
        super(LookupModule, self).__init__(*args, **kwargs)
        self._ccache_path = None
        self._previous_ccache = None
        self._managing_ccache = False

    # ------------------------------------------------------------------
    # Auth helpers (shared pattern across eigenstate.ipa plugins)
    # ------------------------------------------------------------------

    def _ensure_ipalib(self):
        if not HAS_IPALIB:
            raise AnsibleLookupError(
                "The 'ipalib' Python library is required for the "
                "eigenstate.ipa.otp lookup plugin.\n"
                "  RHEL/Fedora: dnf install python3-ipalib "
                "python3-ipaclient")

    def _kinit_keytab(self, keytab, principal):
        """Obtain a Kerberos ticket from a keytab file."""
        if not os.path.isfile(keytab):
            raise AnsibleLookupError(
                "Kerberos keytab file not found: %s" % keytab)

        self._warn_if_sensitive_file_permissive(keytab, "kerberos_keytab")

        ccache_fd, ccache_path = tempfile.mkstemp(
            prefix='krb5cc_ipa_otp_')
        os.close(ccache_fd)
        ccache_env = 'FILE:%s' % ccache_path

        env = os.environ.copy()
        env['KRB5CCNAME'] = ccache_env

        try:
            result = subprocess.run(
                ['kinit', '-kt', keytab, principal],
                capture_output=True, text=True, timeout=30,
                env=env)
        except FileNotFoundError:
            os.remove(ccache_path)
            raise AnsibleLookupError(
                "'kinit' not found. Install krb5-workstation:\n"
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
            prefix='krb5cc_ipa_otp_')
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
            password_input = to_text(
                password, errors='surrogate_or_strict')
            if not password_input.endswith('\n'):
                password_input += '\n'
            env = os.environ.copy()
            env['KRB5CCNAME'] = ccache_env
            try:
                result = subprocess.run(
                    ['kinit', principal],
                    input=password_input, capture_output=True, text=True,
                    timeout=30, env=env)
            except FileNotFoundError:
                os.remove(ccache_path)
                raise AnsibleLookupError(
                    "'kinit' not found and ipalib.kinit_password is "
                    "not available. Install one of:\n"
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
        backend = getattr(getattr(_ipa_api, 'Backend', None), 'rpcclient', None)
        if backend is not None and hasattr(backend, 'isconnected') and backend.isconnected():
            try:
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
        if isinstance(verify, bool):
            if not verify:
                display.warning(
                    "TLS verification is disabled for eigenstate.ipa.otp. "
                    "Set 'verify' to the IPA CA certificate path for production use."
                )
                return False
        elif isinstance(verify, str):
            verify = verify.strip()
            if verify.lower() in ('false', 'no', 'off', '0'):
                display.warning(
                    "TLS verification is disabled for eigenstate.ipa.otp. "
                    "Set 'verify' to the IPA CA certificate path for production use."
                )
                return False
        if verify is not None:
            if not os.path.exists(verify):
                raise AnsibleLookupError(
                    "TLS certificate file not found: %s" % verify)
            return verify

        default_verify = self._default_verify_path()
        if default_verify is not None:
            return default_verify

        display.warning(
            "TLS verification is disabled for eigenstate.ipa.otp. "
            "Set 'verify' to the IPA CA certificate path for production use."
        )
        return False

    def _warn_if_sensitive_file_permissive(self, path, option_name):
        """Warn when sensitive local files are readable by non-owners."""
        mode = stat.S_IMODE(os.stat(path).st_mode)
        if mode & 0o077:
            display.warning(
                "%s '%s' has permissions %s which are more permissive "
                "than 0600." % (option_name, path, oct(mode))
            )

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
    # Utility helpers
    # ------------------------------------------------------------------

    def _unwrap(self, value, fallback=None):
        """Extract the first element from ipalib single-element lists."""
        if isinstance(value, (list, tuple)):
            if len(value) == 1:
                return value[0]
            if len(value) == 0:
                return fallback
        if value is None:
            return fallback
        return value

    def _native_text(self, value, fallback=''):
        """Coerce Ansible/Jinja text wrappers into plain built-in str."""
        raw = self._unwrap(value, fallback=fallback)
        if raw is None:
            return None
        return str(to_text(raw, errors='surrogate_or_strict'))

    def _raw_value(self, record):
        """Return the secret value from a result record (URI or password)."""
        if isinstance(record, dict):
            if record.get('type') == 'host':
                return record.get('password')
            return record.get('uri')
        return record

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_options(self, operation, token_type, algorithm,
                          digits, interval, owner, result_format):
        """Cross-option validation with clear error messages."""
        if token_type == 'host' and operation != 'add':
            raise AnsibleLookupError(
                "type='host' is only valid with operation='add'. "
                "Host enrollment passwords do not have a persistent "
                "token record to find, show, or revoke.")

        if digits not in (6, 8):
            raise AnsibleLookupError(
                "digits must be 6 or 8, got: %r" % digits)

        if not algorithm or not algorithm.strip():
            raise AnsibleLookupError("algorithm cannot be empty.")

        if token_type == 'hotp' and interval != 30:
            display.warning(
                "eigenstate.ipa.otp: 'interval' is only meaningful "
                "for token_type=totp and will be ignored for token_type=hotp.")

        if token_type == 'host' and interval != 30:
            display.warning(
                "eigenstate.ipa.otp: 'interval' is only meaningful "
                "for token_type=totp and will be ignored for token_type=host.")

        if owner and operation != 'find':
            display.warning(
                "eigenstate.ipa.otp: 'owner' is only used as a filter "
                "for operation=find and will be ignored for "
                "operation=%s." % operation)

        if result_format == 'value' and operation in ('find', 'show'):
            raise AnsibleLookupError(
                "result_format='value' is only valid for operation='add'. "
                "Use result_format='record' or result_format='map_record' "
                "for operation='%s'." % operation)

    def _validate_terms(self, operation, terms):
        """Validate that terms are provided when required."""
        if operation == 'add' and not terms:
            raise AnsibleLookupError(
                "operation='add' requires at least one term: a username "
                "for token_type=totp/hotp, or a host FQDN for token_type=host.")
        if operation in ('show', 'revoke') and not terms:
            raise AnsibleLookupError(
                "operation='%s' requires at least one token unique ID "
                "in _terms." % operation)

    # ------------------------------------------------------------------
    # Result builders
    # ------------------------------------------------------------------

    def _build_token_record(self, owner, entry, include_uri=True):
        """Normalize an ipalib OTP token response into an output record."""
        token_type = to_text(
            self._unwrap(
                entry.get('ipatokentype', entry.get('type')),
                fallback=u'totp'),
            errors='surrogate_or_strict').lower()
        interval_raw = self._unwrap(entry.get('ipatokentotptimestep'))
        try:
            interval = int(interval_raw) if interval_raw is not None else None
        except (TypeError, ValueError):
            interval = None

        digits_raw = self._unwrap(entry.get('ipatokenotpdigits'))
        try:
            digits = int(digits_raw) if digits_raw is not None else None
        except (TypeError, ValueError):
            digits = None

        disabled_raw = self._unwrap(entry.get('ipatokendisabled'))
        if disabled_raw is None:
            disabled_raw = entry.get('nsaccountlock')
        if isinstance(disabled_raw, bool):
            disabled = disabled_raw
        elif disabled_raw is not None:
            disabled = bool(disabled_raw)
        else:
            disabled = False

        record = {
            'owner': self._native_text(
                entry.get('ipatokenowner'), fallback=owner or u''),
            'token_id': self._native_text(
                entry.get('ipatokenuniqueid'), fallback=u''),
            'type': token_type,
            'algorithm': self._native_text(
                entry.get('ipatokenotpalgorithm'), fallback=u'sha1'),
            'digits': digits,
            'interval': interval if token_type == 'totp' else None,
            'disabled': disabled,
            'description': (
                self._native_text(entry.get('description'), fallback=u'') or None
            ),
            'exists': True,
        }

        if include_uri:
            uri_raw = self._unwrap(
                entry.get('uri', entry.get('ipatokenotpuri')))
            record['uri'] = (
                self._native_text(uri_raw)
                if uri_raw is not None else None)

        return record

    def _build_host_record(self, fqdn, password):
        """Build a result record for a host enrollment password."""
        return {
            'fqdn': self._native_text(fqdn),
            'type': 'host',
            'password': self._native_text(password),
            'exists': True,
        }

    def _build_not_found_record(self, token_id):
        """Build a result record for a token ID that was not found."""
        return {
            'token_id': self._native_text(token_id),
            'owner': None,
            'type': None,
            'uri': None,
            'algorithm': None,
            'digits': None,
            'interval': None,
            'disabled': None,
            'description': None,
            'exists': False,
        }

    # ------------------------------------------------------------------
    # Result shaping
    # ------------------------------------------------------------------

    def _finalize_results(self, results, result_format, primary_key=None):
        """Apply the requested top-level result container shape."""
        if result_format == 'map':
            return [{
                item[primary_key]: self._raw_value(item)
                for item in results
                if isinstance(item, dict)
            }]
        if result_format == 'map_record':
            return [{
                item[primary_key]: item
                for item in results
                if isinstance(item, dict)
            }]
        if result_format == 'value':
            return [self._raw_value(item) for item in results]
        # record (default)
        return results

    # ------------------------------------------------------------------
    # IPA operations
    # ------------------------------------------------------------------

    def _add_user_token(self, owner, token_type, algorithm, digits,
                        interval, description):
        """Create a TOTP or HOTP token for an IdM user."""
        add_kwargs = {
            'ipatokenowner': self._native_text(owner),
            'type': self._native_text(token_type),
            'ipatokenotpalgorithm': self._native_text(algorithm),
            'ipatokenotpdigits': digits,
        }
        if description:
            add_kwargs['description'] = self._native_text(description)
        if token_type == 'totp':
            add_kwargs['ipatokentotptimestep'] = interval

        try:
            result = _ipa_api.Command.otptoken_add(**add_kwargs)
        except ipalib_errors.NotFound as exc:
            raise AnsibleLookupError(
                "User '%s' not found in IdM. Verify the username "
                "and that the user is enrolled: %s"
                % (owner, to_native(exc)))
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to create OTP tokens for '%s': %s"
                % (owner, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to create %s token for '%s': %s"
                % (token_type.upper(), owner, to_native(exc)))

        entry = result.get('result', {})
        return self._build_token_record(owner, entry, include_uri=True)

    def _add_host_enroll(self, fqdn):
        """Generate a one-time enrollment password for an IdM host."""
        try:
            result = _ipa_api.Command.host_mod(
                self._native_text(fqdn),
                random=True)
        except ipalib_errors.NotFound as exc:
            raise AnsibleLookupError(
                "Host '%s' not found in IdM. Add the host record "
                "before generating an enrollment password: %s"
                % (fqdn, to_native(exc)))
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to set enrollment password for '%s': %s"
                % (fqdn, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to generate enrollment password for '%s': %s"
                % (fqdn, to_native(exc)))

        entry = result.get('result', {})
        password = self._unwrap(entry.get('randompassword'))
        if password is None:
            raise AnsibleLookupError(
                "IdM returned no enrollment password for '%s'. "
                "Verify host_mod supports random=True on this server."
                % fqdn)
        return self._build_host_record(fqdn, password)

    def _find_tokens(self, criteria, owner):
        """Search for OTP tokens, optionally filtered by owner."""
        find_args = {
            'sizelimit': 0,
            'all': True,
        }
        if owner:
            find_args['ipatokenowner'] = self._native_text(owner)

        find_terms = []
        if criteria:
            find_terms = [self._native_text(criteria)]

        try:
            result = _ipa_api.Command.otptoken_find(
                *find_terms, **find_args)
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to search OTP tokens: %s"
                % to_native(exc))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to search OTP tokens: %s" % to_native(exc))

        records = []
        for entry in result.get('result', []):
            record = self._build_token_record(
                owner or '', entry, include_uri=False)
            records.append(record)
        return records

    def _show_token(self, token_id):
        """Retrieve metadata for a token by its unique ID.

        Returns None when the token is not found (caller builds a
        not-found record). All other errors are raised.
        """
        try:
            result = _ipa_api.Command.otptoken_show(
                self._native_text(token_id),
                all=True)
        except ipalib_errors.NotFound:
            return None
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to show token '%s': %s"
                % (token_id, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to show token '%s': %s"
                % (token_id, to_native(exc)))

        entry = result.get('result', {})
        return self._build_token_record('', entry, include_uri=False)

    def _revoke_token(self, token_id):
        """Permanently delete a token by its unique ID."""
        try:
            _ipa_api.Command.otptoken_del(
                self._native_text(token_id))
        except ipalib_errors.NotFound as exc:
            raise AnsibleLookupError(
                "Token '%s' not found. Revocation requires an existing "
                "token ID. Use operation='find' to enumerate tokens: %s"
                % (token_id, to_native(exc)))
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to revoke token '%s': %s"
                % (token_id, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to revoke token '%s': %s"
                % (token_id, to_native(exc)))

        return self._native_text(token_id)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self, terms, variables=None, **kwargs):
        try:
            self._ensure_ipalib()
            self.set_options(var_options=variables, direct=kwargs)

            instance_get_option = self.__dict__.get('get_option')

            def _option(name, default=None, aliases=(), allow_plugin=False):
                for key in (name,) + tuple(aliases):
                    if key in kwargs and kwargs[key] is not None:
                        return kwargs[key]
                if callable(instance_get_option):
                    try:
                        value = instance_get_option(name)
                    except Exception:
                        value = None
                    if value is not None:
                        return value
                    for alias in aliases:
                        try:
                            value = instance_get_option(alias)
                        except Exception:
                            value = None
                        if value is not None:
                            return value
                if allow_plugin:
                    try:
                        value = self.get_option(name)
                    except KeyError:
                        value = None
                    if value is not None:
                        return value
                    for alias in aliases:
                        try:
                            value = self.get_option(alias)
                        except KeyError:
                            value = None
                        if value is not None:
                            return value
                return default

            operation = _option('operation', default='add')
            token_type = _option('token_type', default='totp', aliases=('type',))
            algorithm = _option('algorithm', default='sha1')
            digits = int(_option('digits', default=6))
            interval = int(_option('interval', default=30))
            owner = _option('owner')
            description = _option('description')

            server = _option('server', allow_plugin=True)
            if not server:
                raise AnsibleLookupError(
                    "'server' is required. Set it directly or via the "
                    "IPA_SERVER environment variable.")

            principal = _option('ipaadmin_principal', default='admin', allow_plugin=True)
            password = _option('ipaadmin_password', allow_plugin=True)
            keytab = _option('kerberos_keytab', allow_plugin=True)
            verify = self._resolve_verify(_option('verify', allow_plugin=True))

            # result_format: caller may not specify it; apply operation default
            result_format = _option('result_format')
            if result_format is None:
                result_format = 'value' if operation == 'add' else 'record'

            self._validate_options(
                operation, token_type, algorithm, digits,
                interval, owner, result_format)
            self._validate_terms(operation, terms)

            self._connect(server, principal, password, keytab, verify)

            # ---- revoke --------------------------------------------------
            if operation == 'revoke':
                deleted = []
                for token_id in terms:
                    token_id = self._native_text(token_id)
                    deleted.append(self._revoke_token(token_id))
                return deleted

            # ---- find ----------------------------------------------------
            if operation == 'find':
                criteria = terms[0] if terms else None
                records = self._find_tokens(criteria, owner)
                primary_key = 'token_id'
                return self._finalize_results(
                    records, result_format, primary_key=primary_key)

            # ---- show ----------------------------------------------------
            if operation == 'show':
                records = []
                for token_id in terms:
                    token_id = self._native_text(token_id)
                    entry = self._show_token(token_id)
                    if entry is None:
                        records.append(
                            self._build_not_found_record(token_id))
                    else:
                        records.append(entry)
                primary_key = 'token_id'
                return self._finalize_results(
                    records, result_format, primary_key=primary_key)

            # ---- add -----------------------------------------------------
            records = []
            for term in terms:
                term = self._native_text(term)
                if token_type == 'host':
                    record = self._add_host_enroll(term)
                else:
                    record = self._add_user_token(
                        term, token_type, algorithm,
                        digits, interval, description)
                records.append(record)

            primary_key = 'fqdn' if token_type == 'host' else 'owner'
            return self._finalize_results(
                records, result_format, primary_key=primary_key)

        finally:
            self._cleanup_ccache()

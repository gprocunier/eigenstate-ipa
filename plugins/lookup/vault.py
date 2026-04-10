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
name: vault
version_added: "1.0.0"
short_description: Retrieve secrets from FreeIPA/IDM vaults
description:
  - Retrieves secret data from FreeIPA/IDM vaults.
  - Supports standard, symmetric, and asymmetric vault types.
  - Uses the C(ipalib) framework for vault operations, which handles
    transport encryption and vault-level decryption automatically.
  - Authenticates via password (converted to a Kerberos ticket) or
    an existing Kerberos ticket/keytab.
  - Can be used as a credential source in AAP by referencing the
    lookup in a custom credential type injector.
options:
  _terms:
    description: >-
      One or more vault names to retrieve or inspect when
      C(operation=retrieve) or C(operation=show). Not required when
      C(operation=find).
    type: list
    elements: str
  operation:
    description: >-
      Which vault operation to perform. C(retrieve) returns secret
      payloads, C(show) returns metadata for the named vaults, and
      C(find) searches the selected vault scope and returns matching
      metadata records.
    type: str
    default: retrieve
    choices: ["retrieve", "show", "find"]
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
      Password for the admin principal. The plugin uses this to
      obtain a Kerberos ticket via C(kinit). Not required if
      C(kerberos_keytab) is set or a valid ticket already exists.
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
      Path to the IPA CA certificate for TLS verification.
      If not set, the system CA bundle is used.
    type: str
    env:
      - name: IPA_CERT
  username:
    description: >-
      Retrieve a user vault owned by this user. Mutually exclusive
      with C(service) and C(shared).
    type: str
  service:
    description: >-
      Retrieve a service vault owned by this service principal.
      Mutually exclusive with C(username) and C(shared).
    type: str
  shared:
    description: >-
      Retrieve a shared vault. Mutually exclusive with C(username)
      and C(service).
    type: bool
    default: false
  vault_password:
    description: >-
      Password to decrypt a symmetric vault.
    type: str
    secret: true
  vault_password_file:
    description: >-
      Path to a file containing the symmetric vault password.
    type: str
  private_key_file:
    description: >-
      Path to the private key file for decrypting an asymmetric vault.
    type: str
  encoding:
    description: >-
      How to return the vault data. C(utf-8) decodes the bytes to
      a string (suitable for passwords, API keys, PEM certificates).
      C(base64) returns the data as a base64-encoded string
      (suitable for binary secrets like keytabs or PKCS12 bundles).
    type: str
    default: utf-8
    choices: ["utf-8", "base64"]
  result_format:
    description: >-
      How to shape the lookup result. C(value) returns only the
      decoded secret value. C(record) returns a list of structured
      result records with the vault name, scope, encoding, and value.
      C(map) returns a dictionary of vault name to decoded value.
      C(map_record) returns a dictionary of vault name to structured
      result record.
    type: str
    default: value
    choices: ["value", "record", "map", "map_record"]
  include_metadata:
    description: >-
      When set to C(true), include vault metadata fields in retrieved
      structured records. This is only valid with
      C(operation=retrieve) and C(result_format=record) or
      C(result_format=map_record). The lookup uses vault metadata
      already read during preflight when possible, and falls back to
      best-effort metadata retrieval if needed.
    type: bool
    default: false
  decode_json:
    description: >-
      When set to C(true), parse decoded UTF-8 vault payloads as JSON
      and return structured data instead of a raw string. Only valid
      with C(encoding=utf-8) and C(operation=retrieve).
    type: bool
    default: false
  strip_trailing_newline:
    description: >-
      When set to C(true), remove a single trailing newline from
      decoded UTF-8 payloads before returning them. Useful for
      password-like secrets stored with a trailing newline.
    type: bool
    default: false
  criteria:
    description: >-
      Search criteria used when C(operation=find). If omitted, the
      find operation lists the selected vault scope without a text
      filter.
    type: str
notes:
  - This plugin requires C(python3-ipalib) and C(python3-ipaclient)
    on the Ansible controller. These handle the vault transport
    encryption and vault-level decryption automatically.
  - "RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)"
  - For symmetric vaults, provide C(vault_password) or
    C(vault_password_file).
  - For asymmetric vaults, provide C(private_key_file).
  - Standard vaults require no additional decryption parameters.
  - Local secret material referenced through C(kerberos_keytab),
    C(vault_password_file), or C(private_key_file) should normally
    be owner-readable only, such as mode C(0600).
seealso:
  - module: redhat.rhel_idm.ipavault
author:
  - Greg Procunier
"""

EXAMPLES = """
# Retrieve a standard shared vault using environment-backed auth
- name: Get database password
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault', 'database-password',
             server='idm-01.example.com',
             ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
             shared=true) }}"

# Retrieve a symmetric vault
- name: Get API key from symmetric vault
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault', 'api-key',
             server='idm-01.example.com',
             ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
             shared=true,
             vault_password=lookup('env', 'IPA_VAULT_PASSWORD')) }}"

# Retrieve an asymmetric vault
- name: Get TLS private key from asymmetric vault
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault', 'tls-key',
             server='idm-01.example.com',
             ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
             shared=true,
             private_key_file='/path/to/private.pem') }}"

# Retrieve a user vault with keytab auth (AAP)
- name: Get user secret
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault', 'my-secret',
             server='idm-01.example.com',
             kerberos_keytab='/path/to/admin.keytab',
             username='appuser') }}"

# Retrieve a binary secret as base64
- name: Get keytab from vault
  ansible.builtin.copy:
    content: "{{ lookup('eigenstate.ipa.vault', 'service-keytab',
                  server='idm-01.example.com',
                  ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
                  shared=true,
                  encoding='base64') | b64decode }}"
    dest: /etc/krb5.keytab
    mode: "0600"

# Multiple vaults in one lookup
- name: Retrieve several secrets
  ansible.builtin.set_fact:
    secrets: "{{ lookup('eigenstate.ipa.vault', 'db-pass', 'api-key',
                  server='idm-01.example.com',
                  ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
                  shared=true) }}"

# Return a named mapping instead of a positional list
- name: Retrieve several secrets as a dictionary
  ansible.builtin.set_fact:
    secrets_by_name: "{{ lookup('eigenstate.ipa.vault', 'db-pass', 'api-key',
                          server='idm-01.example.com',
                          ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
                          shared=true,
                          result_format='map') }}"

# Decode a JSON secret into structured data
- name: Retrieve structured JSON config
  ansible.builtin.set_fact:
    app_config: "{{ lookup('eigenstate.ipa.vault', 'app-config',
                    server='idm-01.example.com',
                    kerberos_keytab='/path/to/admin.keytab',
                    shared=true,
                    decode_json=true) }}"

# Retrieve an encrypted artifact with metadata for brokered delivery
- name: Get sealed artifact with routing metadata
  ansible.builtin.set_fact:
    sealed_artifact: "{{ lookup('eigenstate.ipa.vault', 'payments-bootstrap-bundle',
                         server='idm-01.example.com',
                         kerberos_keytab='/path/to/admin.keytab',
                         shared=true,
                         encoding='base64',
                         result_format='record',
                         include_metadata=true) }}"

# Inspect one vault without retrieving the secret payload
- name: Show vault metadata
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault', 'database-password',
             server='idm-01.example.com',
             kerberos_keytab='/path/to/admin.keytab',
             shared=true,
             operation='show') }}"

# Find vaults in the selected scope
- name: List shared vaults that match a string
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault',
             server='idm-01.example.com',
             kerberos_keytab='/path/to/admin.keytab',
             shared=true,
             operation='find',
             criteria='database') }}"

# Use with env vars (set IPA_SERVER, IPA_ADMIN_PASSWORD)
- name: Get secret using environment
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault', 'my-secret', shared=true) }}"
"""

RETURN = """
_raw:
  description: >-
    The decrypted vault data. One element per vault name requested.
    Returned as a UTF-8 string by default, or base64-encoded if
    C(encoding=base64). If C(result_format=record), each element is a
    structured dictionary containing the name, scope, encoding, and
    decoded value. If C(include_metadata=true), retrieved structured
    records also include vault metadata fields such as type,
    description, and vault_id. When C(decode_json=true), UTF-8 payloads are
    parsed into structured JSON values. When
    C(result_format=map) or C(result_format=map_record),
    the return value is a dictionary keyed by vault name. Metadata-only
    operations C(show) and C(find) return structured records.
  type: raw
"""

import base64
import json
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
    """Retrieve secrets from FreeIPA/IDM vaults."""

    def __init__(self, *args, **kwargs):
        super(LookupModule, self).__init__(*args, **kwargs)
        self._result_cache = {}
        self._ccache_path = None
        self._previous_ccache = None
        self._managing_ccache = False

    def _ensure_ipalib(self):
        if not HAS_IPALIB:
            raise AnsibleLookupError(
                "The 'ipalib' Python library is required for the "
                "eigenstate.ipa.vault lookup plugin.\n"
                "  RHEL/Fedora: dnf install python3-ipalib "
                "python3-ipaclient\n"
                "  The vault retrieval process requires client-side "
                "transport decryption that only ipalib provides.")

    def _kinit_keytab(self, keytab, principal):
        """Obtain a Kerberos ticket from a keytab file."""
        if not os.path.isfile(keytab):
            raise AnsibleLookupError(
                "Kerberos keytab file not found: %s" % keytab)

        self._warn_if_sensitive_file_permissive(keytab, "kerberos_keytab")

        ccache_fd, ccache_path = tempfile.mkstemp(
            prefix='krb5cc_ipa_vault_')
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
            prefix='krb5cc_ipa_vault_')
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
                    "TLS verification is disabled for eigenstate.ipa.vault. "
                    "Set 'verify' to the IPA CA certificate path for "
                    "production use."
                )
                return False
        elif isinstance(verify, str):
            verify = verify.strip()
            if verify.lower() in ('false', 'no', 'off', '0'):
                display.warning(
                    "TLS verification is disabled for eigenstate.ipa.vault. "
                    "Set 'verify' to the IPA CA certificate path for "
                    "production use."
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
            "TLS verification is disabled for eigenstate.ipa.vault. "
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

    def _scope_label(self, username, service, shared):
        """Return a human-readable scope label."""
        if username:
            return "username=%s" % username
        if service:
            return "service=%s" % service
        if shared:
            return "shared"
        return "default"

    def _validate_scope(self, username, service, shared):
        """Validate mutually exclusive scope options."""
        scope_count = sum(bool(x) for x in [username, service, shared])
        if scope_count > 1:
            raise AnsibleLookupError(
                "'username', 'service', and 'shared' are mutually "
                "exclusive. Specify at most one.")

    def _validate_decryption_inputs(self, vault_password,
                                    vault_password_file,
                                    private_key_file):
        """Validate mutually exclusive decryption inputs."""
        if vault_password and vault_password_file:
            raise AnsibleLookupError(
                "'vault_password' and 'vault_password_file' are "
                "mutually exclusive. Specify only one symmetric "
                "vault secret source.")
        if (vault_password or vault_password_file) and private_key_file:
            raise AnsibleLookupError(
                "Symmetric vault inputs ('vault_password' or "
                "'vault_password_file') cannot be combined with "
                "'private_key_file'. Choose the matching vault type "
                "for the secret you are retrieving.")

    def _validate_output_options(self, operation, encoding,
                                 result_format, include_metadata,
                                 decode_json, strip_trailing_newline):
        """Validate output shaping options."""
        if decode_json and encoding != 'utf-8':
            raise AnsibleLookupError(
                "'decode_json' requires encoding='utf-8'.")
        if include_metadata and operation != 'retrieve':
            raise AnsibleLookupError(
                "'include_metadata' only applies to "
                "operation='retrieve'.")
        if include_metadata and result_format not in ('record', 'map_record'):
            raise AnsibleLookupError(
                "'include_metadata' requires result_format='record' "
                "or result_format='map_record'.")
        if operation in ('show', 'find') and decode_json:
            raise AnsibleLookupError(
                "'decode_json' only applies to operation='retrieve'.")
        if operation in ('show', 'find') and strip_trailing_newline:
            raise AnsibleLookupError(
                "'strip_trailing_newline' only applies to "
                "operation='retrieve'.")

    def _decode_vault_value(self, data, encoding):
        """Decode a vault payload to the requested encoding."""
        if encoding == 'base64':
            if isinstance(data, bytes):
                return base64.b64encode(data).decode('ascii')
            return base64.b64encode(data.encode('utf-8')).decode('ascii')
        if isinstance(data, bytes):
            return to_text(data, errors='surrogate_or_strict')
        return data

    def _normalize_text_value(self, value, decode_json,
                              strip_trailing_newline):
        """Apply text-specific normalization helpers."""
        if strip_trailing_newline and isinstance(value, str):
            value = value[:-1] if value.endswith('\n') else value
        if decode_json:
            try:
                return json.loads(value)
            except ValueError as exc:
                raise AnsibleLookupError(
                    "Failed to decode vault payload as JSON: %s"
                    % to_native(exc))
        return value

    def _format_vault_result(self, name, data, encoding, result_format,
                             scope_label, metadata=None,
                             decode_json=False,
                             strip_trailing_newline=False):
        """Shape a vault lookup result."""
        value = self._decode_vault_value(data, encoding)
        if encoding == 'utf-8':
            value = self._normalize_text_value(
                value, decode_json, strip_trailing_newline)
        if result_format in ('record', 'map', 'map_record'):
            result = {
                'name': name,
                'scope': scope_label,
                'encoding': encoding,
                'value': value,
            }
            if metadata:
                result.update({
                    'type': metadata.get('type'),
                    'description': metadata.get('description'),
                    'vault_id': metadata.get('vault_id'),
                })
            return result
        return value

    def _unwrap(self, value):
        """Unwrap IPA-style single-element lists."""
        if isinstance(value, (list, tuple)):
            if len(value) == 1:
                return value[0]
            if len(value) == 0:
                return None
        return value

    def _format_vault_metadata(self, name, entry, scope_label):
        """Normalize vault metadata records returned by show/find."""
        if entry is None:
            entry = {}
        return {
            'name': name,
            'scope': scope_label,
            'type': self._unwrap(entry.get('ipavaulttype')),
            'description': self._unwrap(entry.get('description')),
            'vault_id': self._unwrap(entry.get('ipavaultid')),
        }

    def _cache_get(self, key):
        """Read a memoized result for this lookup run."""
        return self._result_cache.get(key)

    def _cache_set(self, key, value):
        """Memoize a result for this lookup run."""
        self._result_cache[key] = value
        return value

    def _get_vault_metadata(self, name, scope_label, **kwargs):
        """Read vault metadata with per-run memoization."""
        cache_key = ("metadata", name, scope_label)
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached
        metadata = self._show_vault(name, scope_label, **kwargs)
        return self._cache_set(cache_key, metadata)

    def _scope_args(self, username, service, shared):
        """Build scope arguments for IPA commands."""
        scope_args = {}
        if username:
            scope_args['username'] = str(
                to_text(username, errors='surrogate_or_strict')
            )
        elif service:
            scope_args['service'] = str(
                to_text(service, errors='surrogate_or_strict')
            )
        elif shared:
            scope_args['shared'] = True
        return scope_args

    def _validate_terms_for_operation(self, operation, terms):
        """Validate term usage for the selected operation."""
        if operation in ('retrieve', 'show') and not terms:
            raise AnsibleLookupError(
                "At least one vault name is required when "
                "operation=%s." % operation)

    def _validate_vault_type_inputs(self, name, vault_type,
                                    vault_password,
                                    vault_password_file,
                                    private_key_file):
        """Validate decryption inputs against a known vault type."""
        has_symmetric = bool(vault_password or vault_password_file)
        has_asymmetric = bool(private_key_file)

        if vault_type == 'standard':
            if has_symmetric or has_asymmetric:
                raise AnsibleLookupError(
                    "Vault '%s' is a standard vault. Do not provide "
                    "'vault_password', 'vault_password_file', or "
                    "'private_key_file'." % name)
        elif vault_type == 'symmetric':
            if has_asymmetric:
                raise AnsibleLookupError(
                    "Vault '%s' is a symmetric vault. Provide "
                    "'vault_password' or 'vault_password_file', not "
                    "'private_key_file'." % name)
            if not has_symmetric:
                raise AnsibleLookupError(
                    "Vault '%s' is a symmetric vault. Provide "
                    "'vault_password' or 'vault_password_file'."
                    % name)
        elif vault_type == 'asymmetric':
            if has_symmetric:
                raise AnsibleLookupError(
                    "Vault '%s' is an asymmetric vault. Provide "
                    "'private_key_file', not 'vault_password' or "
                    "'vault_password_file'." % name)
            if not has_asymmetric:
                raise AnsibleLookupError(
                    "Vault '%s' is an asymmetric vault. Provide "
                    "'private_key_file'." % name)

    def _preflight_retrieve(self, name, scope_label, **kwargs):
        """Best-effort validation of decryption inputs against vault type."""
        try:
            metadata = self._get_vault_metadata(name, scope_label, **kwargs)
        except AnsibleLookupError:
            return None

        self._validate_vault_type_inputs(
            name,
            metadata.get('type'),
            kwargs.get('vault_password'),
            kwargs.get('vault_password_file'),
            kwargs.get('private_key_file'),
        )
        return metadata

    def _best_effort_metadata(self, name, scope_label, **kwargs):
        """Return metadata when available without turning it into a hard dependency."""
        try:
            return self._get_vault_metadata(name, scope_label, **kwargs)
        except AnsibleLookupError:
            return None

    def _connect(self, server, principal, password, keytab, verify):
        """Authenticate and connect to the IPA server."""
        # Obtain a Kerberos ticket
        if keytab:
            self._kinit_keytab(keytab, principal)
        elif password:
            self._kinit_password(principal, password)
        else:
            # Assume an existing ticket
            if 'KRB5CCNAME' not in os.environ:
                display.warning(
                    "No password or keytab provided and KRB5CCNAME "
                    "is not set. Assuming a valid Kerberos ticket "
                    "exists in the default ccache.")

        # Bootstrap ipalib if not already done
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

    def _retrieve_vault(self, name, scope_label, **kwargs):
        """Retrieve a single vault's data via ipalib."""
        name = str(to_text(name, errors='surrogate_or_strict'))
        retrieve_args = {}

        # Vault ownership scope
        if kwargs.get('username'):
            retrieve_args['username'] = kwargs['username']
        elif kwargs.get('service'):
            retrieve_args['service'] = kwargs['service']
        elif kwargs.get('shared'):
            retrieve_args['shared'] = True

        # Decryption parameters
        if kwargs.get('vault_password'):
            retrieve_args['password'] = kwargs['vault_password']
        elif kwargs.get('vault_password_file'):
            pw_path = kwargs['vault_password_file']
            if not os.path.isfile(pw_path):
                raise AnsibleLookupError(
                    "vault_password_file not found: %s" % pw_path)
            self._warn_if_sensitive_file_permissive(
                pw_path, "vault_password_file")
            with open(pw_path, 'r') as fh:
                retrieve_args['password'] = fh.read().rstrip('\n')

        if kwargs.get('private_key_file'):
            pk_path = kwargs['private_key_file']
            if not os.path.isfile(pk_path):
                raise AnsibleLookupError(
                    "private_key_file not found: %s" % pk_path)
            self._warn_if_sensitive_file_permissive(
                pk_path, "private_key_file")
            with open(pk_path, 'rb') as fh:
                retrieve_args['private_key'] = fh.read()

        try:
            result = _ipa_api.Command.vault_retrieve(
                name, **retrieve_args)
        except ipalib_errors.NotFound:
            raise AnsibleLookupError(
                "Vault '%s' not found for scope '%s'. Check the vault "
                "name and ownership scope (username/service/shared)."
                % (name, scope_label))
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to retrieve vault '%s' for scope '%s': %s"
                % (name, scope_label, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to retrieve vault '%s' for scope '%s': %s"
                % (name, scope_label, to_native(exc)))

        data = result.get('result', {}).get('data')
        if data is None:
            raise AnsibleLookupError(
                "Vault '%s' exists but returned no data." % name)

        return data

    def _show_vault(self, name, scope_label, **kwargs):
        """Return metadata for a single vault."""
        name = str(to_text(name, errors='surrogate_or_strict'))
        show_args = self._scope_args(
            kwargs.get('username'),
            kwargs.get('service'),
            kwargs.get('shared'),
        )
        show_args.update({
            'all': True,
            'raw': False,
            'no_members': False,
        })

        try:
            result = _ipa_api.Command.vault_show(name, **show_args)
        except ipalib_errors.NotFound:
            raise AnsibleLookupError(
                "Vault '%s' not found for scope '%s'. Check the vault "
                "name and ownership scope (username/service/shared)."
                % (name, scope_label))
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to inspect vault '%s' for scope '%s': %s"
                % (name, scope_label, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to inspect vault '%s' for scope '%s': %s"
                % (name, scope_label, to_native(exc)))

        entry = result.get('result', {})
        return self._format_vault_metadata(name, entry, scope_label)

    def _find_vaults(self, criteria, scope_label, **kwargs):
        """Search for vault metadata in the selected scope."""
        if criteria is not None:
            criteria = str(to_text(criteria, errors='surrogate_or_strict'))
        find_args = self._scope_args(
            kwargs.get('username'),
            kwargs.get('service'),
            kwargs.get('shared'),
        )
        find_args.update({
            'all': True,
            'raw': False,
            'no_members': True,
            'sizelimit': 0,
        })
        find_terms = []
        if criteria:
            find_terms = [criteria]

        try:
            result = _ipa_api.Command.vault_find(*find_terms, **find_args)
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to search vaults for scope '%s': %s"
                % (scope_label, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to search vaults for scope '%s': %s"
                % (scope_label, to_native(exc)))

        records = []
        for entry in result.get('result', []):
            name = self._unwrap(entry.get('cn'))
            records.append(self._format_vault_metadata(name, entry, scope_label))
        return records

    def _finalize_results(self, results, result_format):
        """Apply the requested top-level result container shape."""
        if result_format == 'map':
            return {
                item['name']: item.get('value', item)
                for item in results
            }
        if result_format == 'map_record':
            return {item['name']: item for item in results}
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
            encoding = self.get_option('encoding')
            result_format = self.get_option('result_format')
            include_metadata = self.get_option('include_metadata')
            decode_json = self.get_option('decode_json')
            strip_trailing_newline = self.get_option('strip_trailing_newline')
            criteria = self.get_option('criteria')

            # Vault scope
            username = self.get_option('username')
            service = self.get_option('service')
            shared = self.get_option('shared')

            # Decryption params
            vault_password = self.get_option('vault_password')
            vault_password_file = self.get_option('vault_password_file')
            private_key_file = self.get_option('private_key_file')

            self._validate_scope(username, service, shared)
            self._validate_decryption_inputs(
                vault_password, vault_password_file, private_key_file)
            self._validate_output_options(
                operation, encoding, result_format, include_metadata,
                decode_json, strip_trailing_newline)

            scope_label = self._scope_label(username, service, shared)
            self._validate_terms_for_operation(operation, terms)

            self._connect(server, principal, password, keytab, verify)

            if operation == 'find':
                return self._finalize_results(self._find_vaults(
                    criteria,
                    scope_label,
                    username=username,
                    service=service,
                    shared=shared,
                ), result_format)

            results = []
            for vault_name in terms:
                vault_name = str(
                    to_text(vault_name, errors='surrogate_or_strict')
                )
                cache_key = (
                    operation,
                    vault_name,
                    scope_label,
                    encoding,
                    result_format,
                    include_metadata,
                    decode_json,
                    strip_trailing_newline,
                    bool(vault_password),
                    vault_password_file,
                    private_key_file,
                )
                cached = self._cache_get(cache_key)
                if cached is not None:
                    results.append(cached)
                    continue

                if operation == 'show':
                    item = self._show_vault(
                        vault_name,
                        scope_label,
                        username=username,
                        service=service,
                        shared=shared,
                    )
                else:
                    metadata = self._preflight_retrieve(
                        vault_name,
                        scope_label,
                        username=username,
                        service=service,
                        shared=shared,
                        vault_password=vault_password,
                        vault_password_file=vault_password_file,
                        private_key_file=private_key_file,
                    )
                    if include_metadata and metadata is None:
                        metadata = self._best_effort_metadata(
                            vault_name,
                            scope_label,
                            username=username,
                            service=service,
                            shared=shared,
                        )
                    data = self._retrieve_vault(
                        vault_name,
                        scope_label,
                        username=username,
                        service=service,
                        shared=shared,
                        vault_password=vault_password,
                        vault_password_file=vault_password_file,
                        private_key_file=private_key_file,
                    )
                    item = self._format_vault_result(
                        vault_name, data, encoding, result_format, scope_label,
                        metadata,
                        decode_json, strip_trailing_newline)

                results.append(self._cache_set(cache_key, item))

            return self._finalize_results(results, result_format)
        finally:
            self._cleanup_ccache()

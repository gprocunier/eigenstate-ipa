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
name: cert
version_added: "1.1.0"
short_description: Request or retrieve certificates from FreeIPA/IDM PKI
description:
  - Submits a CSR to the IdM/FreeIPA Dogtag CA and returns a signed
    certificate (C(operation=request)).
  - Retrieves an existing certificate by serial number
    (C(operation=retrieve)).
  - Searches certificates by principal, subject, or expiry window
    (C(operation=find)).
  - Uses the C(ipalib) framework for all CA operations and Kerberos
    transport.  No C(certmonger) daemon is required on the target.
  - Authenticates via a Kerberos keytab, a password, or an existing
    Kerberos ticket in the environment.
  - Designed as a drop-in alternative to HashiCorp Vault's PKI secrets
    engine when Red Hat IdM is already the identity backend.
options:
  _terms:
    description: >-
      For C(operation=request): one or more service or host principals
      to request a certificate for (e.g.
      C(HTTP/web.example.com@EXAMPLE.COM)).  For C(operation=retrieve):
      one or more certificate serial numbers (decimal or hex C(0x...)).
      Not used when C(operation=find).
    type: list
    elements: str
  operation:
    description: >-
      Which PKI operation to perform.  C(request) submits a CSR and
      returns the signed certificate.  C(retrieve) fetches a certificate
      by serial number.  C(find) searches the CA for certificates
      matching the supplied filters.
    type: str
    default: request
    choices: ["request", "retrieve", "find"]
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
      Password for the admin principal.  The plugin uses this to obtain
      a Kerberos ticket via C(kinit).  Not required if C(kerberos_keytab)
      is set or a valid ticket already exists.
    type: str
    secret: true
    env:
      - name: IPA_ADMIN_PASSWORD
  kerberos_keytab:
    description: >-
      Path to a Kerberos keytab file.  Used to obtain a ticket
      non-interactively (required for AAP Execution Environments).
    type: str
    env:
      - name: IPA_KEYTAB
  verify:
    description: >-
      Path to the IPA CA certificate for TLS verification.  Defaults to
      C(/etc/ipa/ca.crt) when that file exists.  If neither is available
      TLS verification is disabled with a warning.
    type: str
    env:
      - name: IPA_CERT
  encoding:
    description: >-
      Certificate output format.  C(pem) wraps the DER bytes in PEM
      headers (suitable for writing directly to files or passing to
      other modules).  C(base64) returns the raw base64-encoded DER
      (suitable for binary pipelines or storage in IdM vaults).
    type: str
    default: pem
    choices: ["pem", "base64"]
  result_format:
    description: >-
      How to shape the lookup result.  C(value) returns only the
      certificate string.  C(record) returns a structured dictionary
      with the certificate value and metadata.  C(map) returns a
      dictionary keyed by principal or serial number to certificate
      value.  C(map_record) returns a dictionary keyed by principal
      or serial number to the full structured record.
    type: str
    default: value
    choices: ["value", "record", "map", "map_record"]
  csr:
    description: >-
      Certificate Signing Request as an inline PEM string.  Used only
      with C(operation=request).  Mutually exclusive with C(csr_file).
    type: str
  csr_file:
    description: >-
      Path to a PEM-formatted CSR file on the Ansible controller.  Used
      only with C(operation=request).  Mutually exclusive with C(csr).
    type: str
  profile:
    description: >-
      Certificate profile ID to use when signing.  If not set, the IdM
      default profile (C(caIPAserviceCert)) is used.  Run
      C(ipa certprofile-find) to list available profiles.
    type: str
  ca:
    description: >-
      Name of the sub-CA to issue the certificate from.  Defaults to
      the root IPA CA.  Run C(ipa ca-find) to list available CAs.
    type: str
  add:
    description: >-
      When C(true), automatically create the service or host principal
      in IdM if it does not already exist.  Equivalent to
      C(ipa cert-request --add).
    type: bool
    default: false
  principal:
    description: >-
      Filter certificates by service or host principal.  Used only with
      C(operation=find).
    type: str
  subject:
    description: >-
      Filter certificates by subject DN substring.  Used only with
      C(operation=find).
    type: str
  valid_not_after_from:
    description: >-
      Lower bound for the certificate expiry date (ISO 8601 YYYY-MM-DD).
      Returns certificates that expire on or after this date.  Used only
      with C(operation=find).  Combine with C(valid_not_after_to) to
      build a maintenance window query.
    type: str
  valid_not_after_to:
    description: >-
      Upper bound for the certificate expiry date (ISO 8601 YYYY-MM-DD).
      Returns certificates that expire on or before this date.  Used
      only with C(operation=find).
    type: str
  revocation_reason:
    description: >-
      Filter by revocation reason code (0-10).  Used only with
      C(operation=find).  See RFC 5280 section 5.3.1 for reason codes.
    type: int
  exactly:
    description: >-
      When C(true), C(subject) is matched exactly rather than as a
      substring.  Used only with C(operation=find).
    type: bool
    default: false
notes:
  - Requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible
    controller.
  - "RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)"
  - The authenticating principal must hold the C(Request Certificate)
    IdM privilege (or equivalent ACI) to use C(operation=request).
  - C(operation=retrieve) and C(operation=find) require only standard
    read access to the IPA CA.
  - CSR files referenced via C(csr_file) should be owner-readable only
    (mode C(0600)) when they contain private material.
  - When C(add=true) the principal must not already exist, otherwise
    IdM returns an error.  Use C(operation=find) to check first.
seealso:
  - module: redhat.rhel_idm.ipacert
  - lookup: eigenstate.ipa.vault
  - lookup: eigenstate.ipa.keytab
author:
  - Greg Procunier
"""

EXAMPLES = """
# Request a certificate for an HTTP service principal
- name: Request TLS certificate for web server
  ansible.builtin.copy:
    content: "{{ lookup('eigenstate.ipa.cert',
                  'HTTP/web.example.com@EXAMPLE.COM',
                  operation='request',
                  server='idm-01.example.com',
                  kerberos_keytab='/etc/krb5.keytab',
                  csr_file='/etc/pki/tls/certs/web.csr') }}"
    dest: /etc/pki/tls/certs/web.pem
    mode: "0644"

# Request a cert and capture full metadata
- name: Request cert with metadata
  ansible.builtin.set_fact:
    cert_record: "{{ lookup('eigenstate.ipa.cert',
                      'HTTP/web.example.com@EXAMPLE.COM',
                      operation='request',
                      server='idm-01.example.com',
                      ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
                      csr=my_csr_variable,
                      result_format='record') }}"

- name: Show expiry date
  ansible.builtin.debug:
    msg: "Certificate expires: {{ cert_record.metadata.valid_not_after }}"

# Request with a specific profile and sub-CA
- name: Request cert with custom profile
  ansible.builtin.set_fact:
    cert_pem: "{{ lookup('eigenstate.ipa.cert',
                   'vault/backup.example.com@EXAMPLE.COM',
                   operation='request',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/krb5.keytab',
                   csr=csr_content,
                   profile='caIPAserviceCert',
                   ca='internal-ca') }}"

# Request and auto-create the principal if missing
- name: Bootstrap new service principal with cert
  ansible.builtin.set_fact:
    new_cert: "{{ lookup('eigenstate.ipa.cert',
                   'HTTP/newhost.example.com@EXAMPLE.COM',
                   operation='request',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/krb5.keytab',
                   csr=csr_content,
                   add=true) }}"

# Retrieve a certificate by serial number (decimal)
- name: Retrieve cert by serial
  ansible.builtin.set_fact:
    cert_pem: "{{ lookup('eigenstate.ipa.cert', '12345',
                   operation='retrieve',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/krb5.keytab') }}"

# Retrieve multiple certificates by serial; map by serial number
- name: Retrieve several certs as a dictionary
  ansible.builtin.set_fact:
    certs: "{{ lookup('eigenstate.ipa.cert',
                '12345', '67890',
                operation='retrieve',
                server='idm-01.example.com',
                kerberos_keytab='/etc/krb5.keytab',
                result_format='map') }}"

# Find all certificates expiring within 30 days (pre-expiry maintenance)
- name: Find certs expiring soon
  ansible.builtin.set_fact:
    expiring: "{{ lookup('eigenstate.ipa.cert',
                   operation='find',
                   server='idm-01.example.com',
                   kerberos_keytab='/etc/krb5.keytab',
                   valid_not_after_from='2026-04-05',
                   valid_not_after_to='2026-05-05',
                   result_format='record') }}"

# Find all certs issued to a specific service principal
- name: Find certs for a principal
  ansible.builtin.set_fact:
    principal_certs: "{{ lookup('eigenstate.ipa.cert',
                          operation='find',
                          server='idm-01.example.com',
                          kerberos_keytab='/etc/krb5.keytab',
                          principal='HTTP/web.example.com@EXAMPLE.COM',
                          result_format='map_record') }}"

# Retrieve cert as raw base64 DER for use with Java keystores
- name: Get cert as base64 DER
  ansible.builtin.set_fact:
    cert_der_b64: "{{ lookup('eigenstate.ipa.cert', '12345',
                       operation='retrieve',
                       server='idm-01.example.com',
                       kerberos_keytab='/etc/krb5.keytab',
                       encoding='base64') }}"
"""

RETURN = """
_raw:
  description: >-
    Certificate data for the requested operation.  The exact structure
    depends on C(result_format) and C(operation).

    For C(operation=request) or C(operation=retrieve): one element per
    term.  For C(operation=find): a list of matching certificates.

    With C(result_format=value) (default): a PEM string per certificate,
    or base64-encoded DER when C(encoding=base64).

    With C(result_format=record): each element is a structured dictionary
    containing the certificate value plus metadata (serial_number,
    subject, issuer, valid_not_before, valid_not_after, san, revoked,
    revocation_reason).

    With C(result_format=map) or C(result_format=map_record): a
    dictionary keyed by the service principal (for C(request)) or serial
    number string (for C(retrieve) and C(find)).
  type: raw
"""

import base64
import os
import stat
import subprocess
import tempfile
import textwrap
from datetime import datetime

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
    """Request or retrieve certificates from FreeIPA/IDM PKI."""

    def __init__(self, *args, **kwargs):
        super(LookupModule, self).__init__(*args, **kwargs)
        self._ccache_path = None
        self._previous_ccache = None
        self._managing_ccache = False

    # ---------------------------------------------------------------
    # Dependency guard
    # ---------------------------------------------------------------

    def _ensure_ipalib(self):
        if not HAS_IPALIB:
            raise AnsibleLookupError(
                "The 'ipalib' Python library is required for the "
                "eigenstate.ipa.cert lookup plugin.\n"
                "  RHEL/Fedora: dnf install python3-ipalib "
                "python3-ipaclient")

    # ---------------------------------------------------------------
    # Kerberos credential management (mirrors vault.py exactly)
    # ---------------------------------------------------------------

    def _kinit_keytab(self, keytab, principal):
        """Obtain a Kerberos ticket from a keytab file."""
        if not os.path.isfile(keytab):
            raise AnsibleLookupError(
                "Kerberos keytab file not found: %s" % keytab)

        self._warn_if_sensitive_file_permissive(keytab, "kerberos_keytab")

        ccache_fd, ccache_path = tempfile.mkstemp(
            prefix='krb5cc_ipa_cert_')
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
            prefix='krb5cc_ipa_cert_')
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
                    ['kinit', principal],
                    input=password, capture_output=True, text=True,
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

    # ---------------------------------------------------------------
    # TLS and file helpers
    # ---------------------------------------------------------------

    def _default_verify_path(self):
        """Return the conventional IPA CA path when it exists locally."""
        default_path = '/etc/ipa/ca.crt'
        if os.path.exists(default_path):
            return default_path
        return None

    def _resolve_verify(self, verify):
        """Resolve TLS verification behavior for lookup requests."""
        if verify is not None:
            if not os.path.exists(verify):
                raise AnsibleLookupError(
                    "TLS certificate file not found: %s" % verify)
            return verify

        default_verify = self._default_verify_path()
        if default_verify is not None:
            return default_verify

        display.warning(
            "TLS verification is disabled for eigenstate.ipa.cert. "
            "Set 'verify' to the IPA CA certificate path for "
            "production use.")
        return False

    def _warn_if_sensitive_file_permissive(self, path, option_name):
        """Warn when sensitive local files are readable by non-owners."""
        mode = stat.S_IMODE(os.stat(path).st_mode)
        if mode & 0o077:
            display.warning(
                "%s '%s' has permissions %s which are more permissive "
                "than 0600." % (option_name, path, oct(mode)))

    # ---------------------------------------------------------------
    # IPA connection (mirrors vault.py exactly)
    # ---------------------------------------------------------------

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

    # ---------------------------------------------------------------
    # Input validation
    # ---------------------------------------------------------------

    def _validate_operation(self, operation):
        valid = ('request', 'retrieve', 'find')
        if operation not in valid:
            raise AnsibleLookupError(
                "Invalid operation '%s'. Valid values: %s"
                % (operation, ', '.join(valid)))

    def _validate_encoding(self, encoding):
        valid = ('pem', 'base64')
        if encoding not in valid:
            raise AnsibleLookupError(
                "Invalid encoding '%s'. Valid values: %s"
                % (encoding, ', '.join(valid)))

    def _validate_result_format(self, result_format):
        valid = ('value', 'record', 'map', 'map_record')
        if result_format not in valid:
            raise AnsibleLookupError(
                "Invalid result_format '%s'. Valid values: %s"
                % (result_format, ', '.join(valid)))

    def _validate_request_params(self, terms, csr, csr_file):
        """Validate parameters required for the request operation."""
        if not terms:
            raise AnsibleLookupError(
                "At least one service or host principal is required as "
                "a term when operation='request'. Example:\n"
                "  lookup('eigenstate.ipa.cert', "
                "'HTTP/web.example.com@EXAMPLE.COM', "
                "operation='request', csr=my_csr_var, ...)")
        if csr and csr_file:
            raise AnsibleLookupError(
                "'csr' and 'csr_file' are mutually exclusive. "
                "Provide the CSR as an inline string or as a file "
                "path, not both.")
        if not csr and not csr_file:
            raise AnsibleLookupError(
                "A CSR is required for operation='request'. "
                "Provide 'csr' (inline PEM string) or "
                "'csr_file' (path to a PEM file on the controller).")

    def _validate_retrieve_params(self, terms):
        """Validate parameters required for the retrieve operation."""
        if not terms:
            raise AnsibleLookupError(
                "At least one serial number is required as a term "
                "when operation='retrieve'. Example:\n"
                "  lookup('eigenstate.ipa.cert', '12345', "
                "operation='retrieve', ...)")

    def _validate_find_params(self, valid_not_after_from,
                               valid_not_after_to):
        """Validate date parameters for the find operation."""
        for name, val in (('valid_not_after_from', valid_not_after_from),
                          ('valid_not_after_to', valid_not_after_to)):
            if val is not None:
                try:
                    datetime.strptime(val, '%Y-%m-%d')
                except ValueError:
                    raise AnsibleLookupError(
                        "'%s' must be an ISO 8601 date (YYYY-MM-DD), "
                        "got: %s" % (name, val))

    def _validate_serial(self, serial):
        """Parse a serial number string or int and return an integer."""
        if isinstance(serial, int):
            return serial
        s = to_text(serial, errors='surrogate_or_strict').strip()
        try:
            if s.startswith('0x') or s.startswith('0X'):
                return int(s, 16)
            return int(s)
        except ValueError:
            raise AnsibleLookupError(
                "Invalid serial number '%s'. Expected a decimal "
                "integer or hex value prefixed with 0x." % serial)

    def _principal_find_filter(self, principal):
        """Map a principal filter to the supported cert_find owner filter."""
        text = to_text(principal, errors='surrogate_or_strict').strip()
        if text.startswith('host/'):
            hostname = text[5:].split('@', 1)[0]
            if not hostname:
                raise AnsibleLookupError(
                    "Invalid host principal for operation='find': %s"
                    % principal)
            return {'host': [hostname]}
        if '/' in text:
            return {'service': [text]}
        raise AnsibleLookupError(
            "Unsupported principal filter '%s' for operation='find'. "
            "Use a host principal like host/node.example.com@REALM or "
            "a service principal like HTTP/node.example.com@REALM."
            % principal)

    # ---------------------------------------------------------------
    # CSR and PEM helpers
    # ---------------------------------------------------------------

    def _read_csr_file(self, path):
        """Read a PEM CSR from a file on the controller."""
        if not os.path.isfile(path):
            raise AnsibleLookupError("CSR file not found: %s" % path)
        try:
            with open(path, 'r') as fh:
                return fh.read()
        except OSError as exc:
            raise AnsibleLookupError(
                "Failed to read CSR file '%s': %s"
                % (path, to_native(exc)))

    def _der_b64_to_pem(self, b64_der):
        """Convert a base64-encoded DER certificate to PEM (stdlib only).

        IPA returns the certificate as a base64 string without headers.
        This method re-wraps the data at 64 characters and adds the
        standard PEM begin/end markers.  No cryptography library is
        required.
        """
        clean = to_text(b64_der, errors='surrogate_or_strict'
                        ).strip().replace('\n', '').replace('\r', '')
        wrapped = textwrap.fill(clean, width=64)
        return (
            "-----BEGIN CERTIFICATE-----\n"
            "%s\n"
            "-----END CERTIFICATE-----\n" % wrapped
        )

    # ---------------------------------------------------------------
    # Result shaping
    # ---------------------------------------------------------------

    def _unwrap(self, value):
        """Unwrap IPA-style single-element lists."""
        if isinstance(value, (list, tuple)):
            if len(value) == 1:
                return value[0]
            if len(value) == 0:
                return None
        return value

    def _collect_san(self, ipa_result):
        """Collect all SAN extension values from an IPA cert result."""
        san = []
        for key in ('san_rfc822name', 'san_dnsname', 'san_x400address',
                    'san_directoryname', 'san_edipartyname', 'san_uri',
                    'san_ipaddress', 'san_oid', 'san_other'):
            entries = ipa_result.get(key)
            if not entries:
                continue
            if isinstance(entries, (list, tuple)):
                san.extend(
                    to_text(e, errors='surrogate_or_strict')
                    for e in entries)
            else:
                san.append(to_text(entries, errors='surrogate_or_strict'))
        return san

    def _build_record(self, name, ipa_result, encoding):
        """Build a canonical cert record from an IPA cert result dict."""
        b64_der = ipa_result.get('certificate', '')
        if encoding == 'pem':
            value = self._der_b64_to_pem(b64_der)
        else:
            value = to_text(
                b64_der, errors='surrogate_or_strict').strip()

        def _s(key):
            raw = self._unwrap(ipa_result.get(key, ''))
            return to_text(raw or '', errors='surrogate_or_strict')

        return {
            'name': name,
            'value': value,
            'encoding': encoding,
            'metadata': {
                'serial_number': ipa_result.get('serial_number'),
                'subject': _s('subject'),
                'issuer': _s('issuer'),
                'valid_not_before': _s('valid_not_before'),
                'valid_not_after': _s('valid_not_after'),
                'san': self._collect_san(ipa_result),
                'revoked': bool(ipa_result.get('revoked', False)),
                'revocation_reason': ipa_result.get('revocation_reason'),
            },
        }

    def _format_cert_result(self, record, result_format):
        """Shape a cert record to the requested result_format.

        Returns the bare certificate value for 'value' format, or the
        full record dict for 'record', 'map', and 'map_record' (the
        latter two are collapsed by _finalize_results).
        """
        if result_format == 'value':
            return record['value']
        return record

    def _finalize_results(self, results, result_format):
        """Apply the requested top-level result container shape."""
        if result_format == 'map':
            return [{
                item['name']: item.get('value', item)
                for item in results
            }]
        if result_format == 'map_record':
            return [{item['name']: item for item in results}]
        return results

    # ---------------------------------------------------------------
    # IPA API calls
    # ---------------------------------------------------------------

    def _request_cert(self, principal, csr_pem, profile, ca, add):
        """Submit a CSR to the IdM CA and return the signed cert dict."""
        request_args = {
            'principal': principal,
            'all': True,
        }
        if add:
            request_args['add'] = True
        if profile:
            request_args['profile_id'] = profile
        if ca:
            request_args['cacn'] = ca

        try:
            result = _ipa_api.Command.cert_request(
                csr_pem, **request_args)
        except ipalib_errors.NotFound as exc:
            raise AnsibleLookupError(
                "Principal '%s' not found in IdM: %s\n"
                "  Verify the principal exists, or set add=true to "
                "create it automatically."
                % (principal, to_native(exc)))
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Permission denied requesting a certificate for "
                "'%s': %s\n"
                "  The authenticating principal needs the "
                "'Request Certificate' IdM privilege."
                % (principal, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "cert_request failed for principal '%s': %s"
                % (principal, to_native(exc)))

        return result.get('result', {})

    def _retrieve_cert(self, serial):
        """Retrieve a certificate by serial number via ipalib."""
        try:
            result = _ipa_api.Command.cert_show(serial, all=True)
        except ipalib_errors.NotFound as exc:
            raise AnsibleLookupError(
                "Certificate with serial number %s not found: %s"
                % (serial, to_native(exc)))
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Permission denied retrieving serial %s: %s"
                % (serial, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "cert_show failed for serial %s: %s"
                % (serial, to_native(exc)))

        return result.get('result', {})

    def _find_certs(self, principal, subject, valid_not_after_from,
                    valid_not_after_to, revocation_reason, exactly):
        """Search the IdM CA for certificates matching the given criteria."""
        find_args = {
            'all': True,
            'sizelimit': 0,
        }
        if principal:
            find_args.update(self._principal_find_filter(principal))
        if subject:
            find_args['subject'] = subject
        if valid_not_after_from:
            find_args['validnotafter_from'] = datetime.strptime(
                valid_not_after_from, '%Y-%m-%d')
        if valid_not_after_to:
            find_args['validnotafter_to'] = datetime.strptime(
                valid_not_after_to, '%Y-%m-%d')
        if revocation_reason is not None:
            find_args['revocation_reason'] = revocation_reason
        if exactly:
            find_args['exactly'] = True

        try:
            result = _ipa_api.Command.cert_find(**find_args)
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Permission denied searching certificates: %s"
                % to_native(exc))
        except Exception as exc:
            raise AnsibleLookupError(
                "cert_find failed: %s" % to_native(exc))

        return result.get('result', [])

    # ---------------------------------------------------------------
    # Entry point
    # ---------------------------------------------------------------

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

            # request-specific params
            csr = self.get_option('csr')
            csr_file = self.get_option('csr_file')
            profile = self.get_option('profile')
            ca = self.get_option('ca')
            add = self.get_option('add')

            # find-specific params
            find_principal = self.get_option('principal')
            subject = self.get_option('subject')
            valid_not_after_from = self.get_option('valid_not_after_from')
            valid_not_after_to = self.get_option('valid_not_after_to')
            revocation_reason = self.get_option('revocation_reason')
            exactly = self.get_option('exactly')

            self._validate_operation(operation)
            self._validate_encoding(encoding)
            self._validate_result_format(result_format)

            if operation == 'request':
                self._validate_request_params(terms, csr, csr_file)
                if csr_file:
                    csr = self._read_csr_file(csr_file)
            elif operation == 'retrieve':
                self._validate_retrieve_params(terms)
            else:  # find
                self._validate_find_params(
                    valid_not_after_from, valid_not_after_to)

            self._connect(server, principal, password, keytab, verify)

            if operation == 'find':
                has_find_filter = any([
                    find_principal, subject, valid_not_after_from,
                    valid_not_after_to, revocation_reason is not None])
                if not has_find_filter:
                    display.warning(
                        "eigenstate.ipa.cert: operation=find called "
                        "without any filters. This returns all "
                        "certificates in IdM, which may be a very "
                        "large result set. Provide at least one of: "
                        "principal, subject, valid_not_after_from, "
                        "valid_not_after_to, revocation_reason.")

                ipa_entries = self._find_certs(
                    find_principal, subject, valid_not_after_from,
                    valid_not_after_to, revocation_reason, exactly)
                records = []
                for entry in ipa_entries:
                    serial = entry.get('serial_number', 'unknown')
                    record = self._build_record(
                        to_text(serial, errors='surrogate_or_strict'),
                        entry,
                        encoding)
                    records.append(
                        self._format_cert_result(record, result_format))
                return self._finalize_results(records, result_format)

            results = []
            for term in terms:
                term = to_text(term, errors='surrogate_or_strict')

                if operation == 'request':
                    ipa_result = self._request_cert(
                        term, csr, profile, ca, add)
                    record = self._build_record(term, ipa_result, encoding)
                else:  # retrieve
                    serial = self._validate_serial(term)
                    ipa_result = self._retrieve_cert(serial)
                    record = self._build_record(
                        to_text(serial, errors='surrogate_or_strict'),
                        ipa_result,
                        encoding)

                results.append(
                    self._format_cert_result(record, result_format))

            return self._finalize_results(results, result_format)

        finally:
            self._cleanup_ccache()

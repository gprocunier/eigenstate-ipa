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
name: dns
version_added: "1.8.0"
short_description: Query IdM integrated DNS records from FreeIPA/IdM
description:
  - Returns DNS record state from the integrated FreeIPA/IdM DNS service.
  - Supports read-only C(show) and C(find) operations for zone-scoped DNS
    records through the IdM C(dnsrecord_show) and C(dnsrecord_find) APIs.
  - Uses the C(ipalib) framework for all queries. Authentication follows
    the same keytab/password/existing-ticket pattern as other plugins in
    this collection.
  - Use this plugin when playbooks need to validate forward or reverse
    records, confirm zone-apex entries, or audit the DNS names and
    record data that the IdM DNS APIs expose directly.
options:
  _terms:
    description: >-
      One or more DNS record names to look up when C(operation=show).
      Names are relative to C(zone). Use C(@) for the zone apex record.
      Not required when C(operation=find).
    type: list
    elements: str
  operation:
    description: >-
      Which operation to perform. C(show) queries each named record and
      returns its state. C(find) searches all records in C(zone), optionally
      filtered by C(criteria) and C(record_type). Native IdM DNS search
      semantics apply, so treat this as an IdM-side search surface rather
      than a full zone transfer.
    type: str
    default: show
    choices: ["show", "find"]
  zone:
    description: >-
      DNS zone to query. This is required for both C(show) and C(find).
      Examples include C(workshop.lan) and C(0.16.172.in-addr.arpa).
    type: str
    required: true
  criteria:
    description: >-
      Optional search string for C(operation=find). When omitted, all
      records in C(zone) are returned.
    type: str
  record_type:
    description: >-
      Optional record-type filter for C(operation=find). When set, only
      records containing that concrete DNS RR type are returned. The
      filter applies to the record data returned by IdM, not to the
      record name.
    type: str
    choices: ["arecord", "aaaarecord", "cnamerecord", "mxrecord", "naptrrecord", "nsrecord", "ptrrecord", "srvrecord", "sshfprecord", "tlsarecord", "txtrecord", "urirecord"]
  server:
    description: FQDN or IP address of the IPA server.
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
      one per DNS entry. C(map_record) returns a single dictionary keyed by
      the record name.
    type: str
    default: record
    choices: ["record", "map_record"]
notes:
  - This plugin requires C(python3-ipalib) and C(python3-ipaclient) on
    the Ansible controller.
  - "RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)"
  - For records that do not exist, C(operation=show) returns a record with
    C(exists=false) rather than raising an error, allowing pre-flight
    conditionals without C(ignore_errors).
  - The plugin returns DNS RR data in the generic C(records) dictionary,
    keyed by record type (for example C(arecord), C(ptrrecord), or
    C(sshfprecord)). This keeps the surface stable across the wide IdM DNS
    schema.
  - Template-backed DNS attributes such as location-aware CNAME templates
    are returned in the C(template_records) dictionary.
  - Zone-apex metadata fields such as C(zone_active) and the SOA values are
    returned when the IdM DNS APIs expose them for the queried record.
seealso:
  - lookup: eigenstate.ipa.principal
  - lookup: eigenstate.ipa.cert
  - lookup: eigenstate.ipa.hbacrule
author:
  - Greg Procunier
"""

EXAMPLES = """
# Read one host record from a zone
- name: Load idm-01 DNS record
  ansible.builtin.set_fact:
    dns_record: "{{ lookup('eigenstate.ipa.dns',
                     'idm-01',
                     zone='workshop.lan',
                     server='idm-01.example.com',
                     kerberos_keytab='/etc/admin.keytab') }}"

# Read the zone apex record
- name: Inspect the zone apex entry
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.dns',
             '@',
             zone='workshop.lan',
             server='idm-01.example.com',
             kerberos_keytab='/etc/admin.keytab') }}"

# Find PTR records in a reverse zone
- name: List PTR records in 0.16.172.in-addr.arpa
  ansible.builtin.set_fact:
    ptr_records: "{{ lookup('eigenstate.ipa.dns',
                      operation='find',
                      zone='0.16.172.in-addr.arpa',
                      record_type='ptrrecord',
                      server='idm-01.example.com',
                      kerberos_keytab='/etc/admin.keytab') }}"

# Load several records into a keyed map
- name: Build a record map for core infrastructure names
  ansible.builtin.set_fact:
    dns_map: "{{ lookup('eigenstate.ipa.dns',
                  'idm-01', 'bastion-01', 'mirror-registry',
                  zone='workshop.lan',
                  result_format='map_record',
                  server='idm-01.example.com',
                  kerberos_keytab='/etc/admin.keytab') }}"
"""

RETURN = """
_raw:
  description: >-
    One record per DNS entry. When C(result_format=record) (default),
    returns a list of records; a single-term lookup is unwrapped by
    Ansible to a plain dict. When C(result_format=map_record), returns
    a dictionary keyed by record name.
  type: list
  elements: dict
  contains:
    name:
      description: The relative DNS record name inside C(zone).
      type: str
    zone:
      description: The queried DNS zone without a trailing dot.
      type: str
    fqdn:
      description: Fully qualified record name without a trailing dot.
      type: str
    exists:
      description: Whether the record exists in IdM.
      type: bool
    ttl:
      description: DNS TTL when present.
      type: int
    record_types:
      description: Concrete RR types present in C(records).
      type: list
      elements: str
    records:
      description: DNS RR data keyed by RR type.
      type: dict
    template_record_types:
      description: Template RR types present in C(template_records).
      type: list
      elements: str
    template_records:
      description: Template-backed DNS RR data keyed by RR type.
      type: dict
    is_zone_apex:
      description: Whether the record is the zone apex entry.
      type: bool
    zone_active:
      description: Present when the IdM DNS APIs expose zone-apex active state.
      type: bool
    allow_dyn_update:
      description: Present when the IdM DNS APIs expose zone-apex dynamic-update policy.
      type: bool
    allow_query:
      description: Present when the IdM DNS APIs expose zone-apex query ACL state.
      type: str
    allow_transfer:
      description: Present when the IdM DNS APIs expose zone-apex transfer ACL state.
      type: str
    soa_mname:
      description: Present when the IdM DNS APIs expose zone-apex SOA primary nameserver data.
      type: str
    soa_rname:
      description: Present when the IdM DNS APIs expose zone-apex SOA responsible mailbox data.
      type: str
    soa_serial:
      description: Present when the IdM DNS APIs expose zone-apex SOA serial data.
      type: int
    update_policy:
      description: Present when the IdM DNS APIs expose zone-apex update policy data.
      type: str
    object_classes:
      description: LDAP object classes returned by IdM for the record.
      type: list
      elements: str
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

_RECORD_ATTRS = (
    'arecord', 'aaaarecord', 'cnamerecord', 'mxrecord', 'naptrrecord',
    'nsrecord', 'ptrrecord', 'srvrecord', 'sshfprecord', 'tlsarecord',
    'txtrecord', 'urirecord'
)


class LookupModule(LookupBase):
    """Query IdM integrated DNS records from FreeIPA/IdM."""

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

    def _normalize_text(self, value):
        if value is None:
            return None
        return to_text(value, errors='surrogate_or_strict')

    def _unwrap(self, value, fallback=None):
        if isinstance(value, (list, tuple)):
            if not value:
                return fallback
            return self._unwrap(value[0], fallback=fallback)
        if value is None:
            return fallback
        return value

    def _normalize_zone(self, zone):
        zone = self._normalize_text(zone or '')
        zone = zone.rstrip('.')
        if not zone:
            raise AnsibleLookupError("'zone' is required.")
        return zone

    def _normalize_record_name(self, name):
        name = self._normalize_text(name or '')
        if not name:
            raise AnsibleLookupError("DNS record name must not be empty.")
        return name.rstrip('.') if name != '@' else '@'

    def _record_fqdn(self, zone, name):
        if name == '@':
            return zone
        return '%s.%s' % (name, zone)

    def _bool_attr(self, entry, key):
        value = self._normalize_text(self._unwrap(self._entry_value(entry, key)))
        if value is None:
            return None
        return value.upper() == 'TRUE'

    def _int_attr(self, entry, key):
        value = self._unwrap(self._entry_value(entry, key))
        if value is None:
            return None
        try:
            return int(to_text(value, errors='surrogate_or_strict'))
        except (TypeError, ValueError):
            return None

    def _entry_value(self, entry, key):
        key = key.lower()
        for entry_key, value in entry.items():
            norm_key = self._normalize_text(entry_key)
            if norm_key and norm_key.lower() == key:
                return value
        return None

    def _text_attr(self, entry, key):
        return self._normalize_text(self._unwrap(self._entry_value(entry, key)))

    def _list_attr(self, entry, key):
        value = self._entry_value(entry, key)
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            value = [value]
        return [self._normalize_text(item) for item in value]

    def _record_maps(self, entry):
        records = {}
        template_records = {}
        for entry_key in entry.keys():
            norm_key = self._normalize_text(entry_key)
            if not norm_key:
                continue
            lowered = norm_key.lower()
            values = self._list_attr(entry, entry_key)
            if lowered in _RECORD_ATTRS:
                records[lowered] = values
            elif lowered.startswith('idnstemplateattribute;'):
                record_key = lowered.split(';', 1)[1]
                if record_key in _RECORD_ATTRS:
                    template_records[record_key] = values
        return records, template_records

    def _matches_record_type(self, record, record_type):
        if not record_type:
            return True
        return record_type in record['record_types']

    def _record_record(self, zone, name, entry, exists=True):
        zone = self._normalize_zone(zone)
        name = self._normalize_record_name(name)
        records, template_records = self._record_maps(entry)
        return {
            'name': name,
            'zone': zone,
            'fqdn': self._record_fqdn(zone, name),
            'exists': exists,
            'ttl': self._int_attr(entry, 'dnsttl'),
            'record_types': sorted(records.keys()),
            'records': records,
            'template_record_types': sorted(template_records.keys()),
            'template_records': template_records,
            'is_zone_apex': name == '@',
            'zone_active': self._bool_attr(entry, 'idnszoneactive'),
            'allow_dyn_update': self._bool_attr(entry, 'idnsallowdynupdate'),
            'allow_query': self._text_attr(entry, 'idnsallowquery'),
            'allow_transfer': self._text_attr(entry, 'idnsallowtransfer'),
            'soa_mname': self._text_attr(entry, 'idnssoamname'),
            'soa_rname': self._text_attr(entry, 'idnssoarname'),
            'soa_serial': self._int_attr(entry, 'idnssoaserial'),
            'soa_refresh': self._int_attr(entry, 'idnssoarefresh'),
            'soa_retry': self._int_attr(entry, 'idnssoaretry'),
            'soa_expire': self._int_attr(entry, 'idnssoaexpire'),
            'soa_minimum': self._int_attr(entry, 'idnssoaminimum'),
            'update_policy': self._text_attr(entry, 'idnsupdatepolicy'),
            'object_classes': self._list_attr(entry, 'objectclass'),
        }

    def _merge_entries(self, *entries):
        merged = {}
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            merged.update(entry)
        return merged

    def _zone_entry(self, zone):
        try:
            result = _ipa_api.Command.dnszone_show(zone, all=True, raw=True)
            return result.get('result', {})
        except ipalib_errors.NotFound:
            return {}
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to query DNS zone '%s': %s"
                % (zone, to_native(exc)))

    def _show_record(self, zone, name):
        try:
            result = _ipa_api.Command.dnsrecord_show(zone, name, all=True, raw=True)
            entry = result.get('result', {})
            if name == '@':
                entry = self._merge_entries(entry, self._zone_entry(zone))
            return self._record_record(zone, name, entry, exists=True)
        except ipalib_errors.NotFound:
            return self._record_record(zone, name, {}, exists=False)
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to query DNS record '%s' in zone '%s': %s"
                % (name, zone, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to query DNS record '%s' in zone '%s': %s"
                % (name, zone, to_native(exc)))

    def _find_records(self, zone, criteria, record_type):
        search_arg = criteria or ''
        records = []
        try:
            result = _ipa_api.Command.dnsrecord_find(zone, search_arg, sizelimit=0, all=True, raw=True)
            for entry in result.get('result', []):
                name = self._normalize_text(self._unwrap(entry.get('idnsname'), fallback=''))
                if not name:
                    continue
                if name == '@':
                    entry = self._merge_entries(entry, self._zone_entry(zone))
                record = self._record_record(zone, name, entry)
                if self._matches_record_type(record, record_type):
                    records.append(record)
        except ipalib_errors.AuthorizationError as exc:
            raise AnsibleLookupError(
                "Not authorized to search DNS records in zone '%s': %s"
                % (zone, to_native(exc)))
        except Exception as exc:
            raise AnsibleLookupError(
                "Failed to search DNS records in zone '%s': %s"
                % (zone, to_native(exc)))
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

            zone = self._normalize_zone(self.get_option('zone'))
            principal = self.get_option('ipaadmin_principal')
            password = self.get_option('ipaadmin_password')
            keytab = self.get_option('kerberos_keytab')
            verify = self._resolve_verify(self.get_option('verify'))
            criteria = self.get_option('criteria')
            record_type = self.get_option('record_type')
            result_format = self.get_option('result_format')

            if operation == 'show':
                if not terms:
                    raise AnsibleLookupError(
                        "operation=show requires at least one DNS record name in _terms.")
            elif operation != 'find':
                raise AnsibleLookupError(
                    "Unknown operation '%s'. Use: show, find." % operation)

            self._connect(server, principal, password, keytab, verify)

            if operation == 'find':
                return self._finalize_results(
                    self._find_records(zone, criteria, record_type), result_format)

            results = []
            for term in terms:
                term = self._normalize_record_name(term)
                results.append(self._show_record(zone, term))
            return self._finalize_results(results, result_format)
        finally:
            self._cleanup_ccache()

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

ANSIBLE_METADATA = {
    "metadata_version": "1.0",
    "supported_by": "community",
    "status": ["preview"],
}

DOCUMENTATION = """
---
name: idm
version_added: "1.0.0"
short_description: Build dynamic inventory from Red Hat IDM/FreeIPA
description:
  - Creates Ansible inventory from Red Hat Identity Management
    (IDM/FreeIPA) hosts, hostgroups, netgroups, and HBAC rules.
  - IDM hostgroups, netgroups, and HBAC rules are mapped to Ansible
    groups with configurable prefixes.
  - A curated set of host attributes from IDM is exposed as host
    variables with a C(idm_) prefix.
  - Nested hostgroups are fully resolved when building group membership.
  - HBAC rules with C(hostcategory=all) automatically include all
    enrolled hosts.
  - Supports standard Ansible inventory plugin features including
    compose, keyed_groups, groups, and caching.
options:
  plugin:
    description: Marks this as an instance of the C(idm) plugin.
    required: true
    choices: ["eigenstate.ipa.idm", "idm"]
  ipaadmin_principal:
    description: The admin principal.
    default: admin
    type: str
  ipaadmin_password:
    description: >-
      The admin password. Required when not using Kerberos authentication.
    type: str
    required: false
    secret: true
    env:
      - name: IPA_ADMIN_PASSWORD
  server:
    description: FQDN of the IPA server to query.
    type: str
    required: true
    env:
      - name: IPA_SERVER
  verify:
    description: >-
      Path to the server TLS certificate file for verification
      (e.g. /etc/ipa/ca.crt). If not set, the plugin auto-detects
      C(/etc/ipa/ca.crt) when present and only falls back to disabled
      verification with a warning when no IdM CA path is available.
    type: str
    required: false
    env:
      - name: IPA_CERT
  sources:
    description: >-
      List of IDM object types to include in the inventory. C(hosts)
      adds all enrolled hosts. C(hostgroups), C(netgroups), and
      C(hbacrules) create Ansible groups from the corresponding IDM
      objects and populate them with their member hosts.
    type: list
    elements: str
    default:
      - hosts
      - hostgroups
      - netgroups
      - hbacrules
  hostgroup_filter:
    description: >-
      Limit hostgroup-based groups to this list of hostgroup names.
      An empty list means all hostgroups are included.
    type: list
    elements: str
    default: []
  netgroup_filter:
    description: >-
      Limit netgroup-based groups to this list of netgroup names.
      An empty list means all netgroups are included.
    type: list
    elements: str
    default: []
  hbacrule_filter:
    description: >-
      Limit HBAC-rule-based groups to this list of rule names.
      An empty list means all HBAC rules are included.
    type: list
    elements: str
    default: []
  include_disabled_hbacrules:
    description: Whether to include disabled HBAC rules.
    type: bool
    default: false
  hostgroup_prefix:
    description: >-
      Prefix applied to Ansible group names created from IDM hostgroups.
    type: str
    default: "idm_hostgroup_"
  netgroup_prefix:
    description: >-
      Prefix applied to Ansible group names created from IDM netgroups.
    type: str
    default: "idm_netgroup_"
  hbacrule_prefix:
    description: >-
      Prefix applied to Ansible group names created from IDM HBAC rules.
    type: str
    default: "idm_hbacrule_"
  host_filter_from_groups:
    description: >-
      When set to C(true), hosts that do not belong to any group
      created by the configured sources and filters are removed from
      the inventory.  This prevents unrelated hosts from appearing
      under C(ungrouped).  When C(false) (the default), all enrolled
      IDM hosts are kept regardless of group membership.
    type: bool
    default: false
  hostvars_enabled:
    description: >-
      Export curated IDM host attributes as C(idm_*) host variables.
      Disable this when you only want host attribute export. Group
      variables derived from hostgroups, netgroups, or HBAC rules may
      still merge into hostvars during inventory processing.
    type: bool
    default: true
  hostvars_include:
    description: >-
      Restrict exported host-attribute IDM variables to this
      allowlist of C(idm_*) names. An empty list keeps the default
      curated set. Group variables derived from generated inventory
      groups are not filtered by this setting. Unknown variable names
      are rejected so inventory config fails fast instead of silently
      dropping requested metadata.
    type: list
    elements: str
    default: []
  use_kerberos:
    description: >-
      Use Kerberos (GSSAPI) authentication instead of password
      authentication. Requires either a valid Kerberos ticket
      (obtained via C(kinit)) or a keytab file (see
      C(kerberos_keytab)). The following packages must be
      installed on the controller: C(krb5-workstation) (provides
      kinit), and one of C(python3-requests-gssapi) or
      C(python3-requests-kerberos) (provides the GSSAPI transport
      for requests). On RHEL/Fedora install with
      C(dnf install python3-requests-gssapi krb5-workstation).
    type: bool
    default: false
  kerberos_keytab:
    description: >-
      Path to a Kerberos keytab file. When set together with
      C(use_kerberos), the plugin automatically runs C(kinit) with
      the keytab to obtain a ticket before authenticating to the
      IPA server. This eliminates the need for an interactive
      C(kinit) and is required for use inside AAP Execution
      Environments. The principal used with the keytab is taken
      from C(ipaadmin_principal) (default C(admin)).
    type: str
    required: false
    env:
      - name: IPA_KEYTAB
extends_documentation_fragment:
  - constructed
  - inventory_cache
author:
  - Greg Procunier
"""

EXAMPLES = """
# Minimal - all sources, password auth via environment
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"

# With explicit TLS verification
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
verify: /etc/ipa/ca.crt

# Only hostgroups and HBAC rules, filtered
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
sources:
  - hosts
  - hostgroups
  - hbacrules
hostgroup_filter:
  - webservers
  - databases
hbacrule_filter:
  - allow_ssh_admins

# Kerberos authentication with compose and keyed_groups
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
use_kerberos: true
compose:
  ansible_host: idm_fqdn
keyed_groups:
  - key: idm_location
    prefix: location
    separator: "_"
  - key: idm_os
    prefix: os
    separator: "_"
groups:
  has_keytab: idm_has_keytab | default(false)

# Kerberos with keytab (for AAP Execution Environments)
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
use_kerberos: true
kerberos_keytab: /path/to/admin.keytab
ipaadmin_principal: admin
verify: /etc/ipa/ca.crt

# Only keep hosts that belong to a filtered group
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
sources:
  - hosts
  - hostgroups
hostgroup_filter:
  - webservers
host_filter_from_groups: true

# Keep only selected host variables
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
hostvars_include:
  - idm_location
  - idm_os
  - idm_hostgroups

# With caching enabled (useful for large IDM deployments)
---
plugin: eigenstate.ipa.idm
server: idm-01.example.com
ipaadmin_password: "{{ lookup('env', 'IPA_ADMIN_PASSWORD') }}"
cache: true
cache_plugin: jsonfile
cache_timeout: 3600
cache_connection: ~/.ansible/cache/idm_inventory
"""

import os
import re
import stat
import subprocess
import tempfile

try:
    import requests
except ImportError:
    requests = None

try:
    import urllib3
except ImportError:
    urllib3 = None

try:
    from requests_gssapi import HTTPSPNEGOAuth
    HAS_GSSAPI = True
    _GSSAPI_PKG = 'requests-gssapi'
except ImportError:
    try:
        from requests_kerberos import HTTPKerberosAuth as HTTPSPNEGOAuth
        HAS_GSSAPI = True
        _GSSAPI_PKG = 'requests-kerberos'
    except ImportError:
        HAS_GSSAPI = False
        _GSSAPI_PKG = None

try:
    import gssapi as _gssapi_lib  # noqa: F401
    HAS_GSSAPI_LIB = True
except ImportError:
    HAS_GSSAPI_LIB = False

from ansible import constants
from ansible.errors import AnsibleParserError
from ansible.module_utils.common.text.converters import to_native
from ansible.plugins.inventory import (
    BaseInventoryPlugin, Constructable, Cacheable,
)
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible.utils.display import Display


display = Display()


def _sanitize_group_name(name):
    """Sanitize a string for use as an Ansible group name."""
    return re.sub(r'[^A-Za-z0-9_]', '_', name)


def _unwrap(value):
    """Unwrap single-element IPA attribute lists to scalar values."""
    if isinstance(value, (list, tuple)):
        if len(value) == 1:
            return value[0]
        if len(value) == 0:
            return None
    return value


# IPA attribute -> host variable mapping.
# Keys marked True are kept as lists; False are unwrapped to scalars.
_IPA_HOST_ATTRS = {
    'fqdn':                    ('idm_fqdn', False),
    'description':             ('idm_description', False),
    'l':                       ('idm_locality', False),
    'nshostlocation':          ('idm_location', False),
    'nshardwareplatform':      ('idm_platform', False),
    'nsosversion':             ('idm_os', False),
    'krbcanonicalname':        ('idm_krbcanonicalname', False),
    'has_keytab':              ('idm_has_keytab', False),
    'has_password':            ('idm_has_password', False),
    'serverhostname':          ('idm_serverhostname', False),
    'dn':                      ('idm_dn', False),
    'ipakrbokasdelegate':      ('idm_krb_ok_as_delegate', False),
    'ipakrbrequirespreauth':   ('idm_krb_requires_preauth', False),
    'ipasshpubkey':            ('idm_ssh_public_keys', True),
    'krbprincipalname':        ('idm_krbprincipalname', True),
    'managedby_host':          ('idm_managedby', True),
    'memberof_hostgroup':      ('idm_hostgroups', True),
}

_HOSTVAR_NAMES = {
    var_name for var_name, _keep_list in _IPA_HOST_ATTRS.values()
}


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    """Dynamic inventory from Red Hat IDM / FreeIPA."""

    NAME = 'idm'

    def __init__(self):
        super(InventoryModule, self).__init__()
        self._session = None
        self._ipa_url = None
        self._verify = False
        self._hostgroup_members = {}
        self._selected_host_attrs_cache = None
        self._ccache_path = None
        self._previous_ccache = None
        self._managing_ccache = False

    # ------------------------------------------------------------------
    # File detection
    # ------------------------------------------------------------------

    def verify_file(self, path):
        # pylint: disable=super-with-arguments
        if super(InventoryModule, self).verify_file(path):
            _name, ext = os.path.splitext(path)
            if ext in constants.YAML_FILENAME_EXTENSIONS:
                return True
        return False

    # ------------------------------------------------------------------
    # Kerberos keytab helper
    # ------------------------------------------------------------------

    def _kinit_from_keytab(self, keytab, principal):
        """Obtain a Kerberos ticket from a keytab file.

        Creates a private credential cache so the plugin does not
        interfere with any existing tickets on the controller.
        """
        if not os.path.isfile(keytab):
            raise AnsibleParserError(
                "Kerberos keytab file not found: %s" % keytab)

        self._warn_if_sensitive_file_permissive(keytab, "kerberos_keytab")

        # Private ccache avoids polluting the user/system default.
        ccache_fd, ccache_path = tempfile.mkstemp(
            prefix='krb5cc_idm_inv_')
        os.close(ccache_fd)
        self._ccache_path = ccache_path
        ccache_env = 'FILE:%s' % ccache_path

        env = os.environ.copy()
        env['KRB5CCNAME'] = ccache_env

        try:
            result = subprocess.run(          # pylint: disable=W1510
                ['kinit', '-kt', keytab, principal],
                capture_output=True, text=True, timeout=30,
                env=env)
        except FileNotFoundError:
            os.remove(ccache_path)
            raise AnsibleParserError(
                "'kinit' command not found. Install "
                "krb5-workstation:\n"
                "  RHEL/Fedora: dnf install krb5-workstation")
        except subprocess.TimeoutExpired:
            os.remove(ccache_path)
            raise AnsibleParserError(
                "'kinit' timed out after 30 s. Check network "
                "connectivity to the KDC and verify that "
                "/etc/krb5.conf is correct.")

        if result.returncode != 0:
            stderr = result.stderr.strip()
            os.remove(ccache_path)
            raise AnsibleParserError(
                "kinit with keytab failed (exit %d): %s\n"
                "  keytab:    %s\n"
                "  principal: %s\n"
                "Verify the keytab contains the principal:\n"
                "  klist -kt %s"
                % (result.returncode, stderr,
                   keytab, principal, keytab))

        # Point the current process at the new ccache so that
        # requests-gssapi / requests-kerberos picks it up.
        self._activate_ccache(ccache_path, ccache_env)

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

    def _warn_if_sensitive_file_permissive(self, path, option_name):
        """Warn when sensitive local files are readable by non-owners."""
        mode = stat.S_IMODE(os.stat(path).st_mode)
        if mode & 0o077:
            display.warning(
                "%s '%s' has permissions %s which are more permissive "
                "than 0600." % (option_name, path, oct(mode))
            )

    def _default_verify_path(self):
        """Return the conventional IPA CA path when it exists locally."""
        default_path = '/etc/ipa/ca.crt'
        if os.path.exists(default_path):
            return default_path
        return None

    def _resolve_verify(self, verify):
        """Resolve TLS verification behavior for inventory requests."""
        if verify is not None:
            if not os.path.exists(verify):
                raise AnsibleParserError(
                    "TLS certificate file not found: %s" % verify)
            return verify

        default_verify = self._default_verify_path()
        if default_verify is not None:
            return default_verify

        display.warning(
            "TLS verification is disabled for eigenstate.ipa.idm. "
            "Set 'verify' to the IPA CA certificate path for production use."
        )
        if urllib3 is not None:
            urllib3.disable_warnings(
                urllib3.exceptions.InsecureRequestWarning)
        return False

    # ------------------------------------------------------------------
    # IPA session helpers
    # ------------------------------------------------------------------

    def _authenticate(self):
        """Establish an authenticated session with the IPA server."""
        server = self.get_option('server')
        verify = self.get_option('verify')
        use_kerberos = self.get_option('use_kerberos')

        self._verify = self._resolve_verify(verify)

        self._ipa_url = "https://%s/ipa" % server
        self._session = requests.Session()
        self._session.headers.update({"referer": self._ipa_url})

        if use_kerberos:
            if not HAS_GSSAPI:
                raise AnsibleParserError(
                    "Kerberos authentication requires a GSSAPI "
                    "requests adapter but none was found.\n"
                    "Install one of the following:\n"
                    "  RHEL/Fedora: dnf install "
                    "python3-requests-gssapi krb5-workstation\n"
                    "  pip:         pip install requests-gssapi\n"
                    "The 'krb5-workstation' package provides kinit "
                    "and is required to obtain a Kerberos ticket.")
            if not HAS_GSSAPI_LIB:
                raise AnsibleParserError(
                    "The '%s' Python package is installed but the "
                    "underlying 'gssapi' library is missing or "
                    "cannot be loaded.\n"
                    "Install the system GSSAPI development headers "
                    "and the Python binding:\n"
                    "  RHEL/Fedora: dnf install "
                    "krb5-devel python3-gssapi\n"
                    "  pip:         pip install gssapi"
                    % _GSSAPI_PKG)

            # Obtain a ticket from a keytab if one was provided
            # (required for AAP / EE where interactive kinit is not
            # possible).
            keytab = self.get_option('kerberos_keytab')
            if keytab:
                self._kinit_from_keytab(
                    keytab, self.get_option('ipaadmin_principal'))

            self._session.auth = HTTPSPNEGOAuth(
                mutual_authentication='OPTIONAL')
            try:
                response = self._session.post(
                    "%s/session/login_kerberos" % self._ipa_url,
                    verify=self._verify)
            except Exception as exc:
                exc_str = to_native(exc)
                if 'Credentials cache' in exc_str \
                        or 'No Kerberos credentials' in exc_str \
                        or 'GSSAPI' in exc_str:
                    hint = (
                        "Obtain a ticket first:\n"
                        "  kinit %s\n"
                        "Or provide a keytab for non-interactive "
                        "use (AAP):\n"
                        "  kerberos_keytab: /path/to/admin.keytab"
                        % self.get_option('ipaadmin_principal'))
                    raise AnsibleParserError(
                        "Kerberos credential error: %s\n%s"
                        % (exc_str, hint))
                raise AnsibleParserError(
                    "Kerberos login request to %s failed: %s"
                    % (server, exc_str))
            if response.status_code != 200:
                principal = self.get_option('ipaadmin_principal')
                raise AnsibleParserError(
                    "Kerberos authentication failed (HTTP %d). "
                    "Possible causes:\n"
                    "  - No valid ticket: run 'kinit %s'\n"
                    "  - Ticket expired: run 'kinit %s' to renew\n"
                    "  - Clock skew between controller and IPA "
                    "server (check with 'date' on both hosts)\n"
                    "  - Wrong server FQDN (must match the IPA "
                    "Kerberos realm)\n"
                    "For non-interactive environments (AAP), set "
                    "kerberos_keytab."
                    % (response.status_code, principal, principal))
        else:
            ipaadmin_principal = self.get_option('ipaadmin_principal')
            ipaadmin_password = self.get_option('ipaadmin_password')
            if not ipaadmin_password:
                raise AnsibleParserError(
                    "'ipaadmin_password' is required when not using "
                    "Kerberos authentication.")

            self._session.headers.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/plain",
            })
            data = 'user=%s&password=%s' % (
                quote(ipaadmin_principal, safe=''),
                quote(ipaadmin_password, safe=''))
            response = self._session.post(
                "%s/session/login_password" % self._ipa_url,
                data=data, verify=self._verify)
            if response.status_code != 200:
                raise AnsibleParserError(
                    "IPA password authentication failed (HTTP %d). "
                    "Check credentials and server FQDN."
                    % response.status_code)

        # All subsequent calls use the JSON API.
        self._session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _api_call(self, method, args=None, params=None):
        """Execute a single IPA JSON-RPC call and return the result."""
        if args is None:
            args = [""]
        if params is None:
            params = {}

        json_payload = {
            "method": method,
            "params": [args, params],
            "id": 0,
        }

        try:
            response = self._session.post(
                "%s/session/json" % self._ipa_url,
                json=json_payload, verify=self._verify)
        except requests.exceptions.RequestException as exc:
            raise AnsibleParserError(
                "IPA API request failed for '%s': %s"
                % (method, to_native(exc)))

        if response.status_code != 200:
            raise AnsibleParserError(
                "IPA API call '%s' returned HTTP %d: %s"
                % (method, response.status_code, response.text[:500]))

        try:
            json_res = response.json()
        except ValueError:
            raise AnsibleParserError(
                "IPA API call '%s' returned non-JSON response."
                % method)

        error = json_res.get("error")
        if error is not None:
            raise AnsibleParserError(
                "IPA API error in '%s': %s" % (method, to_native(error)))

        return json_res.get("result", {})

    # ------------------------------------------------------------------
    # Data fetching
    # ------------------------------------------------------------------

    def _fetch_hosts(self):
        result = self._api_call("host_find", [""], {
            "all": True, "sizelimit": 0,
        })
        return result.get("result", [])

    def _fetch_hostgroups(self):
        result = self._api_call("hostgroup_find", [""], {
            "all": True, "sizelimit": 0,
        })
        return result.get("result", [])

    def _fetch_netgroups(self):
        result = self._api_call("netgroup_find", [""], {
            "all": True, "sizelimit": 0,
        })
        return result.get("result", [])

    def _fetch_hbacrules(self):
        result = self._api_call("hbacrule_find", [""], {
            "all": True, "sizelimit": 0,
        })
        return result.get("result", [])

    # ------------------------------------------------------------------
    # Inventory population
    # ------------------------------------------------------------------

    def _selected_host_attrs(self):
        """Return the configured subset of host attributes to export."""
        if self._selected_host_attrs_cache is not None:
            return self._selected_host_attrs_cache

        if not self.get_option('hostvars_enabled'):
            self._selected_host_attrs_cache = {}
            return self._selected_host_attrs_cache

        include = self.get_option('hostvars_include') or []
        if not include:
            self._selected_host_attrs_cache = _IPA_HOST_ATTRS
            return self._selected_host_attrs_cache

        unknown = sorted(set(include) - _HOSTVAR_NAMES)
        if unknown:
            raise AnsibleParserError(
                "Unsupported hostvars_include value(s): %s. Valid names: %s"
                % (
                    ', '.join(unknown),
                    ', '.join(sorted(_HOSTVAR_NAMES)),
                )
            )

        allowed = set(include)
        self._selected_host_attrs_cache = {
            ipa_attr: (var_name, keep_list)
            for ipa_attr, (var_name, keep_list) in _IPA_HOST_ATTRS.items()
            if var_name in allowed
        }
        return self._selected_host_attrs_cache

    def _add_host(self, fqdn, host_data):
        """Add a single host to the Ansible inventory."""
        self.inventory.add_host(fqdn)

        for ipa_attr, (var_name, keep_list) in self._selected_host_attrs().items():
            if ipa_attr in host_data:
                value = host_data[ipa_attr]
                if keep_list:
                    self.inventory.set_variable(fqdn, var_name, value)
                else:
                    self.inventory.set_variable(fqdn, var_name,
                                                _unwrap(value))

    def _build_hostgroup_map(self, hostgroups):
        """Build a map of hostgroup name -> resolved host FQDNs.

        Nested hostgroups are resolved recursively.  The map is cached
        in ``self._hostgroup_members`` so that netgroup and HBAC rule
        processing can reuse it without additional API calls.
        """
        raw = {}
        for hg in hostgroups:
            name = _unwrap(hg.get('cn', []))
            if name is not None:
                raw[name] = {
                    'hosts': set(hg.get('member_host', [])),
                    'nested': list(hg.get('member_hostgroup', [])),
                    'data': hg,
                }

        def _resolve(name, visited=None):
            if name in self._hostgroup_members:
                return self._hostgroup_members[name]
            if visited is None:
                visited = set()
            if name in visited or name not in raw:
                return set()
            visited.add(name)
            hosts = set(raw[name]['hosts'])
            for nested in raw[name]['nested']:
                hosts.update(_resolve(nested, visited))
            self._hostgroup_members[name] = hosts
            return hosts

        for name in raw:
            _resolve(name)

        return raw

    def _build_hostgroups(self, raw_map):
        """Create Ansible groups from IDM hostgroups."""
        prefix = self.get_option('hostgroup_prefix')
        hg_filter = self.get_option('hostgroup_filter')

        for hg_name, info in raw_map.items():
            if hg_filter and hg_name not in hg_filter:
                continue

            group_name = _sanitize_group_name(prefix + hg_name)
            self.inventory.add_group(group_name)

            desc = _unwrap(info['data'].get('description', []))
            if desc:
                self.inventory.set_variable(
                    group_name, 'idm_hostgroup_description', desc)

            for host_fqdn in self._hostgroup_members.get(hg_name, set()):
                if host_fqdn in self.inventory.hosts:
                    self.inventory.add_host(host_fqdn, group=group_name)

    def _build_netgroups(self, netgroups):
        """Create Ansible groups from IDM netgroups."""
        prefix = self.get_option('netgroup_prefix')
        ng_filter = self.get_option('netgroup_filter')

        for ng in netgroups:
            ng_name = _unwrap(ng.get('cn', []))
            if ng_name is None:
                continue
            if ng_filter and ng_name not in ng_filter:
                continue

            group_name = _sanitize_group_name(prefix + ng_name)
            self.inventory.add_group(group_name)

            desc = _unwrap(ng.get('description', []))
            if desc:
                self.inventory.set_variable(
                    group_name, 'idm_netgroup_description', desc)

            # Direct host members
            for host_fqdn in ng.get('memberhost_host', []):
                if host_fqdn in self.inventory.hosts:
                    self.inventory.add_host(host_fqdn, group=group_name)

            # Hosts via hostgroup membership
            for hg_name in ng.get('memberhost_hostgroup', []):
                for host_fqdn in self._hostgroup_members.get(hg_name,
                                                              set()):
                    if host_fqdn in self.inventory.hosts:
                        self.inventory.add_host(host_fqdn,
                                                group=group_name)

    def _build_hbacrules(self, hbacrules):
        """Create Ansible groups from IDM HBAC rules."""
        prefix = self.get_option('hbacrule_prefix')
        hbac_filter = self.get_option('hbacrule_filter')
        include_disabled = self.get_option('include_disabled_hbacrules')

        for rule in hbacrules:
            rule_name = _unwrap(rule.get('cn', []))
            if rule_name is None:
                continue
            if hbac_filter and rule_name not in hbac_filter:
                continue

            enabled_flag = _unwrap(rule.get('ipaenabledflag', ['TRUE']))
            is_enabled = str(enabled_flag).upper() == 'TRUE'
            if not include_disabled and not is_enabled:
                continue

            group_name = _sanitize_group_name(prefix + rule_name)
            self.inventory.add_group(group_name)

            desc = _unwrap(rule.get('description', []))
            if desc:
                self.inventory.set_variable(
                    group_name, 'idm_hbacrule_description', desc)
            self.inventory.set_variable(
                group_name, 'idm_hbacrule_enabled', is_enabled)

            # hostcategory=all means every enrolled host matches
            hostcat = _unwrap(rule.get('hostcategory', []))
            if hostcat == 'all':
                for host_fqdn in list(self.inventory.hosts):
                    self.inventory.add_host(host_fqdn, group=group_name)
                continue

            # Direct host members
            for host_fqdn in rule.get('memberhost_host', []):
                if host_fqdn in self.inventory.hosts:
                    self.inventory.add_host(host_fqdn, group=group_name)

            # Hosts via hostgroup membership
            for hg_name in rule.get('memberhost_hostgroup', []):
                for host_fqdn in self._hostgroup_members.get(hg_name,
                                                              set()):
                    if host_fqdn in self.inventory.hosts:
                        self.inventory.add_host(host_fqdn,
                                                group=group_name)

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def _fetch_all(self):
        """Fetch all required data from IDM.  Returns a cache-safe dict."""
        self._authenticate()
        sources = self.get_option('sources')
        data = {}

        # Hosts are always needed as the base inventory.
        data['hosts'] = self._fetch_hosts()

        # Hostgroup data is needed whenever hostgroups, netgroups, or
        # HBAC rules are requested (netgroups/HBAC may reference
        # hostgroups for membership resolution).
        if any(s in sources for s in ('hostgroups', 'netgroups',
                                       'hbacrules')):
            data['hostgroups'] = self._fetch_hostgroups()

        if 'netgroups' in sources:
            data['netgroups'] = self._fetch_netgroups()

        if 'hbacrules' in sources:
            data['hbacrules'] = self._fetch_hbacrules()

        return data

    def _populate(self, data):
        """Populate inventory objects from the fetched data."""
        sources = self.get_option('sources')
        strict = self.get_option('strict')

        # 1. Add all hosts first.
        for host_data in data.get('hosts', []):
            fqdn = _unwrap(host_data.get('fqdn', []))
            if fqdn:
                self._add_host(fqdn, host_data)

        # 2. Build the hostgroup resolution map (needed before
        #    netgroup/HBAC processing even if hostgroup groups are not
        #    requested).
        raw_hg_map = {}
        if 'hostgroups' in data:
            raw_hg_map = self._build_hostgroup_map(data['hostgroups'])

        # 3. Create Ansible groups from the requested sources.
        if 'hostgroups' in sources and raw_hg_map:
            self._build_hostgroups(raw_hg_map)

        if 'netgroups' in sources and 'netgroups' in data:
            self._build_netgroups(data['netgroups'])

        if 'hbacrules' in sources and 'hbacrules' in data:
            self._build_hbacrules(data['hbacrules'])

        # 4. Optionally prune hosts that are not in any created group.
        if self.get_option('host_filter_from_groups'):
            grouped_hosts = set()
            for group_name in self.inventory.groups:
                if group_name in ('all', 'ungrouped'):
                    continue
                group_obj = self.inventory.groups[group_name]
                grouped_hosts.update(h.name for h in group_obj.hosts)
            for host_fqdn in list(self.inventory.hosts):
                if host_fqdn not in grouped_hosts:
                    self.inventory.remove_host(
                        self.inventory.get_host(host_fqdn))

        # 5. Apply Constructable features (compose, groups, keyed_groups).
        for host_fqdn in list(self.inventory.hosts):
            hostvars = self.inventory.get_host(host_fqdn).get_vars()
            self._set_composite_vars(
                self.get_option('compose'), hostvars, host_fqdn, strict)
            self._add_host_to_composed_groups(
                self.get_option('groups'), hostvars, host_fqdn, strict)
            self._add_host_to_keyed_groups(
                self.get_option('keyed_groups'), hostvars, host_fqdn,
                strict)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def parse(self, inventory, loader, path, cache=True):
        # pylint: disable=super-with-arguments
        super(InventoryModule, self).parse(inventory, loader, path,
                                           cache=cache)
        self._read_config_data(path)

        self.get_option('plugin')

        if requests is None:
            raise AnsibleParserError(
                "The 'requests' Python library is required for the "
                "IDM inventory plugin.\n"
                "  RHEL/Fedora: dnf install python3-requests\n"
                "  pip:         pip install requests")

        cache_key = self.get_cache_key(path)
        use_cache = cache and self.get_option('cache')
        update_cache = False
        data = None

        if use_cache:
            try:
                data = self._cache[cache_key]
            except KeyError:
                update_cache = True

        try:
            if data is None:
                data = self._fetch_all()

            self._populate(data)

            if update_cache:
                self._cache[cache_key] = data
        finally:
            self._cleanup_ccache()

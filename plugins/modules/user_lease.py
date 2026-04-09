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

DOCUMENTATION = r"""
---
module: user_lease
version_added: "1.10.0"
short_description: Manage IdM user expiry attributes as lease-like access boundaries
description:
  - >-
    Manages C(krbPrincipalExpiration) and optionally
    C(krbPasswordExpiration) on existing FreeIPA/IdM user accounts.
  - >-
    Designed for temporary user-backed automation or delegated temporary
    operator access where IdM expiry is the primary cutoff and later cleanup
    is hygiene.
  - >-
    Supports absolute UTC timestamps, generalized-time values, and simple
    relative C(HH:MM) durations.
  - >-
    Can assert that the target user belongs to one or more governed groups
    before mutating the expiry attributes.
  - >-
    Supports Ansible check mode.
options:
  username:
    description: IdM username to modify.
    type: str
    required: true
  state:
    description:
      - C(present) ensures one or both expiry attributes are set.
      - C(expired) sets C(krbPrincipalExpiration) to the current UTC time.
      - C(cleared) removes C(krbPrincipalExpiration) and, when
        C(clear_password_expiration=true), also removes
        C(krbPasswordExpiration).
    type: str
    default: present
    choices: [present, expired, cleared]
  principal_expiration:
    description:
      - >-
        Desired lease end for C(krbPrincipalExpiration) when C(state=present).
      - >-
        Accepts UTC generalized time C(YYYYmmddHHMMSSZ), ISO 8601 UTC
        C(YYYY-MM-DDTHH:MM[:SS]Z), C(now), or a relative C(HH:MM) duration.
      - >-
        Relative durations are evaluated at runtime and therefore are not
        stable across repeated runs.
    type: raw
  password_expiration:
    description:
      - >-
        Desired C(krbPasswordExpiration) when C(state=present). Uses the same
        input formats as C(principal_expiration).
      - >-
        Leave unset to avoid changing the password-expiry attribute.
    type: raw
  password_expiration_matches_principal:
    description:
      - >-
        When true, set C(krbPasswordExpiration) to the same effective time as
        C(krbPrincipalExpiration).
      - >-
        With C(state=expired), this expires both attributes immediately.
      - >-
        Mutually exclusive with an explicit C(password_expiration).
    type: bool
    default: false
  clear_password_expiration:
    description:
      - >-
        When C(state=cleared), also remove C(krbPasswordExpiration).
      - >-
        Ignored for other states.
    type: bool
    default: false
  require_groups:
    description:
      - >-
        Require the target user to be a direct member of all listed IdM groups
        before mutating the expiry attributes.
      - >-
        Useful when the authenticated principal only has delegated write rights
        for members of a governed group.
    type: list
    elements: str
    default: []
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
    description: Kerberos principal to authenticate as.
    type: str
    default: admin
  ipaadmin_password:
    description: >-
      Password for the principal. Used to obtain a Kerberos ticket via
      C(kinit). Not required if C(kerberos_keytab) is set or a valid ticket
      already exists.
    type: str
    no_log: true
    env:
      - name: IPA_ADMIN_PASSWORD
  kerberos_keytab:
    description: >-
      Path to a Kerberos keytab file. Takes precedence over
      C(ipaadmin_password). Required for non-interactive use in AAP
      Execution Environments.
    type: str
    env:
      - name: IPA_KEYTAB
  verify:
    description: >-
      Path to the IPA CA certificate for TLS verification. Auto-detected from
      C(/etc/ipa/ca.crt) when not set. Disabled with a warning if neither is
      available.
    type: str
    env:
      - name: IPA_CERT
notes:
  - Requires C(python3-ipalib) and C(python3-ipaclient) on the Ansible controller.
  - "RHEL/Fedora: C(dnf install python3-ipalib python3-ipaclient)"
  - >-
    The authenticated principal needs write access to
    C(krbPrincipalExpiration) on the target user. Managing
    C(krbPasswordExpiration) additionally requires write access to that
    attribute.
  - >-
    A common delegated model is an IdM permission like:
    C(ipa permission-add lease-expiry-write --right=write --attrs=krbprincipalexpiration --attrs=krbpasswordexpiration --type=user --memberof=lease-targets)
    attached to a privilege and role granted to the automation user.
  - >-
    Expiring a principal blocks future authentication. It does not revoke
    already-issued Kerberos tickets; short ticket lifetime still matters when
    a hard cutoff is required.
seealso:
  - module: eigenstate.ipa.vault_write
  - lookup: eigenstate.ipa.principal
  - lookup: eigenstate.ipa.keytab
author:
  - Greg Procunier
"""

EXAMPLES = r"""
# Give a temporary user a two-hour lease window
- name: Set a two-hour principal lease
  eigenstate.ipa.user_lease:
    username: temp-deploy
    principal_expiration: "02:00"
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"

# Expire principal and password together for a governed user
- name: End temporary user access now
  eigenstate.ipa.user_lease:
    username: temp-maintenance
    state: expired
    password_expiration_matches_principal: true
    require_groups:
      - lease-targets
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/lease-operator.keytab
    ipaadmin_principal: lease-operator

# Pin an absolute UTC lease end
- name: Set explicit lease end
  eigenstate.ipa.user_lease:
    username: temp-build
    principal_expiration: "2026-04-09T18:30:00Z"
    password_expiration_matches_principal: true
    server: idm-01.example.com
    kerberos_keytab: /etc/ipa/lease-operator.keytab
    ipaadmin_principal: lease-operator

# Remove the principal expiry while leaving password expiry alone
- name: Clear temporary principal cutoff
  eigenstate.ipa.user_lease:
    username: temp-build
    state: cleared
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"

# Clear both expiry attributes
- name: Clear all lease state
  eigenstate.ipa.user_lease:
    username: temp-build
    state: cleared
    clear_password_expiration: true
    server: idm-01.example.com
    ipaadmin_password: "{{ ipa_password }}"
"""

RETURN = r"""
changed:
  description: Whether the module made any changes.
  type: bool
  returned: always
username:
  description: Target user that was inspected or modified.
  type: str
  returned: always
uid:
  description: Target user login as returned by IdM.
  type: str
  returned: always
principal_expiration_before:
  description: Prior C(krbPrincipalExpiration) value in generalized UTC format.
  type: str
  returned: always
principal_expiration_after:
  description: Final C(krbPrincipalExpiration) value in generalized UTC format.
  type: str
  returned: always
password_expiration_before:
  description: Prior C(krbPasswordExpiration) value in generalized UTC format.
  type: str
  returned: always
password_expiration_after:
  description: Final C(krbPasswordExpiration) value in generalized UTC format.
  type: str
  returned: always
lease_end:
  description: Alias for C(principal_expiration_after).
  type: str
  returned: always
memberof_group:
  description: Direct group memberships returned by IdM for the target user.
  type: list
  elements: str
  returned: always
groups_checked:
  description: Groups that were required through C(require_groups).
  type: list
  elements: str
  returned: always
"""

import datetime
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible_collections.eigenstate.ipa.plugins.module_utils.ipa_client import (
    IPAClient,
    IPAClientError,
)

try:
    from ipalib import errors as ipalib_errors
    HAS_IPALIB = True
except ImportError:
    ipalib_errors = None
    HAS_IPALIB = False

_GENERALIZED_RE = re.compile(r'^\d{14}Z$')
_ISO_UTC_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z$')
_RELATIVE_HHMM_RE = re.compile(r'^\+?(\d{1,3}):(\d{2})$')
_GROUP_CN_RE = re.compile(r'^cn=([^,]+),cn=groups,cn=accounts,', re.IGNORECASE)


def _first(value):
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    return value


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None, microsecond=0)


def _as_utc_naive(value):
    value = _first(value)
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        if value.tzinfo is not None:
            value = value.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return value.replace(microsecond=0)
    text = to_text(value).strip()
    if not text:
        return None
    if _GENERALIZED_RE.match(text):
        return datetime.datetime.strptime(text, '%Y%m%d%H%M%SZ')
    if _ISO_UTC_RE.match(text):
        fmt = '%Y-%m-%dT%H:%M:%SZ'
        if len(text) == 17:
            fmt = '%Y-%m-%dT%H:%MZ'
        return datetime.datetime.strptime(text, fmt)
    raise ValueError('Unsupported datetime value: %s' % text)


def _to_generalized(value):
    dt_value = _as_utc_naive(value)
    if dt_value is None:
        return None
    return dt_value.strftime('%Y%m%d%H%M%SZ')


def _same_datetime(left, right):
    return _to_generalized(left) == _to_generalized(right)


def _parse_time_spec(spec, now=None):
    if spec is None:
        return None
    text = to_text(spec).strip()
    if not text:
        raise ValueError('time spec may not be empty')
    if now is None:
        now = _utc_now()
    lowered = text.lower()
    if lowered == 'now':
        return now
    if _GENERALIZED_RE.match(text):
        return datetime.datetime.strptime(text, '%Y%m%d%H%M%SZ')
    if _ISO_UTC_RE.match(text):
        fmt = '%Y-%m-%dT%H:%M:%SZ'
        if len(text) == 17:
            fmt = '%Y-%m-%dT%H:%MZ'
        return datetime.datetime.strptime(text, fmt)
    match = _RELATIVE_HHMM_RE.match(text)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        return now + datetime.timedelta(hours=hours, minutes=minutes)
    raise ValueError(
        "Unsupported time spec '%s'. Use generalized UTC, ISO 8601 UTC, "
        "'now', or relative HH:MM." % text)


def _direct_groups(entry):
    groups = entry.get('memberof_group') or []
    if groups:
        return sorted(to_text(group) for group in groups)

    memberof_values = entry.get('memberof') or []
    extracted = []
    for value in memberof_values:
        text = to_text(value)
        match = _GROUP_CN_RE.match(text)
        if match:
            extracted.append(match.group(1))
    return sorted(extracted)


def _validate_params(module):
    state = module.params['state']
    principal_expiration = module.params['principal_expiration']
    password_expiration = module.params['password_expiration']
    match_password = module.params['password_expiration_matches_principal']

    if password_expiration is not None and match_password:
        module.fail_json(
            msg="'password_expiration' and 'password_expiration_matches_principal' are mutually exclusive.")

    if state == 'present' and principal_expiration is None and password_expiration is None and not match_password:
        module.fail_json(
            msg="state=present requires 'principal_expiration', 'password_expiration', or 'password_expiration_matches_principal=true'.")

    if state in ('expired', 'cleared'):
        if principal_expiration is not None or password_expiration is not None:
            module.fail_json(
                msg="'principal_expiration' and 'password_expiration' may only be used with state=present.")
        if state == 'cleared' and match_password:
            module.fail_json(
                msg="'password_expiration_matches_principal' is not valid with state=cleared. Use clear_password_expiration=true instead.")


def _user_show(api, username):
    try:
        result = api.Command.user_show(username, all=True)
    except ipalib_errors.NotFound:
        return None
    return result.get('result', {})


def _build_mod_args(before, params, now):
    state = params['state']
    principal_expiration = params['principal_expiration']
    password_expiration = params['password_expiration']
    match_password = params['password_expiration_matches_principal']
    clear_password = params['clear_password_expiration']

    current_principal = _as_utc_naive(before.get('krbprincipalexpiration'))
    current_password = _as_utc_naive(before.get('krbpasswordexpiration'))

    setattr = []
    delattr = []

    if state == 'present':
        target_principal = None

        if principal_expiration is not None:
            target_principal = _parse_time_spec(principal_expiration, now=now)
            if not _same_datetime(current_principal, target_principal):
                setattr.append('krbprincipalexpiration=%s' % _to_generalized(target_principal))

        if match_password:
            if target_principal is None:
                raise ValueError(
                    "'password_expiration_matches_principal=true' requires 'principal_expiration' when state=present.")
            if not _same_datetime(current_password, target_principal):
                setattr.append('krbpasswordexpiration=%s' % _to_generalized(target_principal))
        elif password_expiration is not None:
            target_password = _parse_time_spec(password_expiration, now=now)
            if not _same_datetime(current_password, target_password):
                setattr.append('krbpasswordexpiration=%s' % _to_generalized(target_password))

    elif state == 'expired':
        target_principal = now
        if not _same_datetime(current_principal, target_principal):
            setattr.append('krbprincipalexpiration=%s' % _to_generalized(target_principal))

        if match_password and not _same_datetime(current_password, target_principal):
            setattr.append('krbpasswordexpiration=%s' % _to_generalized(target_principal))

    elif state == 'cleared':
        if current_principal is not None:
            delattr.append('krbprincipalexpiration=%s' % _to_generalized(current_principal))
        if clear_password and current_password is not None:
            delattr.append('krbpasswordexpiration=%s' % _to_generalized(current_password))

    mod_args = {}
    if setattr:
        mod_args['setattr'] = setattr
    if delattr:
        mod_args['delattr'] = delattr
    return mod_args


def _apply_preview(entry, mod_args):
    preview = dict(entry)
    for item in mod_args.get('setattr', []):
        attr, value = item.split('=', 1)
        preview[attr] = (_as_utc_naive(value),)
    for item in mod_args.get('delattr', []):
        attr, _sep, _value = item.partition('=')
        preview.pop(attr, None)
    return preview


def _result_payload(username, entry, before_entry, groups_checked):
    uid = _first(entry.get('uid'))
    principal_after = _to_generalized(entry.get('krbprincipalexpiration'))
    password_after = _to_generalized(entry.get('krbpasswordexpiration'))
    return {
        'username': username,
        'uid': to_text(uid) if uid is not None else username,
        'principal_expiration_before': _to_generalized(before_entry.get('krbprincipalexpiration')),
        'principal_expiration_after': principal_after,
        'password_expiration_before': _to_generalized(before_entry.get('krbpasswordexpiration')),
        'password_expiration_after': password_after,
        'lease_end': principal_after,
        'memberof_group': _direct_groups(entry),
        'groups_checked': list(groups_checked),
    }


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            username=dict(type='str', required=True),
            state=dict(type='str', default='present',
                       choices=['present', 'expired', 'cleared']),
            principal_expiration=dict(type='raw'),
            password_expiration=dict(type='raw', no_log=False),
            password_expiration_matches_principal=dict(type='bool', default=False, no_log=False),
            clear_password_expiration=dict(type='bool', default=False, no_log=False),
            require_groups=dict(type='list', elements='str', default=[]),
            server=dict(type='str', required=True),
            ipaadmin_principal=dict(type='str', default='admin'),
            ipaadmin_password=dict(type='str', no_log=True, required=False),
            kerberos_keytab=dict(type='str', required=False),
            verify=dict(type='str', required=False),
        ),
        supports_check_mode=True,
    )

    if not HAS_IPALIB:
        module.fail_json(
            msg="The 'ipalib' Python library is required.\n  RHEL/Fedora: dnf install python3-ipalib python3-ipaclient")

    _validate_params(module)

    username = module.params['username']
    require_groups = [to_text(group) for group in module.params['require_groups']]
    now = _utc_now()

    client = IPAClient(warn_callback=module.warn)

    try:
        client.connect(
            server=module.params['server'],
            principal=module.params['ipaadmin_principal'],
            password=module.params['ipaadmin_password'],
            keytab=module.params['kerberos_keytab'],
            verify=module.params['verify'],
        )
    except IPAClientError as exc:
        module.fail_json(msg=to_native(exc))

    try:
        before_entry = _user_show(client.api, username)
        if before_entry is None:
            module.fail_json(msg="User '%s' does not exist in IdM." % username)

        groups = _direct_groups(before_entry)
        missing_groups = [group for group in require_groups if group not in groups]
        if missing_groups:
            module.fail_json(
                msg="User '%s' is missing required group membership(s): %s" % (
                    username, ', '.join(missing_groups)),
                username=username,
                memberof_group=groups,
                groups_checked=require_groups,
                groups_missing=missing_groups,
            )

        try:
            mod_args = _build_mod_args(before_entry, module.params, now)
        except ValueError as exc:
            module.fail_json(msg=to_native(exc))

        changed = bool(mod_args)
        if changed and not module.check_mode:
            try:
                client.api.Command.user_mod(username, **mod_args)
            except client.errors.EmptyModlist:
                changed = False
            except Exception as exc:
                authz_msg = IPAClient.authz_error_message(
                    exc, "modify lease attributes for user '%s'" % username,
                    module.params['ipaadmin_principal'])
                if authz_msg:
                    module.fail_json(msg=authz_msg)
                module.fail_json(
                    msg="Failed to modify lease attributes for user '%s': %s"
                        % (username, to_native(exc)))

        after_entry = before_entry
        if changed:
            if module.check_mode:
                after_entry = _apply_preview(before_entry, mod_args)
            else:
                after_entry = _user_show(client.api, username) or before_entry

        result = _result_payload(
            username=username,
            entry=after_entry,
            before_entry=before_entry,
            groups_checked=require_groups,
        )
        result['changed'] = changed
        module.exit_json(**result)
    finally:
        client.cleanup()


def main():
    run_module()


if __name__ == '__main__':
    main()

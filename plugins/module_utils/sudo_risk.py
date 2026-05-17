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

import fnmatch

from ansible.module_utils.common.text.converters import to_native, to_text


DEFAULT_PATTERNS = {
    'shell_escape': [
        '/bin/sh',
        '/bin/bash',
        '/usr/bin/sh',
        '/usr/bin/bash',
        '/usr/bin/su',
        '/usr/bin/sudo',
        '/usr/bin/vi',
        '/usr/bin/vim',
        '/usr/bin/less',
        '/usr/bin/more',
    ],
    'package_manager': [
        '/usr/bin/dnf',
        '/usr/bin/yum',
        '/usr/bin/rpm',
        '/usr/bin/apt',
        '/usr/bin/apt-get',
        '/usr/bin/zypper',
    ],
    'policy_management': [
        '/usr/sbin/semanage',
        '/usr/sbin/semodule',
        '/usr/sbin/setsebool',
        '/usr/bin/chcon',
        '/usr/bin/restorecon',
    ],
    'idm_management': [
        '/usr/bin/ipa',
        '/usr/sbin/ipa-server-install',
        '/usr/sbin/ipa-replica-install',
        '/usr/sbin/ipa-getkeytab',
    ],
    'broad_file_write': [
        '/usr/bin/tee',
        '/usr/bin/cp',
        '/usr/bin/mv',
        '/usr/bin/chmod',
        '/usr/bin/chown',
        '/usr/bin/dd',
    ],
}


CATEGORY_REASONS = {
    'shell_escape': 'command can provide an interactive shell or shell escape',
    'package_manager': 'package managers can alter host privileged state',
    'policy_management': 'policy tools can change host enforcement state',
    'idm_management': 'IdM tools can change identity or access policy state',
    'broad_file_write': 'file-write tools can alter arbitrary privileged files',
    'unrestricted_runas': 'rule allows unrestricted RunAs identity selection',
    'custom': 'command matches a caller-supplied risk pattern',
}


SEVERITY_ORDER = {
    'low': 1,
    'medium': 2,
    'high': 3,
}


def _list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [
            to_native(to_text(item, errors='surrogate_or_strict'))
            for item in value
        ]
    return [to_native(to_text(value, errors='surrogate_or_strict'))]


def _text(value):
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        if not value:
            return None
        value = value[0]
    return to_native(to_text(value, errors='surrogate_or_strict'))


def _commands_from_rule(sudo_rule):
    commands = []
    for key in ('allow_sudocmds', 'commands', 'command', 'sudocmd'):
        commands.extend(_list(sudo_rule.get(key)))
    return sorted(set(commands))


def _merge_patterns(custom_patterns=None):
    patterns = {
        category: list(values)
        for category, values in DEFAULT_PATTERNS.items()
    }
    for category, values in (custom_patterns or {}).items():
        patterns.setdefault(category, [])
        patterns[category].extend(_list(values))
    return patterns


def _matches(command, pattern):
    command_path = command.split()[0] if command else ''
    return (
        command == pattern
        or command_path == pattern
        or fnmatch.fnmatch(command, pattern)
        or fnmatch.fnmatch(command_path, pattern)
    )


def _finding(category, command=None, severity='high', reason=None):
    return {
        'category': category,
        'severity': severity,
        'command': command,
        'reason': reason or CATEGORY_REASONS.get(category, 'risk detected'),
    }


def _risk_level(findings):
    if not findings:
        return 'low'
    highest = max(SEVERITY_ORDER[item['severity']] for item in findings)
    for label, rank in SEVERITY_ORDER.items():
        if rank == highest:
            return label
    return 'unknown'


def classify_sudo_rule(sudo_rule, risk_categories=None, custom_patterns=None):
    """Classify one normalized sudo rule record."""
    if not isinstance(sudo_rule, dict):
        return {
            'risk_level': 'unknown',
            'findings': [_finding(
                'custom',
                severity='medium',
                reason='sudo_rule must be a dictionary')],
            'recommendation': 'review_input_shape',
        }

    active_categories = set(risk_categories or [
        'shell_escape',
        'package_manager',
        'policy_management',
        'idm_management',
        'broad_file_write',
        'unrestricted_runas',
        'custom',
    ])
    patterns = _merge_patterns(custom_patterns)
    findings = []

    cmdcategory = _text(sudo_rule.get('cmdcategory'))
    if cmdcategory == 'all' or 'ALL' in _commands_from_rule(sudo_rule):
        findings.append(_finding(
            'custom',
            command='ALL',
            severity='high',
            reason='rule allows all commands'))

    for command in _commands_from_rule(sudo_rule):
        if command == 'ALL':
            continue
        for category, category_patterns in patterns.items():
            if category not in active_categories:
                continue
            if any(_matches(command, pattern) for pattern in category_patterns):
                severity = 'high'
                if category == 'broad_file_write':
                    severity = 'medium'
                findings.append(_finding(category, command, severity=severity))

    if 'unrestricted_runas' in active_categories:
        runas_category = _text(sudo_rule.get('runasusercategory'))
        runas_users = _list(sudo_rule.get('runasusers'))
        external_runas = _list(sudo_rule.get('external_runasusers'))
        if runas_category == 'all' or 'ALL' in runas_users or 'ALL' in external_runas:
            findings.append(_finding(
                'unrestricted_runas',
                command=None,
                severity='high'))

    # De-duplicate findings while preserving order.
    seen = set()
    unique = []
    for item in findings:
        key = (item['category'], item['command'], item['reason'])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    level = _risk_level(unique)
    if level == 'low':
        recommendation = 'monitor'
    elif level == 'medium':
        recommendation = 'review_or_split_identity'
    elif level == 'high':
        recommendation = 'review_or_split_identity'
    else:
        recommendation = 'review_input_shape'

    return {
        'risk_level': level,
        'findings': unique,
        'recommendation': recommendation,
    }


def sudo_risk(sudo_rule, risk_categories=None, custom_patterns=None):
    """Alias for template readability."""
    return classify_sudo_rule(
        sudo_rule,
        risk_categories=risk_categories,
        custom_patterns=custom_patterns,
    )

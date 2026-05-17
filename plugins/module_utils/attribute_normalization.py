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

from ansible.module_utils.common.text.converters import to_native, to_text


def attribute_type(value, missing=False):
    """Return a stable public type label for an IdM attribute value."""
    if missing:
        return 'missing'
    if value is None:
        return 'none'
    if isinstance(value, (list, tuple)):
        return 'list'
    if isinstance(value, str):
        return 'string'
    if isinstance(value, dict):
        return 'dict'
    return 'unexpected'


def _warning(attribute, expected, actual, action, reason=None):
    item = {
        'attribute': attribute,
        'expected': expected,
        'actual': actual,
        'action': action,
    }
    if reason:
        item['reason'] = reason
    return item


def _stringify_scalar(value):
    return to_native(to_text(value, errors='surrogate_or_strict'))


def normalize_list_attribute(value, attribute, missing=False):
    """Normalize an IdM attribute to ``list[str]`` without stringifying dicts."""
    actual = attribute_type(value, missing=missing)
    warnings = []

    if missing or value is None:
        return {
            'value': [],
            'raw': None if missing else value,
            'type': actual,
            'warnings': warnings,
        }

    if isinstance(value, dict):
        warnings.append(_warning(
            attribute, 'list[str]', actual, 'rejected',
            'dictionary values are not valid list elements'))
        return {
            'value': [],
            'raw': value,
            'type': actual,
            'warnings': warnings,
        }

    if isinstance(value, str):
        if value == '':
            warnings.append(_warning(
                attribute, 'list[str]', actual, 'empty',
                'empty string normalized to an empty list'))
            normalized = []
        else:
            warnings.append(_warning(
                attribute, 'list[str]', actual, 'normalized',
                'string value normalized to a single-item list'))
            normalized = [value]
        return {
            'value': normalized,
            'raw': value,
            'type': actual,
            'warnings': warnings,
        }

    if isinstance(value, (list, tuple)):
        normalized = []
        rejected = 0
        converted = 0
        for item in value:
            if isinstance(item, dict) or isinstance(item, (list, tuple)):
                rejected += 1
                continue
            if item is None:
                rejected += 1
                continue
            if not isinstance(item, str):
                converted += 1
            normalized.append(_stringify_scalar(item))
        if rejected:
            warnings.append(_warning(
                attribute, 'list[str]', actual, 'rejected',
                '%d non-scalar list value(s) were ignored' % rejected))
        if converted:
            warnings.append(_warning(
                attribute, 'list[str]', actual, 'normalized',
                '%d non-string scalar list value(s) were converted' % converted))
        return {
            'value': normalized,
            'raw': value,
            'type': actual,
            'warnings': warnings,
        }

    warnings.append(_warning(
        attribute, 'list[str]', actual, 'normalized',
        'scalar value normalized to a single-item list'))
    return {
        'value': [_stringify_scalar(value)],
        'raw': value,
        'type': actual,
        'warnings': warnings,
    }


def normalize_scalar_attribute(value, attribute, missing=False):
    """Normalize an IdM attribute expected to be scalar-like."""
    actual = attribute_type(value, missing=missing)
    warnings = []

    if missing or value is None:
        return {
            'value': None,
            'raw': None if missing else value,
            'type': actual,
            'warnings': warnings,
        }

    if isinstance(value, dict):
        warnings.append(_warning(
            attribute, 'scalar', actual, 'rejected',
            'dictionary values are not valid scalar values'))
        return {
            'value': None,
            'raw': value,
            'type': actual,
            'warnings': warnings,
        }

    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return {
                'value': None,
                'raw': value,
                'type': actual,
                'warnings': warnings,
            }
        if len(value) == 1:
            item = value[0]
            if isinstance(item, dict) or isinstance(item, (list, tuple)):
                warnings.append(_warning(
                    attribute, 'scalar', actual, 'rejected',
                    'nested value is not a valid scalar'))
                normalized = None
            else:
                normalized = item
            return {
                'value': normalized,
                'raw': value,
                'type': actual,
                'warnings': warnings,
            }
        warnings.append(_warning(
            attribute, 'scalar', actual, 'warning',
            'multi-value list preserved for compatibility'))
        return {
            'value': list(value),
            'raw': value,
            'type': actual,
            'warnings': warnings,
        }

    return {
        'value': value,
        'raw': value,
        'type': actual,
        'warnings': warnings,
    }


def normalize_attribute(value, attribute='attribute', expected='list',
                        missing=False):
    """Normalize an IdM attribute and return value/raw/type/warnings fields."""
    if expected in ('list', 'list[str]'):
        return normalize_list_attribute(value, attribute, missing=missing)
    if expected in ('scalar', 'string'):
        return normalize_scalar_attribute(value, attribute, missing=missing)
    raise ValueError("unsupported expected attribute shape: %s" % expected)


def ensure_list(value):
    """Return only the normalized list value for simple template use."""
    return normalize_list_attribute(value, 'value')['value']

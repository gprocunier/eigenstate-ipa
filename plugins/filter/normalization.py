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
name: normalization
version_added: "1.18.0"
short_description: Normalize IdM attribute shapes for playbook consumers
description:
  - Provides small filters for turning IdM/FreeIPA attribute values into
    stable shapes while preserving enough metadata for callers to inspect
    raw schema drift.
  - The filters are generic and can be used with inventory host variables,
    lookup results, or module return values.
options:
  _input:
    description: Raw IdM attribute value to normalize or classify.
    type: raw
author:
  - Greg Procunier (@gprocunier)
"""

EXAMPLES = """
- name: Normalize a possibly scalar IdM attribute
  ansible.builtin.set_fact:
    normalized_classes: "{{ raw_userclass | eigenstate.ipa.ensure_list }}"

- name: Keep value, raw input, type, and warnings together
  ansible.builtin.set_fact:
    normalized: >-
      {{ raw_location
         | eigenstate.ipa.normalize_attribute(attribute='idm_location',
                                             expected='scalar') }}

- name: Classify an attribute shape
  ansible.builtin.debug:
    msg: "{{ raw_value | eigenstate.ipa.attribute_type }}"
"""

RETURN = """
_value:
  description: Normalized value, metadata dictionary, or type label.
  type: raw
"""

try:
    from ansible_collections.eigenstate.ipa.plugins.module_utils.attribute_normalization import (
        attribute_type,
        ensure_list,
        normalize_attribute,
    )
except ImportError:
    import importlib.util
    import pathlib
    _normalization_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / 'module_utils' / 'attribute_normalization.py')
    _normalization_spec = importlib.util.spec_from_file_location(
        'eigenstate_ipa_attribute_normalization', _normalization_path)
    _normalization_mod = importlib.util.module_from_spec(_normalization_spec)
    _normalization_spec.loader.exec_module(_normalization_mod)
    attribute_type = _normalization_mod.attribute_type
    ensure_list = _normalization_mod.ensure_list
    normalize_attribute = _normalization_mod.normalize_attribute


class FilterModule(object):
    """Expose IdM attribute normalization filters."""

    def filters(self):
        return {
            'attribute_type': attribute_type,
            'ensure_list': ensure_list,
            'normalize_attribute': normalize_attribute,
        }

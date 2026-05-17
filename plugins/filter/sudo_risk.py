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
name: sudo_risk
version_added: "1.18.0"
short_description: Classify sudo rule risk for privileged automation
description:
  - Classifies normalized sudo rule records, such as records returned by
    C(eigenstate.ipa.sudo), into advisory risk findings.
  - The classifier is read-only and does not enforce policy.
  - Default categories are conservative and can be narrowed or extended
    by the caller.
options:
  _input:
    description: Sudo rule record to classify.
    type: dict
  risk_categories:
    description: Optional list of categories to evaluate.
    type: list
    elements: str
  custom_patterns:
    description: Optional category-to-command-pattern mapping.
    type: dict
author:
  - Greg Procunier (@gprocunier)
"""

EXAMPLES = """
- name: Classify a sudo rule
  ansible.builtin.set_fact:
    risk: "{{ sudo_rule | eigenstate.ipa.sudo_risk }}"

- name: Classify with a custom package-management wrapper
  ansible.builtin.set_fact:
    risk: >-
      {{ sudo_rule
         | eigenstate.ipa.classify_sudo_rule(
             custom_patterns={'package_manager': ['/opt/tools/pkgctl']}) }}
"""

RETURN = """
_value:
  description: Risk result with risk_level, findings, and recommendation.
  type: dict
"""

try:
    from ansible_collections.eigenstate.ipa.plugins.module_utils.sudo_risk import (
        classify_sudo_rule,
        sudo_risk,
    )
except ImportError:
    import importlib.util
    import pathlib
    _sudo_risk_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / 'module_utils' / 'sudo_risk.py')
    _sudo_risk_spec = importlib.util.spec_from_file_location(
        'eigenstate_ipa_sudo_risk', _sudo_risk_path)
    _sudo_risk_mod = importlib.util.module_from_spec(_sudo_risk_spec)
    _sudo_risk_spec.loader.exec_module(_sudo_risk_mod)
    classify_sudo_rule = _sudo_risk_mod.classify_sudo_rule
    sudo_risk = _sudo_risk_mod.sudo_risk


class FilterModule(object):
    """Expose sudo risk classification filters."""

    def filters(self):
        return {
            'classify_sudo_rule': classify_sudo_rule,
            'sudo_risk': sudo_risk,
        }

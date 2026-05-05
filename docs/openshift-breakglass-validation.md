---
layout: default
title: OpenShift Breakglass Validation
description: >-
  Validation model for OpenShift emergency access backed by IdM groups,
  documented controls, and auditable RBAC bindings.
---

{% raw %}

# OpenShift Breakglass Validation

Breakglass access should be explicit, narrow, reviewed, and easy to audit. This
collection treats it as a validation problem by default: prove the group,
principal, RBAC, and control evidence before any live cluster action.

## Role

`openshift_breakglass_validation` checks local evidence for:

- expected IdM emergency-access groups
- expected IdM principals
- expected OpenShift RBAC bindings
- required operational controls

The role writes JSON and Markdown readiness reports. It does not contact
OpenShift or IdM and it does not create emergency credentials.

## Playbook

```bash
ansible-playbook playbooks/validate-openshift-breakglass-path.yml
```

Override the evidence variables when validating a site-specific model:

```bash
ansible-playbook playbooks/validate-openshift-breakglass-path.yml \
  -e eigenstate_breakglass_expected_groups='["ocp-breakglass-admins"]' \
  -e eigenstate_breakglass_known_idm_groups='["ocp-breakglass-admins"]'
```

## Review Questions

- Is the emergency-access group distinct from everyday platform-admin groups?
- Is membership reviewed outside the incident window?
- Does the RBAC binding target a group instead of individual users?
- Is credential material stored outside the repository and outside rendered
  reports?
- Is there an expiry, removal, or post-incident review process?

The role cannot answer policy questions for the operator. It makes the evidence
visible and repeatable so the review can be performed consistently.

{% endraw %}

---
layout: default
title: Issue an OTP or host enrollment password
diataxis: how-to
diataxis_type: how-to
audience: Operators completing IdM-backed automation tasks
outcome: Use this when IdM should issue a user OTP token or one-time host enrollment password.
authority_boundary:
  - idm
  - collection
workflow_boundary: mutating
evidence_shape:
  - command-output
public_status: rewritten
last_verified: 2026-05-07
---
{% raw %}

# Issue an OTP or host enrollment password

## When To Use This

Use this when IdM should issue a user OTP token or one-time host enrollment password.

## Required Authority

IdM owns token and host enrollment state. The lookup calls IdM to issue or inspect the credential.

## Safety Boundary

This workflow is `mutating`. Confirm that this is the intended boundary before placing it in a scheduled job or AAP workflow.

## Secret Handling

Do not print payload material. Use `no_log: true` on payload-bearing tasks. Review artifacts should redact secret values, and payload manifest rendering should be opt-in.

## Inputs

- User or host target
- OTP type or host enrollment mode
- Credentials allowed to issue the credential

## Steps

1. Choose user OTP or host enrollment mode.
2. Issue the credential in a `no_log: true` task.
3. Pass the value directly to enrollment or an out-of-band delivery process.

```yaml
- name: Issue host enrollment password
  ansible.builtin.set_fact:
    enrollment_password: "{{ lookup('eigenstate.ipa.otp', 'client01.example.com', operation='host_password') }}"
  no_log: true
```

## Expected Result

IdM issues the requested one-time credential and the play does not print it.

## Troubleshooting

- Token not issued: verify IdM permission and target existence.
- Credential leaked in output: remove debug and keep `no_log: true`.
- Enrollment fails: verify host DNS and IdM enrollment prerequisites.

## Related Reference

- [/reference/lookups/otp.html](../reference/lookups/otp.html)
- [/how-to/query-principal-state.html](query-principal-state.html)

{% endraw %}

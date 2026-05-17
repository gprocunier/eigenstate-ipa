---
layout: default
title: IdM access-path summary
diataxis: how-to
diataxis_type: how-to
audience: Operators preflighting principal, HBAC, sudo, and SELinux map readiness
outcome: Produce one structured readiness result before privileged automation.
authority_boundary:
  - idm
  - collection
workflow_boundary: preflight
evidence_shape:
  - command-output
public_status: new
last_verified: 2026-05-16
---
{% raw %}

# IdM access-path summary

Use `eigenstate.ipa.access_path` before a workflow depends on a principal being
able to reach a host, pass HBAC, use an expected sudo RunAs target, and land in
the expected SELinux user map.

```yaml
- name: Summarize automation access path
  eigenstate.ipa.access_path:
    server: idm-01.example.com
    kerberos_keytab: /runner/env/ipa/automation.keytab
    principal: automation@EXAMPLE.COM
    host: app01.example.com
    hbac_service: sshd
    hbac_rule: automation-ssh
    sudo_rule: automation-root
    selinux_map: automation-confined
    expected_runas_user: root
    expected_selinux_user: staff_u:s0
  register: access_path
```

The module reports facts. It does not create or enforce policy.

```yaml
path_ready: true
principal:
  exists: true
hbac:
  exists: true
  enabled: true
  permits_service: true
sudo:
  exists: true
  enabled: true
  runas_ok: true
selinux_map:
  exists: true
  enabled: true
  selinuxuser_matches: true
warnings: []
errors: []
```

Use `path_ready` as a preflight branch, and preserve `errors` as review
evidence when the path is not ready.

## Release gate

Validate at least one green path and one negative path in the lab, such as a
missing rule or disabled rule, when the test environment can tolerate it.

{% endraw %}

---
layout: default
title: KRA-aware vault health
diataxis: how-to
diataxis_type: how-to
audience: Operators checking whether IdM vault workflows are usable on a specific server
outcome: Distinguish IdM reachability from KRA-backed vault readiness.
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

# KRA-aware vault health

IdM LDAP host and policy data can be reachable while vault operations are not.
Vault payloads depend on the KRA-backed vault plane, so preflight checks should
target the server that the workflow will use.

```yaml
- name: Check vault health on an explicit server
  eigenstate.ipa.vault_health:
    server: idm-01.example.com
    kerberos_keytab: /runner/env/ipa/automation.keytab
    ipaadmin_principal: automation@EXAMPLE.COM
    verify: /etc/ipa/ca.crt
    shared: true
    canary_vault: automation-health-canary
    canary_max_age_seconds: 3600
    require_direct_kra: true
  register: vault_health
```

The result separates planes:

```yaml
changed: false
idm_reachable: true
vault_reachable: true
kra_available: true
canary_present: true
canary_age_seconds: 42
canary_stale: false
failure_class: none
```

Failure classes are intended for branching:

```text
none
auth
ca
ldap
kra_unavailable
vault_not_found
timeout
scope_mismatch
unknown
```

`vault_health` does not validate vault replication consistency or payload
freshness beyond the canary fields it can observe. It shows that the selected
request path can authenticate, reach IdM, and run KRA-backed vault operations.

## Release gate

Validate in the lab against a KRA-enabled server and, when available, a server
that cannot complete vault operations directly:

```bash
ansible-playbook playbooks/validate-vault-health.yml -e server=idm-01.example.com
```

Capture the server, principal, CA path, KRA topology, canary result, and any
negative-test failure class.

{% endraw %}

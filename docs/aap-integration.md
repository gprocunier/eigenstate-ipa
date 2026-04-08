---
layout: default
title: AAP Integration
---

{% raw %}

# AAP Integration

Related docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/vault-cyberark-primer.html"><kbd>&nbsp;&nbsp;VAULT/CYBERARK PRIMER&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>&nbsp;&nbsp;ROTATION USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>&nbsp;&nbsp;INVENTORY USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

## Purpose

This page explains how `eigenstate.ipa` fits into Ansible Automation Platform
and Automation Controller.

The important boundary is simple: the collection is mostly controller-side.
The execution environment talks directly to IdM. Managed hosts usually consume
artifacts or decisions that were produced on the controller.

Use this page for:

- execution-environment dependency planning
- non-interactive authentication guidance
- the controller-side workflows that are actually worth standardizing
- the handoff point between `eigenstate.ipa` and the official IdM collections

Use plugin pages for exact options. Use use-case pages for full playbook detail.
This page is the control-plane view.

## Controller Model

```mermaid
flowchart LR
    ctrl["Controller job or inventory sync"] --> ee["Execution environment"]
    cred["Mounted keytab or password credential"] --> ee
    ee --> inv["idm inventory"]
    ee --> lookups["lookup plugins"]
    ee --> write["vault_write module"]
    inv --> idm["IdM / FreeIPA"]
    lookups --> idm
    write --> idm
```

The collection is strongest when AAP supplies:

- the schedule
- the execution environment image
- credential injection
- approvals and job boundaries
- repeatable controller-side execution

That is the part of the stack that makes IdM-backed workflows feel operationally
coherent instead of ad hoc.

## Current Controller-Side Surface

### Inventory

- `eigenstate.ipa.idm`

### `ipalib`-backed lookups and module

- `eigenstate.ipa.vault`
- `eigenstate.ipa.vault_write`
- `eigenstate.ipa.principal`
- `eigenstate.ipa.cert`
- `eigenstate.ipa.otp`
- `eigenstate.ipa.dns`
- `eigenstate.ipa.selinuxmap`
- `eigenstate.ipa.sudo`
- `eigenstate.ipa.hbacrule`

### CLI-backed lookup

- `eigenstate.ipa.keytab`

The official IdM collections still matter beside this surface. They remain the
right place for enrollment, broad CRUD against IdM objects, and cert revocation.
`eigenstate.ipa` is the read-heavy and workflow-focused layer around those
operations.

## Execution Environment Requirements

| Surface | EE requirements | Notes |
| --- | --- | --- |
| `idm` inventory | `python3-requests`; `python3-gssapi`; `python3-requests-gssapi` or `python3-requests-kerberos`; `krb5-workstation` when keytab-driven `kinit` is used | inventory does not require `ipalib` |
| `vault`, `vault_write`, `principal`, `cert`, `otp`, `dns`, `selinuxmap`, `sudo`, `hbacrule` | `python3-ipalib`; `python3-ipaclient`; `krb5-workstation` for ticket acquisition | these share the same IdM Python stack |
| `keytab` | package providing `ipa-getkeytab`; `krb5-workstation` | on RHEL 10 this is `ipa-client` |

> [!IMPORTANT]
> Inventory can work while the `ipalib`-backed surfaces fail if the EE only
> contains the HTTP stack. That split is deliberate in the collection, so the
> EE image has to be deliberate too.

For most estates, the simplest stable Controller posture is one EE containing
all three dependency groups.

## Authentication Guidance

Prefer Kerberos with a mounted keytab.

Why:

- the same credential shape works for inventory, lookups, `vault_write`, and `keytab`
- it avoids reusable plaintext admin passwords in job templates
- it works for inventory syncs and normal job runs
- it fits Controller credential injection cleanly

Recommended pattern:

- store the keytab as a Controller-managed credential file
- mount it into the EE at runtime
- set `kerberos_keytab` explicitly in the inventory source or task
- mount the IdM CA and set `verify`
- set `ipaadmin_principal` explicitly when ambiguity is possible

## High-Value Controller Workflows

These are the combinations worth documenting and standardizing. They are the
places where the collection becomes a coherent controller workflow instead of isolated plugin calls.

### 1. Identity-driven inventory sync

Use `eigenstate.ipa.idm` to make Controller inventory follow the IdM model
instead of a second static host list.

High-value combinations:

- `hosts` + `hostvars_include` for lean synced metadata
- `hostgroups`, `netgroups`, or `hbacrules` for security- or role-shaped targeting
- `keyed_groups` over `idm_location`, `idm_os`, or `idm_hostgroups` for smart inventory input

Guardrail:

- `hostvars_enabled` and `hostvars_include` only control host attribute export
- Ansible can still merge group-derived vars into final hostvars later in the inventory process

Read next:
<a href="https://gprocunier.github.io/eigenstate-ipa/inventory-use-cases.html"><kbd>INVENTORY USE CASES</kbd></a>

### 2. Pre-flight gate before changing systems

Use lookups on the controller before any managed host work starts.

Best combinations:

- `dns` to verify name state the workflow depends on
- `principal` to confirm the principal exists and is usable
- `hbacrule` to test whether access is actually allowed
- `selinuxmap` and `sudo` to confirm confinement and privilege shape

This is one of the collection's strongest differentiated patterns. Vault and
CyberArk can answer credential questions. They do not answer live IdM policy
questions for a host, service, or login path.

### 3. Service onboarding

Use `principal` as the gate, then branch into the artifact you actually need:

- `keytab` for Kerberos service onboarding
- `cert` for X.509 issuance
- `vault_write` when the workflow must archive a private key or related bootstrap secret

This keeps identity state, key material, and cert issuance in one controller
flow instead of scattering them across shell tasks.

Read next:
<a href="https://gprocunier.github.io/eigenstate-ipa/principal-use-cases.html"><kbd>PRINCIPAL USE CASES</kbd></a>

### 4. Static secret lifecycle

Use `vault_write` for mutation and `vault` for retrieval. Let AAP supply the
schedule, approvals, execution boundary, and credentials.

This is the correct answer to the collection's rotation story:

- no native lease engine
- yes controller-scheduled rotation workflows for static IdM-backed assets

Read next:
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>ROTATION USE CASES</kbd></a>

### 5. Host enrollment and first-day trust

Use `otp` to generate the enrollment credential, then hand the actual
installation to the official IdM collections.

Best combination:

- `eigenstate.ipa.otp` for the one-time host password
- `freeipa.ansible_freeipa.ipahost` or `redhat.rhel_idm.ipahost` to ensure the host object exists
- `freeipa.ansible_freeipa.ipaclient` or `redhat.rhel_idm.ipaclient` for enrollment
- `principal` afterward if the workflow needs a post-enrollment check

That keeps `eigenstate.ipa` on the credential-generation boundary it was built
for instead of turning it into a full enrollment role.

## Example Patterns

### Lean inventory source for Controller

```yaml
plugin: eigenstate.ipa.idm
server: idm-01.corp.example.com
use_kerberos: true
kerberos_keytab: /runner/env/ipa/admin.keytab
verify: /etc/ipa/ca.crt
sources:
  - hosts
  - hostgroups
hostgroup_filter:
  - webservers
  - databases
host_filter_from_groups: true
hostvars_include:
  - idm_fqdn
  - idm_location
  - idm_hostgroups
keyed_groups:
  - key: idm_location
    prefix: dc
    separator: "_"
```

### Controller-side policy gate before maintenance

```yaml
- name: Pre-flight gate before privileged maintenance
  hosts: localhost
  gather_facts: false

  vars:
    target_host: app01.corp.example.com
    deploy_identity: svc-maintenance

  tasks:
    - name: Confirm sudo rule exists
      ansible.builtin.set_fact:
        sudo_rule: "{{ lookup('eigenstate.ipa.sudo',
                        'ops-maintenance',
                        sudo_object='rule',
                        server='idm-01.corp.example.com',
                        kerberos_keytab='/runner/env/ipa/admin.keytab',
                        verify='/etc/ipa/ca.crt') }}"

    - name: Confirm HBAC access would be granted
      ansible.builtin.set_fact:
        access_result: "{{ lookup('eigenstate.ipa.hbacrule',
                            deploy_identity,
                            operation='test',
                            targethost=target_host,
                            service='sshd',
                            server='idm-01.corp.example.com',
                            kerberos_keytab='/runner/env/ipa/admin.keytab',
                            verify='/etc/ipa/ca.crt') }}"

    - name: Assert policy is ready
      ansible.builtin.assert:
        that:
          - sudo_rule.exists
          - sudo_rule.enabled
          - not access_result.denied
        fail_msg: "IdM policy does not match the maintenance workflow boundary."
```

### Scheduled static secret update

```yaml
- name: Rotate a shared application secret
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Generate replacement secret
      ansible.builtin.set_fact:
        new_secret: "{{ lookup('community.general.random_string', length=32, special=false) }}"
      no_log: true

    - name: Archive replacement in IdM vault
      eigenstate.ipa.vault_write:
        name: app-secret
        state: archived
        shared: true
        data: "{{ new_secret }}"
        server: idm-01.corp.example.com
        kerberos_keytab: /runner/env/ipa/admin.keytab
        verify: /etc/ipa/ca.crt
      no_log: true
```

## Where The Official IdM Collections Fit

Use the official collections when the job is primarily object management rather
than lookup-driven decision making.

Typical examples:

- host creation and enrollment
- user, group, HBAC, sudo, or DNS CRUD
- certificate revocation
- large structural IdM configuration roles

Use `eigenstate.ipa` when the job is primarily:

- inventory shaping
- secret retrieval or vault mutation
- state inspection
- live access testing
- pre-flight gating
- controller-side orchestration around IdM state

## Guardrails

To keep the docs and the workflows clear:

- keep EE dependency detail here, not copied into every plugin page
- keep exact parameter reference in plugin pages
- keep cross-plugin flow in use-case pages and collection-wide guides
- do not describe AAP as if it creates dynamic secret leases; it schedules and packages static workflows
- do not describe `hostvars_enabled: false` as "empty hostvars"; it only stops host attribute export from IdM host objects

{% endraw %}

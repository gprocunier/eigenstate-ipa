---
layout: default
title: User Lease Demo
---

{% raw %}

# User Lease Demo

Related docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-plugin.html"><kbd>&nbsp;&nbsp;USER LEASE PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-capabilities.html"><kbd>&nbsp;&nbsp;USER LEASE CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-use-cases.html"><kbd>&nbsp;&nbsp;USER LEASE USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-rbac-setup.html"><kbd>&nbsp;&nbsp;USER LEASE RBAC SETUP&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>&nbsp;&nbsp;EPHEMERAL ACCESS CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

## Purpose

This recording shows the practical behavior boundary for
`eigenstate.ipa.user_lease` with a delegated operator and a temporary user.
It is intentionally focused on the visible login path, not on setup or
recording internals.

This page documents what the published cast shows on screen. It does not keep
the recording helper bundle as part of the published repo material.

The observable flow is:

- `jdoe` authenticates as the delegated lease owner on `bastion-01`
- `jdoe` opens a short lease for `jdoe-autobot`
- `jdoe` retrieves `jdoe-autobot`'s password from the IdM vault
- `jdoe-autobot` gets a fresh Kerberos ticket in a dedicated cache
- `jdoe-autobot` uses that lease for both real SSH access and a simple ad hoc
  Ansible action on `mirror-registry`
- after the lease expires, a fresh `kinit` for `jdoe-autobot` fails

## Recording Artifact

- setting: `cloud-user` shell on `bastion-01.workshop.lan`
- identities shown:
  - delegated operator: `jdoe@WORKSHOP.LAN`
  - leased user: `jdoe-autobot@WORKSHOP.LAN`
- target host used during the lease: `mirror-registry.workshop.lan`

## Embedded Demo

<div
  data-asciinema-src="/eigenstate-ipa/user-lease.cast"
  data-asciinema-poster="npt:0:08"
  data-asciinema-speed="1.5"
  data-asciinema-idle-time-limit="5"
  data-asciinema-terminal-font-family="'MesloGL Nerd Font Mono', 'MesloLGL Nerd Font Mono', 'Red Hat Mono', Consolas, monospace"
  data-asciinema-terminal-font-size="10pt"
  data-asciinema-cols="132"
  data-asciinema-rows="40"
></div>

## What The Demo Proves

The recording demonstrates five operational points:

1. `user_lease` moves the access cutoff into IdM by setting expiry on an
   existing user principal.
2. The leased user's password can stay in an IdM vault and be retrieved only
   when the operator needs to open the access window.
3. While the lease is valid, the leased user can obtain a fresh TGT and use it
   for normal GSSAPI SSH access.
4. The same leased identity can also drive a simple remote Ansible action,
   not just an interactive shell.
5. After the lease boundary passes, a fresh `kinit` fails with an IdM expiry
   error.

The key point is that the access boundary is enforced by IdM. The recording
does not rely on cleanup alone, and it proves both interactive and automation
use before showing the post-expiry failure.

## Sequence In The Recording

### 1. Prepare a clean workspace and authenticate as the delegated operator

The recording starts by creating a temporary workspace, clearing the dedicated
leased-user cache path, and exporting the cache location used later:

```bash
mkdir -p /tmp/demo
rm -f /tmp/krb5cc_jdoe-autobot_demo
export LEASE_CCACHE=FILE:/tmp/krb5cc_jdoe-autobot_demo
```

It then authenticates as the delegated operator:

```bash
kinit jdoe@WORKSHOP.LAN
klist
```

This establishes that the operator context is `jdoe`, not `admin`, before any
lease change is made.

### 2. Open the lease

The recording runs a short Ansible play that opens a brief lease for
`jdoe-autobot` and prints the resulting boundary.

The important observable is the returned lease boundary:

```text
Lease for jdoe-autobot ends at 20260420191557Z
```

### 3. Retrieve the leased user's password from IdM vault

The delegated operator retrieves the vaulted credential into a temporary file:

```bash
ipa vault-retrieve jdoe-autobot-cred --user=jdoe \
  --out=/tmp/demo/jdoe-autobot.pass
chmod 600 /tmp/demo/jdoe-autobot.pass
```

The recording shows the vault retrieval banner, confirming that the leased
credential came from IdM vault rather than from inventory or playbook vars.

### 4. Authenticate as the leased user

The operator uses that vaulted password to obtain a fresh TGT for
`jdoe-autobot` in a dedicated file-backed cache:

```bash
KRB5CCNAME=$LEASE_CCACHE kinit jdoe-autobot@WORKSHOP.LAN
KRB5CCNAME=$LEASE_CCACHE klist
```

The visible `klist` output shows:

```text
Ticket cache: FILE:/tmp/krb5cc_jdoe-autobot_demo
Default principal: jdoe-autobot@WORKSHOP.LAN
```

That proves the leased account can still obtain fresh initial credentials while
the lease is open.

### 5. Use the leased account for a real SSH login

The recording performs a real GSSAPI SSH login to `mirror-registry`:

```bash
KRB5CCNAME=$LEASE_CCACHE \
  ssh -o GSSAPIAuthentication=yes \
  jdoe-autobot@mirror-registry.workshop.lan
```

Inside the session, the recording shows:

```bash
whoami
hostnamectl --static
pwd
ls -ald $HOME
exit
```

The observed results are:

```text
jdoe-autobot
mirror-registry.workshop.lan
/home/jdoe-autobot
drwx------. ... /home/jdoe-autobot
```

This proves the lease is sufficient for a real host login and that the leased
user has a normal home directory on the target.

### 6. Use the same lease for a simple ad hoc Ansible action

The recording then reuses the same leased Kerberos cache for an ad hoc Ansible
run against the same host:

```bash
KRB5CCNAME=$LEASE_CCACHE \
  ansible mirror-registry.workshop.lan \
  -e ansible_user=jdoe-autobot \
  -m shell -a 'whoami; echo $HOME'
```

The important output is:

```text
mirror-registry.workshop.lan | CHANGED | rc=0 >>
jdoe-autobot
/home/jdoe-autobot
```

That extends the proof beyond interactive SSH: the leased identity is also
usable for a basic automation action while the lease remains valid.

### 7. Destroy the leased cache and wait for expiry

After the SSH and ad hoc Ansible checks, the recording destroys the leased
ticket cache and waits long enough for the short lease to pass:

```bash
KRB5CCNAME=$LEASE_CCACHE kdestroy
sleep 70
```

### 8. Attempt a fresh login after expiry

The recording then retries:

```bash
KRB5CCNAME=$LEASE_CCACHE \
  kinit jdoe-autobot@WORKSHOP.LAN
```

The observed result is:

```text
kinit: Client's entry in database has expired while getting initial credentials
```

That is the actual proof point. A fresh Kerberos login fails because IdM has
already expired the principal.

## What The Demo Does Not Claim

The recording does not claim any of these:

- that `user_lease` revokes already-issued Kerberos tickets
- that the vaulted password disappears at the same instant the lease expires
- that a normal user principal should use the collection's service-principal or
  keytab lifecycle patterns
- that this exact recorded flow is the only supported validation path

The demo is narrower and more practical:

- while the lease is open, the leased user can get a fresh TGT, SSH in, and run
  a simple ad hoc Ansible action
- after the lease expires, a fresh `kinit` fails with an IdM expiry error

## Why This Demo Exists

This recording addresses two common practical questions about `user_lease`:

> Does `user_lease` only affect a lab playbook, or does it actually govern
> direct user access?

The recording answers that by showing both a real SSH login and a real ad hoc
Ansible action before expiry, then a failed fresh `kinit` after expiry.

## Appendix: `open-lease` Playbook

The recorded lease-open step is driven by a very small local playbook. This is
the helper shape used to open the short `user_lease` window and print the lease
boundary before vault retrieval, leased-user `kinit`, SSH, and the ad hoc
Ansible check:

```yaml
#!/usr/bin/ansible-playbook
---
- name: Open the demo lease
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    lease_duration: "{{ lookup('env', 'LEASE_DURATION') | default('00:02', true) }}"
    lease_user: "{{ lookup('env', 'LEASE_USER') | default('jdoe-autobot', true) }}"
    operator_user: "{{ lookup('env', 'OPERATOR_USER') | default('jdoe', true) }}"
    lease_group: "{{ lookup('env', 'GROUP') | default('doe-corp-services', true) }}"
    ipa_server: "{{ lookup('env', 'IPA_SERVER') | default('idm-01.workshop.lan', true) }}"

  tasks:
    - name: Open a short user lease
      eigenstate.ipa.user_lease:
        username: "{{ lease_user }}"
        principal_expiration: "{{ lease_duration }}"
        password_expiration_matches_principal: true
        require_groups:
          - "{{ lease_group }}"
        server: "{{ ipa_server }}"
        ipaadmin_principal: "{{ operator_user }}"
        verify: /etc/ipa/ca.crt
      register: lease_state

    - name: Show the lease boundary
      ansible.builtin.debug:
        msg: "Lease for {{ lease_user }} ends at {{ lease_state.lease_end }}"
```

## Where To Go Next

- read <a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-capabilities.html"><kbd>USER LEASE CAPABILITIES</kbd></a>
  if the question is whether this boundary fits your access model
- read <a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-rbac-setup.html"><kbd>USER LEASE RBAC SETUP</kbd></a>
  if the question is delegated operator design
- read <a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-use-cases.html"><kbd>USER LEASE USE CASES</kbd></a>
  if you want the corresponding playbook patterns

{% endraw %}

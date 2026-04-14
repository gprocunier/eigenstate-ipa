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

The recording is intentionally not an all-in-one automation proof. It shows the
actual operator motions that matter:

- a human operator authenticates as the delegated lease owner
- the operator opens a short `user_lease` window
- the operator retrieves the temporary user's vaulted password
- the temporary user authenticates and logs in over SSH while the lease is open
- the operator destroys the Kerberos cache and waits for expiry
- a fresh `kinit` fails after the lease ends

That makes the recording useful when someone needs to understand the behavior
boundary rather than just see one green playbook.

## Recording Artifact

- setting: `cloud-user` shell on `bastion-01.workshop.lan`
- identities shown:
  - delegated operator: `jdoe@WORKSHOP.LAN`
  - leased user: `jdoe-autobot@WORKSHOP.LAN`

## Embedded Demo

<div
  data-asciinema-src="/eigenstate-ipa/user-lease.cast"
  data-asciinema-poster="npt:0:08"
  data-asciinema-speed="1.5"
  data-asciinema-cols="132"
  data-asciinema-rows="40"
></div>

<noscript>
  <img src="./user-lease.svg" alt="Static preview of the recorded user lease demo" />
</noscript>

## What The Demo Proves

The recording demonstrates the practical Approach A model:

1. `user_lease` controls the IdM expiry boundary for an existing user.
2. The leased user's password can live in an IdM vault instead of in the
   playbook or inventory.
3. The leased user can authenticate and SSH normally while the lease is valid.
4. The same password does not bypass the cutoff after
   `krbPrincipalExpiration` and `krbPasswordExpiration` are in the past.
5. A fresh login attempt fails after expiry even though the operator still has
   the vaulted password file.

This is the key operational point: the password remains the same string, but it
stops being usable for a fresh Kerberos login once the IdM lease boundary has
passed.

## Sequence In The Recording

### 1. Start clean and authenticate as the delegated operator

The recording begins by destroying any existing Kerberos cache, then running:

```bash
kinit jdoe@WORKSHOP.LAN
klist
```

This proves the operator context is `jdoe`, not `admin` and not an unrelated
stale cache.

### 2. Open the lease

The recording runs a small `open-lease` play that sets a short relative lease
on `jdoe-autobot` and prints the end time.

The important observable is the returned lease boundary, for example:

```text
Lease for jdoe-autobot ends at 20260413062513Z
```

### 3. Retrieve the leased user's password from IdM vault

The operator retrieves the vaulted credential into a temporary file:

```bash
ipa vault-retrieve jdoe-autobot-cred --user=jdoe --out=$HOME/jdoe-autobot.pass
chmod 600 $HOME/jdoe-autobot.pass
```

In this model, the retrieved file contains the literal password string for
`jdoe-autobot`. That is why the demo also treats the file as sensitive and uses
it only long enough to authenticate.

### 4. Authenticate as the leased user

The operator then uses the vaulted password to get a TGT for
`jdoe-autobot` into a dedicated file-backed cache:

```bash
KRB5CCNAME=FILE:/tmp/krb5cc_jdoe_autobot_demo \
  bash -lc 'kinit jdoe-autobot@WORKSHOP.LAN < $HOME/jdoe-autobot.pass && klist'
```

This proves the account is live during the lease window.

### 5. SSH to bastion as the leased user

The recording then performs a real GSSAPI SSH login:

```bash
KRB5CCNAME=FILE:/tmp/krb5cc_jdoe_autobot_demo \
  ssh -o GSSAPIAuthentication=yes \
      -o PreferredAuthentications=gssapi-with-mic \
      -o PubkeyAuthentication=no \
      -o PasswordAuthentication=no \
      -o KbdInteractiveAuthentication=no \
      jdoe-autobot@bastion-01.workshop.lan
```

Inside the session, the recording shows:

```bash
whoami
uname -a
exit
```

The important proof is that `whoami` returns `jdoe-autobot`.

### 6. Destroy the leased cache and wait for expiry

After logout, the recording destroys the file-backed cache and waits:

```bash
KRB5CCNAME=FILE:/tmp/krb5cc_jdoe_autobot_demo kdestroy || true
sleep 50
```

The exact wait time only needs to exceed the recorded lease window.

### 7. Attempt a fresh login after expiry

The recording then retries:

```bash
KRB5CCNAME=FILE:/tmp/krb5cc_jdoe_autobot_demo \
  bash -lc 'kinit jdoe-autobot@WORKSHOP.LAN < $HOME/jdoe-autobot.pass'; echo "rc=$?"
```

The observed result is:

```text
kinit: Client's entry in database has expired while getting initial credentials
rc=1
```

That is the actual proof that the lease cutoff is enforced by IdM.

## What The Demo Does Not Claim

The recording does not claim any of these:

- that `user_lease` revokes already-issued Kerberos tickets
- that the password file becomes cryptographically invalid after expiry
- that a normal user principal can use the collection's `keytab` workflow
- that the all-in-one play is the only supported way to validate the behavior

The demo is narrower and more practical:

- while the lease is open, the leased user can get a fresh TGT and SSH in
- after the lease expires, a fresh `kinit` fails

## Why This Demo Exists

This recording helps with the most common practical confusion around
`user_lease`:

> If the operator can still retrieve the leased user's password, why can they
> not just keep logging in?

The answer is that the password is only one part of the login path. For a fresh
Kerberos-backed login, the KDC must also agree that the principal is still
valid. `user_lease` moves that validation boundary into IdM itself.

## Helper Files

The recording uses two small helper files from the bastion demo directory
`~/user-lease-demo`.

### `setup-autobot-credential.sh`

This helper appears in the demo because the manual lease flow assumes
`jdoe-autobot` already has a vaulted credential. It seeds a fresh random
password for `jdoe-autobot` and archives it into `jdoe`'s IdM vault before the
visible lease-open / login / expiry sequence starts.

```bash
#!/usr/bin/env bash
set -euo pipefail

# LAB_DEFAULT_PASSWORD is the IPA admin password used to seed the demo resources.
: "${LAB_DEFAULT_PASSWORD:?set LAB_DEFAULT_PASSWORD in the environment}"

IPA_SERVER="${IPA_SERVER:-idm-01.workshop.lan}"
REALM="${REALM:-WORKSHOP.LAN}"
AUTOBOT_USER="${AUTOBOT_USER:-jdoe-autobot}"
GROUP="${GROUP:-doe-corp-services}"
VAULT_OWNER="${VAULT_OWNER:-jdoe}"
VAULT_NAME="${VAULT_NAME:-jdoe-autobot-cred}"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "missing required command: $1" >&2
    exit 69
  }
}

require_cmd kinit
require_cmd ipa
require_cmd mktemp
require_cmd shred
require_cmd openssl

NEW_PASS="$(openssl rand -hex 16)"
TMPFILE=""

cleanup() {
  if [[ -n "${TMPFILE}" && -e "${TMPFILE}" ]]; then
    shred -u "${TMPFILE}" || rm -f "${TMPFILE}"
  fi
  unset NEW_PASS
}
trap cleanup EXIT

echo "==> Authenticating as admin"
printf '%s\n' "${LAB_DEFAULT_PASSWORD}" | kinit "admin@${REALM}" >/dev/null

ipa user-show "${AUTOBOT_USER}" >/dev/null
ipa group-show "${GROUP}" --all | grep -q "Member users:.*${AUTOBOT_USER}"

echo "==> Setting a random password on ${AUTOBOT_USER}"
printf '%s\n%s\n' "${NEW_PASS}" "${NEW_PASS}" | ipa passwd "${AUTOBOT_USER}" >/dev/null

echo "==> Switching to ${VAULT_OWNER} for vault ownership"
kdestroy -A >/dev/null 2>&1 || true
printf '%s\n' "${LAB_DEFAULT_PASSWORD}" | kinit "${VAULT_OWNER}@${REALM}" >/dev/null

ipa vault-add "${VAULT_NAME}" --type=standard >/dev/null 2>&1 || true

TMPFILE="$(mktemp -p /dev/shm "${AUTOBOT_USER}.cred.XXXXXX")"
chmod 600 "${TMPFILE}"
printf '%s' "${NEW_PASS}" > "${TMPFILE}"

echo "==> Archiving the credential to ${VAULT_OWNER}'s vault"
ipa vault-archive "${VAULT_NAME}" --in="${TMPFILE}" >/dev/null

echo "==> Result"
ipa user-show "${AUTOBOT_USER}" --all | grep -E 'User login|User password expiration|Kerberos principal expiration|Password:|Kerberos keys available|Member of groups'
echo "Vault name: ${VAULT_NAME}"
echo "Vault owner: ${VAULT_OWNER}"
```

### `open-lease`

This helper appears in the demo because the manual flow starts with the
operator opening a short `user_lease` window for `jdoe-autobot`. It keeps that
step small and prints the lease end time before vault retrieval, `kinit`, and
SSH.

```yaml
#!/usr/bin/ansible-playbook
---
- hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Open a 2 minute lease for jdoe-autobot
      eigenstate.ipa.user_lease:
        username: jdoe-autobot
        principal_expiration: "00:02"
        password_expiration_matches_principal: true
        require_groups:
          - doe-corp-services
        server: idm-01.workshop.lan
        ipaadmin_principal: jdoe
        verify: /etc/ipa/ca.crt
      register: lease_state

    - ansible.builtin.debug:
        msg: "Lease for jdoe-autobot ends at {{ lease_state.lease_end }}"
```

## Where To Go Next

- read <a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-capabilities.html"><kbd>USER LEASE CAPABILITIES</kbd></a>
  if the question is whether this boundary fits your access model
- read <a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-rbac-setup.html"><kbd>USER LEASE RBAC SETUP</kbd></a>
  if the question is delegated operator design
- read <a href="https://gprocunier.github.io/eigenstate-ipa/user-lease-use-cases.html"><kbd>USER LEASE USE CASES</kbd></a>
  if you want the corresponding playbook patterns

{% endraw %}

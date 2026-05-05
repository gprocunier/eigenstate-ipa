---
layout: default
title: AAP EE Troubleshooting
description: >-
  Troubleshooting notes for the eigenstate.ipa IdM execution environment.
---

{% raw %}

# AAP EE Troubleshooting

## `ipa-getkeytab` Missing

Install the package that provides `ipa-getkeytab`. On RHEL-based EEs, start
with `ipa-client` in `bindep.txt`, rebuild the image, and rerun the smoke
playbook.

## `ipalib` Import Fails

Make sure `python3-ipalib` and `python3-ipaclient` are available from the RPM
repositories used during the build. Prefer RPMs over PyPI packages for the
default AAP-supported image path.

## `kinit` Missing

Add `krb5-workstation` to `bindep.txt` and rebuild. The collection expects
Kerberos tooling in the EE for keytab-backed and password-backed ticket
acquisition.

## CA File Missing In `/etc/ipa/ca.crt`

Mount the IdM CA certificate into the job runtime or bake the trusted CA into a
site-specific image. The default scaffold creates `/etc/ipa` with group-writable
permissions for AAP runtime mounts; it does not include customer CA material.

## `KRB5CCNAME` Or Credential Cache Issues

Only set `KRB5CCNAME` when the workflow intentionally manages a custom cache.
If jobs reuse a cache path, clear it at job start or use a job-unique location.
Prefer keytab-backed authentication for repeatable Controller runs.

## Clock Skew

Kerberos is sensitive to time. Verify that Controller nodes, execution nodes,
IdM servers, and managed hosts use reliable time synchronization.

## DNS Or Realm Discovery Failure

Check that the EE can resolve IdM hosts and realm discovery records from the
execution node network. A working image cannot compensate for missing DNS,
blocked IdM APIs, or incorrect realm names.

## Registry Pull Denied

Confirm the image was pushed to the registry used by Controller and that the
execution node has a valid pull credential. The role does not manage registry
login by design.

## Collection Not Found In EE

Run:

```bash
ansible-playbook playbooks/aap-ee-smoke.yml \
  -e eigenstate_ee_image=registry.example.com/automation/eigenstate-idm-ee:dev
```

If `ansible-doc` cannot find `eigenstate.ipa`, inspect the rendered
`requirements.yml`, the automation hub source, and any private hub token
configuration used at build time.

## `ansible-doc eigenstate.ipa.*` Fails

Use the exact plugin type:

```bash
ansible-doc -t inventory eigenstate.ipa.idm
ansible-doc -t lookup eigenstate.ipa.vault
ansible-doc -t lookup eigenstate.ipa.keytab
ansible-doc -t module eigenstate.ipa.vault_write
ansible-doc -t module eigenstate.ipa.user_lease
```

If type-specific lookup fails, rebuild the image and verify the collection
version in the rendered `requirements.yml`.

{% endraw %}

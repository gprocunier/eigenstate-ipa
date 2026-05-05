# eigenstate.ipa IdM Execution Environment

This build context creates an Ansible Automation Platform execution environment
for IdM-backed automation with `eigenstate.ipa`.

It includes the `eigenstate.ipa`, `freeipa.ansible_freeipa`,
`community.general`, and `community.crypto` collections, plus RHEL packages for
FreeIPA client libraries, Kerberos, `ipa-getkeytab`, and common troubleshooting
tools.

Build it manually:

```bash
ansible-builder build -t localhost/eigenstate-idm-ee:dev
```

Smoke test a built image from the collection checkout:

```bash
ansible-playbook playbooks/aap-ee-smoke.yml \
  -e eigenstate_ee_image=localhost/eigenstate-idm-ee:dev
```

Private automation hub tokens and registry credentials do not belong in this
directory. Keep them in Controller credentials, environment variables, or a
local `ansible.cfg` that is not committed. Use `ansible.cfg.example` as the
shape for collection paths and inventory plugin enablement only.

In AAP, mount IdM runtime material through credentials or job settings:

- CA certificate: `/etc/ipa/ca.crt`
- service or admin keytab: `/runner/env/ipa/<principal>.keytab`
- optional Kerberos cache: set `KRB5CCNAME` if your workflow manages a custom
  credential cache

This default scaffold does not include OpenShift/Kubernetes collections,
Controller configuration-as-code content, registry login material, IPA server
secrets, or a pinned base-image digest. Add those only when your environment
requires them.

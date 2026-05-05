# aap_execution_environment

Render, optionally build, optionally smoke-test, optionally push, and
optionally register an Ansible Automation Platform execution environment for
`eigenstate.ipa`.

The role prepares the runtime for IdM-backed automation. It does not configure
an IdM server and it does not manage registry login credentials.

## Requirements

- `ansible-builder` for image builds
- `podman` or another compatible container runtime for smoke and push
- access to the selected base image
- `ansible.controller` only when Controller registration is enabled

## Variables

Common variables:

```yaml
eigenstate_ee_name: eigenstate-idm-ee
eigenstate_ee_tag: latest
eigenstate_ee_output_dir: "{{ playbook_dir }}/../build/{{ eigenstate_ee_name }}"
eigenstate_ee_image: "localhost/{{ eigenstate_ee_name }}:{{ eigenstate_ee_tag }}"
eigenstate_ee_base_image: "registry.redhat.io/ansible-automation-platform-26/ee-minimal-rhel9:latest"
eigenstate_ee_collection_version: ">=1.11.0"
```

Optional collection toggles:

```yaml
eigenstate_ee_include_kubernetes: false
eigenstate_ee_include_okd: false
eigenstate_ee_include_ansible_controller: false
```

Actions are explicit:

```yaml
eigenstate_ee_render: true
eigenstate_ee_build: false
eigenstate_ee_smoke: false
eigenstate_ee_push: false
eigenstate_ee_register_controller: false
```

Registry and Controller variables:

```yaml
eigenstate_ee_registry_image: ""
eigenstate_ee_registry_tls_verify: true
eigenstate_controller_host: ""
eigenstate_controller_oauthtoken: ""
eigenstate_controller_organization: ""
eigenstate_controller_ee_pull: missing
```

## Examples

Render only:

```bash
ansible-playbook playbooks/aap-ee-render.yml \
  -e eigenstate_ee_output_dir=/tmp/eigenstate-idm-ee
```

Render and build:

```bash
ansible-playbook playbooks/aap-ee-build.yml \
  -e eigenstate_ee_output_dir=/tmp/eigenstate-idm-ee \
  -e eigenstate_ee_image=localhost/eigenstate-idm-ee:dev
```

Render, build, and smoke:

```bash
ansible-playbook playbooks/aap-ee-build.yml \
  -e eigenstate_ee_output_dir=/tmp/eigenstate-idm-ee \
  -e eigenstate_ee_image=localhost/eigenstate-idm-ee:dev

ansible-playbook playbooks/aap-ee-smoke.yml \
  -e eigenstate_ee_image=localhost/eigenstate-idm-ee:dev
```

Push after authenticating with your runtime:

```bash
podman login registry.example.com
ansible-playbook playbooks/aap-ee-push.yml \
  -e eigenstate_ee_image=localhost/eigenstate-idm-ee:dev \
  -e eigenstate_ee_registry_image=registry.example.com/automation/eigenstate-idm-ee:dev
```

Register in Controller with token auth:

```bash
ansible-playbook playbooks/aap-ee-register-controller.yml \
  -e eigenstate_controller_host=https://controller.example.com \
  -e eigenstate_controller_oauthtoken="${CONTROLLER_OAUTH_TOKEN}" \
  -e eigenstate_controller_organization=Default \
  -e eigenstate_ee_registry_image=registry.example.com/automation/eigenstate-idm-ee:dev
```

## Disconnected Builds

Mirror the base image to a local registry, mirror Galaxy content into private
automation hub, and provide RPM repositories through Satellite or an equivalent
internal source. Override `eigenstate_ee_base_image` with the mirrored image and
use an untracked local `ansible.cfg` for private automation hub access.

## Security Notes

Do not commit registry passwords, automation hub tokens, IPA passwords,
keytabs, vault passwords, private keys, or pull secrets. Controller
registration tasks use `no_log: true` for token and password-bearing inputs.

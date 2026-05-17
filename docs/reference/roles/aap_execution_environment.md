---
layout: default
title: AAP Execution Environment role reference
diataxis: reference
diataxis_type: reference
audience: Operators and maintainers looking up exact facts
outcome: Exact source-verified reference for this Ansible collection surface.
authority_boundary:
  - collection
workflow_boundary: read-only
evidence_shape:
  - ansible-doc
public_status: rewritten
source_material:
  - ../../roles/aap_execution_environment/README.md
last_verified: 2026-05-16
---

# AAP Execution Environment role reference

| Role | Purpose | Defaults | Argument spec |
| --- | --- | --- | --- |
| `aap_execution_environment` | Render, optionally build, optionally smoke-test, optionally push, and | `roles/aap_execution_environment/defaults/main.yml` | `roles/aap_execution_environment/meta/argument_specs.yml` |

## Variables

### `aap_execution_environment`

| Default variable | Default value |
| --- | --- |
| `eigenstate_controller_ee_name` | `{{ eigenstate_ee_name }}` |
| `eigenstate_controller_ee_pull` | `missing` |
| `eigenstate_controller_host` | `` |
| `eigenstate_controller_oauthtoken` | `` |
| `eigenstate_controller_organization` | `` |
| `eigenstate_controller_password` | `` |
| `eigenstate_controller_username` | `` |
| `eigenstate_controller_validate_certs` | `true` |
| `eigenstate_ee_base_image` | `registry.redhat.io/ansible-automation-platform-26/ee-minimal-rhel9:latest` |
| `eigenstate_ee_build` | `false` |
| `eigenstate_ee_build_context` | `context` |
| `eigenstate_ee_builder_binary` | `ansible-builder` |
| `eigenstate_ee_collection_version` | `>=1.18.0` |
| `eigenstate_ee_container_runtime` | `podman` |
| `eigenstate_ee_image` | `localhost/{{ eigenstate_ee_name }}:{{ eigenstate_ee_tag }}` |
| `eigenstate_ee_include_ansible_controller` | `false` |
| `eigenstate_ee_include_community_crypto` | `true` |
| `eigenstate_ee_include_community_general` | `true` |
| `eigenstate_ee_include_freeipa_collection` | `true` |
| `eigenstate_ee_include_kubernetes` | `false` |
| `eigenstate_ee_include_okd` | `false` |
| `eigenstate_ee_name` | `eigenstate-idm-ee` |
| `eigenstate_ee_output_dir` | `{{ playbook_dir }}/../build/{{ eigenstate_ee_name }}` |
| `eigenstate_ee_push` | `false` |
| `eigenstate_ee_python_packages` | `` |
| `eigenstate_ee_register_controller` | `false` |
| `eigenstate_ee_registry` | `` |
| `eigenstate_ee_registry_image` | `` |
| `eigenstate_ee_registry_tls_verify` | `true` |
| `eigenstate_ee_render` | `true` |
| `eigenstate_ee_smoke` | `false` |
| `eigenstate_ee_system_packages` | `findutils [platform:rpm], gzip [platform:rpm], ipa-client [platform:rpm], jq [platform:rpm], krb5-workstation [platform:rpm], openssh-clients [platform:rpm], openssl [platform:rpm], python3-ipaclient [platform:rpm], python3-ipalib [platform:rpm], python3-pip [platform:rpm], python3-setuptools [platform:rpm], tar [platform:rpm], which [platform:rpm]` |
| `eigenstate_ee_tag` | `latest` |

## Related Pages

- [Playbook reference](../playbooks.html)
- [Authority boundaries](../../explanation/authority-boundaries.html)

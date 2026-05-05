---
layout: default
title: Sealed Artifact Delivery Role
description: >-
  Safely retrieve, stage, and optionally hand off opaque sealed artifacts from
  IdM vaults.
---

{% raw %}

# Sealed Artifact Delivery Role

`sealed_artifact_delivery` treats IdM vault payloads as sensitive opaque
artifacts. The role can validate metadata, retrieve the payload, stage it with
restrictive permissions, run an optional `argv` handoff, and remove the staged
file after handoff.

## Minimal Preflight

```yaml
eigenstate_sealed_state: preflight
eigenstate_sealed_vault_name: app-bootstrap-bundle
eigenstate_sealed_server: idm-01.example.com
eigenstate_sealed_kerberos_keytab: /runner/env/ipa/admin.keytab
```

## Shared Vault Staging

```yaml
eigenstate_sealed_state: staged
eigenstate_sealed_scope: shared
eigenstate_sealed_vault_name: app-bootstrap-bundle
eigenstate_sealed_output_path: /runner/artifacts/app-bootstrap.bundle
```

Payload retrieval and copy tasks use `no_log` by default.

## Target Staging

```yaml
eigenstate_sealed_target_host: "{{ inventory_hostname }}"
eigenstate_sealed_output_path: /var/lib/app/bootstrap.bundle
eigenstate_sealed_output_mode: "0600"
```

## Handoff

```yaml
eigenstate_sealed_state: handed_off
eigenstate_sealed_handoff_enabled: true
eigenstate_sealed_handoff_argv:
  - /usr/local/bin/apply-bootstrap
  - /var/lib/app/bootstrap.bundle
eigenstate_sealed_cleanup_after_handoff: true
```

The role deliberately does not unseal, parse, or validate the payload content.
It only handles safe retrieval, staging, handoff, cleanup, and metadata reports.

{% endraw %}

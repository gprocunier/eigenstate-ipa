# sealed_artifact_delivery

Retrieves an opaque sealed artifact from an IdM vault, stages it with
restrictive file permissions, optionally runs a handoff command with
`command.argv`, and emits metadata-only reports.

The role treats vault payload bytes as secret material. Retrieval, staging,
handoff, and cleanup tasks use `eigenstate_sealed_no_log: true` by default.
Reports never include payload content.

## Required Variables

```yaml
eigenstate_sealed_vault_name: app-bootstrap-bundle
eigenstate_sealed_server: idm-01.example.com
```

For staged or handed-off states:

```yaml
eigenstate_sealed_state: staged
eigenstate_sealed_output_path: /runner/artifacts/app-bootstrap.bundle
```

## Common States

- `preflight`: validate inputs and inspect vault metadata only.
- `staged`: retrieve the payload and write it to `eigenstate_sealed_output_path`.
- `handed_off`: stage the payload, run an optional `argv` handoff command, and
  optionally remove the staged file.
- `absent`: remove the staged file path.

## Scope Examples

Shared vault:

```yaml
eigenstate_sealed_scope: shared
```

User vault:

```yaml
eigenstate_sealed_scope: user
eigenstate_sealed_username: appuser
```

Service vault:

```yaml
eigenstate_sealed_scope: service
eigenstate_sealed_service: HTTP/app.example.com@EXAMPLE.COM
```

## Handoff

Use `argv`, not shell strings:

```yaml
eigenstate_sealed_state: handed_off
eigenstate_sealed_handoff_enabled: true
eigenstate_sealed_handoff_argv:
  - /usr/local/bin/consume-bundle
  - /runner/artifacts/app-bootstrap.bundle
```

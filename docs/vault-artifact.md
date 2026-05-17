---
layout: default
title: Vault artifact custody
diataxis: how-to
diataxis_type: how-to
audience: Operators storing opaque artifacts in IdM vaults
outcome: Write, read, digest, and read-back verify generic vault artifacts.
authority_boundary:
  - idm
  - collection
workflow_boundary: mutating
evidence_shape:
  - command-output
public_status: new
last_verified: 2026-05-16
---
{% raw %}

# Vault artifact custody

Use `eigenstate.ipa.vault_artifact` when the workflow needs generic custody for
an opaque artifact such as a bootstrap bundle, certificate bundle, or rotation
evidence packet.

The module does not sign, verify, parse, or interpret the payload. It writes or
reads the vault value, calculates SHA-256, and can verify a read-back digest.

```yaml
- name: Archive a bootstrap bundle and verify read-back
  eigenstate.ipa.vault_artifact:
    name: app-bootstrap-bundle
    state: present
    shared: true
    payload_file: ./bootstrap-bundle.json
    server: idm-01.example.com
    kerberos_keytab: /runner/env/ipa/automation.keytab
    ipaadmin_principal: automation@EXAMPLE.COM
    verify: /etc/ipa/ca.crt
    read_back: true
  no_log: true
  register: artifact_write
```

Expected non-payload result fields:

```yaml
changed: true
artifact_ref: shared/app-bootstrap-bundle
artifact_sha256: 64-character-hex-digest
read_back_verified: true
vault_server: idm-01.example.com
vault_type: standard
```

Read without returning the payload:

```yaml
- name: Verify a stored evidence packet digest
  eigenstate.ipa.vault_artifact:
    name: certificate-rotation-evidence
    state: read
    shared: true
    expected_sha256: "{{ expected_digest }}"
    server: idm-01.example.com
    kerberos_keytab: /runner/env/ipa/automation.keytab
  register: artifact_read
```

Only enable `include_payload: true` inside a task that also sets
`no_log: true`.

## Release gate

The live lab gate must write an artifact, read it back, verify the digest, and
record a missing-artifact negative result.

{% endraw %}

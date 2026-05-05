# keytab_secret_render

Render Kubernetes Secret manifests for Kerberos keytab delivery to workloads.

The role expects base64-encoded keytab bytes and renders a review manifest with
the keytab value redacted by default. A payload-bearing manifest is written only
when `eigenstate_keytab_secret_write_payload_manifest: true` or
`eigenstate_keytab_secret_apply: true`.

Cluster mutation is disabled unless both conditions are true:

- `eigenstate_keytab_secret_render_only: false`
- `eigenstate_keytab_secret_apply: true`

When apply is enabled, the role requires explicit kubeconfig and context inputs.
The default CI path does not contact a cluster.

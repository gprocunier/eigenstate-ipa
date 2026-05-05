# kubernetes_secret_from_idm_vault

Render Kubernetes Secret manifests from IdM vault material with safe defaults.

The role is render-only by default. It writes a review manifest with redacted
payload values so platform teams can inspect namespace, name, labels,
annotations, and key names without exposing secret contents.

To write a payload-bearing manifest, set
`eigenstate_k8s_secret_write_payload_manifest: true`. That file is written with
mode `0600` and secret-bearing tasks use `no_log: true`.

Cluster mutation is disabled unless both conditions are true:

- `eigenstate_k8s_secret_render_only: false`
- `eigenstate_k8s_secret_apply: true`

When apply is enabled, the role requires explicit kubeconfig and context inputs.
The default CI path does not contact a cluster.

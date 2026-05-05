# kubernetes_tls_from_idm_cert

Render Kubernetes TLS Secret manifests from certificate material that has been
issued or reviewed through an IdM-centered workflow.

The default output is a review manifest with `tls.crt`, `tls.key`, and optional
`ca.crt` values redacted. A payload-bearing manifest is written only when
`eigenstate_k8s_tls_write_payload_manifest: true` or
`eigenstate_k8s_tls_apply: true`.

Cluster mutation is disabled unless both conditions are true:

- `eigenstate_k8s_tls_render_only: false`
- `eigenstate_k8s_tls_apply: true`

When apply is enabled, the role requires explicit kubeconfig and context inputs.
The default CI path does not contact a cluster.

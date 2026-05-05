# openshift_idm_oidc_validation

Render an OpenShift OAuth/OIDC configuration example and validate local evidence
for IdM-backed group and principal readiness.

The role is render-only and validation-only. It does not contact an OpenShift
cluster, Keycloak realm, or IdM server, and it does not create secrets.

## Common Variables

```yaml
eigenstate_oidc_issuer_url: "https://keycloak.example.com/realms/openshift"
eigenstate_oidc_client_id: "openshift"
eigenstate_oidc_client_secret_name: "openid-client-secret"
eigenstate_oidc_expected_groups:
  - ocp-platform-admins
  - ocp-developers
eigenstate_oidc_idm_known_groups:
  - ocp-platform-admins
  - ocp-developers
eigenstate_oidc_output_dir: "./artifacts"
```

Use `eigenstate_oidc_idm_known_groups` and
`eigenstate_oidc_idm_known_principals` as local evidence gathered from the site
inventory, an approved export, or an earlier validation job.

## Outputs

- `openshift-idm-oidc.oauth.yaml`
- `openshift-idm-oidc.json`
- `openshift-idm-oidc.md`

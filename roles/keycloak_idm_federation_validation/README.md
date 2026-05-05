# keycloak_idm_federation_validation

Validate local evidence for a Keycloak realm that federates IdM or AD identities
and emits the OIDC claims consumed by OpenShift.

The role does not contact Keycloak or IdM. It compares expected groups,
principals, federation mappers, and protocol mappers against local evidence and
renders a readiness report.

## Common Variables

```yaml
eigenstate_keycloak_realm: openshift
eigenstate_keycloak_idm_provider_alias: idm
eigenstate_keycloak_group_claim: groups
eigenstate_keycloak_expected_groups:
  - ocp-platform-admins
  - ocp-developers
eigenstate_keycloak_known_idm_groups:
  - ocp-platform-admins
  - ocp-developers
eigenstate_keycloak_output_dir: "./artifacts"
```

Use `eigenstate_keycloak_configured_mappers` and
`eigenstate_keycloak_configured_protocol_mappers` as local evidence from a
reviewed Keycloak export or a separate read-only collection job.

## Outputs

- `keycloak-idm-federation.json`
- `keycloak-idm-federation.md`

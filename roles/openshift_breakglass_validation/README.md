# openshift_breakglass_validation

Validate local evidence for an OpenShift emergency-access model backed by IdM
groups and auditable RBAC bindings.

The role does not contact OpenShift or IdM. It checks that expected groups,
principals, RBAC binding declarations, and operational controls are represented
in the local evidence supplied to the playbook.

## Common Variables

```yaml
eigenstate_breakglass_expected_groups:
  - ocp-breakglass-admins
eigenstate_breakglass_known_idm_groups:
  - ocp-breakglass-admins
eigenstate_breakglass_required_controls:
  - named IdM group for emergency administrators
  - documented approval path
  - expiry or review process
  - audited OpenShift RBAC binding
eigenstate_breakglass_output_dir: "./artifacts"
```

Keep credentials, kubeconfigs, recovery tokens, and private keys outside the
repository and outside rendered reports.

## Outputs

- `openshift-breakglass.json`
- `openshift-breakglass.md`

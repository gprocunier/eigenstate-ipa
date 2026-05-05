# idm_readiness_report

Renders deterministic IdM readiness evidence in JSON, YAML, and Markdown.
The role is read-only and consumes explicit check records supplied by inventory,
Controller survey values, or a prior discovery job.

The report object uses the schema identifier
`eigenstate.ipa/idm_readiness_report/v1`. Records must use stable check IDs and
one of `pass`, `warn`, `fail`, or `info` as the status.

```yaml
- ansible.builtin.import_role:
    name: eigenstate.ipa.idm_readiness_report
  vars:
    eigenstate_idm_readiness_report_site: prod-idm
    eigenstate_idm_readiness_report_checks:
      - id: kerberos-auth
        title: Kerberos authentication path
        status: pass
        severity: high
        evidence: Keytab authentication is configured for Controller jobs.
        recommendation: Keep the keytab under normal rotation policy.
```

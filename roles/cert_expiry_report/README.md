# cert_expiry_report

Finds IdM certificates matching an expiry or identity filter and renders JSON,
Markdown, and CSV artifacts. The role is read-only and does not mutate IdM.

## Required Variables

```yaml
eigenstate_cert_report_server: idm-01.example.com
```

At least one filter is required to avoid accidental broad CA enumeration:

```yaml
eigenstate_cert_report_valid_not_after_to: "2026-12-31"
```

## Output

Reports are written to `eigenstate_cert_report_output_dir` using
`eigenstate_cert_report_basename`:

```text
artifacts/cert-expiry-report.json
artifacts/cert-expiry-report.md
artifacts/cert-expiry-report.csv
```

## Failure Gate

Use the role as a scheduled compliance gate:

```yaml
eigenstate_cert_report_fail_on_expiring: true
eigenstate_cert_report_fail_threshold_count: 1
```

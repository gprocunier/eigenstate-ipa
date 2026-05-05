---
layout: default
title: Cert Expiry Report Role
description: >-
  Generate JSON, Markdown, and CSV reports for IdM certificates matching expiry
  or identity filters.
---

{% raw %}

# Cert Expiry Report Role

`cert_expiry_report` is a read-only reporting role. It calls
`eigenstate.ipa.cert` with `operation=find`, requires at least one filter, and
renders report artifacts for AAP job output or scheduled compliance checks.

## Expiry Window

```yaml
eigenstate_cert_report_server: idm-01.example.com
eigenstate_cert_report_valid_not_after_from: "2026-05-01"
eigenstate_cert_report_valid_not_after_to: "2026-06-01"
```

## Principal Filter

```yaml
eigenstate_cert_report_principal: HTTP/app.example.com@EXAMPLE.COM
```

## Outputs

```text
artifacts/cert-expiry-report.json
artifacts/cert-expiry-report.md
artifacts/cert-expiry-report.csv
```

## Failure Gate

```yaml
eigenstate_cert_report_fail_on_expiring: true
eigenstate_cert_report_fail_threshold_count: 1
```

Use this when an AAP scheduled job should fail if matching certificates exist.

{% endraw %}

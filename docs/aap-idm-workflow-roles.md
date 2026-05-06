---
layout: default
title: AAP IdM Workflow Roles
description: >-
  AAP-ready workflow roles that package high-value eigenstate.ipa IdM
  automation paths after the execution environment is built.
---

{% raw %}

# AAP IdM Workflow Roles

The execution environment provides the runtime. These roles provide repeatable
AAP jobs that use the collection without requiring every operator to assemble
the same workflow glue by hand.

| Role | Primary job | Safe default |
| --- | --- | --- |
| `sealed_artifact_delivery` | Retrieve and stage an opaque IdM vault artifact | preflight metadata, payload tasks under `no_log` |
| `temporary_access_window` | Preflight policy and manage `user_lease` state | preflight only |
| `cert_expiry_report` | Render IdM certificate expiry reports | read-only, filter required |

Use the roles as Controller job templates, workflow nodes, or ordinary playbook
building blocks. They are designed to run in the Eigenstate IdM execution
environment from the AAP EE quickstart.

## Security Defaults

- secret-bearing sealed artifact tasks use `no_log: true` by default
- reports contain metadata only
- handoff commands use `command.argv`, not shell strings
- certificate reporting refuses to run without at least one filter
- static validation can run without contacting IdM

## Role Docs

<a href="https://gprocunier.github.io/eigenstate-ipa/sealed-artifact-delivery-role.html"><kbd>SEALED ARTIFACT DELIVERY</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/temporary-access-window-role.html"><kbd>TEMPORARY ACCESS WINDOW</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/cert-expiry-report-role.html"><kbd>CERT EXPIRY REPORT</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-idm-workflow-validation-walkthrough.html"><kbd>VALIDATION WALKTHROUGH</kbd></a>

{% endraw %}

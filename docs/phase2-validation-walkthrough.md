---
layout: default
title: Phase 2 Validation Walkthrough
description: >-
  Concise validation path for the AAP golden-path workflow roles.
---

{% raw %}

# Phase 2 Validation Walkthrough

This path validates the three AAP-ready roles after the Eigenstate execution
environment is available.

## 1. Run Certificate Expiry Report

```bash
ansible-playbook playbooks/cert-expiry-report.yml \
  -e eigenstate_cert_report_server=idm-01.example.com \
  -e eigenstate_cert_report_valid_not_after_to=2099-12-31
```

## 2. Preflight Or Open Temporary Access

```bash
ansible-playbook playbooks/temporary-access-window.yml \
  -e eigenstate_taw_state=preflight \
  -e eigenstate_taw_username=temp-maintenance \
  -e eigenstate_taw_server=idm-01.example.com \
  -e eigenstate_taw_hbac_targethost=host01.example.com
```

## 3. Preflight Sealed Artifact Delivery

```bash
ansible-playbook playbooks/sealed-artifact-delivery.yml \
  -e eigenstate_sealed_state=preflight \
  -e eigenstate_sealed_vault_name=app-bootstrap-bundle \
  -e eigenstate_sealed_server=idm-01.example.com
```

## 4. Review Safe Reports

Each role emits metadata-only artifacts under `./artifacts` by default. Sealed
artifact reports do not include payload bytes.

## Boundary

Vault still wins for broad dynamic secret engines, lease revocation semantics,
and multi-backend secret brokering. IdM and `eigenstate.ipa` fit when the
automation boundary is already identity, Kerberos, certificate, DNS, sudo,
SELinux, and HBAC policy state held in IdM.

{% endraw %}

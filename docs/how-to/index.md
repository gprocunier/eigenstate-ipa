---
layout: default
title: How-to Guides
diataxis: orientation
diataxis_type: orientation
audience: Operators completing production tasks
outcome: Choose a task guide.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: stub
last_verified: 2026-05-17
---

# How-to Guides

This index is the routing point for the how-to section.

| Page | Outcome |
| --- | --- |
| [Use IdM as live Ansible inventory](use-idm-as-live-inventory.html) | Target automation from IdM host and policy state. |
| [Retrieve an IdM vault secret](retrieve-idm-vault-secret.html) | Retrieve vault material safely for Ansible or AAP. |
| [Manage IdM vault lifecycle](manage-idm-vault-lifecycle.html) | Create, update, archive, or delete IdM vaults. |
| [Query principal state](query-principal-state.html) | Preflight users, hosts, and service principals. |
| [Retrieve a keytab](retrieve-keytab.html) | Retrieve existing keytabs without rotation. |
| [Rotate a keytab explicitly](rotate-keytab-explicitly.html) | Rotate keytabs with explicit confirmation and evidence. |
| [Request an IdM certificate](request-idm-certificate.html) | Request certificates from CSRs and keep private keys outside the module. |
| [Issue an OTP or host enrollment password](issue-otp-or-host-enrollment-password.html) | Issue user OTP tokens or host enrollment passwords. |
| [Inspect DNS state](inspect-dns-state.html) | Inspect forward, reverse, zone-apex, and broad DNS records. |
| [Test HBAC access](test-hbac-access.html) | Use live HBAC test results as an automation gate. |
| [Inspect sudo policy](inspect-sudo-policy.html) | Inspect sudo rules, commands, and command groups. |
| [Inspect SELinux map scope](inspect-selinux-map-scope.html) | Inspect SELinux user maps and linked HBAC scope. |
| [Open a temporary access window](open-temporary-access-window.html) | Set, expire, or clear temporary user access boundaries. |
| [Render OpenShift identity evidence](render-openshift-identity-evidence.html) | Render and validate OpenShift identity evidence without mutating the cluster. |
| [Render a Kubernetes Secret from an IdM vault](render-kubernetes-secret-from-idm-vault.html) | Render review-first Kubernetes Secret manifests. |
| [Render Kubernetes TLS from an IdM certificate](render-kubernetes-tls-from-idm-cert.html) | Render review-first TLS Secret manifests. |
| [Render a keytab Secret](render-keytab-secret.html) | Render review-first keytab Secret manifests. |
| [Build a disconnected AAP execution environment](build-disconnected-aap-ee.html) | Build the execution environment for disconnected use. |
| [Generate operational evidence](generate-operational-evidence.html) | Generate readiness, certificate, keytab, temporary access, and drift reports. |
| [Migrate side-effecting lookups](migrate-side-effecting-lookups.html) | Move keytab and certificate side-effecting flows to explicit modules. |

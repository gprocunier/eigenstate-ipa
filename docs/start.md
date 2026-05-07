---
layout: default
title: Start Here
diataxis: orientation
diataxis_type: orientation
audience: Operators, platform engineers, and maintainers
outcome: Choose the right tutorial, how-to, reference, or explanation page for the job.
authority_boundary:
  - idm
  - collection
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
last_verified: 2026-05-07
---

# Start Here

Choose by the work you need to do, not by repository path.

## I Need To Learn The Shape

| Goal | Page |
| --- | --- |
| See how IdM becomes inventory | [Build your first live IdM inventory](tutorials/first-idm-inventory.html) |
| Retrieve sample vault material safely | [Retrieve your first IdM vault value](tutorials/first-vault-retrieval.html) |
| Build the AAP runtime image | [Build an AAP execution environment](tutorials/build-aap-execution-environment.html) |
| Walk through service onboarding | [Onboard a service with principal, keytab, and certificate checks](tutorials/service-onboarding-with-principal-keytab-cert.html) |
| Render review-first workload material | [Render a workload Secret from IdM material](tutorials/render-workload-secret.html) |

## I Need To Do A Production Task

| Task | Page |
| --- | --- |
| Target hosts from IdM | [Use IdM as live Ansible inventory](how-to/use-idm-as-live-inventory.html) |
| Retrieve vault material | [Retrieve an IdM vault secret](how-to/retrieve-idm-vault-secret.html) |
| Manage vault lifecycle | [Manage IdM vault lifecycle](how-to/manage-idm-vault-lifecycle.html) |
| Preflight principals | [Query principal state](how-to/query-principal-state.html) |
| Retrieve or rotate keytabs | [Retrieve a keytab](how-to/retrieve-keytab.html) or [Rotate a keytab explicitly](how-to/rotate-keytab-explicitly.html) |
| Request a certificate | [Request an IdM certificate](how-to/request-idm-certificate.html) |
| Test HBAC or inspect policy | [Test HBAC access](how-to/test-hbac-access.html), [Inspect sudo policy](how-to/inspect-sudo-policy.html), or [Inspect SELinux map scope](how-to/inspect-selinux-map-scope.html) |
| Open temporary access | [Open a temporary access window](how-to/open-temporary-access-window.html) |
| Render OpenShift or Kubernetes artifacts | [Render OpenShift identity evidence](how-to/render-openshift-identity-evidence.html) or [Render a Kubernetes Secret from an IdM vault](how-to/render-kubernetes-secret-from-idm-vault.html) |
| Produce reports | [Generate operational evidence](how-to/generate-operational-evidence.html) |

## I Need Exact Facts

Start with [Reference](reference/). It routes to:

- inventory plugin options and hostvars
- lookup plugin terms, options, modes, and returns
- module arguments, check mode, changed state, and return values
- role variables and outputs
- wrapper playbooks
- authentication, return shapes, report schemas, support, and release process

## I Need To Understand Boundaries

| Question | Page |
| --- | --- |
| What is the collection? | [What is eigenstate.ipa?](explanation/what-is-eigenstate-ipa.html) |
| Why read IdM as automation state? | [IdM as an automation state plane](explanation/idm-as-automation-state-plane.html) |
| Which system owns what? | [Authority boundaries](explanation/authority-boundaries.html) |
| Where is the secret boundary? | [Secret boundary](explanation/secret-boundary.html) |
| What are keytab and certificate risks? | [Kerberos keytab boundary](explanation/kerberos-keytab-boundary.html) and [Certificate boundary](explanation/certificate-boundary.html) |
| What remains risky? | [Security threat model](explanation/security-threat-model.html) |

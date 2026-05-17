---
layout: default
title: eigenstate.ipa
diataxis: orientation
diataxis_type: orientation
audience: IdM, Ansible, AAP, OpenShift, and platform operators
outcome: Understand what the collection does, where to start, and which boundary each workflow uses.
authority_boundary:
  - idm
  - collection
  - ansible
  - aap
workflow_boundary: read-only
evidence_shape:
  - architecture-boundary
public_status: rewritten
source_material:
  - ../README.md
  - ../llms.txt
last_verified: 2026-05-17
---

# eigenstate.ipa

`eigenstate.ipa` is an Ansible collection for Red Hat IdM / FreeIPA. It lets
automation consume live identity, host, vault, Kerberos, certificate, DNS,
sudo, SELinux map, and HBAC state without copying that state into a parallel
inventory or side-channel secret workflow.

The collection's center of gravity is simple: IdM already records useful
automation state, and Ansible should read or change that state through explicit,
reviewable surfaces.

## The 2-Minute Version

| Question | Answer |
| --- | --- |
| What problem does this solve? | IdM-managed hosts, policy, vaults, principals, keytabs, certificates, and access checks can become live Ansible inputs instead of duplicated static files. |
| What makes it credible? | The repository contains one inventory plugin, nine lookup plugins, seven modules, filter utilities, execution-environment assets, roles, wrapper playbooks, and tests. |
| What should change by default? | Read-only lookups and render-first roles should produce evidence before any workflow mutates IdM, writes key material, or applies cluster configuration. |
| Where should I start? | Use [Start Here](start.html) if you have a job to do, or [Reference](reference/) if you already know the exact surface. |

## Use With, Not Instead Of

`eigenstate.ipa` is a companion automation collection for Red Hat IdM /
FreeIPA. It does not replace `redhat.rhel_idm` or
`freeipa.ansible_freeipa`.

Use the established IdM collections for IdM server, replica, and client
lifecycle and broad IdM object management. Use `eigenstate.ipa` when Ansible
needs live IdM state as inventory, policy evidence, vault/keytab/certificate
input, temporary-access context, AAP execution material, or
OpenShift/Kubernetes review artifacts.

| Need | Use |
| --- | --- |
| Install IdM server, replica, or client | `redhat.rhel_idm` or `freeipa.ansible_freeipa` |
| Manage broad IdM object lifecycle | `redhat.rhel_idm` or `freeipa.ansible_freeipa` |
| Build live Ansible inventory from IdM | `eigenstate.ipa` |
| Use vault, keytab, or certificate state in automation workflows | `eigenstate.ipa` |
| Preflight HBAC, sudo, SELinux, DNS, or access-path state | `eigenstate.ipa` |
| Render AAP, OpenShift, or Kubernetes evidence before mutation | `eigenstate.ipa` |

## Start Here

| Need | First page |
| --- | --- |
| Learn the shape of the collection | [Tutorials](tutorials/) |
| Complete a production task | [How-to guides](how-to/) |
| Look up exact syntax or return data | [Reference](reference/) |
| Understand authority and safety boundaries | [Explanation](explanation/) |

## Problem

Without a live IdM-backed path, operators usually end up with duplicated
inventory, policy facts copied into variables, secret values moved through
other stores, keytabs staged by hand, and certificate workflows split away from
the automation job that needs the result.

`eigenstate.ipa` does not make IdM a universal vault or PAM platform. It makes
IdM state usable where IdM is already the right authority: enrolled hosts,
groups, vaults, Kerberos principals, certificate requests, DNS, sudo, HBAC,
SELinux maps, and temporary account expiry.

## Architecture Mini-Map

<figure class="diagram-card diagram-card--focus">
  <figcaption>
    <strong>Authority Flow</strong>
    <span>IdM owns identity and policy state. The collection reads, renders, validates, or mutates through explicit Ansible interfaces. AAP records job evidence. Runtime systems enforce only after their own controls apply.</span>
  </figcaption>
  <div class="stage-flow" role="img" aria-label="Authority flow from IdM to Ansible collection to AAP and runtime systems">
    <ol class="stage-flow__stages">
      <li class="stage-flow__stage">
        <span class="stage-flow__number">1</span>
        <h3>Authoritative state</h3>
        <ol class="stage-flow__steps">
          <li>IdM hosts, groups, vaults, principals, certificates, DNS, sudo, HBAC, and SELinux maps</li>
          <li>Kerberos and IdM client tools provide authenticated access</li>
        </ol>
      </li>
      <li class="stage-flow__stage">
        <span class="stage-flow__number">2</span>
        <h3>Collection surfaces</h3>
        <ol class="stage-flow__steps">
          <li>Inventory and lookups read state</li>
          <li>Modules mutate only when called explicitly</li>
          <li>Roles render or report reviewable artifacts</li>
        </ol>
      </li>
      <li class="stage-flow__stage">
        <span class="stage-flow__number">3</span>
        <h3>Automation evidence</h3>
        <ol class="stage-flow__steps">
          <li>Ansible and AAP run jobs from the declared inputs</li>
          <li>Reports, manifests, and job output show what was checked or produced</li>
        </ol>
      </li>
      <li class="stage-flow__stage">
        <span class="stage-flow__number">4</span>
        <h3>Runtime enforcement</h3>
        <ol class="stage-flow__steps">
          <li>OpenShift, Kubernetes, Kerberos, CA, and IdM enforce through their own control planes</li>
          <li>Reports remain evidence, not remediation</li>
        </ol>
      </li>
    </ol>
  </div>
</figure>

## Proof Paths

| Proof path | Surfaces | Evidence |
| --- | --- | --- |
| Live IdM inventory | `eigenstate.ipa.idm` | Inventory graph and hostvars derived from IdM. |
| Inventory normalization | `eigenstate.ipa.idm` and normalization filters | Stable hostvars, raw values, type metadata, and schema warnings. |
| Vault diagnostics and retrieval | `eigenstate.ipa.vault`, `vault_health`, `vault_artifact` | Redacted task output, structured record returns, health status, and digest evidence. |
| Explicit mutation | `vault_write`, `keytab_manage`, `cert_request`, `user_lease` | Changed state, check-mode predictions, or guarded module returns. |
| Access preflight | `access_path`, `sudo_risk` | Readiness blockers and advisory sudo risk findings before privileged work. |
| AAP execution environment | `aap_execution_environment` role and `aap-ee-*` playbooks | Rendered EE context, build result, smoke output, optional Controller registration. |
| OpenShift and workload delivery | OpenShift validation and workload Secret roles | Review manifests and readiness reports before cluster mutation. |
| Operational reporting | Read-only report roles | JSON, YAML, and Markdown evidence artifacts. |

## What This Does Not Claim

- It is not a general-purpose enterprise vault, PAM suite, or dynamic secret
  lease engine.
- It does not make AAP the identity authority.
- It does not make reports enforce remediation.
- It does not apply Kubernetes or OpenShift configuration unless a role or
  playbook is explicitly configured to do so.
- It does not own private-key generation for certificate requests.

## How It Scales

The collection scales by keeping authority boundaries narrow. Inventory stays
live. Lookup plugins stay read-focused. Modules carry explicit mutation
semantics. Roles render artifacts and reports with controlled inputs. AAP can
schedule and record these workflows without becoming the source of identity
truth.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `plugins/inventory/idm.py` | Dynamic inventory from IdM host and policy state. |
| `plugins/lookup/` | Read-oriented lookups for vaults, principals, keytabs, certificates, OTP, DNS, sudo, SELinux maps, and HBAC. |
| `plugins/modules/` | Explicit write modules for vault lifecycle, keytab management, certificate requests, and user lease boundaries. |
| `roles/` | AAP execution environment, OpenShift identity validation, workload Secret rendering, temporary access, and reports. |
| `playbooks/` | Wrapper playbooks for common role workflows. |
| `execution-environment/eigenstate-idm/` | Ready-to-build AAP execution environment scaffold. |
| `tests/` | Unit, structure, argument-spec, secret-safety, and integration fixtures. |
| `docs/` | Public documentation and rewrite governance. |

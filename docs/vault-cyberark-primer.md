---
layout: default
title: Vault And CyberArk Primer
description: >-
  Primer for HashiCorp Vault and CyberArk users comparing Eigenstate's
  IdM-native automation model, current collection surface, and AAP-backed
  controller workflows against external secrets and PAM platforms.
---

{% raw %}

# Vault And CyberArk Primer

Related docs:

<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>&nbsp;&nbsp;ROTATION CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/rotation-use-cases.html"><kbd>&nbsp;&nbsp;ROTATION USE CASES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>&nbsp;&nbsp;EPHEMERAL ACCESS CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

## Purpose

Use this guide when you already understand HashiCorp Vault or CyberArk and you
want to know where `eigenstate.ipa` overlaps, where it is stronger inside an
IdM-centric estate, and where it is not a substitute.

This is a comparison and positioning document, not a plugin reference page.
It is meant to answer the adoption question honestly for RHEL- and IdM-centric
automation teams.

In this document, **Eigenstate** means the current `eigenstate.ipa` collection,
the official IdM collections (`freeipa.ansible_freeipa` / `redhat.rhel_idm`),
and AAP working together as one automation stack.

> [!NOTE]
> AAP matters in this comparison because it provides the scheduler, execution
> environment, credential injection, approval path, and repeatable controller
> boundary that make IdM-backed workflows operationally coherent. Without AAP,
> the IdM-backed capabilities still exist, but the controller story becomes a
> plain-Ansible pattern rather than a first-class platform workflow. For the
> controller execution model, see
> <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a>.

## The Short Version

If you already run Red Hat IdM or FreeIPA, you are already operating:

- an X.509 CA through Dogtag
- a Kerberos KDC with principal lifecycle
- IdM vaults for static secret storage
- an LDAP directory with host, user, group, and policy state
- HBAC and SELinux user-map policy
- OTP and host-enrollment credentials
- integrated DNS in many deployments

`eigenstate.ipa` turns those IdM surfaces into controller-side Ansible inputs:

- live inventory from IdM host and policy data
- vault retrieval and vault lifecycle mutation
- principal, keytab, and certificate workflows
- DNS inspection
- sudo, SELinux map, and HBAC inspection or access testing
- OTP-driven enrollment credentials

The claim is not that this stack replaces Vault or CyberArk everywhere.
The claim is narrower and stronger:

- it covers a real part of the automation-facing surface already
- it is especially strong in RHEL- and IdM-centric estates
- it should not be described as a dynamic secret lease engine or a PAM session broker

## What The Collection Actually Ships Now

| Area | Current surface | Best operational use |
| --- | --- | --- |
| Inventory | `eigenstate.ipa.idm` | make AAP or Ansible inventory follow live IdM state |
| Static secret retrieval | `eigenstate.ipa.vault` | consume IdM vault content in playbooks |
| Static secret lifecycle | `eigenstate.ipa.vault_write` | create, archive, rotate, and delegate vault access |
| Kerberos identity checks | `eigenstate.ipa.principal` | gate workflows before keytab or cert work |
| Key material | `eigenstate.ipa.keytab` | retrieve or rotate service keytabs |
| Temporary user lease boundary | `eigenstate.ipa.user_lease` | expire delegated temporary users in IdM instead of relying on cleanup alone |
| PKI | `eigenstate.ipa.cert` | request, retrieve, and audit IdM certificates |
| Enrollment credentials | `eigenstate.ipa.otp` | issue user OTP seeds and host enrollment passwords |
| DNS inspection | `eigenstate.ipa.dns` | verify forward, reverse, and zone-apex state |
| Access-policy inspection | `eigenstate.ipa.hbacrule`, `eigenstate.ipa.selinuxmap`, `eigenstate.ipa.sudo` | pre-flight gate a change against IdM policy |
| Adjacent official modules | `ipaclient`, `ipahost`, `ipacert`, and broader CRUD | enrollment, revocation, and write-heavy IdM management |

The stack is strongest when these surfaces are composed intentionally instead of
read as isolated plugins.

## Feature-By-Feature Comparison

### Secrets Storage And Retrieval

| Capability | HashiCorp Vault | CyberArk | Eigenstate |
| --- | --- | --- | --- |
| Static secret storage | KV v1/v2 | Safe + account | IdM vault |
| Per-user secret scope | Cubbyhole / policies | Personal Safe | User-scoped vault |
| Per-service secret scope | Namespaces / policies | Application Safe | Service-principal-scoped vault |
| Binary artifact storage | convention in KV | safe attachment patterns | IdM vault with base64 payloads |
| Static secret update in automation | API write / `vault kv put` | account update workflow | `vault_write` |
| Vault member management | Vault policies | Safe permissions | `vault_write` members / `members_absent` |
| Metadata inspection | `kv metadata get` | safe metadata | `vault` `operation=show` / `find` |
| Native Ansible retrieval surface | community plugins | AAM plugin | built-in `eigenstate.ipa.vault` |
| Auth for automation | AppRole, OIDC, cloud IAM, Kubernetes | AIM / CCP certificate | Kerberos keytab |
| Native automatic rotation engine | Yes | Yes | No native engine; AAP-scheduled static workflows |

What stands out here is not that IdM vaults beat Vault's dynamic engines. They do not.
What stands out is that in an IdM-centric estate the ownership model, access model,
and automation auth model already live in the same identity system. There is no second
policy plane to stand up just to store static automation material.

### PKI And Certificate Lifecycle

| Capability | HashiCorp Vault PKI | CyberArk | Eigenstate |
| --- | --- | --- | --- |
| Built-in CA | Yes | No | Yes, through Dogtag |
| CSR signing from Ansible | `vault write pki/sign/...` | external CA workflow | `eigenstate.ipa.cert operation=request` |
| Retrieve by serial | limited outside PKI engine flows | external CA dependent | `operation=retrieve` |
| Expiry-window discovery | engine-specific | account-oriented | `operation=find` with expiry bounds |
| Batch certificate issuance | repeated API calls | external workflow | multiple principals in one lookup call |
| Cert + private key workflow | manual assembly | external workflow | `cert` + `vault_write` / `vault` |
| Cert revocation | yes | external CA dependent | official IdM `ipacert` modules |
| Certmonger alignment | No | No | native RHEL / IdM pattern |

This is one of the collection's strongest challenger positions. If you already
operate IdM, you already operate a CA. `eigenstate.ipa.cert` exposes that CA to
Ansible directly instead of forcing a second PKI control plane beside the one
RHEL systems already trust.

### Kerberos And Service Identity Lifecycle

| Capability | HashiCorp Vault | CyberArk | Eigenstate |
| --- | --- | --- | --- |
| Keytab retrieval | No | No | `eigenstate.ipa.keytab` |
| Key rotation through keytab generation | No | No | `retrieve_mode='generate'` |
| Principal existence / state check | No | No | `eigenstate.ipa.principal` |
| Key presence check | No | No | `has_keytab` |
| Disabled / locked state | No | No | `disabled` |
| Last authentication signal | No | No | `last_auth` |
| Bulk principal audit | No | No | `operation=find` |
| Pre-flight gate before keytab work | No | No | principal lookup then conditional keytab |
| Enrollment bootstrap into Kerberos estate | No | No | OTP + official IdM enrollment modules |

This is the area where Eigenstate stands out most clearly. Vault and CyberArk are
not substitutes for an IdM-native Kerberos lifecycle. In RHEL estates that still
run on service principals and keytabs, that matters more than generic secret storage.

### Access Policy And Identity-Aware Automation

| Capability | HashiCorp Vault | CyberArk | Eigenstate |
| --- | --- | --- | --- |
| Host-based access control engine | No | No | HBAC in IdM |
| Live access test from automation | No | No | `hbacrule operation=test` |
| HBAC rule inspection | No | No | `show` / `find` |
| SELinux user-map inspection | No | No | `selinuxmap` |
| Sudo rule / command / group inspection | No | manage-oriented PAM context | `sudo` |
| Pipeline gate on access policy | No | indirect at best | HBAC / SELinux / sudo pre-flight |
| Identity-driven inventory groups | No | No | `idm` inventory |
| Inventory groups from HBAC scope | No | No | `idm` with `hbacrules` |
| Session recording policy | No | PSM proxy model | tlog via SSSD + IdM policy |

This is where the collection is most different from both competitors. Vault can tell
you whether a token may read a secret path. CyberArk can tell you whether a credential
is governed by PAM policy. Neither answers the IdM-native question: would this identity
actually be allowed onto this host, in this service path, under current directory policy?

### OTP And Host Enrollment

| Capability | HashiCorp Vault | CyberArk | Eigenstate |
| --- | --- | --- | --- |
| TOTP token management | Vault TOTP engine | No | `eigenstate.ipa.otp` |
| HOTP token management | No | No | `eigenstate.ipa.otp` |
| One-time host enrollment passwords | no IdM-native equivalent | No | `token_type='host'` |
| Token revocation | Yes | No | `operation=revoke` |
| Token state inspection | limited outside engine semantics | No | `operation=show` / `find` |
| Host enrollment workflow tie-in | No native IdM path | No | OTP + `ipahost` / `ipaclient` |

Vault's TOTP engine is useful, but it is not tied to RHEL host enrollment. IdM's OTP
model is. That makes `eigenstate.ipa.otp` more than just another token API when the
estate actually enrolls systems into IdM.

### Inventory As Identity Data

| Capability | HashiCorp Vault | CyberArk | Eigenstate |
| --- | --- | --- | --- |
| Dynamic Ansible inventory | No | No | `eigenstate.ipa.idm` |
| Inventory from hostgroups | No | No | Yes |
| Inventory from netgroups | No | No | Yes |
| Inventory from HBAC rules | No | No | Yes |
| Curated host metadata export | No | No | `idm_*` hostvars |
| Narrow exported metadata surface | No | No | `hostvars_include` |
| Disable host-level enrichment | No | No | `hostvars_enabled: false` |

Neither competitor gives you identity-backed inventory. This is not a side feature.
It is one of the collection's most operationally important differentiators because it
keeps targeting, grouping, and access context anchored to the same IdM source of truth.

## High-Value Compositions

These are the current combinations that actually change how an operator should
run the system.

### 1. Controller-scheduled static secret lifecycle

Use `vault_write` for mutation, `vault` for retrieval, and AAP for schedule and
approval.

This is the collection's answer to the rotation gap:

- no native automatic lease engine
- yes controller-scheduled rotation workflows for static assets

### 2. Service onboarding from IdM outward

Use `principal` as the pre-flight gate, then branch into `keytab` or `cert`.
Archive private keys or follow-on bootstrap material in a vault when the
workflow needs it.

### 3. Policy-aware controller gates

Use `hbacrule`, `selinuxmap`, and `sudo` to answer questions that Vault and
CyberArk do not answer:

- would this identity actually be allowed onto this host?
- would it land in the expected SELinux context?
- does the expected sudo policy surface exist?

### 4. Lease-like temporary access where IdM owns the cutoff

Use `user_lease` when a delegated temporary user should become unusable because
IdM expiry attributes close the window, not because a later cleanup job happens
to run. Use `principal` + `keytab` when the stronger answer is a Kerberos-first
machine identity with immediate key retirement.

### 5. Identity-backed inventory rather than static inventory drift

Use `idm` inventory to let AAP or Ansible target by IdM hostgroups, netgroups,
HBAC scope, and curated host metadata.

### 6. Enrollment and first-day trust

Use `otp` to create the one-time host password, then hand enrollment to the
official IdM collections. Use `principal` afterward if the play needs a
post-enrollment gate.

## Where Eigenstate Is Stronger Than The Comparison Usually Assumes

### Kerberos and keytabs

Vault and CyberArk do not give you an IdM-native keytab lifecycle. If your
estate uses Kerberos service identities heavily, `principal` plus `keytab` is a
material differentiator.

### IdM policy as automation input

Vault can answer whether a token has access to a secret path. CyberArk can
answer whether an account is in a safe or mediated through PSM. Neither tells
you whether current IdM policy would allow a given identity onto a given host.
`hbacrule operation=test` does.

### Dogtag-backed PKI without a second CA stack

If you already operate IdM, you already operate a CA. `eigenstate.ipa.cert`
turns that into an Ansible-native issuance and audit surface. That is different
from bolting a new PKI engine beside the identity system you already trust.

### Session recording context

CyberArk PSM is a privileged session proxy. IdM session recording is different:
`SSSD` and `tlog` enforce and capture recording on the host, with policy keyed
off IdM users and groups. That is useful, but it is not the same product shape
as a proxy-mediated PAM gateway.

## Where Eigenstate Is Not A Substitute

### Dynamic secrets

IdM vaults are static. Vault's database secrets engine, AWS dynamic
credentials, and ephemeral IAM roles have no equivalent in IdM. The collection
supports controller-scheduled rotation workflows for static assets, but not
native short-lived credential issuance with lease, renew, and revoke semantics.

AAP can emulate short-lived operational workflows for static secrets by running
create, deploy, rotate, and cleanup jobs on a schedule. That is useful. It is
not the same security contract as a credential born with native TTL and backend
revocation semantics.

The strongest partial answers to this gap are IdM-native identity controls, not the vault surface.
For delegated temporary users, `user_lease` can make the user expire in IdM itself so the
cutoff is not just a later cleanup task. For Kerberos machine identity, `eigenstate.ipa`
makes keytab-backed automation much easier to orchestrate than ordinary static
passwords. A controller can retrieve or issue a keytab, use it to obtain
Kerberos tickets for the run, and then retire the underlying key material
immediately by rotating the principal again. That gives you operationally
short-lived machine credentials without pretending they are Vault-style leased
secrets.

The boundary still matters:

- there is no native lease object, TTL, or renewal contract
- rotation is a workflow decision, not an issuer-enforced expiry model
- destructive key rotation still requires coordinated rollout to every consumer

So this is not a replacement for dynamic database or cloud credentials. It is a
stronger machine-identity story when Kerberos already fits the architecture.

For the broader temporary-access framing, including delegated temporary users
and the difference between IdM-native expiry controls and AAP cleanup hygiene,
see <a href="https://gprocunier.github.io/eigenstate-ipa/ephemeral-access-capabilities.html"><kbd>EPHEMERAL ACCESS CAPABILITIES</kbd></a>.

### Broad PAM and privileged session brokering

CyberArk still owns the stronger story for central privileged session brokering,
credential checkout workflows, and platform-spanning PAM controls. IdM session
recording is narrower and host-centric.

### Cross-platform and cloud-native secret sprawl

If the estate is mostly databases, cloud IAM roles, SaaS API tokens, or
non-RHEL platforms with little IdM gravity, Vault or CyberArk remains the more
natural control plane.

## Quick Decision Reference

| If the real need is... | Better fit |
| --- | --- |
| static secret storage and retrieval for an IdM-centric estate | `eigenstate.ipa` + IdM vaults |
| scheduled rotation of static secrets, keytabs, or cert-adjacent artifacts | `eigenstate.ipa` + AAP |
| Kerberos principal and keytab lifecycle | `eigenstate.ipa` |
| Dogtag-backed PKI automation inside an IdM estate | `eigenstate.ipa` |
| live IdM policy validation before change | `eigenstate.ipa` |
| dynamic database or cloud credentials with TTL and revocation | Vault |
| broad privileged session brokering and PAM workflows | CyberArk |
| mixed estate with little IdM dependence | usually Vault or CyberArk |

## How To Read The Rest Of The Docs

After this primer:

- read <a href="https://gprocunier.github.io/eigenstate-ipa/aap-integration.html"><kbd>AAP INTEGRATION</kbd></a> for the controller model
- read <a href="https://gprocunier.github.io/eigenstate-ipa/rotation-capabilities.html"><kbd>ROTATION CAPABILITIES</kbd></a> if the question is lifecycle and scheduling
- read <a href="https://gprocunier.github.io/eigenstate-ipa/documentation-map.html"><kbd>DOCUMENTATION MAP</kbd></a> for plugin-by-plugin routing

## Guardrails

To keep the comparison honest:

- do not describe the collection as a Vault replacement in general
- do not describe AAP scheduling as a native lease engine
- do not describe IdM session recording as if it were CyberArk PSM
- do not bury the strongest parts of the stack: keytabs, PKI, policy gating, and IdM-backed inventory

{% endraw %}

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
| PKI | `eigenstate.ipa.cert` | request, retrieve, and audit IdM certificates |
| Enrollment credentials | `eigenstate.ipa.otp` | issue user OTP seeds and host enrollment passwords |
| DNS inspection | `eigenstate.ipa.dns` | verify forward, reverse, and zone-apex state |
| Access-policy inspection | `eigenstate.ipa.hbacrule`, `eigenstate.ipa.selinuxmap`, `eigenstate.ipa.sudo` | pre-flight gate a change against IdM policy |
| Adjacent official modules | `ipaclient`, `ipahost`, `ipacert`, and broader CRUD | enrollment, revocation, and write-heavy IdM management |

The stack is strongest when these surfaces are composed intentionally instead of
read as isolated plugins.

## High-Value Compositions

These are the current combinations that actually change how an operator should
run the system.

### 1. Controller-scheduled static secret lifecycle

Use `vault_write` for mutation, `vault` for retrieval, and AAP for schedule and
approval.

This is the collection's answer to the "rotation gap":

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

### 4. Identity-backed inventory rather than static inventory drift

Use `idm` inventory to let AAP or Ansible target by IdM hostgroups, netgroups,
HBAC scope, and curated host metadata.

### 5. Enrollment and first-day trust

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

# Vault Capabilities

Nearby docs:

<a href="./vault-plugin.md"><kbd>&nbsp;&nbsp;VAULT PLUGIN&nbsp;&nbsp;</kbd></a>
<a href="./inventory-capabilities.md"><kbd>&nbsp;&nbsp;INVENTORY CAPABILITIES&nbsp;&nbsp;</kbd></a>
<a href="./aap-integration.md"><kbd>&nbsp;&nbsp;AAP INTEGRATION&nbsp;&nbsp;</kbd></a>
<a href="./README.md"><kbd>&nbsp;&nbsp;DOCS MAP&nbsp;&nbsp;</kbd></a>

## Purpose

This page explains when and why an operator would use each major vault retrieval
pattern exposed by `eigenstate.ipa.vault`.

It is the vault-side companion to the inventory capabilities guide.

## Contents

- [Retrieval Model](#retrieval-model)
- [1. Shared Standard Vaults: Estate-Wide Secret Injection](#1-shared-standard-vaults-estate-wide-secret-injection)
- [2. Shared Symmetric Vaults: Centrally Owned Secret With Extra Unlock Material](#2-shared-symmetric-vaults-centrally-owned-secret-with-extra-unlock-material)
- [3. Shared Asymmetric Vaults: Private-Key-Gated Retrieval](#3-shared-asymmetric-vaults-private-key-gated-retrieval)
- [4. User Vaults: Principal-Scoped Secrets](#4-user-vaults-principal-scoped-secrets)
- [5. Service Vaults: Service-Principal-Scoped Secrets](#5-service-vaults-service-principal-scoped-secrets)
- [6. Binary Retrieval: Keytabs And Opaque Artifacts](#6-binary-retrieval-keytabs-and-opaque-artifacts)
- [7. Rotation And Incident Response](#7-rotation-and-incident-response)
- [8. Metadata Inspection Before Retrieval](#8-metadata-inspection-before-retrieval)
- [9. Brokered Sealed Artifact Metadata Convention](#9-brokered-sealed-artifact-metadata-convention)
- [10. Brokered Sealed Artifact Delivery](#10-brokered-sealed-artifact-delivery)
- [11. Structured Text Payloads](#11-structured-text-payloads)
- [Quick Decision Matrix](#quick-decision-matrix)

## Retrieval Model

```mermaid
flowchart TD
    vaults["IdM vaults"]
    scopes["user / service / shared scope"]
    auth["Kerberos auth\npassword, ticket, or keytab"]
    lookup["eigenstate.ipa.vault"]
    tasks["Ansible tasks, templates,\ncredential injection"]

    vaults --> lookup
    scopes --> lookup
    auth --> lookup
    lookup --> tasks
```

Use the vault pattern that matches both:

- the ownership boundary of the secret
- the runtime form the consuming automation actually needs

## 1. Shared Standard Vaults: Estate-Wide Secret Injection

Use a shared standard vault when the same secret must be consumed by automation
across many hosts or jobs and no extra decryption material should be required at
lookup time.

Typical cases:

- database passwords
- internal service credentials
- API tokens managed centrally

```mermaid
flowchart LR
    V["Shared standard vault"] --> L["lookup(..., shared=true)"] --> U["utf-8 secret for task/template use"]
```

Example:

```yaml
- name: Read a shared database password
  ansible.builtin.set_fact:
    db_password: "{{ lookup('eigenstate.ipa.vault',
                     'database-password',
                     server='idm-01.corp.example.com',
                     ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
                     shared=true,
                     verify='/etc/ipa/ca.crt') }}"
```

Why this pattern fits:

- retrieval is simple
- no additional vault-specific secret material is required
- the ownership model is clear for multi-consumer automation

## 2. Shared Symmetric Vaults: Centrally Owned Secret With Extra Unlock Material

Use a symmetric vault when the automation should retrieve a centrally owned
secret, but the vault itself should still require a second password for
decryption.

Typical cases:

- externally issued API credentials
- partner integration secrets
- staged rotation where the vault password is managed separately from the IdM
  principal

```mermaid
flowchart LR
    V["Shared symmetric vault"] --> P["vault_password\nor vault_password_file"] --> L["lookup"] --> U["decrypted secret"]
```

Example:

```yaml
- name: Read a symmetric vault using a password file
  ansible.builtin.set_fact:
    api_key: "{{ lookup('eigenstate.ipa.vault',
                 'partner-api-key',
                 server='idm-01.corp.example.com',
                 kerberos_keytab='/runner/env/ipa/admin.keytab',
                 shared=true,
                 vault_password_file='/runner/env/ipa/partner-api.pass',
                 verify='/etc/ipa/ca.crt') }}"
```

Why this pattern fits:

- the vault remains centrally owned
- decryption requires an additional control
- it works well when the decrypt password is handled by a separate controller
  credential or mounted file

## 3. Shared Asymmetric Vaults: Private-Key-Gated Retrieval

Use an asymmetric vault when the consuming automation should only succeed if it
also possesses a corresponding private key.

Typical cases:

- TLS private key recovery
- PKI artifacts stored under stronger operator control
- secrets intended for a narrow automation boundary

```mermaid
flowchart LR
    V["Shared asymmetric vault"] --> K["private_key_file"] --> L["lookup"] --> U["decrypted output"]
```

Example:

```yaml
- name: Read a TLS private key from an asymmetric vault
  ansible.builtin.copy:
    content: "{{ lookup('eigenstate.ipa.vault',
                  'wildcard-tls-key',
                  server='idm-01.corp.example.com',
                  kerberos_keytab='/runner/env/ipa/admin.keytab',
                  shared=true,
                  private_key_file='/runner/env/ipa/tls-recovery.pem',
                  verify='/etc/ipa/ca.crt') }}"
    dest: /etc/pki/tls/private/wildcard.key
    mode: "0600"
```

Why this pattern fits:

- access is tied to possession of the private key
- authorization is not based only on IdM principal rights
- it reduces accidental broad retrievability for sensitive material

## 4. User Vaults: Principal-Scoped Secrets

Use a user vault when the secret belongs to one named user principal rather than
to a shared automation domain.

Typical cases:

- per-user tokens
- personal signing material
- isolated operator bootstrap data

```mermaid
flowchart LR
    V["User vault"] --> S["username='appuser'"] --> L["lookup"] --> U["principal-scoped secret"]
```

Example:

```yaml
- name: Read a user-owned secret
  ansible.builtin.debug:
    msg: "{{ lookup('eigenstate.ipa.vault',
             'my-bootstrap-token',
             server='idm-01.corp.example.com',
             kerberos_keytab='/runner/env/ipa/admin.keytab',
             username='appuser',
             verify='/etc/ipa/ca.crt') }}"
```

Why this pattern fits:

- ownership stays aligned with a single principal
- it avoids pushing personal material into a shared vault namespace

## 5. Service Vaults: Service-Principal-Scoped Secrets

Use a service vault when the secret belongs to a service principal boundary.

Typical cases:

- application service credentials
- daemon-specific tokens
- automation that manages service identity rather than human identity

```mermaid
flowchart LR
    V["Service vault"] --> S["service='HTTP/app.example.com'"] --> L["lookup"] --> U["service-scoped secret"]
```

Example:

```yaml
- name: Read a service-principal secret
  ansible.builtin.set_fact:
    service_secret: "{{ lookup('eigenstate.ipa.vault',
                         'oidc-client-secret',
                         server='idm-01.corp.example.com',
                         ipaadmin_password=lookup('env', 'IPA_ADMIN_PASSWORD'),
                         service='HTTP/app.corp.example.com',
                         verify='/etc/ipa/ca.crt') }}"
```

Why this pattern fits:

- the vault boundary mirrors the service identity boundary
- service secrets stay out of generic shared namespaces

## 6. Binary Retrieval: Keytabs And Opaque Artifacts

Use `encoding='base64'` when the vault content is not reliably text.

Typical cases:

- keytabs
- PKCS#12 bundles
- opaque binary blobs passed to another tool

```mermaid
flowchart LR
    V["Binary vault data"] --> E["encoding='base64'"] --> L["lookup"] --> D["b64decode in consuming task"]
```

Example:

```yaml
- name: Install service keytab from IdM vault
  ansible.builtin.copy:
    content: "{{ lookup('eigenstate.ipa.vault',
                  'service-keytab',
                  server='idm-01.corp.example.com',
                  kerberos_keytab='/runner/env/ipa/admin.keytab',
                  shared=true,
                  encoding='base64',
                  verify='/etc/ipa/ca.crt') | b64decode }}"
    dest: /etc/krb5.keytab
    mode: "0600"
```

Why this pattern fits:

- it preserves binary integrity through the lookup boundary
- the consuming task decides how and where to materialize the file

> [!CAUTION]
> Do not rely on the default `utf-8` return mode for binary payloads. Use
> `base64` intentionally when the content is a keytab, archive, bundle, or any
> other opaque byte sequence.

## 7. Rotation And Incident Response

Use IdM vault lookups when you need automation to consume the latest rotated
secret without changing repository content.

Typical cases:

- rotating a shared API key
- replacing a TLS certificate and private key bundle
- swapping breakglass credentials during an incident

The operational advantage is:

- rotate in IdM
- rerun the job
- let the lookup resolve the new value at execution time

That keeps secret version changes out of Git and out of static inventory.

## 8. Metadata Inspection Before Retrieval

Use `operation='show'` or `operation='find'` when the caller needs to inspect
vault metadata before deciding whether payload retrieval is appropriate.

Typical cases:

- delegated operators validating that a vault exists in their own scope
- controller flows that need to search for a matching vault name first
- playbooks that should fail earlier with scope and type context

```mermaid
flowchart LR
    find["operation=find"] --> inspect["metadata records"]
    show["operation=show"] --> inspect
    inspect --> retrieve["optional later retrieve"]
```

Why this pattern fits:

- it separates discovery from secret consumption
- it makes scope and vault type visible earlier in the workflow
- it reduces guesswork for non-admin callers working inside narrow boundaries

## 9. Brokered Sealed Artifact Metadata Convention

Use a consistent metadata shape when the vault is holding an opaque artifact
that will be brokered by Ansible and consumed elsewhere.

Recommended fields:

- vault name:
  - describe the artifact class and consumer boundary, for example
    `payments-bootstrap-bundle` or `cluster-sealed-payload`
- description:
  - include the artifact format, the intended consumer, and the final trust
    boundary, for example `sealed bootstrap bundle for payments-agent`
- type:
  - keep the IdM vault type explicit
  - use `standard` for opaque sealed blobs unless the vault itself needs a
    second unlock material
- routing hint:
  - keep the playbook decision in metadata, not in ad hoc task names

Example convention:

```yaml
sealed_artifact:
  vault_name: payments-bootstrap-bundle
  description: sealed bootstrap bundle for payments-agent
  consumer: payments-agent
  final_boundary: target-host
  format: base64
```

Why this pattern fits:

- the lookup can return payload plus context in one record
- the playbook does not need to infer handling from the artifact bytes
- future operators can understand the flow from the vault record itself

## 10. Brokered Sealed Artifact Delivery

Use this pattern when the vault is storing an encrypted or sealed artifact that
Ansible should transport, but not interpret.

Typical cases:

- an encrypted TLS bundle delivered to a target host for final local unwrap
- a bootstrap payload handed to another controller or agent
- a sealed blob that should stay opaque inside the automation layer

```mermaid
flowchart LR
    vault["IdM vault with sealed payload"] --> lookup["lookup(..., encoding='base64', include_metadata=true)"]
    lookup --> broker["Ansible brokers payload plus metadata"]
    broker --> consumer["downstream agent, controller, or target host"]
```

Why this pattern fits:

- IdM stays the access-control and storage boundary
- Ansible can deliver the artifact without turning it into plaintext logic
- metadata can travel with the payload so the playbook can route it safely

This is not a Vault-style sealing controller. The collection retrieves and
brokers the artifact. The downstream system is still responsible for final
consumption or unseal.

## 11. Structured Text Payloads

Use the text-normalization helpers when the vault payload is text, but the
consumer really wants structured data or newline-free values.

Typical cases:

- JSON application configuration
- tokens or passwords accidentally stored with a final newline
- controller injectors that should receive parsed fields instead of a raw blob

```mermaid
flowchart LR
    text["UTF-8 vault payload"] --> helper["decode_json or strip_trailing_newline"] --> task["task or template consumes normalized value"]
```

Why this pattern fits:

- JSON secrets can be returned as native data instead of reparsed later
- password-like values can be normalized at the lookup boundary
- the consuming task gets cleaner, less repetitive templating logic

## Quick Decision Matrix

| Need | Best pattern |
| --- | --- |
| Simple centrally shared text secret | shared standard vault |
| Centrally shared secret with extra unlock material | shared symmetric vault |
| Secret gated by private-key possession | shared asymmetric vault |
| Principal-owned secret | user vault |
| Service-identity-owned secret | service vault |
| Binary artifact | any of the above with `encoding='base64'` |
| Inspect before retrieving | `operation='show'` or `operation='find'` |
| Brokered sealed artifact | consistent metadata convention plus `include_metadata=true` |
| Opaque encrypted artifact with routing context | `encoding='base64'` plus `include_metadata=true` |
| Parsed JSON or trimmed text | `decode_json=true` or `strip_trailing_newline=true` |

For option-level behavior, failure modes, and exact lookup syntax, return to
<a href="./vault-plugin.md"><kbd>VAULT PLUGIN</kbd></a>.

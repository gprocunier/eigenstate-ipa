# Changelog

## 1.5.0

- added `eigenstate.ipa.vault_write` for IdM vault lifecycle management from Ansible
- added `plugins/module_utils/ipa_client.py` as a shared Kerberos auth and `ipalib` connection layer for write-capable IPA operations
- `vault_write` supports `state: present`, `state: absent`, and `state: archived`
- supports standard, symmetric, and asymmetric vault types
- standard vault writes are idempotent; symmetric and asymmetric archive operations remain write-always because content comparison would require decryption
- supports delta-only member management via `members` and `members_absent`
- supports Ansible check mode
- added vault-write reference, capability, and use-case documentation
- refreshed collection metadata and docs to describe the integrated inventory, vault, principal, keytab, cert, OTP, and vault-write feature set

## 1.4.0

- added `eigenstate.ipa.otp` for OTP token issue, lookup, revoke, and host enrollment password generation
- fixed repeated OTP lookups in one Ansible process by disconnecting the managed `ipalib` RPC backend before ccache cleanup
- aligned structured `map` and `map_record` OTP results with the Ansible lookup return contract
- added explicit `verify=false` handling for OTP lookup TLS behavior
- refreshed collection metadata and docs to describe the integrated inventory, vault, principal, keytab, cert, and otp feature set

## 1.3.0

- added `eigenstate.ipa.principal` for Kerberos principal existence, key, lock, and last-auth inspection
- fixed repeated principal lookups in one Ansible process by disconnecting the managed `ipalib` RPC backend before ccache cleanup
- aligned `map_record` results with the Ansible lookup return contract
- added explicit `verify=false` handling for principal lookup TLS behavior
- refreshed collection metadata and docs to describe the integrated inventory, vault, principal, keytab, and cert feature set

## 1.2.0

- added `eigenstate.ipa.cert` for IdM CA certificate request, retrieve, and find operations
- fixed repeated cert lookups in one Ansible process by disconnecting the managed `ipalib` RPC backend before ccache cleanup
- fixed `operation=find` principal filtering to use the supported IdM CA owner arguments
- fixed structured `map` and `map_record` cert results to satisfy the Ansible lookup return contract
- excluded transient `.ansible` state from built collection artifacts
- refreshed collection metadata and docs to describe the integrated inventory, vault, keytab, and cert feature set

## 1.1.1

- refreshed release metadata to match the keytab-enabled collection scope
- updated the packaged README, LLM metadata, Galaxy metadata, and citation file for the 1.1.1 release

## 1.1.0

- added `eigenstate.ipa.keytab` lookup plugin for retrieving Kerberos keytab
  files from FreeIPA/IdM service and host principals
- keytab retrieval uses `ipa-getkeytab` from the platform IPA client tooling over an
  authenticated Kerberos session; no ipalib dependency at keytab-retrieval time
- supports `retrieve` mode (existing keys, safe default) and `generate` mode
  (rotates principal keys) with an explicit warning on key rotation
- supports per-principal encryption-type selection via `enctypes`
- returns base64-encoded keytab content in `value`, `record`, or `map` result
  formats to match vault plugin conventions
- added unit tests for flag generation, result formatting, and error paths
- added keytab plugin reference doc and scenario-based capability guide

## 1.0.4

- hardened the vault lookup plugin by normalizing lookup terms and scope values to text before IPA calls
- added regression tests covering normalized term and scope handling in the vault lookup
- corrected the sealed-artifact workflow documentation to reflect the certmonger prerequisite and the validated collection retrieval pattern

## 1.0.3

- removed Mermaid from the packaged root README so Galaxy renders the overview cleanly

## 1.0.2

- tightened documentation tone in the reference and capability guides
- prepared the next Galaxy release after the 1.0.1 README link fix

## 1.0.1

- fixed Galaxy README links by switching packaged documentation links to absolute GitHub Pages URLs

## 1.0.0

- initial `eigenstate.ipa` collection release
- added `eigenstate.ipa.idm` dynamic inventory plugin
- added `eigenstate.ipa.vault` lookup plugin
- added operator, capability, use-case, and AAP integration documentation

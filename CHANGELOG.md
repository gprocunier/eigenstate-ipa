# Changelog

## 1.4.0

- added `eigenstate.ipa.vault_write` action module for vault lifecycle management
- added `plugins/module_utils/ipa_client.py` shared Kerberos auth and ipalib connection layer
- vault_write supports `state: present`, `state: absent`, and `state: archived`
- vault_write supports standard, symmetric, and asymmetric vault types
- vault_write is fully idempotent for standard vaults; symmetric and asymmetric vaults are write-always for `state: archived`
- vault_write supports delta-only member management via `members` and `members_absent`
- vault_write supports Ansible check mode
- added vault-write-plugin.md, vault-write-capabilities.md, and vault-write-use-cases.md documentation

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

# Changelog

## 1.1.0

- added `eigenstate.ipa.keytab` lookup plugin for retrieving Kerberos keytab
  files from FreeIPA/IdM service and host principals
- keytab retrieval uses `ipa-getkeytab` from `ipa-client-utils` over an
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

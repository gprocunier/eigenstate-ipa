# Changelog

## 1.16.0 - 2026-05-05

- added release engineering maturity gates with an ansible-core 2.15 through
  2.18 CI matrix aligned to `meta/runtime.yml`
- added blocking collection metadata lint, a release-gated `ansible-test`
  sanity subset, public documentation language validation, Markdown example
  checks, and AAP EE scaffold validation to the standard validation path
- added release workflow version/tag checks, artifact checksum generation,
  manifest inspection, and clean-install documentation smoke tests before
  GitHub release publication
- added release process, test strategy, and support matrix documentation with
  explicit separation between fast CI, optional integration tests, and private
  lab validation
- kept public documentation language neutral and removed release gates that
  would depend on byte-identical Galaxy tarball output across builds

## 1.15.0 - 2026-05-05

- added `idm_readiness_report` for deterministic IdM automation readiness
  evidence in JSON, YAML, and Markdown
- added `certificate_inventory_report` for certificate lifecycle evidence
  without private keys or secret payloads
- added `keytab_rotation_candidates` for read-only keytab rotation planning
  without exposing keytab bytes
- added `temporary_access_report` and `policy_drift_report` for access-window
  review and expected-versus-observed policy drift evidence
- documented the Phase 6 report schemas and validated the feature set in an
  on-prem lab from the bastion execution boundary before publication
- wired Phase 6 playbook syntax checks, static validation, rendered-output
  tests, argument spec checks, and secret-safety tests into the standard
  validation path

## 1.14.0 - 2026-05-05

- added `kubernetes_secret_from_idm_vault` for render-first Kubernetes Secret
  manifests from IdM vault material with redacted review output by default
- added `kubernetes_tls_from_idm_cert` for render-first TLS Secret manifests
  from certificate material governed by an IdM-centered process
- added `keytab_secret_render` for review-first Kerberos keytab Secret
  delivery to Kubernetes and OpenShift workloads
- documented the Kubernetes Secret delivery threat model, including etcd
  encryption, RBAC, namespace scope, audit, and rotation limitations
- wired Phase 5 playbook syntax checks, static validation, rendered-output
  tests, argument spec checks, and secret-safety tests into the standard
  validation path

## 1.13.0 - 2026-05-05

- added OpenShift OIDC validation workflows for rendering OAuth/OIDC examples
  and checking IdM group evidence before platform integration
- added Keycloak-to-IdM federation validation workflows for local federation
  metadata and OIDC claim evidence
- added OpenShift breakglass validation workflows for emergency group,
  control, and RBAC evidence review
- added OpenShift, Keycloak, IdM federation, breakglass, and LDAP fallback
  documentation for evidence-driven identity integration reviews
- wired the Phase 4 validation roles, wrapper playbooks, static validation, and
  regression tests into the standard collection validation path

## 1.12.0 - 2026-05-05

- added `keytab_manage` for explicit keytab generation, retrieval, and
  removal workflows with `check_mode` support and structured change reporting
- added `cert_request` for IdM certificate request workflows with CSR input,
  principal targeting, and fail-closed validation semantics
- documented the compatibility policy and migration path from lookup-only
  mutation surfaces to module-backed workflows
- hardened `vault_write` compatibility handling so deprecated alias use emits
  warnings while unsafe or unsupported option combinations fail closed
- refreshed the documentation map, machine-readable context, and module docs
  for the expanded mutation surface set

## 1.11.0 - 2026-05-05

- added `roles/aap_execution_environment` to render, build, smoke-test, push,
  and optionally register an AAP execution environment for `eigenstate.ipa`
- added a static `execution-environment/eigenstate-idm/` scaffold for manual
  Ansible Builder workflows
- added AAP EE quickstart, disconnected build, troubleshooting, and validation
  walkthrough documentation
- added render-only validation for the EE scaffold and unit coverage for the
  role render path
- hardened RHOSO `user_lease` examples so admin keytab examples use the
  matching `admin` principal

## 1.10.13 - 2026-04-27

- normalized Ansible unsafe text values before passing `tls_ca_cert` to FreeIPA bootstrap so AAP-provided certificate paths satisfy FreeIPA's exact primitive type checks
- guarded against finalizing a partially initialized FreeIPA environment when bootstrap has failed before core defaults are available
- added regression coverage for unsafe text certificate paths and incomplete bootstrap state

## 1.10.12 - 2026-04-27

- refined the FreeIPA bootstrap compatibility path so a `tls_ca_cert` override rejection that still leaves bootstrap complete is treated as successful bootstrap before finalization
- added regression coverage for the partially completed bootstrap case observed in AAP execution environments

## 1.10.11 - 2026-04-27

- made `IPAClient.connect()` retry FreeIPA bootstrap without a `tls_ca_cert` override when upstream FreeIPA rejects the override after loading controller-provided `/etc/ipa` configuration
- added regression coverage for the bootstrap retry path used by AAP execution environments that provide `/etc/ipa/ca.crt`

## 1.10.10 - 2026-04-27

- fixed ipalib-backed lookup plugin import fallback handling so cleanup does not mask missing or failed `ipalib` imports as `_ipa_api` `NameError` failures
- added DNS lookup regression coverage proving a missing `ipalib` dependency reports the real dependency error instead of a cleanup-time variable failure

## 1.10.9 - 2026-04-27

- replaced fragile lookup-level `IPAClient.cleanup.__globals__` mutation with explicit cleanup context passing through the shared `IPAClient` helper
- normalized the OTP lookup option path by documenting the `type` compatibility alias and using standard `self.get_option()` handling in `run()`
- refreshed release hygiene by adding changelog date stamps, keeping `COPYING` and `LICENSE` byte-identical, and correcting README wording around the user-lease surface
- added focused regression coverage for the OTP compatibility alias and the explicit `IPAClient.cleanup(ipa_api=..., has_ipalib=...)` path

## 1.10.8 - 2026-04-27

- fixed live IdM vault metadata lookups by removing the unsupported `no_members` option from `vault_show` and `vault_find` API calls
- added regression coverage proving `eigenstate.ipa.vault` omits that option while preserving `all`, `raw`, scope, and `sizelimit` arguments
- validated the 1.10.8 artifact against a live IdM server from a bastion host across the refactored lookup plugin set before Galaxy publication

## 1.10.7 - 2026-04-27

- centralized Kerberos authentication, TLS verification, credential-cache cleanup, and ipalib connection setup for the `cert`, `dns`, `hbacrule`, `keytab`, `otp`, `principal`, `selinuxmap`, `sudo`, and `vault` lookup plugins through the shared `IPAClient` helper
- fixed ipalib bootstrap behavior needed by controller-side and bastion-side automation by avoiding the problematic server override while still passing explicit TLS CA paths through to bootstrap
- corrected sudo rule lookup handling when legacy IdM responses omit `ipaenabledflag` and added regression coverage for that record shape
- tightened the Galaxy collection artifact boundary for this release: `.github`, tests, scripts, Python caches, and pytest caches are excluded, and the standalone OpenShift/AAP demo scripts remain separate work outside the published collection

## 1.10.6 - 2026-04-16

- changed `eigenstate.ipa.user_lease` so `password_expiration_matches_principal` now defaults to `true`, updated validation around the safer default, and added unit coverage for the explicit unsafe opt-out path
- tightened the user-lease reference and use-case docs so every published lease example keeps password expiry aligned with the principal boundary and explicitly warns that setting `password_expiration_matches_principal: false` is generally unsafe
- expanded the AAP and user-lease docs with the validated manual demo flow and defense-in-depth guidance showing why `user_lease` plus IdM vault is stronger than treating Controller as the only guardrail around a leased-user password

## 1.10.5 - 2026-04-12

- hardened `eigenstate.ipa.vault` against Ansible and Jinja string-wrapper inputs by collapsing server, principal, scope, criteria, and decryption-related options to native built-in `str` values before connection setup and IPA calls
- added regression coverage for wrapped vault lookup inputs so templated controller values do not regress into type-sensitive lookup failures
- added the `user-lease-rbac-setup` guide and threaded it into the user-lease docs so IdM operators have a concrete delegated-RBAC setup path before consuming `eigenstate.ipa.user_lease`

## 1.10.4 - 2026-04-10

- merged the full devsec hardening branch stack into `main`, covering TLS verification hardening, clearer authorization failures, explicit `kinit` path handling, stderr sanitization, cache-example hygiene, vault output guidance, and password `kinit` fallback validation
- tightened the collection validation lane so the merged tree now passes both workstation validation and bastion-side source validation against a live IdM lab through the documented jump-host boundary
- hardened unit-test exception assertions across ansible-core versions so the validation path stays stable on newer controller environments instead of depending on one local Python and Ansible combination
- refreshed release references for the `1.10.4` security-hardening release

## 1.10.3 - 2026-04-08

- added a RHOSO branch to the OpenShift ecosystem docs with separate operator and tenant use-case pages instead of folding cloud and tenant identity into one page
- threaded the new RHOSO branch through the OpenShift primer, AAP integration guide, docs map, docs home, and repository README so the navigation flow stays aligned with the rest of the project
- refreshed release references for the `1.10.3` docs release

## 1.10.2 - 2026-04-08

- broadened the OpenShift docs stream into an explicit OpenShift ecosystem primer while keeping the stable `openshift-primer.md` URL
- added RHACM, RHACS, and Quay workflow branches plus focused use-case pages for event-driven remediation, security-response paths, and registry automation
- refactored the repo and Pages navigation so the ecosystem primer now routes naturally into the adjacent product-specific branches instead of collapsing into one long OpenShift page

## 1.10.1 - 2026-04-08

- refactored the repository `README.md` to remove the global navigation-button dump and group `<kbd>` links by topic adjacency instead
- trimmed redundant README content so the repository front page reads more cleanly without changing the GitHub Pages docs set

## 1.10.0 - 2026-04-08

- added `eigenstate.ipa.user_lease` for narrow IdM-native control of `krbPrincipalExpiration` and optional `krbPasswordExpiration` on existing users
- validated delegated non-admin operation in the lab with RBAC scoped to governed group membership and expiry-attribute writes
- added user-lease reference, capabilities, and use-case docs and wired the new module into the docs home, documentation map, AAP guide, ephemeral-access guide, and Vault/CyberArk primer
- fixed the broken Mermaid flowchart in section 8 of `keytab-use-cases.md` so the GitHub Pages render no longer fails

## 1.9.3 - 2026-04-08

- added the collection-wide `ephemeral-access-capabilities` guide to frame delegated temporary users and Kerberos key retirement as IdM-native lease-like access patterns
- linked the new temporary-access guidance into the docs home, documentation map, AAP integration guide, and Vault/CyberArk primer without collapsing those pages into circular comparison prose

## 1.9.2 - 2026-04-08

- refined the Vault/CyberArk primer to explain the Kerberos and keytab angle on the ephemeral-secrets gap: not dynamic leases, but a stronger machine-identity story when immediate key retirement fits the workflow
- expanded the keytab reference, capabilities, and use-case docs to frame key rotation as an operationally short-lived credential pattern for dedicated automation principals

## 1.9.1 - 2026-04-08

- restored the detailed Vault versus CyberArk versus Eigenstate comparison tables in the primer, with stronger emphasis on where IdM-native Kerberos, PKI, policy, OTP, and inventory workflows materially differentiate the collection
- kept the tighter `1.9.0` primer flow while bringing back the side-by-side capability framing for challenger positioning

## 1.9.0 - 2026-04-08

- added inventory hostvar enrichment controls with `hostvars_enabled` and `hostvars_include`, plus validation tests and updated inventory guidance for real Ansible hostvar merge behavior
- refactored the docs home, documentation map, and AAP integration pages around the current shipped plugin surface and the collection's highest-value controller-side workflows
- refreshed the Vault/CyberArk primer to reflect the current collection state and tightened cross-plugin use cases for DNS plus principal/cert, sudo plus HBAC, and OTP plus vault recovery flows

## 1.8.2 - 2026-04-08

- updated the AAP integration guide to reflect the current collection surface, including `vault_write`, `dns`, `selinuxmap`, `sudo`, and `hbacrule`
- reorganized the AAP page around the real execution-environment dependency stacks and current controller-side runtime patterns
- refreshed release references for the AAP documentation update

## 1.8.1 - 2026-04-08

- refactored the docs landing flow so the Vault/CyberArk primer is the single comparison entry point
- removed redundant primer callouts from the docs home capability section and simplified the reading order around rotation and AAP guidance
- refreshed release references for the docs-navigation cleanup

## 1.8.0 - 2026-04-08

- added `eigenstate.ipa.dns` for read-only inspection of IdM DNS records through `show` and `find` operations
- DNS lookup covers forward records, reverse records, zone-apex entry checks, and broad zone searches over the record families the IdM DNS APIs expose directly
- added unit coverage for DNS lookup behavior, including missing-record handling, apex markers, and record-type filtering
- added DNS plugin reference, capability, and use-case documentation
- refreshed the collection overview, docs home, and documentation map to surface the new DNS lookup release

## 1.7.0 - 2026-04-08

- added `eigenstate.ipa.sudo` for read-only inspection of IdM sudo rules, sudo commands, and sudo command groups
- `sudo` supports `show` and `find` operations across rules, commands, and command groups with the established controller-side `ipalib` auth pattern
- added unit coverage for sudo rule, command, and command-group lookup behavior, including missing-object handling
- added sudo plugin reference, capability, and use-case documentation
- refreshed the collection overview, docs home, and documentation map to surface the new sudo lookup release

## 1.6.4 - 2026-04-08

- normalized Mermaid flowcharts from top-down to left-to-right layout across the docs set to remove the repeated vertical spacing artifact in GitHub Pages renders
- refreshed release references to match the diagram-rendering cleanup

## 1.6.3 - 2026-04-08

- restructured the documentation map into a problem-oriented landing page instead of a flat link dump
- aligned `docs/documentation-map.md` and `docs/README.md` so the docs navigation model is consistent

## 1.6.2 - 2026-04-08

- clarified the Vault/CyberArk primer wording for session recording so it reflects IdM user and group policy with host-side SSSD resolution
- updated the release docs and landing pages to keep the comparison and rotation guidance aligned

## 1.6.1 - 2026-04-08

- added collection-wide rotation workflow guidance for static secrets, keytabs, and certificates
- added a Vault/CyberArk primer to position `eigenstate.ipa` for operators coming from external secrets and PAM platforms
- expanded the docs landing pages, navigation map, and related guides to surface the new rotation and comparison material

## 1.6.0 - 2026-04-07

- added `eigenstate.ipa.selinuxmap` for read-only inspection of SELinux user map state from FreeIPA/IdM
- added `eigenstate.ipa.hbacrule` for read-only inspection of HBAC rule state and live access testing via the FreeIPA `hbactest` engine
- `selinuxmap` supports `show` (named map lookup) and `find` (bulk enumeration); returns `selinuxuser`, `enabled`, `hbacrule` (linked rule name extracted from `seealso` DN), direct member lists, and `description`
- `hbacrule` supports `show`, `find`, and `test`; the `test` operation invokes `hbactest` and returns `denied`, `matched`, and `notmatched`
- both plugins follow the established ccache lifecycle pattern and support `result_format=record` and `result_format=map_record`
- fixed `hbacrule operation=test` to accept the top-level `ipalib` `hbactest` response shape seen on live IdM servers
- fixed `selinuxmap` and `hbacrule` `DOCUMENTATION` parsing so `ansible-doc`, Ansible runtime loading, and Galaxy import can load the plugins cleanly
- added selinuxmap plugin reference, capability, and use-case documentation
- added hbacrule plugin reference, capability, and use-case documentation
- bumped collection tags to include `selinux`, `hbac`, and `policy`

## 1.5.1 - 2026-04-06

- fixed the `eigenstate.ipa.vault_write` module `DOCUMENTATION` block so `ansible-doc` and Ansible Galaxy can parse the module docs cleanly

## 1.5.0 - 2026-04-06

- added `eigenstate.ipa.vault_write` for IdM vault lifecycle management from Ansible
- added `plugins/module_utils/ipa_client.py` as a shared Kerberos auth and `ipalib` connection layer for write-capable IPA operations
- `vault_write` supports `state: present`, `state: absent`, and `state: archived`
- supports standard, symmetric, and asymmetric vault types
- standard vault writes are idempotent; symmetric and asymmetric archive operations remain write-always because content comparison would require decryption
- supports delta-only member management via `members` and `members_absent`
- supports Ansible check mode
- added vault-write reference, capability, and use-case documentation
- refreshed collection metadata and docs to describe the integrated inventory, vault, principal, keytab, cert, OTP, and vault-write feature set

## 1.4.0 - 2026-04-06

- added `eigenstate.ipa.otp` for OTP token issue, lookup, revoke, and host enrollment password generation
- fixed repeated OTP lookups in one Ansible process by disconnecting the managed `ipalib` RPC backend before ccache cleanup
- aligned structured `map` and `map_record` OTP results with the Ansible lookup return contract
- added explicit `verify=false` handling for OTP lookup TLS behavior
- refreshed collection metadata and docs to describe the integrated inventory, vault, principal, keytab, cert, and otp feature set

## 1.3.0 - 2026-04-06

- added `eigenstate.ipa.principal` for Kerberos principal existence, key, lock, and last-auth inspection
- fixed repeated principal lookups in one Ansible process by disconnecting the managed `ipalib` RPC backend before ccache cleanup
- aligned `map_record` results with the Ansible lookup return contract
- added explicit `verify=false` handling for principal lookup TLS behavior
- refreshed collection metadata and docs to describe the integrated inventory, vault, principal, keytab, and cert feature set

## 1.2.0 - 2026-04-06

- added `eigenstate.ipa.cert` for IdM CA certificate request, retrieve, and find operations
- fixed repeated cert lookups in one Ansible process by disconnecting the managed `ipalib` RPC backend before ccache cleanup
- fixed `operation=find` principal filtering to use the supported IdM CA owner arguments
- fixed structured `map` and `map_record` cert results to satisfy the Ansible lookup return contract
- excluded transient `.ansible` state from built collection artifacts
- refreshed collection metadata and docs to describe the integrated inventory, vault, keytab, and cert feature set

## 1.1.1 - 2026-04-06

- refreshed release metadata to match the keytab-enabled collection scope
- updated the packaged README, LLM metadata, Galaxy metadata, and citation file for the 1.1.1 release

## 1.1.0 - 2026-04-06

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

## 1.0.4 - 2026-04-05

- hardened the vault lookup plugin by normalizing lookup terms and scope values to text before IPA calls
- added regression tests covering normalized term and scope handling in the vault lookup
- corrected the sealed-artifact workflow documentation to reflect the certmonger prerequisite and the validated collection retrieval pattern

## 1.0.3 - 2026-04-03

- removed Mermaid from the packaged root README so Galaxy renders the overview cleanly

## 1.0.2 - 2026-04-03

- tightened documentation tone in the reference and capability guides
- prepared the next Galaxy release after the 1.0.1 README link fix

## 1.0.1 - 2026-04-03

- fixed Galaxy README links by switching packaged documentation links to absolute GitHub Pages URLs

## 1.0.0 - 2026-04-03

- initial `eigenstate.ipa` collection release
- added `eigenstate.ipa.idm` dynamic inventory plugin
- added `eigenstate.ipa.vault` lookup plugin
- added operator, capability, use-case, and AAP integration documentation

---
layout: default
title: Rewrite Validation
diataxis: reference
diataxis_type: reference
audience: Documentation maintainers
outcome: Record validation commands, results, known warnings, and remaining risks for the Diataxis rewrite.
authority_boundary:
  - collection
workflow_boundary: read-only
evidence_shape:
  - command-output
public_status: validation-report
source_material:
  - rewrite-audit.md
last_verified: 2026-05-07
---

# Rewrite Validation

This report records local validation for the documentation rewrite branch.

## Commands Run

| Check | Command | Result |
| --- | --- | --- |
| Git status | `git status --short --branch` | Completed. |
| Jekyll availability | `bundle exec jekyll build -s docs -d /tmp/eigenstate-ipa-site` or `jekyll build -s docs -d /tmp/eigenstate-ipa-site` | Not run locally; Ruby/Jekyll are not installed on this workstation. |
| Governance front matter | Python check over `docs/**/*.md` for `diataxis_type`, `authority_boundary`, `workflow_boundary`, `evidence_shape`, and `public_status` | Passed. |
| Docs data YAML | Python `yaml.safe_load` over `docs/_data/*.yml` | Passed. |
| Internal links | Python Markdown/HTML link resolver for local docs links | Passed. |
| External spot check | `curl -L -I` for representative shields and published docs URLs | Passed with HTTP 200 for checked URLs. |
| Public language | `./scripts/validate-doc-language.sh` | Passed. |
| Governance language and secret hygiene | `./scripts/check-docs-language.py` | Passed with advisory warnings listed below. |
| Markdown YAML examples | `./scripts/validate-doc-examples.sh` | Passed. |
| Shell syntax | `bash -n scripts/validate-collection.sh scripts/validate-doc-language.sh scripts/validate-doc-examples.sh` | Passed. |
| Repository validation | `./scripts/validate-collection.sh` | Passed. |
| Compatibility unit test after legacy stubs | `python3 -m unittest tests.test_compatibility_warnings` | Passed. |
| CSS visual rule scan | `rg -n "letter-spacing:\\s*-|clamp\\(" docs/assets/site.css docs/_layouts docs/_includes` | Passed after cleanup. |

## Validation Notes

- The local machine does not have Ruby, `gem`, `bundle`, or `jekyll`, so the
  GitHub Pages build could not be executed locally. The repository workflow
  still uses `actions/jekyll-build-pages@v1`.
- `ansible-test` was skipped by `validate-collection.sh` because `python3.11`
  is not installed locally.
- `yamllint` reported warnings for new `docs/_data/*.yml` files: missing YAML
  document starts and a few long data values. These were warnings, not
  failures.
- The new language checker and existing secret-doc checker warn on source
  generated reference examples for vault, keytab, OTP, and `vault_write`
  examples that do not show nearby `no_log: true`. The how-to and tutorial
  pages show the safe task pattern. The warnings are advisory unless
  `EIGENSTATE_DOCS_SECRET_LINT_STRICT=1`.

## Remaining Risks

- The site shell has not been visually inspected from a local Jekyll preview on
  this workstation.
- Legacy compatibility stubs preserve old URLs, but external links to section
  anchors inside legacy pages may land at the stub top rather than an exact new
  anchor.
- Reference examples are generated from source documentation. If strict secret
  lint becomes required, source examples or generated reference rendering should
  be updated to include explicit `no_log: true` context for secret-bearing
  lookup examples.

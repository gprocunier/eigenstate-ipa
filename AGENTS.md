# Repository Guidance

This repository is a public open-source Ansible collection. Documentation and
automation changes should stand on technical behavior, source evidence, and
clear operational boundaries.

## Documentation Posture

- Write as an operator explaining how Identity Management state becomes usable
  automation evidence.
- Keep Red Hat IdM, FreeIPA, Ansible Automation Platform, OpenShift,
  Kubernetes, Kerberos, certificates, DNS, sudo, HBAC, SELinux maps, and vaults
  as factual technical integration surfaces.
- Do not frame the project around private field activity, commercial motions,
  or promotional claims.
- Avoid broad claims that IdM replaces general-purpose vault, PAM, or dynamic
  secret-lease systems. State the IdM-native boundary precisely.

## Diataxis Boundaries

- Tutorial pages teach a reader by doing one safe learning path.
- How-to pages complete one production task with clear prerequisites, steps,
  expected results, and troubleshooting.
- Reference pages document exact options, return shapes, roles, playbooks,
  schemas, dependencies, and compatibility.
- Explanation pages describe architecture, authority, threat boundaries,
  tradeoffs, and non-goals.

Do not mix these page types unless the page is an index or routing page.

## Authority And Workflow Boundaries

Every rewritten page should declare these front matter keys:

```yaml
diataxis_type:
authority_boundary:
workflow_boundary:
evidence_shape:
public_status:
```

Use repository data files under `docs/_data/` as the controlled vocabulary.
When a workflow can expose or mutate sensitive material, state whether it is
read-only, render-only, preflight, check-mode, or mutating.

## Evidence Rules

- Tie reference facts back to plugin documentation blocks, role defaults,
  argument specs, playbooks, tests, or generated `ansible-doc` output.
- Prefer examples that produce reviewable JSON, YAML, Markdown, manifests,
  inventory output, or command output.
- Do not show real credentials, tokens, keytabs, private keys, or certificate
  material. Use placeholders and redacted examples.
- Use `no_log: true` near secret-bearing Ansible examples.

## Workflow

- Keep the Jekyll Pages workflow unless the whole site is intentionally
  converted and the workflow is updated in the same change.
- Do not add binary fonts or generated private planning files.
- Run lightweight validation for documentation governance changes, including
  the docs language checker and YAML/Python syntax checks where practical.

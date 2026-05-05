#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMP_BUILD_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "${TEMP_BUILD_DIR}"
}
trap cleanup EXIT

COLLECTIONS_ROOT="${TEMP_BUILD_DIR}/collections"
mkdir -p "${COLLECTIONS_ROOT}/ansible_collections/eigenstate"
ln -s "${PROJECT_ROOT}" "${COLLECTIONS_ROOT}/ansible_collections/eigenstate/ipa"

echo "==> Checking support matrix metadata"
python3 - "${PROJECT_ROOT}" <<'PY2'
import sys
from pathlib import Path

import yaml

project_root = Path(sys.argv[1])
runtime = yaml.safe_load((project_root / "meta/runtime.yml").read_text())
requires_ansible = runtime.get("requires_ansible")
if requires_ansible != ">=2.15.0":
    raise SystemExit(
        "meta/runtime.yml requires_ansible must remain aligned with the "
        "documented and tested lower bound >=2.15.0"
    )

docs = {
    "docs/support-matrix.md",
    "docs/test-strategy.md",
    "docs/release-process.md",
}
missing = [path for path in docs if not (project_root / path).is_file()]
if missing:
    raise SystemExit(f"missing release engineering docs: {', '.join(sorted(missing))}")
PY2

echo "==> Parsing YAML sources"
python3 - "${PROJECT_ROOT}" <<'PY2'
import sys
from pathlib import Path

import yaml

project_root = Path(sys.argv[1])
yaml_files = []
for pattern in ("*.yml", "*.yaml"):
    yaml_files.extend(project_root.rglob(pattern))

failures = []
for path in sorted(set(yaml_files)):
    if any(part in {".git", "__pycache__"} for part in path.parts):
        continue
    try:
        yaml.safe_load(path.read_text())
    except Exception as exc:  # pragma: no cover - CLI validation
        failures.append(f"{path}: {exc}")

if failures:
    print("YAML parsing failed for:")
    for failure in failures:
        print(f"  - {failure}")
    sys.exit(1)

print("YAML parsing succeeded.")
PY2

echo "==> Checking Python syntax"
mapfile -t python_files < <(find "${PROJECT_ROOT}/plugins" "${PROJECT_ROOT}/tests" -type f -name '*.py' | sort)
if ((${#python_files[@]} > 0)); then
  PYTHONPYCACHEPREFIX="${TEMP_BUILD_DIR}/pycache" python3 -m py_compile "${python_files[@]}"
else
  echo "No Python files found to compile."
fi

if command -v yamllint >/dev/null 2>&1; then
  echo "==> Running yamllint"
  yamllint -c "${PROJECT_ROOT}/.yamllint"     "${PROJECT_ROOT}/galaxy.yml"     "${PROJECT_ROOT}/meta/runtime.yml"     "${PROJECT_ROOT}/docs"     "${PROJECT_ROOT}/.github/workflows"
else
  echo "==> yamllint not installed; skipping"
fi

if command -v ansible-lint >/dev/null 2>&1; then
  echo "==> Running ansible-lint on collection metadata"
  ansible-lint     "${PROJECT_ROOT}/galaxy.yml"     "${PROJECT_ROOT}/meta/runtime.yml"
else
  echo "==> ansible-lint not installed; skipping"
fi

if command -v ansible-test >/dev/null 2>&1; then
  echo "==> Running ansible-test sanity"
  test_python="${EIGENSTATE_ANSIBLE_TEST_PYTHON:-3.11}"
  require_ansible_test="${EIGENSTATE_REQUIRE_ANSIBLE_TEST:-0}"
  if command -v "python${test_python}" >/dev/null 2>&1 || [[ "${require_ansible_test}" == "1" ]]; then
    (
      cd "${COLLECTIONS_ROOT}/ansible_collections/eigenstate/ipa"
      ansible-test sanity --python "${test_python}" --color no --truncate 0
    )
  else
    echo "python${test_python} not installed; skipping ansible-test sanity"
  fi
elif [[ "${EIGENSTATE_REQUIRE_ANSIBLE_TEST:-0}" == "1" ]]; then
  echo "ansible-test not installed but EIGENSTATE_REQUIRE_ANSIBLE_TEST=1" >&2
  exit 1
else
  echo "==> ansible-test not installed; skipping sanity"
fi

if command -v ansible-doc >/dev/null 2>&1; then
  echo "==> Validating plugin docs parse"
  while IFS= read -r file; do
    name="$(basename "${file}" .py)"
    ANSIBLE_COLLECTIONS_PATH="${TEMP_BUILD_DIR}"       ansible-doc -t inventory -M "${PROJECT_ROOT}/plugins/inventory" "${name}" >/dev/null
  done < <(find "${PROJECT_ROOT}/plugins/inventory" -maxdepth 1 -type f -name '*.py' ! -name '__init__.py' | sort)

  while IFS= read -r file; do
    name="$(basename "${file}" .py)"
    ANSIBLE_COLLECTIONS_PATH="${TEMP_BUILD_DIR}"       ansible-doc -t lookup -M "${PROJECT_ROOT}/plugins/lookup" "${name}" >/dev/null
  done < <(find "${PROJECT_ROOT}/plugins/lookup" -maxdepth 1 -type f -name '*.py' ! -name '__init__.py' | sort)

  while IFS= read -r file; do
    name="$(basename "${file}" .py)"
    ANSIBLE_COLLECTIONS_PATH="${TEMP_BUILD_DIR}"       ansible-doc -t module -M "${PROJECT_ROOT}/plugins/modules" "${name}" >/dev/null
  done < <(find "${PROJECT_ROOT}/plugins/modules" -maxdepth 1 -type f -name '*.py' ! -name '__init__.py' | sort)
else
  echo "==> ansible-doc not installed; skipping"
fi

echo "==> Validating public documentation language"
"${PROJECT_ROOT}/scripts/validate-doc-language.sh"

echo "==> Validating documentation examples"
"${PROJECT_ROOT}/scripts/validate-doc-examples.sh"

if command -v ansible-playbook >/dev/null 2>&1; then
  echo "==> Validating AAP EE scaffold"
  EIGENSTATE_EE_VALIDATE_OUTPUT_DIR="${TEMP_BUILD_DIR}/eigenstate-idm-ee" \
    "${PROJECT_ROOT}/scripts/validate-ee-scaffold.sh"

  echo "==> Checking Phase 2 role playbook syntax"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/sealed-artifact-delivery.yml"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/temporary-access-window.yml"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/cert-expiry-report.yml"

  echo "==> Running Phase 2 static validation playbook"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ANSIBLE_LOCALHOST_WARNING=false \
    ansible-playbook "${PROJECT_ROOT}/playbooks/phase2-static-validation.yml"

  echo "==> Checking Phase 4 role playbook syntax"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/render-openshift-oidc-config.yml"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/validate-openshift-idm-groups.yml"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/validate-keycloak-idm-claims.yml"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/validate-openshift-breakglass-path.yml"

  echo "==> Running Phase 4 static validation playbook"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ANSIBLE_LOCALHOST_WARNING=false \
    ansible-playbook "${PROJECT_ROOT}/playbooks/phase4-static-validation.yml"

  echo "==> Checking Phase 5 workload delivery playbook syntax"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/render-kubernetes-secret-from-idm-vault.yml"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/render-kubernetes-tls-secret-from-idm-cert.yml"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/render-keytab-secret.yml"

  echo "==> Running Phase 5 static validation playbook"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ANSIBLE_LOCALHOST_WARNING=false \
    ansible-playbook "${PROJECT_ROOT}/playbooks/phase5-static-validation.yml"

  echo "==> Checking Phase 6 reporting playbook syntax"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/report-idm-readiness.yml"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/report-certificate-inventory.yml"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/report-keytab-rotation-candidates.yml"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/report-temporary-access.yml"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/report-policy-drift.yml"

  echo "==> Running Phase 6 static validation playbook"
  ANSIBLE_COLLECTIONS_PATH="${COLLECTIONS_ROOT}" \
    ANSIBLE_LOCALHOST_WARNING=false \
    ansible-playbook "${PROJECT_ROOT}/playbooks/phase6-static-validation.yml"
else
  echo "==> ansible-playbook not installed; skipping AAP EE role checks"
fi

echo "==> Checking docs for likely secret-bearing examples"
python3 "${PROJECT_ROOT}/scripts/check-docs-no-secret-debug.py"

if command -v ansible-galaxy >/dev/null 2>&1; then
  echo "==> Building collection tarball"
  ansible-galaxy collection build "${PROJECT_ROOT}"     --output-path "${TEMP_BUILD_DIR}" >/dev/null
else
  echo "==> ansible-galaxy not installed; skipping collection build"
fi

if [[ -d "${PROJECT_ROOT}/tests" ]]; then
  echo "==> Running unit tests"
  mapfile -t test_files < <(find "${PROJECT_ROOT}/tests" -maxdepth 1 -type f -name 'test_*.py' | sort)
  for test_file in "${test_files[@]}"; do
    test_module="$(basename "${test_file}" .py)"
    echo "  -> ${test_module}"
    python3 -m unittest "tests.${test_module}"
  done
else
  echo "==> tests directory not present; skipping unit tests"
fi

echo "Validation complete."

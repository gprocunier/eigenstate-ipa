#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMP_BUILD_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "${TEMP_BUILD_DIR}"
}
trap cleanup EXIT

echo "==> Parsing YAML sources"
python3 - "${PROJECT_ROOT}" <<'PY'
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
PY

echo "==> Checking Python syntax"
PYTHONPYCACHEPREFIX="${TEMP_BUILD_DIR}/pycache" python3 -m py_compile \
  "${PROJECT_ROOT}/plugins/inventory/idm.py" \
  "${PROJECT_ROOT}/plugins/lookup/vault.py" \
  "${PROJECT_ROOT}/plugins/lookup/principal.py" \
  "${PROJECT_ROOT}/plugins/lookup/keytab.py" \
  "${PROJECT_ROOT}/plugins/lookup/cert.py" \
  "${PROJECT_ROOT}/plugins/lookup/otp.py"

if command -v yamllint >/dev/null 2>&1; then
  echo "==> Running yamllint"
  yamllint -c "${PROJECT_ROOT}/.yamllint" \
    "${PROJECT_ROOT}/galaxy.yml" \
    "${PROJECT_ROOT}/meta/runtime.yml" \
    "${PROJECT_ROOT}/docs"
else
  echo "==> yamllint not installed; skipping"
fi

if command -v ansible-lint >/dev/null 2>&1; then
  echo "==> Running ansible-lint on collection metadata"
  if ! ansible-lint \
    "${PROJECT_ROOT}/galaxy.yml" \
    "${PROJECT_ROOT}/meta/runtime.yml"; then
    echo "ansible-lint reported issues; continuing because this validation path is advisory." >&2
  fi
else
  echo "==> ansible-lint not installed; skipping"
fi

if command -v ansible-doc >/dev/null 2>&1; then
  echo "==> Validating plugin docs parse"
  ANSIBLE_COLLECTIONS_PATH="${TEMP_BUILD_DIR}" \
    ansible-doc -t inventory -M "${PROJECT_ROOT}/plugins/inventory" idm >/dev/null
  ANSIBLE_COLLECTIONS_PATH="${TEMP_BUILD_DIR}" \
    ansible-doc -t lookup -M "${PROJECT_ROOT}/plugins/lookup" vault >/dev/null
  ANSIBLE_COLLECTIONS_PATH="${TEMP_BUILD_DIR}" \
    ansible-doc -t lookup -M "${PROJECT_ROOT}/plugins/lookup" principal >/dev/null
  ANSIBLE_COLLECTIONS_PATH="${TEMP_BUILD_DIR}" \
    ansible-doc -t lookup -M "${PROJECT_ROOT}/plugins/lookup" keytab >/dev/null
  ANSIBLE_COLLECTIONS_PATH="${TEMP_BUILD_DIR}" \
    ansible-doc -t lookup -M "${PROJECT_ROOT}/plugins/lookup" cert >/dev/null
  ANSIBLE_COLLECTIONS_PATH="${TEMP_BUILD_DIR}" \
    ansible-doc -t lookup -M "${PROJECT_ROOT}/plugins/lookup" otp >/dev/null
else
  echo "==> ansible-doc not installed; skipping"
fi

if command -v ansible-galaxy >/dev/null 2>&1; then
  echo "==> Building collection tarball"
  ansible-galaxy collection build "${PROJECT_ROOT}" \
    --output-path "${TEMP_BUILD_DIR}" >/dev/null
else
  echo "==> ansible-galaxy not installed; skipping collection build"
fi

if [[ -d "${PROJECT_ROOT}/tests" ]]; then
  echo "==> Running unit tests"
  python3 -m unittest discover -s "${PROJECT_ROOT}/tests" -p 'test_*.py'
else
  echo "==> tests directory not present; skipping unit tests"
fi

echo "Validation complete."

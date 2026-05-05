#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${EIGENSTATE_EE_VALIDATE_OUTPUT_DIR:-}"
TEMP_DIR=""

if [[ -z "${OUTPUT_DIR}" ]]; then
  TEMP_DIR="$(mktemp -d)"
  OUTPUT_DIR="${TEMP_DIR}/eigenstate-idm-ee"
fi

cleanup() {
  if [[ -n "${TEMP_DIR}" ]]; then
    rm -rf "${TEMP_DIR}"
  fi
}
trap cleanup EXIT

ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/aap-ee-render.yml"
ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/aap-ee-build.yml"
ansible-playbook --syntax-check "${PROJECT_ROOT}/playbooks/aap-ee-smoke.yml"

ansible-playbook "${PROJECT_ROOT}/playbooks/aap-ee-render.yml" \
  -e "eigenstate_ee_output_dir=${OUTPUT_DIR}"

for path in \
  execution-environment.yml \
  requirements.yml \
  bindep.txt \
  python-requirements.txt \
  ansible.cfg.example \
  README.md; do
  test -f "${OUTPUT_DIR}/${path}"
done

python3 - "${PROJECT_ROOT}" "${OUTPUT_DIR}" <<'PY'
import re
import sys
from pathlib import Path

import yaml

project_root = Path(sys.argv[1])
output_dir = Path(sys.argv[2])
defaults = yaml.safe_load(
    (project_root / "roles/aap_execution_environment/defaults/main.yml").read_text()
)
requirements = yaml.safe_load((output_dir / "requirements.yml").read_text())

expected = defaults["eigenstate_ee_collection_version"]
collections = requirements.get("collections", [])
match = next(
    (item for item in collections if item.get("name") == "eigenstate.ipa"),
    None,
)
if match is None:
    raise SystemExit("rendered requirements.yml does not include eigenstate.ipa")
if match.get("version") != expected:
    raise SystemExit(
        "rendered eigenstate.ipa collection version "
        f"{match.get('version')!r} does not match role default {expected!r}"
    )

runtime = yaml.safe_load((project_root / "meta/runtime.yml").read_text())
if runtime.get("requires_ansible") != ">=2.15.0":
    raise SystemExit("runtime lower bound drifted from documented support matrix")

version = yaml.safe_load((project_root / "galaxy.yml").read_text())["version"]
minimum = re.sub(r"^[<>=!~ ]+", "", expected)
if minimum != version:
    raise SystemExit(
        f"EE default {expected!r} must track the current collection version {version!r}"
    )

print("AAP EE scaffold validation passed.")
PY

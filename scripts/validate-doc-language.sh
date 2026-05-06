#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 - "${PROJECT_ROOT}" <<'PY'
import re
import sys
from pathlib import Path

project_root = Path(sys.argv[1])
paths = [
    project_root / "README.md",
    project_root / "llms.txt",
    project_root / "CITATION.cff",
    project_root / "galaxy.yml",
]
paths.extend(sorted((project_root / "docs").glob("*.md")))
paths.extend(sorted((project_root / "roles").glob("*/README.md")))

patterns = [
    re.compile(r"\bseller(s)?\b", re.IGNORECASE),
    re.compile(r"\bpre[- ]?sales\b", re.IGNORECASE),
    re.compile(r"\bsales motion(s)?\b", re.IGNORECASE),
    re.compile(r"\bseller demo\b", re.IGNORECASE),
    re.compile(r"\bphase\s*\d+\b", re.IGNORECASE),
    re.compile(r"\bphase[-_]?\d+\b", re.IGNORECASE),
    re.compile(r"\bgolden[- ]path\b", re.IGNORECASE),
    re.compile(r"\bmutation_phase\b", re.IGNORECASE),
    re.compile(r"\bremediation_phase\b", re.IGNORECASE),
]

public_name_roots = [
    project_root / "docs",
    project_root / "playbooks",
    project_root / "aap",
]
public_name_patterns = [
    re.compile(r"phase[-_]?\d+", re.IGNORECASE),
    re.compile(r"golden[-_]path", re.IGNORECASE),
]

failures = []
for path in paths:
    if not path.is_file():
        continue
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for pattern in patterns:
            if pattern.search(line):
                rel = path.relative_to(project_root)
                failures.append(f"{rel}:{lineno}: {pattern.pattern}: {line.strip()}")

for root in public_name_roots:
    if not root.exists():
        continue
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(project_root)
        rel_text = str(rel)
        if rel_text.startswith("docs/assets/vendor/"):
            continue
        for pattern in public_name_patterns:
            if pattern.search(rel_text):
                failures.append(f"{rel}: public filename matches {pattern.pattern}")

if failures:
    print("Public documentation language validation failed:")
    for failure in failures:
        print(f"  - {failure}")
    sys.exit(1)

print("Public documentation language validation passed.")
PY

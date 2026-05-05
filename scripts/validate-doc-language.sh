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

if failures:
    print("Public documentation language validation failed:")
    for failure in failures:
        print(f"  - {failure}")
    sys.exit(1)

print("Public documentation language validation passed.")
PY

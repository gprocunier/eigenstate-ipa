#!/usr/bin/env python3
"""Advisory lint for secret-bearing documentation examples."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SEARCH_ROOTS = [PROJECT_ROOT / "README.md", PROJECT_ROOT / "docs"]
LOOKUP_RE = re.compile(r"lookup\('eigenstate\.ipa\.(vault|keytab|otp)'")


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for root in SEARCH_ROOTS:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(sorted(root.rglob("*.md")))
    return files


def has_nearby_no_log(lines: list[str], index: int) -> bool:
    start = max(0, index - 2)
    end = min(len(lines), index + 10)
    return any("no_log: true" in line for line in lines[start:end])


def main() -> int:
    warnings: list[str] = []
    for path in iter_markdown_files():
        relpath = path.relative_to(PROJECT_ROOT)
        lines = path.read_text().splitlines()
        for index, line in enumerate(lines):
            if LOOKUP_RE.search(line) and not has_nearby_no_log(lines, index):
                warnings.append(f"{relpath}:{index + 1}: lookup without nearby no_log: true")

    if warnings:
        print("Potential secret-bearing docs examples need review:")
        for warning in warnings:
            print(f"  - {warning}")
        if os.environ.get("EIGENSTATE_DOCS_SECRET_LINT_STRICT") == "1":
            return 1
        print("Docs secret lint is advisory unless EIGENSTATE_DOCS_SECRET_LINT_STRICT=1.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

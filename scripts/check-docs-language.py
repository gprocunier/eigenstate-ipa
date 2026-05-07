#!/usr/bin/env python3
"""Public documentation language and secret-hygiene checks."""

from __future__ import annotations

import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOTS = [
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "llms.txt",
    PROJECT_ROOT / "docs",
    PROJECT_ROOT / "playbooks",
]
ROLE_READMES = PROJECT_ROOT / "roles"
SKIP_PATH_PARTS = {
    ".git",
    "__pycache__",
    "_site",
    "assets",
    "vendor",
    "fonts",
}
SKIP_FILES = {
    PROJECT_ROOT / "docs" / "_data" / "forbidden_terms.yml",
}
TEXT_SUFFIXES = {".md", ".html", ".txt", ".yml", ".yaml"}
PLACEHOLDER_RE = re.compile(
    r"^(TODO|CHANGEME|REDACTED|<[^>]+>|\{\{[^}]+\}\}|\$\{[^}]+\}|example|dummy|changeme)$",
    re.IGNORECASE,
)


def load_terms() -> tuple[list[str], list[str]]:
    data_file = PROJECT_ROOT / "docs" / "_data" / "forbidden_terms.yml"
    if not data_file.is_file():
        return (["seller", "presales", "sales motion", "seller demo"], ["golden path"])

    block: list[str] = []
    filename_block: list[str] = []
    current: list[str] | None = None
    for raw_line in data_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "block:":
            current = block
            continue
        if line == "filename_block:":
            current = filename_block
            continue
        if line.endswith(":"):
            current = None
            continue
        if current is not None and line.startswith("- "):
            current.append(line[2:].strip().strip("'\""))
    return block, filename_block


def iter_public_files() -> list[Path]:
    files: list[Path] = []
    for root in PUBLIC_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path in SKIP_FILES:
                continue
            if any(part in SKIP_PATH_PARTS for part in path.parts):
                continue
            if path.suffix in TEXT_SUFFIXES:
                files.append(path)
    if ROLE_READMES.is_dir():
        files.extend(sorted(ROLE_READMES.glob("*/README.md")))
    return sorted(set(files))


def is_placeholder(value: str) -> bool:
    cleaned = value.strip().strip("'\"")
    if not cleaned:
        return True
    if PLACEHOLDER_RE.match(cleaned):
        return True
    if cleaned.startswith("{{") or cleaned.startswith("${"):
        return True
    return False


def has_nearby_no_log(lines: list[str], index: int) -> bool:
    start = max(0, index - 3)
    end = min(len(lines), index + 10)
    return any("no_log: true" in line for line in lines[start:end])


def main() -> int:
    block_terms, filename_terms = load_terms()
    block_patterns = [
        re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE) for term in block_terms
    ]
    filename_patterns = [
        re.compile(re.escape(term).replace(r"\-", "[-_ ]"), re.IGNORECASE)
        for term in filename_terms
    ]
    secret_assignment = re.compile(
        r"^\s*(password|passwd|token|secret|api_key|apikey|private_key)\s*[:=]\s*(.+?)\s*$",
        re.IGNORECASE,
    )
    pem_marker = re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")
    secret_lookup = re.compile(
        r"lookup\(['\"]eigenstate\.ipa\.(vault|keytab|otp)['\"]", re.IGNORECASE
    )
    no_log_false = re.compile(r"\bno_log:\s*false\b", re.IGNORECASE)

    failures: list[str] = []
    warnings: list[str] = []
    for path in iter_public_files():
        rel = path.relative_to(PROJECT_ROOT)
        rel_text = str(rel)
        for pattern in filename_patterns:
            if pattern.search(rel_text):
                failures.append(f"{rel}: filename contains blocked public term")

        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            lineno = index + 1
            for pattern in block_patterns:
                if pattern.search(line):
                    failures.append(f"{rel}:{lineno}: blocked public term: {line.strip()}")

            assignment = secret_assignment.match(line)
            if assignment and not is_placeholder(assignment.group(2)):
                failures.append(f"{rel}:{lineno}: non-placeholder secret-like value")

            if pem_marker.search(line):
                failures.append(f"{rel}:{lineno}: private key marker must not appear in public docs")

            if secret_lookup.search(line) and not has_nearby_no_log(lines, index):
                warnings.append(f"{rel}:{lineno}: secret-bearing lookup without nearby no_log: true")

            if no_log_false.search(line):
                window = "\n".join(lines[max(0, index - 4) : min(len(lines), index + 5)])
                if re.search(r"vault|keytab|cert|otp|secret", window, re.IGNORECASE):
                    failures.append(f"{rel}:{lineno}: no_log: false near secret-bearing context")

    if failures:
        print("Public documentation language validation failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    if warnings:
        print("Public documentation language validation warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    print("Public documentation language validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

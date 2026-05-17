#!/usr/bin/env python3
"""Public documentation language and secret-hygiene checks."""

from __future__ import annotations

import re
import shlex
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
GENERIC_EXPECTED_RESULT = (
    "The workflow produces the expected evidence or artifact for review"
)
EXPECTED_HEADING_RE = re.compile(r"^## Expected (Result|Output|Evidence)\s*$", re.IGNORECASE)
NEXT_H2_RE = re.compile(r"^##\s+")
ANSIBLE_PLAYBOOK_RE = re.compile(r"\bansible-playbook\s+([^\n`]+)")
PLACEHOLDER_RE = re.compile(
    r"^(TODO|CHANGEME|REDACTED|<[^>]+>|\{\{[^}]+\}\}|\$\{[^}]+\}|example|dummy|changeme)$",
    re.IGNORECASE,
)
PLACEHOLDER_SECTION_RE = re.compile(
    r"\b(TODO|TBD|fill this in|expected evidence goes here|expected output goes here)\b",
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


def frontmatter_value(lines: list[str], key: str) -> str | None:
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            return None
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return None


def expected_section_body(lines: list[str], heading_index: int) -> str:
    body: list[str] = []
    for line in lines[heading_index + 1 :]:
        if NEXT_H2_RE.match(line):
            break
        body.append(line)
    return "\n".join(body).strip()


def has_concrete_evidence(body: str) -> bool:
    if not body:
        return False
    if PLACEHOLDER_SECTION_RE.search(body):
        return False
    evidence_markers = [
        "```",
        "PLAY RECAP",
        "TASK [",
        "changed=",
        "ok=",
        "apiVersion:",
        "kind:",
        '"schema"',
        "'schema'",
    ]
    if any(marker in body for marker in evidence_markers):
        return True
    if re.search(r"^\s*[-*]\s+`?[/A-Za-z0-9_.-]+`?:", body, re.MULTILINE):
        return True
    return False


def extract_playbook_reference(command_tail: str) -> str | None:
    try:
        tokens = shlex.split(command_tail, comments=False, posix=True)
    except ValueError:
        tokens = command_tail.split()

    skip_next = False
    for token in tokens:
        if skip_next:
            skip_next = False
            continue
        if token in {"-i", "--inventory", "-e", "--extra-vars", "--limit", "-l"}:
            skip_next = True
            continue
        if token.startswith("-"):
            continue
        cleaned = token.strip("'\"")
        if cleaned.endswith((".yml", ".yaml")):
            return cleaned
    return None


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
        public_status = frontmatter_value(lines, "public_status")
        check_expected_sections = (
            path.suffix == ".md"
            and "_templates" not in path.parts
            and public_status not in {"draft", "stub"}
        )

        for index, line in enumerate(lines):
            lineno = index + 1
            for pattern in block_patterns:
                if pattern.search(line):
                    failures.append(f"{rel}:{lineno}: blocked public term: {line.strip()}")

            if GENERIC_EXPECTED_RESULT in line:
                failures.append(f"{rel}:{lineno}: generic expected-result placeholder")

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

            if check_expected_sections and EXPECTED_HEADING_RE.match(line):
                body = expected_section_body(lines, index)
                if not has_concrete_evidence(body):
                    failures.append(
                        f"{rel}:{lineno}: expected section lacks concrete output or artifact evidence"
                    )

            if path.suffix == ".md":
                for command in ANSIBLE_PLAYBOOK_RE.finditer(line):
                    playbook_ref = extract_playbook_reference(command.group(1))
                    if playbook_ref and playbook_ref.startswith("playbooks/"):
                        playbook_path = PROJECT_ROOT / playbook_ref
                        if not playbook_path.is_file():
                            failures.append(
                                f"{rel}:{lineno}: referenced playbook does not exist: {playbook_ref}"
                            )

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

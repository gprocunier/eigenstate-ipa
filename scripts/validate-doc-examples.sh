#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 - "${PROJECT_ROOT}" <<'PY'
import re
import shutil
import subprocess
import sys
import tempfile
import os
from pathlib import Path

import yaml

project_root = Path(sys.argv[1])
doc_paths = [
    project_root / "README.md",
    project_root / "llms.txt",
]
doc_paths.extend(
    sorted(
        path
        for path in (project_root / "docs").rglob("*.md")
        if "_templates" not in path.parts
        and "_site" not in path.parts
        and "assets" not in path.parts
    )
)
doc_paths.extend(sorted((project_root / "roles").glob("*/README.md")))

fence = re.compile(r"^```(?P<lang>[A-Za-z0-9_-]*)\s*$")
yaml_langs = {"yaml", "yml"}
ansible_playbook = re.compile(r"\bansible-playbook\s+([^\n`]+)")
parse_failures = []
syntax_blocks = []
reference_failures = []


def extract_playbook_reference(command_tail):
    try:
        import shlex

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

for path in doc_paths:
    if not path.is_file():
        continue
    lines = path.read_text(encoding="utf-8").splitlines()
    rel = path.relative_to(project_root)
    for lineno, line in enumerate(lines, 1):
        for match in ansible_playbook.finditer(line):
            playbook_ref = extract_playbook_reference(match.group(1))
            if playbook_ref and playbook_ref.startswith("playbooks/"):
                if not (project_root / playbook_ref).is_file():
                    reference_failures.append(
                        f"{rel}:{lineno}: referenced playbook does not exist: {playbook_ref}"
                    )

    in_block = False
    lang = ""
    start = 0
    block = []
    for lineno, line in enumerate(lines, 1):
        match = fence.match(line)
        if match and not in_block:
            in_block = True
            lang = match.group("lang").lower()
            start = lineno + 1
            block = []
            continue
        if in_block and line == "```":
            if lang in yaml_langs:
                text = "\n".join(block)
                rel = path.relative_to(project_root)
                if "{{" not in text and "{%" not in text and "{#" not in text:
                    try:
                        docs = list(yaml.safe_load_all(text))
                    except Exception as exc:
                        parse_failures.append(f"{rel}:{start}: {exc}")
                    else:
                        if any(isinstance(item, list) for item in docs):
                            for item in docs:
                                if isinstance(item, list) and any(
                                    isinstance(entry, dict) and "hosts" in entry
                                    for entry in item
                                ):
                                    syntax_blocks.append((rel, start, text))
                                    break
            in_block = False
            lang = ""
            block = []
            continue
        if in_block:
            block.append(line)

task_examples_path = project_root / "docs" / "_data" / "task_examples.yml"
if task_examples_path.is_file():
    try:
        task_examples = yaml.safe_load(task_examples_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        parse_failures.append(f"{task_examples_path.relative_to(project_root)}:1: {exc}")
        task_examples = {}

    if isinstance(task_examples, dict):
        for key, example in task_examples.items():
            if not isinstance(example, dict):
                continue
            known_files = {
                file_entry.get("name")
                for file_entry in example.get("files", [])
                if isinstance(file_entry, dict)
            }
            for match in ansible_playbook.finditer(str(example.get("run", ""))):
                playbook_ref = extract_playbook_reference(match.group(1))
                if not playbook_ref:
                    continue
                if playbook_ref.startswith("playbooks/"):
                    if not (project_root / playbook_ref).is_file():
                        reference_failures.append(
                            f"docs/_data/task_examples.yml:{key}: referenced playbook does not exist: {playbook_ref}"
                        )
                elif Path(playbook_ref).name not in known_files:
                    reference_failures.append(
                        f"docs/_data/task_examples.yml:{key}: run command references {playbook_ref} but the example does not define that file"
                    )
    else:
        parse_failures.append("docs/_data/task_examples.yml:1: expected mapping")

if parse_failures:
    print("Markdown YAML example parsing failed:")
    for failure in parse_failures:
        print(f"  - {failure}")
    sys.exit(1)

if reference_failures:
    print("Documentation command references failed:")
    for failure in reference_failures:
        print(f"  - {failure}")
    sys.exit(1)

if syntax_blocks and shutil.which("ansible-playbook"):
    with tempfile.TemporaryDirectory() as tmpdir:
        collections_root = Path(tmpdir) / "collections"
        collection_path = (
            collections_root / "ansible_collections" / "eigenstate" / "ipa"
        )
        collection_path.parent.mkdir(parents=True)
        collection_path.symlink_to(project_root, target_is_directory=True)
        env = dict(os.environ)
        env["ANSIBLE_COLLECTIONS_PATH"] = str(collections_root)
        for rel, start, text in syntax_blocks:
            playbook = Path(tmpdir) / f"doc-example-{len(list(Path(tmpdir).glob('*.yml')))}.yml"
            playbook.write_text(text, encoding="utf-8")
            result = subprocess.run(
                ["ansible-playbook", "--syntax-check", str(playbook)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
            )
            if result.returncode != 0:
                print(f"Ansible syntax check failed for {rel}:{start}")
                print(result.stdout)
                sys.exit(result.returncode)

print("Markdown YAML examples validated.")
PY

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
doc_paths.extend(sorted((project_root / "docs").glob("*.md")))
doc_paths.extend(sorted((project_root / "roles").glob("*/README.md")))

fence = re.compile(r"^```(?P<lang>[A-Za-z0-9_-]*)\s*$")
yaml_langs = {"yaml", "yml"}
parse_failures = []
syntax_blocks = []

for path in doc_paths:
    if not path.is_file():
        continue
    lines = path.read_text(encoding="utf-8").splitlines()
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

if parse_failures:
    print("Markdown YAML example parsing failed:")
    for failure in parse_failures:
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

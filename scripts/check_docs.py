"""Validate the new documentation entry points and example configuration."""

import ast
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]


def main():
    documents = [ROOT / "README.md",
                 ROOT / "docs/README.md", ROOT / "docs/01-快速入门.md",
                 ROOT / "docs/02-进阶教程.md", ROOT / "docs/03-命令与配置参考.md",
                 ROOT / "docs/管理端使用手册.md",
                 ROOT / "playground/README.md", ROOT / "examples/yolo-edge/README.md"]
    documents.extend(sorted((ROOT / "docs/案例库").rglob("*.md")))
    for document in documents:
        content = document.read_text(encoding="utf-8")
        for link in re.findall(r'\]\(([^)]+)\)', content):
            target = urlparse(link.strip("<>"))
            if target.scheme or not target.path:
                continue
            path = (document.parent / unquote(target.path)).resolve()
            if not path.exists():
                raise SystemExit(f"Broken link: {document.relative_to(ROOT)} -> {link}")
        if content.count("```") % 2:
            raise SystemExit(f"Unclosed code fence: {document}")

    cli_tree = ast.parse((ROOT / "main.py").read_text(encoding="utf-8"))
    reference = (ROOT / "docs/03-命令与配置参考.md").read_text(encoding="utf-8")
    for call in ast.walk(cli_tree):
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "add_argument":
            for arg in call.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("-"):
                    if arg.value not in reference:
                        raise SystemExit(f"CLI option missing from reference: {arg.value}")

    metadata = json.loads((ROOT / ".github/repository-metadata.json").read_text(encoding="utf-8"))
    topics = metadata["topics"]
    if len(topics) > 20 or len(topics) != len(set(topics)):
        raise SystemExit("Invalid topic count or duplicates")
    if not all(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,49}", topic) for topic in topics):
        raise SystemExit("Invalid topic spelling")
    json.loads((ROOT / ".devcontainer/devcontainer.json").read_text(encoding="utf-8"))
    manifests = [*sorted((ROOT / "examples").rglob("*.manifest")),
                 *sorted((ROOT / "docs/案例库").rglob("*.manifest"))]
    for manifest in manifests:
        lines = manifest.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0] != "[VS2019]":
            raise SystemExit(f"Missing compiler tag: {manifest}")
    for script in [*sorted((ROOT / "playground").glob("*.py")), Path(__file__)]:
        ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
    print(f"PASS: {len(documents)} documents, local links, fences, metadata, manifests and demo Python syntax")


if __name__ == "__main__":
    main()

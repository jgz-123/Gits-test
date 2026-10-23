"""Prepare an isolated, credential-free copy of the CLI for the demo."""

import json
from pathlib import Path
import shutil
import sys
import zipfile


REPO = Path(__file__).resolve().parents[1]
STATE = REPO / ".playground"


def main():
    runtime = STATE / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    for name in ("gits", "utils"):
        shutil.copytree(REPO / name, runtime / name, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copy2(REPO / "main.py", runtime / "main.py")
    (runtime / "utils" / "generate_config.py").write_text(
        'def gene_conf(parent_dir):\n'
        '    raise RuntimeError("System installation is disabled in the demo")\n',
        encoding="utf-8")
    conf = runtime / "conf"
    conf.mkdir(exist_ok=True)
    (conf / "__init__.py").write_text("", encoding="utf-8")
    (conf / "config.py").write_text(
        'VERSION = "playground"\nPUBLISH_DATE = "demo"\n'
        'OS = "demo"\npassword = "public-demo-only"\n', encoding="utf-8")
    cache = STATE / "lean"
    cache.mkdir(exist_ok=True)
    config = {"lean": {
        "lean_remote_ip": "unused.invalid", "lean_remote_port": 22,
        "lean_remote_user": "demo", "lean_remote_pwd": "unused",
        "lean_remote_path": "/date/gits/base_lean",
        "lean_local_path": str(cache),
    }, "base_url": "https://example.invalid/"}
    (conf / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    remote = STATE / "remote" / "windows-11"
    remote.mkdir(parents=True, exist_ok=True)
    (remote / "import.cmake").write_text("# Public demo: no SDK imports.\n", encoding="utf-8")
    (remote / "gits-usage-readme.md").write_text(
        "# Public fixture packages\n\nThese files do not perform model inference.\n", encoding="utf-8")
    packages = {
        "demo-runtime": ("demo-runtime/bin/runtime.txt", "GITS public runtime fixture\n"),
        "demo-assets": ("data/labels.txt", "fixture-label-not-a-model\n"),
    }
    for name, (member, content) in packages.items():
        archive = remote / "VS2019" / name / "stable" / f"{name}@1.0.zip"
        archive.parent.mkdir(parents=True, exist_ok=True)
        # Preserve timestamps on repeat setup so an unchanged fixture stays up to date.
        if not archive.exists():
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
                bundle.writestr(member, content)

    project = STATE / "project"
    project.mkdir(exist_ok=True)
    for item in (REPO / "playground" / "fixtures").iterdir():
        shutil.copy2(item, project / item.name)
    bin_dir = STATE / "bin"
    bin_dir.mkdir(exist_ok=True)
    launcher = bin_dir / "gis"
    launcher.write_text(
        f'#!{sys.executable}\nimport runpy\n'
        f'runpy.run_path({str(REPO / "playground" / "run.py")!r}, run_name="__main__")\n',
        encoding="utf-8")
    launcher.chmod(0o755)
    print(f"Prepared isolated playground: {project}")
    print(f"Run: {sys.executable} {REPO / 'playground' / 'run.py'} status --lean -m setup.manifest")


if __name__ == "__main__":
    main()

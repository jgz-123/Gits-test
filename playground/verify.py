"""Check delivery files, flattening, and the actual CLI post-update state."""

from pathlib import Path
import subprocess
import sys


REPO = Path(__file__).resolve().parents[1]
STATE = REPO / ".playground"


def main():
    expected = {
        "lean/demo-runtime@1.0@VS2019/bin/runtime.txt": "GITS public runtime fixture\n",
        "lean/demo-assets@1.0@VS2019/data/labels.txt": "fixture-label-not-a-model\n",
        "project/workspace/runtime.txt": "GITS public runtime fixture\n",
        "project/workspace/data/labels.txt": "fixture-label-not-a-model\n",
    }
    for name, content in expected.items():
        path = STATE / name
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise SystemExit(f"FAIL: missing or incorrect {name}")
    if (STATE / "lean/demo-runtime@1.0@VS2019/demo-runtime").exists():
        raise SystemExit("FAIL: matching package wrapper was not flattened")
    result = subprocess.run(
        [sys.executable, str(REPO / "playground/run.py"), "status", "--lean", "-m", "setup.manifest"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
    print(result.stdout)
    for marker in ("0 unresolved packages", "0 missing packages", "0 packages need to update",
                   "demo-runtime: copy", "demo-assets: copy"):
        if marker not in result.stdout:
            raise SystemExit(f"FAIL: status marker missing: {marker}")
    for marker in ("Command rejected", "Connection failed", "Error:", "Cannot check files"):
        if marker in result.stdout:
            raise SystemExit(f"FAIL: status reported {marker}")
    print("PASS: real CLI selected, extracted, flattened, copied and checked public fixture packages.")


if __name__ == "__main__":
    main()

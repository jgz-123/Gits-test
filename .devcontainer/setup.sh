#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
printf '%s\n' '[1/3] Creating the isolated Python environment...'
python -m venv .playground/venv
printf '%s\n' '[2/3] Installing GITS Python dependencies...'
.playground/venv/bin/python -m pip install -r playground/requirements.txt
printf '%s\n' '[3/3] Preparing the gis launcher and example project...'
.playground/venv/bin/python playground/bootstrap.py
test -x .playground/bin/gis
printf '\n%s\n' 'GITS Playground ready! Open Terminal > New Terminal, then follow README.md.'

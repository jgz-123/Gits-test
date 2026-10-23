#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v cmake >/dev/null || ! command -v g++ >/dev/null; then
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends cmake g++
fi
python -m venv .playground/venv
.playground/venv/bin/python -m pip install -r playground/requirements.txt
.playground/venv/bin/python playground/bootstrap.py
printf '\n%s\n' 'GITS Playground ready! Open Terminal > New Terminal, then follow README.md.'

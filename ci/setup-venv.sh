#!/usr/bin/env bash
# One-time venv setup for the ibex DV flow. Idempotent.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${IBEX_PYTHON:?source ci/env.sh first}"

[ -d "$ROOT/.venv" ] || "$PYTHON" -m venv "$ROOT/.venv"
source "$ROOT/.venv/bin/activate"
pip install --upgrade pip

if [ -f "$ROOT/ci/requirements.lock" ]; then
    pip install -r "$ROOT/ci/requirements.lock"
else
    pip install -U -r "$ROOT/python-requirements.txt"
fi

#!/usr/bin/env bash
# One-time venv setup for the ibex DV flow. Idempotent.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${IBEX_PYTHON:?source ci/env.sh first}"

[ -d "$ROOT/.venv" ] || "$PYTHON" -m venv "$ROOT/.venv"
source "$ROOT/.venv/bin/activate"
pip install --upgrade pip
pip install -U -r "$ROOT/python-requirements.txt"

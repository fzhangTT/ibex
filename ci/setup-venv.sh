#!/usr/bin/env bash
# One-time venv setup for the ibex DV flow. Idempotent.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${IBEX_PYTHON:-/tools_soc/opensrc/python/python-3.12.10/bin/python3}"

[ -d "$ROOT/.venv" ] || "$PYTHON" -m venv "$ROOT/.venv"
source "$ROOT/.venv/bin/activate"
pip install --upgrade pip
pip install -U -r "$ROOT/python-requirements.txt"

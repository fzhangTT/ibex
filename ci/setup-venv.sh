#!/usr/bin/env bash
# One-time venv setup for the ibex DV flow. Idempotent.
set -euo pipefail
# Site login shells export PYTHONPATH entries (e.g. siliconpilot's app dir)
# that carry their own package metadata; left in place, pip/pip-freeze see
# those as "installed" even though they're not in the venv. Clear it for
# every pip operation below so the venv the lock describes is the venv we
# actually get.
unset PYTHONPATH
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${IBEX_PYTHON:?source ci/env.sh first}"

[ -d "$ROOT/.venv" ] || "$PYTHON" -m venv "$ROOT/.venv"
source "$ROOT/.venv/bin/activate"
pip install --upgrade pip

if [ -f "$ROOT/ci/requirements.lock" ]; then
    pip install -r "$ROOT/ci/requirements.lock"

    # Exact freeze-vs-lock check (pip freeze already excludes pip/setuptools/
    # wheel by default; strip them from both sides too in case that changes).
    _freeze="$(pip freeze --local | grep -vE '^(pip|setuptools|wheel)==' | sort)"
    _lock="$(grep -vE '^\s*(#|$)' "$ROOT/ci/requirements.lock" | grep -vE '^(pip|setuptools|wheel)==' | sort)"
    if [ "$_freeze" != "$_lock" ]; then
        echo "setup-venv ERROR: pip freeze does not match ci/requirements.lock" >&2
        diff <(echo "$_lock") <(echo "$_freeze") >&2 || true
        exit 1
    fi
else
    pip install -U -r "$ROOT/python-requirements.txt"
fi

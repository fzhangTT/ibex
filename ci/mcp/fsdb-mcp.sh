#!/usr/bin/env bash
# fsdb-mcp-server launcher; pinned path exported by ci/env.sh (IBEX_MCP_FSDB_SERVER).
# Needs VERDI_HOME; ci/env.sh exports it. Zone B only — never ship to the cleanroom (spec WS5/WS7).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export IBEX_ENV_TOOLCHECK=off  # servers need no simulator toolchain (rationale: ci/mcp/README.md)
# stdout only: the MCP stdio stream owns stdout; keep stderr for env.sh diagnostics.
source "$REPO_ROOT/ci/env.sh" >/dev/null || { echo "ERROR: cannot source ci/env.sh" >&2; exit 1; }
SERVER="${IBEX_MCP_FSDB_SERVER:?ci/env.sh must export IBEX_MCP_FSDB_SERVER}"
[ -n "${VERDI_HOME:-}" ] || { echo "ERROR: VERDI_HOME not set by ci/env.sh" >&2; exit 1; }
[ -x "$SERVER" ] || { echo "ERROR: fsdb-mcp-server not found at $SERVER" >&2; exit 1; }
exec "$SERVER"

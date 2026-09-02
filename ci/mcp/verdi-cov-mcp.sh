#!/usr/bin/env bash
# verdi-cov-mcp launcher; pinned path exported by ci/env.sh (IBEX_MCP_VERDI_COV).
# Needs VERDI_HOME; ci/env.sh exports it. Zone B only — never ship to the cleanroom (spec WS5/WS7).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# stdout only: the MCP stdio stream owns stdout; keep stderr for env.sh diagnostics.
source "$REPO_ROOT/ci/env.sh" >/dev/null || { echo "ERROR: cannot source ci/env.sh" >&2; exit 1; }
SERVER="${IBEX_MCP_VERDI_COV:?ci/env.sh must export IBEX_MCP_VERDI_COV}"
[ -x "$SERVER" ] || { echo "ERROR: verdi-cov-mcp not found at $SERVER" >&2; exit 1; }
exec "$SERVER"

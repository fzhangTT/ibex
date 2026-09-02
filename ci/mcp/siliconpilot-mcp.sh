#!/usr/bin/env bash
# siliconpilot-mcp launcher; pinned path exported by ci/env.sh (IBEX_MCP_SILICONPILOT).
# No VERDI_HOME dependency — only needs the IBEX_MCP_SILICONPILOT export from ci/env.sh.
# Zone B only — never ship to the cleanroom (spec WS5/WS7).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export IBEX_ENV_TOOLCHECK=off  # servers need no simulator toolchain (rationale: ci/mcp/README.md)
# stdout only: the MCP stdio stream owns stdout; keep stderr for env.sh diagnostics.
source "$REPO_ROOT/ci/env.sh" >/dev/null || { echo "ERROR: cannot source ci/env.sh" >&2; exit 1; }
SERVER="${IBEX_MCP_SILICONPILOT:?ci/env.sh must export IBEX_MCP_SILICONPILOT}"
[ -x "$SERVER" ] || { echo "ERROR: siliconpilot-mcp not found at $SERVER" >&2; exit 1; }
exec "$SERVER" --workspace "$REPO_ROOT"

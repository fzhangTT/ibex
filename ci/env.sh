#!/usr/bin/env bash
# Environment entry point for ibex auto-DV work (Zone A cleanroom clone). Source, don't execute:
#   source ci/env.sh
# Central authority for tool paths — nothing else in the repo hardcodes them.
#
# Contract: supported on site hosts that already carry the standard site
# profile — a login shell (`bash -l`) or any shell that inherits the site
# environment (Modules init, PATH, etc.) from one. This script loads
# additional site Modules on top of that; it does not bootstrap a sanitized
# shell that never sourced the site profile at all.

IBEX_CI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export IBEX_TOOLS_DIR="${IBEX_TOOLS_DIR:-/localdev/fzhang/ws/tools}"
export IBEX_PYTHON="${IBEX_PYTHON:-/tools_soc/opensrc/python/python-3.12.10/bin/python3}"

# --- Host GCC (VCS DPI/PLI compiles need gcc-toolset-11; a non-login shell
# doesn't pick this up from /etc/profile.d) ---
if [ -f /opt/rh/gcc-toolset-11/enable ]; then
    source /opt/rh/gcc-toolset-11/enable
fi

# --- Simulator (VCS must match the Verdi release already on PATH) ---
source /etc/profile.d/modules.sh 2>/dev/null || true
# synopsys/vcs has an undeclared prereq on synopsys/licenses; 2.3 is the newest
# available (of 1.0-2.3) and a superset of older servers, so pick it.
# This site's module command exits 1 even on a successful load, hence `|| true`.
module load synopsys/licenses/2.3 2>/dev/null || true
module load synopsys/vcs/X-2025.06-SP2 2>/dev/null || true
export VERDI_HOME="${VERDI_HOME:-/tools_vendor/synopsys/verdi/X-2025.06-SP2}"

# --- MCP server installs (the three local servers this clone ships; wrappers in
# ci/mcp/ consume these — point them only at this clone's own out-tree artifacts) ---
export IBEX_MCP_SILICONPILOT=/tools_risc/tt/siliconpilot/0.18.1/bin/siliconpilot-mcp  # pinned 0.18.1
export IBEX_MCP_FSDB_SERVER=/tools_soc/tt/fsdb-mcp-server/0.2.6/start_server.sh       # pinned 0.2.6
export IBEX_MCP_VERDI_COV=/tools_vendor/tt/verdi_cov_npi_mcp/v0.2.2/mcp_env_wrap.sh   # pinned v0.2.2
# fsdb-mcp needs verdi/waveutils as commands (an alias does not reach subprocesses).
case ":$PATH:" in *":$VERDI_HOME/bin:"*) ;; *) export PATH="$VERDI_HOME/bin:$PATH";; esac

# dtc (device-tree compiler) is a build dep of some upstream RISC-V tools (e.g. an
# ISS built from source); this site's module command exits 1 even on a successful
# load, hence the `|| true`.
module load dtc/1.7.2 2>/dev/null || true

# --- GitHub CLI ---
export PATH="/tools_vendor/FOSS/gh/2.53.0/bin:$PATH"

# --- RISC-V toolchain (lowRISC prebuilt preferred; site fallback below) ---
# _IBEX_RV_TC_AUTO caches our own last pick so re-sourcing after installing
# the lowRISC toolchain picks it up, without clobbering a real user override
# (RISCV_TOOLCHAIN set to anything other than our own last pick).
if [ -n "${RISCV_TOOLCHAIN:-}" ] && [ "${RISCV_TOOLCHAIN:-}" != "${_IBEX_RV_TC_AUTO:-}" ]; then
    _ibex_rv_tc="$RISCV_TOOLCHAIN"
elif [ -x "$IBEX_TOOLS_DIR/lowrisc-toolchain-gcc-rv32imcb/bin/riscv32-unknown-elf-gcc" ]; then
    _ibex_rv_tc="$IBEX_TOOLS_DIR/lowrisc-toolchain-gcc-rv32imcb"
else
    # Site riscv64 multilib fallback (bitmanip tests unavailable)
    _ibex_rv_tc=/tools_risc/opensrc/latest/newlib
fi
export RISCV_TOOLCHAIN="$_ibex_rv_tc"
export _IBEX_RV_TC_AUTO="$_ibex_rv_tc"
unset _ibex_rv_tc

if [ -x "$RISCV_TOOLCHAIN/bin/riscv32-unknown-elf-gcc" ]; then
    export RISCV_GCC="$RISCV_TOOLCHAIN/bin/riscv32-unknown-elf-gcc"
    export RISCV_OBJCOPY="$RISCV_TOOLCHAIN/bin/riscv32-unknown-elf-objcopy"
else
    export RISCV_GCC="$RISCV_TOOLCHAIN/bin/riscv64-unknown-elf-gcc"
    export RISCV_OBJCOPY="$RISCV_TOOLCHAIN/bin/riscv64-unknown-elf-objcopy"
fi

# --- Python venv (created by ci/setup-venv.sh; optional until then) ---
if [ -f "$IBEX_CI_ROOT/.venv/bin/activate" ]; then
    source "$IBEX_CI_ROOT/.venv/bin/activate"
fi

# --- cocotb (installed by ci/setup-venv.sh). cocotb's VPI library dlopens libpython
# through LIBPYTHON_LOC, so the value must come from THIS clone's venv: a site
# cocotb-config on PATH answers for the pinned one, its --libpython fails, and a
# bare export would mask that as an empty string (dv/auto_dv/docs/gen_intervention_log.md
# LOG-099/LOG-100). Fail loud when the venv's tool cannot answer; before the venv
# exists (bootstrap, or a fresh worktree) warn and leave any inherited value alone. ---
_ibex_cc="$IBEX_CI_ROOT/.venv/bin/cocotb-config"
if [ -x "$_ibex_cc" ]; then
    if _ibex_lp="$("$_ibex_cc" --libpython 2>/dev/null)" && [ -n "$_ibex_lp" ]; then
        export LIBPYTHON_LOC="$_ibex_lp"
    else
        echo "ibex env ERROR: $_ibex_cc --libpython failed or printed nothing; LIBPYTHON_LOC not set (rerun ci/setup-venv.sh)" >&2
        unset _ibex_cc _ibex_lp
        return 1
    fi
else
    echo "ibex env WARN: no $_ibex_cc (run ci/setup-venv.sh); LIBPYTHON_LOC left as inherited (${LIBPYTHON_LOC:-unset})" >&2
fi
unset _ibex_cc _ibex_lp

echo "ibex env: vcs=$(command -v vcs || echo MISSING)" \
     "gcc=$(command -v "$RISCV_GCC" >/dev/null && echo "$RISCV_GCC" || echo MISSING)"

# --- Fail loud: load noise above is tolerated, but the tools it was supposed
# to produce are not optional. verdi/dtc are only needed for waveform debug
# and source-built RISC-V tools respectively, so those are WARN-only.
# IBEX_ENV_TOOLCHECK=off skips this whole block, for callers (MCP wrappers) that
# only need the exports above and never invoke vcs/gcc/python3 themselves. ---
if [ "${IBEX_ENV_TOOLCHECK:-}" = "off" ]; then
    echo "ibex env: tool check skipped (IBEX_ENV_TOOLCHECK=off)" >&2
else
    _ibex_env_status=0
    command -v verdi >/dev/null 2>&1 || echo "ibex env WARN: verdi missing — waveform debug (FSDB dumping) unavailable" >&2
    command -v dtc >/dev/null 2>&1 || echo "ibex env WARN: dtc missing — building device-tree-dependent tools from source will fail" >&2
    command -v vcs >/dev/null 2>&1 || {
        echo "ibex env ERROR: vcs missing — are you on a site host?" >&2
        _ibex_env_status=1
    }
    command -v "$RISCV_GCC" >/dev/null 2>&1 || {
        echo "ibex env ERROR: RISCV_GCC ($RISCV_GCC) missing — are you on a site host?" >&2
        _ibex_env_status=1
    }
    command -v python3 >/dev/null 2>&1 || {
        echo "ibex env ERROR: python3 missing — are you on a site host?" >&2
        _ibex_env_status=1
    }
    if [ "$_ibex_env_status" -ne 0 ]; then
        unset _ibex_env_status
        return 1
    fi
    unset _ibex_env_status
fi

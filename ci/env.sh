#!/usr/bin/env bash
# Environment entry point for ibex auto-DV work. Source, don't execute:
#   source ci/env.sh
# Central authority for tool paths — nothing else in the repo hardcodes them.

IBEX_CI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export IBEX_TOOLS_DIR="${IBEX_TOOLS_DIR:-/localdev/fzhang/ws/tools}"

# --- Simulator (VCS must match the Verdi release already on PATH) ---
source /etc/profile.d/modules.sh 2>/dev/null || true
# synopsys/vcs has an undeclared prereq on synopsys/licenses; 2.3 is the newest
# available (of 1.0-2.3) and a superset of older servers, so pick it.
module load synopsys/licenses/2.3
module load synopsys/vcs/X-2025.06-SP2
export VERDI_HOME="${VERDI_HOME:-/tools_vendor/synopsys/verdi/X-2025.06-SP2}"

# --- GitHub CLI (auth already configured for fzhangTT) ---
export PATH="/tools_vendor/FOSS/gh/2.53.0/bin:$PATH"

# --- RISC-V toolchain (Task 4 decides which; lowRISC preferred) ---
export RISCV_TOOLCHAIN="${RISCV_TOOLCHAIN:-$IBEX_TOOLS_DIR/lowrisc-toolchain-gcc-rv32imcb}"
if [ -x "$RISCV_TOOLCHAIN/bin/riscv32-unknown-elf-gcc" ]; then
    export RISCV_GCC="$RISCV_TOOLCHAIN/bin/riscv32-unknown-elf-gcc"
    export RISCV_OBJCOPY="$RISCV_TOOLCHAIN/bin/riscv32-unknown-elf-objcopy"
else
    # Site riscv64 multilib fallback (bitmanip tests unavailable)
    export RISCV_TOOLCHAIN=/tools_risc/opensrc/latest/newlib
    export RISCV_GCC="$RISCV_TOOLCHAIN/bin/riscv64-unknown-elf-gcc"
    export RISCV_OBJCOPY="$RISCV_TOOLCHAIN/bin/riscv64-unknown-elf-objcopy"
fi

# --- Spike (lowRISC ibex_cosim fork, built by ci/build-spike.sh) ---
export SPIKE_INSTALL="$IBEX_TOOLS_DIR/spike-ibex-cosim"
export SPIKE_PATH="$SPIKE_INSTALL/bin"
export PKG_CONFIG_PATH="$SPIKE_INSTALL/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"

# --- Python venv (created by Task 2; optional until then) ---
if [ -f "$IBEX_CI_ROOT/.venv/bin/activate" ]; then
    source "$IBEX_CI_ROOT/.venv/bin/activate"
fi

echo "ibex env: vcs=$(command -v vcs || echo MISSING)" \
     "gcc=$(command -v "$RISCV_GCC" >/dev/null && echo "$RISCV_GCC" || echo MISSING)" \
     "spike=$([ -d "$SPIKE_INSTALL" ] && echo "$SPIKE_INSTALL" || echo NOT-BUILT)"
